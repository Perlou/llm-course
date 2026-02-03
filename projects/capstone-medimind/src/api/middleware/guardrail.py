"""
MediMind - 护栏中间件

FastAPI 中间件实现，自动对请求和响应进行安全检查。
"""

import json
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.guardrails import get_guardrails, RiskLevel
from src.utils import log


class GuardrailMiddleware(BaseHTTPMiddleware):
    """
    护栏中间件
    
    对 API 请求进行安全检查：
    1. 输入检查：检测危险意图和紧急情况
    2. 输出检查：确保不包含诊断性语言
    """
    
    # 需要检查的路由前缀
    PROTECTED_ROUTES = [
        "/api/v1/health",
        "/api/v1/drug",
        "/api/v1/report",
        "/api/v1/triage",
    ]
    
    # 跳过检查的路由
    SKIP_ROUTES = [
        "/api/v1/system",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        path = request.url.path
        
        # 跳过不需要检查的路由
        if self._should_skip(path):
            return await call_next(request)
        
        # 跳过非 API 路由
        if not self._should_check(path):
            return await call_next(request)
        
        start_time = time.time()
        guardrails = get_guardrails()
        
        # === 输入检查 ===
        input_text = await self._extract_input_text(request)
        
        if input_text:
            input_result = guardrails.check_input(input_text)
            
            # 危险内容，直接拒绝
            if not input_result.passed:
                log.warning(f"危险输入被拦截: {input_text[:100]}...")
                return JSONResponse(
                    status_code=400,
                    content={
                        "code": 400,
                        "message": input_result.message,
                        "data": None,
                        "risk_level": input_result.risk_level.value,
                    },
                )
            
            # 紧急情况，标记在请求状态中
            if input_result.risk_level == RiskLevel.EMERGENCY:
                request.state.is_emergency = True
                request.state.emergency_message = input_result.message
                log.info(f"检测到紧急情况: {input_text[:100]}...")
            else:
                request.state.is_emergency = False
        
        # === 调用原始处理 ===
        response = await call_next(request)
        
        # 记录处理时间
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(round(process_time, 3))
        
        return response
    
    def _should_skip(self, path: str) -> bool:
        """检查是否跳过"""
        return any(path.startswith(route) for route in self.SKIP_ROUTES)
    
    def _should_check(self, path: str) -> bool:
        """检查是否需要护栏检查"""
        return any(path.startswith(route) for route in self.PROTECTED_ROUTES)
    
    async def _extract_input_text(self, request: Request) -> str:
        """从请求中提取输入文本"""
        if request.method not in ["POST", "PUT", "PATCH"]:
            # GET 请求从 query 参数提取
            query = request.query_params.get("q") or request.query_params.get("query")
            return query or ""
        
        try:
            # POST 请求从 body 提取
            body = await request.body()
            if body:
                data = json.loads(body)
                # 尝试多个常见字段名
                for field in ["query", "question", "message", "content", "text", "input"]:
                    if field in data:
                        return str(data[field])
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        
        return ""


def get_emergency_status(request: Request) -> bool:
    """
    从请求状态获取紧急情况标记
    
    在路由处理函数中使用：
        is_emergency = get_emergency_status(request)
    """
    return getattr(request.state, "is_emergency", False)
