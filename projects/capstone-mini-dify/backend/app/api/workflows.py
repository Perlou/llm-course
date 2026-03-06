"""
Mini-Dify - 工作流 API
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.workflow import Workflow
from app.schemas import WorkflowCreate, WorkflowUpdate, WorkflowResponse

router = APIRouter(prefix="/workflows", tags=["工作流"])


@router.post("", response_model=WorkflowResponse, status_code=201)
async def create_workflow(data: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    """创建工作流"""
    workflow = Workflow(**data.model_dump())
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return workflow


@router.get("", response_model=list[WorkflowResponse])
async def list_workflows(db: AsyncSession = Depends(get_db)):
    """获取工作流列表"""
    result = await db.execute(select(Workflow).order_by(Workflow.updated_at.desc()))
    return result.scalars().all()


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取工作流详情"""
    workflow = await db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(404, "工作流不存在")
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID, data: WorkflowUpdate, db: AsyncSession = Depends(get_db)
):
    """更新工作流"""
    workflow = await db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(404, "工作流不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(workflow, key, value)
    await db.commit()
    await db.refresh(workflow)
    return workflow


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: UUID, db: AsyncSession = Depends(get_db)):
    """删除工作流"""
    workflow = await db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(404, "工作流不存在")
    if workflow.status == "published":
        raise HTTPException(400, "已发布的工作流不可删除，请先取消发布")
    await db.delete(workflow)
    await db.commit()


@router.post("/{workflow_id}/publish")
async def publish_workflow(workflow_id: UUID, db: AsyncSession = Depends(get_db)):
    """发布工作流"""
    workflow = await db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(404, "工作流不存在")
    workflow.status = "published"
    await db.commit()
    return {"status": "published"}


@router.post("/{workflow_id}/unpublish")
async def unpublish_workflow(workflow_id: UUID, db: AsyncSession = Depends(get_db)):
    """取消发布工作流"""
    workflow = await db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(404, "工作流不存在")
    workflow.status = "draft"
    await db.commit()
    return {"status": "draft"}
