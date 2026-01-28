"""
Skill 实现与注册
================

学习目标：
    1. 实现完整的 Skill 类
    2. 创建 Skill 注册中心
    3. 动态加载和管理 Skills

核心概念：
    - Skill 注册中心
    - 参数验证
    - 动态发现

环境要求：
    - pip install openai python-dotenv
"""

import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

load_dotenv()


def skill_implementation():
    """Skill 完整实现"""
    print("=" * 60)
    print("第一部分：Skill 完整实现")
    print("=" * 60)

    @dataclass
    class SkillParameter:
        name: str
        type: type
        description: str
        required: bool = True
        default: Any = None

    @dataclass
    class SkillMetadata:
        name: str
        description: str
        category: str
        parameters: List[SkillParameter]
        returns: str
        version: str = "1.0.0"

    class Skill(ABC):
        """技能基类"""

        def __init__(self):
            self.metadata = self._get_metadata()

        @abstractmethod
        def _get_metadata(self) -> SkillMetadata:
            pass

        @abstractmethod
        def execute(self, **kwargs) -> Any:
            pass

        def validate_params(self, **kwargs) -> bool:
            for p in self.metadata.parameters:
                if p.required and p.name not in kwargs:
                    raise ValueError(f"Missing: {p.name}")
            return True

        def to_function_schema(self) -> Dict:
            props = {}
            required = []
            type_map = {
                str: "string",
                int: "integer",
                float: "number",
                bool: "boolean",
                list: "array",
            }

            for p in self.metadata.parameters:
                props[p.name] = {
                    "type": type_map.get(p.type, "string"),
                    "description": p.description,
                }
                if p.required:
                    required.append(p.name)

            return {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "parameters": {
                    "type": "object",
                    "properties": props,
                    "required": required,
                },
            }

    # 实现具体 Skill
    class WebSearchSkill(Skill):
        """网络搜索技能"""

        def _get_metadata(self) -> SkillMetadata:
            return SkillMetadata(
                name="web_search",
                description="搜索互联网获取信息",
                category="search",
                parameters=[
                    SkillParameter("query", str, "搜索查询词"),
                    SkillParameter("num_results", int, "结果数量", False, 5),
                ],
                returns="搜索结果列表",
            )

        def execute(self, query: str, num_results: int = 5) -> List[Dict]:
            self.validate_params(query=query)
            print(f"   🔍 搜索: {query}")
            return [
                {"title": f"结果{i}", "url": f"http://example.com/{i}"}
                for i in range(num_results)
            ]

    class CodeExecutionSkill(Skill):
        """代码执行技能"""

        def _get_metadata(self) -> SkillMetadata:
            return SkillMetadata(
                name="execute_code",
                description="执行 Python 代码",
                category="code",
                parameters=[
                    SkillParameter("code", str, "要执行的代码"),
                    SkillParameter("timeout", int, "超时(秒)", False, 30),
                ],
                returns="执行结果",
            )

        def execute(self, code: str, timeout: int = 30) -> Dict:
            self.validate_params(code=code)
            print(f"   💻 执行代码...")
            try:
                result = eval(code, {"__builtins__": {}})
                return {"success": True, "result": result}
            except Exception as e:
                return {"success": False, "error": str(e)}

    # 演示
    print("\n📌 Skill 实现演示：")

    search = WebSearchSkill()
    print(f"   技能: {search.metadata.name}")
    print(f"   描述: {search.metadata.description}")
    results = search.execute("AI趋势", 3)
    print(f"   结果: {len(results)} 条")

    return Skill, SkillMetadata, SkillParameter


def skill_registry():
    """Skill 注册中心"""
    print("\n" + "=" * 60)
    print("第二部分：Skill 注册中心")
    print("=" * 60)

    class SkillRegistry:
        """技能注册中心"""

        def __init__(self):
            self._skills: Dict[str, Any] = {}
            self._categories: Dict[str, List[str]] = {}

        def register(self, skill) -> None:
            """注册技能"""
            name = skill.metadata.name
            category = skill.metadata.category

            self._skills[name] = skill

            if category not in self._categories:
                self._categories[category] = []
            self._categories[category].append(name)

            print(f"   ✅ 注册: {name} [{category}]")

        def unregister(self, name: str) -> bool:
            """注销技能"""
            if name in self._skills:
                skill = self._skills.pop(name)
                self._categories[skill.metadata.category].remove(name)
                return True
            return False

        def get(self, name: str):
            """获取技能"""
            return self._skills.get(name)

        def list_all(self) -> List[str]:
            """列出所有技能"""
            return list(self._skills.keys())

        def list_by_category(self, category: str) -> List[str]:
            """按分类列出"""
            return self._categories.get(category, [])

        def get_all_schemas(self) -> List[Dict]:
            """获取所有 Function Schema"""
            return [s.to_function_schema() for s in self._skills.values()]

        def execute(self, name: str, **kwargs) -> Any:
            """执行技能"""
            skill = self.get(name)
            if not skill:
                raise ValueError(f"Skill not found: {name}")
            return skill.execute(**kwargs)

    # 演示
    print("\n📌 注册中心演示：")

    # 创建简单的模拟 Skill
    class MockSkill:
        def __init__(self, name, category):
            self.metadata = type("Metadata", (), {"name": name, "category": category})()

        def to_function_schema(self):
            return {"name": self.metadata.name}

        def execute(self, **kwargs):
            return f"执行 {self.metadata.name}"

    registry = SkillRegistry()
    registry.register(MockSkill("search", "info"))
    registry.register(MockSkill("calculate", "math"))
    registry.register(MockSkill("translate", "language"))

    print(f"\n   所有技能: {registry.list_all()}")
    print(f"   执行结果: {registry.execute('search')}")


def dynamic_loading():
    """动态加载"""
    print("\n" + "=" * 60)
    print("第三部分：动态加载 Skills")
    print("=" * 60)

    print("""
    动态加载技能
    ───────────
    
    可以从目录、配置文件或远程服务动态加载 Skills。
    
    skills/
    ├── search_skill.py
    ├── code_skill.py
    └── data_skill.py
    
    代码示例：
    
    import importlib
    import os

    class SkillLoader:
        def __init__(self, skill_dir: str):
            self.skill_dir = skill_dir

        def load_all(self) -> List[Skill]:
            skills = []
            for file in os.listdir(self.skill_dir):
                if file.endswith('_skill.py'):
                    module_name = file[:-3]
                    module = importlib.import_module(f"skills.{module_name}")
                    if hasattr(module, 'create_skill'):
                        skills.append(module.create_skill())
            return skills
    """)


def agent_integration():
    """与 Agent 集成"""
    print("\n" + "=" * 60)
    print("第四部分：与 Agent 集成")
    print("=" * 60)

    print("""
    Agent 使用 Skills
    ─────────────────
    
    class SkillfulAgent:
        def __init__(self, registry: SkillRegistry, llm_client):
            self.registry = registry
            self.client = llm_client

        async def process(self, user_input: str):
            # 1. 获取可用技能的 schemas
            tools = self.registry.get_all_schemas()

            # 2. 让 LLM 决定使用哪个技能
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": user_input}],
                tools=[{"type": "function", "function": t} for t in tools],
                tool_choice="auto"
            )

            # 3. 执行选中的技能
            if response.choices[0].message.tool_calls:
                call = response.choices[0].message.tool_calls[0]
                result = self.registry.execute(
                    call.function.name,
                    **json.loads(call.function.arguments)
                )
                return result
    """)


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现 Skill 热重载
    练习 2：添加 Skill 使用统计
    练习 3：实现 Skill 依赖管理
    
    思考题：
    1. 如何处理 Skill 版本冲突？
    2. 如何实现 Skill 的权限控制？
    """)


def main():
    print("📦 Skill 实现与注册")
    print("=" * 60)
    skill_implementation()
    skill_registry()
    dynamic_loading()
    agent_integration()
    exercises()
    print("\n✅ 课程完成！下一步：12-skill-composition.py")


if __name__ == "__main__":
    main()
