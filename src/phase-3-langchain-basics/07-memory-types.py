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
    - pip install langchain langchain-openai python-dotenv
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

    from langchain.memory import ConversationBufferMemory

    # 创建 Memory
    memory = ConversationBufferMemory(return_messages=True)

    # 手动添加对话
    memory.save_context(
        {"input": "你好，我叫张三"}, {"output": "你好张三！很高兴认识你！"}
    )
    memory.save_context(
        {"input": "我喜欢编程"}, {"output": "编程是个很棒的技能！你主要用什么语言？"}
    )

    print("📌 存储的对话历史：")
    history = memory.load_memory_variables({})
    for msg in history["history"]:
        role = type(msg).__name__.replace("Message", "")
        print(f"  [{role}] {msg.content}")

    # 清空
    print("\n📌 清空记忆：")
    memory.clear()
    print(f"  清空后: {memory.load_memory_variables({})}")


# ==================== 第三部分：ConversationBufferWindowMemory ====================


def window_memory_demo():
    """ConversationBufferWindowMemory 演示"""
    print("\n" + "=" * 60)
    print("第三部分：WindowMemory（滑动窗口）")
    print("=" * 60)

    from langchain.memory import ConversationBufferWindowMemory

    # 只保留最近 2 轮
    memory = ConversationBufferWindowMemory(k=2, return_messages=True)

    # 添加 3 轮对话
    conversations = [
        ("你好", "你好！"),
        ("今天星期几？", "今天是星期三"),
        ("天气怎么样？", "天气晴朗"),
    ]

    print("📌 添加 3 轮对话（k=2 只保留最近 2 轮）：")
    for user, ai in conversations:
        memory.save_context({"input": user}, {"output": ai})
        print(f"  添加: {user} -> {ai}")

    print("\n📌 实际保留的历史：")
    history = memory.load_memory_variables({})
    for msg in history["history"]:
        role = type(msg).__name__.replace("Message", "")
        print(f"  [{role}] {msg.content}")


# ==================== 第四部分：在链中使用 Memory ====================


def memory_in_chain():
    """在链中使用 Memory"""
    print("\n" + "=" * 60)
    print("第四部分：在链中使用 Memory")
    print("=" * 60)

    try:
        from langchain_openai import ChatOpenAI
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
        llm = ChatOpenAI(model="gpt-3.5-turbo")
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
        使用 BufferMemory 创建能记住用户信息的客服。

    练习 2：测试 WindowMemory
        设置不同的 k 值，观察记忆保留情况。

    练习 3：多会话管理
        使用 session_id 管理多个独立会话。

    思考题：
        1. Buffer vs Window 何时选哪个？
        2. 如何处理超长对话的 token 限制？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 记忆类型详解")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 OPENAI_API_KEY")
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
