"""
Skill 设计模式
==============

学习目标：
    1. 掌握 Skill 设计原则
    2. 学习常见设计模式
    3. 实现可组合的 Skills

核心概念：
    - 单一职责原则
    - 组合模式
    - 装饰器模式

环境要求：
    - pip install openai python-dotenv
"""

import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Callable
from functools import wraps
from abc import ABC, abstractmethod

load_dotenv()


def design_principles():
    """设计原则"""
    print("=" * 60)
    print("第一部分：Skill 设计原则")
    print("=" * 60)

    print("""
    Skill 设计原则
    ─────────────
    
    1. 单一职责 (Single Responsibility)
       每个 Skill 只做一件事，做好一件事
    
    2. 开闭原则 (Open-Closed)
       对扩展开放，对修改关闭
    
    3. 自描述性 (Self-Describing)
       Skill 应该能清晰描述自己的功能和用法
    
    4. 可组合性 (Composability)
       Skills 应该能够组合使用
    
    5. 幂等性 (Idempotency)
       相同输入应产生相同输出
    
    6. 错误隔离 (Error Isolation)
       一个 Skill 的失败不应影响其他 Skills
    """)


def decorator_pattern():
    """装饰器模式"""
    print("\n" + "=" * 60)
    print("第二部分：装饰器模式")
    print("=" * 60)

    def with_logging(func: Callable) -> Callable:
        """日志装饰器"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"   📝 调用: {func.__name__}")
            result = func(*args, **kwargs)
            print(f"   📝 完成: {func.__name__}")
            return result

        return wrapper

    def with_retry(max_retries: int = 3):
        """重试装饰器"""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                for i in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        print(f"   ⚠️ 重试 {i + 1}/{max_retries}: {e}")
                raise Exception(f"{func.__name__} 失败")

            return wrapper

        return decorator

    def with_cache(func: Callable) -> Callable:
        """缓存装饰器"""
        cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key in cache:
                print(f"   💾 命中缓存")
                return cache[key]
            result = func(*args, **kwargs)
            cache[key] = result
            return result

        return wrapper

    # 演示
    print("\n📌 装饰器演示：")

    @with_logging
    @with_cache
    def search_skill(query: str) -> List:
        return [f"结果: {query}"]

    print("\n第一次调用：")
    search_skill("AI")
    print("\n第二次调用（缓存）：")
    search_skill("AI")


def composite_pattern():
    """组合模式"""
    print("\n" + "=" * 60)
    print("第三部分：组合模式")
    print("=" * 60)

    class SkillComponent(ABC):
        """技能组件基类"""

        @abstractmethod
        def execute(self, **kwargs) -> Any:
            pass

    class AtomicSkill(SkillComponent):
        """原子技能"""

        def __init__(self, name: str, func: Callable):
            self.name = name
            self.func = func

        def execute(self, **kwargs) -> Any:
            print(f"   ▶️ 执行原子技能: {self.name}")
            return self.func(**kwargs)

    class CompositeSkill(SkillComponent):
        """组合技能"""

        def __init__(self, name: str):
            self.name = name
            self.skills: List[SkillComponent] = []

        def add(self, skill: SkillComponent):
            self.skills.append(skill)
            return self

        def execute(self, **kwargs) -> Dict:
            print(f"   🔄 执行组合技能: {self.name}")
            results = {}
            data = kwargs
            for skill in self.skills:
                result = skill.execute(**data)
                if isinstance(result, dict):
                    data.update(result)
                results[skill.name if hasattr(skill, "name") else "step"] = result
            return results

    # 演示
    print("\n📌 组合技能演示：")

    search = AtomicSkill("搜索", lambda query: {"data": f"搜索结果: {query}"})
    analyze = AtomicSkill("分析", lambda data, **_: {"analysis": f"分析: {data}"})
    summarize = AtomicSkill("总结", lambda analysis, **_: f"总结: {analysis}")

    research_pipeline = CompositeSkill("研究流水线")
    research_pipeline.add(search).add(analyze).add(summarize)

    result = research_pipeline.execute(query="AI趋势")
    print(f"   结果: {list(result.keys())}")


def factory_pattern():
    """工厂模式"""
    print("\n" + "=" * 60)
    print("第四部分：工厂模式")
    print("=" * 60)

    class SkillFactory:
        """技能工厂"""

        _skills: Dict[str, type] = {}

        @classmethod
        def register(cls, name: str):
            """注册装饰器"""

            def decorator(skill_class: type):
                cls._skills[name] = skill_class
                return skill_class

            return decorator

        @classmethod
        def create(cls, name: str, **config) -> Any:
            """创建技能实例"""
            if name not in cls._skills:
                raise ValueError(f"Unknown skill: {name}")
            return cls._skills[name](**config)

        @classmethod
        def list_skills(cls) -> List[str]:
            return list(cls._skills.keys())

    @SkillFactory.register("search")
    class SearchSkill:
        def __init__(self, api_key: str = ""):
            self.api_key = api_key

        def execute(self, query: str):
            return f"搜索: {query}"

    @SkillFactory.register("calc")
    class CalcSkill:
        def execute(self, expr: str):
            return eval(expr, {"__builtins__": {}})

    # 演示
    print("\n📌 工厂模式演示：")
    print(f"   已注册技能: {SkillFactory.list_skills()}")

    skill = SkillFactory.create("search", api_key="xxx")
    print(f"   创建: {skill.execute('AI')}")


def chain_pattern():
    """链式模式"""
    print("\n" + "=" * 60)
    print("第五部分：链式模式")
    print("=" * 60)

    class SkillChain:
        """技能链"""

        def __init__(self):
            self.steps: List[Callable] = []

        def then(self, func: Callable) -> "SkillChain":
            self.steps.append(func)
            return self

        def execute(self, initial_data: Any) -> Any:
            data = initial_data
            for step in self.steps:
                data = step(data)
            return data

    # 演示
    print("\n📌 链式调用演示：")

    chain = SkillChain()
    chain.then(lambda x: x.upper()).then(lambda x: f"[处理] {x}").then(
        lambda x: {"result": x}
    )

    result = chain.execute("hello world")
    print(f"   结果: {result}")


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现超时装饰器

        ✅ 参考答案：
        ```python
        import signal
        from functools import wraps

        def with_timeout(seconds: int):
            def decorator(func):
                def handler(signum, frame):
                    raise TimeoutError(f"执行超时 ({seconds}s)")
                
                @wraps(func)
                def wrapper(*args, **kwargs):
                    signal.signal(signal.SIGALRM, handler)
                    signal.alarm(seconds)
                    try:
                        return func(*args, **kwargs)
                    finally:
                        signal.alarm(0)
                return wrapper
            return decorator

        # 使用
        @with_timeout(30)
        def slow_skill(data):
            # 耗时操作
            return process(data)
        ```

    练习 2：创建条件执行的组合技能

        ✅ 参考答案：
        ```python
        class ConditionalSkill:
            def __init__(self, conditions: list):
                # conditions: [(condition_func, skill), ...]
                self.conditions = conditions
                self.default_skill = None
            
            def set_default(self, skill):
                self.default_skill = skill
                return self
            
            def execute(self, context: dict):
                for condition, skill in self.conditions:
                    if condition(context):
                        return skill.execute(context)
                
                if self.default_skill:
                    return self.default_skill.execute(context)
                
                raise ValueError("没有匹配的条件")

        # 使用
        skill = ConditionalSkill([
            (lambda c: c.get("type") == "text", TextProcessor()),
            (lambda c: c.get("type") == "image", ImageProcessor()),
        ]).set_default(DefaultProcessor())
        ```

    练习 3：实现技能版本管理

        ✅ 参考答案：
        ```python
        from dataclasses import dataclass
        from typing import Dict

        @dataclass
        class SkillVersion:
            major: int
            minor: int
            patch: int
            
            def __str__(self):
                return f"{self.major}.{self.minor}.{self.patch}"
            
            def is_compatible(self, other: 'SkillVersion'):
                return self.major == other.major

        class VersionedSkillRegistry:
            def __init__(self):
                self.skills: Dict[str, Dict[str, BaseSkill]] = {}
            
            def register(self, skill: BaseSkill, version: str):
                name = skill.name
                self.skills.setdefault(name, {})[version] = skill
            
            def get(self, name: str, version: str = None):
                if name not in self.skills:
                    raise KeyError(f"Skill not found: {name}")
                
                versions = self.skills[name]
                if version:
                    return versions.get(version)
                
                # 返回最新版本
                latest = sorted(versions.keys())[-1]
                return versions[latest]
        ```
    
    思考题：
    1. 装饰器模式的优缺点？

       ✅ 答：
       优点：灵活组合、不修改原代码、可复用
       缺点：调试困难、嵌套过深难以理解

    2. 如何选择合适的设计模式？

       ✅ 答：根据需求选择：
       - 需要增强功能 → 装饰器
       - 需要条件处理 → 策略模式
       - 需要组合多步 → 管道模式
       - 需要统一接口 → 适配器模式
    """)


def main():
    print("📐 Skill 设计模式")
    print("=" * 60)
    design_principles()
    decorator_pattern()
    composite_pattern()
    factory_pattern()
    chain_pattern()
    exercises()
    print("\n✅ 课程完成！下一步：11-skill-implementation.py")


if __name__ == "__main__":
    main()
