"""
MediMind - LLM 推理引擎

支持 Gemini API 和 Ollama 本地模型。
"""

from typing import Optional, List, Dict, Any, AsyncGenerator
from abc import ABC, abstractmethod

from src.utils import get_settings, log


class BaseLLMEngine(ABC):
    """LLM 引擎基类"""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """生成文本"""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """流式生成文本"""
        pass


class GeminiEngine(BaseLLMEngine):
    """Gemini API 引擎"""

    def __init__(
        self,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
    ):
        settings = get_settings()
        
        self.model = model or settings.gemini.model
        self.temperature = temperature or settings.gemini.temperature
        self.max_tokens = max_tokens or settings.gemini.max_tokens
        self.api_key = settings.gemini_api_key
        
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
                log.info(f"Gemini 引擎初始化完成: {self.model}")
            except Exception as e:
                log.error(f"Gemini 初始化失败: {e}")
                raise
        return self._client

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """生成文本"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = self.client.generate_content(
            full_prompt,
            generation_config={
                "temperature": kwargs.get("temperature", self.temperature),
                "max_output_tokens": kwargs.get("max_tokens", self.max_tokens),
            },
        )
        
        return response.text

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """流式生成文本"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = self.client.generate_content(
            full_prompt,
            generation_config={
                "temperature": kwargs.get("temperature", self.temperature),
                "max_output_tokens": kwargs.get("max_tokens", self.max_tokens),
            },
            stream=True,
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text


class OllamaEngine(BaseLLMEngine):
    """Ollama 本地模型引擎"""

    def __init__(
        self,
        model: str = None,
        base_url: str = None,
        temperature: float = None,
    ):
        settings = get_settings()
        
        self.model = model or settings.ollama.model
        self.base_url = base_url or settings.ollama.base_url
        self.temperature = temperature or settings.ollama.temperature
        
        log.info(f"Ollama 引擎配置: {self.model} @ {self.base_url}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """生成文本"""
        import requests
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.temperature),
                },
            },
            timeout=120,
        )
        response.raise_for_status()
        
        return response.json()["message"]["content"]

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """流式生成文本"""
        import httpx
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": kwargs.get("temperature", self.temperature),
                    },
                },
            ) as response:
                import json
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]


def get_llm_engine() -> BaseLLMEngine:
    """获取 LLM 引擎"""
    settings = get_settings()
    
    if settings.use_ollama:
        return OllamaEngine()
    else:
        return GeminiEngine()
