---
name: add-core-module
description: 为 MediMind 添加核心业务模块（RAG、Agent、Guardrails等）
---

# 添加核心模块技能

此技能用于为 MediMind 健康助手项目添加核心业务模块。

## 项目结构

```
src/core/
├── __init__.py           # 模块导出
├── embedder.py           # 向量嵌入
├── vector_store.py       # 向量存储 (Chroma)
├── retriever.py          # 检索器
├── llm_engine.py         # LLM 引擎 (Gemini/Ollama)
├── rag_service.py        # RAG 问答服务
├── triage_agent.py       # 导诊 Agent (LangGraph)
├── report_analyzer.py    # 报告解读服务
└── guardrails.py         # 安全护栏
```

## 核心模块模板

### 1. RAG 服务 (rag_service.py)

```python
"""
MediMind - RAG 问答服务
"""

from typing import AsyncGenerator, List, Optional
from dataclasses import dataclass

from src.core.embedder import Embedder
from src.core.vector_store import VectorStore
from src.core.llm_engine import LLMEngine
from src.core.guardrails import Guardrail
from src.utils import get_settings, log


@dataclass
class HealthAnswer:
    """健康问答结果"""
    content: str
    sources: List[dict]
    emergency: bool = False
    disclaimer: str = "以上信息仅供参考，如有健康问题请咨询专业医生。"


class RAGService:
    """健康知识问答服务"""

    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        llm: LLMEngine,
        guardrail: Guardrail,
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.llm = llm
        self.guardrail = guardrail
        self.settings = get_settings()

    async def answer(self, query: str) -> HealthAnswer:
        """回答健康问题"""
        # 1. 输入安全检查
        input_check = self.guardrail.check_input(query)
        if not input_check.passed:
            return HealthAnswer(
                content=input_check.message,
                sources=[],
                emergency=input_check.is_emergency,
            )

        # 2. 检索相关知识
        query_embedding = self.embedder.embed(query)
        chunks = self.vector_store.search(query_embedding, top_k=5)

        # 3. 构建 Prompt
        prompt = self._build_prompt(query, chunks)

        # 4. 生成回答
        response = await self.llm.generate(prompt)

        # 5. 输出合规检查
        output_check = self.guardrail.check_output(response)

        # 6. 提取来源
        sources = self._extract_sources(chunks)

        return HealthAnswer(
            content=output_check.content,
            sources=sources,
            emergency=input_check.is_emergency,
        )

    async def stream_answer(self, query: str) -> AsyncGenerator[str, None]:
        """流式回答"""
        # 输入检查
        input_check = self.guardrail.check_input(query)
        if not input_check.passed:
            yield input_check.message
            return

        # 检索
        query_embedding = self.embedder.embed(query)
        chunks = self.vector_store.search(query_embedding, top_k=5)

        # 流式生成
        prompt = self._build_prompt(query, chunks)
        async for chunk in self.llm.stream_generate(prompt):
            yield chunk

    def _build_prompt(self, query: str, chunks: List[dict]) -> str:
        """构建 RAG Prompt"""
        context = "\n\n".join([
            f"【来源: {c['source']}】\n{c['content']}"
            for c in chunks
        ])

        return f"""你是一个专业的健康信息助手。请基于以下参考内容回答用户的健康问题。

## 参考资料
{context}

## 重要注意事项
1. 只基于参考资料回答，不要编造医学信息
2. 使用通俗易懂的语言解释医学概念
3. 如果参考资料无法回答，请明确说明并建议咨询医生
4. 回答时标注信息来源
5. 不要给出诊断或处方建议
6. 适当建议用户在必要时就医

## 用户问题
{query}

## 回答
"""

    def _extract_sources(self, chunks: List[dict]) -> List[dict]:
        """提取来源信息"""
        return [
            {"title": c.get("source", ""), "page": c.get("page", "")}
            for c in chunks
        ]
```

### 2. LLM 引擎 (llm_engine.py)

```python
"""
MediMind - LLM 推理引擎 (支持 Gemini 和 Ollama)
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator
import os

from src.utils import get_settings, log


class BaseLLM(ABC):
    """LLM 基类"""

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """生成文本"""
        pass

    @abstractmethod
    async def stream_generate(self, prompt: str) -> AsyncGenerator[str, None]:
        """流式生成"""
        pass


class GeminiLLM(BaseLLM):
    """Gemini LLM"""

    def __init__(self, model_name: str = "gemini-2.0-flash"):
        import google.generativeai as genai

        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(model_name)

    async def generate(self, prompt: str) -> str:
        response = await self.model.generate_content_async(prompt)
        return response.text

    async def stream_generate(self, prompt: str) -> AsyncGenerator[str, None]:
        response = await self.model.generate_content_async(
            prompt, stream=True
        )
        async for chunk in response:
            if chunk.text:
                yield chunk.text


class OllamaLLM(BaseLLM):
    """Ollama 本地 LLM"""

    def __init__(self, model_name: str = "qwen2.5:7b"):
        import httpx
        self.model_name = model_name
        self.base_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.client = httpx.AsyncClient()

    async def generate(self, prompt: str) -> str:
        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model_name, "prompt": prompt, "stream": False},
        )
        return response.json()["response"]

    async def stream_generate(self, prompt: str) -> AsyncGenerator[str, None]:
        async with self.client.stream(
            "POST",
            f"{self.base_url}/api/generate",
            json={"model": self.model_name, "prompt": prompt, "stream": True},
        ) as response:
            async for line in response.aiter_lines():
                import json
                data = json.loads(line)
                if data.get("response"):
                    yield data["response"]


def get_llm() -> BaseLLM:
    """获取 LLM 实例"""
    settings = get_settings()
    if settings.use_ollama:
        return OllamaLLM(settings.ollama_model)
    return GeminiLLM(settings.gemini_model)
```

### 3. 向量存储 (vector_store.py)

```python
"""
MediMind - 向量存储 (Chroma)
"""

from typing import List, Optional
from pathlib import Path

from src.utils import get_settings, log


class VectorStore:
    """Chroma 向量存储"""

    def __init__(self, collection_name: str = "medical_knowledge"):
        import chromadb

        settings = get_settings()
        persist_dir = Path(settings.data_dir) / "chroma_index"

        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
    ):
        """添加文档"""
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[dict] = None,
    ) -> List[dict]:
        """搜索相似文档"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter,
        )

        chunks = []
        for i, doc_id in enumerate(results["ids"][0]):
            chunks.append({
                "id": doc_id,
                "content": results["documents"][0][i],
                "score": 1 - results["distances"][0][i],  # cosine -> similarity
                **results["metadatas"][0][i],
            })

        return chunks
```

## 模块注册

在 `__init__.py` 导出：

```python
from .embedder import Embedder
from .vector_store import VectorStore
from .retriever import Retriever
from .llm_engine import BaseLLM, GeminiLLM, OllamaLLM, get_llm
from .rag_service import RAGService, HealthAnswer
from .triage_agent import TriageAgent
from .report_analyzer import ReportAnalyzer
from .guardrails import Guardrail, GuardrailResult

__all__ = [
    "Embedder",
    "VectorStore",
    "Retriever",
    "BaseLLM",
    "GeminiLLM",
    "OllamaLLM",
    "get_llm",
    "RAGService",
    "HealthAnswer",
    "TriageAgent",
    "ReportAnalyzer",
    "Guardrail",
    "GuardrailResult",
]
```

## 单例模式

```python
# src/core/__init__.py

_embedder: Optional[Embedder] = None
_llm: Optional[BaseLLM] = None

def get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder

def get_llm_instance() -> BaseLLM:
    global _llm
    if _llm is None:
        _llm = get_llm()
    return _llm
```

## 注意事项

1. **延迟加载**：模型在首次使用时加载
2. **异步优先**：所有 LLM 调用使用 async/await
3. **安全护栏**：所有服务必须集成 Guardrail
4. **医疗合规**：输出必须包含免责声明
5. **来源引用**：回答必须标注信息来源
