---
name: code-review
description: 审查 Mini-Dify 代码，确保符合项目架构和最佳实践
---

# 代码审查技能

此技能用于审查 Mini-Dify 项目代码，确保符合项目架构规范和 LLM 应用最佳实践。

## 审查清单

### 1. 项目架构

- [ ] **分层清晰**: API → Core → Models 三层分离
- [ ] **依赖方向**: 只允许上层依赖下层（API → Core → Models）
- [ ] **核心模块**: 不直接依赖 FastAPI（保持框架无关）
- [ ] **配置管理**: 通过 `config.py` 和 `.env` 管理，无硬编码

### 2. 后端规范

**FastAPI 路由**:

- [ ] 路由前缀统一 `/api/v1/xxx`
- [ ] 所有端点有 Pydantic Schema
- [ ] 响应格式统一 `{code, data, message}`
- [ ] 正确使用 HTTP 状态码
- [ ] 列表接口支持分页

**SQLAlchemy 模型**:

- [ ] 使用 UUID 主键 (`gen_random_uuid()`)
- [ ] 时间字段使用 `TIMESTAMPTZ`
- [ ] 可变数据使用 `JSONB` 而非 `TEXT` 存 JSON 字符串
- [ ] 外键有正确的级联策略
- [ ] 模式变更有 Alembic 迁移

**异步**:

- [ ] 数据库操作使用 `async/await`
- [ ] LLM 调用使用异步 API
- [ ] 不在异步函数中调用同步阻塞操作

### 3. LLM 特有审查

**Prompt 安全**:

- [ ] 无 Prompt 注入风险（用户输入不直接拼入系统 Prompt）
- [ ] 模板变量使用 Jinja2 安全渲染
- [ ] 系统 Prompt 和用户 Prompt 分离

**模型调用**:

- [ ] 通过 ModelHub 统一调用，不直接 import 供应商 SDK
- [ ] API Key 从数据库加密存储中获取，不硬编码
- [ ] 错误处理：超时、限流、无效 Key 等

**RAG 管道**:

- [ ] 文档切分参数可配置
- [ ] Embedding 模型可切换
- [ ] 检索结果有相似度得分
- [ ] Milvus Collection 按知识库隔离

**Agent**:

- [ ] 工具调用有超时保护
- [ ] 代码执行有沙箱限制
- [ ] 思考过程可追踪

**工作流**:

- [ ] 节点执行有超时限制
- [ ] 条件分支覆盖所有路径
- [ ] 支持错误节点中断
- [ ] 执行状态通过 SSE 实时推送

### 4. 前端规范

**React**:

- [ ] 组件使用函数式 + Hooks
- [ ] 复杂状态使用 Zustand
- [ ] API 调用有 loading/error 状态
- [ ] 列表有空状态展示

**TypeScript**:

- [ ] 所有 props 和 state 有类型定义
- [ ] API 响应有类型定义
- [ ] 避免 `any` 类型

**UI/UX**:

- [ ] 遵循设计规范 (indigo 主色, Inter 字体)
- [ ] 响应式布局 (mobile/tablet/desktop)
- [ ] SSE 流式有打字机效果
- [ ] 操作有加载反馈

### 5. 安全

- [ ] API Key 加密存储 (AES)
- [ ] API Key 界面脱敏显示
- [ ] 外部 API 调用需 Bearer Token 认证
- [ ] 代码执行节点限时 + 限制系统调用
- [ ] 文件上传限制类型和大小

## 常见问题模板

### 问题：直接拼接 Prompt

```python
# ❌ 错误
prompt = f"System: {system_prompt}\nUser: {user_input}"

# ✅ 正确
from langchain_core.messages import SystemMessage, HumanMessage
messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content=user_input),
]
```

### 问题：同步阻塞

```python
# ❌ 错误（在异步函数中调用同步）
async def process():
    result = requests.get(url)  # 同步阻塞！

# ✅ 正确
async def process():
    async with httpx.AsyncClient() as client:
        result = await client.get(url)
```

### 问题：JSON 存为 TEXT

```python
# ❌ 错误
config = Column(String)  # 存 JSON 字符串

# ✅ 正确
config = Column(JSONB, default=dict)  # PostgreSQL JSONB
```

### 问题：未处理 SSE 断连

```tsx
// ❌ 错误：不处理连接错误
const eventSource = new EventSource(url);
eventSource.onmessage = (e) => { ... }

// ✅ 正确：处理错误和重连
const eventSource = new EventSource(url);
eventSource.onmessage = (e) => { ... }
eventSource.onerror = (e) => {
  eventSource.close();
  // 显示错误提示或重试
}
```
