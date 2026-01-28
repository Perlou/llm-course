"""
Agent 工作流设计 (Agent Workflows)
=================================

学习目标：
    1. 理解工作流设计原则
    2. 掌握常见工作流模式
    3. 实现复杂工作流

核心概念：
    - 顺序工作流
    - 并行工作流
    - 条件分支
    - 循环迭代

环境要求：
    - pip install openai python-dotenv
"""

import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio

load_dotenv()


def workflow_patterns():
    """工作流模式"""
    print("=" * 60)
    print("第一部分：工作流模式概述")
    print("=" * 60)

    print("""
    常见工作流模式
    ─────────────
    
    1. 顺序工作流 (Sequential)
       A → B → C → D
    
    2. 并行工作流 (Parallel)
       ┌→ B ─┐
       A     ├→ D
       └→ C ─┘
    
    3. 条件分支 (Conditional)
            ┌→ B (条件1)
       A →──┼→ C (条件2)
            └→ D (默认)
    
    4. 循环迭代 (Loop)
       A → B → C ─┐
           ↑      │
           └──────┘
    
    5. 混合模式 (Hybrid)
       组合以上多种模式
    """)


def workflow_implementation():
    """工作流实现"""
    print("\n" + "=" * 60)
    print("第二部分：工作流实现")
    print("=" * 60)

    class WorkflowStep:
        """工作流步骤"""

        def __init__(self, name: str, func: Callable):
            self.name = name
            self.func = func

        def execute(self, input_data: Any) -> Any:
            print(f"   ▶️ 执行步骤: {self.name}")
            result = self.func(input_data)
            print(f"   ✅ {self.name} 完成")
            return result

    class SequentialWorkflow:
        """顺序工作流"""

        def __init__(self, name: str):
            self.name = name
            self.steps: List[WorkflowStep] = []

        def add_step(self, name: str, func: Callable):
            self.steps.append(WorkflowStep(name, func))
            return self

        def run(self, initial_input: Any) -> Any:
            print(f"\n🔄 运行工作流: {self.name}")
            print("-" * 40)
            data = initial_input
            for step in self.steps:
                data = step.execute(data)
            return data

    # 演示顺序工作流
    print("\n📌 顺序工作流演示：")

    def research(data):
        return {**data, "research": "完成调研"}

    def analyze(data):
        return {**data, "analysis": "完成分析"}

    def write(data):
        return {**data, "content": "完成写作"}

    def review(data):
        return {**data, "reviewed": True}

    workflow = SequentialWorkflow("内容创作流程")
    workflow.add_step("调研", research)
    workflow.add_step("分析", analyze)
    workflow.add_step("写作", write)
    workflow.add_step("审核", review)

    result = workflow.run({"topic": "AI趋势"})
    print(f"\n📦 最终结果: {list(result.keys())}")


def parallel_workflow():
    """并行工作流"""
    print("\n" + "=" * 60)
    print("第三部分：并行工作流")
    print("=" * 60)

    class ParallelWorkflow:
        """并行工作流"""

        def __init__(self, name: str):
            self.name = name
            self.parallel_tasks: List[Callable] = []

        def add_parallel_task(self, func: Callable):
            self.parallel_tasks.append(func)
            return self

        def run_sync(self, input_data: Any) -> List[Any]:
            """同步模拟并行"""
            print(f"\n🔄 并行执行: {self.name}")
            results = []
            for i, task in enumerate(self.parallel_tasks):
                print(f"   ▶️ 任务 {i + 1}")
                results.append(task(input_data))
            return results

    print("\n📌 并行工作流演示：")

    def task_a(data):
        return f"A处理: {data}"

    def task_b(data):
        return f"B处理: {data}"

    def task_c(data):
        return f"C处理: {data}"

    parallel = ParallelWorkflow("并行处理")
    parallel.add_parallel_task(task_a)
    parallel.add_parallel_task(task_b)
    parallel.add_parallel_task(task_c)

    results = parallel.run_sync("输入数据")
    print(f"   结果: {results}")


def conditional_workflow():
    """条件工作流"""
    print("\n" + "=" * 60)
    print("第四部分：条件分支工作流")
    print("=" * 60)

    class ConditionalWorkflow:
        """条件分支工作流"""

        def __init__(self):
            self.routes: Dict[str, Callable] = {}
            self.default_route: Callable = lambda x: x

        def add_route(self, condition: str, handler: Callable):
            self.routes[condition] = handler
            return self

        def set_default(self, handler: Callable):
            self.default_route = handler
            return self

        def run(self, input_data: Any, condition: str) -> Any:
            handler = self.routes.get(condition, self.default_route)
            print(f"   🔀 条件: {condition} → {handler.__name__}")
            return handler(input_data)

    print("\n📌 条件分支演示：")

    def handle_text(data):
        return f"[文本处理] {data}"

    def handle_image(data):
        return f"[图像处理] {data}"

    def handle_default(data):
        return f"[默认处理] {data}"

    workflow = ConditionalWorkflow()
    workflow.add_route("text", handle_text)
    workflow.add_route("image", handle_image)
    workflow.set_default(handle_default)

    for cond in ["text", "image", "video"]:
        result = workflow.run("数据", cond)
        print(f"   {result}")


def loop_workflow():
    """循环工作流"""
    print("\n" + "=" * 60)
    print("第五部分：循环迭代工作流")
    print("=" * 60)

    class IterativeWorkflow:
        """循环迭代工作流"""

        def __init__(self, max_iterations: int = 5):
            self.max_iterations = max_iterations
            self.process_func = None
            self.check_func = None

        def set_process(self, func: Callable):
            self.process_func = func
            return self

        def set_check(self, func: Callable):
            self.check_func = func
            return self

        def run(self, initial_data: Any) -> Any:
            data = initial_data
            for i in range(self.max_iterations):
                print(f"   🔁 迭代 {i + 1}")
                data = self.process_func(data)
                if self.check_func(data):
                    print(f"   ✅ 完成条件满足")
                    break
            return data

    print("\n📌 循环迭代演示：")

    def improve(data):
        data["quality"] = data.get("quality", 0) + 20
        return data

    def is_good_enough(data):
        return data.get("quality", 0) >= 80

    workflow = IterativeWorkflow(max_iterations=5)
    workflow.set_process(improve)
    workflow.set_check(is_good_enough)

    result = workflow.run({"content": "初稿", "quality": 30})
    print(f"   最终质量: {result['quality']}")


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：组合工作流 - 结合顺序和并行
    练习 2：添加错误处理 - 步骤失败时的回退
    练习 3：使用 LangGraph 重写工作流
    
    思考题：
    1. 如何决定任务是顺序还是并行？
    2. 循环工作流如何避免无限循环？
    """)


def main():
    print("🔄 Agent 工作流设计")
    print("=" * 60)
    workflow_patterns()
    workflow_implementation()
    parallel_workflow()
    conditional_workflow()
    loop_workflow()
    exercises()
    print("\n✅ 课程完成！下一步：08-human-in-the-loop.py")


if __name__ == "__main__":
    main()
