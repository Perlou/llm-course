"""
AI 客服系统 - 完整实现
====================

学习目标：
    1. 实现智能客服核心功能
    2. 掌握意图识别和对话管理
    3. 实现人工接入流程

本文件包含核心实现代码参考
"""


# ==================== 项目结构 ====================

PROJECT_STRUCTURE = """
customer-service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── chat.py             # 对话接口
│   │   ├── agent.py            # 坐席接口
│   │   └── webhook.py          # 渠道接入
│   │
│   ├── services/
│   │   ├── intent_service.py   # 意图识别
│   │   ├── dialogue_service.py # 对话管理
│   │   ├── rag_service.py      # 知识问答
│   │   ├── ticket_service.py   # 工单服务
│   │   └── queue_service.py    # 排队服务
│   │
│   ├── models/
│   │   ├── dialogue.py         # 对话模型
│   │   ├── ticket.py           # 工单模型
│   │   └── agent.py            # 坐席模型
│   │
│   └── utils/
│       └── sentiment.py        # 情感分析
│
├── tests/
└── docker-compose.yml
"""

print("=" * 60)
print("第一部分：项目结构")
print("=" * 60)
print(PROJECT_STRUCTURE)


# ==================== 意图识别服务 ====================

INTENT_SERVICE = '''
# app/services/intent_service.py
import google.generativeai as genai
from typing import Dict, List, Optional
from pydantic import BaseModel

class IntentResult(BaseModel):
    intent: str
    confidence: float
    sub_intent: Optional[str] = None
    entities: Dict[str, str] = {}

class IntentService:
    """意图识别服务"""

    INTENT_PROMPT = """你是一个意图识别助手。分析用户输入，识别意图和实体。

意图分类：
- 咨询.产品: 关于产品功能、特性的问题
- 咨询.价格: 关于价格、优惠的问题
- 咨询.配送: 关于物流、配送的问题
- 售后.退货: 要求退货
- 售后.换货: 要求换货
- 售后.维修: 要求维修
- 投诉.产品: 产品质量投诉
- 投诉.服务: 服务态度投诉
- 其他.闲聊: 日常寒暄
- 其他.转人工: 要求人工服务

实体类型：
- 订单号: 订单编号
- 产品名: 产品名称
- 金额: 金额数字
- 时间: 日期时间

用户输入：{user_input}

请以JSON格式返回：
{{"intent": "意图", "confidence": 0.95, "entities": {{"实体类型": "值"}}}}"""

    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    async def recognize(self, user_input: str, context: List[Dict] = None) -> IntentResult:
        """识别意图"""
        # 构建上下文
        messages = []
        if context:
            messages.extend(context[-4:])  # 最近4轮对话
        messages.append({
            "role": "user",
            "content": self.INTENT_PROMPT.format(user_input=user_input)
        })

        response = self.model.generate_content(
            self.INTENT_PROMPT.format(user_input=user_input)
        )

        result = json.loads(response.text)
        return IntentResult(**result)
'''

print("\n" + "=" * 60)
print("第二部分：意图识别服务")
print("=" * 60)
print(INTENT_SERVICE)


# ==================== 对话管理服务 ====================

DIALOGUE_SERVICE = '''
# app/services/dialogue_service.py
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import redis.asyncio as redis
import json

class DialogueState(Enum):
    GREETING = "greeting"
    UNDERSTANDING = "understanding"
    SLOT_FILLING = "slot_filling"
    EXECUTING = "executing"
    HUMAN_QUEUE = "human_queue"
    HUMAN_CHAT = "human_chat"
    FAREWELL = "farewell"

@dataclass
class DialogueContext:
    session_id: str
    user_id: str
    channel: str  # web/app/wechat
    state: DialogueState = DialogueState.GREETING
    intent: Optional[str] = None
    slots: Dict[str, str] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)
    sentiment_score: float = 0.5
    retry_count: int = 0

class DialogueService:
    """对话管理服务"""

    # 意图需要的槽位
    REQUIRED_SLOTS = {
        "售后.退货": ["订单号", "退货原因"],
        "售后.换货": ["订单号", "换货原因"],
        "投诉.产品": ["订单号", "问题描述"],
        "投诉.服务": ["问题描述"],
    }

    def __init__(self, intent_service, rag_service, queue_service):
        self.intent_service = intent_service
        self.rag_service = rag_service
        self.queue_service = queue_service
        self.redis = redis.from_url("redis://localhost")

    async def get_context(self, session_id: str) -> DialogueContext:
        """获取对话上下文"""
        data = await self.redis.get(f"dialogue:{session_id}")
        if data:
            return DialogueContext(**json.loads(data))
        return None

    async def save_context(self, context: DialogueContext):
        """保存对话上下文"""
        await self.redis.setex(
            f"dialogue:{context.session_id}",
            3600,  # 1小时过期
            json.dumps(context.__dict__, default=str)
        )

    async def process(self, session_id: str, user_input: str) -> str:
        """处理用户消息"""
        context = await self.get_context(session_id)
        if not context:
            context = DialogueContext(session_id=session_id, user_id="")

        # 更新历史
        context.history.append({"role": "user", "content": user_input})

        # 检查转人工条件
        if self._should_transfer_human(user_input, context):
            return await self._transfer_to_human(context)

        # 状态机处理
        response = await self._dispatch(user_input, context)

        # 更新上下文
        context.history.append({"role": "assistant", "content": response})
        await self.save_context(context)

        return response

    async def _dispatch(self, user_input: str, context: DialogueContext) -> str:
        """状态分发"""
        handlers = {
            DialogueState.GREETING: self._handle_greeting,
            DialogueState.UNDERSTANDING: self._handle_understanding,
            DialogueState.SLOT_FILLING: self._handle_slot_filling,
            DialogueState.EXECUTING: self._handle_executing,
        }
        handler = handlers.get(context.state, self._handle_greeting)
        return await handler(user_input, context)

    async def _handle_greeting(self, user_input: str, context: DialogueContext) -> str:
        """处理问候"""
        context.state = DialogueState.UNDERSTANDING
        return "您好！我是智能客服小助手，请问有什么可以帮您？"

    async def _handle_understanding(self, user_input: str, context: DialogueContext) -> str:
        """理解用户意图"""
        # 意图识别
        intent_result = await self.intent_service.recognize(user_input, context.history)
        context.intent = intent_result.intent
        context.slots.update(intent_result.entities)

        # 咨询类 - 直接 RAG 回答
        if intent_result.intent.startswith("咨询"):
            answer = await self.rag_service.query(user_input)
            return answer

        # 售后/投诉类 - 检查槽位
        required = self.REQUIRED_SLOTS.get(intent_result.intent, [])
        missing = [s for s in required if s not in context.slots]

        if missing:
            context.state = DialogueState.SLOT_FILLING
            return f"好的，我来帮您处理。请问您的{missing[0]}是什么？"

        context.state = DialogueState.EXECUTING
        return await self._handle_executing(user_input, context)

    async def _handle_slot_filling(self, user_input: str, context: DialogueContext) -> str:
        """槽位填充"""
        # 用 LLM 提取实体
        intent_result = await self.intent_service.recognize(user_input, context.history)
        context.slots.update(intent_result.entities)

        # 检查是否还有缺失
        required = self.REQUIRED_SLOTS.get(context.intent, [])
        missing = [s for s in required if s not in context.slots]

        if missing:
            return f"收到，请问您的{missing[0]}是什么？"

        context.state = DialogueState.EXECUTING
        return await self._handle_executing(user_input, context)

    async def _handle_executing(self, user_input: str, context: DialogueContext) -> str:
        """执行动作"""
        # 这里可以调用实际的业务系统
        if context.intent == "售后.退货":
            return f"好的，已为您提交退货申请（订单：{context.slots.get('订单号')}），请保持手机畅通，我们会在24小时内联系您。"
        elif context.intent == "售后.换货":
            return f"好的，已为您提交换货申请，请等待审核。"
        else:
            return "好的，我已记录您的反馈，会尽快处理。"

    def _should_transfer_human(self, user_input: str, context: DialogueContext) -> bool:
        """判断是否转人工"""
        # 显式请求
        if any(kw in user_input for kw in ["人工", "客服", "转人工"]):
            return True
        # 多次重试
        if context.retry_count >= 3:
            return True
        # 敏感意图
        if context.intent and "投诉" in context.intent:
            return True
        return False

    async def _transfer_to_human(self, context: DialogueContext) -> str:
        """转接人工"""
        context.state = DialogueState.HUMAN_QUEUE
        position = await self.queue_service.enqueue(context)
        return f"正在为您转接人工客服，当前排队位置：第{position}位，请稍候..."
'''

print("\n" + "=" * 60)
print("第三部分：对话管理服务")
print("=" * 60)
print(DIALOGUE_SERVICE)


# ==================== 工单服务 ====================

TICKET_SERVICE = '''
# app/services/ticket_service.py
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.ticket import Ticket, TicketStatus

class TicketService:
    """工单服务"""

    def __init__(self, db: Session):
        self.db = db

    async def create_ticket(
        self,
        user_id: str,
        session_id: str,
        intent: str,
        content: str,
        priority: int = 2
    ) -> Ticket:
        """创建工单"""
        ticket = Ticket(
            user_id=user_id,
            session_id=session_id,
            intent=intent,
            content=content,
            priority=priority,
            status=TicketStatus.PENDING,
            created_at=datetime.utcnow()
        )
        self.db.add(ticket)
        self.db.commit()
        return ticket

    async def assign_ticket(self, ticket_id: str, agent_id: str):
        """分配工单给坐席"""
        ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        ticket.agent_id = agent_id
        ticket.status = TicketStatus.PROCESSING
        ticket.assigned_at = datetime.utcnow()
        self.db.commit()

    async def close_ticket(self, ticket_id: str, resolution: str):
        """关闭工单"""
        ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        ticket.status = TicketStatus.CLOSED
        ticket.resolution = resolution
        ticket.closed_at = datetime.utcnow()
        self.db.commit()
'''

print("\n" + "=" * 60)
print("第四部分：工单服务")
print("=" * 60)
print(TICKET_SERVICE)


# ==================== API 接口 ====================

API_CODE = '''
# app/api/chat.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import StreamingResponse
from app.services.dialogue_service import DialogueService
from app.dependencies import get_dialogue_service

router = APIRouter(prefix="/chat", tags=["chat"])

# WebSocket 连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        self.active_connections.pop(session_id, None)

    async def send_message(self, session_id: str, message: str):
        ws = self.active_connections.get(session_id)
        if ws:
            await ws.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    dialogue_service: DialogueService = Depends(get_dialogue_service)
):
    """WebSocket 实时对话"""
    await manager.connect(session_id, websocket)
    try:
        while True:
            user_input = await websocket.receive_text()
            response = await dialogue_service.process(session_id, user_input)
            await websocket.send_json({
                "type": "message",
                "content": response
            })
    except WebSocketDisconnect:
        manager.disconnect(session_id)

@router.post("/message")
async def send_message(
    session_id: str,
    message: str,
    dialogue_service: DialogueService = Depends(get_dialogue_service)
):
    """HTTP 消息接口"""
    response = await dialogue_service.process(session_id, message)
    return {"response": response}


# app/api/agent.py
from fastapi import APIRouter, Depends
from app.services.queue_service import QueueService
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/agent", tags=["agent"])

@router.get("/queue")
async def get_queue(queue_service: QueueService = Depends()):
    """获取等待队列"""
    return await queue_service.get_pending_sessions()

@router.post("/accept/{session_id}")
async def accept_session(
    session_id: str,
    agent_id: str,
    queue_service: QueueService = Depends()
):
    """接入会话"""
    return await queue_service.assign_to_agent(session_id, agent_id)

@router.post("/transfer/{session_id}")
async def transfer_session(
    session_id: str,
    target_agent_id: str,
    queue_service: QueueService = Depends()
):
    """转接会话"""
    return await queue_service.transfer(session_id, target_agent_id)
'''

print("\n" + "=" * 60)
print("第五部分：API 接口")
print("=" * 60)
print(API_CODE)


# ==================== 情感分析 ====================

SENTIMENT_CODE = '''
# app/utils/sentiment.py
import google.generativeai as genai

class SentimentAnalyzer:
    """情感分析器"""

    PROMPT = """分析以下对话中用户的情感状态，返回JSON：
{{"sentiment": "positive/neutral/negative", "score": 0.0-1.0, "reason": "原因"}}

对话内容：
{messages}"""

    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    async def analyze(self, messages: list) -> dict:
        """分析情感"""
        # 提取用户消息
        user_msgs = [m["content"] for m in messages if m["role"] == "user"]
        text = "\\n".join(user_msgs[-5:])  # 最近5条

        response = self.model.generate_content(
            self.PROMPT.format(messages=text)
        )

        return json.loads(response.text)
'''

print("\n" + "=" * 60)
print("第六部分：情感分析")
print("=" * 60)
print(SENTIMENT_CODE)


print("\n" + "=" * 60)
print("课程完成！下一步：05-code-assistant-design.py")
print("=" * 60)
