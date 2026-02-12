"""
向量数据库概述
==============

学习目标：
    1. 理解向量数据库的作用
    2. 了解主流向量数据库
    3. 掌握向量检索的基本概念

核心概念：
    - 向量存储：保存和检索向量
    - ANN 搜索：近似最近邻搜索
    - 索引类型：HNSW、IVF 等

前置知识：
    - 04-embeddings-basics.py

环境要求：
    - pip install langchain langchain-google-genai python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：向量数据库概念 ====================


def vector_db_concept():
    """向量数据库概念"""
    print("=" * 60)
    print("第一部分：向量数据库概念")
    print("=" * 60)

    print("""
    为什么需要向量数据库？
    ─────────────────────
    
    传统数据库：精确匹配
    SELECT * FROM docs WHERE title = 'AI'
    
    向量数据库：语义相似
    找出与 [0.1, 0.2, ...] 最相似的向量
    
    向量数据库的核心功能：
    ─────────────────────
    
    1. 存储
       - 高维向量（512-4096维）
       - 关联的元数据
    
    2. 索引
       - 构建高效搜索索引
       - 支持快速相似度查询
    
    3. 检索
       - Top-K 相似搜索
       - 过滤条件支持
    
    RAG 中的角色：
    
    ┌─────────┐    ┌──────────────┐    ┌─────────┐
    │  文档   │ ─▶ │  向量数据库   │ ─▶ │  检索   │
    │ Embedding│    │   存储索引    │    │  Top-K  │
    └─────────┘    └──────────────┘    └─────────┘
    """)


# ==================== 第二部分：主流向量数据库 ====================


def vector_db_comparison():
    """主流向量数据库对比"""
    print("\n" + "=" * 60)
    print("第二部分：主流向量数据库")
    print("=" * 60)

    print("""
    向量数据库对比：
    
    | 数据库      | 类型     | 特点                      | 适用场景   |
    |------------|---------|--------------------------|-----------|
    | Chroma     | 嵌入式   | 轻量、易用、Python原生     | 开发测试   |
    | FAISS      | 嵌入式   | Meta出品、性能强           | 离线处理   |
    | Pinecone   | 云服务   | 全托管、易扩展             | 生产环境   |
    | Weaviate   | 自托管   | 功能丰富、支持多模态        | 企业应用   |
    | Milvus     | 自托管   | 高性能、分布式             | 大规模应用 |
    | Qdrant     | 自托管   | 现代化、Rust编写           | 高性能需求 |
    | pgvector   | 扩展     | PostgreSQL扩展            | 已有PG环境 |
    
    选择建议：
    ─────────
    
    🟢 开发测试：Chroma（本地）
    🟡 快速上线：Pinecone（云服务）
    🔴 企业部署：Milvus / Weaviate（自托管）
    """)


# ==================== 第三部分：索引类型 ====================


def index_types():
    """索引类型介绍"""
    print("\n" + "=" * 60)
    print("第三部分：索引类型")
    print("=" * 60)

    print("""
    常见索引算法：
    
    1. Flat（暴力搜索）
       ─────────────────
       - 精确搜索，无索引
       - 适合小数据量
    
    2. IVF（倒排文件索引）
       ──────────────────
       - 将向量分组到聚类中
       - 搜索时只查相关聚类
       - nlist：聚类数量
       - nprobe：搜索的聚类数
    
    3. HNSW（分层可导航小世界图）
       ─────────────────────────
       - 构建多层图结构
       - 效率高，召回率好
       - M：连接数
       - efConstruction：构建参数
    
    4. PQ（乘积量化）
       ────────────────
       - 压缩向量减少内存
       - 适合超大规模
    
    权衡：
    ──────
    精度 ◀────────────────▶ 速度
    内存 ◀────────────────▶ 性能
    """)


# ==================== 第四部分：LangChain VectorStore 接口 ====================


def vectorstore_interface():
    """LangChain VectorStore 接口"""
    print("\n" + "=" * 60)
    print("第四部分：LangChain VectorStore 接口")
    print("=" * 60)

    print("""
    VectorStore 统一接口：
    
    from langchain_core.vectorstores import VectorStore
    
    主要方法：
    ──────────
    
    # 添加文档
    vs.add_documents(documents)
    vs.add_texts(texts, metadatas)
    
    # 相似搜索
    vs.similarity_search(query, k=4)
    vs.similarity_search_with_score(query, k=4)
    
    # 带过滤的搜索
    vs.similarity_search(query, filter={"type": "article"})
    
    # MMR 搜索（最大边际相关性）
    vs.max_marginal_relevance_search(query, k=4)
    
    # 转换为 Retriever
    retriever = vs.as_retriever()
    """)


# ==================== 第五部分：内存向量存储 ====================


def in_memory_store():
    """内存向量存储演示"""
    print("\n" + "=" * 60)
    print("第五部分：内存向量存储")
    print("=" * 60)

    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_core.documents import Document
        from langchain_community.vectorstores import DocArrayInMemorySearch

        # 创建文档
        docs = [
            Document(page_content="Python 是一种编程语言", metadata={"type": "tech"}),
            Document(page_content="机器学习用于预测", metadata={"type": "tech"}),
            Document(page_content="今天天气晴朗", metadata={"type": "other"}),
        ]

        # 创建向量存储
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        vectorstore = DocArrayInMemorySearch.from_documents(docs, embeddings)

        # 搜索
        results = vectorstore.similarity_search("AI 技术", k=2)

        print("📌 搜索结果：")
        for doc in results:
            print(f"  - {doc.page_content} [{doc.metadata}]")

    except Exception as e:
        print(f"❌ 错误: {e}")
        print("  提示: pip install docarray")


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：对比搜索结果
        使用不同 k 值，观察搜索结果变化。

        ✅ 参考答案：
        ```python
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_community.vectorstores import DocArrayInMemorySearch
        from langchain_core.documents import Document

        docs = [
            Document(page_content="Python 编程基础"),
            Document(page_content="机器学习入门"),
            Document(page_content="深度学习实战"),
            Document(page_content="数据科学指南"),
            Document(page_content="Web 开发教程"),
        ]

        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        vectorstore = DocArrayInMemorySearch.from_documents(docs, embeddings)

        query = "AI 学习"
        for k in [1, 2, 3, 5]:
            results = vectorstore.similarity_search(query, k=k)
            print(f"k={k}: {[d.page_content for d in results]}")
        ```

    练习 2：元数据过滤
        添加元数据，测试过滤搜索。

        ✅ 参考答案：
        ```python
        docs = [
            Document(page_content="Python 基础", metadata={"level": "beginner", "year": 2023}),
            Document(page_content="高级 Python", metadata={"level": "advanced", "year": 2024}),
            Document(page_content="ML 入门", metadata={"level": "beginner", "year": 2024}),
        ]

        vectorstore = DocArrayInMemorySearch.from_documents(docs, embeddings)

        # 过滤初学者内容
        results = vectorstore.similarity_search(
            "编程", k=5, filter={"level": "beginner"}
        )
        print(f"初学者内容: {[d.page_content for d in results]}")
        ```

    练习 3：评估召回
        构建测试集，评估检索准确率。

        ✅ 参考答案：
        ```python
        # 构建测试集
        test_cases = [
            {"query": "Python 语言", "expected": "Python 编程基础"},
            {"query": "神经网络", "expected": "深度学习实战"},
            {"query": "数据分析", "expected": "数据科学指南"},
        ]

        # 评估
        correct = 0
        for case in test_cases:
            results = vectorstore.similarity_search(case["query"], k=1)
            if results[0].page_content == case["expected"]:
                correct += 1
        
        accuracy = correct / len(test_cases)
        print(f"准确率: {accuracy:.2%}")
        ```

    思考题：
        1. 如何选择合适的 k 值？
           
           ✅ 答案：
           - 太小 (k=1)：可能错过相关文档
           - 太大 (k=10+)：增加噪声，增加成本
           - 推荐：k=3-5 起步，根据效果调整
           - 考虑 LLM 上下文长度限制

        2. 索引构建后可以更新吗？
           
           ✅ 答案：
           - 大多数向量数据库支持增量更新
           - add_documents() 添加新文档
           - delete() 删除文档
           - 部分数据库需要重建索引才能反映更新
           - Chroma/Pinecone 支持实时更新
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 向量数据库概述")
    print("=" * 60)

    try:
        vector_db_concept()
        vector_db_comparison()
        index_types()
        vectorstore_interface()
        in_memory_store()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：06-chroma-basics.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
