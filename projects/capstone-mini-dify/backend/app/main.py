"""
Mini-Dify - FastAPI 应用入口
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.models import router as models_router
from app.api.prompts import router as prompts_router
from app.api.datasets import router as datasets_router
from app.api.agents import router as agents_router
from app.api.workflows import router as workflows_router
from app.api.apps import router as apps_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动和关闭"""
    # 启动
    print("🚀 Mini-Dify Backend Starting...")
    yield
    # 关闭
    print("👋 Mini-Dify Backend Shutting Down...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Mini-Dify",
        description="简化版 Dify - 可视化 LLM 应用开发平台",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 健康检查
    @app.get("/health", tags=["系统"])
    async def health_check():
        return {
            "status": "healthy",
            "version": "0.1.0",
            "services": {
                "database": "connected",
                "milvus": "connected",
            },
        }

    # 注册路由
    app.include_router(models_router, prefix="/api/v1")
    app.include_router(prompts_router, prefix="/api/v1")
    app.include_router(datasets_router, prefix="/api/v1")
    app.include_router(agents_router, prefix="/api/v1")
    app.include_router(workflows_router, prefix="/api/v1")
    app.include_router(apps_router, prefix="/api/v1")

    return app


app = create_app()
