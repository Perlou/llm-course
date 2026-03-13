"""
Mini-Dify - 工作流 API
"""

import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.workflow import Workflow
from app.models.provider import Provider
from app.schemas import WorkflowCreate, WorkflowUpdate, WorkflowResponse, WorkflowRunRequest
from app.core.workflow_engine import WorkflowEngine

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


# ==================== Workflow Execution (SSE) ====================


@router.post("/{workflow_id}/run")
async def run_workflow(
    workflow_id: UUID,
    data: WorkflowRunRequest,
    db: AsyncSession = Depends(get_db),
):
    """执行工作流（SSE 流式输出每个节点状态）"""
    workflow = await db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(404, "工作流不存在")

    graph_data = workflow.graph_data
    if not graph_data or not graph_data.get("nodes"):
        raise HTTPException(400, "工作流图数据为空")

    # 收集所有 LLM 节点中引用的 provider_id，批量加载 Provider 配置
    provider_ids = set()
    for node in graph_data.get("nodes", []):
        if node.get("type") == "llm":
            pid = node.get("config", {}).get("provider_id")
            if pid:
                provider_ids.add(pid)

    provider_configs = {}
    if provider_ids:
        result = await db.execute(
            select(Provider).where(Provider.id.in_(provider_ids))
        )
        providers = result.scalars().all()
        for p in providers:
            provider_configs[str(p.id)] = {
                "provider_type": p.provider_type,
                "api_key": p.api_key,
                "base_url": p.base_url,
            }

    async def event_stream():
        async for event in WorkflowEngine.run(
            graph_data=graph_data,
            inputs=data.inputs,
            provider_configs=provider_configs,
        ):
            event_type = event.get("type", event.get("status", "message"))
            yield f"event: {event_type}\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
