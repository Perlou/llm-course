"""
统一 LLM 客户端
================

提供统一的接口来调用不同的 LLM API。
默认使用 Google Gemini（免费额度较大），可切换到 OpenAI 或 Ollama。

使用方法：
    from utils.llm_client import get_client, chat

    # 简单调用
    response = chat("你好")
    print(response)

    # 流式调用
    for chunk in chat("你好", stream=True):
        print(chunk, end="", flush=True)
"""

import os
from typing import Iterator, Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """统一的 LLM 客户端"""

    def __init__(self, provider: str = "auto"):
        """
        初始化 LLM 客户端

        Args:
            provider: "gemini", "openai", "ollama", 或 "auto"（自动检测）
        """
        self.provider = self._detect_provider() if provider == "auto" else provider
        self._client = None
        self._model = None
        self._setup_client()

    def _detect_provider(self) -> str:
        """自动检测可用的 API 提供商"""
        if os.getenv("GOOGLE_API_KEY"):
            return "gemini"
        elif os.getenv("OPENAI_API_KEY"):
            return "openai"
        elif os.getenv("OLLAMA_HOST") or self._check_ollama():
            return "ollama"
        else:
            raise ValueError(
                "未找到可用的 API Key，请配置 GOOGLE_API_KEY 或 OPENAI_API_KEY"
            )

    def _check_ollama(self) -> bool:
        """检查 Ollama 是否可用"""
        try:
            import requests

            host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            response = requests.get(f"{host}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def _setup_client(self):
        """设置客户端"""
        if self.provider == "gemini":
            import google.generativeai as genai

            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self._model = genai.GenerativeModel("gemini-2.0-flash")

        elif self.provider == "openai":
            from openai import OpenAI

            self._client = OpenAI()
            self._model = "gpt-3.5-turbo"

        elif self.provider == "ollama":
            from openai import OpenAI

            host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            self._client = OpenAI(base_url=f"{host}/v1", api_key="ollama")
            self._model = "llama3"

    def chat(
        self,
        message: str,
        system: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False,
        **kwargs,
    ) -> str | Iterator[str]:
        """
        发送聊天消息

        Args:
            message: 用户消息
            system: 系统提示词（可选）
            history: 对话历史（可选）
            stream: 是否流式输出
            **kwargs: 其他参数（如 temperature, max_tokens）

        Returns:
            回复文本，或流式输出的迭代器
        """
        if self.provider == "gemini":
            return self._chat_gemini(message, system, history, stream, **kwargs)
        else:
            return self._chat_openai(message, system, history, stream, **kwargs)

    def _chat_gemini(
        self,
        message: str,
        system: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False,
        **kwargs,
    ) -> str | Iterator[str]:
        """Gemini 聊天实现"""
        import google.generativeai as genai

        # 如果有系统提示词，重新创建模型
        if system:
            model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=system)
        else:
            model = self._model

        # 构建对话历史
        if history:
            chat = model.start_chat(
                history=[{"role": h["role"], "parts": [h["content"]]} for h in history]
            )
            response = chat.send_message(message, stream=stream)
        else:
            response = model.generate_content(message, stream=stream)

        if stream:

            def stream_generator():
                for chunk in response:
                    if chunk.text:
                        yield chunk.text

            return stream_generator()
        else:
            return response.text

    def _chat_openai(
        self,
        message: str,
        system: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False,
        **kwargs,
    ) -> str | Iterator[str]:
        """OpenAI/Ollama 聊天实现"""
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": message})

        response = self._client.chat.completions.create(
            model=self._model, messages=messages, stream=stream, **kwargs
        )

        if stream:

            def stream_generator():
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

            return stream_generator()
        else:
            return response.choices[0].message.content

    def get_provider_info(self) -> Dict[str, Any]:
        """获取当前提供商信息"""
        return {
            "provider": self.provider,
            "model": self._model
            if isinstance(self._model, str)
            else "gemini-2.0-flash",
        }


# 全局客户端实例
_default_client: Optional[LLMClient] = None


def get_client(provider: str = "auto") -> LLMClient:
    """获取 LLM 客户端实例"""
    global _default_client
    if _default_client is None or _default_client.provider != provider:
        _default_client = LLMClient(provider)
    return _default_client


def chat(
    message: str,
    system: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None,
    stream: bool = False,
    **kwargs,
) -> str | Iterator[str]:
    """
    快捷聊天函数

    示例：
        # 简单调用
        response = chat("你好")

        # 带系统提示词
        response = chat("今天天气很好", system="你是翻译官，将中文翻译成英文")

        # 流式输出
        for chunk in chat("写一首诗", stream=True):
            print(chunk, end="", flush=True)
    """
    client = get_client()
    return client.chat(message, system, history, stream, **kwargs)


def check_api_status() -> Dict[str, bool]:
    """检查各 API 的可用状态"""
    status = {
        "gemini": bool(os.getenv("GOOGLE_API_KEY")),
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "ollama": False,
    }

    # 检查 Ollama
    try:
        import requests

        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        response = requests.get(f"{host}/api/tags", timeout=2)
        status["ollama"] = response.status_code == 200
    except:
        pass

    return status


if __name__ == "__main__":
    # 测试代码
    print("🔍 检查 API 状态...")
    status = check_api_status()
    for provider, available in status.items():
        icon = "✅" if available else "❌"
        print(f"  {icon} {provider}")

    print("\n📤 测试聊天...")
    try:
        client = get_client()
        info = client.get_provider_info()
        print(f"  使用: {info['provider']} ({info['model']})")

        response = chat("用一句话介绍你自己")
        print(f"  回复: {response}")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
