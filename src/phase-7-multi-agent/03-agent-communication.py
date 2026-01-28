"""
Agent 通信机制
==============

学习目标：
    1. 理解 Agent 间通信的重要性
    2. 掌握消息传递模式
    3. 学会使用消息总线架构
    4. 理解共享状态管理

核心概念：
    - 消息传递 (Message Passing)
    - 发布-订阅模式 (Pub/Sub)
    - 共享黑板 (Blackboard)
    - 状态同步

前置知识：
    - 01-multi-agent-intro.py
    - 02-langgraph-basics.py
    - 异步编程基础

环境要求：
    - pip install openai python-dotenv
"""

import os
import asyncio
from dotenv import load_dotenv
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime
from enum import Enum
import uuid

load_dotenv()


# ==================== 第一部分：Agent 通信概述 ====================


def communication_overview():
    """Agent 通信概述"""
    print("=" * 60)
    print("第一部分：Agent 通信概述")
    print("=" * 60)

    print("""
    为什么 Agent 需要通信？
    ─────────────────────
    
    多 Agent 系统中，Agent 需要：
    ✅ 共享信息和发现
    ✅ 协调行动
    ✅ 请求帮助
    ✅ 报告进度
    ✅ 传递任务结果
    
    通信模式对比
    ───────────
    
    ┌─────────────────┬─────────────────┬─────────────────┐
    │   直接消息传递   │   发布-订阅     │   共享黑板      │
    ├─────────────────┼─────────────────┼─────────────────┤
    │                 │                 │                 │
    │  A ──────► B    │    ┌── B        │   ┌─────────┐   │
    │                 │    │            │   │Blackboard│   │
    │  点对点         │ A ─┼── C        │   └────┬────┘   │
    │                 │    │            │   A   B   C     │
    │                 │    └── D        │   ↑↓  ↑↓  ↑↓    │
    ├─────────────────┼─────────────────┼─────────────────┤
    │ 简单直接        │ 松耦合          │ 共享知识        │
    │ 需要知道接收者  │ 主题订阅        │ 读写共享状态    │
    └─────────────────┴─────────────────┴─────────────────┘
    """)


# ==================== 第二部分：消息数据结构 ====================


def message_data_structure():
    """消息数据结构"""
    print("\n" + "=" * 60)
    print("第二部分：消息数据结构")
    print("=" * 60)

    print("\n📌 定义消息类")

    class MessageType(Enum):
        """消息类型"""

        TEXT = "text"  # 文本消息
        TASK = "task"  # 任务分配
        RESULT = "result"  # 结果返回
        STATUS = "status"  # 状态更新
        REQUEST = "request"  # 请求帮助
        BROADCAST = "broadcast"  # 广播消息

    @dataclass
    class Message:
        """Agent 间通信消息"""

        id: str = field(default_factory=lambda: str(uuid.uuid4()))
        sender: str = ""
        receiver: str = ""  # 空字符串表示广播
        content: Any = None
        msg_type: MessageType = MessageType.TEXT
        timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
        priority: int = 0  # 0=普通, 1=高, 2=紧急
        metadata: Dict = field(default_factory=dict)
        reply_to: Optional[str] = None  # 回复哪条消息

        def __repr__(self):
            return f"Message({self.msg_type.value}: {self.sender} → {self.receiver or 'ALL'})"

    # 演示消息创建
    print("""
    class MessageType(Enum):
        TEXT = "text"           # 文本消息
        TASK = "task"           # 任务分配
        RESULT = "result"       # 结果返回
        STATUS = "status"       # 状态更新
        REQUEST = "request"     # 请求帮助
        BROADCAST = "broadcast" # 广播消息

    @dataclass
    class Message:
        id: str                    # 唯一标识
        sender: str                # 发送者
        receiver: str              # 接收者（空=广播）
        content: Any               # 消息内容
        msg_type: MessageType      # 消息类型
        timestamp: str             # 时间戳
        priority: int              # 优先级
        metadata: Dict             # 元数据
        reply_to: Optional[str]    # 回复标识
    """)

    # 创建示例消息
    print("\n📌 消息示例：")

    msg1 = Message(
        sender="Supervisor",
        receiver="Worker1",
        content={"task": "分析数据", "deadline": "2024-01-01"},
        msg_type=MessageType.TASK,
        priority=1,
    )

    msg2 = Message(
        sender="Worker1",
        receiver="Supervisor",
        content={"status": "completed", "result": "分析完成"},
        msg_type=MessageType.RESULT,
        reply_to=msg1.id,
    )

    print(f"   任务消息: {msg1}")
    print(f"   结果消息: {msg2}")

    return Message, MessageType


# ==================== 第三部分：直接消息传递 ====================


def direct_messaging():
    """直接消息传递"""
    print("\n" + "=" * 60)
    print("第三部分：直接消息传递")
    print("=" * 60)

    print("""
    直接消息传递模式
    ───────────────
    
    最简单的通信方式：Agent A 直接发送消息给 Agent B
    
         ┌─────────┐                ┌─────────┐
         │ Agent A │ ──── msg ────► │ Agent B │
         │ 发送者  │                │ 接收者  │
         └─────────┘                └─────────┘
    """)

    print("\n📌 简单的 Agent 实现：")

    class SimpleAgent:
        """支持直接消息传递的 Agent"""

        def __init__(self, name: str):
            self.name = name
            self.inbox: List[Dict] = []
            self.contacts: Dict[str, "SimpleAgent"] = {}

        def register_contact(self, agent: "SimpleAgent"):
            """注册联系人"""
            self.contacts[agent.name] = agent

        def send_message(self, receiver_name: str, content: str):
            """发送消息"""
            if receiver_name not in self.contacts:
                print(f"❌ {self.name}: 未找到联系人 {receiver_name}")
                return False

            message = {
                "id": str(uuid.uuid4()),
                "sender": self.name,
                "receiver": receiver_name,
                "content": content,
                "timestamp": datetime.now().isoformat(),
            }

            receiver = self.contacts[receiver_name]
            receiver.receive_message(message)
            print(f"📤 {self.name} → {receiver_name}: {content}")
            return True

        def receive_message(self, message: Dict):
            """接收消息"""
            self.inbox.append(message)

        def process_inbox(self):
            """处理收件箱"""
            while self.inbox:
                msg = self.inbox.pop(0)
                print(
                    f"📥 {self.name} 收到来自 {msg['sender']} 的消息: {msg['content']}"
                )
                # 可以在这里添加消息处理逻辑

    # 演示
    print("\n🚀 直接消息传递演示：")
    print("-" * 40)

    alice = SimpleAgent("Alice")
    bob = SimpleAgent("Bob")

    # 相互注册
    alice.register_contact(bob)
    bob.register_contact(alice)

    # 发送消息
    alice.send_message("Bob", "你好，Bob！我需要你帮忙分析数据。")
    bob.send_message("Alice", "收到，Alice！我马上开始处理。")

    print("\n📬 处理收件箱：")
    bob.process_inbox()
    alice.process_inbox()


# ==================== 第四部分：消息总线 ====================


def message_bus_pattern():
    """消息总线模式"""
    print("\n" + "=" * 60)
    print("第四部分：消息总线模式")
    print("=" * 60)

    print("""
    消息总线架构
    ───────────
    
    所有 Agent 通过中央消息总线通信，支持：
    - 点对点消息
    - 广播消息
    - 主题订阅
    
       ┌─────────┐     ┌─────────┐     ┌─────────┐
       │ Agent A │     │ Agent B │     │ Agent C │
       └────┬────┘     └────┬────┘     └────┬────┘
            │               │               │
       ─────┴───────────────┴───────────────┴─────
                            │
                  ┌─────────┴─────────┐
                  │    Message Bus     │
                  │  ┌─────────────┐  │
                  │  │ Topic: tasks│  │
                  │  │ Topic: events│ │
                  │  │ Topic: status│ │
                  │  └─────────────┘  │
                  └───────────────────┘
    """)

    print("\n📌 消息总线实现：")

    class MessageBus:
        """消息总线 - 中央消息调度器"""

        def __init__(self):
            self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
            self.message_history: List[Dict] = []
            self.agents: Dict[str, Any] = {}

        def register_agent(self, name: str, agent: Any):
            """注册 Agent"""
            self.agents[name] = agent
            print(f"   ✅ 注册 Agent: {name}")

        def subscribe(self, topic: str, handler: Callable):
            """订阅主题"""
            self.subscribers[topic].append(handler)
            print(f"   📥 订阅主题: {topic}")

        def publish(self, topic: str, message: Dict):
            """发布消息到主题"""
            message["topic"] = topic
            message["timestamp"] = datetime.now().isoformat()
            self.message_history.append(message)

            handlers = self.subscribers.get(topic, [])
            for handler in handlers:
                try:
                    handler(message)
                except Exception as e:
                    print(f"   ❌ 处理消息出错: {e}")

            print(f"   📢 发布到 {topic}: {message.get('content', '')[:30]}...")

        def send_direct(self, sender: str, receiver: str, content: Any):
            """直接发送消息给特定 Agent"""
            if receiver not in self.agents:
                print(f"   ❌ 未找到 Agent: {receiver}")
                return False

            message = {
                "sender": sender,
                "receiver": receiver,
                "content": content,
                "type": "direct",
            }

            agent = self.agents[receiver]
            if hasattr(agent, "receive_message"):
                agent.receive_message(message)
            print(f"   📤 {sender} → {receiver}: {str(content)[:30]}...")
            return True

        def broadcast(self, sender: str, content: Any):
            """广播消息给所有 Agent"""
            message = {"sender": sender, "content": content, "type": "broadcast"}

            for name, agent in self.agents.items():
                if name != sender and hasattr(agent, "receive_message"):
                    agent.receive_message(message)

            print(f"   📢 {sender} 广播: {str(content)[:30]}...")

    class BusAgent:
        """使用消息总线的 Agent"""

        def __init__(self, name: str, bus: MessageBus):
            self.name = name
            self.bus = bus
            self.inbox: List[Dict] = []
            bus.register_agent(name, self)

        def receive_message(self, message: Dict):
            """接收消息"""
            self.inbox.append(message)

        def send_to(self, receiver: str, content: Any):
            """发送给指定 Agent"""
            self.bus.send_direct(self.name, receiver, content)

        def broadcast(self, content: Any):
            """广播消息"""
            self.bus.broadcast(self.name, content)

        def subscribe(self, topic: str):
            """订阅主题"""
            self.bus.subscribe(topic, self._handle_topic)

        def _handle_topic(self, message: Dict):
            """处理主题消息"""
            self.inbox.append(message)

    # 演示
    print("\n🚀 消息总线演示：")
    print("-" * 40)

    bus = MessageBus()

    supervisor = BusAgent("Supervisor", bus)
    worker1 = BusAgent("Worker1", bus)
    worker2 = BusAgent("Worker2", bus)

    # 订阅主题
    worker1.subscribe("tasks")
    worker2.subscribe("tasks")

    print("\n📤 发送消息：")
    supervisor.send_to("Worker1", "请处理任务 A")
    supervisor.broadcast("所有人注意：系统即将维护")
    bus.publish("tasks", {"content": "新任务：数据分析", "priority": 1})

    print(f"\n📬 Worker1 收件箱: {len(worker1.inbox)} 条消息")
    print(f"📬 Worker2 收件箱: {len(worker2.inbox)} 条消息")


# ==================== 第五部分：共享黑板模式 ====================


def blackboard_pattern():
    """共享黑板模式"""
    print("\n" + "=" * 60)
    print("第五部分：共享黑板模式")
    print("=" * 60)

    print("""
    黑板模式 (Blackboard Pattern)
    ────────────────────────────
    
    所有 Agent 共享一个"黑板"来读写信息。
    适合需要共享知识和协作推理的场景。
    
       ┌─────────────────────────────────────┐
       │            BLACKBOARD               │
       │  ┌─────────┐  ┌─────────────────┐  │
       │  │ GOALS   │  │ FACTS           │  │
       │  │ • 目标1 │  │ • 事实1         │  │
       │  │ • 目标2 │  │ • 事实2         │  │
       │  └─────────┘  └─────────────────┘  │
       │  ┌─────────────┐  ┌─────────────┐  │
       │  │ HYPOTHESES  │  │ SOLUTIONS   │  │
       │  │ • 假设1     │  │ • 方案1     │  │
       │  └─────────────┘  └─────────────┘  │
       └───────────┬────────────┬───────────┘
                   │            │
        ┌──────────┼────────────┼──────────┐
        ▼          ▼            ▼          ▼
    ┌───────┐ ┌───────┐   ┌───────┐  ┌───────┐
    │Agent A│ │Agent B│   │Agent C│  │Agent D│
    └───────┘ └───────┘   └───────┘  └───────┘
    """)

    print("\n📌 黑板实现：")

    class Blackboard:
        """共享黑板"""

        def __init__(self):
            self.sections = {
                "goals": {},  # 目标
                "facts": {},  # 确定的事实
                "hypotheses": {},  # 假设/推测
                "solutions": {},  # 解决方案
                "status": {},  # 状态信息
            }
            self.history: List[Dict] = []

        def write(
            self,
            section: str,
            key: str,
            value: Any,
            author: str = "system",
            confidence: float = 1.0,
        ):
            """写入黑板"""
            if section not in self.sections:
                print(f"❌ 未知分区: {section}")
                return False

            entry = {
                "value": value,
                "author": author,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
            }

            self.sections[section][key] = entry
            self.history.append(
                {"action": "write", "section": section, "key": key, "entry": entry}
            )

            print(f"   ✍️ {author} 写入 [{section}] {key}: {str(value)[:30]}...")
            return True

        def read(self, section: str, key: str = None) -> Any:
            """读取黑板"""
            if section not in self.sections:
                return None

            if key is None:
                return self.sections[section]

            entry = self.sections[section].get(key)
            if entry:
                return entry["value"]
            return None

        def find_by_confidence(
            self, section: str, min_confidence: float = 0.5
        ) -> List[Dict]:
            """按置信度筛选"""
            items = self.sections.get(section, {})
            return [
                {"key": k, **v}
                for k, v in items.items()
                if v["confidence"] >= min_confidence
            ]

        def display(self):
            """显示黑板内容"""
            print("\n" + "=" * 50)
            print("            📋 BLACKBOARD")
            print("=" * 50)

            for section, items in self.sections.items():
                if items:
                    print(f"\n  📁 {section.upper()}")
                    print("  " + "-" * 30)
                    for key, entry in items.items():
                        conf = entry["confidence"]
                        val = str(entry["value"])[:40]
                        print(f"    • {key}: {val} (conf: {conf:.1f})")

    class BlackboardAgent:
        """使用黑板的 Agent"""

        def __init__(self, name: str, blackboard: Blackboard):
            self.name = name
            self.blackboard = blackboard

        def write_fact(self, key: str, value: Any, confidence: float = 1.0):
            """写入事实"""
            self.blackboard.write("facts", key, value, self.name, confidence)

        def write_hypothesis(self, key: str, value: Any, confidence: float = 0.5):
            """写入假设"""
            self.blackboard.write("hypotheses", key, value, self.name, confidence)

        def read_facts(self) -> Dict:
            """读取所有事实"""
            return self.blackboard.read("facts")

    # 演示
    print("\n🚀 黑板模式演示：")
    print("-" * 40)

    board = Blackboard()

    researcher = BlackboardAgent("Researcher", board)
    analyst = BlackboardAgent("Analyst", board)

    # 研究员写入事实
    researcher.write_fact("data_source", "用户访问日志 2024-01", confidence=1.0)
    researcher.write_fact("sample_size", 10000, confidence=1.0)

    # 分析师基于事实提出假设
    analyst.write_hypothesis("trend", "用户活跃度在周末较低", confidence=0.7)
    analyst.write_hypothesis("cause", "可能与工作性质相关", confidence=0.5)

    # 显示黑板
    board.display()


# ==================== 第六部分：异步通信 ====================


def async_communication():
    """异步通信"""
    print("\n" + "=" * 60)
    print("第六部分：异步通信")
    print("=" * 60)

    print("""
    异步消息总线
    ───────────
    
    使用 asyncio 实现非阻塞的消息传递。
    适合 I/O 密集型的多 Agent 系统。
    
    ┌─────────────────────────────────────────────────────┐
    │              Async Message Bus                       │
    │                                                     │
    │   ┌─────────┐  publish   ┌──────────────┐          │
    │   │ Agent A │ ─────────► │ Message Queue │          │
    │   └─────────┘            └───────┬──────┘          │
    │                                  │                  │
    │                            async │ dispatch        │
    │                                  │                  │
    │   ┌─────────┐◄───────────────────┼────────────────┐│
    │   │ Agent B │              ┌─────┴─────┐          ││
    │   └─────────┘              │ Agent C   │          ││
    │                            └───────────┘          ││
    └─────────────────────────────────────────────────────┘
    """)

    print("\n📌 异步消息总线示例代码：")

    print("""
    import asyncio
    from collections import defaultdict
    
    class AsyncMessageBus:
        \"\"\"异步消息总线\"\"\"
        
        def __init__(self):
            self.subscribers = defaultdict(list)
            self.message_queue = asyncio.Queue()
            self.running = False
        
        async def publish(self, topic: str, message: dict):
            \"\"\"发布消息到队列\"\"\"
            await self.message_queue.put((topic, message))
        
        async def subscribe(self, topic: str, handler):
            \"\"\"订阅主题\"\"\"
            self.subscribers[topic].append(handler)
        
        async def start(self):
            \"\"\"启动消息分发\"\"\"
            self.running = True
            while self.running:
                try:
                    topic, message = await asyncio.wait_for(
                        self.message_queue.get(), 
                        timeout=1.0
                    )
                    handlers = self.subscribers.get(topic, [])
                    await asyncio.gather(
                        *[h(message) for h in handlers]
                    )
                except asyncio.TimeoutError:
                    continue
        
        def stop(self):
            self.running = False
    
    # 使用示例
    async def main():
        bus = AsyncMessageBus()
        
        # 启动总线
        bus_task = asyncio.create_task(bus.start())
        
        # 订阅
        async def handler(msg):
            print(f"收到: {msg}")
        
        await bus.subscribe("tasks", handler)
        
        # 发布
        await bus.publish("tasks", {"content": "新任务"})
        
        # 等待处理
        await asyncio.sleep(1)
        bus.stop()
    """)


# ==================== 第七部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现优先级队列
        修改 MessageBus，使消息按优先级处理。
        提示：使用 heapq 或 PriorityQueue。
    
    练习 2：添加消息过滤
        为黑板添加过滤功能，Agent 只接收感兴趣的消息。
        例如：只接收置信度 > 0.8 的假设。
    
    练习 3：实现请求-响应模式
        扩展消息系统，支持同步的请求-响应：
        - Agent A 发送请求
        - 等待 Agent B 的响应
        - 设置超时机制
    
    练习 4：消息持久化
        实现消息历史的持久化存储：
        - 保存到文件
        - 支持历史回放
    
    思考题：
    ────────
    1. 直接消息传递和发布订阅各适合什么场景？
       答：直接传递适合明确的点对点通信，
       发布订阅适合一对多或解耦的场景。
    
    2. 如何处理消息丢失问题？
       答：实现消息确认机制、消息持久化、
       重试逻辑、死信队列。
    
    3. 黑板模式的并发访问如何处理？
       答：使用锁机制、原子操作、
       乐观锁或版本控制。
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("📬 Agent 通信机制")
    print("=" * 60)

    communication_overview()
    message_data_structure()
    direct_messaging()
    message_bus_pattern()
    blackboard_pattern()
    async_communication()
    exercises()

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：04-supervisor-agent.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
