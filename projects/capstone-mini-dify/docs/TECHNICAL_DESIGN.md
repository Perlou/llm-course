# Mini-Dify - 技术架构设计文档

> 版本: v1.0  
> 更新日期: 2026-03-06  
> 项目类型: LLM 课程毕业项目

---

## 1. 系统架构总览

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Mini-Dify 系统架构                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        Presentation Layer                         │   │
│  │  ┌──────────────────────────────────────────────────────────────┐│   │
│  │  │              React + TypeScript + TailwindCSS                 ││   │
│  │  │   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   ││   │
│  │  │   │Model   │ │Prompt  │ │Knowl-  │ │Agent   │ │Work-   │   ││   │
│  │  │   │Hub     │ │Studio  │ │edge    │ │Builder │ │flow    │   ││   │
│  │  │   └────────┘ └────────┘ └────────┘ └────────┘ └────────┘   ││   │
│  │  │   ┌────────┐ ┌────────┐ ┌────────────────────────────────┐  ││   │
│  │  │   │Apps    │ │Monitor │ │     Playground / Chat Widget    │  ││   │
│  │  │   └────────┘ └────────┘ └────────────────────────────────┘  ││   │
│  │  └──────────────────────────────────────────────────────────────┘│   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                          API Layer (FastAPI)                       │   │
│  │   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │   │
│  │   │/models   │ │/prompts  │ │/datasets │ │/agents   │          │   │
│  │   └──────────┘ └──────────┘ └──────────┘ └──────────┘          │   │
│  │   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │   │
│  │   │/workflows│ │/apps     │ │/gateway  │ │/analytics│          │   │
│  │   └──────────┘ └──────────┘ └──────────┘ └──────────┘          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        Service Layer                              │   │
│  │  ┌────────────┐ ┌─────────────┐ ┌─────────────┐                 │   │
│  │  │ Model Hub  │ │ Prompt      │ │ RAG         │                 │   │
│  │  │ Service    │ │ Engine      │ │ Pipeline    │                 │   │
│  │  │            │ │             │ │             │                 │   │
│  │  │ · 多供应商 │ │ · 模板解析  │ │ · 文档加载  │                 │   │
│  │  │ · 统一调用 │ │ · 变量注入  │ │ · 切分索引  │                 │   │
│  │  │ · 健康检查 │ │ · 版本管理  │ │ · 向量检索  │                 │   │
│  │  └────────────┘ └─────────────┘ └─────────────┘                 │   │
│  │  ┌────────────┐ ┌─────────────┐ ┌─────────────┐                 │   │
│  │  │ Agent      │ │ Workflow    │ │ LLM Ops     │                 │   │
│  │  │ Runtime    │ │ Engine      │ │ Service     │                 │   │
│  │  │            │ │             │ │             │                 │   │
│  │  │ · ReAct    │ │ · LangGraph │ │ · 日志记录  │                 │   │
│  │  │ · FC       │ │ · 节点执行  │ │ · Token统计 │                 │   │
│  │  │ · 工具管理 │ │ · 条件路由  │ │ · 成本分析  │                 │   │
│  │  └────────────┘ └─────────────┘ └─────────────┘                 │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        Storage Layer                              │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                 │   │
│  │  │ PostgreSQL │  │  Milvus    │  │ File System│                 │   │
│  │  │            │  │            │  │            │                 │   │
│  │  │ 元数据     │  │ 向量索引   │  │ 上传文档   │                 │   │
│  │  │ 配置数据   │  │ Embeddings │  │ 日志文件   │                 │   │
│  │  │ 对话日志   │  │            │  │            │                 │   │
│  │  └────────────┘  └────────────┘  └────────────┘                 │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 技术选型

| 层级 | 组件           | 技术选型                     | 选型理由                         |
| ---- | -------------- | ---------------------------- | -------------------------------- |
| 前端 | UI 框架        | React 18 + TypeScript        | 类型安全、生态丰富               |
| 前端 | 样式框架       | TailwindCSS                  | 快速原型、一致性                 |
| 前端 | 工作流编辑器   | React Flow                   | 开源、成熟的节点编辑器           |
| 前端 | 图表库         | Recharts                     | 基于 React、声明式 API           |
| 前端 | 构建工具       | Vite                         | 快速 HMR、ESBuild                |
| 前端 | 路由           | React Router v6              | 标准 SPA 路由                    |
| 前端 | 状态管理       | Zustand                      | 简洁轻量、无模板代码             |
| 前端 | HTTP 客户端    | Axios                        | 拦截器、流式支持                 |
| 后端 | API 框架       | FastAPI                      | 异步、自动文档、类型安全         |
| 后端 | ORM            | SQLAlchemy (async) + Alembic | 成熟 ORM + 数据库迁移管理        |
| 后端 | 数据验证       | Pydantic v2                  | 请求/响应 Schema 验证            |
| 后端 | LLM 框架       | LangChain                    | 统一模型接口、丰富工具链         |
| 后端 | 工作流引擎     | LangGraph                    | 图状态机、条件路由               |
| 存储 | 关系型数据库   | PostgreSQL 16 + asyncpg      | JSONB 支持、性能优秀、生产级     |
| 存储 | 向量数据库     | Milvus 2.x + pymilvus        | 高性能向量检索、支持多种索引类型 |
| 嵌入 | Embedding 模型 | bge-large-zh-v1.5            | 中文效果优秀、开源               |
| 部署 | 容器化         | Docker + Docker Compose      | 一键部署                         |

---

## 2. 核心模块设计

### 2.1 Model Hub 模块

#### 2.1.1 统一模型接口

```python
from abc import ABC, abstractmethod
from langchain_core.language_models import BaseChatModel

class ModelProvider(ABC):
    """模型供应商基类"""

    @abstractmethod
    def get_chat_model(self, model_name: str, **params) -> BaseChatModel:
        """获取聊天模型实例"""
        pass

    @abstractmethod
    def list_models(self) -> list[str]:
        """列出可用模型"""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """健康检查"""
        pass


class OpenAIProvider(ModelProvider):
    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url

    def get_chat_model(self, model_name: str, **params) -> BaseChatModel:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            **params
        )


class ModelHub:
    """模型管理中心 - 统一管理所有供应商和模型"""

    def __init__(self):
        self._providers: dict[str, ModelProvider] = {}

    def register_provider(self, name: str, provider: ModelProvider):
        self._providers[name] = provider

    def get_model(self, provider_name: str, model_name: str, **params) -> BaseChatModel:
        provider = self._providers[provider_name]
        return provider.get_chat_model(model_name, **params)
```

### 2.2 Prompt Engine 模块

#### 2.2.1 模板解析引擎

```python
import re
from jinja2 import Template

class PromptEngine:
    """Prompt 模板引擎"""

    VARIABLE_PATTERN = re.compile(r'\{\{(\w+)\}\}')

    def extract_variables(self, template: str) -> list[str]:
        """从模板中提取变量名"""
        return self.VARIABLE_PATTERN.findall(template)

    def render(self, template: str, variables: dict) -> str:
        """渲染 Prompt 模板"""
        jinja_template = Template(template)
        return jinja_template.render(**variables)

    async def test_prompt(
        self,
        template: str,
        variables: dict,
        model_configs: list[dict]
    ) -> list[dict]:
        """多模型对比测试"""
        rendered = self.render(template, variables)
        results = []
        for config in model_configs:
            model = self.model_hub.get_model(**config)
            response = await model.ainvoke(rendered)
            results.append({
                "model": config["model_name"],
                "response": response.content,
                "tokens": response.usage_metadata
            })
        return results
```

### 2.3 RAG Pipeline 模块

#### 2.3.1 文档处理与检索流程

```
用户上传文档
      │
      ▼
┌──────────────┐
│  文档加载器   │  PyPDF, Markdown, DOCX
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  文本切分器   │  RecursiveCharacterTextSplitter
│              │  可配置: chunk_size, overlap
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Embedding   │  BGE-Large-ZH / OpenAI Embedding
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Milvus      │  持久化存储，每个知识库独立 collection
└──────┬───────┘
       │
       ▼
  可供检索使用
```

#### 2.3.2 检索服务

```python
from pymilvus import MilvusClient, DataType, CollectionSchema, FieldSchema

class RAGPipeline:
    """RAG 管道 - 基于 Milvus 向量数据库"""

    def __init__(self, embedder, milvus_client: MilvusClient):
        self.embedder = embedder
        self.milvus = milvus_client

    def _get_collection_name(self, dataset_id: str) -> str:
        return f"dataset_{dataset_id}"

    async def create_collection(self, dataset_id: str, dimension: int = 1024):
        """为知识库创建 Milvus Collection"""
        collection = self._get_collection_name(dataset_id)
        schema = CollectionSchema([
            FieldSchema("id", DataType.VARCHAR, is_primary=True, max_length=36),
            FieldSchema("content", DataType.VARCHAR, max_length=65535),
            FieldSchema("document_id", DataType.VARCHAR, max_length=36),
            FieldSchema("chunk_index", DataType.INT64),
            FieldSchema("embedding", DataType.FLOAT_VECTOR, dim=dimension),
        ])
        self.milvus.create_collection(collection, schema=schema)
        # 创建向量索引 (IVF_FLAT)
        self.milvus.create_index(collection, "embedding", {
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 128}
        })

    async def ingest_document(
        self,
        file_path: str,
        dataset_id: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> int:
        """文档摄入"""
        # 1. 加载文档
        docs = self._load_document(file_path)
        # 2. 切分
        chunks = self._split_text(docs, chunk_size, chunk_overlap)
        # 3. 嵌入
        embeddings = self.embedder.embed_documents([c.page_content for c in chunks])
        # 4. 写入 Milvus
        collection = self._get_collection_name(dataset_id)
        data = [{
            "id": str(uuid4()),
            "content": chunk.page_content,
            "document_id": chunk.metadata["document_id"],
            "chunk_index": i,
            "embedding": embedding
        } for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))]
        self.milvus.insert(collection, data)
        return len(chunks)

    async def retrieve(
        self,
        query: str,
        dataset_id: str,
        top_k: int = 5,
        strategy: str = "similarity"
    ) -> list[dict]:
        """检索相关内容"""
        collection = self._get_collection_name(dataset_id)
        query_embedding = self.embedder.embed_query(query)
        results = self.milvus.search(
            collection_name=collection,
            data=[query_embedding],
            limit=top_k,
            output_fields=["content", "document_id", "chunk_index"],
            search_params={"metric_type": "COSINE", "params": {"nprobe": 16}}
        )
        return [{
            "content": hit["entity"]["content"],
            "score": hit["distance"],
            "document_id": hit["entity"]["document_id"],
            "chunk_index": hit["entity"]["chunk_index"]
        } for hit in results[0]]
```

### 2.4 Agent Runtime 模块

```python
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

class AgentRuntime:
    """Agent 运行时"""

    def __init__(self, model_hub: ModelHub, tool_registry: ToolRegistry):
        self.model_hub = model_hub
        self.tool_registry = tool_registry

    def create_agent(self, config: AgentConfig):
        """根据配置创建 Agent"""
        # 1. 获取模型
        model = self.model_hub.get_model(
            config.provider, config.model_name,
            temperature=config.temperature
        )
        # 2. 收集工具
        tools = self.tool_registry.get_tools(config.tool_ids)
        # 3. 创建 Agent (LangGraph ReAct)
        agent = create_react_agent(
            model=model,
            tools=tools,
            state_modifier=config.system_prompt
        )
        return agent

    async def run(self, agent, message: str, history: list = None):
        """执行 Agent"""
        messages = (history or []) + [{"role": "user", "content": message}]
        result = await agent.ainvoke({"messages": messages})
        return result["messages"][-1]
```

### 2.5 Workflow Engine 模块 ⭐

#### 2.5.1 工作流执行架构

```
┌─────────────────────────────────────────────────────────┐
│                   Workflow Engine                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  前端 (React Flow)           后端 (LangGraph)            │
│  ┌────────────────┐         ┌────────────────┐          │
│  │ 节点拖拽/连线   │  JSON   │ 解析 workflow  │          │
│  │ 节点配置面板    │ ─────→  │ 定义           │          │
│  │ 实时预览       │         │                │          │
│  └────────────────┘         │ 动态构建       │          │
│                             │ StateGraph     │          │
│                             │                │          │
│  ┌────────────────┐         │ 执行并返回     │          │
│  │ 展示执行结果    │ ←─────  │ 每个节点输出   │          │
│  │ 节点状态高亮    │  SSE    │                │          │
│  └────────────────┘         └────────────────┘          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

#### 2.5.2 节点类型定义

```python
from enum import Enum

class NodeType(str, Enum):
    START = "start"           # 开始节点
    LLM = "llm"             # 大模型调用
    KNOWLEDGE = "knowledge"  # 知识库检索
    CONDITION = "condition"  # 条件分支
    CODE = "code"           # 代码执行
    HTTP = "http"           # HTTP 请求
    END = "end"             # 结束节点


class WorkflowEngine:
    """工作流引擎 - 基于 LangGraph"""

    def build_graph(self, workflow_def: dict) -> CompiledGraph:
        """从 JSON 定义动态构建 LangGraph"""
        graph = StateGraph(WorkflowState)

        # 1. 添加所有节点
        for node in workflow_def["nodes"]:
            handler = self._get_node_handler(node["type"])
            graph.add_node(node["id"], handler(node["config"]))

        # 2. 添加边
        for edge in workflow_def["edges"]:
            if edge.get("condition"):
                graph.add_conditional_edges(
                    edge["source"], self._build_condition(edge["condition"]),
                    edge["targets"]
                )
            else:
                graph.add_edge(edge["source"], edge["target"])

        # 3. 设置入口和出口
        graph.set_entry_point(workflow_def["entry"])
        return graph.compile()

    async def execute(self, workflow_id: str, inputs: dict) -> AsyncGenerator:
        """执行工作流，流式返回每个节点的结果"""
        graph = self._get_compiled_graph(workflow_id)
        async for event in graph.astream_events(inputs, version="v2"):
            yield {
                "node_id": event.get("name"),
                "status": event.get("event"),
                "data": event.get("data")
            }
```

### 2.6 LLMOps 模块

```python
class LLMOpsService:
    """LLM 运维监控服务"""

    async def log_conversation(self, log: ConversationLog):
        """记录对话日志"""
        await self.db.insert(log)

    async def get_token_stats(self, app_id: str, period: str) -> TokenStats:
        """获取 Token 用量统计"""
        logs = await self.db.query(
            app_id=app_id,
            period=period
        )
        return TokenStats(
            total_input_tokens=sum(l.input_tokens for l in logs),
            total_output_tokens=sum(l.output_tokens for l in logs),
            total_cost=self._calculate_cost(logs),
            daily_breakdown=self._group_by_day(logs)
        )
```

---

## 3. 目录结构设计

```
capstone-mini-dify/
├── backend/                          # Python 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI 入口
│   │   ├── config.py                # 配置管理
│   │   ├── database.py              # 数据库初始化
│   │   │
│   │   ├── api/                     # API 路由层
│   │   │   ├── __init__.py
│   │   │   ├── deps.py              # 依赖注入
│   │   │   ├── models.py            # 模型管理 API
│   │   │   ├── prompts.py           # Prompt 管理 API
│   │   │   ├── datasets.py          # 知识库 API
│   │   │   ├── agents.py            # Agent 管理 API
│   │   │   ├── workflows.py         # 工作流 API
│   │   │   ├── apps.py              # 应用管理 API
│   │   │   ├── gateway.py           # API 网关
│   │   │   └── analytics.py         # 监控分析 API
│   │   │
│   │   ├── core/                    # 核心业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── model_hub.py         # 多模型管理
│   │   │   ├── prompt_engine.py     # Prompt 引擎
│   │   │   ├── rag_pipeline.py      # RAG 管道
│   │   │   ├── agent_runtime.py     # Agent 运行时
│   │   │   ├── workflow_engine.py   # 工作流引擎
│   │   │   ├── tool_registry.py     # 工具注册表
│   │   │   └── llm_ops.py          # LLMOps 监控
│   │   │
│   │   ├── models/                  # 数据模型 (SQLAlchemy)
│   │   │   ├── __init__.py
│   │   │   ├── provider.py          # 供应商模型
│   │   │   ├── prompt.py            # Prompt 模型
│   │   │   ├── dataset.py           # 知识库模型
│   │   │   ├── agent.py             # Agent 模型
│   │   │   ├── workflow.py          # 工作流模型
│   │   │   ├── app.py               # 应用模型
│   │   │   └── log.py               # 日志模型
│   │   │
│   │   ├── schemas/                 # Pydantic 请求/响应
│   │   │   ├── __init__.py
│   │   │   └── ...
│   │   │
│   │   └── utils/                   # 工具函数
│   │       ├── __init__.py
│   │       ├── crypto.py            # 加密工具
│   │       └── logger.py            # 日志工具
│   │
│   ├── alembic/                     # 数据库迁移
│   │   ├── env.py
│   │   ├── versions/               # 迁移版本
│   │   └── alembic.ini
│   │
│   ├── tests/                       # 测试
│   │   ├── test_model_hub.py
│   │   ├── test_rag.py
│   │   ├── test_workflow.py
│   │   └── ...
│   │
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                         # React 前端
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   │
│   │   ├── pages/                   # 页面组件
│   │   │   ├── ModelHub/            # 模型管理
│   │   │   ├── PromptStudio/        # Prompt 工坊
│   │   │   ├── Datasets/           # 知识库管理
│   │   │   ├── AgentBuilder/        # Agent 构建
│   │   │   ├── Workflow/            # 工作流编辑
│   │   │   ├── Apps/                # 应用管理
│   │   │   ├── Analytics/           # 监控面板
│   │   │   └── Playground/          # 测试游乐场
│   │   │
│   │   ├── components/              # 通用组件
│   │   │   ├── Layout/
│   │   │   ├── Chat/
│   │   │   └── common/
│   │   │
│   │   ├── services/                # API 调用
│   │   │   └── api.ts
│   │   │
│   │   ├── stores/                  # 状态管理 (Zustand)
│   │   │   └── ...
│   │   │
│   │   └── types/                   # TypeScript 类型
│   │       └── index.ts
│   │
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── data/                             # 数据存储
│   └── uploads/                     # 上传文件
│
├── scripts/                          # 运维脚本
│   ├── start.sh
│   ├── stop.sh
│   └── init_db.py
│
├── docker/                           # Docker 配置
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yaml
│
├── docs/                             # 项目文档
│   ├── PRD.md
│   ├── TECHNICAL_DESIGN.md
│   ├── DATABASE_DESIGN.md
│   ├── API_DESIGN.md
│   ├── UI_DESIGN.md
│   └── PROGRESS_TRACKER.md
│
├── .env.example
├── .gitignore
└── README.md
```

---

## 4. 数据流设计

### 4.1 Chatbot 应用调用链路

```
用户发送消息
      │
      ▼
┌──────────────┐
│ API Gateway  │  验证 API Key → 限流检查
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ App Manager  │  加载应用配置 (绑定的 Agent/知识库)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Agent Runtime│  执行 Agent（可能调用多个工具）
│              │   ├── 知识库检索 (RAG Pipeline)
│              │   ├── Web 搜索
│              │   └── 代码执行
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ LLM Ops      │  记录日志、统计 Token
└──────┬───────┘
       │
       ▼
   返回响应 (SSE 流式)
```

### 4.2 工作流执行链路

```
触发工作流执行 (手动 / API)
      │
      ▼
┌──────────────┐
│ Workflow     │  加载工作流 JSON 定义
│ Engine       │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Build Graph  │  动态构建 LangGraph StateGraph
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Execute      │  按拓扑顺序执行节点
│ Nodes        │
│              │  Start → Node1 → Condition → Node2/Node3 → End
└──────┬───────┘
       │
       ▼
   SSE 流式返回每个节点的执行状态和输出
```

---

## 5. 部署架构

### 5.1 Docker Compose

```yaml
# docker/docker-compose.yaml
version: "3.8"

services:
  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=mini_dify
      - POSTGRES_USER=mini_dify
      - POSTGRES_PASSWORD=mini_dify_secret
    volumes:
      - pg_data:/var/lib/postgresql/data
    restart: unless-stopped

  milvus:
    image: milvusdb/milvus:v2.4-latest
    ports:
      - "19530:19530" # gRPC
      - "9091:9091" # Health check
    environment:
      - ETCD_USE_EMBED=true
      - COMMON_STORAGETYPE=local
    volumes:
      - milvus_data:/var/lib/milvus
    restart: unless-stopped

  backend:
    build:
      context: ../
      dockerfile: docker/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://mini_dify:mini_dify_secret@postgres:5432/mini_dify
      - MILVUS_HOST=milvus
      - MILVUS_PORT=19530
    volumes:
      - ../data/uploads:/app/data/uploads
    depends_on:
      - postgres
      - milvus
    restart: unless-stopped

  frontend:
    build:
      context: ../frontend
      dockerfile: ../docker/Dockerfile.frontend
    ports:
      - "5173:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  pg_data:
  milvus_data:
```

---

## 6. 关键技术决策

| 决策点       | 选择                 | 备选方案            | 理由                              |
| ------------ | -------------------- | ------------------- | --------------------------------- |
| 数据库       | PostgreSQL + asyncpg | SQLite / MySQL      | JSONB 原生支持、高并发、生产级    |
| ORM          | SQLAlchemy + Alembic | SQLModel / Tortoise | 最成熟的 Python ORM、迁移管理完善 |
| 向量数据库   | Milvus               | ChromaDB/Pinecone   | 高性能、多索引类型、生产级可扩展  |
| 工作流编辑器 | React Flow           | 自研 Canvas         | 成熟开源、文档完善                |
| 状态管理     | Zustand              | Redux / Context     | 简洁、无模板代码、适合中型应用    |
| Agent 框架   | LangGraph            | 自研 Agent Loop     | 与课程一致、功能强大              |
| 前端框架     | Vite + React         | Next.js             | CSR 足够、无需 SSR                |
