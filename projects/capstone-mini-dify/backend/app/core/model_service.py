"""
Mini-Dify - 统一模型调用服务
基于 LangChain 封装多供应商 LLM 调用
"""

import time
import asyncio
from typing import AsyncGenerator, Optional
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel


@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class ChatResult:
    content: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    finish_reason: str = "stop"


@dataclass
class HealthCheckResult:
    status: str  # "healthy" | "unhealthy"
    latency_ms: int = 0
    error: Optional[str] = None


class ModelService:
    """统一模型调用服务，支持多供应商"""

    SUPPORTED_PROVIDERS = {"openai", "anthropic", "google", "ollama"}

    @staticmethod
    def _create_chat_model(
        provider_type: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        streaming: bool = False,
    ) -> BaseChatModel:
        """根据 provider_type 创建对应的 LangChain ChatModel"""

        if provider_type == "openai":
            from langchain_openai import ChatOpenAI

            kwargs = {
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "streaming": streaming,
            }
            if api_key:
                kwargs["api_key"] = api_key
            if base_url:
                kwargs["base_url"] = base_url
            return ChatOpenAI(**kwargs)

        elif provider_type == "anthropic":
            from langchain_anthropic import ChatAnthropic

            kwargs = {
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "streaming": streaming,
            }
            if api_key:
                kwargs["anthropic_api_key"] = api_key
            if base_url:
                kwargs["anthropic_api_url"] = base_url
            return ChatAnthropic(**kwargs)

        elif provider_type == "google":
            from langchain_community.chat_models import ChatGoogleGenerativeAI

            kwargs = {
                "model": model,
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            if api_key:
                kwargs["google_api_key"] = api_key
            return ChatGoogleGenerativeAI(**kwargs)

        elif provider_type == "ollama":
            from langchain_community.chat_models import ChatOllama

            kwargs = {
                "model": model,
                "temperature": temperature,
            }
            if base_url:
                kwargs["base_url"] = base_url
            return ChatOllama(**kwargs)

        else:
            raise ValueError(f"不支持的供应商类型: {provider_type}")

    @staticmethod
    def _convert_messages(messages: list[ChatMessage]) -> list:
        """将 ChatMessage 转为 LangChain Message"""
        lc_messages = []
        for msg in messages:
            if msg.role == "system":
                lc_messages.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))
        return lc_messages

    @classmethod
    async def health_check(
        cls,
        provider_type: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o-mini",
    ) -> HealthCheckResult:
        """检测供应商连通性：发送简单请求测试连接"""
        start = time.time()
        try:
            chat_model = cls._create_chat_model(
                provider_type=provider_type,
                api_key=api_key,
                base_url=base_url,
                model=model,
                temperature=0,
                max_tokens=5,
                streaming=False,
            )
            messages = [HumanMessage(content="Hi")]
            # 在线程池中运行同步 invoke
            await asyncio.to_thread(chat_model.invoke, messages)
            latency = int((time.time() - start) * 1000)
            return HealthCheckResult(status="healthy", latency_ms=latency)
        except Exception as e:
            latency = int((time.time() - start) * 1000)
            return HealthCheckResult(
                status="unhealthy", latency_ms=latency, error=str(e)
            )

    @classmethod
    async def chat(
        cls,
        provider_type: str,
        messages: list[ChatMessage],
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> ChatResult:
        """非流式对话调用"""
        start = time.time()
        chat_model = cls._create_chat_model(
            provider_type=provider_type,
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=False,
        )
        lc_messages = cls._convert_messages(messages)
        response = await asyncio.to_thread(chat_model.invoke, lc_messages)
        latency = int((time.time() - start) * 1000)

        # 提取 token 使用信息
        usage = getattr(response, "usage_metadata", None)
        input_tokens = getattr(usage, "input_tokens", 0) if usage else 0
        output_tokens = getattr(usage, "output_tokens", 0) if usage else 0

        return ChatResult(
            content=response.content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency,
        )

    @classmethod
    async def chat_stream(
        cls,
        provider_type: str,
        messages: list[ChatMessage],
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[dict, None]:
        """流式对话调用，返回 SSE 数据片段"""
        start = time.time()
        chat_model = cls._create_chat_model(
            provider_type=provider_type,
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=True,
        )
        lc_messages = cls._convert_messages(messages)

        full_content = ""
        async for chunk in chat_model.astream(lc_messages):
            token = chunk.content
            if token:
                full_content += token
                yield {"content": token, "finish_reason": None}

        latency = int((time.time() - start) * 1000)

        # 最后一条带 finish_reason 和 usage
        usage = getattr(chunk, "usage_metadata", None)
        input_tokens = getattr(usage, "input_tokens", 0) if usage else 0
        output_tokens = getattr(usage, "output_tokens", 0) if usage else 0

        yield {
            "content": "",
            "finish_reason": "stop",
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
            "latency_ms": latency,
        }
