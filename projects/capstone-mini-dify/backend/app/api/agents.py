"""
Mini-Dify - Agent 管理 API
"""

import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models.agent import Agent, Tool
from app.models.provider import Provider
from app.core.agent_service import AgentRunner, BUILTIN_TOOLS
from app.schemas import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentChatRequest,
    ToolCreate,
    ToolResponse,
)

router = APIRouter(tags=["Agent 管理"])


# ==================== Agent CRUD ====================


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


# ==================== Agent Chat (SSE) ====================


@router.post("/agents/{agent_id}/chat")
async def agent_chat(
    agent_id: UUID,
    data: AgentChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """Agent 对话（SSE 流式输出）"""
    # 获取 Agent 及关联数据
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id).options(selectinload(Agent.tools))
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(404, "Agent 不存在")

    # 获取 Provider 配置
    provider_config = {"provider_type": "openai", "api_key": "", "base_url": None}
    if agent.provider_id:
        provider = await db.get(Provider, agent.provider_id)
        if provider:
            provider_config = {
                "provider_type": provider.provider_type,
                "api_key": provider.api_key,
                "base_url": provider.base_url,
            }

    agent_config = {
        "system_prompt": agent.system_prompt,
        "model_name": agent.model_name,
        "temperature": agent.temperature,
        "max_tokens": agent.max_tokens,
        "strategy": agent.strategy,
    }

    tool_names = [t.name for t in agent.tools] if agent.tools else []
    dataset_ids = [str(did) for did in agent.dataset_ids] if agent.dataset_ids else []
    messages = [{"role": m.role, "content": m.content} for m in data.messages]

    async def event_stream():
        async for event in AgentRunner.chat_stream(
            provider_config=provider_config,
            agent_config=agent_config,
            messages=messages,
            tool_names=tool_names,
            dataset_ids=dataset_ids,
        ):
            event_type = event.get("event", "message")
            event_data = event.get("data", "")
            yield f"event: {event_type}\ndata: {json.dumps(event_data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


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


@router.post("/tools/init-builtins")
async def init_builtin_tools(db: AsyncSession = Depends(get_db)):
    """初始化内置工具"""
    created = []
    for bt in BUILTIN_TOOLS:
        result = await db.execute(select(Tool).where(Tool.name == bt["name"]))
        existing = result.scalar_one_or_none()
        if not existing:
            tool = Tool(
                name=bt["name"],
                description=bt["description"],
                tool_type="builtin",
                parameters=bt["parameters"],
                is_active=True,
            )
            db.add(tool)
            created.append(bt["name"])
    await db.commit()
    return {"created": created, "message": f"初始化了 {len(created)} 个内置工具"}


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
