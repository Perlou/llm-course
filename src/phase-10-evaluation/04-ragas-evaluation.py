"""
Ragas 评估框架
=============

学习目标：
    1. 理解 Ragas 的核心评估指标
    2. 使用 Ragas 评估 RAG 系统
    3. 解读评估结果并优化

核心概念：
    - Faithfulness：忠实度
    - Answer Relevancy：回答相关性
    - Context Precision/Recall：上下文精确率/召回率

环境要求：
    - pip install ragas datasets
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Ragas 简介 ====================


def introduction():
    """Ragas 简介"""
    print("=" * 60)
    print("第一部分：Ragas 简介")
    print("=" * 60)

    print("""
    📌 Ragas 是什么？
    ┌─────────────────────────────────────────────────────────┐
    │  Ragas (RAG Assessment) 是专门用于评估 RAG 系统的框架   │
    │  提供了一套标准化的评估指标，无需人工标注参考答案       │
    └─────────────────────────────────────────────────────────┘

    📌 核心评估指标：
    ┌──────────────────┬────────────────────────────────────┐
    │ Faithfulness     │ 回答是否忠实于检索到的上下文       │
    │ Answer Relevancy │ 回答与问题的相关程度               │
    │ Context Precision│ 检索结果中相关内容的比例           │
    │ Context Recall   │ 正确答案被检索上下文覆盖的程度     │
    └──────────────────┴────────────────────────────────────┘

    📌 评估流程：
    问题 → RAG 系统 → 回答 + 上下文 → Ragas 评估 → 指标分数
    """)


# ==================== 第二部分：核心指标详解 ====================


def core_metrics():
    """核心指标详解"""
    print("\n" + "=" * 60)
    print("第二部分：核心指标详解")
    print("=" * 60)

    print("""
    📌 Faithfulness（忠实度）
    ┌─────────────────────────────────────────────────────────┐
    │  定义：回答中的声明是否能从上下文中推断出来             │
    │  计算：(可从上下文推断的声明数) / (回答中的总声明数)    │
    │  范围：0-1，越高越好                                   │
    │  意义：检测幻觉，确保回答基于事实                       │
    └─────────────────────────────────────────────────────────┘

    📌 Answer Relevancy（回答相关性）
    ┌─────────────────────────────────────────────────────────┐
    │  定义：回答与问题的语义相关程度                         │
    │  计算：生成问题与原问题的相似度                         │
    │  范围：0-1，越高越好                                   │
    │  意义：确保回答切题，没有答非所问                       │
    └─────────────────────────────────────────────────────────┘

    📌 Context Precision（上下文精确率）
    ┌─────────────────────────────────────────────────────────┐
    │  定义：检索结果中与回答相关的内容比例                   │
    │  意义：评估检索质量，避免噪声干扰                       │
    └─────────────────────────────────────────────────────────┘

    📌 Context Recall（上下文召回率）
    ┌─────────────────────────────────────────────────────────┐
    │  定义：正确答案中的信息被检索上下文覆盖的程度           │
    │  意义：确保检索到足够的相关信息                         │
    └─────────────────────────────────────────────────────────┘
    """)


# ==================== 第三部分：使用 Ragas ====================


def using_ragas():
    """使用 Ragas"""
    print("\n" + "=" * 60)
    print("第三部分：使用 Ragas 评估")
    print("=" * 60)

    code = """
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
from datasets import Dataset

# 准备评估数据
eval_data = {
    "question": [
        "什么是 RAG？",
        "LangChain 有什么用？"
    ],
    "answer": [
        "RAG 是检索增强生成技术，结合检索和生成来回答问题。",
        "LangChain 是一个用于构建 LLM 应用的框架。"
    ],
    "contexts": [
        ["RAG（Retrieval Augmented Generation）是一种将信息检索与文本生成相结合的技术。"],
        ["LangChain 是一个开源框架，用于开发由语言模型驱动的应用程序。"]
    ],
    "ground_truth": [  # 可选，用于 context_recall
        "RAG 是检索增强生成，结合检索系统和大语言模型。",
        "LangChain 是构建 LLM 应用的开源框架。"
    ]
}

dataset = Dataset.from_dict(eval_data)

# 运行评估
result = evaluate(
    dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall
    ]
)

print(result)
# 输出示例：
# {'faithfulness': 0.95, 'answer_relevancy': 0.88, ...}
"""
    print(code)


# ==================== 第四部分：评估 RAG 系统 ====================


def evaluate_rag_system():
    """评估 RAG 系统"""
    print("\n" + "=" * 60)
    print("第四部分：评估完整 RAG 系统")
    print("=" * 60)

    code = '''
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from datasets import Dataset

class RAGEvaluator:
    """RAG 系统评估器"""

    def __init__(self, rag_system):
        self.rag_system = rag_system

    def prepare_dataset(self, test_questions: list) -> Dataset:
        """准备评估数据集"""
        data = {
            "question": [],
            "answer": [],
            "contexts": []
        }

        for question in test_questions:
            # 调用 RAG 系统
            result = self.rag_system.query(question)

            data["question"].append(question)
            data["answer"].append(result["answer"])
            data["contexts"].append(result["retrieved_docs"])

        return Dataset.from_dict(data)

    def evaluate(self, test_questions: list) -> dict:
        """评估 RAG 系统"""
        dataset = self.prepare_dataset(test_questions)

        result = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy]
        )

        return {
            "faithfulness": result["faithfulness"],
            "answer_relevancy": result["answer_relevancy"],
            "overall": (result["faithfulness"] + result["answer_relevancy"]) / 2
        }

# 使用示例
# evaluator = RAGEvaluator(my_rag_system)
# scores = evaluator.evaluate(["问题1", "问题2", ...])
'''
    print(code)


# ==================== 第五部分：结果解读与优化 ====================


def interpretation():
    """结果解读与优化"""
    print("\n" + "=" * 60)
    print("第五部分：结果解读与优化")
    print("=" * 60)

    print("""
    📌 如何解读评估结果：
    ┌─────────────────────────────────────────────────────────┐
    │ 指标低的可能原因       │ 优化方向                      │
    ├─────────────────────────────────────────────────────────┤
    │ Faithfulness 低       │ 检查幻觉，增强上下文约束       │
    │                       │ 使用更强的提示词约束           │
    ├─────────────────────────────────────────────────────────┤
    │ Answer Relevancy 低   │ 优化生成 prompt                │
    │                       │ 检查问题理解是否正确           │
    ├─────────────────────────────────────────────────────────┤
    │ Context Precision 低  │ 优化检索模型/重排序            │
    │                       │ 调整 top_k 参数                │
    ├─────────────────────────────────────────────────────────┤
    │ Context Recall 低     │ 扩大检索范围                   │
    │                       │ 优化文档切分策略               │
    └─────────────────────────────────────────────────────────┘

    📌 优化建议：
    1. Faithfulness 低 → 加强 prompt 约束，使用引用格式
    2. Relevancy 低 → 优化问题改写，使用 HyDE
    3. Precision 低 → 添加 Reranker
    4. Recall 低 → 使用混合检索，增加召回数量
    """)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：使用 Ragas 评估你的 RAG 系统

        ✅ 参考答案：
        ```python
        from ragas import evaluate
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        )
        from datasets import Dataset
        
        class RAGEvaluator:
            '''RAG 系统 Ragas 评估器'''
            
            def __init__(self, rag_system):
                self.rag_system = rag_system
                self.metrics = [
                    faithfulness,
                    answer_relevancy,
                    context_precision,
                    context_recall
                ]
            
            def collect_data(
                self, 
                questions: list,
                ground_truths: list = None
            ) -> Dataset:
                '''收集评估数据'''
                data = {
                    "question": [],
                    "answer": [],
                    "contexts": []
                }
                
                if ground_truths:
                    data["ground_truth"] = []
                
                for i, q in enumerate(questions):
                    result = self.rag_system.query(q)
                    data["question"].append(q)
                    data["answer"].append(result["answer"])
                    data["contexts"].append(result["contexts"])
                    
                    if ground_truths:
                        data["ground_truth"].append(ground_truths[i])
                
                return Dataset.from_dict(data)
            
            def evaluate(
                self, 
                questions: list,
                ground_truths: list = None
            ) -> dict:
                '''运行评估'''
                dataset = self.collect_data(questions, ground_truths)
                
                result = evaluate(
                    dataset,
                    metrics=self.metrics
                )
                
                return {
                    "faithfulness": result["faithfulness"],
                    "answer_relevancy": result["answer_relevancy"],
                    "context_precision": result["context_precision"],
                    "context_recall": result["context_recall"],
                    "overall": (
                        result["faithfulness"] + 
                        result["answer_relevancy"]
                    ) / 2
                }
        
        # 使用示例
        # evaluator = RAGEvaluator(my_rag)
        # questions = ["什么是 RAG？", "LangChain 有什么用？"]
        # scores = evaluator.evaluate(questions)
        # print(f"Faithfulness: {scores['faithfulness']:.2f}")
        ```
    
    练习 2：根据评估结果优化 RAG 系统并重新评估

        ✅ 参考答案：
        ```python
        class RAGOptimizer:
            '''基于评估结果优化 RAG'''
            
            def __init__(self, rag_system, evaluator):
                self.rag = rag_system
                self.evaluator = evaluator
            
            def optimize_based_on_scores(
                self, 
                scores: dict,
                test_questions: list
            ) -> dict:
                '''根据评分优化'''
                optimizations = []
                
                # 1. Faithfulness 低 → 增强提示词约束
                if scores["faithfulness"] < 0.7:
                    self.rag.update_prompt(
                        "仅基于上下文回答，不要添加额外信息。"
                        "如果上下文不足，明确说明。"
                    )
                    optimizations.append("增强忠实度约束")
                
                # 2. Context Precision 低 → 添加 Reranker
                if scores["context_precision"] < 0.7:
                    self.rag.add_reranker()
                    optimizations.append("添加 Reranker")
                
                # 3. Context Recall 低 → 增加召回数量
                if scores["context_recall"] < 0.7:
                    self.rag.update_config(top_k=10)
                    self.rag.enable_hybrid_search()
                    optimizations.append("扩大召回范围")
                
                # 4. Answer Relevancy 低 → 优化问题改写
                if scores["answer_relevancy"] < 0.7:
                    self.rag.enable_query_rewrite()
                    optimizations.append("启用查询改写")
                
                # 重新评估
                new_scores = self.evaluator.evaluate(test_questions)
                
                return {
                    "before": scores,
                    "after": new_scores,
                    "optimizations": optimizations,
                    "improvement": {
                        k: new_scores[k] - scores[k]
                        for k in scores if k in new_scores
                    }
                }
        ```

    思考题：为什么 Ragas 不需要人工标注的参考答案？

        ✅ 答：
        1. LLM 作为评判 - 使用 LLM 分析回答与上下文的关系
        2. 声明级检验 - 将回答分解为声明，逐条验证是否有上下文支持
        3. 自洽性验证 - 通过生成问题再比较的方式评估相关性
        4. 自动化流程 - 整个评估过程无需人工干预
        5. 但注意：Context Recall 仍需要 ground_truth 来计算召回率
    """)


def main():
    introduction()
    core_metrics()
    using_ragas()
    evaluate_rag_system()
    interpretation()
    exercises()
    print("\n课程完成！下一步：05-contextual-relevance.py")


if __name__ == "__main__":
    main()
