"""
FastAPI LLM 服务
================

学习目标：
    1. 使用 FastAPI 构建 LLM API 服务
    2. 实现流式响应 (SSE)
    3. 添加中间件（认证、限流）

核心概念：
    - FastAPI：高性能 Python Web 框架
    - SSE：Server-Sent Events 流式响应
    - 中间件：请求/响应处理管道

环境要求：
    - pip install fastapi uvicorn pydantic openai
"""

import os
import json
import time
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：服务架构 ====================


def introduction():
    """服务架构介绍"""
    print("=" * 60)
    print("第一部分：服务架构")
    print("=" * 60)

    print("""
    📌 LLM 服务架构：
    ┌─────────────────────────────────────────────────────────┐
    │                    FastAPI 服务层                       │
    ├─────────────────────────────────────────────────────────┤
    │   ┌─────────┐    ┌─────────┐    ┌─────────┐           │
    │   │  路由   │ →  │ 中间件  │ →  │ 处理器  │           │
    │   └─────────┘    └─────────┘    └─────────┘           │
    │        ↓                                               │
    │   ┌─────────────────────────────────────────┐         │
    │   │           推理引擎 (vLLM/TGI)           │         │
    │   └─────────────────────────────────────────┘         │
    └─────────────────────────────────────────────────────────┘

    项目结构：
    llm-service/
    ├── app/
    │   ├── main.py           # 入口
    │   ├── routers/          # 路由
    │   ├── models/           # 数据模型
    │   └── services/         # 业务逻辑
    └── requirements.txt
    """)


# ==================== 第二部分：基础服务 ====================


def basic_service():
    """基础服务实现"""
    print("\n" + "=" * 60)
    print("第二部分：基础服务实现")
    print("=" * 60)

    code = """
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from openai import OpenAI

app = FastAPI(title="LLM API Service")

# 连接后端推理服务
client = OpenAI(base_url="http://localhost:8000/v1", api_key="x")

# 请求模型
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "Qwen/Qwen2-7B-Instruct"
    max_tokens: int = 2048
    temperature: float = 0.7
    stream: bool = False

# 非流式响应
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    response = client.chat.completions.create(
        model=request.model,
        messages=[m.dict() for m in request.messages],
        max_tokens=request.max_tokens,
        temperature=request.temperature
    )
    return response

# 健康检查
@app.get("/health")
async def health():
    return {"status": "ok"}

# 启动: uvicorn app.main:app --host 0.0.0.0 --port 8080
"""
    print(code)


# ==================== 第三部分：流式响应 ====================


def streaming_response():
    """流式响应实现"""
    print("\n" + "=" * 60)
    print("第三部分：流式响应 (SSE)")
    print("=" * 60)

    code = """
from fastapi.responses import StreamingResponse
import json

@app.post("/v1/chat/completions/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        stream = client.chat.completions.create(
            model=request.model,
            messages=[m.dict() for m in request.messages],
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                data = {
                    "choices": [{
                        "delta": {"content": chunk.choices[0].delta.content},
                        "index": 0
                    }]
                }
                yield f"data: {json.dumps(data)}\\n\\n"
        yield "data: [DONE]\\n\\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
"""
    print(code)


# ==================== 第四部分：中间件 ====================


def middleware():
    """中间件实现"""
    print("\n" + "=" * 60)
    print("第四部分：中间件")
    print("=" * 60)

    code = """
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

# 请求日志中间件
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        print(f"{request.method} {request.url.path} - {duration:.3f}s")
        return response

# API Key 认证中间件
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health", "/docs"]:
            return await call_next(request)

        api_key = request.headers.get("Authorization")
        if not api_key or not api_key.startswith("Bearer "):
            return JSONResponse({"error": "Unauthorized"}, 401)

        # 验证 API Key...
        return await call_next(request)

# 注册中间件
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)
"""
    print(code)


# ==================== 第五部分：速率限制 ====================


def rate_limiting():
    """速率限制"""
    print("\n" + "=" * 60)
    print("第五部分：速率限制")
    print("=" * 60)

    code = """
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/v1/chat/completions")
@limiter.limit("10/minute")  # 每分钟 10 次
async def chat_completions(request: Request, chat_request: ChatRequest):
    # ... 处理逻辑
    pass

# 使用 Redis 进行分布式限流
from slowapi import Limiter
from slowapi.util import get_remote_address
import redis

redis_client = redis.Redis(host="localhost", port=6379)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)
"""
    print(code)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现完整的 FastAPI LLM 服务

        ✅ 参考答案：
        ```python
        # app/main.py
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import StreamingResponse
        from pydantic import BaseModel
        from typing import List, Optional
        from openai import OpenAI
        import json
        
        app = FastAPI(title="LLM API Service")
        client = OpenAI(base_url="http://localhost:8000/v1", api_key="x")
        
        class Message(BaseModel):
            role: str
            content: str
        
        class ChatRequest(BaseModel):
            messages: List[Message]
            model: str = "Qwen/Qwen2-7B-Instruct"
            max_tokens: int = 2048
            temperature: float = 0.7
            stream: bool = False
        
        @app.post("/v1/chat/completions")
        async def chat_completions(request: ChatRequest):
            if request.stream:
                return await stream_chat(request)
            
            response = client.chat.completions.create(
                model=request.model,
                messages=[m.dict() for m in request.messages],
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
            return response
        
        async def stream_chat(request: ChatRequest):
            async def generate():
                stream = client.chat.completions.create(
                    model=request.model,
                    messages=[m.dict() for m in request.messages],
                    stream=True,
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\\n\\n"
                yield "data: [DONE]\\n\\n"
            
            return StreamingResponse(generate(), media_type="text/event-stream")
        
        @app.get("/health")
        async def health():
            return {"status": "ok"}
        ```
    
    练习 2：添加用户认证和速率限制

        ✅ 参考答案：
        ```python
        from fastapi import Request, HTTPException
        from fastapi.responses import JSONResponse
        from starlette.middleware.base import BaseHTTPMiddleware
        from slowapi import Limiter
        from slowapi.util import get_remote_address
        import time
        
        # API Key 认证
        VALID_API_KEYS = {"sk-abc123": "user1", "sk-xyz789": "user2"}
        
        class AuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next):
                if request.url.path in ["/health", "/docs", "/openapi.json"]:
                    return await call_next(request)
                
                auth = request.headers.get("Authorization", "")
                if not auth.startswith("Bearer "):
                    return JSONResponse({"error": "Missing API key"}, 401)
                
                api_key = auth.replace("Bearer ", "")
                if api_key not in VALID_API_KEYS:
                    return JSONResponse({"error": "Invalid API key"}, 401)
                
                request.state.user = VALID_API_KEYS[api_key]
                return await call_next(request)
        
        # 速率限制
        limiter = Limiter(key_func=get_remote_address)
        
        @app.post("/v1/chat/completions")
        @limiter.limit("20/minute")
        async def chat_completions(request: Request, chat_request: ChatRequest):
            # ... 处理逻辑
            pass
        
        app.add_middleware(AuthMiddleware)
        ```

    思考题：为什么需要在 LLM 服务前添加一层 API 网关？

        ✅ 答：
        1. 统一认证鉴权 - 集中管理 API Key
        2. 负载均衡 - 分发到多个推理实例
        3. 请求限流 - 保护后端服务
        4. 日志审计 - 记录所有请求用于分析
        5. 协议转换 - 统一 API 格式
        6. 缓存加速 - 相同请求可缓存
    """)


def main():
    introduction()
    basic_service()
    streaming_response()
    middleware()
    rate_limiting()
    exercises()
    print("\n课程完成！下一步：05-async-processing.py")


if __name__ == "__main__":
    main()
