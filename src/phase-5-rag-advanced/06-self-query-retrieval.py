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
    - pip install langchain langchain-google-genai chromadb lark python-dotenv
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
        from langchain_classic.chains.query_constructor.base import AttributeInfo
        from langchain_classic.retrievers.self_query.base import SelfQueryRetriever
        from langchain_google_genai import (
            ChatGoogleGenerativeAI,
            GoogleGenerativeAIEmbeddings,
        )
        from langchain_chroma import Chroma
        from langchain_core.documents import Document

        # 文档元数据描述
        metadata_field_info = [
            AttributeInfo(
                name="category",
                description="文档类别：教程、API文档、博客",
                type="string",
            ),
            AttributeInfo(
                name="difficulty",
                description="难度级别：初级、中级、高级",
                type="string",
            ),
            AttributeInfo(name="year", description="发布年份", type="integer"),
        ]

        # 准备文档
        docs = [
            Document(
                page_content="Python 基础语法教程",
                metadata={"category": "教程", "difficulty": "初级", "year": 2023},
            ),
            Document(
                page_content="机器学习算法详解",
                metadata={"category": "教程", "difficulty": "中级", "year": 2024},
            ),
            Document(
                page_content="FastAPI 官方文档",
                metadata={"category": "API文档", "difficulty": "中级", "year": 2024},
            ),
        ]

        # 创建向量存储
        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
        vectorstore = Chroma.from_documents(docs, embeddings)

        # 创建 SelfQueryRetriever
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
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
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
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

        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
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

        ✅ 参考答案：
        ```python
        # 技术文档元数据设计
        tech_doc_metadata = {
            "title": str,      # 文档标题
            "author": str,     # 作者
            "date": str,       # 发布日期 (YYYY-MM-DD)
            "category": str,   # 分类：tutorial, reference, guide
            "difficulty": str, # 难度：beginner, intermediate, advanced
            "language": str,   # 编程语言
            "version": str,    # 版本号
            "tags": list,      # 标签列表
        }

        # 商品元数据设计
        product_metadata = {
            "name": str,
            "price": float,
            "category": str,
            "brand": str,
            "rating": float,
            "in_stock": bool,
        }

        # LangChain AttributeInfo 定义
        from langchain_classic.chains.query_constructor.base import AttributeInfo

        metadata_field_info = [
            AttributeInfo(name="category", description="文档类别", type="string"),
            AttributeInfo(name="difficulty", description="难度级别", type="string"),
            AttributeInfo(name="date", description="发布日期", type="string"),
        ]
        ```

    练习 2：复杂过滤
        实现多条件组合过滤（AND/OR）。

        ✅ 参考答案：
        ```python
        # 自定义查询解析
        def parse_complex_query(query: str):
            '''解析包含条件的自然语言查询'''
            prompt = f'''
            分析以下查询，提取搜索词和过滤条件：
            查询：{query}
            
            返回 JSON 格式：
            {{"search": "搜索词", "filters": {{"field": "value"}}}}
            '''
            return llm.invoke(prompt)

        # 使用 Chroma 的过滤语法
        # AND 条件
        results = vectorstore.similarity_search(
            "Python",
            filter={
                "$and": [
                    {"category": "tutorial"},
                    {"difficulty": "beginner"}
                ]
            }
        )

        # OR 条件
        results = vectorstore.similarity_search(
            "Python",
            filter={
                "$or": [
                    {"language": "python"},
                    {"language": "javascript"}
                ]
            }
        )
        ```

    练习 3：对比效果
        对比自查询与普通检索的准确率。

        ✅ 参考答案：
        ```python
        test_cases = [
            {
                "query": "2024年发布的Python初级教程",
                "expected_filter": {"date": {"$gte": "2024-01-01"}, "difficulty": "beginner"}
            },
            {
                "query": "价格低于100的电子产品",
                "expected_filter": {"price": {"$lt": 100}, "category": "electronics"}
            },
        ]

        def evaluate_self_query():
            correct = 0
            for case in test_cases:
                # 普通检索
                normal_results = retriever.invoke(case["query"])
                
                # 自查询
                self_query_results = self_query_retriever.invoke(case["query"])
                
                # 检查过滤是否正确应用
                for doc in self_query_results:
                    if matches_filter(doc.metadata, case["expected_filter"]):
                        correct += 1
            
            print(f"自查询准确率: {correct/len(test_cases):.2%}")
        ```

    思考题：
        1. 元数据过滤的性能影响？
           
           ✅ 答案：
           - 向量数据库通常先过滤后搜索，性能影响较小
           - 索引设计很重要：常用过滤字段建立索引
           - 复杂过滤（多条件 OR）可能较慢
           - 建议：测试不同过滤条件的响应时间

        2. 如何处理 LLM 解析错误？
           
           ✅ 答案：
           - 设置默认值：解析失败时使用纯语义检索
           - 验证过滤条件：检查字段名和值是否有效
           - 重试机制：解析失败时重新尝试
           - Fallback：降级到普通检索
           - 日志记录：记录失败案例用于改进
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
