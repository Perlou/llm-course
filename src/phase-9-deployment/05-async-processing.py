"""
异步处理
========

学习目标：
    1. 理解异步处理的必要性
    2. 使用 Celery 实现任务队列
    3. 实现长任务的异步处理

核心概念：
    - 异步：非阻塞的任务处理方式
    - 任务队列：解耦请求与处理
    - Worker：后台任务执行器

环境要求：
    - pip install celery redis
"""

import os
import time
import asyncio


# ==================== 第一部分：异步处理概念 ====================


def introduction():
    """异步处理概念"""
    print("=" * 60)
    print("第一部分：异步处理概念")
    print("=" * 60)

    print("""
    📌 为什么需要异步处理？

    同步处理：
    请求1 ████████████████░░░░░░░░  阻塞等待
    请求2 ░░░░░░░░░░░░░░░░████████  排队

    异步处理：
    请求1 ████───────████           IO时释放
    请求2 ░░░░████───────████       并发处理
            ↑ 等待推理时处理其他请求

    📌 异步处理架构：
    ┌─────────────────────────────────────────────────────────┐
    │  请求 → [消息队列] → [Worker池] → [结果存储]           │
    │           Redis       Celery      Redis/DB             │
    │                                                         │
    │  轮询/回调 ←─────────────────────────┘                 │
    └─────────────────────────────────────────────────────────┘
    """)


# ==================== 第二部分：Celery 任务队列 ====================


def celery_basics():
    """Celery 基础"""
    print("\n" + "=" * 60)
    print("第二部分：Celery 任务队列")
    print("=" * 60)

    code = """
# celery_app.py
from celery import Celery

app = Celery(
    "llm_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    task_time_limit=300,  # 5分钟超时
)

# tasks.py
from celery_app import app
from llm_service import generate

@app.task(bind=True, max_retries=3)
def async_generate(self, request_data: dict):
    try:
        result = generate(request_data)
        return {"status": "success", "result": result}
    except Exception as e:
        self.retry(countdown=5)  # 5秒后重试

# 启动 Worker
# celery -A celery_app worker --loglevel=info
"""
    print(code)


# ==================== 第三部分：FastAPI 集成 ====================


def fastapi_integration():
    """FastAPI 集成"""
    print("\n" + "=" * 60)
    print("第三部分：FastAPI 集成")
    print("=" * 60)

    code = """
from fastapi import FastAPI
from celery.result import AsyncResult
from tasks import async_generate

app = FastAPI()

# 提交异步任务
@app.post("/v1/async/chat")
async def submit_task(request: ChatRequest):
    task = async_generate.delay(request.dict())
    return {"task_id": task.id, "status": "pending"}

# 查询任务状态
@app.get("/v1/async/task/{task_id}")
async def get_task_status(task_id: str):
    result = AsyncResult(task_id)

    if result.ready():
        return {
            "task_id": task_id,
            "status": "completed",
            "result": result.get()
        }
    elif result.failed():
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(result.result)
        }
    else:
        return {
            "task_id": task_id,
            "status": "pending"
        }
"""
    print(code)


# ==================== 第四部分：原生 AsyncIO ====================


def asyncio_example():
    """AsyncIO 示例"""
    print("\n" + "=" * 60)
    print("第四部分：原生 AsyncIO")
    print("=" * 60)

    code = '''
import asyncio
from typing import Dict, Any

class AsyncLLMService:
    def __init__(self):
        self.pending_tasks: Dict[str, asyncio.Task] = {}

    async def generate_async(self, task_id: str, request: dict):
        """异步生成任务"""
        # 模拟 LLM 推理
        await asyncio.sleep(2)
        result = f"Generated response for {request}"
        return result

    async def submit(self, request: dict) -> str:
        """提交任务"""
        task_id = str(uuid.uuid4())
        task = asyncio.create_task(
            self.generate_async(task_id, request)
        )
        self.pending_tasks[task_id] = task
        return task_id

    async def get_result(self, task_id: str):
        """获取结果"""
        if task_id not in self.pending_tasks:
            return None
        task = self.pending_tasks[task_id]
        if task.done():
            return task.result()
        return "pending"
'''
    print(code)


# ==================== 第五部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：使用 Celery 实现异步 LLM 推理服务
    练习 2：实现任务状态轮询和 WebSocket 通知

    思考题：什么场景需要异步处理？
    答案：1. 长时间推理任务 2. 批量处理 3. 需要解耦前后端
    """)


def main():
    introduction()
    celery_basics()
    fastapi_integration()
    asyncio_example()
    exercises()
    print("\n课程完成！下一步：06-batch-inference.py")


if __name__ == "__main__":
    main()
