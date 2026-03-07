"""
Mini-Dify - 模型管理 API
"""

import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.provider import Provider
from app.core.model_service import ModelService, ChatMessage
from app.schemas import (
    ProviderCreate,
    ProviderUpdate,
    ProviderResponse,
    HealthCheckResponse,
    ModelChatRequest,
)

router = APIRouter(prefix="/models", tags=["模型管理"])


# ==================== Provider CRUD ====================


@router.post("/providers", response_model=ProviderResponse, status_code=201)
async def create_provider(data: ProviderCreate, db: AsyncSession = Depends(get_db)):
    """添加模型供应商"""
    provider = Provider(**data.model_dump())
    db.add(provider)
    await db.commit()
    await db.refresh(provider)
    return provider


@router.get("/providers", response_model=list[ProviderResponse])
async def list_providers(db: AsyncSession = Depends(get_db)):
    """获取所有供应商"""
    result = await db.execute(select(Provider).order_by(Provider.created_at.desc()))
    return result.scalars().all()


@router.get("/providers/{provider_id}", response_model=ProviderResponse)
async def get_provider(provider_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取供应商详情"""
    provider = await db.get(Provider, provider_id)
    if not provider:
        raise HTTPException(404, "供应商不存在")
    return provider


@router.put("/providers/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    provider_id: UUID, data: ProviderUpdate, db: AsyncSession = Depends(get_db)
):
    """更新供应商配置"""
    provider = await db.get(Provider, provider_id)
    if not provider:
        raise HTTPException(404, "供应商不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(provider, key, value)
    await db.commit()
    await db.refresh(provider)
    return provider


@router.delete("/providers/{provider_id}", status_code=204)
async def delete_provider(provider_id: UUID, db: AsyncSession = Depends(get_db)):
    """删除供应商"""
    provider = await db.get(Provider, provider_id)
    if not provider:
        raise HTTPException(404, "供应商不存在")
    await db.delete(provider)
    await db.commit()


# ==================== Health Check ====================


@router.post("/providers/{provider_id}/health", response_model=HealthCheckResponse)
async def check_provider_health(provider_id: UUID, db: AsyncSession = Depends(get_db)):
    """检测供应商连通性"""
    provider = await db.get(Provider, provider_id)
    if not provider:
        raise HTTPException(404, "供应商不存在")

    # 取第一个可用模型做健康检查
    test_model = provider.models[0] if provider.models else "gpt-4o-mini"

    result = await ModelService.health_check(
        provider_type=provider.provider_type,
        api_key=provider.api_key,
        base_url=provider.base_url,
        model=test_model,
    )
    return HealthCheckResponse(
        status=result.status,
        latency_ms=result.latency_ms,
        error=result.error,
    )


# ==================== Chat (模型对话测试) ====================


@router.post("/chat")
async def chat_with_model(data: ModelChatRequest, db: AsyncSession = Depends(get_db)):
    """调用模型进行对话测试"""
    provider = await db.get(Provider, data.provider_id)
    if not provider:
        raise HTTPException(404, "供应商不存在")

    messages = [ChatMessage(role=m.role, content=m.content) for m in data.messages]

    if data.stream:
        # SSE 流式响应
        async def event_stream():
            try:
                async for chunk in ModelService.chat_stream(
                    provider_type=provider.provider_type,
                    messages=messages,
                    api_key=provider.api_key,
                    base_url=provider.base_url,
                    model=data.model,
                    temperature=data.temperature,
                    max_tokens=data.max_tokens,
                ):
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    else:
        # 非流式响应
        try:
            result = await ModelService.chat(
                provider_type=provider.provider_type,
                messages=messages,
                api_key=provider.api_key,
                base_url=provider.base_url,
                model=data.model,
                temperature=data.temperature,
                max_tokens=data.max_tokens,
            )
            return {
                "content": result.content,
                "input_tokens": result.input_tokens,
                "output_tokens": result.output_tokens,
                "latency_ms": result.latency_ms,
            }
        except Exception as e:
            raise HTTPException(500, f"模型调用失败: {str(e)}")
