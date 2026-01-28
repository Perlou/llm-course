"""
Agent Skill 概述
================

学习目标：
    1. 理解 Agent Skill 的概念
    2. 掌握 Skill 的设计原则
    3. 了解 Skill 架构

核心概念：
    - Skill：Agent 的可复用能力单元
    - Skill 注册与发现
    - Skill 参数化

环境要求：
    - pip install openai python-dotenv
"""

import os
from dotenv import load_dotenv
from typing import Dict, List, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

load_dotenv()


def skill_overview():
    """Skill 概述"""
    print("=" * 60)
    print("第一部分：Agent Skill 概述")
    print("=" * 60)

    print("""
    什么是 Agent Skill？
    ───────────────────
    
    Skill 是 Agent 的可复用能力单元，封装特定功能。
    
    ┌─────────────────────────────────────────────────────┐
    │                    Agent                             │
    │                                                     │
    │   ┌──────────────────────────────────────────────┐ │
    │   │              Skill Registry                   │ │
    │   │  ┌─────────┐ ┌─────────┐ ┌─────────┐        │ │
    │   │  │ 搜索    │ │ 代码    │ │ 数据    │        │ │
    │   │  │ Skill   │ │ Skill   │ │ Skill   │        │ │
    │   │  └─────────┘ └─────────┘ └─────────┘        │ │
    │   └──────────────────────────────────────────────┘ │
    │                       ↓                             │
    │   ┌──────────────────────────────────────────────┐ │
    │   │              Skill Executor                   │ │
    │   └──────────────────────────────────────────────┘ │
    └─────────────────────────────────────────────────────┘
    
    Skill vs Tool
    ─────────────
    - Tool：基础的外部工具调用
    - Skill：更高层次的能力封装，可组合多个 Tool
    
    Skill 的特点：
    - 自描述：包含元数据和使用说明
    - 参数化：定义输入输出规范
    - 可发现：可被 Agent 动态发现和调用
    """)


def skill_structure():
    """Skill 结构"""
    print("\n" + "=" * 60)
    print("第二部分：Skill 结构定义")
    print("=" * 60)

    @dataclass
    class SkillParameter:
        """技能参数"""

        name: str
        type: type
        description: str
        required: bool = True
        default: Any = None

    @dataclass
    class SkillMetadata:
        """技能元数据"""

        name: str
        description: str
        category: str
        parameters: List[SkillParameter]
        returns: str
        examples: List[str] = field(default_factory=list)

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

        def to_function_schema(self) -> Dict:
            """转换为 OpenAI Function 格式"""
            props = {}
            required = []
            for p in self.metadata.parameters:
                props[p.name] = {
                    "type": "string" if p.type == str else "integer",
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

    print("""
    @dataclass
    class SkillMetadata:
        name: str          # 技能名称
        description: str   # 技能描述
        category: str      # 分类
        parameters: List   # 参数列表
        returns: str       # 返回值说明

    class Skill(ABC):
        @abstractmethod
        def _get_metadata(self) -> SkillMetadata: ...
        
        @abstractmethod
        def execute(self, **kwargs) -> Any: ...
        
        def to_function_schema(self) -> Dict: ...
    """)

    return Skill, SkillMetadata, SkillParameter


def example_skills():
    """示例 Skills"""
    print("\n" + "=" * 60)
    print("第三部分：示例 Skills")
    print("=" * 60)

    class SearchSkill:
        """搜索技能"""

        def __init__(self):
            self.name = "web_search"
            self.description = "搜索网络获取信息"

        def execute(self, query: str, num_results: int = 5) -> List[Dict]:
            print(f"   🔍 搜索: {query}")
            return [
                {"title": f"结果{i}", "url": f"http://example.com/{i}"}
                for i in range(num_results)
            ]

    class CalculatorSkill:
        """计算技能"""

        def __init__(self):
            self.name = "calculator"
            self.description = "执行数学计算"

        def execute(self, expression: str) -> float:
            print(f"   🧮 计算: {expression}")
            try:
                return eval(expression, {"__builtins__": {}})
            except:
                return 0

    class FileSkill:
        """文件操作技能"""

        def __init__(self):
            self.name = "file_operation"
            self.description = "读写文件"

        def execute(self, operation: str, path: str, content: str = "") -> Dict:
            print(f"   📁 文件操作: {operation} {path}")
            return {"success": True, "operation": operation}

    # 演示
    print("\n📌 技能演示：")

    search = SearchSkill()
    results = search.execute("AI趋势", 3)
    print(f"   结果: {len(results)} 条")

    calc = CalculatorSkill()
    result = calc.execute("10 * 5 + 3")
    print(f"   结果: {result}")


def skill_categories():
    """Skill 分类"""
    print("\n" + "=" * 60)
    print("第四部分：Skill 分类")
    print("=" * 60)

    print("""
    常见 Skill 分类
    ───────────────
    
    📂 信息获取类
       - web_search: 网络搜索
       - document_read: 文档读取
       - database_query: 数据库查询
    
    💻 代码执行类
       - code_execute: 代码执行
       - code_analyze: 代码分析
       - code_generate: 代码生成
    
    📄 文档处理类
       - document_write: 文档写入
       - document_format: 格式转换
       - document_summarize: 内容摘要
    
    🔧 系统操作类
       - file_operation: 文件操作
       - api_call: API 调用
       - shell_command: 命令执行
    
    📊 数据分析类
       - data_analyze: 数据分析
       - data_visualize: 数据可视化
       - data_transform: 数据转换
    """)


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：创建翻译 Skill
    练习 2：创建邮件发送 Skill
    练习 3：为 Skill 添加权限控制
    
    思考题：
    1. Skill 与 Tool 的边界在哪里？
    2. 如何版本化管理 Skills？
    """)


def main():
    print("🛠️ Agent Skill 概述")
    print("=" * 60)
    skill_overview()
    skill_structure()
    example_skills()
    skill_categories()
    exercises()
    print("\n✅ 课程完成！下一步：10-skill-design-patterns.py")


if __name__ == "__main__":
    main()
