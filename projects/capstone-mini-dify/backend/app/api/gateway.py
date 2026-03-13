"""
Mini-Dify - API 网关
统一对外接口，通过 API Key 认证，路由到 Chat/Completion/Workflow
"""

import json
import hashlib
import uuid
import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.app import App, AppApiKey
from app.models.log import ConversationLog
from app.models.provider import Provider
from app.core.model_service import ModelService, ChatMessage
from app.core.workflow_engine import WorkflowEngine

router = APIRouter(prefix="/gateway", tags=["API 网关"])


# ==================== Auth Dependency ====================


async def authenticate_api_key(request: Request, db: AsyncSession = Depends(get_db)):
    """
    从 Authorization: Bearer md-xxx 提取 API Key，
    SHA256 匹配 app_api_keys 表，返回关联的 App。
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(401, "缺少 Authorization Bearer token")

    raw_key = auth_header[7:]
    if not raw_key.startswith("md-"):
        raise HTTPException(401, "无效的 API Key 格式")

    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    result = await db.execute(
        select(AppApiKey).where(
            AppApiKey.key_hash == key_hash,
            AppApiKey.is_active == True,
        )
    )
    api_key = result.scalar_one_or_none()
    if not api_key:
        raise HTTPException(401, "无效的 API Key")

    # 加载关联的 App
    app = await db.get(App, api_key.app_id)
    if not app:
        raise HTTPException(404, "关联的应用不存在")
    if not app.is_published:
        raise HTTPException(403, "应用未发布，无法调用")

    # 更新 last_used
    await db.execute(
        update(AppApiKey)
        .where(AppApiKey.id == api_key.id)
        .values(last_used=datetime.now(timezone.utc))
    )
    await db.commit()

    return app


# ==================== Gateway Routes ====================


@router.post("/chat")
async def gateway_chat(
    request: Request,
    app: App = Depends(authenticate_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Chat 接口 — Chatbot 类型应用
    请求体: {"message": "你好", "conversation_id": "optional-uuid"}
    """
    if app.app_type != "chatbot":
        raise HTTPException(400, f"此应用类型为 {app.app_type}，请使用对应的接口")

    body = await request.json()
    message = body.get("message", "")
    if not message:
        raise HTTPException(400, "message 不能为空")

    config = app.config or {}
    provider_id = config.get("provider_id")
    model_name = config.get("model", "gpt-4o-mini")
    system_prompt = config.get("system_prompt", "")
    temperature = config.get("temperature", 0.7)

    # 加载 Provider
    provider_type = "openai"
    api_key = ""
    base_url = None
    if provider_id:
        provider = await db.get(Provider, provider_id)
        if provider:
            provider_type = provider.provider_type
            api_key = provider.api_key
            base_url = provider.base_url

    # 检查是否关联 Agent
    agent_id = config.get("agent_id")
    if agent_id:
        # 通过 AgentRunner 执行
        from app.core.agent_service import AgentRunner

        async def agent_stream():
            async for chunk in AgentRunner.run_stream(
                agent_id=agent_id,
                message=message,
                db=db,
            ):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

        return StreamingResponse(
            agent_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # 直接 LLM 调用
    messages = []
    if system_prompt:
        messages.append(ChatMessage(role="system", content=system_prompt))
    messages.append(ChatMessage(role="user", content=message))

    async def llm_stream():
        async for chunk in ModelService.chat_stream(
            provider_type=provider_type,
            messages=messages,
            api_key=api_key,
            base_url=base_url,
            model=model_name,
            temperature=temperature,
        ):
            yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        llm_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/completion")
async def gateway_completion(
    request: Request,
    app: App = Depends(authenticate_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Completion 接口 — Completion 类型应用
    请求体: {"inputs": {"text": "你好"}}
    """
    if app.app_type != "completion":
        raise HTTPException(400, f"此应用类型为 {app.app_type}，请使用对应的接口")

    body = await request.json()
    inputs = body.get("inputs", {})

    config = app.config or {}
    provider_id = config.get("provider_id")
    model_name = config.get("model", "gpt-4o-mini")
    prompt_template = config.get("prompt", "")
    system_prompt = config.get("system_prompt", "")
    temperature = config.get("temperature", 0.7)

    # 渲染 prompt
    import re
    def render(template, variables):
        def replacer(match):
            var_name = match.group(1).strip()
            return str(variables.get(var_name, match.group(0)))
        return re.sub(r"\{\{(\w+)\}\}", replacer, template)

    prompt = render(prompt_template, inputs) if prompt_template else str(inputs)

    # 加载 Provider
    provider_type = "openai"
    api_key = ""
    base_url = None
    if provider_id:
        provider = await db.get(Provider, provider_id)
        if provider:
            provider_type = provider.provider_type
            api_key = provider.api_key
            base_url = provider.base_url

    messages = []
    if system_prompt:
        messages.append(ChatMessage(role="system", content=render(system_prompt, inputs)))
    messages.append(ChatMessage(role="user", content=prompt))

    start_time = time.time()
    result = await ModelService.chat(
        provider_type=provider_type,
        messages=messages,
        api_key=api_key,
        base_url=base_url,
        model=model_name,
        temperature=temperature,
    )
    latency = int((time.time() - start_time) * 1000)

    # 记录对话日志
    conv_id = uuid.uuid4()
    try:
        user_log = ConversationLog(
            app_id=app.id,
            conversation_id=conv_id,
            role="user",
            content=prompt,
            provider_name=provider_type,
            model_name=model_name,
            input_tokens=0, output_tokens=0,
        )
        assistant_log = ConversationLog(
            app_id=app.id,
            conversation_id=conv_id,
            role="assistant",
            content=result.content or "",
            provider_name=provider_type,
            model_name=model_name,
            input_tokens=getattr(result, 'input_tokens', 0) or 0,
            output_tokens=getattr(result, 'output_tokens', 0) or 0,
            latency_ms=latency,
        )
        db.add(user_log)
        db.add(assistant_log)
        await db.commit()
    except Exception:
        pass

    return {"output": result.content}


@router.post("/workflow")
async def gateway_workflow(
    request: Request,
    app: App = Depends(authenticate_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Workflow 接口 — Workflow 类型应用 (SSE)
    请求体: {"inputs": {"user_message": "你好"}}
    """
    if app.app_type != "workflow":
        raise HTTPException(400, f"此应用类型为 {app.app_type}，请使用对应的接口")

    body = await request.json()
    inputs = body.get("inputs", {})

    config = app.config or {}
    workflow_id = config.get("workflow_id")
    if not workflow_id:
        raise HTTPException(400, "应用未关联工作流")

    from app.models.workflow import Workflow

    workflow = await db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(404, "关联的工作流不存在")

    graph_data = workflow.graph_data
    if not graph_data or not graph_data.get("nodes"):
        raise HTTPException(400, "工作流图数据为空")

    # 收集 Provider 配置
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
            inputs=inputs,
            provider_configs=provider_configs,
        ):
            event_type = event.get("type", event.get("status", "message"))
            yield f"event: {event_type}\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
