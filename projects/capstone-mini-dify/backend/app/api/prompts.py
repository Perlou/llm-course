"""
Mini-Dify - Prompt 管理 API
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.prompt import Prompt, PromptVersion
from app.schemas import PromptCreate, PromptUpdate, PromptResponse

router = APIRouter(prefix="/prompts", tags=["Prompt 管理"])


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
            change_note="自动保存",
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


@router.post("/{prompt_id}/test")
async def test_prompt(
    prompt_id: UUID, variables: dict = {}, db: AsyncSession = Depends(get_db)
):
    """测试 Prompt 模板渲染"""
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(404, "Prompt 不存在")
    # TODO: 实现 Jinja2 变量渲染 + 模型调用
    return {"rendered_prompt": prompt.user_prompt, "variables": variables}
