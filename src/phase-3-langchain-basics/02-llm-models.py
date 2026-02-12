"""
LLM 模型封装 - Gemini 版本
==========================

学习目标：
    1. 理解 LangChain 中的模型类型
    2. 掌握 ChatGoogleGenerativeAI 的配置和使用
    3. 了解 Embeddings 模型的使用

核心概念：
    - Chat Models：基于消息的对话模型
    - Embeddings：文本向量化模型

前置知识：
    - 01-langchain-intro.py

环境要求：
    - pip install langchain langchain-google-genai python-dotenv
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
    | Chat Models| 消息列表       | AI消息对象   | gemini-2.0-flash |
    | Embeddings | 文本           | 向量        | gemini-embedding-001    |
    
    💡 Chat Models 最常用，是开发的首选。
    """)


# ==================== 第二部分：Chat Models 详解 ====================


def chat_models_demo():
    """Chat Models 详解"""
    print("\n" + "=" * 60)
    print("第二部分：Chat Models 详解")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage, SystemMessage

        # 创建模型
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
        print(f"\n✅ 模型已创建: gemini-2.0-flash")

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
    - max_output_tokens: 最大输出长度
    - timeout: 超时时间
    - max_retries: 最大重试次数
    """)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        # 对比不同温度
        print("\n📌 温度对比：")
        prompt = "用一句话描述月亮"

        llm_low = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
        llm_high = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=1.2)

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
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        import numpy as np

        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

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
        使用低温度和大 max_output_tokens 创建适合代码生成的模型。

        ✅ 参考答案：
        ```python
        from langchain_google_genai import ChatGoogleGenerativeAI

        # 代码生成模型配置
        code_llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.2,          # 低温度保证一致性
            max_output_tokens=2048,   # 足够长的代码输出
            timeout=60,               # 较长超时
        )

        # 使用
        response = code_llm.invoke("写一个 Python 快速排序函数")
        print(response.content)
        ```

    练习 2：多轮对话
        使用消息列表实现连续的多轮对话。

        ✅ 参考答案：
        ```python
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

        # 多轮对话消息
        messages = [
            SystemMessage(content="你是一个友好的助手"),
            HumanMessage(content="你好，我叫小明"),
            AIMessage(content="你好小明！很高兴认识你！"),
            HumanMessage(content="我之前告诉过你我的名字，你还记得吗？"),
        ]

        response = llm.invoke(messages)
        print(response.content)  # 会回答 "小明"
        ```

    练习 3：文本相似度搜索
        使用 Embeddings 找出最相似的文档。

        ✅ 参考答案：
        ```python
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        import numpy as np

        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

        def cosine_similarity(v1, v2):
            v1, v2 = np.array(v1), np.array(v2)
            return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

        # 文档库
        documents = [
            "Python 是一种编程语言",
            "机器学习需要大量数据",
            "今天天气晴朗",
            "深度学习是机器学习的一个分支"
        ]

        # 查询
        query = "什么是人工智能"

        # 向量化
        query_vec = embeddings.embed_query(query)
        doc_vecs = embeddings.embed_documents(documents)

        # 找最相似
        similarities = [cosine_similarity(query_vec, dv) for dv in doc_vecs]
        most_similar_idx = np.argmax(similarities)
        print(f"最相似文档: {documents[most_similar_idx]}")
        ```

    思考题：
        1. 什么时候使用低温度 vs 高温度？
           
           ✅ 答案：
           - 低温度 (0-0.3)：代码生成、事实问答、数据提取
           - 中等温度 (0.5-0.7)：通用对话、文档总结
           - 高温度 (0.8-1.2)：创意写作、头脑风暴、故事生成
           - 关键原则：需要确定性用低温度，需要创意用高温度

        2. Embeddings 有什么实际应用？
           
           ✅ 答案：
           - 语义搜索：找到意思相近的文档
           - RAG 应用：检索相关上下文
           - 文档聚类：将相似文档分组
           - 推荐系统：基于相似度推荐
           - 异常检测：找出与众不同的文本
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 LLM 模型封装 - Gemini 版本")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
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
