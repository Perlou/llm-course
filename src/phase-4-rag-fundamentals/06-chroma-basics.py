"""
Chroma 向量数据库
=================

学习目标：
    1. 掌握 Chroma 的安装和配置
    2. 学会使用 Chroma 存储和检索
    3. 理解持久化存储

核心概念：
    - Collection：Chroma 中的集合
    - 持久化：数据保存到磁盘
    - 过滤查询：元数据条件过滤

前置知识：
    - 05-vector-stores-intro.py

环境要求：
    - pip install langchain langchain-google-genai chromadb python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Chroma 简介 ====================


def chroma_intro():
    """Chroma 简介"""
    print("=" * 60)
    print("第一部分：Chroma 简介")
    print("=" * 60)

    print("""
    Chroma 特点：
    ────────────
    
    ✅ 开源免费
    ✅ 轻量级、易安装
    ✅ 支持持久化
    ✅ Python 原生
    ✅ 支持元数据过滤
    
    适用场景：
    ─────────
    - 本地开发和测试
    - 中小规模应用
    - 快速原型验证
    
    安装：
    ──────
    pip install chromadb
    """)


# ==================== 第二部分：基础使用 ====================


def basic_usage():
    """基础使用"""
    print("\n" + "=" * 60)
    print("第二部分：基础使用")
    print("=" * 60)

    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.documents import Document

        # 准备文档
        docs = [
            Document(
                page_content="Python 是一种解释型编程语言",
                metadata={"topic": "programming"},
            ),
            Document(page_content="机器学习是人工智能的分支", metadata={"topic": "ai"}),
            Document(page_content="深度学习使用神经网络", metadata={"topic": "ai"}),
            Document(
                page_content="JavaScript 用于 Web 开发",
                metadata={"topic": "programming"},
            ),
        ]

        # 创建 Chroma（内存模式）
        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
        vectorstore = Chroma.from_documents(docs, embeddings)

        # 相似度搜索
        results = vectorstore.similarity_search("AI 技术", k=2)

        print("📌 相似度搜索结果：")
        for doc in results:
            print(f"  - {doc.page_content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第三部分：带分数的搜索 ====================


def search_with_score():
    """带分数的搜索"""
    print("\n" + "=" * 60)
    print("第三部分：带分数的搜索")
    print("=" * 60)

    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.documents import Document

        docs = [
            Document(page_content="自然语言处理让机器理解人类语言"),
            Document(page_content="计算机视觉识别图像内容"),
            Document(page_content="强化学习通过试错优化策略"),
        ]

        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
        vectorstore = Chroma.from_documents(docs, embeddings)

        # 带分数搜索
        results = vectorstore.similarity_search_with_score("文本分析技术", k=3)

        print("📌 带分数的搜索结果：")
        for doc, score in results:
            print(f"  [{score:.4f}] {doc.page_content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：元数据过滤 ====================


def metadata_filtering():
    """元数据过滤"""
    print("\n" + "=" * 60)
    print("第四部分：元数据过滤")
    print("=" * 60)

    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.documents import Document

        docs = [
            Document(
                page_content="Python 数据分析",
                metadata={"category": "tech", "year": 2023},
            ),
            Document(
                page_content="机器学习入门", metadata={"category": "ai", "year": 2023}
            ),
            Document(
                page_content="Python 基础教程",
                metadata={"category": "tech", "year": 2022},
            ),
            Document(
                page_content="深度学习实践", metadata={"category": "ai", "year": 2024}
            ),
        ]

        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
        vectorstore = Chroma.from_documents(docs, embeddings)

        # 过滤搜索
        print("📌 过滤: category=ai")
        results = vectorstore.similarity_search(
            "学习教程", k=2, filter={"category": "ai"}
        )
        for doc in results:
            print(f"  - {doc.page_content} {doc.metadata}")

        print("\n📌 过滤: year >= 2023")
        results = vectorstore.similarity_search(
            "Python", k=2, filter={"year": {"$gte": 2023}}
        )
        for doc in results:
            print(f"  - {doc.page_content} {doc.metadata}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第五部分：持久化存储 ====================


def persistent_storage():
    """持久化存储"""
    print("\n" + "=" * 60)
    print("第五部分：持久化存储")
    print("=" * 60)

    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.documents import Document
        import shutil

        persist_dir = "/tmp/chroma_demo"

        # 创建持久化向量存储
        docs = [
            Document(page_content="持久化测试文档一"),
            Document(page_content="持久化测试文档二"),
        ]

        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

        # 保存
        vectorstore = Chroma.from_documents(
            docs, embeddings, persist_directory=persist_dir
        )

        print(f"📌 已保存到: {persist_dir}")

        # 重新加载
        loaded_store = Chroma(
            persist_directory=persist_dir, embedding_function=embeddings
        )

        results = loaded_store.similarity_search("测试", k=2)
        print(f"📌 重新加载后搜索到: {len(results)} 条结果")

        # 清理
        shutil.rmtree(persist_dir)

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：创建知识库
        加载几篇文章，创建 Chroma 向量库。

        ✅ 参考答案：
        ```python
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.documents import Document

        # 准备文档
        articles = [
            Document(page_content="Python 是最流行的编程语言之一...", 
                    metadata={"title": "Python 入门", "author": "张三"}),
            Document(page_content="机器学习改变了许多行业...", 
                    metadata={"title": "ML 概述", "author": "李四"}),
        ]

        # 创建持久化知识库
        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
        vectorstore = Chroma.from_documents(
            articles,
            embeddings,
            persist_directory="./my_knowledge_base"
        )
        print(f"知识库创建完成，共 {len(articles)} 篇文章")
        ```

    练习 2：复杂过滤
        使用 $and、$or 构建复杂过滤条件。

        ✅ 参考答案：
        ```python
        # $and 过滤：同时满足多个条件
        results = vectorstore.similarity_search(
            "编程",
            k=5,
            filter={"$and": [
                {"category": "tech"},
                {"year": {"$gte": 2023}}
            ]}
        )

        # $or 过滤：满足任一条件
        results = vectorstore.similarity_search(
            "学习",
            k=5,
            filter={"$or": [
                {"level": "beginner"},
                {"level": "intermediate"}
            ]}
        )

        # 组合过滤
        results = vectorstore.similarity_search(
            "AI",
            filter={"$and": [
                {"$or": [{"type": "article"}, {"type": "tutorial"}]},
                {"year": 2024}
            ]}
        )
        ```

    练习 3：增量更新
        向已有集合添加新文档。

        ✅ 参考答案：
        ```python
        # 连接已有数据库
        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
        vectorstore = Chroma(
            persist_directory="./my_knowledge_base",
            embedding_function=embeddings
        )

        # 添加新文档
        new_docs = [
            Document(page_content="新文章内容...", metadata={"title": "新文章"}),
        ]
        vectorstore.add_documents(new_docs)

        # 添加纯文本
        vectorstore.add_texts(
            texts=["另一段文本"],
            metadatas=[{"source": "manual"}]
        )
        ```

    思考题：
        1. 持久化目录结构是怎样的？
           
           ✅ 答案：
           ```
           persist_directory/
           ├── chroma.sqlite3      # 元数据和索引
           └── data_level0/        # 向量数据
               └── *.bin           # 二进制向量文件
           ```

        2. 如何备份和迁移 Chroma 数据？
           
           ✅ 答案：
           - 备份：直接复制 persist_directory 目录
           - 迁移：复制目录到新位置，修改连接路径
           - 导出：遍历 collection 导出为 JSON
           - 跨版本：注意 Chroma 版本兼容性
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 Chroma 向量数据库")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
        return

    try:
        chroma_intro()
        basic_usage()
        search_with_score()
        metadata_filtering()
        persistent_storage()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：07-pinecone-basics.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
