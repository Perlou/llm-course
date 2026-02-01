"""
Gemini Function Calling
=======================

学习目标：
    1. 掌握 Gemini Function Calling 机制
    2. 理解 tool_choice 参数
    3. 处理并行工具调用

核心概念：
    - tools 参数：定义可用工具
    - tool_calls：LLM 返回的工具调用请求
    - tool_choice：控制工具使用策略

前置知识：
    - 04-tool-basics.py
    - 05-custom-tools.py

环境要求：
    - pip install google-generativeai python-dotenv
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Function Calling 概述 ====================


def function_calling_overview():
    """Function Calling 概述"""
    print("=" * 60)
    print("第一部分：Function Calling 概述")
    print("=" * 60)

    print("""
    Gemini Function Calling
    ─────────────────────────
    
    1. 注册工具（tools 参数）
           │
           ▼
    2. 发送消息给 LLM
           │
           ▼
    3. LLM 决定是否调用工具
           │
           ▼
    4. 返回 tool_calls（工具调用请求）
           │
           ▼
    5. 执行工具并获取结果
           │
           ▼
    6. 将结果发送回 LLM
           │
           ▼
    7. LLM 生成最终回复
    
    tool_choice 选项：
    ─────────────────
    • "auto"    - LLM 自动决定
    • "none"    - 不使用工具
    • "required" - 必须使用工具
    • {"type": "function", "function": {"name": "xxx"}}
                - 强制使用指定工具
    """)


# ==================== 第二部分：基础调用示例 ====================


def basic_function_calling():
    """基础调用示例"""
    print("\n" + "=" * 60)
    print("第二部分：基础调用示例")
    print("=" * 60)

    # 工具定义
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "获取指定城市的天气信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "城市名称"}
                    },
                    "required": ["city"],
                },
            },
        }
    ]

    print("📌 工具定义：")
    print(json.dumps(tools, indent=2, ensure_ascii=False))

    # 模拟调用流程
    print("\n📌 调用流程演示（模拟）：")

    # 模拟 LLM 返回的 tool_call
    mock_tool_call = {
        "id": "call_abc123",
        "type": "function",
        "function": {"name": "get_weather", "arguments": '{"city": "北京"}'},
    }

    print(f"  1. 用户: '北京天气怎么样？'")
    print(f"  2. LLM 返回 tool_call:")
    print(f"     {json.dumps(mock_tool_call, indent=6, ensure_ascii=False)}")

    # 执行工具
    args = json.loads(mock_tool_call["function"]["arguments"])
    result = f"{args['city']}: 晴，25°C"
    print(f"  3. 执行工具，结果: {result}")
    print(f"  4. 将结果返回 LLM，生成最终回复")


# ==================== 第三部分：完整实现 ====================


def complete_implementation():
    """完整实现"""
    print("\n" + "=" * 60)
    print("第三部分：完整实现（代码示例）")
    print("=" * 60)

    code = """
import google.generativeai as genai

# 工具函数
def get_weather(city: str) -> str:
    return f"{city}: 晴, 25°C"

def calculate(expression: str) -> str:
    return str(eval(expression, {"__builtins__": {}}))

TOOLS = {
    "get_weather": get_weather,
    "calculate": calculate,
}

# 工具定义
tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取天气",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "calculate",
            "description": "数学计算",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"]
            }
        }
    }
]

def chat_with_tools(message: str) -> str:
    messages = [{"role": "user", "content": message}]
    
    # 第一次调用
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tool_definitions,
        tool_choice="auto"
    )
    
    assistant_msg = response.choices[0].message
    
    # 检查工具调用
    if assistant_msg.tool_calls:
        messages.append(assistant_msg)
        
        for tool_call in assistant_msg.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            
            # 执行工具
            result = TOOLS[func_name](**func_args)
            
            # 添加工具结果
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
        
        # 再次调用获取最终回复
        final = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        return final.choices[0].message.content
    
    return assistant_msg.content
"""

    print(code)


# ==================== 第四部分：并行工具调用 ====================


def parallel_tool_calls():
    """并行工具调用"""
    print("\n" + "=" * 60)
    print("第四部分：并行工具调用")
    print("=" * 60)

    print("""
    并行工具调用
    ────────────
    
    用户: "北京和上海的天气分别怎么样？"
    
    LLM 返回多个 tool_calls：
    [
        {"id": "call_1", "name": "get_weather", "args": {"city": "北京"}},
        {"id": "call_2", "name": "get_weather", "args": {"city": "上海"}}
    ]
    
    处理方式：
    1. 遍历所有 tool_calls
    2. 分别执行每个工具
    3. 收集所有结果
    4. 一起返回给 LLM
    """)

    # 演示
    tool_calls = [
        {"id": "call_1", "name": "get_weather", "args": {"city": "北京"}},
        {"id": "call_2", "name": "get_weather", "args": {"city": "上海"}},
    ]

    def get_weather(city):
        return f"{city}: 晴, 25°C"

    print("📌 并行执行演示：")
    for tc in tool_calls:
        result = get_weather(**tc["args"])
        print(f"  {tc['id']}: {result}")


# ==================== 第五部分：错误处理 ====================


def error_handling():
    """错误处理"""
    print("\n" + "=" * 60)
    print("第五部分：错误处理")
    print("=" * 60)

    print("""
    错误处理要点
    ────────────
    
    1. 工具不存在
       if func_name not in TOOLS:
           return {"error": f"未知工具: {func_name}"}
    
    2. 参数解析失败
       try:
           args = json.loads(arguments)
       except json.JSONDecodeError:
           return {"error": "参数格式错误"}
    
    3. 工具执行失败
       try:
           result = tool(**args)
       except Exception as e:
           return {"error": str(e)}
    
    4. 返回错误信息给 LLM
       让 LLM 知道工具执行失败，可以重试或换策略
    """)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现完整的多工具 Agent
    练习 2：添加工具调用次数限制
    练习 3：实现工具调用日志记录
    
    思考题：
        tool_choice="required" 适合什么场景？
        答：需要强制使用工具的场景，如必须查询最新信息
    """)


def main():
    print("⚡ Gemini Function Calling")
    print("=" * 60)

    function_calling_overview()
    basic_function_calling()
    complete_implementation()
    parallel_tool_calls()
    error_handling()
    exercises()

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：07-plan-and-execute.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
