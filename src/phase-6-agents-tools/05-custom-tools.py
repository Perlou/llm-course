"""
自定义工具开发
=============

学习目标：
    1. 掌握自定义工具开发流程
    2. 学会工具参数验证
    3. 实现实用工具集

核心概念：
    - 工具抽象类设计
    - 参数验证与错误处理
    - 异步工具支持

前置知识：
    - 04-tool-basics.py

环境要求：
    - pip install openai python-dotenv pydantic requests
"""

import os
import json
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：工具基类设计 ====================


def tool_base_class():
    """工具基类设计"""
    print("=" * 60)
    print("第一部分：工具基类设计")
    print("=" * 60)

    from abc import ABC, abstractmethod

    class BaseTool(ABC):
        """工具基类"""

        name: str = ""
        description: str = ""

        @abstractmethod
        def _run(self, **kwargs) -> str:
            """执行工具（子类实现）"""
            pass

        def run(self, **kwargs) -> str:
            """执行工具（带错误处理）"""
            try:
                return self._run(**kwargs)
            except Exception as e:
                return f"工具执行错误: {str(e)}"

        def get_schema(self) -> dict:
            """获取工具 Schema（子类可覆盖）"""
            return {
                "type": "function",
                "function": {
                    "name": self.name,
                    "description": self.description,
                    "parameters": {"type": "object", "properties": {}},
                },
            }

    # 具体工具实现
    class CalculatorTool(BaseTool):
        name = "calculator"
        description = "执行数学计算，支持加减乘除"

        def _run(self, expression: str) -> str:
            result = eval(expression, {"__builtins__": {}})
            return f"计算结果: {result}"

        def get_schema(self) -> dict:
            return {
                "type": "function",
                "function": {
                    "name": self.name,
                    "description": self.description,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "数学表达式",
                            }
                        },
                        "required": ["expression"],
                    },
                },
            }

    # 测试
    calc = CalculatorTool()
    print(f"📌 工具名称: {calc.name}")
    print(f"📌 工具描述: {calc.description}")
    print(f"📌 执行测试: {calc.run(expression='100 * 5 + 50')}")


# ==================== 第二部分：Pydantic 工具 ====================


def pydantic_tools():
    """Pydantic 工具实现"""
    print("\n" + "=" * 60)
    print("第二部分：Pydantic 工具")
    print("=" * 60)

    try:
        from pydantic import BaseModel, Field

        class SearchInput(BaseModel):
            """搜索工具输入"""

            query: str = Field(..., description="搜索关键词")
            max_results: int = Field(default=5, description="最大结果数")

        class SearchTool:
            """搜索工具"""

            name = "search"
            description = "搜索互联网信息"
            args_schema = SearchInput

            def run(self, query: str, max_results: int = 5) -> str:
                # 模拟搜索
                return f"搜索 '{query}' 的前 {max_results} 条结果..."

            def validate_and_run(self, **kwargs) -> str:
                validated = self.args_schema(**kwargs)
                return self.run(**validated.model_dump())

        tool = SearchTool()
        print(f"📌 执行: {tool.validate_and_run(query='Python 教程')}")

    except ImportError:
        print("⚠️ 需要安装 pydantic")


# ==================== 第三部分：实用工具集 ====================


def practical_tools():
    """实用工具集"""
    print("\n" + "=" * 60)
    print("第三部分：实用工具集")
    print("=" * 60)

    import datetime

    class DateTimeTool:
        """日期时间工具"""

        name = "datetime"
        description = "获取当前日期时间"

        def run(self, format: str = "%Y-%m-%d %H:%M:%S") -> str:
            return datetime.datetime.now().strftime(format)

    class TextTool:
        """文本处理工具"""

        name = "text_tool"
        description = "文本处理：统计字数、提取关键词等"

        def count_words(self, text: str) -> dict:
            chars = len(text)
            words = len(text.split())
            return {"字符数": chars, "词数": words}

        def run(self, text: str, action: str = "count") -> str:
            if action == "count":
                return str(self.count_words(text))
            return "未知操作"

    # 测试
    dt_tool = DateTimeTool()
    txt_tool = TextTool()

    print(f"📌 当前时间: {dt_tool.run()}")
    print(f"📌 文本统计: {txt_tool.run('Hello World 你好世界')}")


# ==================== 第四部分：工具注册表 ====================


def tool_registry():
    """工具注册表"""
    print("\n" + "=" * 60)
    print("第四部分：工具注册表")
    print("=" * 60)

    class ToolRegistry:
        """工具注册表"""

        def __init__(self):
            self._tools = {}

        def register(self, tool):
            """注册工具"""
            self._tools[tool.name] = tool
            return tool

        def get(self, name: str):
            """获取工具"""
            return self._tools.get(name)

        def list_names(self) -> list:
            return list(self._tools.keys())

        def get_all_schemas(self) -> list:
            """获取所有工具 Schema"""
            schemas = []
            for tool in self._tools.values():
                if hasattr(tool, "get_schema"):
                    schemas.append(tool.get_schema())
            return schemas

    # 使用装饰器模式
    registry = ToolRegistry()

    @registry.register
    class WeatherTool:
        name = "weather"
        description = "查询天气"

        def run(self, city: str) -> str:
            return f"{city}: 晴, 25°C"

        def get_schema(self):
            return {"type": "function", "function": {"name": self.name}}

    print(f"📌 已注册工具: {registry.list_names()}")
    weather = registry.get("weather")
    print(f"📌 执行: {weather.run('上海')}")


# ==================== 第五部分：错误处理 ====================


def error_handling():
    """错误处理"""
    print("\n" + "=" * 60)
    print("第五部分：错误处理")
    print("=" * 60)

    class SafeTool:
        """安全工具（带重试和超时）"""

        def __init__(self, max_retries: int = 3):
            self.max_retries = max_retries

        def run_with_retry(self, func, *args, **kwargs):
            """带重试的执行"""
            for i in range(self.max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == self.max_retries - 1:
                        return f"执行失败（已重试{self.max_retries}次）: {e}"
                    print(f"  重试 {i + 1}/{self.max_retries}...")

    tool = SafeTool(max_retries=3)

    def risky_operation():
        import random

        if random.random() < 0.7:
            raise Exception("随机错误")
        return "成功"

    print("📌 带重试的执行：")
    result = tool.run_with_retry(risky_operation)
    print(f"  结果: {result}")


# ==================== 第六部分：练习 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现一个文件读取工具
    练习 2：实现异步工具支持
    练习 3：添加工具执行日志
    
    思考题：如何限制工具的权限（如只读文件）？
    """)


def main():
    print("🛠️ 自定义工具开发")
    print("=" * 60)

    tool_base_class()
    pydantic_tools()
    practical_tools()
    tool_registry()
    error_handling()
    exercises()

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：06-openai-functions.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
