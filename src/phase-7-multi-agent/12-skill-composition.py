"""
Skill 组合与编排
================

学习目标：
    1. 掌握 Skill 组合模式
    2. 实现 Skill 编排引擎
    3. 学会动态 Skill 选择

核心概念：
    - Skill 流水线
    - 条件编排
    - 动态选择

环境要求：
    - pip install openai python-dotenv
"""

import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum

load_dotenv()


def skill_pipeline():
    """Skill 流水线"""
    print("=" * 60)
    print("第一部分：Skill 流水线")
    print("=" * 60)

    class SkillPipeline:
        """技能流水线"""

        def __init__(self, name: str):
            self.name = name
            self.skills: List[Callable] = []

        def add(self, skill_func: Callable) -> "SkillPipeline":
            self.skills.append(skill_func)
            return self

        def execute(self, initial_data: Any) -> Any:
            print(f"\n🔄 执行流水线: {self.name}")
            data = initial_data
            for i, skill in enumerate(self.skills):
                print(f"   步骤 {i + 1}: {skill.__name__}")
                data = skill(data)
            return data

    # 定义技能函数
    def search_skill(data: Dict) -> Dict:
        data["search_result"] = f"搜索结果: {data.get('query', '')}"
        return data

    def analyze_skill(data: Dict) -> Dict:
        data["analysis"] = f"分析: {data.get('search_result', '')}"
        return data

    def summarize_skill(data: Dict) -> Dict:
        data["summary"] = f"总结: {data.get('analysis', '')[:20]}..."
        return data

    # 演示
    print("\n📌 流水线演示：")
    pipeline = SkillPipeline("研究流水线")
    pipeline.add(search_skill).add(analyze_skill).add(summarize_skill)

    result = pipeline.execute({"query": "AI趋势"})
    print(f"   结果: {list(result.keys())}")


def conditional_orchestration():
    """条件编排"""
    print("\n" + "=" * 60)
    print("第二部分：条件编排")
    print("=" * 60)

    class ConditionalOrchestrator:
        """条件编排器"""

        def __init__(self):
            self.routes: Dict[str, Callable] = {}
            self.condition_func: Callable = lambda x: "default"

        def set_condition(self, func: Callable):
            self.condition_func = func
            return self

        def add_route(self, key: str, skill: Callable):
            self.routes[key] = skill
            return self

        def execute(self, data: Any) -> Any:
            route_key = self.condition_func(data)
            print(f"   🔀 路由: {route_key}")

            if route_key in self.routes:
                return self.routes[route_key](data)
            return data

    # 演示
    print("\n📌 条件编排演示：")

    def route_by_type(data: Dict) -> str:
        task_type = data.get("type", "")
        if "code" in task_type:
            return "code"
        elif "text" in task_type:
            return "text"
        return "default"

    orchestrator = ConditionalOrchestrator()
    orchestrator.set_condition(route_by_type)
    orchestrator.add_route("code", lambda d: {**d, "result": "代码处理"})
    orchestrator.add_route("text", lambda d: {**d, "result": "文本处理"})
    orchestrator.add_route("default", lambda d: {**d, "result": "默认处理"})

    for task_type in ["code_review", "text_analysis", "unknown"]:
        result = orchestrator.execute({"type": task_type})
        print(f"   {task_type} → {result['result']}")


def parallel_composition():
    """并行组合"""
    print("\n" + "=" * 60)
    print("第三部分：并行组合")
    print("=" * 60)

    class ParallelComposer:
        """并行组合器"""

        def __init__(self):
            self.skills: List[Callable] = []

        def add(self, skill: Callable) -> "ParallelComposer":
            self.skills.append(skill)
            return self

        def execute(self, data: Any) -> Dict[str, Any]:
            """并行执行所有技能"""
            print(f"   ⚡ 并行执行 {len(self.skills)} 个技能")
            results = {}
            for skill in self.skills:
                name = skill.__name__
                results[name] = skill(data)
                print(f"      ✅ {name}")
            return results

    # 演示
    print("\n📌 并行组合演示：")

    def skill_a(data):
        return f"A处理: {data}"

    def skill_b(data):
        return f"B处理: {data}"

    def skill_c(data):
        return f"C处理: {data}"

    composer = ParallelComposer()
    composer.add(skill_a).add(skill_b).add(skill_c)
    results = composer.execute("输入数据")
    print(f"   结果: {list(results.keys())}")


def dynamic_selection():
    """动态选择"""
    print("\n" + "=" * 60)
    print("第四部分：动态 Skill 选择")
    print("=" * 60)

    class DynamicSelector:
        """动态技能选择器"""

        def __init__(self):
            self.skills: Dict[str, Dict] = {}

        def register(
            self, name: str, skill: Callable, keywords: List[str], priority: int = 0
        ):
            self.skills[name] = {
                "func": skill,
                "keywords": keywords,
                "priority": priority,
            }

        def select(self, query: str) -> Optional[str]:
            """根据查询选择最佳技能"""
            matches = []
            query_lower = query.lower()

            for name, info in self.skills.items():
                score = sum(1 for kw in info["keywords"] if kw in query_lower)
                if score > 0:
                    matches.append((name, score + info["priority"]))

            if matches:
                matches.sort(key=lambda x: x[1], reverse=True)
                return matches[0][0]
            return None

        def execute(self, query: str, data: Any) -> Any:
            selected = self.select(query)
            if selected:
                print(f"   🎯 选择技能: {selected}")
                return self.skills[selected]["func"](data)
            print("   ❌ 未找到匹配技能")
            return data

    # 演示
    print("\n📌 动态选择演示：")

    selector = DynamicSelector()
    selector.register("search", lambda d: "搜索结果", ["搜索", "查找", "search"], 1)
    selector.register(
        "calculate", lambda d: "计算结果", ["计算", "求和", "calculate"], 0
    )
    selector.register("translate", lambda d: "翻译结果", ["翻译", "translate"], 0)

    queries = ["请帮我搜索AI新闻", "计算1+2+3", "翻译这段话", "做点什么"]
    for q in queries:
        result = selector.execute(q, {})


def orchestration_engine():
    """编排引擎"""
    print("\n" + "=" * 60)
    print("第五部分：完整编排引擎")
    print("=" * 60)

    class OrchestrationEngine:
        """编排引擎"""

        def __init__(self):
            self.skills = {}
            self.workflows = {}

        def register_skill(self, name: str, func: Callable):
            self.skills[name] = func

        def define_workflow(self, name: str, steps: List[Dict]):
            """定义工作流: [{"skill": "name", "condition": func}]"""
            self.workflows[name] = steps

        def run_workflow(self, workflow_name: str, data: Any) -> Any:
            if workflow_name not in self.workflows:
                raise ValueError(f"工作流不存在: {workflow_name}")

            print(f"\n🚀 执行工作流: {workflow_name}")
            steps = self.workflows[workflow_name]

            for i, step in enumerate(steps):
                skill_name = step["skill"]
                condition = step.get("condition", lambda x: True)

                if not condition(data):
                    print(f"   ⏭️ 跳过: {skill_name}")
                    continue

                if skill_name in self.skills:
                    print(f"   ▶️ 执行: {skill_name}")
                    data = self.skills[skill_name](data)

            return data

    # 演示
    print("\n📌 编排引擎演示：")

    engine = OrchestrationEngine()
    engine.register_skill("prepare", lambda d: {**d, "prepared": True})
    engine.register_skill("process", lambda d: {**d, "processed": True})
    engine.register_skill("validate", lambda d: {**d, "valid": True})
    engine.register_skill("cleanup", lambda d: {**d, "cleaned": True})

    engine.define_workflow(
        "standard",
        [
            {"skill": "prepare"},
            {"skill": "process"},
            {
                "skill": "validate",
                "condition": lambda d: d.get("need_validation", True),
            },
            {"skill": "cleanup"},
        ],
    )

    result = engine.run_workflow("standard", {"input": "data"})
    print(f"   结果: {list(result.keys())}")


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现带重试的流水线
    练习 2：添加工作流可视化
    练习 3：实现 A/B 测试选择器
    
    思考题：
    1. 如何监控 Skill 执行性能？
    2. 工作流失败如何回滚？
    """)


def main():
    print("🎼 Skill 组合与编排")
    print("=" * 60)
    skill_pipeline()
    conditional_orchestration()
    parallel_composition()
    dynamic_selection()
    orchestration_engine()
    exercises()
    print("\n" + "=" * 60)
    print("🎉 Phase 7 全部课程完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
