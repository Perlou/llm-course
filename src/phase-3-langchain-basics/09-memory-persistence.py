"""
记忆持久化
==========

学习目标：
    1. 理解记忆持久化的重要性
    2. 掌握文件持久化方案
    3. 了解 Redis 持久化方案

核心概念：
    - 持久化：将记忆保存到外部存储
    - 文件存储：简单的 JSON 文件存储
    - Redis 存储：生产环境推荐方案

前置知识：
    - 08-conversation-memory.py

环境要求：
    - pip install langchain langchain-google-genai python-dotenv
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：为什么需要持久化 ====================


def why_persistence():
    """为什么需要持久化"""
    print("=" * 60)
    print("第一部分：为什么需要持久化")
    print("=" * 60)

    print("""
    内存存储的问题：
    ───────────────
    
    1. 程序重启后数据丢失
    2. 无法在多个实例间共享
    3. 内存容量有限
    
    持久化方案对比：
    ───────────────
    
    | 方案      | 优点          | 缺点           | 适用场景    |
    |----------|--------------|---------------|------------|
    | 文件     | 简单易实现    | 性能低、并发差  | 开发测试    |
    | SQLite   | 轻量级       | 并发支持有限   | 小规模应用  |
    | Redis    | 高性能       | 需要额外部署   | 生产环境    |
    | 数据库   | 持久可靠     | 复杂度高      | 企业应用    |
    """)


# ==================== 第二部分：文件持久化 ====================


def file_persistence():
    """文件持久化"""
    print("\n" + "=" * 60)
    print("第二部分：文件持久化")
    print("=" * 60)

    from langchain_community.chat_message_histories import ChatMessageHistory
    from langchain_core.messages import HumanMessage, AIMessage

    class FileChatHistory:
        """基于文件的聊天历史存储"""

        def __init__(self, file_path: str):
            self.file_path = file_path
            self.history = ChatMessageHistory()
            self._load()

        def _load(self):
            """从文件加载历史"""
            if os.path.exists(self.file_path):
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for msg in data:
                        if msg["type"] == "human":
                            self.history.add_user_message(msg["content"])
                        else:
                            self.history.add_ai_message(msg["content"])

        def _save(self):
            """保存历史到文件"""
            data = []
            for msg in self.history.messages:
                data.append(
                    {
                        "type": "human" if isinstance(msg, HumanMessage) else "ai",
                        "content": msg.content,
                    }
                )
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        def add_exchange(self, user_msg: str, ai_msg: str):
            """添加对话"""
            self.history.add_user_message(user_msg)
            self.history.add_ai_message(ai_msg)
            self._save()

        @property
        def messages(self):
            return self.history.messages

    # 演示
    print("📌 文件持久化演示：")

    test_file = "/tmp/chat_history_demo.json"

    # 创建并添加对话
    chat = FileChatHistory(test_file)
    chat.add_exchange("你好", "你好！有什么可以帮你的？")
    chat.add_exchange("Python怎么学", "建议从基础语法开始")

    print(f"保存到: {test_file}")
    print(f"消息数: {len(chat.messages)}")

    # 重新加载验证
    chat2 = FileChatHistory(test_file)
    print(f"\n重新加载后消息数: {len(chat2.messages)}")
    for msg in chat2.messages:
        role = "用户" if isinstance(msg, HumanMessage) else "AI"
        print(f"  [{role}] {msg.content}")

    # 清理
    os.remove(test_file)


# ==================== 第三部分：Redis 持久化方案 ====================


def redis_persistence():
    """Redis 持久化方案（代码示例）"""
    print("\n" + "=" * 60)
    print("第三部分：Redis 持久化方案")
    print("=" * 60)

    code_example = """
    # Redis 持久化示例（需要安装 redis 包）
    # pip install redis
    
    from langchain_community.chat_message_histories import RedisChatMessageHistory
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.runnables.history import RunnableWithMessageHistory
    from langchain_google_genai import ChatGoogleGenerativeAI

    def get_redis_history(session_id: str):
        return RedisChatMessageHistory(
            session_id=session_id,
            url="redis://localhost:6379"
        )

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个有帮助的助手"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    chain = prompt | llm

    chatbot = RunnableWithMessageHistory(
        chain,
        get_redis_history,
        input_messages_key="input",
        history_messages_key="history"
    )

    # 使用 - 历史会自动保存到 Redis
    response = chatbot.invoke(
        {"input": "你好"},
        config={"configurable": {"session_id": "user123"}}
    )
    """
    print(code_example)

    print("""
    Redis 优势：
    ───────────
    
    1. 高性能：内存存储，毫秒级响应
    2. 持久化：支持 RDB/AOF 持久化
    3. 过期策略：可设置会话自动过期
    4. 集群支持：支持分布式部署
    
    安装 Redis:
    ──────────
    
    # macOS
    brew install redis
    brew services start redis
    
    # Docker
    docker run -d -p 6379:6379 redis
    """)


# ==================== 第四部分：完整持久化聊天机器人 ====================


def persistent_chatbot():
    """完整持久化聊天机器人"""
    print("\n" + "=" * 60)
    print("第四部分：完整持久化聊天机器人")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables.history import RunnableWithMessageHistory
        from langchain_community.chat_message_histories import ChatMessageHistory
        from langchain_core.messages import HumanMessage, AIMessage

        # 简单的文件持久化
        sessions_file = "/tmp/sessions.json"

        def load_sessions():
            if os.path.exists(sessions_file):
                with open(sessions_file, "r") as f:
                    return json.load(f)
            return {}

        def save_sessions(sessions):
            with open(sessions_file, "w") as f:
                json.dump(sessions, f, ensure_ascii=False)

        store = {}

        def get_session(session_id: str):
            if session_id not in store:
                store[session_id] = ChatMessageHistory()
                # 从文件加载
                sessions = load_sessions()
                if session_id in sessions:
                    for msg in sessions[session_id]:
                        if msg["type"] == "human":
                            store[session_id].add_user_message(msg["content"])
                        else:
                            store[session_id].add_ai_message(msg["content"])
            return store[session_id]

        def save_to_file():
            sessions = load_sessions()
            for sid, history in store.items():
                sessions[sid] = [
                    {
                        "type": "human" if isinstance(m, HumanMessage) else "ai",
                        "content": m.content,
                    }
                    for m in history.messages
                ]
            save_sessions(sessions)

        # 创建聊天机器人
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一个友好的助手"),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )

        chatbot = RunnableWithMessageHistory(
            prompt | llm | StrOutputParser(),
            get_session,
            input_messages_key="input",
            history_messages_key="history",
        )

        print("📌 持久化聊天演示：")

        response = chatbot.invoke(
            {"input": "你好，我是测试用户"},
            config={"configurable": {"session_id": "persistent_test"}},
        )
        print(f"AI: {response}")

        # 保存
        save_to_file()
        print(f"\n✅ 会话已保存到 {sessions_file}")

        # 清理
        os.remove(sessions_file)

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第五部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：SQLite 持久化
        使用 SQLite 实现会话存储。

    练习 2：会话过期
        实现会话超时自动清理功能。

    练习 3：会话导出
        实现将会话导出为 Markdown 格式。

    思考题：
        1. 如何设计会话数据的备份策略？
        2. 如何处理敏感对话数据的安全存储？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 记忆持久化")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
        return

    try:
        why_persistence()
        file_persistence()
        redis_persistence()
        persistent_chatbot()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：10-output-parsers.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
