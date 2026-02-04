"""
MediMind - 健康问答路由

基于 RAG 的健康知识问答接口。
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List

from src.utils import log, generate_id

router = APIRouter(prefix="/health")


class ChatRequest(BaseModel):
    """问答请求"""
    query: str = Field(..., min_length=1, max_length=1000, description="用户问题")
    conversation_id: Optional[str] = Field(None, description="对话 ID")


class SourceInfo(BaseModel):
    """来源信息"""
    title: str
    source: Optional[str] = None
    score: Optional[float] = None


class ChatResponseData(BaseModel):
    """问答响应数据"""
    answer: str
    sources: List[SourceInfo] = []
    is_emergency: bool = False
    conversation_id: str
    disclaimer: str = "⚕️ 以上信息仅供参考，如有健康问题请咨询专业医生。"


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    健康问答接口
    
    基于医学知识库的 RAG 问答，返回答案和参考来源。
    """
    try:
        from src.core import get_rag_service
        
        rag_service = get_rag_service()
        response = rag_service.query(
            question=request.query,
            conversation_id=request.conversation_id,
        )
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "answer": response.answer,
                "sources": [
                    {
                        "title": s.title,
                        "source": s.source,
                        "score": round(s.score, 4),
                    }
                    for s in response.sources
                ],
                "is_emergency": response.is_emergency,
                "conversation_id": response.conversation_id,
                "disclaimer": response.disclaimer,
            },
        }
    except ImportError as e:
        log.warning(f"RAG 服务依赖未安装: {e}")
        return {
            "code": 0,
            "message": "success",
            "data": {
                "answer": "健康问答服务需要安装依赖项。请运行: pip install sentence-transformers chromadb google-generativeai",
                "sources": [],
                "is_emergency": False,
                "conversation_id": request.conversation_id or generate_id("conv_"),
                "disclaimer": "⚕️ 以上信息仅供参考，如有健康问题请咨询专业医生。",
            },
        }
    except Exception as e:
        log.error(f"健康问答失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """
    流式健康问答接口
    
    返回 Server-Sent Events 流式响应。
    """
    async def generate():
        try:
            from src.core import get_rag_service
            
            rag_service = get_rag_service()
            async for chunk in rag_service.query_stream(
                question=request.query,
                conversation_id=request.conversation_id,
            ):
                yield f"data: {chunk}\n\n"
            
            yield "data: [DONE]\n\n"
        except ImportError as e:
            yield f"data: 服务依赖未安装: {e}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            log.error(f"流式问答失败: {e}")
            yield f"data: 发生错误: {str(e)}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


@router.get("/history/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """
    获取对话历史
    
    从数据库获取指定对话的所有消息记录。
    """
    try:
        from src.core.conversation_service import get_conversation_service
        
        service = get_conversation_service()
        messages = service.get_messages(conversation_id)
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "conversation_id": conversation_id,
                "messages": messages,
                "total": len(messages),
            },
        }
    except Exception as e:
        log.error(f"获取对话历史失败: {e}")
        return {
            "code": 0,
            "message": "success",
            "data": {
                "conversation_id": conversation_id,
                "messages": [],
                "total": 0,
            },
        }


@router.get("/conversations")
async def list_conversations(limit: int = 20):
    """
    获取最近对话列表
    
    返回用户最近的健康问答对话列表。
    """
    try:
        from src.core.conversation_service import get_conversation_service
        
        service = get_conversation_service()
        conversations = service.get_recent_conversations(
            limit=limit,
            conversation_type="health_qa",
        )
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "conversations": conversations,
                "total": len(conversations),
            },
        }
    except Exception as e:
        log.error(f"获取对话列表失败: {e}")
        return {
            "code": 0,
            "message": "success",
            "data": {
                "conversations": [],
                "total": 0,
            },
        }


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    删除对话
    
    删除指定对话及其所有消息记录。
    """
    try:
        from src.core.conversation_service import get_conversation_service
        
        service = get_conversation_service()
        success = service.delete_conversation(conversation_id)
        
        if success:
            return {
                "code": 0,
                "message": "success",
                "data": {"deleted": conversation_id},
            }
        else:
            return {
                "code": 404,
                "message": "对话不存在",
                "data": None,
            }
    except Exception as e:
        log.error(f"删除对话失败: {e}")
        return {
            "code": 500,
            "message": str(e),
            "data": None,
        }
