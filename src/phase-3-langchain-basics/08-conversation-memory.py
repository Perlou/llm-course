"""
会话记忆实现
============

学习目标：
    1. 深入理解 RunnableWithMessageHistory
    2. 掌握多会话管理
    3. 构建完整的聊天机器人

核心概念：
    - ChatMessageHistory：消息历史存储
    - RunnableWithMessageHistory：链的历史包装器
    - 会话隔离：基于 session_id 隔离

前置知识：
    - 07-memory-types.py

环境要求：
    - pip install langchain langchain-google-genai python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：ChatMessageHistory ====================


def chat_message_history():
    """ChatMessageHistory 基础"""
    print("=" * 60)
    print("第一部分：ChatMessageHistory")
    print("=" * 60)

    from langchain_community.chat_message_histories import ChatMessageHistory
    from langchain_core.messages import HumanMessage, AIMessage

    # 创建历史
    history = ChatMessageHistory()

    # 添加消息
    history.add_user_message("你好")
    history.add_ai_message("你好！有什么可以帮你的？")
    history.add_message(HumanMessage(content="我想学 Python"))
    history.add_message(AIMessage(content="好的，Python 是很好的选择！"))

    print("📌 消息历史：")
    for msg in history.messages:
        role = "用户" if isinstance(msg, HumanMessage) else "AI"
        print(f"  [{role}] {msg.content}")

    # 清空
    history.clear()
    print(f"\n📌 清空后消息数: {len(history.messages)}")


# ==================== 第二部分：多会话管理 ====================


def multi_session():
    """多会话管理"""
    print("\n" + "=" * 60)
    print("第二部分：多会话管理")
    print("=" * 60)

    from langchain_community.chat_message_histories import ChatMessageHistory

    # 会话存储
    sessions = {}

    def get_history(session_id: str) -> ChatMessageHistory:
        if session_id not in sessions:
            sessions[session_id] = ChatMessageHistory()
        return sessions[session_id]

    # 模拟两个用户
    print("📌 模拟两个用户对话：")

    # 用户 A
    history_a = get_history("user_a")
    history_a.add_user_message("我是张三")
    history_a.add_ai_message("你好张三！")

    # 用户 B
    history_b = get_history("user_b")
    history_b.add_user_message("我是李四")
    history_b.add_ai_message("你好李四！")

    print("\n用户 A 的历史：")
    for msg in get_history("user_a").messages:
        print(f"  {msg.content}")

    print("\n用户 B 的历史：")
    for msg in get_history("user_b").messages:
        print(f"  {msg.content}")


# ==================== 第三部分：完整聊天机器人 ====================


def chatbot_demo():
    """完整聊天机器人"""
    print("\n" + "=" * 60)
    print("第三部分：完整聊天机器人")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables.history import RunnableWithMessageHistory
        from langchain_community.chat_message_histories import ChatMessageHistory

        # 会话存储
        store = {}

        def get_session(session_id: str):
            if session_id not in store:
                store[session_id] = ChatMessageHistory()
            return store[session_id]

        # 构建聊天机器人
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "你是小智，一个友好幽默的AI助手。记住用户告诉你的信息。"),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )

        chain = prompt | llm | StrOutputParser()

        chatbot = RunnableWithMessageHistory(
            chain,
            get_session,
            input_messages_key="input",
            history_messages_key="history",
        )

        # 对话函数
        def chat(message: str, session_id: str = "default"):
            return chatbot.invoke(
                {"input": message}, config={"configurable": {"session_id": session_id}}
            )

        print("📌 对话测试：")

        conversations = [
            "你好，我叫王五，今年25岁",
            "我是一名程序员，喜欢用Python",
            "你还记得我的名字和年龄吗？",
        ]

        for msg in conversations:
            print(f"\n用户: {msg}")
            response = chat(msg, "test_user")
            print(f"小智: {response}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：交互式聊天 ====================


def interactive_chat():
    """交互式聊天演示"""
    print("\n" + "=" * 60)
    print("第四部分：交互式聊天（代码示例）")
    print("=" * 60)

    code_example = """
    # 完整的交互式聊天机器人代码
    
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables.history import RunnableWithMessageHistory
    from langchain_community.chat_message_histories import ChatMessageHistory

    store = {}

    def get_session(session_id):
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个有帮助的助手"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    chatbot = RunnableWithMessageHistory(
        prompt | llm | StrOutputParser(),
        get_session,
        input_messages_key="input",
        history_messages_key="history"
    )

    # 交互循环
    session_id = "user_001"
    print("聊天机器人已启动，输入 'quit' 退出")
    
    while True:
        user_input = input("你: ")
        if user_input.lower() == 'quit':
            break
        response = chatbot.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )
        print(f"AI: {response}")
    """
    print(code_example)


# ==================== 第五部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：个性化助手
        创建能记住用户偏好的个性化助手。

        ✅ 参考答案：
        ```python
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.runnables.history import RunnableWithMessageHistory
        from langchain_community.chat_message_histories import ChatMessageHistory

        store = {}
        user_preferences = {}  # 存储用户偏好

        def get_session(session_id):
            if session_id not in store:
                store[session_id] = ChatMessageHistory()
            return store[session_id]

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        
        # 动态构建系统提示词
        def build_prompt(user_id):
            prefs = user_preferences.get(user_id, {})
            pref_str = ", ".join([f"{k}:{v}" for k,v in prefs.items()])
            return ChatPromptTemplate.from_messages([
                ("system", f"你是个性化助手。用户偏好: {pref_str}"),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}")
            ])

        # 保存偏好
        def save_preference(user_id, key, value):
            if user_id not in user_preferences:
                user_preferences[user_id] = {}
            user_preferences[user_id][key] = value
        ```

    练习 2：多角色助手
        根据用户需求切换不同角色（技术/生活/学习）。

        ✅ 参考答案：
        ```python
        role_prompts = {
            "技术": "你是技术专家，擅长编程和系统设计",
            "生活": "你是生活顾问，擅长健康、烹饪和家居",
            "学习": "你是学习导师，擅长教学和学习方法"
        }

        def detect_role(message: str) -> str:
            tech_keywords = ["代码", "编程", "bug", "API"]
            life_keywords = ["健康", "做饭", "运动", "睡眠"]
            study_keywords = ["学习", "考试", "复习", "课程"]
            
            if any(k in message for k in tech_keywords):
                return "技术"
            elif any(k in message for k in life_keywords):
                return "生活"
            elif any(k in message for k in study_keywords):
                return "学习"
            return "技术"  # 默认

        def get_role_prompt(role: str) -> str:
            return role_prompts.get(role, role_prompts["技术"])
        ```

    练习 3：对话导出
        实现导出对话历史为文本文件的功能。

        ✅ 参考答案：
        ```python
        from langchain_core.messages import HumanMessage, AIMessage
        from datetime import datetime

        def export_conversation(session_id: str, filename: str = None):
            history = get_session(session_id)
            
            if filename is None:
                filename = f"conversation_{session_id}_{datetime.now().strftime('%Y%m%d')}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"对话记录 - {session_id}\\n")
                f.write(f"导出时间: {datetime.now()}\\n")
                f.write("=" * 50 + "\\n\\n")
                
                for msg in history.messages:
                    role = "用户" if isinstance(msg, HumanMessage) else "AI"
                    f.write(f"[{role}]\\n{msg.content}\\n\\n")
            
            return filename

        # 导出为 Markdown
        def export_to_markdown(session_id: str):
            history = get_session(session_id)
            md_content = f"# 对话记录 - {session_id}\\n\\n"
            
            for msg in history.messages:
                if isinstance(msg, HumanMessage):
                    md_content += f"**用户**: {msg.content}\\n\\n"
                else:
                    md_content += f"**AI**: {msg.content}\\n\\n"
            
            return md_content
        ```

    思考题：
        1. 如何处理会话超时？
           
           ✅ 答案：
           - 记录最后活跃时间，定期清理过期会话
           - 使用 TTL（Time To Live）机制
           - Redis 自带过期功能：`RedisChatMessageHistory(..., ttl=3600)`
           - 给用户提示"会话已过期，请重新开始"

        2. 如何实现会话持久化到数据库？
           
           ✅ 答案：
           - 使用 SQLAlchemy 存储到 PostgreSQL/MySQL
           - 使用 MongoDB 存储 JSON 格式消息
           - 使用 Redis 快速读写 + MySQL 长期存储
           - LangChain 提供 SQLChatMessageHistory 组件
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 会话记忆实现")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
        return

    try:
        chat_message_history()
        multi_session()
        chatbot_demo()
        interactive_chat()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：09-memory-persistence.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
