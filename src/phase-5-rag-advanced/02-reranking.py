"""
重排序技术
==========

学习目标：
    1. 理解重排序的作用
    2. 掌握 Cross-Encoder 重排序
    3. 了解 LLM 重排序方法

核心概念：
    - 两阶段检索：粗检索 + 精排序
    - Cross-Encoder：同时编码 query 和 doc
    - Rerank Score：重排序分数

前置知识：
    - 01-hybrid-search.py

环境要求：
    - pip install langchain langchain-google-genai sentence-transformers python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：重排序概念 ====================


def reranking_concept():
    """重排序概念"""
    print("=" * 60)
    print("第一部分：重排序概念")
    print("=" * 60)

    print("""
    为什么需要重排序？
    ─────────────────
    
    第一阶段：粗检索（快速）
    - 从百万文档中检索 Top 100
    - 使用向量相似度或 BM25
    - 速度快，但精度有限
    
    第二阶段：精排序（精确）
    - 对 Top 100 重新排序
    - 使用更复杂的模型
    - 速度慢，但精度高
    
    ┌─────────────────────────────────────────────────────┐
    │                                                     │
    │   Query                                             │
    │     │                                               │
    │     ▼                                               │
    │  ┌─────────────────────────────────────────────┐   │
    │  │ 粗检索：向量相似度 (毫秒级)                    │   │
    │  │        百万 → Top 100                        │   │
    │  └──────────────────────┬──────────────────────┘   │
    │                         │                          │
    │                         ▼                          │
    │  ┌─────────────────────────────────────────────┐   │
    │  │ 精排序：Cross-Encoder (秒级)                  │   │
    │  │        Top 100 → Top 10                      │   │
    │  └─────────────────────────────────────────────┘   │
    │                                                     │
    └─────────────────────────────────────────────────────┘
    """)


# ==================== 第二部分：Bi-Encoder vs Cross-Encoder ====================


def encoder_comparison():
    """编码器对比"""
    print("\n" + "=" * 60)
    print("第二部分：Bi-Encoder vs Cross-Encoder")
    print("=" * 60)

    print("""
    Bi-Encoder（双塔模型）
    ──────────────────────
    - 分别编码 Query 和 Document
    - 可以预计算文档向量
    - 速度快，适合粗检索
    
    Query ──▶ [Encoder] ──▶ Query向量
                                    ╲
                                     ▶ 余弦相似度
                                    ╱
    Doc ──▶ [Encoder] ──▶ Doc向量
    
    Cross-Encoder（交叉编码）
    ─────────────────────────
    - 同时编码 Query 和 Document
    - 无法预计算
    - 精度高，适合精排序
    
    [CLS] Query [SEP] Doc [SEP] ──▶ [Encoder] ──▶ 相关性分数
    """)


# ==================== 第三部分：Cross-Encoder 实现 ====================


def cross_encoder_demo():
    """Cross-Encoder 重排序"""
    print("\n" + "=" * 60)
    print("第三部分：Cross-Encoder 重排序")
    print("=" * 60)

    try:
        from sentence_transformers import CrossEncoder

        # 加载模型
        model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

        query = "什么是机器学习"
        documents = [
            "机器学习是人工智能的一个分支，让计算机从数据中学习。",
            "深度学习使用多层神经网络处理复杂问题。",
            "Python 是一种流行的编程语言。",
            "机器学习算法可以自动改进性能。",
        ]

        # 创建 query-doc 对
        pairs = [[query, doc] for doc in documents]

        # 获取相关性分数
        scores = model.predict(pairs)

        # 排序
        ranked = sorted(zip(documents, scores), key=lambda x: -x[1])

        print(f"📌 查询: '{query}'")
        print("\nCross-Encoder 重排序结果：")
        for doc, score in ranked:
            print(f"  [{score:.4f}] {doc[:40]}...")

    except ImportError:
        print("⚠️ 需要安装: pip install sentence-transformers")


# ==================== 第四部分：LLM 重排序 ====================


def llm_reranking():
    """LLM 重排序"""
    print("\n" + "=" * 60)
    print("第四部分：LLM 重排序")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

        query = "Python 的优点"
        documents = [
            "Python 语法简洁易读",
            "Java 是强类型语言",
            "Python 有丰富的库生态",
        ]

        # Pointwise 评分
        prompt = ChatPromptTemplate.from_template("""
评估以下文档与查询的相关性，只输出 1-10 的分数。

查询: {query}
文档: {document}

分数:""")

        scored = []
        for doc in documents:
            response = llm.invoke(prompt.format_messages(query=query, document=doc))
            try:
                score = float(response.content.strip())
            except:
                score = 5.0
            scored.append((doc, score))

        ranked = sorted(scored, key=lambda x: -x[1])

        print(f"📌 查询: '{query}'")
        print("\nLLM 重排序结果：")
        for doc, score in ranked:
            print(f"  [{score:.1f}] {doc}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第五部分：Cohere Rerank ====================


def cohere_rerank():
    """Cohere Rerank API"""
    print("\n" + "=" * 60)
    print("第五部分：Cohere Rerank API")
    print("=" * 60)

    code_example = """
# Cohere Rerank 使用示例

import cohere

co = cohere.Client("YOUR_API_KEY")

query = "什么是机器学习"
documents = [
    "机器学习让计算机从数据学习...",
    "深度学习使用神经网络...",
    "Python 是编程语言...",
]

# 调用 Rerank API
results = co.rerank(
    model="rerank-multilingual-v2.0",
    query=query,
    documents=documents,
    top_n=3
)

for result in results:
    print(f"[{result.relevance_score:.4f}] {documents[result.index]}")
"""
    print("📌 Cohere Rerank 代码示例：")
    print(code_example)


# ==================== 第六部分：集成到 RAG ====================


def integrate_to_rag():
    """集成到 RAG 流程"""
    print("\n" + "=" * 60)
    print("第六部分：集成到 RAG 流程")
    print("=" * 60)

    code_example = '''
class RAGWithRerank:
    """带重排序的 RAG"""
    
    def __init__(self, retriever, reranker, llm):
        self.retriever = retriever
        self.reranker = reranker
        self.llm = llm
    
    def query(self, question, k=5, rerank_top=10):
        # 1. 粗检索
        candidates = self.retriever.search(question, k=rerank_top)
        
        # 2. 重排序
        reranked = self.reranker.rerank(question, candidates, top_k=k)
        
        # 3. 生成答案
        context = "\\n\\n".join([doc for doc, _ in reranked])
        answer = self.llm.predict(f"Context: {context}\\n\\nQ: {question}")
        
        return answer, reranked
'''
    print("📌 集成到 RAG 的示例：")
    print(code_example)


# ==================== 第七部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：对比效果
        比较有无重排序的 RAG 回答质量。

        ✅ 参考答案：
        ```python
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        
        def qa_without_rerank(query):
            docs = retriever.invoke(query)[:3]
            context = "\\n".join(d.page_content for d in docs)
            return generate_answer(context, query)

        def qa_with_rerank(query):
            docs = retriever.invoke(query)[:10]
            reranked = reranker.rerank(query, docs)[:3]
            context = "\\n".join(d.page_content for d in reranked)
            return generate_answer(context, query)

        # 对比测试
        test_queries = ["Python 的优点", "如何学习机器学习"]
        for q in test_queries:
            print(f"无重排序: {qa_without_rerank(q)[:100]}")
            print(f"有重排序: {qa_with_rerank(q)[:100]}")
        ```

    练习 2：不同模型
        测试不同 Cross-Encoder 模型的效果。

        ✅ 参考答案：
        ```python
        from sentence_transformers import CrossEncoder
        import time

        models = [
            "cross-encoder/ms-marco-MiniLM-L-6-v2",  # 快速
            "cross-encoder/ms-marco-MiniLM-L-12-v2",  # 中等
            # "cross-encoder/ms-marco-TinyBERT-L-6-v2",  # 更快
        ]

        query = "Python programming"
        docs = ["Python is a language", "Java is popular", "Machine learning uses Python"]

        for model_name in models:
            model = CrossEncoder(model_name)
            
            start = time.time()
            scores = model.predict([(query, doc) for doc in docs])
            latency = time.time() - start
            
            print(f"{model_name}")
            print(f"  延迟: {latency*1000:.2f}ms")
            print(f"  分数: {scores}")
        ```

    练习 3：中文重排序
        尝试中文 Cross-Encoder 模型。

        ✅ 参考答案：
        ```python
        from sentence_transformers import CrossEncoder

        # 中文重排序模型
        chinese_models = [
            "BAAI/bge-reranker-base",
            "BAAI/bge-reranker-large",
        ]

        query = "Python 编程语言的优点"
        docs = [
            "Python 语法简洁易读",
            "Java 是企业级语言",
            "Python 拥有丰富的库",
        ]

        for model_name in chinese_models:
            model = CrossEncoder(model_name)
            pairs = [(query, doc) for doc in docs]
            scores = model.predict(pairs)
            
            # 排序
            sorted_pairs = sorted(zip(scores, docs), reverse=True)
            print(f"{model_name}:")
            for score, doc in sorted_pairs:
                print(f"  [{score:.4f}] {doc}")
        ```

    思考题：
        1. 重排序会增加多少延迟？
           
           ✅ 答案：
           - MiniLM 模型：~10-50ms (CPU)
           - Large 模型：~50-200ms (CPU)
           - GPU 加速可降低 5-10 倍
           - 批处理比逐条处理更高效
           - 延迟与候选文档数量线性相关

        2. 如何权衡精度和速度？
           
           ✅ 答案：
           - 两阶段检索：先粗检索多，再重排序少量
           - 模型选择：小模型速度快，大模型精度高
           - 缓存热门查询的重排序结果
           - 异步重排序：先返回初始结果，后台重排
           - 设置超时机制：超时时返回未重排结果
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 重排序技术")
    print("=" * 60)

    try:
        reranking_concept()
        encoder_comparison()
        cross_encoder_demo()
        llm_reranking()
        cohere_rerank()
        integrate_to_rag()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：03-parent-document-retriever.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
