"""
Agent 类型对比
=============

学习目标：
    1. 了解不同类型的 Agent 架构
    2. 理解各类型的优缺点
    3. 根据场景选择合适的 Agent 类型

核心概念：
    - Zero-shot Agent：无需示例，直接推理
    - ReAct Agent：推理与行动交织
    - Plan-and-Execute Agent：先规划后执行
    - Self-Ask Agent：自问自答模式

前置知识：
    - 01-agent-fundamentals.py
    - 02-react-agent.py

环境要求：
    - pip install openai python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Agent 类型概览 ====================


def agent_types_overview():
    """Agent 类型概览"""
    print("=" * 60)
    print("第一部分：Agent 类型概览")
    print("=" * 60)

    print("""
    主要 Agent 类型
    ───────────────
    
    │ 类型           │ 特点                          │
    ├────────────────┼───────────────────────────────┤
    │ Zero-shot      │ 单步决策，无需示例              │
    │ ReAct          │ 思考-行动-观察循环              │
    │ Plan-Execute   │ 先制定计划，再逐步执行          │
    │ Self-Ask       │ 自问自答，层层深入              │
    │ OpenAI Tools   │ 利用 Function Calling 特性    │
    
    选择依据：任务复杂度、是否需要规划、工具使用频率
    """)


# ==================== 第二部分：Zero-shot Agent ====================


def zero_shot_agent():
    """Zero-shot Agent"""
    print("\n" + "=" * 60)
    print("第二部分：Zero-shot Agent")
    print("=" * 60)

    print("""
    Zero-shot Agent：单步决策
    ─────────────────────────
    输入 → 分析 → 选择工具 → 执行 → 输出
    
    ✅ 简单快速、延迟低
    ❌ 不适合复杂多步任务
    """)

    class ZeroShotAgent:
        def __init__(self):
            self.tools = {
                "calculator": lambda x: str(eval(x, {"__builtins__": {}})),
                "weather": lambda x: f"{x}：晴，25°C",
            }

        def run(self, query: str) -> str:
            if any(op in query for op in ["+", "-", "*", "/"]):
                import re

                match = re.search(r"[\d+\-*/\s]+", query)
                return f"计算结果: {self.tools['calculator'](match.group())}"
            elif "天气" in query:
                return self.tools["weather"]("北京")
            return f"直接回答: {query}"

    agent = ZeroShotAgent()
    print(f"\n📌 测试: {agent.run('100 + 200')}")


# ==================== 第三部分：Plan-and-Execute Agent ====================


def plan_and_execute_agent():
    """Plan-and-Execute Agent"""
    print("\n" + "=" * 60)
    print("第三部分：Plan-and-Execute Agent")
    print("=" * 60)

    print("""
    Plan-and-Execute：先规划后执行
    ───────────────────────────────
    
    1. 规划阶段：制定完整计划
    2. 执行阶段：按计划逐步执行
    
    ✅ 有全局视野，适合长期任务
    ❌ 规划可能不够灵活
    """)

    class PlanExecuteAgent:
        def plan(self, task: str) -> list:
            return ["搜索资料", "整理信息", "撰写内容"]

        def run(self, task: str):
            print(f"\n任务: {task}")
            plan = self.plan(task)
            for i, step in enumerate(plan, 1):
                print(f"  步骤 {i}: {step}")

    agent = PlanExecuteAgent()
    agent.run("撰写 AI 报告")


# ==================== 第四部分：Self-Ask Agent ====================


def self_ask_agent():
    """Self-Ask Agent"""
    print("\n" + "=" * 60)
    print("第四部分：Self-Ask Agent")
    print("=" * 60)

    print("""
    Self-Ask：自问自答模式
    ──────────────────────
    
    原始问题: "A 和 B 谁更大？"
    ↓
    Sub-Q 1: "A 是多少？" → Answer 1
    Sub-Q 2: "B 是多少？" → Answer 2
    ↓
    Final Answer: 比较得出结论
    
    适用：需要多跳推理、比较类问题
    """)


# ==================== 第五部分：选择指南 ====================


def selection_guide():
    """类型选择指南"""
    print("\n" + "=" * 60)
    print("第五部分：选择指南")
    print("=" * 60)

    print("""
    │ 场景              │ 推荐类型          │
    ├───────────────────┼──────────────────┤
    │ 简单问答           │ Zero-shot        │
    │ 搜索 + 总结        │ ReAct            │
    │ 撰写长文档         │ Plan-and-Execute │
    │ 比较多个实体       │ Self-Ask         │
    """)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现 Self-Ask Agent

        ✅ 参考答案：
        ```python
        class SelfAskAgent:
            def __init__(self, llm, search_tool):
                self.llm = llm
                self.search = search_tool
            
            def run(self, question: str) -> str:
                '''Self-Ask 主循环'''
                context = f"问题：{question}\\n"
                
                for _ in range(5):  # 最多5轮
                    prompt = f'''
                    {context}
                    是否需要分解为子问题？如果是，写出子问题；
                    如果可以回答，直接给出答案。
                    '''
                    response = self.llm.invoke(prompt).content
                    
                    if "子问题" in response:
                        sub_q = self.extract_sub_question(response)
                        answer = self.search(sub_q)
                        context += f"子问题：{sub_q}\\n答案：{answer}\\n"
                    else:
                        return response
                
                return "无法回答"
        ```

    练习 2：为 Plan-Execute 添加重规划能力

        ✅ 参考答案：
        ```python
        class AdaptivePlanExecuteAgent:
            def replan(self, original_plan, failed_step, error):
                '''根据失败情况重新规划'''
                prompt = f'''
                原计划：{original_plan}
                失败步骤：{failed_step}
                错误信息：{error}
                
                请生成新的执行计划：
                '''
                new_plan = self.llm.invoke(prompt).content
                return self.parse_plan(new_plan)
            
            def execute_with_retry(self, plan):
                for i, step in enumerate(plan):
                    try:
                        result = self.execute_step(step)
                    except Exception as e:
                        # 重规划
                        remaining = plan[i:]
                        new_plan = self.replan(plan, step, str(e))
                        return self.execute_with_retry(new_plan)
                return result
        ```
    
    思考题：何时需要混合多种 Agent 类型？

        ✅ 答案：
        - 复杂任务需要先规划再执行（Plan-Execute + ReAct）
        - 多步骤任务需要分解子问题（Self-Ask + ReAct）
        - 不同子任务适合不同策略时
        - 需要兼顾效率和灵活性时
        
        示例：研究助手
        1. Plan-Execute：制定研究大纲
        2. Self-Ask：分解复杂问题
        3. ReAct：执行具体搜索和分析
    """)


def main():
    print("📊 Agent 类型对比")
    print("=" * 60)

    agent_types_overview()
    zero_shot_agent()
    plan_and_execute_agent()
    self_ask_agent()
    selection_guide()
    exercises()

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：04-tool-basics.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
