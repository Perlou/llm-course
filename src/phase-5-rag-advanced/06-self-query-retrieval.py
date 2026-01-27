"""
自查询检索
==========

学习目标：
    1. 理解自查询检索的原理
    2. 掌握 LangChain SelfQueryRetriever
    3. 学会结构化元数据过滤

核心概念：
    - Self-Query：LLM 自动解析查询意图
    - 元数据过滤：基于属性的精确筛选
    - 结构化查询：语义 + 过滤

前置知识：
    - 05-multi-query-retrieval.py

环境要求：
    - pip install langchain langchain-openai chromadb lark python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：自查询检索概念 ====================


def self_query_concept():
    """自查询检索概念"""
    print("=" * 60)
    print("第一部分：自查询检索概念")
    print("=" * 60)

    print("""
    自查询检索的优势：
    ──────────────────
    
    传统检索只能做语义匹配
    但用户的查询往往包含过滤条件
    
    示例查询：
    ─────────
    「找一篇 2023 年发布的关于 RAG 的论文」
    
    传统检索：只能语义匹配 "RAG"
    自查询：同时过滤 年份=2023 AND 类型=论文
    
    ┌─────────────────────────────────────────────────────┐
    │  用户查询: "2023年关于RAG的论文"                     │
    │                     │                               │
    │                     ▼                               │
    │          ┌───────────────────┐                     │
    │          │   LLM 意图解析     │                     │
    │          └───────────────────┘                     │
    │                     │                               │
    │         ┌───────────┴───────────┐                  │
    │         ▼                       ▼                   │
    │  ┌─────────────┐        ┌─────────────┐           │
    │  │  语义查询    │        │  元数据过滤  │           │
    │  │  "RAG"      │        │  year=2023  │           │
    │  │             │        │  type=paper │           │
    │  └──────┬──────┘        └──────┬──────┘           │
    │         │                      │                   │
    │         └──────────┬───────────┘                   │
    │                    ▼                               │
    │            ┌──────────────┐                        │
    │            │ 联合检索      │                        │
    │            │ 向量 + 过滤   │                        │
    │            └──────────────┘                        │
    │                                                     │
    └─────────────────────────────────────────────────────┘
    """)


# ==================== 第二部分：元数据设计 ====================


def metadata_design():
    """元数据设计"""
    print("\n" + "=" * 60)
    print("第二部分：元数据设计")
    print("=" * 60)

    print("""
    常见的元数据字段：
    ──────────────────
    
    文档类型元数据：
    - source: 来源 (blog, paper, doc)
    - type: 类型 (tutorial, reference, news)
    - author: 作者
    - date/year: 发布日期
    
    内容相关元数据：
    - topic: 主题标签
    - language: 语言
    - difficulty: 难度级别
    - rating: 评分
    
    技术元数据：
    - word_count: 字数
    - page_number: 页码
    - chunk_id: 分块ID
    """)

    from langchain_core.documents import Document

    # 示例：带元数据的文档
    docs = [
        Document(
            page_content="RAG 技术综述：检索增强生成的原理与应用",
            metadata={
                "source": "paper",
                "year": 2023,
                "topic": "RAG",
                "language": "zh",
            },
        ),
        Document(
            page_content="LangChain 入门教程：构建你的第一个 AI 应用",
            metadata={
                "source": "tutorial",
                "year": 2024,
                "topic": "LangChain",
                "difficulty": "beginner",
            },
        ),
    ]

    print("📌 示例文档：")
    for doc in docs:
        print(f"  内容: {doc.page_content[:30]}...")
        print(f"  元数据: {doc.metadata}")
        print()


# ==================== 第三部分：LangChain SelfQueryRetriever ====================


def langchain_self_query():
    """LangChain SelfQueryRetriever"""
    print("\n" + "=" * 60)
    print("第三部分：LangChain SelfQueryRetriever")
    print("=" * 60)

    try:
        from langchain.chains.query_constructor.base import AttributeInfo
        from langchain.retrievers.self_query.base import SelfQueryRetriever
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.documents import Document

        # 准备带元数据的文档
        docs = [
            Document(
                page_content="RAG (Retrieval-Augmented Generation) 是一种结合检索和生成的技术",
                metadata={"source": "paper", "year": 2023, "topic": "RAG"},
            ),
            Document(
                page_content="向量数据库用于高效存储和检索向量",
                metadata={"source": "tutorial", "year": 2024, "topic": "vector_db"},
            ),
            Document(
                page_content="LangChain 是构建 LLM 应用的框架",
                metadata={"source": "doc", "year": 2023, "topic": "LangChain"},
            ),
            Document(
                page_content="GPT-4 的多模态能力使其可以处理图像",
                metadata={"source": "news", "year": 2024, "topic": "LLM"},
            ),
        ]

        # 创建向量存储
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(docs, embeddings)

        # 定义元数据属性
        metadata_field_info = [
            AttributeInfo(
                name="source",
                description="文档来源类型: paper, tutorial, doc, news",
                type="string",
            ),
            AttributeInfo(name="year", description="发布年份", type="integer"),
            AttributeInfo(name="topic", description="主题标签", type="string"),
        ]

        # 创建自查询检索器
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        retriever = SelfQueryRetriever.from_llm(
            llm=llm,
            vectorstore=vectorstore,
            document_contents="技术文档关于 AI 和 LLM 的内容",
            metadata_field_info=metadata_field_info,
        )

        # 测试查询
        queries = [
            "2023年的 RAG 论文",
            "关于向量数据库的教程",
            "2024年发布的内容",
        ]

        for query in queries:
            results = retriever.invoke(query)
            print(f"\n📌 查询: '{query}'")
            for doc in results:
                print(f"  - {doc.page_content[:40]}...")
                print(f"    元数据: {doc.metadata}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        print("ℹ️ 需要安装: pip install lark")


# ==================== 第四部分：自定义过滤器 ====================


def custom_filter():
    """自定义过滤器"""
    print("\n" + "=" * 60)
    print("第四部分：自定义过滤器")
    print("=" * 60)

    print("""
    Chroma 过滤器语法：
    ──────────────────
    
    单条件过滤：
    {"field": {"$eq": value}}     # 等于
    {"field": {"$ne": value}}     # 不等于
    {"field": {"$gt": value}}     # 大于
    {"field": {"$lt": value}}     # 小于
    
    多条件组合：
    {"$and": [条件1, 条件2]}
    {"$or": [条件1, 条件2]}
    """)

    try:
        from langchain_openai import OpenAIEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.documents import Document

        docs = [
            Document(
                page_content="Python 基础教程", metadata={"level": 1, "lang": "zh"}
            ),
            Document(
                page_content="Python 高级特性", metadata={"level": 3, "lang": "zh"}
            ),
            Document(
                page_content="Python Advanced", metadata={"level": 3, "lang": "en"}
            ),
        ]

        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(docs, embeddings)

        # 带过滤的检索
        retriever = vectorstore.as_retriever(
            search_kwargs={
                "k": 2,
                "filter": {"level": {"$gt": 1}},  # level > 1
            }
        )

        results = retriever.invoke("Python")

        print("📌 过滤条件: level > 1")
        print("\n检索结果：")
        for doc in results:
            print(f"  - {doc.page_content}")
            print(f"    元数据: {doc.metadata}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第五部分：查询解析实现 ====================


def query_parsing():
    """查询解析实现"""
    print("\n" + "=" * 60)
    print("第五部分：查询解析实现")
    print("=" * 60)

    code_example = '''
class QueryParser:
    """查询解析器"""
    
    def __init__(self, llm, field_info):
        self.llm = llm
        self.field_info = field_info
    
    def parse(self, query: str) -> dict:
        """解析查询为结构化格式"""
        
        prompt = f"""
分析用户查询，提取：
1. 语义查询部分（用于向量检索）
2. 过滤条件（基于元数据字段）

可用字段: {self.field_info}

用户查询: {query}

输出 JSON 格式:
{{
  "semantic_query": "...",
  "filters": {{
    "field1": "value1",
    ...
  }}
}}
"""
        response = self.llm.predict(prompt)
        return json.loads(response)
    
    def search(self, query: str, vectorstore):
        parsed = self.parse(query)
        
        return vectorstore.similarity_search(
            parsed["semantic_query"],
            filter=parsed["filters"]
        )
'''
    print("📌 查询解析器示例：")
    print(code_example)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：设计元数据
        为你的文档设计合适的元数据结构。

    练习 2：复杂过滤
        实现多条件组合过滤（AND/OR）。

    练习 3：对比效果
        对比自查询与普通检索的准确率。

    思考题：
        1. 元数据过滤的性能影响？
        2. 如何处理 LLM 解析错误？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 自查询检索")
    print("=" * 60)

    try:
        self_query_concept()
        metadata_design()
        langchain_self_query()
        custom_filter()
        query_parsing()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：07-hypothetical-questions.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
