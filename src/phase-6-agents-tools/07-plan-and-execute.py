"""
计划执行 Agent
=============

学习目标：
    1. 理解 Plan-and-Execute 架构
    2. 实现任务规划器
    3. 实现步骤执行器

核心概念：
    - Planner：将任务分解为步骤
    - Executor：逐步执行计划
    - Replanner：根据执行结果调整计划

前置知识：
    - 01-06 所有 Agent 基础课程

环境要求：
    - pip install google-generativeai python-dotenv
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：架构概述 ====================


def architecture_overview():
    """架构概述"""
    print("=" * 60)
    print("第一部分：Plan-and-Execute 架构")
    print("=" * 60)

    print("""
    Plan-and-Execute 架构
    ─────────────────────
    
    ┌──────────────────────────────────────────────────────┐
    │                                                      │
    │   任务 ──→ [Planner] ──→ 计划                        │
    │                           │                          │
    │                           ▼                          │
    │              ┌────────────────────┐                  │
    │              │ 步骤1 → 步骤2 → ...  │                  │
    │              └─────────┬──────────┘                  │
    │                        │                             │
    │                        ▼                             │
    │                   [Executor]                         │
    │                        │                             │
    │              ┌────────┴────────┐                     │
    │              ▼                 ▼                     │
    │          执行成功           执行失败                   │
    │              │                 │                     │
    │              ▼                 ▼                     │
    │          下一步           [Replanner]                 │
    │                               │                      │
    │                               ▼                      │
    │                          调整计划                     │
    │                                                      │
    └──────────────────────────────────────────────────────┘
    
    优势：
    ✅ 全局视野，不会迷失方向
    ✅ 适合复杂长期任务
    ✅ 可预先优化计划
    
    劣势：
    ❌ 初始规划可能不够灵活
    ❌ 需要额外的重规划逻辑
    """)


# ==================== 第二部分：任务规划器 ====================


def task_planner():
    """任务规划器"""
    print("\n" + "=" * 60)
    print("第二部分：任务规划器 (Planner)")
    print("=" * 60)

    class Planner:
        """任务规划器"""

        PLAN_PROMPT = """
请将以下任务分解为可执行的步骤列表：

任务：{task}

要求：
1. 每个步骤应该简洁明确
2. 步骤按逻辑顺序排列
3. 返回 JSON 格式的步骤列表

输出格式：
["步骤1", "步骤2", ...]
"""

        def plan(self, task: str) -> List[str]:
            """生成执行计划（简化版）"""
            # 基于规则的简单规划
            if "研究" in task or "报告" in task:
                return [
                    "搜索相关资料和最新信息",
                    "整理和归纳关键信息",
                    "撰写报告大纲",
                    "填充详细内容",
                    "检查和优化",
                ]
            elif "代码" in task or "开发" in task:
                return [
                    "分析需求和设计方案",
                    "搭建基础框架",
                    "实现核心功能",
                    "添加错误处理",
                    "测试和调试",
                ]
            else:
                return ["理解任务需求", "收集必要信息", "执行核心操作", "验证结果"]

    planner = Planner()

    print("📌 规划示例 1：")
    task1 = "研究 AI Agent 最新进展并撰写报告"
    plan1 = planner.plan(task1)
    print(f"任务: {task1}")
    for i, step in enumerate(plan1, 1):
        print(f"  {i}. {step}")

    print("\n📌 规划示例 2：")
    task2 = "开发一个天气查询工具"
    plan2 = planner.plan(task2)
    print(f"任务: {task2}")
    for i, step in enumerate(plan2, 1):
        print(f"  {i}. {step}")


# ==================== 第三部分：步骤执行器 ====================


def step_executor():
    """步骤执行器"""
    print("\n" + "=" * 60)
    print("第三部分：步骤执行器 (Executor)")
    print("=" * 60)

    class Executor:
        """步骤执行器"""

        def __init__(self):
            self.tools = {
                "search": lambda q: f"搜索结果: {q}的相关信息...",
                "summarize": lambda t: f"总结: {t[:20]}...",
                "write": lambda t: f"已撰写: {t}",
            }

        def execute_step(self, step: str, context: Dict) -> Dict:
            """执行单个步骤"""
            print(f"  执行: {step}")

            # 简单的步骤-工具映射
            if "搜索" in step:
                result = self.tools["search"](step)
            elif "整理" in step or "归纳" in step:
                result = self.tools["summarize"](context.get("last_result", ""))
            elif "撰写" in step:
                result = self.tools["write"](step)
            else:
                result = f"完成: {step}"

            return {"success": True, "result": result}

    executor = Executor()

    print("📌 执行示例：")
    steps = ["搜索 AI 最新进展", "整理关键信息", "撰写报告"]
    context = {}

    for step in steps:
        result = executor.execute_step(step, context)
        context["last_result"] = result["result"]
        print(f"    结果: {result['result']}")


# ==================== 第四部分：完整 Agent ====================


def complete_plan_execute_agent():
    """完整 Plan-Execute Agent"""
    print("\n" + "=" * 60)
    print("第四部分：完整 Plan-Execute Agent")
    print("=" * 60)

    class PlanExecuteAgent:
        """Plan-and-Execute Agent"""

        def __init__(self):
            self.plan = []
            self.current_step = 0
            self.context = {}

        def create_plan(self, task: str) -> List[str]:
            """创建计划"""
            if "研究" in task:
                return ["搜索资料", "整理信息", "撰写内容", "检查完善"]
            return ["分析任务", "执行操作", "验证结果"]

        def execute_step(self, step: str) -> str:
            """执行步骤"""
            return f"✅ 完成: {step}"

        def should_replan(self, result: str) -> bool:
            """判断是否需要重规划"""
            return "失败" in result or "错误" in result

        def replan(self, failed_step: str) -> List[str]:
            """重新规划"""
            return [f"重试: {failed_step}"]

        def run(self, task: str) -> str:
            """运行 Agent"""
            print(f"\n🎯 任务: {task}")

            # 1. 创建计划
            print("\n📋 规划阶段:")
            self.plan = self.create_plan(task)
            for i, step in enumerate(self.plan, 1):
                print(f"  {i}. {step}")

            # 2. 执行计划
            print("\n⚙️ 执行阶段:")
            results = []
            for step in self.plan:
                result = self.execute_step(step)
                print(f"  {result}")

                if self.should_replan(result):
                    new_steps = self.replan(step)
                    self.plan.extend(new_steps)

                results.append(result)

            return "\n".join(results)

    agent = PlanExecuteAgent()
    agent.run("研究 LLM Agent 技术并撰写总结")


# ==================== 第五部分：LangChain 实现 ====================


def langchain_implementation():
    """LangChain 实现"""
    print("\n" + "=" * 60)
    print("第五部分：LangChain 实现（代码参考）")
    print("=" * 60)

    code = """
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.plan_and_execute import (
    PlanAndExecute,
    load_agent_executor,
    load_chat_planner
)
from langchain.tools import Tool

# 定义工具
tools = [
    Tool(name="Search", func=search, description="搜索信息"),
    Tool(name="Calculator", func=calc, description="计算"),
]

# 创建规划器和执行器
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
planner = load_chat_planner(llm)
executor = load_agent_executor(llm, tools, verbose=True)

# 创建 Agent
agent = PlanAndExecute(planner=planner, executor=executor)

# 运行
result = agent.run("研究并总结 AI 最新进展")
"""

    print(code)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现智能重规划
        当步骤失败时，分析原因并生成替代方案

        ✅ 参考答案：
        ```python
        class SmartPlanExecuteAgent:
            def __init__(self, llm):
                self.llm = llm

            def analyze_failure(self, step, error):
                '''分析失败原因'''
                prompt = f'''
                步骤：{step}
                错误：{error}
                
                分析失败原因，并给出2个替代方案：
                '''
                return self.llm.invoke(prompt).content

            def replan(self, original_plan, failed_step, error, remaining_steps):
                '''智能重规划'''
                analysis = self.analyze_failure(failed_step, error)
                
                prompt = f'''
                原计划剩余步骤：{remaining_steps}
                失败分析：{analysis}
                
                请生成新的执行计划（避免重复失败的方法）：
                '''
                return self.llm.invoke(prompt).content
        ```
    
    练习 2：添加进度追踪
        记录每个步骤的执行时间和状态

        ✅ 参考答案：
        ```python
        from datetime import datetime
        from dataclasses import dataclass
        from enum import Enum

        class StepStatus(Enum):
            PENDING = "pending"
            RUNNING = "running"
            SUCCESS = "success"
            FAILED = "failed"

        @dataclass
        class StepProgress:
            step: str
            status: StepStatus
            start_time: datetime = None
            end_time: datetime = None
            result: str = None
            error: str = None

        class ProgressTracker:
            def __init__(self):
                self.steps = []
            
            def start_step(self, step: str):
                progress = StepProgress(step=step, status=StepStatus.RUNNING, start_time=datetime.now())
                self.steps.append(progress)
                return progress
            
            def complete_step(self, progress, result):
                progress.end_time = datetime.now()
                progress.status = StepStatus.SUCCESS
                progress.result = result
            
            def get_summary(self):
                return {
                    "total": len(self.steps),
                    "completed": sum(1 for s in self.steps if s.status == StepStatus.SUCCESS),
                    "failed": sum(1 for s in self.steps if s.status == StepStatus.FAILED),
                }
        ```
    
    思考题：
        Plan-Execute vs ReAct 如何选择？
        答：长期复杂任务用 Plan-Execute，
        需要实时交互和调整的用 ReAct

        ✅ 详细答案：
        
        Plan-Execute 适合：
        - 任务有明确目标和步骤
        - 需要全局规划
        - 步骤间有依赖关系
        - 例如：报告生成、数据分析流程
        
        ReAct 适合：
        - 探索性任务
        - 需要实时反馈调整
        - 不确定需要多少步
        - 例如：信息搜索、问答
    """)


def main():
    print("📝 计划执行 Agent")
    print("=" * 60)

    architecture_overview()
    task_planner()
    step_executor()
    complete_plan_execute_agent()
    langchain_implementation()
    exercises()

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：08-self-ask-agent.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
