"""
基础检索
========

学习目标：
    1. 理解 Retriever 的概念
    2. 掌握不同检索策略
    3. 学会配置检索参数

核心概念：
    - Retriever：检索器接口
    - MMR：最大边际相关性
    - 自查询：基于元数据的检索

前置知识：
    - 06-chroma-basics.py

环境要求：
    - pip install langchain langchain-google-genai chromadb python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Retriever 概念 ====================


def retriever_concept():
    """Retriever 概念"""
    print("=" * 60)
    print("第一部分：Retriever 概念")
    print("=" * 60)

    print("""
    Retriever 是什么？
    ─────────────────
    
    Retriever 是一个检索接口，从数据源中获取相关文档。
    
    ┌──────────────────────────────────────────────────┐
    │                                                  │
    │  Query ─▶ Retriever ─▶ [Doc1, Doc2, Doc3, ...]  │
    │                                                  │
    └──────────────────────────────────────────────────┘
    
    常见 Retriever 类型：
    ────────────────────
    
    1. VectorStoreRetriever - 基于向量的检索
    2. BM25Retriever - 基于关键词的检索
    3. MultiQueryRetriever - 多查询检索
    4. SelfQueryRetriever - 自查询检索
    5. EnsembleRetriever - 混合检索
    """)


# ==================== 第二部分：VectorStore Retriever ====================


def vectorstore_retriever():
    """VectorStore Retriever"""
    print("\n" + "=" * 60)
    print("第二部分：VectorStore Retriever")
    print("=" * 60)

    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.documents import Document

        # 准备数据
        docs = [
            Document(page_content="Python 是一种编程语言，广泛用于数据科学"),
            Document(page_content="机器学习是人工智能的重要分支"),
            Document(page_content="深度学习使用多层神经网络"),
            Document(page_content="JavaScript 是 Web 开发的核心语言"),
        ]

        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vectorstore = Chroma.from_documents(docs, embeddings)

        # 创建 Retriever
        retriever = vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 2}
        )

        # 检索
        query = "AI 技术"
        results = retriever.invoke(query)

        print(f"📌 查询: '{query}'")
        print(f"检索到 {len(results)} 条结果：")
        for doc in results:
            print(f"  - {doc.page_content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第三部分：MMR 检索 ====================


def mmr_retrieval():
    """MMR 检索（最大边际相关性）"""
    print("\n" + "=" * 60)
    print("第三部分：MMR 检索")
    print("=" * 60)

    print("""
    MMR (Maximal Marginal Relevance)：
    ──────────────────────────────────
    
    在相关性的基础上，增加结果的多样性。
    
    普通相似搜索：可能返回很多相似的结果
    MMR 搜索：平衡相关性和多样性
    
    参数：
    - fetch_k: 初始获取数量
    - lambda_mult: 多样性权重 (0-1, 越小越多样)
    """)

    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.documents import Document

        docs = [
            Document(page_content="Python 是一种编程语言"),
            Document(page_content="Python 用于数据分析"),
            Document(page_content="Python 语法简洁"),
            Document(page_content="机器学习使用 Python"),
            Document(page_content="JavaScript 用于前端开发"),
        ]

        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vectorstore = Chroma.from_documents(docs, embeddings)

        # MMR 检索
        retriever = vectorstore.as_retriever(
            search_type="mmr", search_kwargs={"k": 3, "fetch_k": 5, "lambda_mult": 0.5}
        )

        results = retriever.invoke("Python")

        print("📌 MMR 检索结果（更多样化）：")
        for doc in results:
            print(f"  - {doc.page_content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：相似度阈值 ====================


def similarity_threshold():
    """相似度阈值过滤"""
    print("\n" + "=" * 60)
    print("第四部分：相似度阈值")
    print("=" * 60)

    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.documents import Document

        docs = [
            Document(page_content="人工智能改变世界"),
            Document(page_content="机器学习是 AI 分支"),
            Document(page_content="今天天气晴朗"),
        ]

        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vectorstore = Chroma.from_documents(docs, embeddings)

        # 带阈值的检索
        retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": 0.7},
        )

        print("📌 高阈值过滤（只返回高相关度）：")
        results = retriever.invoke("AI 技术")
        for doc in results:
            print(f"  - {doc.page_content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第五部分：多查询检索 ====================


def multi_query_retriever():
    """多查询检索"""
    print("\n" + "=" * 60)
    print("第五部分：多查询检索")
    print("=" * 60)

    print("""
    MultiQueryRetriever：
    ────────────────────
    
    使用 LLM 生成多个查询变体，增加召回率。
    
    原始查询: "AI 有什么应用?"
    
    生成变体:
    - "人工智能的应用场景有哪些?"
    - "AI 技术在哪些领域使用?"
    - "机器学习的实际用途?"
    
    合并所有查询的结果，去重后返回。
    """)

    code_example = """
    from langchain.retrievers.multi_query import MultiQueryRetriever
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    
    retriever = MultiQueryRetriever.from_llm(
        retriever=vectorstore.as_retriever(),
        llm=llm
    )
    
    # 会自动生成多个查询并合并结果
    docs = retriever.invoke("AI 有什么应用?")
    """
    print("📌 代码示例：")
    print(code_example)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：对比检索策略
        对比 similarity、mmr、threshold 的结果差异。

    练习 2：调优参数
        测试不同 k、lambda_mult 值的效果。

    练习 3：实现重排序
        检索后使用 LLM 对结果重新排序。

    思考题：
        1. 何时使用 MMR？
        2. 阈值设置过高或过低有什么问题？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 基础检索")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
        return

    try:
        retriever_concept()
        vectorstore_retriever()
        mmr_retrieval()
        similarity_threshold()
        multi_query_retriever()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：09-qa-chains.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
