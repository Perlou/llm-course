"""
Mini-Dify - 应用管理 API
"""

import secrets
import hashlib
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.app import App, AppApiKey
from app.schemas import AppCreate, AppUpdate, AppResponse

router = APIRouter(prefix="/apps", tags=["应用管理"])


@router.post("", response_model=AppResponse, status_code=201)
async def create_app(data: AppCreate, db: AsyncSession = Depends(get_db)):
    """创建应用"""
    app = App(**data.model_dump())
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return app


@router.get("", response_model=list[AppResponse])
async def list_apps(db: AsyncSession = Depends(get_db)):
    """获取应用列表"""
    result = await db.execute(select(App).order_by(App.updated_at.desc()))
    return result.scalars().all()


@router.get("/{app_id}", response_model=AppResponse)
async def get_app(app_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取应用详情"""
    app = await db.get(App, app_id)
    if not app:
        raise HTTPException(404, "应用不存在")
    return app


@router.put("/{app_id}", response_model=AppResponse)
async def update_app(app_id: UUID, data: AppUpdate, db: AsyncSession = Depends(get_db)):
    """更新应用"""
    app = await db.get(App, app_id)
    if not app:
        raise HTTPException(404, "应用不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(app, key, value)
    await db.commit()
    await db.refresh(app)
    return app


@router.delete("/{app_id}", status_code=204)
async def delete_app(app_id: UUID, db: AsyncSession = Depends(get_db)):
    """删除应用"""
    app = await db.get(App, app_id)
    if not app:
        raise HTTPException(404, "应用不存在")
    await db.delete(app)
    await db.commit()


@router.post("/{app_id}/api-keys")
async def create_api_key(
    app_id: UUID, name: str = "default", db: AsyncSession = Depends(get_db)
):
    """为应用生成 API Key"""
    app = await db.get(App, app_id)
    if not app:
        raise HTTPException(404, "应用不存在")

    raw_key = f"md-{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    api_key = AppApiKey(
        app_id=app_id,
        key_prefix=raw_key[:7],
        key_hash=key_hash,
        name=name,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return {
        "id": str(api_key.id),
        "key": raw_key,
        "prefix": api_key.key_prefix,
        "name": api_key.name,
        "message": "请保存此 API Key，它不会再次显示",
    }


@router.get("/{app_id}/api-keys")
async def list_api_keys(app_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取应用的 API Key 列表（脱敏显示）"""
    result = await db.execute(
        select(AppApiKey)
        .where(AppApiKey.app_id == app_id)
        .order_by(AppApiKey.created_at.desc())
    )
    keys = result.scalars().all()
    return [
        {
            "id": str(k.id),
            "prefix": k.key_prefix,
            "name": k.name,
            "is_active": k.is_active,
            "last_used": k.last_used,
            "created_at": k.created_at,
        }
        for k in keys
    ]


@router.delete("/{app_id}/api-keys/{key_id}", status_code=204)
async def delete_api_key(
    app_id: UUID, key_id: UUID, db: AsyncSession = Depends(get_db)
):
    """删除 API Key"""
    api_key = await db.get(AppApiKey, key_id)
    if not api_key or api_key.app_id != app_id:
        raise HTTPException(404, "API Key 不存在")
    await db.delete(api_key)
    await db.commit()
