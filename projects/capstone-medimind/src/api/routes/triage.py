"""
MediMind - 智能导诊路由

多轮对话导诊接口，实现症状分析和科室推荐。
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from src.utils import log
from src.api.middleware.guardrail import get_emergency_status

router = APIRouter(prefix="/triage")


class StartSessionResponse(BaseModel):
    """开始会话响应"""
    session_id: str
    message: str
    state: str


class ChatRequest(BaseModel):
    """对话请求"""
    message: str = Field(..., min_length=1, max_length=500, description="用户消息")


class ChatResponse(BaseModel):
    """对话响应"""
    session_id: str
    state: str
    urgency: str
    message: str
    is_complete: bool
    recommended_departments: Optional[List[str]] = None
    symptoms: Optional[List[str]] = None


class SessionStatusResponse(BaseModel):
    """会话状态响应"""
    session_id: str
    state: str
    urgency: str
    symptoms: List[str]
    recommended_departments: List[str]
    questions_asked: int
    is_complete: bool


@router.post("/start", response_model=dict)
async def start_triage_session():
    """
    开始导诊会话
    
    创建新的导诊会话，返回会话 ID 和初始问候语。
    """
    from src.core.triage_agent import get_triage_agent
    
    agent = get_triage_agent()
    context = agent.start_session()
    
    welcome_message = """👋 您好！我是 MediMind 智能导诊助手。

我会根据您描述的症状，帮您分析可能的原因并推荐合适的科室。

**请告诉我您现在的主要不适是什么？**

例如：头痛、咳嗽、胃痛、发烧等。"""
    
    context.messages.append({
        "role": "assistant",
        "content": welcome_message,
    })
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "session_id": context.session_id,
            "state": context.state.value,
            "message": welcome_message,
        },
    }


@router.post("/{session_id}/chat", response_model=dict)
async def triage_chat(session_id: str, request: ChatRequest):
    """
    导诊对话
    
    发送用户消息并获取导诊回复。
    """
    from src.core.triage_agent import get_triage_agent
    
    agent = get_triage_agent()
    
    # 检查会话是否存在
    context = agent.get_session(session_id)
    if not context:
        raise HTTPException(
            status_code=404,
            detail="会话不存在或已过期，请开始新的导诊会话",
        )
    
    # 处理消息
    result = agent.process_message(session_id, request.message)
    
    if result.get("error"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "处理失败"),
        )
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "session_id": result.get("session_id"),
            "state": result.get("state"),
            "urgency": result.get("urgency", "normal"),
            "message": result.get("message"),
            "is_complete": result.get("is_complete", False),
            "recommended_departments": result.get("recommended_departments", []),
            "symptoms": result.get("symptoms", []),
        },
    }


@router.get("/{session_id}/status", response_model=dict)
async def get_session_status(session_id: str):
    """
    获取会话状态
    
    查询当前导诊会话的状态和已收集的信息。
    """
    from src.core.triage_agent import get_triage_agent
    
    agent = get_triage_agent()
    context = agent.get_session(session_id)
    
    if not context:
        raise HTTPException(
            status_code=404,
            detail="会话不存在",
        )
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "session_id": context.session_id,
            "state": context.state.value,
            "urgency": context.urgency.value,
            "symptoms": [s.name for s in context.symptoms],
            "recommended_departments": context.recommended_departments,
            "questions_asked": context.questions_asked,
            "is_complete": context.state.value == "complete",
        },
    }


@router.get("/{session_id}/history", response_model=dict)
async def get_session_history(session_id: str):
    """
    获取对话历史
    
    返回会话中的所有消息记录。
    """
    from src.core.triage_agent import get_triage_agent
    
    agent = get_triage_agent()
    context = agent.get_session(session_id)
    
    if not context:
        raise HTTPException(
            status_code=404,
            detail="会话不存在",
        )
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "session_id": context.session_id,
            "messages": context.messages,
            "total": len(context.messages),
        },
    }


@router.post("/{session_id}/end", response_model=dict)
async def end_session(session_id: str):
    """
    结束会话
    
    主动结束导诊会话。
    """
    from src.core.triage_agent import get_triage_agent, TriageState
    
    agent = get_triage_agent()
    context = agent.get_session(session_id)
    
    if not context:
        raise HTTPException(
            status_code=404,
            detail="会话不存在",
        )
    
    # 如果有收集到症状，生成最终建议
    if context.symptoms:
        context.state = TriageState.ANALYZING
        result = agent._handle_analyzing(context)
        
        return {
            "code": 0,
            "message": "success",
            "data": result,
        }
    else:
        context.state = TriageState.COMPLETE
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "session_id": session_id,
                "state": "complete",
                "message": "导诊会话已结束。如需帮助，请开始新的会话。",
                "is_complete": True,
            },
        }


@router.get("/departments", response_model=dict)
async def list_departments():
    """
    获取科室列表
    
    返回系统支持的所有科室类型。
    """
    departments = [
        {"id": "emergency", "name": "急诊科", "description": "紧急情况、意外伤害"},
        {"id": "cardiovascular", "name": "心血管内科", "description": "心脏、血管相关疾病"},
        {"id": "respiratory", "name": "呼吸内科", "description": "呼吸系统疾病"},
        {"id": "gastroenterology", "name": "消化内科", "description": "消化系统疾病"},
        {"id": "neurology", "name": "神经内科", "description": "神经系统疾病"},
        {"id": "orthopedics", "name": "骨科", "description": "骨骼、关节疾病"},
        {"id": "dermatology", "name": "皮肤科", "description": "皮肤疾病"},
        {"id": "ent", "name": "耳鼻喉科", "description": "耳、鼻、咽喉疾病"},
        {"id": "ophthalmology", "name": "眼科", "description": "眼部疾病"},
        {"id": "psychiatry", "name": "心理科", "description": "心理健康问题"},
        {"id": "endocrinology", "name": "内分泌科", "description": "内分泌代谢疾病"},
        {"id": "urology", "name": "泌尿外科", "description": "泌尿系统疾病"},
        {"id": "gynecology", "name": "妇科", "description": "女性生殖系统疾病"},
        {"id": "general", "name": "全科门诊", "description": "常见病、多发病"},
        {"id": "fever", "name": "发热门诊", "description": "发热、感染性疾病"},
    ]
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "departments": departments,
            "total": len(departments),
        },
    }
