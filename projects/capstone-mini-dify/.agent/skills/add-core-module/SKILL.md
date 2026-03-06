---
name: add-core-module
description: 为 Mini-Dify 添加核心业务模块（ModelHub、RAG、Agent、Workflow）
---

# 添加核心模块技能

此技能用于为 Mini-Dify 添加核心业务模块。

## 核心模块结构

```
backend/app/core/
├── __init__.py
├── model_hub.py         # 多模型管理
├── prompt_engine.py     # Prompt 模板引擎
├── rag_pipeline.py      # RAG 管道 (Milvus)
├── agent_runtime.py     # Agent 运行时 (LangGraph)
├── workflow_engine.py   # 工作流引擎 (LangGraph)
├── tool_registry.py     # 工具注册表
└── llm_ops.py           # LLMOps 监控
```

## 模块模板

### 1. Model Hub (多模型管理)

```python
"""
Mini-Dify - Model Hub 统一模型管理
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator
from langchain_core.language_models import BaseChatModel


class ModelProvider(ABC):
    """模型供应商基类"""

    @abstractmethod
    def get_chat_model(self, model_name: str, **params) -> BaseChatModel:
        pass

    @abstractmethod
    def list_models(self) -> list[str]:
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        pass


class OpenAIProvider(ModelProvider):
    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url

    def get_chat_model(self, model_name: str, **params) -> BaseChatModel:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model_name, api_key=self.api_key,
            base_url=self.base_url, **params
        )


class AnthropicProvider(ModelProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_chat_model(self, model_name: str, **params) -> BaseChatModel:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model_name, api_key=self.api_key, **params
        )


class ModelHub:
    """统一管理所有供应商和模型"""

    def __init__(self):
        self._providers: dict[str, ModelProvider] = {}

    def register_provider(self, name: str, provider: ModelProvider):
        self._providers[name] = provider

    def get_model(self, provider_name: str, model_name: str, **params) -> BaseChatModel:
        provider = self._providers.get(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found")
        return provider.get_chat_model(model_name, **params)

    async def health_check(self, provider_name: str) -> dict:
        provider = self._providers.get(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found")
        return await provider.health_check()
```

### 2. RAG Pipeline (基于 Milvus)

```python
"""
Mini-Dify - RAG Pipeline (Milvus 向量数据库)
"""

from uuid import uuid4
from pymilvus import MilvusClient, CollectionSchema, FieldSchema, DataType


class RAGPipeline:
    """RAG 管道"""

    def __init__(self, embedder, milvus_client: MilvusClient):
        self.embedder = embedder
        self.milvus = milvus_client

    async def create_collection(self, dataset_id: str, dimension: int = 1024):
        """创建 Milvus Collection"""
        collection = f"dataset_{dataset_id}"
        schema = CollectionSchema([
            FieldSchema("id", DataType.VARCHAR, is_primary=True, max_length=36),
            FieldSchema("content", DataType.VARCHAR, max_length=65535),
            FieldSchema("document_id", DataType.VARCHAR, max_length=36),
            FieldSchema("chunk_index", DataType.INT64),
            FieldSchema("embedding", DataType.FLOAT_VECTOR, dim=dimension),
        ])
        self.milvus.create_collection(collection, schema=schema)

    async def ingest(self, file_path: str, dataset_id: str, chunk_size=500, overlap=50) -> int:
        """文档摄入：加载 → 切分 → 嵌入 → 存储"""
        docs = self._load_document(file_path)
        chunks = self._split(docs, chunk_size, overlap)
        embeddings = self.embedder.embed_documents([c.page_content for c in chunks])

        data = [{
            "id": str(uuid4()),
            "content": chunk.page_content,
            "document_id": chunk.metadata.get("document_id", ""),
            "chunk_index": i,
            "embedding": emb
        } for i, (chunk, emb) in enumerate(zip(chunks, embeddings))]

        self.milvus.insert(f"dataset_{dataset_id}", data)
        return len(data)

    async def retrieve(self, query: str, dataset_id: str, top_k: int = 5) -> list[dict]:
        """向量检索"""
        query_emb = self.embedder.embed_query(query)
        results = self.milvus.search(
            collection_name=f"dataset_{dataset_id}",
            data=[query_emb], limit=top_k,
            output_fields=["content", "document_id", "chunk_index"],
            search_params={"metric_type": "COSINE", "params": {"nprobe": 16}}
        )
        return [{"content": h["entity"]["content"], "score": h["distance"],
                 "document_id": h["entity"]["document_id"]} for h in results[0]]
```

### 3. Agent Runtime (LangGraph)

```python
"""
Mini-Dify - Agent Runtime (LangGraph ReAct)
"""

from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool


class AgentRuntime:
    """Agent 运行时"""

    def __init__(self, model_hub, tool_registry):
        self.model_hub = model_hub
        self.tool_registry = tool_registry

    def create_agent(self, config):
        model = self.model_hub.get_model(
            config.provider_id, config.model_name,
            temperature=config.temperature
        )
        tools = self.tool_registry.get_tools(config.tool_ids)
        return create_react_agent(
            model=model, tools=tools,
            state_modifier=config.system_prompt
        )

    async def run(self, agent, message: str, history=None):
        messages = (history or []) + [{"role": "user", "content": message}]
        result = await agent.ainvoke({"messages": messages})
        return result["messages"][-1]

    async def stream(self, agent, message: str, history=None):
        messages = (history or []) + [{"role": "user", "content": message}]
        async for event in agent.astream_events({"messages": messages}, version="v2"):
            yield event
```

### 4. Workflow Engine (LangGraph StateGraph)

```python
"""
Mini-Dify - Workflow Engine (动态 LangGraph)
"""

from langgraph.graph import StateGraph
from typing import AsyncGenerator


class WorkflowEngine:
    """工作流引擎"""

    def build_graph(self, workflow_def: dict):
        graph = StateGraph(dict)

        for node in workflow_def["nodes"]:
            handler = self._get_node_handler(node["type"])
            graph.add_node(node["id"], handler(node["config"]))

        for edge in workflow_def["edges"]:
            if edge.get("condition"):
                graph.add_conditional_edges(
                    edge["source"],
                    self._build_condition(edge["condition"]),
                    edge["targets"]
                )
            else:
                graph.add_edge(edge["source"], edge["target"])

        graph.set_entry_point(workflow_def["entry"])
        return graph.compile()

    async def execute(self, workflow_id: str, inputs: dict) -> AsyncGenerator:
        graph = self._get_compiled_graph(workflow_id)
        async for event in graph.astream_events(inputs, version="v2"):
            yield {
                "node_id": event.get("name"),
                "status": event.get("event"),
                "data": event.get("data")
            }
```

## 新模块规范

1. **异步优先**: 所有 I/O 操作使用 `async/await`
2. **依赖注入**: 通过构造函数注入依赖，便于测试
3. **类型安全**: 所有函数标注类型提示
4. **日志记录**: 关键操作记录日志
5. **错误处理**: 使用自定义异常类

```python
# app/utils/exceptions.py
class MiniDifyError(Exception):
    """基础异常"""
    pass

class ProviderNotFoundError(MiniDifyError):
    pass

class ModelConnectionError(MiniDifyError):
    pass

class WorkflowExecutionError(MiniDifyError):
    pass
```
