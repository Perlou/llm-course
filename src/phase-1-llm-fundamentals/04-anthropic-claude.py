"""
Anthropic Claude API 使用
=========================

学习目标：
    1. 了解 Claude 的特点和优势
    2. 掌握 Anthropic API 的使用方法
    3. 理解 Claude 与 OpenAI API 的差异
    4. 学会利用 Claude 的长上下文能力

核心概念：
    - Claude：Anthropic 开发的 AI 助手
    - Messages API：Claude 的对话接口
    - 长上下文：Claude 支持最多 200K tokens

前置知识：
    - 完成 01-openai-api-basics.py

环境要求：
    - pip install anthropic python-dotenv
    - 配置 ANTHROPIC_API_KEY
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Claude 介绍 ====================


def claude_introduction():
    """Claude 模型介绍"""
    print("=" * 60)
    print("第一部分：Claude 介绍")
    print("=" * 60)

    print("""
Claude 模型家族：
┌───────────────────┬────────────┬────────────┬─────────────────────┐
│ 模型              │ 上下文长度 │ 相对成本   │ 特点                │
├───────────────────┼────────────┼────────────┼─────────────────────┤
│ Claude 3.5 Sonnet │ 200K      │ 中         │ 最强综合能力        │
│ Claude 3 Opus     │ 200K      │ 高         │ 复杂推理            │
│ Claude 3 Haiku    │ 200K      │ 低         │ 快速响应，低成本    │
└───────────────────┴────────────┴────────────┴─────────────────────┘

Claude 的优势：
1. 超长上下文（200K tokens ≈ 一本书）
2. 强大的推理能力
3. 出色的中文能力
4. 安全性设计（Constitutional AI）
5. 更少的幻觉
    """)


# ==================== 第二部分：基础 API 调用 ====================


def basic_claude_api():
    """Claude 基础 API 调用"""
    print("\n" + "=" * 60)
    print("第二部分：基础 API 调用")
    print("=" * 60)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️ 未配置 ANTHROPIC_API_KEY，跳过实际 API 调用")
        print("\n📝 示例代码：")
        show_claude_example_code()
        return

    from anthropic import Anthropic

    client = Anthropic()

    print("\n📤 发送请求...")

    # Claude API 调用
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # 最新的 Claude 3.5 Sonnet
        max_tokens=1024,
        messages=[{"role": "user", "content": "请用一句话介绍你自己。"}],
    )

    print(f"\n📥 收到回复:")
    print(f"   {message.content[0].text}")

    print(f"\n📊 Token 使用情况:")
    print(f"   输入 tokens: {message.usage.input_tokens}")
    print(f"   输出 tokens: {message.usage.output_tokens}")


def show_claude_example_code():
    """显示 Claude API 示例代码"""
    print("""
from anthropic import Anthropic

client = Anthropic()  # 自动读取 ANTHROPIC_API_KEY

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "你好！"}
    ]
)

print(message.content[0].text)
    """)


# ==================== 第三部分：System Prompt 使用 ====================


def claude_system_prompt():
    """Claude 的 System Prompt"""
    print("\n" + "=" * 60)
    print("第三部分：System Prompt 使用")
    print("=" * 60)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️ 未配置 ANTHROPIC_API_KEY，显示示例代码")
        show_system_prompt_example()
        return

    from anthropic import Anthropic

    client = Anthropic()

    print("""
💡 Claude 的 system 参数是顶层参数，而不是消息角色

OpenAI 风格:
  messages=[{"role": "system", "content": "..."}, ...]

Claude 风格:
  system="...",
  messages=[...]
    """)

    # 使用 system 参数
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system="你是一个专业的中英翻译官。用户输入中文翻译成英文。只输出翻译结果。",
        messages=[{"role": "user", "content": "今天天气真好"}],
    )

    print(f"📝 翻译示例:")
    print(f"   输入: 今天天气真好")
    print(f"   输出: {message.content[0].text}")


def show_system_prompt_example():
    """显示 system prompt 示例"""
    print("""
# Claude 使用单独的 system 参数

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system="你是一个专业的翻译官...",  # 注意：这是单独的参数
    messages=[
        {"role": "user", "content": "今天天气真好"}
    ]
)
    """)


# ==================== 第四部分：流式响应 ====================


def claude_streaming():
    """Claude 流式响应"""
    print("\n" + "=" * 60)
    print("第四部分：流式响应")
    print("=" * 60)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️ 未配置 ANTHROPIC_API_KEY，显示示例代码")
        show_streaming_example()
        return

    from anthropic import Anthropic

    client = Anthropic()

    print("📝 流式输出演示：")
    print("-" * 40)
    print("回复: ", end="", flush=True)

    with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        max_tokens=256,
        messages=[{"role": "user", "content": "写一首关于编程的俳句"}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    print("\n")


def show_streaming_example():
    """显示流式示例代码"""
    print("""
# Claude 流式响应

with client.messages.stream(
    model="claude-3-5-sonnet-20241022",
    max_tokens=256,
    messages=[{"role": "user", "content": "..."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    """)


# ==================== 第五部分：与 OpenAI 的差异 ====================


def compare_with_openai():
    """对比 Claude 和 OpenAI API"""
    print("\n" + "=" * 60)
    print("第五部分：Claude vs OpenAI API 差异")
    print("=" * 60)

    print("""
┌─────────────────┬───────────────────────┬───────────────────────┐
│ 特性            │ OpenAI                │ Claude                │
├─────────────────┼───────────────────────┼───────────────────────┤
│ 客户端          │ OpenAI()              │ Anthropic()           │
├─────────────────┼───────────────────────┼───────────────────────┤
│ 方法名          │ chat.completions.     │ messages.create()     │
│                 │ create()              │                       │
├─────────────────┼───────────────────────┼───────────────────────┤
│ System 设置     │ 作为 message 角色     │ 单独的 system 参数    │
├─────────────────┼───────────────────────┼───────────────────────┤
│ max_tokens      │ 可选                  │ 必填                  │
├─────────────────┼───────────────────────┼───────────────────────┤
│ 响应内容        │ response.choices[0]   │ message.content[0]    │
│                 │ .message.content      │ .text                 │
├─────────────────┼───────────────────────┼───────────────────────┤
│ 流式响应        │ stream=True           │ messages.stream()     │
└─────────────────┴───────────────────────┴───────────────────────┘

代码对比：

# OpenAI
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."}
    ]
)
print(response.choices[0].message.content)

# Claude
from anthropic import Anthropic
client = Anthropic()
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,  # Claude 必须指定
    system="...",     # system 是单独参数
    messages=[
        {"role": "user", "content": "..."}
    ]
)
print(message.content[0].text)
    """)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    exercises_text = """
练习 1：封装统一接口
    创建一个函数，接受模型名称参数，
    自动选择调用 OpenAI 或 Claude API。

练习 2：长文档处理
    利用 Claude 的长上下文能力，
    读取一个长文档（如 README.md）并让 Claude 总结。

练习 3：多轮对话
    实现一个同时支持 OpenAI 和 Claude 的多轮对话函数。

练习 4：模型对比
    对同一个问题，分别调用 GPT-4 和 Claude，
    对比回答质量和响应速度。

思考题：
    1. 为什么 Claude 要求必须指定 max_tokens？
    2. Claude 的 200K 上下文能处理多长的文档？
    3. 在什么场景下你会选择 Claude 而不是 GPT-4？
    """
    print(exercises_text)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 Anthropic Claude API 使用")
    print("=" * 60)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print("✅ ANTHROPIC_API_KEY 已配置")
        print("⚠️ 注意：本课程会调用 Claude API，产生少量费用")
    else:
        print("⚠️ ANTHROPIC_API_KEY 未配置，将以演示模式运行")
        print("   如需实际运行，请在 .env 中配置 API Key")
    print("=" * 60)

    try:
        claude_introduction()
        basic_claude_api()
        claude_system_prompt()
        claude_streaming()
        compare_with_openai()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！")
    print("下一步：05-google-gemini.py（Gemini API 使用）")
    print("=" * 60)


if __name__ == "__main__":
    main()
