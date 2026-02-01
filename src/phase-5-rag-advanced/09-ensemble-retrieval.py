"""
集成检索
========

学习目标：
    1. 理解集成检索的原理
    2. 掌握多检索器融合策略
    3. 学会构建自适应检索系统

核心概念：
    - Ensemble：组合多个检索器
    - 策略选择：根据查询类型选择检索器
    - 结果融合：合并多路检索结果

前置知识：
    - 08-contextual-compression.py

环境要求：
    - pip install langchain langchain-google-genai chromadb rank_bm25 python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：集成检索概念 ====================


def ensemble_concept():
    """集成检索概念"""
    print("=" * 60)
    print("第一部分：集成检索概念")
    print("=" * 60)

    print("""
    集成检索的优势：
    ────────────────
    
    单一检索器的局限：
    - 向量检索擅长语义，但弱关键词
    - BM25 擅长关键词，但弱语义
    - 不同检索器适合不同类型查询
    
    集成检索解决方案：
    - 组合多个检索器
    - 融合各自优势
    - 提高整体召回率和准确率
    
    ┌─────────────────────────────────────────────────────┐
    │                      Query                          │
    │                        │                            │
    │          ┌─────────────┼─────────────┐              │
    │          ▼             ▼             ▼              │
    │    ┌──────────┐  ┌──────────┐  ┌──────────┐        │
    │    │  向量    │  │  BM25    │  │  知识图谱 │        │
    │    │  检索    │  │  检索    │  │  检索    │        │
    │    └────┬─────┘  └────┬─────┘  └────┬─────┘        │
    │         │             │             │               │
    │         └─────────────┼─────────────┘               │
    │                       ▼                             │
    │              ┌───────────────────┐                 │
    │              │   结果融合器       │                 │
    │              │  (RRF / 加权)     │                 │
    │              └───────────────────┘                 │
    │                       │                             │
    │                       ▼                             │
    │                 融合后的结果                         │
    │                                                     │
    └─────────────────────────────────────────────────────┘
    """)


# ==================== 第二部分：LangChain EnsembleRetriever ====================


def langchain_ensemble():
    """LangChain EnsembleRetriever"""
    print("\n" + "=" * 60)
    print("第二部分：LangChain EnsembleRetriever")
    print("=" * 60)

    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_chroma import Chroma
        from langchain_community.retrievers import BM25Retriever
        from langchain.retrievers import EnsembleRetriever
        from langchain_core.documents import Document

        # 准备文档
        docs = [
            Document(page_content="Python 是一种解释型编程语言"),
            Document(page_content="机器学习需要大量数据训练模型"),
            Document(page_content="深度学习使用神经网络"),
            Document(page_content="Python 广泛用于数据科学"),
        ]

        # 创建 BM25 检索器
        bm25_retriever = BM25Retriever.from_documents(docs)
        bm25_retriever.k = 2

        # 创建向量检索器
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vectorstore = Chroma.from_documents(docs, embeddings)
        vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

        # 创建集成检索器
        ensemble = EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[0.4, 0.6],  # 向量检索权重更高
        )

        # 测试
        query = "Python 机器学习"
        results = ensemble.invoke(query)

        print(f"📌 查询: '{query}'")
        print(f"\n集成检索结果（{len(results)} 个文档）：")
        for doc in results:
            print(f"  - {doc.page_content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第三部分：自适应检索 ====================


def adaptive_retrieval():
    """自适应检索"""
    print("\n" + "=" * 60)
    print("第三部分：自适应检索")
    print("=" * 60)

    print("""
    自适应检索策略：
    ────────────────
    
    根据查询类型自动选择最佳检索器
    
    查询分类：
    - 关键词查询 → BM25
    - 语义查询 → 向量检索
    - 结构化查询 → 元数据过滤
    - 复杂查询 → 集成检索
    """)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

        classify_prompt = ChatPromptTemplate.from_template("""
分析以下查询的类型，选择最佳检索策略。

查询: {query}

类型选项:
- keyword: 精确匹配关键词（如人名、产品型号）
- semantic: 语义相似（如概念解释、原理说明）
- structured: 包含过滤条件（如年份、类型）
- complex: 需要多种策略结合

只输出类型名称:""")

        queries = [
            "iPhone 15 Pro Max",
            "什么是深度学习",
            "2023年发布的 AI 论文",
            "Python 异步编程的最佳实践",
        ]

        print("📌 查询分类示例：")
        for query in queries:
            chain = classify_prompt | llm
            result = chain.invoke({"query": query})
            print(f"  {query}")
            print(f"    → 类型: {result.content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：路由检索器 ====================


def router_retriever():
    """路由检索器"""
    print("\n" + "=" * 60)
    print("第四部分：路由检索器")
    print("=" * 60)

    code_example = '''
class RouterRetriever:
    """路由检索器 - 根据查询类型选择检索器"""
    
    def __init__(self, retrievers: dict, classifier):
        self.retrievers = retrievers
        self.classifier = classifier
    
    def retrieve(self, query: str):
        # 1. 分类查询
        query_type = self.classifier(query)
        
        # 2. 选择检索器
        if query_type in self.retrievers:
            retriever = self.retrievers[query_type]
        else:
            retriever = self.retrievers["default"]
        
        # 3. 执行检索
        return retriever.invoke(query)

# 使用示例
router = RouterRetriever(
    retrievers={
        "keyword": bm25_retriever,
        "semantic": vector_retriever,
        "structured": self_query_retriever,
        "complex": ensemble_retriever,
        "default": vector_retriever,
    },
    classifier=query_classifier
)

results = router.retrieve("Python 是什么")
'''
    print("📌 路由检索器示例：")
    print(code_example)


# ==================== 第五部分：级联检索 ====================


def cascade_retrieval():
    """级联检索"""
    print("\n" + "=" * 60)
    print("第五部分：级联检索")
    print("=" * 60)

    print("""
    级联检索策略：
    ──────────────
    
    多阶段检索，逐步精细化
    
    阶段 1: 粗检索 (快速，高召回)
        ↓
    阶段 2: 精检索 (精确，高准确)
        ↓
    阶段 3: 重排序 (优化排名)
    
    ┌─────────────────────────────────────────────────────┐
    │  Stage 1: BM25 快速检索                             │
    │           百万文档 → Top 100                        │
    │                    ↓                               │
    │  Stage 2: 向量检索精筛                              │
    │           Top 100 → Top 20                         │
    │                    ↓                               │
    │  Stage 3: Cross-Encoder 重排序                     │
    │           Top 20 → Top 5                           │
    └─────────────────────────────────────────────────────┘
    """)

    code_example = '''
class CascadeRetriever:
    """级联检索器"""
    
    def __init__(self, stages: list):
        self.stages = stages
    
    def retrieve(self, query: str, k: int = 5):
        results = None
        
        for stage in self.stages:
            if results is None:
                # 第一阶段：全量检索
                results = stage.retrieve(query, k=stage.k)
            else:
                # 后续阶段：从前阶段结果中筛选
                docs = [r.page_content for r in results]
                results = stage.rerank(query, docs, k=stage.k)
        
        return results[:k]
'''
    print("📌 级联检索器示例：")
    print(code_example)


# ==================== 第六部分：完整实现 ====================


def complete_ensemble():
    """完整集成检索实现"""
    print("\n" + "=" * 60)
    print("第六部分：完整集成检索实现")
    print("=" * 60)

    code_example = '''
class AdvancedEnsembleRetriever:
    """高级集成检索器"""
    
    def __init__(self, vector_store, bm25_retriever, llm):
        self.vector_store = vector_store
        self.bm25 = bm25_retriever
        self.llm = llm
    
    def retrieve(self, query: str, k: int = 5):
        # 1. 多路检索
        vector_results = self.vector_store.similarity_search(query, k=k*2)
        bm25_results = self.bm25.invoke(query)[:k*2]
        
        # 2. RRF 融合
        fused = self._rrf_fusion(
            [vector_results, bm25_results],
            k=60
        )
        
        # 3. 压缩上下文
        compressed = self._compress(query, fused[:k])
        
        return compressed
    
    def _rrf_fusion(self, result_lists, k=60):
        scores = {}
        for results in result_lists:
            for rank, doc in enumerate(results):
                doc_id = doc.page_content
                if doc_id not in scores:
                    scores[doc_id] = 0
                scores[doc_id] += 1 / (k + rank + 1)
        
        sorted_docs = sorted(scores.keys(), key=lambda x: -scores[x])
        return sorted_docs
    
    def _compress(self, query, docs):
        # 使用 LLM 压缩
        pass
'''
    print("📌 高级集成检索器示例：")
    print(code_example)


# ==================== 第七部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：权重调优
        测试不同检索器权重对效果的影响。

    练习 2：实现路由器
        实现一个基于规则的查询路由器。

    练习 3：级联优化
        构建一个三阶段级联检索系统。

    思考题：
        1. 如何确定最佳的检索器组合？
        2. 集成会增加多少延迟？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 集成检索")
    print("=" * 60)

    try:
        ensemble_concept()
        langchain_ensemble()
        adaptive_retrieval()
        router_retriever()
        cascade_retrieval()
        complete_ensemble()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：10-rag-evaluation-metrics.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
