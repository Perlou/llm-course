# Mini-Dify - API 设计文档

> 版本: v1.0  
> 基础路径: `/api/v1`  
> 更新日期: 2026-03-06

---

## 0. 系统健康检查

### GET /health

系统健康检查（用于 Docker 或监控）。

**响应**:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "milvus": "connected"
  }
}
```

---

## 1. 模型管理 API

### POST /models/providers

添加模型供应商。

**请求**:

```json
{
  "name": "OpenAI",
  "provider_type": "openai",
  "api_key": "sk-xxx...",
  "base_url": null,
  "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
}
```

**响应**:

```json
{
  "code": 200,
  "data": {
    "id": "prov_xxx",
    "name": "OpenAI",
    "provider_type": "openai",
    "api_key": "sk-xxx...***",
    "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
    "is_active": true
  }
}
```

---

### GET /models/providers

获取供应商列表。

---

### PUT /models/providers/{provider_id}

更新供应商信息。

---

### DELETE /models/providers/{provider_id}

删除供应商。

---

### POST /models/providers/{provider_id}/health

检测供应商连通性。

**响应**:

```json
{
  "code": 200,
  "data": {
    "status": "healthy",
    "latency_ms": 234,
    "available_models": ["gpt-4o", "gpt-4o-mini"]
  }
}
```

---

### POST /models/chat

调用模型进行对话（用于测试）。

**请求**:

```json
{
  "provider_id": "prov_xxx",
  "model": "gpt-4o",
  "messages": [
    { "role": "system", "content": "You are a helpful assistant." },
    { "role": "user", "content": "Hello!" }
  ],
  "temperature": 0.7,
  "max_tokens": 1024,
  "stream": true
}
```

**响应**: SSE 流式

```
data: {"content": "Hello", "finish_reason": null}
data: {"content": "!", "finish_reason": null}
data: {"content": "", "finish_reason": "stop", "usage": {"input_tokens": 15, "output_tokens": 2}}
```

---

## 2. Prompt 管理 API

### POST /prompts

创建 Prompt 模板。

**请求**:

```json
{
  "name": "翻译助手",
  "description": "多语言翻译 Prompt",
  "system_prompt": "你是一个专业的翻译助手，擅长{{source_lang}}到{{target_lang}}的翻译。",
  "user_prompt": "请翻译以下内容：\n\n{{text}}",
  "tags": "翻译,多语言"
}
```

---

### GET /prompts

获取 Prompt 列表。

**参数**: `tag` (可选)、`page`、`page_size`

---

### GET /prompts/{prompt_id}

获取 Prompt 详情。

---

### PUT /prompts/{prompt_id}

更新 Prompt（自动创建新版本）。

---

### DELETE /prompts/{prompt_id}

删除 Prompt。

---

### GET /prompts/{prompt_id}/versions

获取版本历史。

---

### POST /prompts/{prompt_id}/versions/{version}/rollback

回滚到指定版本。

---

### POST /prompts/{prompt_id}/test

测试 Prompt（多模型对比）。

**请求**:

```json
{
  "variables": {
    "source_lang": "中文",
    "target_lang": "英文",
    "text": "你好世界"
  },
  "model_configs": [
    { "provider_id": "prov_1", "model": "gpt-4o" },
    { "provider_id": "prov_2", "model": "claude-3.5-sonnet" }
  ]
}
```

**响应**:

```json
{
  "code": 200,
  "data": {
    "results": [
      {
        "model": "gpt-4o",
        "response": "Hello World",
        "input_tokens": 45,
        "output_tokens": 3,
        "latency_ms": 890
      },
      {
        "model": "claude-3.5-sonnet",
        "response": "Hello, World",
        "input_tokens": 42,
        "output_tokens": 4,
        "latency_ms": 1200
      }
    ]
  }
}
```

---

## 3. 知识库 API

### POST /datasets

创建知识库。

**请求**:

```json
{
  "name": "产品文档库",
  "description": "公司产品的技术文档集合",
  "embedding_model": "bge-large-zh",
  "chunk_size": 500,
  "chunk_overlap": 50,
  "retrieval_strategy": "similarity"
}
```

---

### GET /datasets

获取知识库列表。

---

### GET /datasets/{dataset_id}

获取知识库详情（含文档列表）。

---

### PUT /datasets/{dataset_id}

更新知识库配置。

---

### DELETE /datasets/{dataset_id}

删除知识库（同时删除所有文档和向量索引）。

---

### POST /datasets/{dataset_id}/documents

上传文档到知识库。

**请求**: `multipart/form-data`

- `file`: 文件 (PDF/MD/TXT/DOCX)

**响应**:

```json
{
  "code": 200,
  "data": {
    "document_id": "doc_xxx",
    "name": "product_manual.pdf",
    "file_type": "pdf",
    "file_size": 1024000,
    "chunk_count": 42,
    "status": "completed"
  }
}
```

---

### DELETE /datasets/{dataset_id}/documents/{document_id}

删除文档。

---

### POST /datasets/{dataset_id}/retrieve

检索测试。

**请求**:

```json
{
  "query": "如何配置系统参数？",
  "top_k": 5,
  "strategy": "similarity"
}
```

**响应**:

```json
{
  "code": 200,
  "data": {
    "results": [
      {
        "content": "系统参数可以通过配置文件进行设置...",
        "score": 0.92,
        "document_name": "product_manual.pdf",
        "chunk_index": 15
      }
    ]
  }
}
```

---

## 4. Agent 管理 API

### POST /agents

创建 Agent。

**请求**:

```json
{
  "name": "客服助手",
  "description": "智能客服 Agent",
  "system_prompt": "你是一个专业的客服助手，擅长回答产品相关问题。",
  "provider_id": "prov_xxx",
  "model_name": "gpt-4o",
  "temperature": 0.7,
  "strategy": "react",
  "tool_ids": ["tool_web_search", "tool_knowledge"],
  "dataset_ids": ["ds_xxx"]
}
```

---

### GET /agents

获取 Agent 列表。

---

### GET /agents/{agent_id}

获取 Agent 详情。

---

### PUT /agents/{agent_id}

更新 Agent。

---

### DELETE /agents/{agent_id}

删除 Agent。

---

### POST /agents/{agent_id}/chat

Agent 对话测试 (Playground)。

**请求**:

```json
{
  "message": "你们的产品支持哪些功能？",
  "conversation_id": "conv_xxx"
}
```

**响应**: SSE 流式

```
data: {"type": "thought", "content": "用户想了解产品功能，我应该查询知识库"}
data: {"type": "tool_call", "tool": "knowledge_retrieval", "input": {"query": "产品功能"}}
data: {"type": "tool_result", "content": "产品支持以下功能：..."}
data: {"type": "message", "content": "根据产品文档，我们的产品支持以下功能：\n1. ..."}
data: {"type": "done", "usage": {"input_tokens": 150, "output_tokens": 80}}
```

---

## 4.5 工具管理 API

### GET /tools

获取工具列表。

**参数**: `tool_type` (可选, builtin/custom)

**响应**:

```json
{
  "code": 200,
  "data": [
    {
      "id": "tool_xxx",
      "name": "web_search",
      "description": "搜索互联网获取实时信息",
      "tool_type": "builtin",
      "parameters": { "query": { "type": "string", "required": true } },
      "is_active": true
    }
  ]
}
```

---

### POST /tools

创建自定义工具。

**请求**:

```json
{
  "name": "price_lookup",
  "description": "查询商品价格",
  "parameters": {
    "product_name": { "type": "string", "required": true }
  },
  "code": "def run(product_name: str) -> str:\n    # 自定义逻辑\n    return f'{product_name} 价格为 99 元'"
}
```

---

### PUT /tools/{tool_id}

更新自定义工具。

---

### DELETE /tools/{tool_id}

删除自定义工具（内置工具不可删除）。

---

## 5. 工作流 API

### POST /workflows

创建工作流。

**请求**:

```json
{
  "name": "智能客服工作流",
  "description": "自动分类用户意图并回复",
  "graph_data": {
    "nodes": [...],
    "edges": [...]
  }
}
```

---

### GET /workflows

获取工作流列表。

---

### GET /workflows/{workflow_id}

获取工作流详情（含完整图数据）。

---

### PUT /workflows/{workflow_id}

更新工作流（保存画布）。

---

### DELETE /workflows/{workflow_id}

删除工作流。

---

### POST /workflows/{workflow_id}/run

执行工作流。

**请求**:

```json
{
  "inputs": {
    "user_message": "我要退换货"
  }
}
```

**响应**: SSE 流式 (实时返回每个节点的执行状态)

```
data: {"node_id": "node_1", "status": "running", "type": "start"}
data: {"node_id": "node_1", "status": "completed"}
data: {"node_id": "node_2", "status": "running", "type": "llm"}
data: {"node_id": "node_2", "status": "completed", "output": "意图: 退换货"}
data: {"node_id": "node_3", "status": "running", "type": "condition"}
data: {"node_id": "node_3", "status": "completed", "branch": "退换货"}
data: {"node_id": "node_5", "status": "running", "type": "llm"}
data: {"node_id": "node_5", "status": "completed", "output": "好的，请您提供订单号..."}
data: {"type": "workflow_completed", "final_output": "好的，请您提供订单号..."}
```

---

## 6. 应用管理 API

### POST /apps

创建应用。

**请求**:

```json
{
  "name": "产品客服",
  "description": "产品智能客服对话机器人",
  "app_type": "chatbot",
  "config": {
    "agent_id": "agent_xxx",
    "welcome_message": "您好！我是产品客服助手，请问有什么可以帮您？",
    "suggested_questions": ["产品有哪些功能？", "如何退换货？"]
  }
}
```

---

### GET /apps

获取应用列表。

---

### PUT /apps/{app_id}

更新应用。

---

### DELETE /apps/{app_id}

删除应用。

---

### POST /apps/{app_id}/publish

发布应用（生成 API Key）。

**响应**:

```json
{
  "code": 200,
  "data": {
    "api_key": "md-xxxxxxxxxxxxxxxxxxxx",
    "api_endpoint": "/api/v1/gateway/{app_id}/chat"
  }
}
```

---

### GET /apps/{app_id}/api-keys

获取应用的 API Key 列表。

---

### DELETE /apps/{app_id}/api-keys/{key_id}

吊销 API Key。

---

## 7. API 网关 (对外接口)

### POST /gateway/{app_id}/chat

通过 API 调用已发布的应用。

**请求头**:

```
Authorization: Bearer md-xxxxxxxxxxxxxxxxxxxx
```

**请求**:

```json
{
  "message": "你好",
  "conversation_id": "conv_xxx",
  "stream": true
}
```

**响应** (stream=true): SSE 流式

```
data: {"content": "你好", "conversation_id": "conv_xxx"}
data: {"content": "！有什么", "conversation_id": "conv_xxx"}
data: {"content": "可以帮您的？", "conversation_id": "conv_xxx", "finish_reason": "stop"}
```

**响应** (stream=false):

```json
{
  "code": 200,
  "data": {
    "message": "你好！有什么可以帮您的？",
    "conversation_id": "conv_xxx",
    "usage": { "input_tokens": 10, "output_tokens": 8 }
  }
}
```

---

### POST /gateway/{app_id}/completion

文本生成接口 (Completion 类型应用)。

**请求**:

```json
{
  "variables": { "topic": "人工智能" },
  "stream": false
}
```

---

### POST /gateway/{app_id}/workflow

触发工作流执行 (Workflow 类型应用)。

**请求**:

```json
{
  "inputs": { "user_message": "帮我分析这份报告" }
}
```

---

## 8. 监控分析 API

### GET /analytics/overview

获取全局统计概览。

**响应**:

```json
{
  "code": 200,
  "data": {
    "total_conversations": 1234,
    "total_tokens": 567890,
    "total_cost_usd": 12.34,
    "active_apps": 5,
    "today_conversations": 42
  }
}
```

---

### GET /analytics/tokens

Token 用量统计。

**参数**: `app_id` (可选)、`period` (7d/30d/90d)

**响应**:

```json
{
  "code": 200,
  "data": {
    "total_input_tokens": 123456,
    "total_output_tokens": 78901,
    "daily_breakdown": [
      { "date": "2026-03-06", "input": 5000, "output": 3000, "cost": 0.5 },
      { "date": "2026-03-05", "input": 4500, "output": 2800, "cost": 0.45 }
    ]
  }
}
```

---

### GET /analytics/conversations

对话日志列表。

**参数**: `app_id`、`page`、`page_size`

**响应**:

```json
{
  "code": 200,
  "data": {
    "conversations": [
      {
        "conversation_id": "conv_xxx",
        "app_name": "产品客服",
        "message_count": 6,
        "total_tokens": 450,
        "created_at": "2026-03-06T10:00:00Z"
      }
    ],
    "total": 100
  }
}
```

---

### GET /analytics/conversations/{conversation_id}

获取对话详情（完整消息列表）。

---

## 9. 通用约定

### 9.1 响应格式

所有 API 统一响应格式：

```json
{
  "code": 200,
  "data": { ... },
  "message": "success"
}
```

### 9.2 错误码

| 错误码 | 说明         |
| ------ | ------------ |
| 400    | 请求参数错误 |
| 401    | API Key 无效 |
| 404    | 资源不存在   |
| 429    | 请求频率超限 |
| 500    | 服务内部错误 |

### 9.3 分页

列表接口统一支持分页：

**参数**: `page` (默认 1)、`page_size` (默认 20, 最大 100)

**响应**:

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```
