---
name: add-api-route
description: 为 Mini-Dify 添加新的 FastAPI 路由接口
---

# 添加 API 路由技能

此技能用于为 Mini-Dify 可视化 LLM 应用开发平台添加新的 FastAPI 路由接口。

## 项目结构

```
backend/app/
├── main.py                 # FastAPI 入口，注册路由
├── config.py               # 配置管理
├── database.py             # 数据库初始化 (async SQLAlchemy)
├── api/                    # API 路由层
│   ├── __init__.py
│   ├── deps.py             # 依赖注入
│   ├── models.py           # 模型管理 API
│   ├── prompts.py          # Prompt 管理 API
│   ├── datasets.py         # 知识库 API
│   ├── agents.py           # Agent 管理 API
│   ├── workflows.py        # 工作流 API
│   ├── apps.py             # 应用管理 API
│   ├── gateway.py          # API 网关
│   └── analytics.py        # 监控分析 API
├── schemas/                # Pydantic 请求/响应
│   └── ...
├── core/                   # 核心业务逻辑
│   └── ...
└── models/                 # SQLAlchemy 数据模型
    └── ...
```

## 创建新路由步骤

### 1. 在 `schemas/` 添加 Pydantic Schema

```python
# app/schemas/new_feature.py
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class NewFeatureCreate(BaseModel):
    """创建请求"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    config: dict = Field(default_factory=dict)


class NewFeatureUpdate(BaseModel):
    """更新请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[dict] = None


class NewFeatureResponse(BaseModel):
    """响应模型"""
    id: UUID
    name: str
    description: Optional[str]
    config: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

### 2. 创建路由文件 `api/new_feature.py`

```python
"""
Mini-Dify - 新功能路由
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.new_feature import (
    NewFeatureCreate,
    NewFeatureUpdate,
    NewFeatureResponse,
)

router = APIRouter(prefix="/new-feature", tags=["新功能"])


@router.post("", response_model=NewFeatureResponse, status_code=201)
async def create_feature(
    data: NewFeatureCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新资源"""
    # 业务逻辑
    pass


@router.get("", response_model=list[NewFeatureResponse])
async def list_features(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """查询列表"""
    pass


@router.get("/{feature_id}", response_model=NewFeatureResponse)
async def get_feature(
    feature_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """获取详情"""
    pass


@router.put("/{feature_id}", response_model=NewFeatureResponse)
async def update_feature(
    feature_id: UUID,
    data: NewFeatureUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新资源"""
    pass


@router.delete("/{feature_id}", status_code=204)
async def delete_feature(
    feature_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """删除资源"""
    pass
```

### 3. 在 `main.py` 注册路由

```python
from app.api.new_feature import router as new_feature_router

# 在 create_app() 中添加
app.include_router(new_feature_router, prefix="/api/v1")
```

## Mini-Dify 路由规范

### 命名规范

| HTTP 方法 | 路径模式       | 函数名       | 用途     |
| --------- | -------------- | ------------ | -------- |
| POST      | `/`            | `create_xxx` | 创建资源 |
| GET       | `/`            | `list_xxx`   | 列表查询 |
| GET       | `/{id}`        | `get_xxx`    | 获取详情 |
| PUT       | `/{id}`        | `update_xxx` | 更新资源 |
| DELETE    | `/{id}`        | `delete_xxx` | 删除资源 |
| POST      | `/{id}/action` | `action_xxx` | 特定操作 |

### 统一响应格式

```python
from app.schemas.common import ApiResponse

# 成功
{"code": 200, "data": {...}, "message": "success"}

# 错误
{"code": 400, "data": null, "message": "请求参数错误"}
```

### 分页规范

```python
@router.get("")
async def list_items(page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size
    items = await db.execute(select(Model).offset(offset).limit(page_size))
    total = await db.execute(select(func.count(Model.id)))
    return {"items": items, "total": total, "page": page, "page_size": page_size}
```

### 依赖注入

```python
from app.api.deps import get_db, get_model_hub, get_rag_pipeline

@router.post("/chat")
async def chat(
    db: AsyncSession = Depends(get_db),
    model_hub: ModelHub = Depends(get_model_hub),
):
    pass
```

## SSE 流式响应

```python
from fastapi.responses import StreamingResponse

@router.post("/{id}/chat")
async def stream_chat(request: ChatRequest):
    async def generate():
        async for chunk in service.stream(request):
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

## 测试新路由

```python
# tests/test_new_feature.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_feature(client: AsyncClient):
    response = await client.post(
        "/api/v1/new-feature",
        json={"name": "测试", "config": {}}
    )
    assert response.status_code == 201
    assert response.json()["data"]["name"] == "测试"
```
