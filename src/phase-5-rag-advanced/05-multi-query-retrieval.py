"""
多查询检索
==========

学习目标：
    1. 理解多查询检索的原理
    2. 掌握 LangChain MultiQueryRetriever
    3. 学会结果融合策略

核心概念：
    - Multi-Query：从多个角度生成查询
    - 结果去重与融合
    - 提高召回率

前置知识：
    - 04-query-expansion.py

环境要求：
    - pip install langchain langchain-google-genai chromadb python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：多查询检索概念 ====================


def multi_query_concept():
    """多查询检索概念"""
    print("=" * 60)
    print("第一部分：多查询检索概念")
    print("=" * 60)

    print("""
    多查询检索原理：
    ────────────────
    
    用户的单一查询可能无法覆盖所有相关文档
    通过 LLM 从多个角度生成变体查询
    合并所有查询的检索结果
    
    ┌─────────────────────────────────────────────────────┐
    │                                                     │
    │   原始查询: "如何优化 Python 代码性能"               │
    │                     │                               │
    │                     ▼                               │
    │          ┌───────────────────┐                     │
    │          │   LLM 生成变体     │                     │
    │          └───────────────────┘                     │
    │                     │                               │
    │     ┌───────────────┼───────────────┐              │
    │     ▼               ▼               ▼              │
    │ ┌─────────┐   ┌─────────┐   ┌─────────┐           │
    │ │ Query 1 │   │ Query 2 │   │ Query 3 │           │
    │ │Python   │   │代码优化 │   │性能调优 │           │
    │ │性能提升 │   │技术     │   │方法    │            │
    │ └────┬────┘   └────┬────┘   └────┬────┘           │
    │      │             │             │                 │
    │      ▼             ▼             ▼                 │
    │   [检索]        [检索]        [检索]               │
    │      │             │             │                 │
    │      └─────────────┼─────────────┘                 │
    │                    ▼                               │
    │          ┌───────────────────┐                     │
    │          │   去重 & 融合      │                     │
    │          └───────────────────┘                     │
    │                    │                               │
    │                    ▼                               │
    │              最终结果集                             │
    │                                                     │
    └─────────────────────────────────────────────────────┘
    """)


# ==================== 第二部分：LangChain MultiQueryRetriever ====================


def langchain_multi_query():
    """LangChain MultiQueryRetriever"""
    print("\n" + "=" * 60)
    print("第二部分：LangChain MultiQueryRetriever")
    print("=" * 60)

    try:
        from langchain.retrievers.multi_query import MultiQueryRetriever
        from langchain_google_genai import (
            ChatGoogleGenerativeAI,
            GoogleGenerativeAIEmbeddings,
        )
        from langchain_chroma import Chroma
        from langchain_core.documents import Document

        # 准备文档
        docs = [
            Document(page_content="Python 的 GIL 锁会限制多线程性能"),
            Document(page_content="使用 Cython 可以加速 Python 代码"),
            Document(page_content="NumPy 向量化运算比 for 循环快很多"),
            Document(page_content="性能分析工具 cProfile 帮助定位瓶颈"),
            Document(page_content="异步编程可以提升 IO 密集型任务性能"),
        ]

        # 创建向量存储
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vectorstore = Chroma.from_documents(docs, embeddings)
        base_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

        # 创建多查询检索器
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        multi_retriever = MultiQueryRetriever.from_llm(
            retriever=base_retriever, llm=llm
        )

        # 检索
        query = "Python 代码优化"

        # 查看生成的查询
        from langchain.retrievers.multi_query import LineListOutputParser
        import logging

        logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.DEBUG)

        results = multi_retriever.invoke(query)

        print(f"📌 原始查询: '{query}'")
        print(f"\n检索到 {len(results)} 个唯一文档：")
        for doc in results:
            print(f"  - {doc.page_content[:50]}...")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第三部分：自定义查询生成 ====================


def custom_query_generator():
    """自定义查询生成器"""
    print("\n" + "=" * 60)
    print("第三部分：自定义查询生成器")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

        # 自定义提示模板
        prompt = ChatPromptTemplate.from_template("""
你是一个查询生成专家。给定用户问题，请从以下角度生成3个不同的查询变体：
1. 技术实现角度
2. 问题解决角度  
3. 最佳实践角度

原始问题: {question}

请直接输出3个查询，每行一个:""")

        chain = prompt | llm | StrOutputParser()

        question = "如何处理 Python 中的内存泄漏"
        result = chain.invoke({"question": question})

        print(f"📌 原始问题: '{question}'")
        print("\n生成的查询变体：")
        for line in result.strip().split("\n"):
            if line.strip():
                print(f"  - {line.strip()}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：结果融合策略 ====================


def result_fusion():
    """结果融合策略"""
    print("\n" + "=" * 60)
    print("第四部分：结果融合策略")
    print("=" * 60)

    print("""
    融合策略：
    ──────────
    
    1. 简单去重
       - 合并所有结果，移除重复文档
       
    2. 投票计数
       - 文档被多个查询检索到的次数越多，排名越高
       
    3. RRF (Reciprocal Rank Fusion)
       - 考虑每个查询中的排名位置
       - score = Σ 1/(k + rank)
    """)

    def fuse_results(query_results: list):
        """融合多查询结果"""
        doc_counts = {}
        doc_content = {}

        for results in query_results:
            for rank, doc in enumerate(results):
                content = doc if isinstance(doc, str) else doc.page_content
                if content not in doc_counts:
                    doc_counts[content] = 0
                    doc_content[content] = doc
                doc_counts[content] += 1

        # 按出现次数排序
        sorted_docs = sorted(doc_counts.keys(), key=lambda x: -doc_counts[x])

        return [(doc_content[d], doc_counts[d]) for d in sorted_docs]

    # 示例
    results_q1 = ["文档A", "文档B", "文档C"]
    results_q2 = ["文档B", "文档D", "文档A"]
    results_q3 = ["文档A", "文档E", "文档B"]

    fused = fuse_results([results_q1, results_q2, results_q3])

    print("📌 融合示例：")
    print(f"  Query 1: {results_q1}")
    print(f"  Query 2: {results_q2}")
    print(f"  Query 3: {results_q3}")
    print("\n融合结果（按投票数）：")
    for doc, count in fused:
        print(f"  [{count}票] {doc}")


# ==================== 第五部分：完整实现 ====================


def complete_implementation():
    """完整实现"""
    print("\n" + "=" * 60)
    print("第五部分：完整实现")
    print("=" * 60)

    code_example = '''
class MultiQueryRAG:
    """多查询 RAG 系统"""
    
    def __init__(self, vectorstore, llm, n_queries=3):
        self.vectorstore = vectorstore
        self.llm = llm
        self.n_queries = n_queries
    
    def query(self, question: str, k: int = 5):
        # 1. 生成多个查询
        queries = self._generate_queries(question)
        
        # 2. 对每个查询检索
        all_results = []
        for q in queries:
            results = self.vectorstore.similarity_search(q, k=k)
            all_results.append(results)
        
        # 3. 融合结果
        fused = self._fuse_results(all_results)
        
        # 4. 取 Top K
        top_docs = [doc for doc, _ in fused[:k]]
        
        # 5. 生成答案
        context = "\\n\\n".join([d.page_content for d in top_docs])
        answer = self._generate_answer(question, context)
        
        return answer, top_docs, queries
    
    def _generate_queries(self, question):
        prompt = f"""生成{self.n_queries}个关于'{question}'的查询变体..."""
        # 实现略
        pass
    
    def _fuse_results(self, query_results):
        # 实现略
        pass
    
    def _generate_answer(self, question, context):
        # 实现略
        pass
'''
    print("📌 完整实现示例：")
    print(code_example)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现 RRF 融合
        完成 RRF 融合算法并对比效果。

    练习 2：调整查询数量
        测试不同查询数量对结果的影响。

    练习 3：领域定制
        为特定领域定制查询生成提示。

    思考题：
        1. 生成多少个查询比较合适？
        2. 如何评估多查询的效果？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 多查询检索")
    print("=" * 60)

    try:
        multi_query_concept()
        langchain_multi_query()
        custom_query_generator()
        result_fusion()
        complete_implementation()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：06-self-query-retrieval.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
