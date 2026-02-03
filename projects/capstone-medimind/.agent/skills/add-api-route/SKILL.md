---
name: add-api-route
description: 为 MediMind 添加新的 FastAPI 路由接口
---

# 添加 API 路由技能

此技能用于为 MediMind 健康助手项目添加新的 FastAPI 路由接口。

## 项目结构

```
src/api/
├── main.py                 # 应用入口，注册路由
├── dependencies.py         # 依赖注入
├── schemas/
│   ├── __init__.py
│   ├── health.py           # 健康问答 schemas
│   ├── drug.py             # 药品查询 schemas
│   └── report.py           # 报告解读 schemas
├── routes/
│   ├── __init__.py
│   ├── health_qa.py        # 健康问答路由
│   ├── drug.py             # 药品查询路由
│   ├── report.py           # 报告解读路由
│   ├── triage.py           # 智能导诊路由
│   └── system.py           # 系统路由
└── middleware/
    └── guardrail.py        # 安全护栏中间件
```

## 创建新路由步骤

### 1. 在 `schemas/` 添加 Pydantic 模型

```python
# src/api/schemas/new_feature.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class NewFeatureRequest(BaseModel):
    """请求模型"""
    query: str = Field(..., min_length=1, max_length=1000)
    options: Optional[dict] = None

class NewFeatureResponse(BaseModel):
    """响应模型"""
    result: str
    sources: List[dict] = []
    disclaimer: str = "以上信息仅供参考，如有健康问题请咨询专业医生。"
```

### 2. 创建路由文件 `routes/new_feature.py`

```python
"""
MediMind - 新功能路由
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from src.api.dependencies import get_db_session, get_guardrail
from src.api.schemas.new_feature import (
    NewFeatureRequest,
    NewFeatureResponse,
)
from src.core.guardrails import Guardrail

router = APIRouter(prefix="/new-feature", tags=["新功能"])


@router.post("", response_model=NewFeatureResponse)
async def process_feature(
    request: NewFeatureRequest,
    guardrail: Guardrail = Depends(get_guardrail),
):
    """处理新功能请求"""
    # 1. 输入安全检查
    input_check = guardrail.check_input(request.query)
    if not input_check.passed:
        return NewFeatureResponse(
            result=input_check.message,
            sources=[],
        )

    # 2. 业务逻辑处理
    result = "处理结果"

    # 3. 输出合规检查
    output_check = guardrail.check_output(result)

    return NewFeatureResponse(
        result=output_check.content,
        sources=[],
    )
```

### 3. 在 `routes/__init__.py` 导出路由

```python
from .new_feature import router as new_feature_router

__all__ = [
    # ... 已有路由
    "new_feature_router",
]
```

### 4. 在 `main.py` 注册路由

```python
from src.api.routes import new_feature_router

# 在 create_app() 函数中添加
app.include_router(new_feature_router, prefix="/api/v1")
```

## MediMind 路由规范

### 命名规范

| HTTP 方法 | 路径模式   | 函数名        | 用途     |
| --------- | ---------- | ------------- | -------- |
| POST      | `/chat`    | `chat`        | 问答对话 |
| POST      | `/stream`  | `stream_chat` | 流式对话 |
| GET       | `/search`  | `search_xxx`  | 搜索查询 |
| GET       | `/{id}`    | `get_xxx`     | 获取详情 |
| POST      | `/analyze` | `analyze_xxx` | 分析处理 |

### 响应格式

```python
{
    "code": 0,          # 0 成功，非 0 错误
    "message": "success",
    "data": { ... },
    "disclaimer": "以上信息仅供参考..."  # 医疗合规声明
}
```

### 必须包含安全护栏

所有涉及用户输入的接口必须经过 Guardrail 检查：

```python
from src.api.dependencies import get_guardrail
from src.core.guardrails import Guardrail

@router.post("/xxx")
async def xxx(
    request: Request,
    guardrail: Guardrail = Depends(get_guardrail),
):
    # 输入检查
    input_check = guardrail.check_input(request.query)
    if not input_check.passed:
        # 处理紧急情况或拒绝请求
        ...

    # 输出检查
    output_check = guardrail.check_output(response)
```

## 流式响应示例

```python
from fastapi.responses import StreamingResponse

@router.post("/stream")
async def stream_chat(request: ChatRequest):
    """流式问答"""
    async def generate():
        async for chunk in rag_service.stream_answer(request.query):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )
```

## 测试新路由

```python
# tests/test_api.py
class TestNewFeatureAPI:
    def test_process_feature(self, client):
        response = client.post(
            "/api/v1/new-feature",
            json={"query": "测试问题"}
        )
        assert response.status_code == 200
        assert "disclaimer" in response.json()
```
