"""
MediMind - 健康问答路由

基于 RAG 的健康知识问答接口。
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List

router = APIRouter(prefix="/health")


class ChatRequest(BaseModel):
    """问答请求"""
    query: str = Field(..., min_length=1, max_length=1000, description="用户问题")
    conversation_id: Optional[str] = Field(None, description="对话 ID")


class Source(BaseModel):
    """来源信息"""
    title: str
    page: Optional[str] = None
    score: Optional[float] = None


class ChatResponse(BaseModel):
    """问答响应"""
    answer: str
    sources: List[Source] = []
    emergency: bool = False
    conversation_id: str
    disclaimer: str = "⚕️ 以上信息仅供参考，如有健康问题请咨询专业医生。"


@router.post("/chat", response_model=dict)
async def chat(request: ChatRequest):
    """
    健康问答接口
    
    基于医学知识库的 RAG 问答，返回答案和参考来源。
    """
    # TODO: 实现 RAG 问答逻辑
    # 1. 输入安全检查
    # 2. 向量检索
    # 3. LLM 生成
    # 4. 输出合规检查
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "answer": "健康问答功能开发中，请稍后再试。",
            "sources": [],
            "emergency": False,
            "conversation_id": request.conversation_id or "new_conversation",
            "disclaimer": "⚕️ 以上信息仅供参考，如有健康问题请咨询专业医生。",
        },
    }


@router.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """
    流式健康问答接口
    
    返回 Server-Sent Events 流式响应。
    """
    async def generate():
        # TODO: 实现流式 RAG 问答
        yield "data: 健康问答功能开发中...\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )
