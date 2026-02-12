"""
RAG 评估指标
===========

学习目标：
    1. 掌握 RAG 评估的核心维度
    2. 学会检索质量评估
    3. 理解生成质量评估

环境要求：
    - pip install langchain langchain-google-genai python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：评估维度 ====================


def evaluation_dimensions():
    """RAG 评估维度"""
    print("=" * 60)
    print("第一部分：RAG 评估维度")
    print("=" * 60)

    print("""
    RAG 评估体系：
    ──────────────
    
    1. 检索质量
       - Precision@K: 检索精确率
       - Recall@K: 检索召回率
       - MRR: 平均倒数排名
    
    2. 生成质量
       - Faithfulness: 忠实度
       - Relevance: 相关性
       - Completeness: 完整性
    
    3. 端到端
       - Answer Correctness: 正确性
       - Latency: 延迟
    """)


# ==================== 第二部分：检索评估 ====================


def retrieval_metrics():
    """检索评估"""
    print("\n" + "=" * 60)
    print("第二部分：检索评估")
    print("=" * 60)

    def precision_at_k(retrieved, relevant, k):
        hits = sum(1 for d in retrieved[:k] if d in relevant)
        return hits / k

    def recall_at_k(retrieved, relevant, k):
        hits = sum(1 for d in retrieved[:k] if d in relevant)
        return hits / len(relevant) if relevant else 0

    def mrr(retrieved, relevant):
        for i, doc in enumerate(retrieved):
            if doc in relevant:
                return 1 / (i + 1)
        return 0

    retrieved = ["doc1", "doc2", "doc3", "doc4", "doc5"]
    relevant = {"doc2", "doc4", "doc6"}

    print(f"📌 Precision@5: {precision_at_k(retrieved, relevant, 5):.3f}")
    print(f"📌 Recall@5: {recall_at_k(retrieved, relevant, 5):.3f}")
    print(f"📌 MRR: {mrr(retrieved, relevant):.3f}")


# ==================== 第三部分：生成评估 ====================


def generation_metrics():
    """生成评估"""
    print("\n" + "=" * 60)
    print("第三部分：生成评估")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

        context = "Python 是一种解释型编程语言。"
        answer = "Python 是一种解释型编程语言。"
        question = "Python 是什么？"

        prompt = f"""
评估回答是否忠实于上下文(1-10分):
上下文: {context}
回答: {answer}
只输出分数:"""

        score = llm.invoke(prompt)
        print(f"📌 忠实度: {score.content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 主函数 ====================


def main():
    print("🚀 RAG 评估指标")
    print("=" * 60)

    evaluation_dimensions()
    retrieval_metrics()
    generation_metrics()

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：11-project-enterprise-qa.py")


if __name__ == "__main__":
    main()
