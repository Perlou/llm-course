"""
记忆类型详解
============

学习目标：
    1. 理解 Memory 的作用和类型
    2. 掌握 ConversationBufferMemory
    3. 了解 WindowMemory 和 SummaryMemory

核心概念：
    - Memory：存储对话历史的组件
    - BufferMemory：完整历史存储
    - WindowMemory：滑动窗口存储
    - SummaryMemory：摘要存储

前置知识：
    - 06-sequential-chains.py

环境要求：
    - pip install langchain langchain-google-genai python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Memory 概述 ====================


def memory_overview():
    """Memory 概述"""
    print("=" * 60)
    print("第一部分：Memory 概述")
    print("=" * 60)

    print("""
    为什么需要 Memory？
    ─────────────────
    
    LLM 本身是无状态的，每次调用都是独立的。
    Memory 组件让 LLM 能够"记住"之前的对话。
    
    Memory 类型对比：
    ─────────────────
    
    | 类型             | 特点                    | 适用场景      |
    |-----------------|------------------------|--------------|
    | BufferMemory    | 存储完整历史            | 短对话        |
    | WindowMemory    | 只保留最近 k 轮         | 中等对话      |
    | SummaryMemory   | 使用 LLM 总结历史       | 长对话        |
    | TokenBufferMem  | 按 token 数限制         | 精确成本控制   |
    """)


# ==================== 第二部分：ConversationBufferMemory ====================


def buffer_memory_demo():
    """ConversationBufferMemory 演示"""
    print("\n" + "=" * 60)
    print("第二部分：ConversationBufferMemory")
    print("=" * 60)

    from langchain_community.chat_message_histories import ChatMessageHistory

    # 创建 Memory (使用 ChatMessageHistory 替代已废弃的 ConversationBufferMemory)
    memory = ChatMessageHistory()

    # 手动添加对话
    memory.add_user_message("你好，我叫张三")
    memory.add_ai_message("你好张三！很高兴认识你！")
    memory.add_user_message("我喜欢编程")
    memory.add_ai_message("编程是个很棒的技能！你主要用什么语言？")

    print("📌 存储的对话历史：")
    for msg in memory.messages:
        role = type(msg).__name__.replace("Message", "")
        print(f"  [{role}] {msg.content}")

    # 清空
    print("\n📌 清空记忆：")
    memory.clear()
    print(f"  清空后: {memory.messages}")


# ==================== 第三部分：ConversationBufferWindowMemory ====================


def window_memory_demo():
    """ConversationBufferWindowMemory 演示"""
    print("\n" + "=" * 60)
    print("第三部分：WindowMemory（滑动窗口）")
    print("=" * 60)

    from langchain_community.chat_message_histories import ChatMessageHistory

    # 创建一个辅助类来实现窗口记忆
    class WindowMemory:
        def __init__(self, k=2):
            self.k = k  # 保留最近 k 轮对话（1轮 = 1个用户消息 + 1个AI消息）
            self.history = ChatMessageHistory()

        def add_conversation(self, user_msg, ai_msg):
            self.history.add_user_message(user_msg)
            self.history.add_ai_message(ai_msg)
            # 保持窗口大小：每轮对话有2条消息（用户+AI）
            max_messages = self.k * 2
            if len(self.history.messages) > max_messages:
                # 删除最旧的消息
                self.history.messages = self.history.messages[-max_messages:]

        @property
        def messages(self):
            return self.history.messages

    # 只保留最近 2 轮
    memory = WindowMemory(k=2)

    # 添加 3 轮对话
    conversations = [
        ("你好", "你好！"),
        ("今天星期几？", "今天是星期三"),
        ("天气怎么样？", "天气晴朗"),
    ]

    print("📌 添加 3 轮对话（k=2 只保留最近 2 轮）：")
    for user, ai in conversations:
        memory.add_conversation(user, ai)
        print(f"  添加: {user} -> {ai}")

    print("\n📌 实际保留的历史：")
    for msg in memory.messages:
        role = type(msg).__name__.replace("Message", "")
        print(f"  [{role}] {msg.content}")


# ==================== 第四部分：在链中使用 Memory ====================


def memory_in_chain():
    """在链中使用 Memory"""
    print("\n" + "=" * 60)
    print("第四部分：在链中使用 Memory")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.runnables.history import RunnableWithMessageHistory
        from langchain_community.chat_message_histories import ChatMessageHistory

        # 会话存储
        store = {}

        def get_session_history(session_id: str):
            if session_id not in store:
                store[session_id] = ChatMessageHistory()
            return store[session_id]

        # 创建链
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一个友好的助手"),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )
        chain = prompt | llm

        # 添加历史支持
        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

        print("📌 多轮对话测试：")

        # 第一轮
        r1 = chain_with_history.invoke(
            {"input": "你好，我叫李明"},
            config={"configurable": {"session_id": "user123"}},
        )
        print(f"  用户: 你好，我叫李明")
        print(f"  AI: {r1.content}")

        # 第二轮
        r2 = chain_with_history.invoke(
            {"input": "我叫什么名字？"},
            config={"configurable": {"session_id": "user123"}},
        )
        print(f"\n  用户: 我叫什么名字？")
        print(f"  AI: {r2.content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第五部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：创建客服机器人
        使用 ChatMessageHistory 创建能记住用户信息的客服。

        ✅ 参考答案：
        ```python
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.runnables.history import RunnableWithMessageHistory
        from langchain_community.chat_message_histories import ChatMessageHistory

        store = {}
        def get_session(session_id):
            if session_id not in store:
                store[session_id] = ChatMessageHistory()
            return store[session_id]

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是客服助手。记住用户的姓名、订单号等信息。"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        customer_service = RunnableWithMessageHistory(
            prompt | llm,
            get_session,
            input_messages_key="input",
            history_messages_key="history"
        )
        ```

    练习 2：测试 WindowMemory
        设置不同的 k 值，观察记忆保留情况。

        ✅ 参考答案：
        ```python
        from langchain_community.chat_message_histories import ChatMessageHistory

        # 使用前面定义的 WindowMemory 类
        class WindowMemory:
            def __init__(self, k=2):
                self.k = k
                self.history = ChatMessageHistory()
            
            def add_conversation(self, user_msg, ai_msg):
                self.history.add_user_message(user_msg)
                self.history.add_ai_message(ai_msg)
                max_messages = self.k * 2
                if len(self.history.messages) > max_messages:
                    self.history.messages = self.history.messages[-max_messages:]

        # 测试 k=1（只记住最后1轮）
        memory_k1 = WindowMemory(k=1)

        # 测试 k=3（记住最后3轮）
        memory_k3 = WindowMemory(k=3)

        # 添加5轮对话
        for i in range(5):
            memory_k1.add_conversation(f"问题{i}", f"回答{i}")
            memory_k3.add_conversation(f"问题{i}", f"回答{i}")

        # 对比
        print(f"k=1 保留: {len(memory_k1.history.messages)} 条")
        print(f"k=3 保留: {len(memory_k3.history.messages)} 条")
        ```

    练习 3：多会话管理
        使用 session_id 管理多个独立会话。

        ✅ 参考答案：
        ```python
        sessions = {}

        def get_or_create_session(user_id: str) -> ChatMessageHistory:
            if user_id not in sessions:
                sessions[user_id] = ChatMessageHistory()
            return sessions[user_id]

        # 用户 A 的会话
        session_a = get_or_create_session("user_a")
        session_a.add_user_message("我是A用户")

        # 用户 B 的会话
        session_b = get_or_create_session("user_b")
        session_b.add_user_message("我是B用户")

        # 会话完全隔离
        print(f"用户A消息数: {len(session_a.messages)}")
        print(f"用户B消息数: {len(session_b.messages)}")
        ```

    思考题：
        1. Buffer vs Window 何时选哪个？
           
           ✅ 答案：
           | 场景 | 选择 | 原因 |
           |------|------|------|
           | 短对话 (<10轮) | Buffer | 保留完整上下文 |
           | 长对话 | Window | 控制 token 消耗 |
           | 需要回顾历史 | Buffer | 信息完整 |
           | 成本敏感 | Window | 限制 token |

        2. 如何处理超长对话的 token 限制？
           
           ✅ 答案：
           - 使用 WindowMemory 限制轮数
           - 使用 SummaryMemory 压缩历史
           - 使用 TokenBufferMemory 按 token 数限制
           - 混合策略：最近几轮完整 + 之前的摘要
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 记忆类型详解")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
        return

    try:
        memory_overview()
        buffer_memory_demo()
        window_memory_demo()
        memory_in_chain()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：08-conversation-memory.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
