"""
Pinecone 向量数据库
==================

学习目标：
    1. 了解 Pinecone 云服务
    2. 掌握 Pinecone 基本操作
    3. 理解与本地方案的差异

核心概念：
    - 云托管：无需自己维护基础设施
    - Index：Pinecone 中的索引
    - Namespace：索引内的命名空间

前置知识：
    - 06-chroma-basics.py

环境要求：
    - pip install langchain langchain-google-genai pinecone-client python-dotenv
    - 需要 Pinecone API Key
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Pinecone 简介 ====================


def pinecone_intro():
    """Pinecone 简介"""
    print("=" * 60)
    print("第一部分：Pinecone 简介")
    print("=" * 60)

    print("""
    Pinecone 特点：
    ───────────────
    
    ✅ 全托管云服务
    ✅ 自动扩展
    ✅ 低延迟查询
    ✅ 支持元数据过滤
    ✅ 免费层可用
    
    适用场景：
    ─────────
    - 生产环境部署
    - 需要高可用
    - 不想维护基础设施
    
    vs Chroma：
    ──────────
    
    | 特性     | Pinecone | Chroma  |
    |---------|----------|---------|
    | 部署方式 | 云服务    | 本地/嵌入 |
    | 扩展性   | 自动扩展  | 手动     |
    | 成本     | 付费      | 免费     |
    | 延迟     | 网络延迟  | 本地快   |
    """)


# ==================== 第二部分：配置和连接 ====================


def pinecone_setup():
    """Pinecone 配置"""
    print("\n" + "=" * 60)
    print("第二部分：配置和连接")
    print("=" * 60)

    print("""
    1. 注册账号
       访问 https://www.pinecone.io/ 注册
    
    2. 获取 API Key
       在控制台获取 API Key 和 Environment
    
    3. 配置环境变量
       export PINECONE_API_KEY="your-api-key"
       export PINECONE_ENVIRONMENT="your-environment"
    
    4. 安装依赖
       pip install pinecone-client
    """)

    code_example = """
    from pinecone import Pinecone
    
    # 初始化
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    
    # 创建索引
    pc.create_index(
        name="my-index",
        dimension=1536,  # OpenAI ada-002 维度
        metric="cosine"
    )
    
    # 连接索引
    index = pc.Index("my-index")
    """
    print("📌 连接代码示例：")
    print(code_example)


# ==================== 第三部分：LangChain 集成 ====================


def langchain_integration():
    """LangChain 集成"""
    print("\n" + "=" * 60)
    print("第三部分：LangChain 集成")
    print("=" * 60)

    code_example = """
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_pinecone import PineconeVectorStore
    from langchain_core.documents import Document
    
    # 准备文档
    docs = [
        Document(page_content="AI 技术发展迅速"),
        Document(page_content="机器学习应用广泛"),
    ]
    
    # 创建向量存储
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    vectorstore = PineconeVectorStore.from_documents(
        docs,
        embeddings,
        index_name="my-index",
        namespace="default"  # 可选：使用命名空间隔离数据
    )
    
    # 搜索
    results = vectorstore.similarity_search("AI", k=2)
    
    # 连接已有索引
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name="my-index",
        embedding=embeddings
    )
    """

    print("📌 LangChain 集成代码：")
    print(code_example)


# ==================== 第四部分：命名空间 ====================


def namespaces():
    """命名空间使用"""
    print("\n" + "=" * 60)
    print("第四部分：命名空间")
    print("=" * 60)

    print("""
    命名空间的作用：
    ───────────────
    
    在同一个索引内隔离不同类别的数据
    
    ┌─────────────────────────────────────────────┐
    │              Index: my-index                │
    ├─────────────────────────────────────────────┤
    │  ┌─────────────┐  ┌─────────────────────┐   │
    │  │ Namespace:  │  │    Namespace:       │   │
    │  │ "user-123"  │  │    "user-456"       │   │
    │  │ (用户A的数据)│  │    (用户B的数据)     │   │
    │  └─────────────┘  └─────────────────────┘   │
    └─────────────────────────────────────────────┘
    
    使用场景：
    - 多租户隔离
    - 不同类别数据分开存储
    - 方便独立删除某类数据
    """)


# ==================== 第五部分：最佳实践 ====================


def best_practices():
    """最佳实践"""
    print("\n" + "=" * 60)
    print("第五部分：最佳实践")
    print("=" * 60)

    print("""
    Pinecone 使用建议：
    ──────────────────
    
    1. 索引设计
       - 选择合适的 dimension（与 Embedding 模型匹配）
       - 选择合适的 metric（cosine、euclidean、dotproduct）
    
    2. 批量操作
       - 使用 batch 方式 upsert
       - 避免单条插入
    
    3. 元数据
       - 只存储必要的元数据
       - 元数据大小有限制
    
    4. 命名空间
       - 合理使用 namespace 隔离数据
       - 便于管理和删除
    
    5. 成本控制
       - 监控查询数量
       - 及时清理不需要的数据
    """)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：注册 Pinecone
        注册免费账号，创建一个测试索引。

        ✅ 参考答案：
        ```python
        from pinecone import Pinecone, ServerlessSpec

        # 初始化
        pc = Pinecone(api_key="your-api-key")

        # 创建 Serverless 索引（免费层）
        pc.create_index(
            name="my-test-index",
            dimension=768,  # Gemini embedding 维度
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

        # 连接索引
        index = pc.Index("my-test-index")
        print(index.describe_index_stats())
        ```

    练习 2：数据迁移
        将 Chroma 中的数据迁移到 Pinecone。

        ✅ 参考答案：
        ```python
        from langchain_chroma import Chroma
        from langchain_pinecone import PineconeVectorStore

        # 从 Chroma 读取
        chroma_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
        
        # 获取所有文档
        all_docs = chroma_store.get()
        
        # 如果需要完整 Document 对象
        from langchain_core.documents import Document
        docs = [
            Document(page_content=content, metadata=meta)
            for content, meta in zip(all_docs['documents'], all_docs['metadatas'])
        ]

        # 写入 Pinecone
        pinecone_store = PineconeVectorStore.from_documents(
            docs,
            embeddings,
            index_name="my-index"
        )
        ```

    练习 3：性能对比
        对比 Chroma 和 Pinecone 的查询延迟。

        ✅ 参考答案：
        ```python
        import time

        def benchmark(vectorstore, query, iterations=10):
            times = []
            for _ in range(iterations):
                start = time.time()
                vectorstore.similarity_search(query, k=5)
                times.append(time.time() - start)
            return sum(times) / len(times)

        chroma_latency = benchmark(chroma_store, "AI 技术")
        pinecone_latency = benchmark(pinecone_store, "AI 技术")

        print(f"Chroma 平均延迟: {chroma_latency*1000:.2f}ms")
        print(f"Pinecone 平均延迟: {pinecone_latency*1000:.2f}ms")
        # Chroma 本地通常更快，Pinecone 有网络延迟
        ```

    思考题：
        1. 什么情况下选择 Pinecone？
           
           ✅ 答案：
           - 生产环境需要高可用
           - 数据量大需要自动扩展
           - 团队没有运维向量数据库的能力
           - 需要全球分布式部署
           - 预算允许付费服务

        2. 如何处理 Pinecone 服务中断？
           
           ✅ 答案：
           - 实现重试机制和指数退避
           - 本地缓存热门查询结果
           - 准备 Fallback 方案（如本地 Chroma）
           - 监控报警及时发现问题
           - 使用多区域部署提高可用性
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 Pinecone 向量数据库")
    print("=" * 60)
    print("⚠️ 注意：本课程需要 Pinecone API Key")
    print("=" * 60)

    try:
        pinecone_intro()
        pinecone_setup()
        langchain_integration()
        namespaces()
        best_practices()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：08-retrieval-basics.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
