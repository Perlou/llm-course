"""
混合检索
========

学习目标：
    1. 理解混合检索的原理
    2. 掌握 BM25 与向量检索结合
    3. 学会分数融合策略

核心概念：
    - 稀疏检索：基于关键词（BM25）
    - 稠密检索：基于向量（Embedding）
    - 分数融合：RRF、加权融合

前置知识：
    - Phase 4 RAG 基础

环境要求：
    - pip install langchain langchain-google-genai chromadb rank_bm25 python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：混合检索概念 ====================


def hybrid_search_concept():
    """混合检索概念"""
    print("=" * 60)
    print("第一部分：混合检索概念")
    print("=" * 60)

    print("""
    为什么需要混合检索？
    ────────────────────
    
    稀疏检索（BM25）：
    ✅ 精确匹配关键词
    ✅ 对专有名词、编号敏感
    ❌ 无法理解语义
    
    稠密检索（向量）：
    ✅ 理解语义相似性
    ✅ 处理同义词
    ❌ 可能错过精确匹配
    
    混合检索 = BM25 + 向量检索
    ─────────────────────────
    
    ┌─────────────┐    ┌─────────────┐
    │   BM25      │    │   向量检索   │
    │  (关键词)    │    │  (语义)     │
    └──────┬──────┘    └──────┬──────┘
           │                  │
           └────────┬─────────┘
                    ▼
            ┌──────────────┐
            │  分数融合     │
            │  (RRF/加权)   │
            └──────────────┘
    """)


# ==================== 第二部分：BM25 检索 ====================


def bm25_retrieval():
    """BM25 检索"""
    print("\n" + "=" * 60)
    print("第二部分：BM25 检索")
    print("=" * 60)

    try:
        from rank_bm25 import BM25Okapi
        import jieba

        # 示例文档
        documents = [
            "Python 是一种流行的编程语言",
            "机器学习使用 Python 进行数据分析",
            "深度学习框架包括 TensorFlow 和 PyTorch",
            "JavaScript 用于 Web 前端开发",
        ]

        # 中文分词
        tokenized_docs = [list(jieba.cut(doc)) for doc in documents]

        # 创建 BM25 索引
        bm25 = BM25Okapi(tokenized_docs)

        # 查询
        query = "Python 编程"
        tokenized_query = list(jieba.cut(query))
        scores = bm25.get_scores(tokenized_query)

        print(f"📌 查询: '{query}'")
        print("\nBM25 分数：")
        for doc, score in sorted(zip(documents, scores), key=lambda x: -x[1]):
            print(f"  [{score:.4f}] {doc}")

    except ImportError:
        print("⚠️ 需要安装: pip install rank_bm25 jieba")


# ==================== 第三部分：分数融合 ====================


def score_fusion():
    """分数融合策略"""
    print("\n" + "=" * 60)
    print("第三部分：分数融合策略")
    print("=" * 60)

    print("""
    1. 加权融合
    ──────────
    final_score = α * bm25_score + (1-α) * vector_score
    
    需要归一化分数到 [0, 1]
    
    2. Reciprocal Rank Fusion (RRF)
    ─────────────────────────────────
    RRF_score = Σ 1 / (k + rank)
    
    k 通常设为 60
    优点：不需要归一化
    """)

    # RRF 示例
    def rrf_fusion(rankings: list, k: int = 60):
        """RRF 融合"""
        rrf_scores = {}

        for ranking in rankings:
            for rank, doc_id in enumerate(ranking):
                if doc_id not in rrf_scores:
                    rrf_scores[doc_id] = 0
                rrf_scores[doc_id] += 1 / (k + rank + 1)

        return sorted(rrf_scores.items(), key=lambda x: -x[1])

    # 示例
    bm25_ranking = ["doc_A", "doc_B", "doc_C", "doc_D"]
    vector_ranking = ["doc_C", "doc_A", "doc_D", "doc_B"]

    result = rrf_fusion([bm25_ranking, vector_ranking])

    print("📌 RRF 融合示例：")
    print(f"  BM25 排名: {bm25_ranking}")
    print(f"  向量排名: {vector_ranking}")
    print(f"  融合结果: {[doc for doc, _ in result]}")


# ==================== 第四部分：LangChain 混合检索 ====================


def langchain_hybrid():
    """LangChain 混合检索实现"""
    print("\n" + "=" * 60)
    print("第四部分：LangChain 混合检索")
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

        # 创建混合检索器
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[0.5, 0.5],  # 等权重
        )

        # 检索
        query = "Python 编程"
        results = ensemble_retriever.invoke(query)

        print(f"📌 查询: '{query}'")
        print("\n混合检索结果：")
        for doc in results:
            print(f"  - {doc.page_content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第五部分：自定义混合检索器 ====================


def custom_hybrid_retriever():
    """自定义混合检索器"""
    print("\n" + "=" * 60)
    print("第五部分：自定义混合检索器")
    print("=" * 60)

    code_example = '''
class HybridRetriever:
    """自定义混合检索器"""
    
    def __init__(self, documents, embeddings, alpha=0.5):
        from rank_bm25 import BM25Okapi
        
        self.documents = documents
        self.alpha = alpha
        
        # BM25
        tokenized = [doc.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)
        
        # 向量存储
        self.embeddings = embeddings
        self.doc_vectors = embeddings.embed_documents(documents)
    
    def search(self, query, k=5):
        # BM25 分数
        bm25_scores = self.bm25.get_scores(query.split())
        bm25_norm = self._normalize(bm25_scores)
        
        # 向量分数
        query_vec = self.embeddings.embed_query(query)
        vector_scores = [self._cosine_sim(query_vec, dv) 
                        for dv in self.doc_vectors]
        
        # 融合
        final_scores = [
            self.alpha * b + (1 - self.alpha) * v
            for b, v in zip(bm25_norm, vector_scores)
        ]
        
        # 排序返回
        ranked = sorted(enumerate(final_scores), 
                       key=lambda x: -x[1])[:k]
        return [(self.documents[i], s) for i, s in ranked]
'''
    print("📌 自定义实现示例：")
    print(code_example)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现 RRF
        实现一个完整的 RRF 融合函数并测试。

        ✅ 参考答案：
        ```python
        def reciprocal_rank_fusion(results_list: list, k: int = 60):
            '''
            RRF 融合算法
            results_list: 多个检索器的结果列表 [[doc1, doc2], [doc3, doc1], ...]
            k: 平滑参数
            '''
            doc_scores = {}
            
            for results in results_list:
                for rank, doc in enumerate(results):
                    doc_id = doc.page_content  # 或使用 doc.metadata["id"]
                    if doc_id not in doc_scores:
                        doc_scores[doc_id] = {"doc": doc, "score": 0}
                    # RRF 公式: 1 / (k + rank)
                    doc_scores[doc_id]["score"] += 1 / (k + rank + 1)
            
            # 按分数排序
            sorted_docs = sorted(doc_scores.values(), key=lambda x: x["score"], reverse=True)
            return [item["doc"] for item in sorted_docs]

        # 使用
        bm25_results = bm25_retriever.invoke("query")
        vector_results = vector_retriever.invoke("query")
        fused = reciprocal_rank_fusion([bm25_results, vector_results])
        ```

    练习 2：调整权重
        测试不同 alpha 值对混合检索效果的影响。

        ✅ 参考答案：
        ```python
        from langchain.retrievers import EnsembleRetriever

        # 测试不同权重组合
        alphas = [0.0, 0.3, 0.5, 0.7, 1.0]
        query = "Python 编程"
        
        for alpha in alphas:
            retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, vector_retriever],
                weights=[1 - alpha, alpha]  # BM25 权重, Vector 权重
            )
            results = retriever.invoke(query)
            print(f"alpha={alpha}: {[d.page_content[:20] for d in results[:3]]}")
        
        # alpha=0.0 纯 BM25
        # alpha=1.0 纯向量
        # alpha=0.5 平衡混合
        ```

    练习 3：中文优化
        使用 jieba 分词优化中文 BM25 检索。

        ✅ 参考答案：
        ```python
        import jieba
        from rank_bm25 import BM25Okapi

        def chinese_tokenizer(text: str):
            return list(jieba.cut(text))

        # 文档分词
        docs = ["Python是编程语言", "机器学习改变世界"]
        tokenized_docs = [chinese_tokenizer(doc) for doc in docs]

        # 创建 BM25 索引
        bm25 = BM25Okapi(tokenized_docs)

        # 查询
        query = "编程"
        tokenized_query = chinese_tokenizer(query)
        scores = bm25.get_scores(tokenized_query)
        
        # 获取排序结果
        top_indices = scores.argsort()[::-1]
        print([docs[i] for i in top_indices[:3]])
        ```

    思考题：
        1. 什么场景下 BM25 比向量检索更好？
           
           ✅ 答案：
           - 精确关键词匹配（产品型号、代码变量名）
           - 罕见术语或新词（向量模型可能未训练过）
           - 需要精确召回的场景
           - 短文本查询
           - 对语义理解要求不高的场景

        2. 如何动态调整融合权重？
           
           ✅ 答案：
           - 基于查询特征：短查询用 BM25，长查询用向量
           - 基于领域：技术文档偏 BM25，问答偏向量
           - 基于用户反馈：根据点击率动态调整
           - A/B 测试：找到最佳权重组合
           - 使用 LLM 判断查询类型后路由
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 混合检索")
    print("=" * 60)

    try:
        hybrid_search_concept()
        bm25_retrieval()
        score_fusion()
        langchain_hybrid()
        custom_hybrid_retriever()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：02-reranking.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
