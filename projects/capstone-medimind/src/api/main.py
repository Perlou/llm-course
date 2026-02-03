"""
MediMind - FastAPI 应用入口

智能健康助手平台 API 服务。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.utils import get_settings, setup_logger, log
from src.api.routes import (
    system_router,
    health_qa_router,
    drug_router,
    report_router,
    triage_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    settings = get_settings()
    
    # 启动时
    setup_logger(level=settings.log_level)
    log.info(f"🚀 {settings.app_name} v{settings.app_version} 启动中...")
    log.info(f"📍 环境: {settings.app_env}")
    log.info(f"🔧 调试模式: {settings.debug}")
    
    yield
    
    # 关闭时
    log.info(f"👋 {settings.app_name} 关闭")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        description="智能健康助手平台 - 提供健康问答、药品查询、报告解读、智能导诊服务",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应限制域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 护栏中间件 - 医疗安全检查
    from src.api.middleware import GuardrailMiddleware
    app.add_middleware(GuardrailMiddleware)
    
    # 注册路由
    app.include_router(system_router, prefix="/api/v1", tags=["系统"])
    app.include_router(health_qa_router, prefix="/api/v1", tags=["健康问答"])
    app.include_router(drug_router, prefix="/api/v1", tags=["药品查询"])
    app.include_router(report_router, prefix="/api/v1", tags=["报告解读"])
    app.include_router(triage_router, prefix="/api/v1", tags=["智能导诊"])
    
    # 全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        log.error(f"未处理异常: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "服务器内部错误",
                "data": None,
            },
        )
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
