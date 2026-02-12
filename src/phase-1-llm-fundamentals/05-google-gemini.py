"""
Google Gemini API 使用
=====================

学习目标：
    1. 了解 Gemini 的特点和优势
    2. 掌握 Google AI API 的使用方法
    3. 理解 Gemini 的多模态能力
    4. 学会使用 Gemini 的长上下文

核心概念：
    - Gemini：Google 的多模态 AI 模型
    - 多模态：支持文本、图像、音频、视频输入
    - 长上下文：Gemini 1.5 Pro 支持 100 万 tokens

前置知识：
    - 完成 01-openai-api-basics.py

环境要求：
    - pip install google-generativeai python-dotenv
    - 配置 GOOGLE_API_KEY
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Gemini 介绍 ====================


def gemini_introduction():
    """Gemini 模型介绍"""
    print("=" * 60)
    print("第一部分：Gemini 介绍")
    print("=" * 60)

    print("""
Gemini 模型家族：
┌─────────────────────┬────────────┬────────────┬──────────────────────┐
│ 模型                │ 上下文长度 │ 相对成本   │ 特点                 │
├─────────────────────┼────────────┼────────────┼──────────────────────┤
│ Gemini 1.5 Pro      │ 2M        │ 中         │ 最强综合能力         │
│ Gemini 1.5 Flash    │ 1M        │ 低         │ 快速响应             │
│ Gemini 2.0 Flash    │ 1M        │ 低         │ 最新实验版           │
└─────────────────────┴────────────┴────────────┴──────────────────────┘

Gemini 的优势：
1. 超长上下文（最高 200 万 tokens）
2. 原生多模态（图像、视频、音频、PDF）
3. 代码能力强
4. 免费额度较大（适合学习）
5. 与 Google 生态集成
    """)


# ==================== 第二部分：基础 API 调用 ====================


def basic_gemini_api():
    """Gemini 基础 API 调用"""
    print("\n" + "=" * 60)
    print("第二部分：基础 API 调用")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️ 未配置 GOOGLE_API_KEY，跳过实际 API 调用")
        print("\n📝 示例代码：")
        show_gemini_example_code()
        return

    import google.generativeai as genai

    # 配置 API Key
    genai.configure(api_key=api_key)

    # 创建模型实例
    model = genai.GenerativeModel("gemini-2.0-flash")

    print("\n📤 发送请求...")

    # 简单对话
    response = model.generate_content("请用一句话介绍你自己。")

    print(f"\n📥 收到回复:")
    print(f"   {response.text}")

    # 显示 token 信息（如果可用）
    if hasattr(response, "usage_metadata"):
        print(f"\n📊 Token 使用情况:")
        print(f"   输入 tokens: {response.usage_metadata.prompt_token_count}")
        print(f"   输出 tokens: {response.usage_metadata.candidates_token_count}")


def show_gemini_example_code():
    """显示 Gemini API 示例代码"""
    print("""
import google.generativeai as genai

# 配置 API Key
genai.configure(api_key="your-api-key")

# 创建模型实例
model = genai.GenerativeModel("gemini-2.0-flash")

# 生成回复
response = model.generate_content("你好！")
print(response.text)
    """)


# ==================== 第三部分：多轮对话 ====================


def gemini_chat():
    """Gemini 多轮对话"""
    print("\n" + "=" * 60)
    print("第三部分：多轮对话")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️ 未配置 GOOGLE_API_KEY，显示示例代码")
        show_chat_example()
        return

    import google.generativeai as genai

    genai.configure(api_key=api_key)

    print("""
💡 Gemini 使用 start_chat() 创建对话会话
   会话会自动维护对话历史
    """)

    model = genai.GenerativeModel("gemini-2.0-flash")

    # 开始多轮对话
    chat = model.start_chat(history=[])

    conversations = [
        "我叫小明",
        "我是一名程序员",
        "你还记得我叫什么名字吗？我的职业是什么？",
    ]

    print("📝 多轮对话演示：")
    print("-" * 40)

    for user_input in conversations:
        response = chat.send_message(user_input)
        print(f"\n👤 用户: {user_input}")
        print(f"🤖 Gemini: {response.text}")

    print(f"\n📊 对话历史长度: {len(chat.history)} 条")


def show_chat_example():
    """显示多轮对话示例"""
    print("""
# Gemini 多轮对话

model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat(history=[])

# 发送消息
response = chat.send_message("你好")
print(response.text)

# 继续对话（自动保持上下文）
response = chat.send_message("记住我叫小明")
print(response.text)
    """)


# ==================== 第四部分：流式响应 ====================


def gemini_streaming():
    """Gemini 流式响应"""
    print("\n" + "=" * 60)
    print("第四部分：流式响应")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️ 未配置 GOOGLE_API_KEY，显示示例代码")
        show_streaming_example()
        return

    import google.generativeai as genai

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-2.0-flash")

    print("📝 流式输出演示：")
    print("-" * 40)
    print("回复: ", end="", flush=True)

    response = model.generate_content("写一首关于星空的俳句", stream=True)

    for chunk in response:
        print(chunk.text, end="", flush=True)

    print("\n")


def show_streaming_example():
    """显示流式示例"""
    print("""
# Gemini 流式响应

response = model.generate_content(
    "你的提示词",
    stream=True  # 启用流式
)

for chunk in response:
    print(chunk.text, end="", flush=True)
    """)


# ==================== 第五部分：系统指令 ====================


def gemini_system_instruction():
    """Gemini 系统指令"""
    print("\n" + "=" * 60)
    print("第五部分：系统指令")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️ 未配置 GOOGLE_API_KEY，显示示例代码")
        show_system_instruction_example()
        return

    import google.generativeai as genai

    genai.configure(api_key=api_key)

    print("""
💡 Gemini 在创建模型时设置系统指令
   使用 system_instruction 参数
    """)

    # 创建带系统指令的模型
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        system_instruction="你是一个专业的翻译官。只输出翻译结果，不要解释。",
    )

    response = model.generate_content("Hello, how are you today?")

    print(f"📝 翻译示例:")
    print(f"   输入: Hello, how are you today?")
    print(f"   输出: {response.text}")


def show_system_instruction_example():
    """显示系统指令示例"""
    print("""
# Gemini 系统指令

model = genai.GenerativeModel(
    "gemini-2.0-flash",
    system_instruction="你是一个专业的翻译官..."  # 在创建模型时设置
)

response = model.generate_content("Hello!")
print(response.text)
    """)


# ==================== 第六部分：与其他 API 对比 ====================


def compare_apis():
    """对比三大 API"""
    print("\n" + "=" * 60)
    print("第六部分：三大 LLM API 对比")
    print("=" * 60)

    print("""
┌─────────────────┬───────────────────┬───────────────────┬───────────────────┐
│ 特性            │ OpenAI            │ Claude            │ Gemini            │
├─────────────────┼───────────────────┼───────────────────┼───────────────────┤
│ 最强模型        │ GPT-4o            │ Claude 3.5 Sonnet │ Gemini 1.5 Pro    │
├─────────────────┼───────────────────┼───────────────────┼───────────────────┤
│ 上下文长度      │ 128K              │ 200K              │ 2M                │
├─────────────────┼───────────────────┼───────────────────┼───────────────────┤
│ 多模态          │ 支持              │ 支持              │ 原生支持          │
├─────────────────┼───────────────────┼───────────────────┼───────────────────┤
│ 免费额度        │ 少                │ 少                │ 较多              │
├─────────────────┼───────────────────┼───────────────────┼───────────────────┤
│ System 设置     │ message 角色      │ system 参数       │ 模型参数          │
├─────────────────┼───────────────────┼───────────────────┼───────────────────┤
│ 库名称          │ openai            │ anthropic         │ google-genai      │
└─────────────────┴───────────────────┴───────────────────┴───────────────────┘

选择建议：
- 通用任务 → OpenAI GPT-4o（生态最完善）
- 长文档/推理 → Claude（逻辑能力强）
- 多模态/免费 → Gemini（视频/音频支持好）
- 中文任务 → Claude 或 Qwen
    """)


# ==================== 第七部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    exercises_text = """
练习 1：统一 API 封装
    创建一个 LLMClient 类，封装 OpenAI、Claude、Gemini，
    提供统一的 chat() 方法。

练习 2：长文档处理
    利用 Gemini 的超长上下文，
    读取一个较大的文本文件并进行总结。

练习 3：多模态尝试（需要 Gemini）
    使用 Gemini 分析一张图片的内容。
    提示：可以使用 PIL 库加载图片。

练习 4：成本对比
    计算三个 API 处理相同任务的成本差异。

思考题：
    1. 为什么 Gemini 能支持如此长的上下文？
    2. 原生多模态和 GPT-4V 的区别是什么？
    3. 如何设计一个故障转移机制，当一个 API 失败时切换到另一个？
    """
    print(exercises_text)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 Google Gemini API 使用")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print("✅ GOOGLE_API_KEY 已配置")
        print("💡 Gemini 有较多免费额度，适合学习使用")
    else:
        print("⚠️ GOOGLE_API_KEY 未配置，将以演示模式运行")
        print("   如需实际运行，请在 .env 中配置 API Key")
    print("=" * 60)

    try:
        gemini_introduction()
        basic_gemini_api()
        gemini_chat()
        gemini_streaming()
        gemini_system_instruction()
        compare_apis()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！")
    print("下一步：06-local-llm-ollama.py（本地 LLM 部署）")
    print("=" * 60)


if __name__ == "__main__":
    main()
