"""
LLM 作为评判者
=============

学习目标：
    1. 理解 LLM-as-Judge 的原理和优势
    2. 实现单模型评估和成对比较
    3. 掌握评估 prompt 设计技巧

核心概念：
    - LLM-as-Judge：用 LLM 评估 LLM
    - 单点评分：对单个回复打分
    - 成对比较：比较两个回复的优劣

环境要求：
    - pip install openai
    - 需要 Google API Key
"""

import json
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：LLM-as-Judge 概述 ====================


def introduction():
    """LLM-as-Judge 概述"""
    print("=" * 60)
    print("第一部分：LLM-as-Judge 概述")
    print("=" * 60)

    print("""
    📌 为什么使用 LLM 作为评判者？
    ┌─────────────────────────────────────────────────────────┐
    │  • 人工评估成本高、速度慢                             │
    │  • 自动指标难以评估开放式生成                          │
    │  • LLM 可以理解语义和意图                              │
    │  • 可扩展性强，支持大规模评估                          │
    └─────────────────────────────────────────────────────────┘

    📌 评估模式：
    ┌────────────────┬─────────────────────────────────────┐
    │   单点评分     │ 对单个回复按多个维度打分 (1-10)      │
    ├────────────────┼─────────────────────────────────────┤
    │   成对比较     │ 比较两个回复，选择更好的一个          │
    ├────────────────┼─────────────────────────────────────┤
    │   参考答案比较 │ 与标准答案对比打分                   │
    └────────────────┴─────────────────────────────────────┘

    📌 常用评判模型：
    - GPT-4 (最常用，效果好)
    - Claude 3.5
    - 开源模型 (需要足够大)
    """)


# ==================== 第二部分：单点评分 ====================


def single_point_scoring():
    """单点评分"""
    print("\n" + "=" * 60)
    print("第二部分：单点评分")
    print("=" * 60)

    code = '''
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

JUDGE_PROMPT = """
你是一个专业的评估助手。请根据以下标准评估AI助手的回复质量。

评估标准：
1. 准确性 (1-10): 回答是否事实正确
2. 相关性 (1-10): 回答是否切题
3. 完整性 (1-10): 回答是否全面
4. 清晰度 (1-10): 表达是否清晰易懂
5. 有用性 (1-10): 对用户是否有实际帮助

用户问题：
{question}

AI回复：
{response}

请按以下JSON格式输出评分：
{{
    "accuracy": <score>,
    "relevance": <score>,
    "completeness": <score>,
    "clarity": <score>,
    "helpfulness": <score>,
    "overall": <score>,
    "explanation": "<简要解释>"
}}
"""

def evaluate_single(question: str, response: str) -> dict:
    """单点评分评估"""
    prompt = JUDGE_PROMPT.format(question=question, response=response)

    result = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return json.loads(result.choices[0].message.content)

# 使用示例
# scores = evaluate_single(
#     "什么是机器学习？",
#     "机器学习是人工智能的一个分支..."
# )
'''
    print(code)


# ==================== 第三部分：成对比较 ====================


def pairwise_comparison():
    """成对比较"""
    print("\n" + "=" * 60)
    print("第三部分：成对比较")
    print("=" * 60)

    code = '''
PAIRWISE_PROMPT = """
请比较以下两个AI助手的回复，判断哪个更好。

用户问题：{question}

回复A：
{response_a}

回复B：
{response_b}

请从以下方面比较：
1. 准确性和事实正确性
2. 回答的完整性和深度
3. 表达的清晰度
4. 对用户的帮助程度

请选择更好的回复，并解释原因。
输出格式：
{{
    "winner": "A" 或 "B" 或 "tie",
    "explanation": "<详细原因>"
}}
"""

def pairwise_compare(question: str, response_a: str, response_b: str) -> dict:
    """成对比较评估"""
    prompt = PAIRWISE_PROMPT.format(
        question=question,
        response_a=response_a,
        response_b=response_b
    )

    result = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return json.loads(result.choices[0].message.content)

def evaluate_with_position_swap(question, response_a, response_b):
    """消除位置偏见的成对比较"""
    # 正向比较
    result1 = pairwise_compare(question, response_a, response_b)
    # 交换位置再比较
    result2 = pairwise_compare(question, response_b, response_a)

    # 综合判断
    if result1["winner"] == "A" and result2["winner"] == "B":
        return {"winner": "A", "confidence": "high"}
    elif result1["winner"] == "B" and result2["winner"] == "A":
        return {"winner": "B", "confidence": "high"}
    else:
        return {"winner": "tie", "confidence": "low"}
'''
    print(code)


# ==================== 第四部分：MT-Bench 风格评估 ====================


def mt_bench_style():
    """MT-Bench 风格评估"""
    print("\n" + "=" * 60)
    print("第四部分：MT-Bench 风格评估")
    print("=" * 60)

    code = '''
"""
MT-Bench: 多轮对话评估框架
- 80个高质量多轮对话问题
- 覆盖8个能力维度
"""

MT_BENCH_CATEGORIES = [
    "writing",      # 写作
    "roleplay",     # 角色扮演
    "extraction",   # 信息提取
    "reasoning",    # 推理
    "math",         # 数学
    "coding",       # 编程
    "knowledge",    # 知识
    "generic"       # 通用
]

class MTBenchEvaluator:
    def __init__(self, judge_model="gpt-4"):
        self.judge_model = judge_model

    def evaluate_turn(self, question, response, reference=None):
        """评估单轮对话"""
        prompt = f"""
请评估以下AI回复的质量，给出1-10分。

问题：{question}

回复：{response}

评分标准：
- 1-3: 差，答非所问或有明显错误
- 4-6: 中等，基本回答了问题
- 7-8: 好，回答准确且有帮助
- 9-10: 优秀，超出预期的高质量回答

输出格式：{{"score": <分数>, "reason": "<理由>"}}
"""
        result = model.generate_content(prompt)
        return json.loads(result.text)

    def evaluate_model(self, model, questions):
        """评估模型在所有问题上的表现"""
        scores_by_category = {cat: [] for cat in MT_BENCH_CATEGORIES}

        for q in questions:
            response = model.generate(q["prompt"])
            result = self.evaluate_turn(q["prompt"], response)
            scores_by_category[q["category"]].append(result["score"])

        # 计算平均分
        return {cat: sum(s)/len(s) for cat, s in scores_by_category.items() if s}
'''
    print(code)


# ==================== 第五部分：最佳实践 ====================


def best_practices():
    """最佳实践"""
    print("\n" + "=" * 60)
    print("第五部分：最佳实践")
    print("=" * 60)

    print("""
    📌 LLM-as-Judge 最佳实践：

    ✅ 评判模型选择
    - 使用比被评估模型更强的模型
    - GPT-4 是目前最常用的评判模型
    - 开源模型需要足够大 (70B+)

    ✅ Prompt 设计
    - 明确评估维度和标准
    - 使用结构化输出 (JSON)
    - 要求给出评分理由

    ✅ 消除偏见
    - 成对比较时交换位置
    - 多次评估取平均
    - 检测自我偏好

    ✅ 验证评估质量
    - 与人工评估对比
    - 计算评估一致性
    - 检查异常评分

    ⚠️ 注意事项
    - LLM 可能偏好自己的风格
    - 位置偏见（倾向选择第一个）
    - 冗长偏见（偏好长回复）
    """)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现一个完整的 LLM-as-Judge 评估器
    练习 2：对比不同评判模型的评估结果

    思考题：如何验证 LLM 评判的可靠性？
    答案：1. 与人工评估结果对比计算相关性
          2. 测试评估的一致性（重复评估）
          3. 检测位置偏见和自我偏好
    """)


def main():
    introduction()
    single_point_scoring()
    pairwise_comparison()
    mt_bench_style()
    best_practices()
    exercises()
    print("\n课程完成！下一步：04-ragas-evaluation.py")


if __name__ == "__main__":
    main()
