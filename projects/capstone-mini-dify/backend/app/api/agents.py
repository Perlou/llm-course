"""
Mini-Dify - Agent 管理 API
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models.agent import Agent, Tool
from app.schemas import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    ToolCreate,
    ToolResponse,
)

router = APIRouter(tags=["Agent 管理"])


# ==================== Agent ====================


@router.post("/agents", response_model=AgentResponse, status_code=201)
async def create_agent(data: AgentCreate, db: AsyncSession = Depends(get_db)):
    """创建 Agent"""
    agent_data = data.model_dump(exclude={"tool_ids"})
    agent = Agent(**agent_data)

    if data.tool_ids:
        result = await db.execute(select(Tool).where(Tool.id.in_(data.tool_ids)))
        agent.tools = list(result.scalars().all())

    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


@router.get("/agents", response_model=list[AgentResponse])
async def list_agents(db: AsyncSession = Depends(get_db)):
    """获取 Agent 列表"""
    result = await db.execute(select(Agent).order_by(Agent.updated_at.desc()))
    return result.scalars().all()


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取 Agent 详情"""
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id).options(selectinload(Agent.tools))
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(404, "Agent 不存在")
    return agent


@router.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID, data: AgentUpdate, db: AsyncSession = Depends(get_db)
):
    """更新 Agent"""
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(404, "Agent 不存在")

    update_data = data.model_dump(exclude_unset=True, exclude={"tool_ids"})
    for key, value in update_data.items():
        setattr(agent, key, value)

    if data.tool_ids is not None:
        result = await db.execute(select(Tool).where(Tool.id.in_(data.tool_ids)))
        agent.tools = list(result.scalars().all())

    await db.commit()
    await db.refresh(agent)
    return agent


@router.delete("/agents/{agent_id}", status_code=204)
async def delete_agent(agent_id: UUID, db: AsyncSession = Depends(get_db)):
    """删除 Agent"""
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(404, "Agent 不存在")
    await db.delete(agent)
    await db.commit()


# ==================== Tool ====================


@router.get("/tools", response_model=list[ToolResponse])
async def list_tools(tool_type: str = None, db: AsyncSession = Depends(get_db)):
    """获取工具列表"""
    query = select(Tool).order_by(Tool.created_at.desc())
    if tool_type:
        query = query.where(Tool.tool_type == tool_type)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/tools", response_model=ToolResponse, status_code=201)
async def create_tool(data: ToolCreate, db: AsyncSession = Depends(get_db)):
    """创建自定义工具"""
    tool = Tool(tool_type="custom", **data.model_dump())
    db.add(tool)
    await db.commit()
    await db.refresh(tool)
    return tool


@router.put("/tools/{tool_id}", response_model=ToolResponse)
async def update_tool(
    tool_id: UUID, data: ToolCreate, db: AsyncSession = Depends(get_db)
):
    """更新自定义工具"""
    tool = await db.get(Tool, tool_id)
    if not tool:
        raise HTTPException(404, "工具不存在")
    if tool.tool_type == "builtin":
        raise HTTPException(400, "内置工具不可修改")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(tool, key, value)
    await db.commit()
    await db.refresh(tool)
    return tool


@router.delete("/tools/{tool_id}", status_code=204)
async def delete_tool(tool_id: UUID, db: AsyncSession = Depends(get_db)):
    """删除自定义工具"""
    tool = await db.get(Tool, tool_id)
    if not tool:
        raise HTTPException(404, "工具不存在")
    if tool.tool_type == "builtin":
        raise HTTPException(400, "内置工具不可删除")
    await db.delete(tool)
    await db.commit()
