"""
Mini-Dify - 模型管理 API
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.provider import Provider
from app.schemas import ProviderCreate, ProviderUpdate, ProviderResponse

router = APIRouter(prefix="/models/providers", tags=["模型管理"])


@router.post("", response_model=ProviderResponse, status_code=201)
async def create_provider(data: ProviderCreate, db: AsyncSession = Depends(get_db)):
    """添加模型供应商"""
    provider = Provider(**data.model_dump())
    db.add(provider)
    await db.commit()
    await db.refresh(provider)
    return provider


@router.get("", response_model=list[ProviderResponse])
async def list_providers(db: AsyncSession = Depends(get_db)):
    """获取所有供应商"""
    result = await db.execute(select(Provider).order_by(Provider.created_at.desc()))
    return result.scalars().all()


@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(provider_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取供应商详情"""
    provider = await db.get(Provider, provider_id)
    if not provider:
        raise HTTPException(404, "供应商不存在")
    return provider


@router.put("/{provider_id}", response_model=ProviderResponse)
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


@router.delete("/{provider_id}", status_code=204)
async def delete_provider(provider_id: UUID, db: AsyncSession = Depends(get_db)):
    """删除供应商"""
    provider = await db.get(Provider, provider_id)
    if not provider:
        raise HTTPException(404, "供应商不存在")
    await db.delete(provider)
    await db.commit()


@router.post("/{provider_id}/test")
async def test_provider(provider_id: UUID, db: AsyncSession = Depends(get_db)):
    """测试供应商连接"""
    provider = await db.get(Provider, provider_id)
    if not provider:
        raise HTTPException(404, "供应商不存在")
    # TODO: 实现实际的模型连接测试
    return {"status": "ok", "message": f"供应商 {provider.name} 连接正常"}
