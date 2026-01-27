"""
LLM 模型封装
============

学习目标：
    1. 理解 LangChain 中的模型类型
    2. 掌握 ChatOpenAI 的配置和使用
    3. 了解 Embeddings 模型的使用

核心概念：
    - Chat Models：基于消息的对话模型
    - Embeddings：文本向量化模型

前置知识：
    - 01-langchain-intro.py

环境要求：
    - pip install langchain langchain-openai python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：模型类型概述 ====================


def model_types_overview():
    """模型类型概述"""
    print("=" * 60)
    print("第一部分：模型类型概述")
    print("=" * 60)

    print("""
    LangChain 中的模型类型：
    
    | 类型        | 输入           | 输出        | 典型模型          |
    |------------|---------------|------------|------------------|
    | Chat Models| 消息列表       | AI消息对象   | gpt-4, gpt-3.5   |
    | Embeddings | 文本           | 向量        | text-embedding-3 |
    
    💡 Chat Models 最常用，是开发的首选。
    """)


# ==================== 第二部分：Chat Models 详解 ====================


def chat_models_demo():
    """Chat Models 详解"""
    print("\n" + "=" * 60)
    print("第二部分：Chat Models 详解")
    print("=" * 60)

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage

        # 创建模型
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        print(f"\n✅ 模型已创建: {llm.model_name}")

        # 简单调用
        print("\n📌 简单调用：")
        response = llm.invoke("用一句话解释什么是 LangChain")
        print(f"回复: {response.content}")

        # 使用消息列表
        print("\n📌 使用消息列表：")
        messages = [
            SystemMessage(content="你是 Python 专家"),
            HumanMessage(content="列表推导式是什么？"),
        ]
        response = llm.invoke(messages)
        print(f"回复: {response.content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第三部分：模型配置 ====================


def model_configuration():
    """模型配置"""
    print("\n" + "=" * 60)
    print("第三部分：模型配置")
    print("=" * 60)

    print("""
    关键参数：
    - temperature (0-2): 0=确定性, 1+=创造性
    - max_tokens: 最大输出长度
    - timeout: 超时时间
    - max_retries: 最大重试次数
    """)

    try:
        from langchain_openai import ChatOpenAI

        # 对比不同温度
        print("\n📌 温度对比：")
        prompt = "用一句话描述月亮"

        llm_low = ChatOpenAI(temperature=0)
        llm_high = ChatOpenAI(temperature=1.2)

        print(f"temperature=0: {llm_low.invoke(prompt).content}")
        print(f"temperature=1.2: {llm_high.invoke(prompt).content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：Embeddings 模型 ====================


def embeddings_demo():
    """Embeddings 模型演示"""
    print("\n" + "=" * 60)
    print("第四部分：Embeddings 模型")
    print("=" * 60)

    print("""
    Embeddings 将文本转换为向量，用于：
    - 语义搜索
    - 文档相似度
    - RAG 应用
    """)

    try:
        from langchain_openai import OpenAIEmbeddings
        import numpy as np

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        # 单个文本嵌入
        text = "LangChain 是一个强大的框架"
        vector = embeddings.embed_query(text)
        print(f"\n文本: {text}")
        print(f"向量维度: {len(vector)}")

        # 相似度计算
        texts = ["Python 编程", "Java 编程", "烹饪技巧"]
        vectors = embeddings.embed_documents(texts)

        def cosine_sim(v1, v2):
            v1, v2 = np.array(v1), np.array(v2)
            return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

        print(
            f"\n相似度: '{texts[0]}' vs '{texts[1]}': {cosine_sim(vectors[0], vectors[1]):.4f}"
        )
        print(
            f"相似度: '{texts[0]}' vs '{texts[2]}': {cosine_sim(vectors[0], vectors[2]):.4f}"
        )

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第五部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：创建代码生成模型
        使用低温度和大 max_tokens 创建适合代码生成的模型。

    练习 2：多轮对话
        使用消息列表实现连续的多轮对话。

    练习 3：文本相似度搜索
        使用 Embeddings 找出最相似的文档。

    思考题：
        1. 什么时候使用低温度 vs 高温度？
        2. Embeddings 有什么实际应用？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 LLM 模型封装")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 OPENAI_API_KEY")
        return

    print(f"✅ API Key 已配置: {api_key[:8]}...{api_key[-4:]}")

    try:
        model_types_overview()
        chat_models_demo()
        model_configuration()
        embeddings_demo()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：03-prompt-templates.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
