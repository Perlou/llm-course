"""
提示词优化
==========

学习目标：
    1. 理解提示词优化的方法
    2. 使用自动化工具优化提示词
    3. 建立提示词迭代流程

核心概念：
    - Prompt Engineering：提示词工程
    - Automatic Prompt Optimization：自动提示词优化
    - A/B Testing：对比测试

环境要求：
    - pip install google-generativeai
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：提示词优化概述 ====================


def introduction():
    """提示词优化概述"""
    print("=" * 60)
    print("第一部分：提示词优化概述")
    print("=" * 60)

    print("""
    📌 为什么需要优化提示词？
    ┌─────────────────────────────────────────────────────────┐
    │  • 好的提示词可以显著提升模型表现                       │
    │  • 减少幻觉，提高准确性                                 │
    │  • 降低 token 消耗，节省成本                            │
    └─────────────────────────────────────────────────────────┘

    📌 优化维度：
    ┌──────────────┬────────────────────────────────────────┐
    │ 结构优化     │ 清晰的格式、分段、示例                 │
    │ 内容优化     │ 精确的指令、必要的上下文               │
    │ 约束优化     │ 输出格式、长度限制、风格要求           │
    │ 效率优化     │ 精简表达、减少冗余                     │
    └──────────────┴────────────────────────────────────────┘

    📌 优化流程：
    设计 → 测试 → 评估 → 迭代 → 部署
    """)


# ==================== 第二部分：提示词优化技巧 ====================


def optimization_techniques():
    """提示词优化技巧"""
    print("\n" + "=" * 60)
    print("第二部分：提示词优化技巧")
    print("=" * 60)

    print("""
    📌 结构化提示词模板：
    ```
    # 角色定义
    你是一个专业的{role}。

    # 任务说明
    你的任务是{task}。

    # 输入格式
    输入：{input_format}

    # 输出要求
    请按以下格式输出：
    {output_format}

    # 约束条件
    - 约束1
    - 约束2

    # 示例（可选）
    输入：{example_input}
    输出：{example_output}
    ```

    📌 常用优化技巧：
    1. 明确角色和专业背景
    2. 分步骤说明任务
    3. 提供正确和错误的示例
    4. 使用分隔符区分内容
    5. 明确输出格式要求
    """)

    code = '''
# 优化前
prompt_v1 = "回答用户问题：{question}"

# 优化后
prompt_v2 = """
你是一个专业的技术问答助手。

请根据以下信息回答用户问题：
- 仅基于提供的上下文回答
- 如果信息不足，明确说明
- 使用简洁、专业的语言

上下文：
{context}

问题：{question}

请用 2-3 句话简洁回答：
"""
'''
    print(code)


# ==================== 第三部分：自动提示词优化 ====================


def automatic_optimization():
    """自动提示词优化"""
    print("\n" + "=" * 60)
    print("第三部分：自动提示词优化")
    print("=" * 60)

    code = '''
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

META_PROMPT = """
你是一个提示词优化专家。请优化以下提示词以提高效果。

原始提示词：
{original_prompt}

期望改进：
{improvement_goal}

历史测试结果（可选）：
{test_results}

请输出优化后的提示词，并解释改进点。
"""

def optimize_prompt(
    original_prompt: str,
    improvement_goal: str,
    test_results: str = ""
) -> str:
    """使用 LLM 优化提示词"""
    prompt = META_PROMPT.format(
        original_prompt=original_prompt,
        improvement_goal=improvement_goal,
        test_results=test_results
    )

    response = model.generate_content(prompt)
    return response.text

# 使用示例
original = "回答问题：{question}"
goal = "减少幻觉，提高准确性，确保回答基于上下文"
optimized = optimize_prompt(original, goal)
'''
    print(code)


# ==================== 第四部分：A/B 测试框架 ====================


def ab_testing():
    """A/B 测试框架"""
    print("\n" + "=" * 60)
    print("第四部分：A/B 测试框架")
    print("=" * 60)

    code = '''
class PromptABTester:
    """提示词 A/B 测试框架"""

    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.results = {}

    def run_test(
        self,
        prompt_a: str,
        prompt_b: str,
        test_cases: list,
        model: str = "gpt-4"
    ) -> dict:
        """运行 A/B 测试"""
        results_a = []
        results_b = []

        for case in test_cases:
            # 测试 Prompt A
            response_a = self._generate(prompt_a, case, model)
            score_a = self.evaluator.evaluate(case, response_a)
            results_a.append(score_a)

            # 测试 Prompt B
            response_b = self._generate(prompt_b, case, model)
            score_b = self.evaluator.evaluate(case, response_b)
            results_b.append(score_b)

        return {
            "prompt_a": {
                "avg_score": sum(results_a) / len(results_a),
                "scores": results_a
            },
            "prompt_b": {
                "avg_score": sum(results_b) / len(results_b),
                "scores": results_b
            },
            "winner": "A" if sum(results_a) > sum(results_b) else "B"
        }

    def iterative_optimization(
        self,
        initial_prompt: str,
        test_cases: list,
        iterations: int = 3
    ) -> str:
        """迭代优化提示词"""
        current_prompt = initial_prompt

        for i in range(iterations):
            # 生成变体
            variant = optimize_prompt(current_prompt, "提高整体效果")

            # A/B 测试
            result = self.run_test(current_prompt, variant, test_cases)

            # 选择更好的
            if result["winner"] == "B":
                current_prompt = variant
                print(f"迭代 {i+1}: 新提示词胜出")
            else:
                print(f"迭代 {i+1}: 保持当前提示词")

        return current_prompt
'''
    print(code)


# ==================== 第五部分：最佳实践 ====================


def best_practices():
    """最佳实践"""
    print("\n" + "=" * 60)
    print("第五部分：最佳实践")
    print("=" * 60)

    print("""
    📌 提示词优化检查清单：
    ✅ 角色定义清晰
    ✅ 任务说明明确
    ✅ 包含必要的上下文
    ✅ 输出格式规范
    ✅ 有约束条件
    ✅ 提供示例（Few-shot）

    📌 常见问题与解决：
    ┌──────────────────┬────────────────────────────────────┐
    │ 问题             │ 解决方案                           │
    ├──────────────────┼────────────────────────────────────┤
    │ 回答过于冗长     │ 添加长度限制："用2句话回答"        │
    │ 格式不统一       │ 提供明确的输出模板                 │
    │ 幻觉严重         │ 强调"仅基于提供的信息"             │
    │ 风格不一致       │ 添加风格说明和示例                 │
    └──────────────────┴────────────────────────────────────┘
    """)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：优化一个 RAG 系统的生成提示词

        ✅ 参考答案：
        ```python
        class RAGPromptOptimizer:
            '''RAG 提示词优化器'''
            
            # 原始版本
            v1_basic = '''
回答问题：{question}
参考信息：{context}
'''
            
            # 优化版 V2 - 添加角色和约束
            v2_constrained = '''
你是一个专业的问答助手。请根据提供的参考信息回答问题。

规则：
- 仅使用参考信息中的内容回答
- 如果信息不足，明确说明
- 保持回答简洁，2-3句话

参考信息：
{context}

问题：{question}

回答：
'''
            
            # 优化版 V3 - 添加示例和格式
            v3_with_example = '''
你是一个专业的问答助手。

【任务】根据参考信息回答用户问题
【规则】
1. 仅使用参考信息回答
2. 信息不足时说"无法确定"
3. 引用关键来源

【示例】
问题：Python 是什么？
参考：Python 是一种高级编程语言，创建于1991年。
回答：Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年创建。[来源：参考信息]

【当前任务】
参考信息：
{context}

问题：{question}

回答：
'''
            
            def optimize_iteratively(
                self,
                initial_prompt: str,
                test_cases: list,
                evaluator,
                iterations: int = 3
            ) -> str:
                '''迭代优化'''
                current = initial_prompt
                best_score = 0
                
                for i in range(iterations):
                    # 评估当前版本
                    score = self._evaluate_prompt(current, test_cases, evaluator)
                    
                    if score > best_score:
                        best_score = score
                        best_prompt = current
                    
                    # 生成改进版本
                    current = self._improve_prompt(current, score)
                
                return best_prompt
        ```
    
    练习 2：使用 A/B 测试比较不同版本的效果

        ✅ 参考答案：
        ```python
        from typing import List, Dict
        import random
        
        class PromptABTest:
            '''Prompt A/B 测试框架'''
            
            def __init__(self, model, evaluator):
                self.model = model
                self.evaluator = evaluator
            
            def run_test(
                self,
                prompt_a: str,
                prompt_b: str,
                test_cases: List[Dict],
                metrics: List[str] = ['relevancy', 'faithfulness']
            ) -> Dict:
                '''运行 A/B 测试'''
                results = {'A': [], 'B': []}
                
                for case in test_cases:
                    # 测试 Prompt A
                    resp_a = self.model.generate(
                        prompt_a.format(**case)
                    )
                    score_a = self.evaluator.evaluate(
                        case['context'], resp_a
                    )
                    results['A'].append(score_a)
                    
                    # 测试 Prompt B
                    resp_b = self.model.generate(
                        prompt_b.format(**case)
                    )
                    score_b = self.evaluator.evaluate(
                        case['context'], resp_b
                    )
                    results['B'].append(score_b)
                
                return {
                    'A': {
                        'avg': sum(results['A']) / len(results['A']),
                        'scores': results['A']
                    },
                    'B': {
                        'avg': sum(results['B']) / len(results['B']),
                        'scores': results['B']
                    },
                    'winner': 'A' if sum(results['A']) > sum(results['B']) else 'B',
                    'improvement': abs(
                        sum(results['A']) - sum(results['B'])
                    ) / len(test_cases)
                }
            
            def statistical_significance(
                self, 
                results: Dict
            ) -> bool:
                '''检验统计显著性'''
                from scipy.stats import ttest_ind
                t_stat, p_value = ttest_ind(
                    results['A']['scores'],
                    results['B']['scores']
                )
                return p_value < 0.05  # 5% 显著性水平
        ```

    思考题：自动提示词优化有什么局限性？

        ✅ 答：
        1. 目标偏差 - 优化目标可能与实际业务目标不一致
        2. 测试集局限 - 测试集可能不够全面，导致过拟合
        3. 复杂度膨胀 - 优化后的提示词可能过于冗长
        4. 成本增加 - 复杂提示词消耗更多 token
        5. 可解释性差 - 自动生成的提示词可能难以理解
        6. 上下文依赖 - 不同场景可能需要不同的提示词
    """)


def main():
    introduction()
    optimization_techniques()
    automatic_optimization()
    ab_testing()
    best_practices()
    exercises()
    print("\n课程完成！下一步：08-cost-optimization.py")


if __name__ == "__main__":
    main()
