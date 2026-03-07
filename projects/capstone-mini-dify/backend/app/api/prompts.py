"""
Mini-Dify - Prompt 管理 API
"""

import re
import asyncio
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.provider import Provider
from app.models.prompt import Prompt, PromptVersion
from app.core.model_service import ModelService, ChatMessage
from app.schemas import (
    PromptCreate,
    PromptUpdate,
    PromptResponse,
    PromptVersionResponse,
    PromptTestRequest,
    PromptTestResponse,
    PromptTestResultItem,
)

router = APIRouter(prefix="/prompts", tags=["Prompt 管理"])


# ==================== CRUD ====================


@router.post("", response_model=PromptResponse, status_code=201)
async def create_prompt(data: PromptCreate, db: AsyncSession = Depends(get_db)):
    """创建 Prompt 模板"""
    prompt = Prompt(**data.model_dump())
    db.add(prompt)
    await db.commit()
    await db.refresh(prompt)

    # 创建初始版本
    version = PromptVersion(
        prompt_id=prompt.id,
        version=1,
        system_prompt=data.system_prompt,
        user_prompt=data.user_prompt,
        change_note="初始版本",
    )
    db.add(version)
    await db.commit()

    return prompt


@router.get("", response_model=list[PromptResponse])
async def list_prompts(tag: str = None, db: AsyncSession = Depends(get_db)):
    """获取 Prompt 列表"""
    query = select(Prompt).order_by(Prompt.updated_at.desc())
    if tag:
        query = query.where(Prompt.tags.any(tag))
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取 Prompt 详情"""
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(404, "Prompt 不存在")
    return prompt


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: UUID, data: PromptUpdate, db: AsyncSession = Depends(get_db)
):
    """更新 Prompt（自动创建新版本）"""
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(404, "Prompt 不存在")

    update_data = data.model_dump(exclude_unset=True)
    needs_version = "system_prompt" in update_data or "user_prompt" in update_data

    for key, value in update_data.items():
        setattr(prompt, key, value)

    if needs_version:
        prompt.current_version += 1
        version = PromptVersion(
            prompt_id=prompt.id,
            version=prompt.current_version,
            system_prompt=prompt.system_prompt,
            user_prompt=prompt.user_prompt,
            change_note=update_data.get("change_note", "更新"),
        )
        db.add(version)

    await db.commit()
    await db.refresh(prompt)
    return prompt


@router.delete("/{prompt_id}", status_code=204)
async def delete_prompt(prompt_id: UUID, db: AsyncSession = Depends(get_db)):
    """删除 Prompt"""
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(404, "Prompt 不存在")
    await db.delete(prompt)
    await db.commit()


# ==================== Version History ====================


@router.get("/{prompt_id}/versions", response_model=list[PromptVersionResponse])
async def list_versions(prompt_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取 Prompt 版本历史"""
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(404, "Prompt 不存在")

    result = await db.execute(
        select(PromptVersion)
        .where(PromptVersion.prompt_id == prompt_id)
        .order_by(PromptVersion.version.desc())
    )
    return result.scalars().all()


@router.post("/{prompt_id}/versions/{version}/rollback", response_model=PromptResponse)
async def rollback_version(
    prompt_id: UUID, version: int, db: AsyncSession = Depends(get_db)
):
    """回滚到指定版本"""
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(404, "Prompt 不存在")

    result = await db.execute(
        select(PromptVersion).where(
            PromptVersion.prompt_id == prompt_id,
            PromptVersion.version == version,
        )
    )
    target_version = result.scalar_one_or_none()
    if not target_version:
        raise HTTPException(404, f"版本 v{version} 不存在")

    # 更新当前 prompt 内容
    prompt.system_prompt = target_version.system_prompt
    prompt.user_prompt = target_version.user_prompt
    prompt.current_version += 1

    # 创建新的版本记录（回滚也是一个新版本）
    new_version = PromptVersion(
        prompt_id=prompt.id,
        version=prompt.current_version,
        system_prompt=target_version.system_prompt,
        user_prompt=target_version.user_prompt,
        change_note=f"回滚至 v{version}",
    )
    db.add(new_version)
    await db.commit()
    await db.refresh(prompt)
    return prompt


# ==================== Prompt Test ====================


def render_template(template: str, variables: dict) -> str:
    """使用简单的 {{var}} 模板渲染"""
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


def extract_variables(template: str) -> list[str]:
    """从模板中提取 {{var}} 格式变量"""
    return list(set(re.findall(r"\{\{(\w+)\}\}", template)))


@router.post("/{prompt_id}/test", response_model=PromptTestResponse)
async def test_prompt(
    prompt_id: UUID,
    data: PromptTestRequest,
    db: AsyncSession = Depends(get_db),
):
    """测试 Prompt（多模型对比）"""
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(404, "Prompt 不存在")

    # 渲染模板
    rendered_system = render_template(prompt.system_prompt, data.variables)
    rendered_user = render_template(prompt.user_prompt, data.variables)

    # 并行调用多个模型
    async def _call_model(config):
        provider = await db.get(Provider, config.provider_id)
        if not provider:
            return PromptTestResultItem(
                model=config.model,
                provider_id=config.provider_id,
                error="供应商不存在",
            )
        try:
            messages = [
                ChatMessage(role="system", content=rendered_system),
                ChatMessage(role="user", content=rendered_user),
            ]
            result = await ModelService.chat(
                provider_type=provider.provider_type,
                messages=messages,
                api_key=provider.api_key,
                base_url=provider.base_url,
                model=config.model,
            )
            return PromptTestResultItem(
                model=config.model,
                provider_id=config.provider_id,
                response=result.content,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                latency_ms=result.latency_ms,
            )
        except Exception as e:
            return PromptTestResultItem(
                model=config.model,
                provider_id=config.provider_id,
                error=str(e),
            )

    results = await asyncio.gather(*[_call_model(cfg) for cfg in data.model_configs])

    return PromptTestResponse(
        rendered_system_prompt=rendered_system,
        rendered_user_prompt=rendered_user,
        results=list(results),
    )
