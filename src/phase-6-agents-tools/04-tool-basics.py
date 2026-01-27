"""
工具定义与调用
=============

学习目标：
    1. 理解工具调用的基本原理
    2. 掌握工具定义规范
    3. 实现工具调用流程

核心概念：
    - 工具定义：JSON Schema 描述工具接口
    - 工具调用：LLM 决定调用时机和参数
    - 工具执行：执行并返回结果

前置知识：
    - 01-03 Agent 基础课程

环境要求：
    - pip install openai python-dotenv pydantic
"""

import os
import json
from dotenv import load_dotenv
from typing import Callable, Any

load_dotenv()


# ==================== 第一部分：工具调用概念 ====================


def tool_calling_concept():
    """工具调用概念"""
    print("=" * 60)
    print("第一部分：工具调用概念")
    print("=" * 60)

    print("""
    什么是工具调用？
    ────────────────
    
    用户: "帮我查询北京到上海的机票"
           │
           ▼
    ┌─────────────────────────────────────┐
    │ LLM 分析: 需要调用机票查询工具        │
    └─────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │ 生成工具调用请求:                     │
    │ {                                   │
    │   "tool": "search_flights",         │
    │   "arguments": {                    │
    │     "from": "北京",                 │
    │     "to": "上海"                    │
    │   }                                 │
    │ }                                   │
    └─────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │ 执行工具 & 返回结果                   │
    └─────────────────────────────────────┘
           │
           ▼
    LLM 整合回复: "为您找到以下航班..."
    """)


# ==================== 第二部分：工具定义规范 ====================


def tool_definition():
    """工具定义规范"""
    print("\n" + "=" * 60)
    print("第二部分：工具定义规范")
    print("=" * 60)

    # JSON Schema 方式
    tool_schema = {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的当前天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，如 '北京'"},
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度单位",
                    },
                },
                "required": ["city"],
            },
        },
    }

    print("📌 JSON Schema 工具定义：")
    print(json.dumps(tool_schema, indent=2, ensure_ascii=False))

    print("""
    
    工具定义要点：
    ─────────────
    1. name: 工具名称，用于 LLM 调用
    2. description: 详细描述工具功能
    3. parameters: JSON Schema 定义参数
    4. required: 必需参数列表
    """)


# ==================== 第三部分：Pydantic 定义工具 ====================


def pydantic_tool_definition():
    """使用 Pydantic 定义工具"""
    print("\n" + "=" * 60)
    print("第三部分：Pydantic 定义工具")
    print("=" * 60)

    try:
        from pydantic import BaseModel, Field

        class WeatherInput(BaseModel):
            """天气查询输入参数"""

            city: str = Field(..., description="城市名称")
            unit: str = Field(default="celsius", description="温度单位")

        class Tool:
            """工具定义类"""

            def __init__(
                self, name: str, description: str, parameters: type, function: Callable
            ):
                self.name = name
                self.description = description
                self.parameters = parameters
                self.function = function

            def to_schema(self) -> dict:
                """转换为 JSON Schema"""
                return {
                    "type": "function",
                    "function": {
                        "name": self.name,
                        "description": self.description,
                        "parameters": self.parameters.model_json_schema(),
                    },
                }

            def execute(self, **kwargs) -> Any:
                """执行工具"""
                validated = self.parameters(**kwargs)
                return self.function(**validated.model_dump())

        # 定义工具函数
        def get_weather(city: str, unit: str = "celsius") -> dict:
            return {"city": city, "temp": 25, "unit": unit, "condition": "晴"}

        # 创建工具
        weather_tool = Tool(
            name="get_weather",
            description="获取城市天气",
            parameters=WeatherInput,
            function=get_weather,
        )

        print("📌 使用 Pydantic 定义的工具：")
        print(f"  名称: {weather_tool.name}")
        print(f"  描述: {weather_tool.description}")

        # 测试执行
        result = weather_tool.execute(city="北京")
        print(f"\n📌 执行测试: get_weather(city='北京')")
        print(f"  结果: {result}")

    except ImportError:
        print("⚠️ 需要安装: pip install pydantic")


# ==================== 第四部分：工具管理器 ====================


def tool_manager_demo():
    """工具管理器"""
    print("\n" + "=" * 60)
    print("第四部分：工具管理器")
    print("=" * 60)

    class ToolManager:
        """工具管理器"""

        def __init__(self):
            self.tools = {}

        def register(self, name: str, description: str, func: Callable):
            """注册工具"""
            self.tools[name] = {"description": description, "function": func}
            print(f"  ✅ 注册工具: {name}")

        def execute(self, name: str, **kwargs) -> Any:
            """执行工具"""
            if name not in self.tools:
                return f"❌ 未找到工具: {name}"
            return self.tools[name]["function"](**kwargs)

        def list_tools(self) -> list:
            """列出所有工具"""
            return list(self.tools.keys())

    # 创建管理器
    manager = ToolManager()

    print("📌 注册工具：")
    manager.register(
        "calculator", "数学计算", lambda expr: eval(expr, {"__builtins__": {}})
    )
    manager.register("weather", "查询天气", lambda city: f"{city}: 晴, 25°C")
    manager.register("search", "搜索信息", lambda q: f"搜索结果: {q}")

    print(f"\n📌 已注册工具: {manager.list_tools()}")

    print("\n📌 执行测试：")
    print(f"  calculator('10 + 20') = {manager.execute('calculator', expr='10 + 20')}")
    print(f"  weather('北京') = {manager.execute('weather', city='北京')}")


# ==================== 第五部分：完整调用流程 ====================


def complete_flow():
    """完整调用流程"""
    print("\n" + "=" * 60)
    print("第五部分：完整调用流程")
    print("=" * 60)

    code_example = """
from openai import OpenAI

client = OpenAI()

# 1. 定义工具
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取天气",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"}
            },
            "required": ["city"]
        }
    }
}]

# 2. 调用 LLM（带工具）
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "北京天气"}],
    tools=tools,
    tool_choice="auto"
)

# 3. 检查工具调用
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    
    # 4. 执行工具
    result = get_weather(**args)
    
    # 5. 返回结果给 LLM
    messages.append({"role": "tool", 
                     "tool_call_id": tool_call.id,
                     "content": result})
"""

    print("📌 OpenAI 工具调用流程：")
    print(code_example)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：定义一个翻译工具
        参数：text（文本），target_lang（目标语言）
    
    练习 2：实现工具验证
        在执行前验证参数类型和必需参数
    
    思考题：
        如何处理工具执行超时？
        答：设置超时时间，超时返回错误信息
    """)


def main():
    print("🔧 工具定义与调用")
    print("=" * 60)

    tool_calling_concept()
    tool_definition()
    pydantic_tool_definition()
    tool_manager_demo()
    complete_flow()
    exercises()

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：05-custom-tools.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
