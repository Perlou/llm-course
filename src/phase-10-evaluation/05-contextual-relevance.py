"""
上下文相关性评估
===============

学习目标：
    1. 理解上下文相关性的重要性
    2. 实现上下文精确率和召回率计算
    3. 优化检索结果的相关性

核心概念：
    - Context Precision：检索精确率
    - Context Recall：检索召回率
    - Semantic Similarity：语义相似度

环境要求：
    - pip install sentence-transformers numpy
"""

import numpy as np
from typing import List


# ==================== 第一部分：上下文相关性概念 ====================


def introduction():
    """上下文相关性概念"""
    print("=" * 60)
    print("第一部分：上下文相关性概念")
    print("=" * 60)

    print("""
    📌 为什么关注上下文相关性？
    ┌─────────────────────────────────────────────────────────┐
    │  RAG 系统的效果很大程度取决于检索质量                   │
    │  • 检索到不相关内容 → 噪声干扰，降低回答质量            │
    │  • 检索不到相关内容 → 信息缺失，无法正确回答            │
    └─────────────────────────────────────────────────────────┘

    📌 核心指标：
    ┌──────────────────┬────────────────────────────────────┐
    │ Context Precision│ 检索结果中相关内容的比例           │
    │                  │ = 相关文档数 / 检索文档总数         │
    ├──────────────────┼────────────────────────────────────┤
    │ Context Recall   │ 相关内容被检索到的程度             │
    │                  │ = 检索到的相关信息 / 所需总信息    │
    └──────────────────┴────────────────────────────────────┘

    📌 评估流程：
    问题 → 检索文档 → 计算相关性 → 精确率/召回率
    """)


# ==================== 第二部分：语义相似度计算 ====================


def semantic_similarity():
    """语义相似度计算"""
    print("\n" + "=" * 60)
    print("第二部分：语义相似度计算")
    print("=" * 60)

    code = '''
from sentence_transformers import SentenceTransformer
import numpy as np

# 加载嵌入模型
model = SentenceTransformer('all-MiniLM-L6-v2')

def compute_similarity(text1: str, text2: str) -> float:
    """计算两个文本的语义相似度"""
    embeddings = model.encode([text1, text2])
    similarity = np.dot(embeddings[0], embeddings[1]) / (
        np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
    )
    return float(similarity)

def compute_relevance_scores(question: str, contexts: list) -> list:
    """计算问题与每个上下文的相关性分数"""
    question_embedding = model.encode([question])[0]
    context_embeddings = model.encode(contexts)

    scores = []
    for ctx_emb in context_embeddings:
        similarity = np.dot(question_embedding, ctx_emb) / (
            np.linalg.norm(question_embedding) * np.linalg.norm(ctx_emb)
        )
        scores.append(float(similarity))

    return scores

# 使用示例
question = "什么是机器学习？"
contexts = [
    "机器学习是人工智能的一个分支，让计算机从数据中学习。",
    "今天天气很好，适合散步。",
    "深度学习是机器学习的一种方法。"
]
scores = compute_relevance_scores(question, contexts)
# [0.72, 0.15, 0.68] - 第1和第3个文档相关
'''
    print(code)


# ==================== 第三部分：上下文精确率 ====================


def context_precision():
    """上下文精确率"""
    print("\n" + "=" * 60)
    print("第三部分：上下文精确率 (Context Precision)")
    print("=" * 60)

    code = '''
def calculate_context_precision(
    question: str,
    contexts: list,
    threshold: float = 0.5
) -> dict:
    """
    计算上下文精确率
    - 检索到的文档中有多少是真正相关的
    """
    scores = compute_relevance_scores(question, contexts)
    relevant_count = sum(1 for s in scores if s >= threshold)
    total_count = len(contexts)

    precision = relevant_count / total_count if total_count > 0 else 0

    return {
        "precision": precision,
        "relevant_count": relevant_count,
        "total_count": total_count,
        "scores": scores
    }

# 使用示例
result = calculate_context_precision(
    question="什么是 RAG？",
    contexts=[
        "RAG 是检索增强生成技术...",  # 相关
        "今天股市上涨...",           # 不相关
        "检索是 RAG 的核心组件..."    # 相关
    ]
)
# precision = 2/3 = 0.67
'''
    print(code)


# ==================== 第四部分：上下文召回率 ====================


def context_recall():
    """上下文召回率"""
    print("\n" + "=" * 60)
    print("第四部分：上下文召回率 (Context Recall)")
    print("=" * 60)

    code = '''
def calculate_context_recall(
    answer: str,
    contexts: list,
    ground_truth: str
) -> dict:
    """
    计算上下文召回率
    - 正确答案中的信息有多少被检索上下文覆盖

    需要: 标准答案 (ground_truth)
    """
    # 将标准答案分解为关键信息点
    truth_sentences = ground_truth.split('。')
    truth_sentences = [s.strip() for s in truth_sentences if s.strip()]

    # 计算每个信息点是否被上下文覆盖
    covered = 0
    context_text = ' '.join(contexts)

    for sentence in truth_sentences:
        # 使用语义相似度判断是否覆盖
        similarity = compute_similarity(sentence, context_text)
        if similarity >= 0.6:  # 阈值
            covered += 1

    recall = covered / len(truth_sentences) if truth_sentences else 0

    return {
        "recall": recall,
        "covered": covered,
        "total_points": len(truth_sentences)
    }
'''
    print(code)


# ==================== 第五部分：优化策略 ====================


def optimization():
    """优化策略"""
    print("\n" + "=" * 60)
    print("第五部分：优化上下文相关性")
    print("=" * 60)

    print("""
    📌 提高 Precision 的方法：
    ┌─────────────────────────────────────────────────────────┐
    │ 1. 使用 Reranker 重排序                                │
    │ 2. 减少 top_k，只保留最相关的                          │
    │ 3. 设置相似度阈值过滤                                  │
    │ 4. 使用更好的嵌入模型                                  │
    └─────────────────────────────────────────────────────────┘

    📌 提高 Recall 的方法：
    ┌─────────────────────────────────────────────────────────┐
    │ 1. 增加 top_k 召回数量                                 │
    │ 2. 使用混合检索（关键词 + 向量）                       │
    │ 3. 查询扩展/改写                                       │
    │ 4. 优化文档切分策略                                    │
    └─────────────────────────────────────────────────────────┘

    📌 Precision vs Recall 权衡：
    - 高 Precision，低 Recall → 信息不全
    - 低 Precision，高 Recall → 噪声过多
    - 目标：两者平衡 (F1 Score)
    """)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现上下文相关性评估函数

        ✅ 参考答案：
        ```python
        from sentence_transformers import SentenceTransformer
        import numpy as np
        from typing import List, Dict
        
        class ContextRelevanceEvaluator:
            '''上下文相关性评估器'''
            
            def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
                self.model = SentenceTransformer(model_name)
            
            def compute_similarity(
                self, 
                text1: str, 
                text2: str
            ) -> float:
                '''计算语义相似度'''
                emb = self.model.encode([text1, text2])
                return float(np.dot(emb[0], emb[1]) / (
                    np.linalg.norm(emb[0]) * np.linalg.norm(emb[1])
                ))
            
            def evaluate_precision(
                self,
                question: str,
                contexts: List[str],
                threshold: float = 0.5
            ) -> Dict:
                '''评估上下文精确率'''
                q_emb = self.model.encode([question])[0]
                ctx_embs = self.model.encode(contexts)
                
                scores = []
                for ctx_emb in ctx_embs:
                    sim = np.dot(q_emb, ctx_emb) / (
                        np.linalg.norm(q_emb) * np.linalg.norm(ctx_emb)
                    )
                    scores.append(float(sim))
                
                relevant = sum(1 for s in scores if s >= threshold)
                
                return {
                    'precision': relevant / len(contexts),
                    'scores': scores,
                    'relevant_count': relevant,
                    'total': len(contexts)
                }
            
            def evaluate_recall(
                self,
                contexts: List[str],
                ground_truth: str,
                threshold: float = 0.6
            ) -> Dict:
                '''评估上下文召回率'''
                truth_sentences = [s.strip() for s in ground_truth.split('。') if s.strip()]
                context_text = ' '.join(contexts)
                
                covered = 0
                for sentence in truth_sentences:
                    sim = self.compute_similarity(sentence, context_text)
                    if sim >= threshold:
                        covered += 1
                
                return {
                    'recall': covered / len(truth_sentences) if truth_sentences else 0,
                    'covered': covered,
                    'total_points': len(truth_sentences)
                }
            
            def evaluate_f1(
                self,
                question: str,
                contexts: List[str],
                ground_truth: str
            ) -> Dict:
                '''计算 F1 分数'''
                p = self.evaluate_precision(question, contexts)['precision']
                r = self.evaluate_recall(contexts, ground_truth)['recall']
                
                f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
                
                return {'precision': p, 'recall': r, 'f1': f1}
        
        # 使用示例
        evaluator = ContextRelevanceEvaluator()
        result = evaluator.evaluate_f1(
            question="什么是 RAG？",
            contexts=["RAG 是检索增强生成...", "今天天气很好"],
            ground_truth="RAG 是检索增强生成技术，结合检索和生成"
        )
        print(f"F1: {result['f1']:.2f}")
        ```
    
    练习 2：对比不同 top_k 设置对 Precision/Recall 的影响

        ✅ 参考答案：
        ```python
        class TopKExperiment:
            '''top_k 实验'''
            
            def __init__(self, retriever, evaluator):
                self.retriever = retriever
                self.evaluator = evaluator
            
            def run_experiment(
                self,
                questions: List[str],
                ground_truths: List[str],
                k_values: List[int] = [1, 3, 5, 10, 20]
            ) -> Dict:
                '''运行 top_k 对比实验'''
                results = {}
                
                for k in k_values:
                    precisions, recalls = [], []
                    
                    for q, gt in zip(questions, ground_truths):
                        contexts = self.retriever.retrieve(q, top_k=k)
                        metrics = self.evaluator.evaluate_f1(q, contexts, gt)
                        precisions.append(metrics['precision'])
                        recalls.append(metrics['recall'])
                    
                    results[k] = {
                        'precision': sum(precisions) / len(precisions),
                        'recall': sum(recalls) / len(recalls),
                        'f1': 2 * results[k]['precision'] * results[k]['recall'] / (
                            results[k]['precision'] + results[k]['recall'] + 1e-6
                        )
                    }
                
                # 找到最优 k
                best_k = max(results.keys(), key=lambda k: results[k]['f1'])
                
                return {
                    'results': results,
                    'best_k': best_k,
                    'best_f1': results[best_k]['f1']
                }
        
        # 预期结果趋势：
        # k ↑ → Recall ↑, Precision ↓
        # 需要找到 F1 最优的 k 值
        ```

    思考题：如何在 Precision 和 Recall 之间取得平衡？

        ✅ 答：
        1. 两段式召回 - 先大量召回（高 Recall），再 Rerank 精选（高 Precision）
        2. 动态 k - 根据问题复杂度动态调整 top_k
        3. 阈值过滤 - 设置相似度阈值，过滤低质量结果
        4. 混合检索 - 结合关键词和向量检索的优势
        5. F1 优化 - 选择 F1 最高的配置作为平衡点
    """)


def main():
    introduction()
    semantic_similarity()
    context_precision()
    context_recall()
    optimization()
    exercises()
    print("\n课程完成！下一步：06-faithfulness.py")


if __name__ == "__main__":
    main()
