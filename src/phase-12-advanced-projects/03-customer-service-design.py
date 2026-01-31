"""
AI 客服系统 - 系统设计
====================

学习目标：
    1. 理解智能客服系统的架构
    2. 掌握意图识别和对话管理
    3. 设计人机协作流程

项目概述：
    构建一个支持多轮对话、意图识别、知识库问答、
    人工接入的企业级 AI 客服系统。

技术栈：
    - 后端：FastAPI + LangChain
    - 对话管理：状态机 + LLM
    - 存储：Redis + PostgreSQL
"""


# ==================== 第一部分：需求分析 ====================


def requirements():
    """需求分析"""
    print("=" * 60)
    print("第一部分：需求分析")
    print("=" * 60)

    print("""
    📌 核心功能：
    ┌─────────────────────────────────────────────────────────┐
    │ 1. 智能问答                                            │
    │    - 常见问题自动回复                                  │
    │    - 知识库检索回答                                    │
    │    - 多轮对话理解                                      │
    │                                                        │
    │ 2. 意图识别                                            │
    │    - 用户意图分类                                      │
    │    - 实体抽取                                          │
    │    - 情感分析                                          │
    │                                                        │
    │ 3. 工单系统                                            │
    │    - 自动创建工单                                      │
    │    - 工单状态跟踪                                      │
    │    - 优先级排序                                        │
    │                                                        │
    │ 4. 人工接入                                            │
    │    - 智能转人工                                        │
    │    - 会话转接                                          │
    │    - 坐席工作台                                        │
    └─────────────────────────────────────────────────────────┘

    📌 典型意图分类：
    - 咨询类：产品咨询、价格咨询、使用帮助
    - 投诉类：质量投诉、服务投诉
    - 售后类：退换货、维修保修
    - 其他：闲聊、无法识别
    """)


# ==================== 第二部分：架构设计 ====================


def architecture():
    """架构设计"""
    print("\n" + "=" * 60)
    print("第二部分：系统架构")
    print("=" * 60)

    print("""
    📌 整体架构：
    ┌─────────────────────────────────────────────────────────────┐
    │                        接入层                               │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
    │  │  Web     │ │  App     │ │  微信    │ │  电话    │       │
    │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │
    └───────┼────────────┼────────────┼────────────┼─────────────┘
            └────────────┴────────────┴────────────┘
                                 │
    ┌────────────────────────────┴───────────────────────────────┐
    │                      对话管理层                             │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │                 对话状态机                           │   │
    │  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │   │
    │  │  │ 意图   │→│ 槽位   │→│ 确认   │→│ 执行   │        │   │
    │  │  │ 识别   │ │ 填充   │ │ 动作   │ │ 动作   │        │   │
    │  │  └────────┘ └────────┘ └────────┘ └────────┘        │   │
    │  └─────────────────────────────────────────────────────┘   │
    └────────────────────────────┬───────────────────────────────┘
                                 │
    ┌────────────────────────────┴───────────────────────────────┐
    │                       能力层                                │
    │  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
    │  │  意图识别  │ │  知识问答  │ │  情感分析  │              │
    │  └────────────┘ └────────────┘ └────────────┘              │
    │  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
    │  │  实体抽取  │ │  工单系统  │ │  人工路由  │              │
    │  └────────────┘ └────────────┘ └────────────┘              │
    └─────────────────────────────────────────────────────────────┘

    📌 对话状态流转：
    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │ 接待    │ -> │ 理解    │ -> │ 处理    │ -> │ 结束    │
    │ greeting│    │ 意图/槽 │    │ 执行    │    │ farewell│
    └─────────┘    └─────────┘    └─────────┘    └─────────┘
         │              │              │              │
         │              ▼              │              │
         │        ┌─────────┐         │              │
         │        │ 转人工  │◄────────┘              │
         │        │ human   │                        │
         │        └─────────┘                        │
         └───────────────────────────────────────────┘
    """)


# ==================== 第三部分：意图识别设计 ====================


def intent_design():
    """意图识别设计"""
    print("\n" + "=" * 60)
    print("第三部分：意图识别设计")
    print("=" * 60)

    print("""
    📌 意图分类体系：
    ┌─────────────────────────────────────────────────────────┐
    │ 一级意图      │ 二级意图        │ 示例                 │
    ├───────────────┼─────────────────┼──────────────────────┤
    │ 咨询          │ 产品咨询        │ "这个产品怎么用"     │
    │               │ 价格咨询        │ "多少钱"             │
    │               │ 配送咨询        │ "多久能到"           │
    ├───────────────┼─────────────────┼──────────────────────┤
    │ 投诉          │ 产品投诉        │ "质量有问题"         │
    │               │ 服务投诉        │ "态度太差"           │
    ├───────────────┼─────────────────┼──────────────────────┤
    │ 售后          │ 退货            │ "我要退货"           │
    │               │ 换货            │ "换一个"             │
    │               │ 维修            │ "坏了"               │
    ├───────────────┼─────────────────┼──────────────────────┤
    │ 其他          │ 闲聊            │ "你好"               │
    │               │ 转人工          │ "人工客服"           │
    └───────────────┴─────────────────┴──────────────────────┘

    📌 实体类型：
    - 产品名称
    - 订单号
    - 时间
    - 金额
    - 联系方式
    """)


# ==================== 第四部分：对话管理设计 ====================


def dialogue_design():
    """对话管理设计"""
    print("\n" + "=" * 60)
    print("第四部分：对话管理设计")
    print("=" * 60)

    code = '''
# 对话状态定义
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional

class DialogueState(Enum):
    """对话状态枚举"""
    GREETING = "greeting"       # 问候
    INTENT_RECOGNITION = "intent"  # 意图识别
    SLOT_FILLING = "slot"       # 槽位填充
    CONFIRM = "confirm"         # 确认
    EXECUTE = "execute"         # 执行
    HUMAN_TRANSFER = "human"    # 转人工
    FAREWELL = "farewell"       # 结束

@dataclass
class DialogueContext:
    """对话上下文"""
    session_id: str
    user_id: str
    state: DialogueState = DialogueState.GREETING
    intent: Optional[str] = None
    slots: Dict[str, str] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)
    sentiment: Optional[str] = None
    transfer_reason: Optional[str] = None

class DialogueManager:
    """对话管理器"""

    # 意图对应的必需槽位
    INTENT_SLOTS = {
        "退货": ["订单号", "退货原因"],
        "换货": ["订单号", "换货原因", "期望商品"],
        "投诉": ["投诉内容", "期望处理"],
    }

    def __init__(self, intent_service, rag_service, llm_service):
        self.intent_service = intent_service
        self.rag_service = rag_service
        self.llm_service = llm_service

    async def process(self, user_input: str, context: DialogueContext) -> str:
        """处理用户输入"""
        # 更新历史
        context.history.append({"role": "user", "content": user_input})

        # 检查是否要转人工
        if self._should_transfer(user_input, context):
            context.state = DialogueState.HUMAN_TRANSFER
            return "正在为您转接人工客服，请稍候..."

        # 根据状态处理
        response = await self._handle_state(user_input, context)

        # 更新历史
        context.history.append({"role": "assistant", "content": response})
        return response

    async def _handle_state(self, user_input: str, context: DialogueContext) -> str:
        """根据状态处理"""
        if context.state == DialogueState.GREETING:
            return await self._handle_greeting(user_input, context)

        elif context.state == DialogueState.INTENT_RECOGNITION:
            return await self._handle_intent(user_input, context)

        elif context.state == DialogueState.SLOT_FILLING:
            return await self._handle_slot(user_input, context)

        elif context.state == DialogueState.CONFIRM:
            return await self._handle_confirm(user_input, context)

    def _should_transfer(self, user_input: str, context: DialogueContext) -> bool:
        """判断是否需要转人工"""
        # 显式请求
        transfer_keywords = ["人工", "客服", "转人工", "真人"]
        if any(kw in user_input for kw in transfer_keywords):
            return True

        # 负面情绪
        if context.sentiment == "negative" and len(context.history) > 6:
            return True

        return False
'''
    print(code)


# ==================== 第五部分：人工接入设计 ====================


def human_transfer():
    """人工接入设计"""
    print("\n" + "=" * 60)
    print("第五部分：人工接入设计")
    print("=" * 60)

    print("""
    📌 转人工触发条件：
    ┌─────────────────────────────────────────────────────────┐
    │ 1. 用户显式请求转人工                                   │
    │ 2. 连续 3 次无法理解用户意图                            │
    │ 3. 涉及敏感操作（大额退款、投诉等）                     │
    │ 4. 用户情绪负面且多轮未解决                             │
    │ 5. 机器人置信度低于阈值                                 │
    └─────────────────────────────────────────────────────────┘

    📌 会话转接流程：
    ┌────────────────────────────────────────────────────────┐
    │ 1. AI 整理会话摘要                                     │
    │    - 用户意图                                          │
    │    - 已收集的信息（槽位）                              │
    │    - 转接原因                                          │
    │                                                        │
    │ 2. 分配坐席                                            │
    │    - 技能组匹配                                        │
    │    - 坐席负载均衡                                      │
    │    - 优先级排队                                        │
    │                                                        │
    │ 3. 坐席接入                                            │
    │    - 推送会话摘要                                      │
    │    - 展示对话历史                                      │
    │    - 提供知识库辅助                                    │
    └────────────────────────────────────────────────────────┘

    📌 坐席辅助功能：
    - 实时话术推荐
    - 知识库快速检索
    - 工单模板填充
    - 情绪预警提示
    """)


# ==================== 第六部分：系统指标 ====================


def metrics():
    """系统指标"""
    print("\n" + "=" * 60)
    print("第六部分：关键指标设计")
    print("=" * 60)

    print("""
    📌 核心指标：
    ┌─────────────────┬──────────────────────────────────────┐
    │ 指标名称        │ 说明                                 │
    ├─────────────────┼──────────────────────────────────────┤
    │ 自动解决率      │ AI 独立解决的会话占比               │
    │ 意图识别准确率  │ 意图分类的正确率                    │
    │ 用户满意度      │ 会话结束后的评价                    │
    │ 平均响应时间    │ 从收到消息到回复的时间              │
    │ 转人工率        │ 需要转接人工的会话占比              │
    │ 首次响应时间    │ 用户首条消息的响应时间              │
    └─────────────────┴──────────────────────────────────────┘

    📌 目标值：
    - 自动解决率：> 80%
    - 意图识别准确率：> 90%
    - 用户满意度：> 4.0/5.0
    - 平均响应时间：< 2s
    - 转人工率：< 20%
    """)


def main():
    requirements()
    architecture()
    intent_design()
    dialogue_design()
    human_transfer()
    metrics()
    print("\n下一步：04-customer-service-implementation.py")


if __name__ == "__main__":
    main()
