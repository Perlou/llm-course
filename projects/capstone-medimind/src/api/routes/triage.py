"""
MediMind - 智能导诊路由

基于 LangGraph Agent 的多轮对话导诊接口。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

from src.utils import generate_id

router = APIRouter(prefix="/triage")


class StartTriageResponse(BaseModel):
    """开始导诊响应"""
    session_id: str
    message: str
    questions: Optional[List[str]] = None


class TriageChatRequest(BaseModel):
    """导诊对话请求"""
    session_id: str = Field(..., description="会话 ID")
    message: str = Field(..., min_length=1, max_length=1000, description="用户消息")


class TriageResult(BaseModel):
    """导诊结果"""
    symptoms: List[str]
    duration: Optional[str] = None
    severity: str  # mild, moderate, severe
    recommended_department: str
    urgency: str  # routine, soon, urgent, emergency
    advice: str


class TriageChatResponse(BaseModel):
    """导诊对话响应"""
    message: str
    is_complete: bool = False
    result: Optional[TriageResult] = None


@router.post("/start")
async def start_triage():
    """
    开始导诊会话
    
    初始化导诊 Agent，返回欢迎语和初始问题。
    """
    session_id = generate_id("triage_")
    
    # TODO: 初始化 LangGraph Agent 状态
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "session_id": session_id,
            "message": "您好！我是智能导诊助手。请描述一下您的主要不适症状，我会帮您分析并推荐合适的科室。",
            "questions": [
                "您目前最主要的不适是什么？",
                "症状持续多长时间了？",
                "疼痛程度如何？(轻微/中度/剧烈)",
            ],
        },
    }


@router.post("/chat")
async def triage_chat(request: TriageChatRequest):
    """
    导诊对话接口
    
    进行多轮对话，收集症状信息，最终给出科室推荐。
    """
    # TODO: 实现 LangGraph Agent 对话逻辑
    # 1. 获取会话状态
    # 2. 分析用户输入
    # 3. 更新状态
    # 4. 决定下一步（继续提问 or 给出结果）
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "message": "智能导诊功能开发中，请稍后再试。",
            "is_complete": False,
            "result": None,
        },
        "disclaimer": "⚕️ 智能导诊仅供参考，不代表医学诊断。如有严重症状请立即就医。",
    }


@router.get("/session/{session_id}")
async def get_triage_session(session_id: str):
    """
    获取导诊会话状态
    
    返回当前会话的对话历史和状态。
    """
    # TODO: 从存储获取会话状态
    return {
        "code": 0,
        "message": "success",
        "data": {
            "session_id": session_id,
            "messages": [],
            "is_complete": False,
        },
    }


@router.get("/departments")
async def list_departments():
    """
    获取科室列表
    
    返回医院常见科室及其说明。
    """
    departments = [
        {"name": "内科", "description": "呼吸、消化、心血管等内脏疾病"},
        {"name": "外科", "description": "需要手术治疗的疾病"},
        {"name": "骨科", "description": "骨骼、关节、肌肉疾病"},
        {"name": "皮肤科", "description": "皮肤相关疾病"},
        {"name": "眼科", "description": "眼部疾病"},
        {"name": "耳鼻喉科", "description": "耳、鼻、咽喉疾病"},
        {"name": "妇科", "description": "女性生殖系统疾病"},
        {"name": "儿科", "description": "儿童疾病"},
        {"name": "急诊科", "description": "紧急情况"},
    ]
    
    return {
        "code": 0,
        "message": "success",
        "data": departments,
    }
