"""
MediMind - 系统路由

健康检查、版本信息等系统接口。
"""

from fastapi import APIRouter

from src.utils import get_settings

router = APIRouter(prefix="/system")


@router.get("/health")
async def health_check():
    """
    健康检查接口
    
    用于监控服务状态。
    """
    return {
        "code": 0,
        "message": "success",
        "data": {
            "status": "healthy",
            "service": "medimind-api",
        },
    }


@router.get("/version")
async def get_version():
    """
    获取版本信息
    """
    settings = get_settings()
    return {
        "code": 0,
        "message": "success",
        "data": {
            "name": settings.app_name,
            "version": settings.app_version,
            "env": settings.app_env,
        },
    }


@router.get("/config")
async def get_config():
    """
    获取公开配置（不含敏感信息）
    """
    settings = get_settings()
    return {
        "code": 0,
        "message": "success",
        "data": {
            "llm_provider": "ollama" if settings.use_ollama else "gemini",
            "embedding_model": settings.embedding.model,
            "features": {
                "health_qa": True,
                "drug_search": True,
                "report_analysis": True,
                "triage": True,
            },
        },
    }
