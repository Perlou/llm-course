"""
LLM API 基础 (Gemini 版本)
===========================

学习目标：
    1. 了解 LLM API 的基本结构
    2. 掌握 Google Gemini API 的使用方法
    3. 理解消息角色（system、user、assistant）的作用
    4. 学会构建多轮对话

核心概念：
    - Gemini API：Google 的多模态 AI 接口
    - Messages：消息列表，包含角色和内容
    - Response：API 返回的响应结构

前置知识：
    - Python 基础
    - 已配置 GOOGLE_API_KEY 环境变量

环境要求：
    - pip install google-generativeai python-dotenv
    - 配置 GOOGLE_API_KEY
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


# ==================== 第一部分：环境检查 ====================


def check_environment():
    """检查 API Key 是否配置"""
    print("=" * 60)
    print("第一部分：环境检查")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY 环境变量")
        print("\n请按以下步骤配置：")
        print("1. 复制 .env.example 为 .env")
        print("2. 在 .env 中填入你的 Google API Key")
        print("3. 获取地址：https://aistudio.google.com/apikey")
        print("4. 重新运行此脚本")
        return False

    # 仅显示前几位，保护隐私
    masked_key = api_key[:8] + "..." + api_key[-4:]
    print(f"✅ Google API Key 已配置: {masked_key}")
    return True


# ==================== 第二部分：基础 API 调用 ====================


def basic_api_call():
    """最简单的 API 调用示例"""
    print("\n" + "=" * 60)
    print("第二部分：基础 API 调用")
    print("=" * 60)

    import google.generativeai as genai

    # 配置 API Key
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    # 创建模型实例
    model = genai.GenerativeModel("gemini-2.0-flash")

    print("\n📤 发送请求...")
    print("消息: '你好，请用一句话介绍你自己。'")

    # 最简单的 API 调用
    response = model.generate_content("你好，请用一句话介绍你自己。")

    # 获取回复内容
    reply = response.text

    print(f"\n📥 收到回复:")
    print(f"   {reply}")

    # 显示 token 使用情况
    if hasattr(response, "usage_metadata"):
        print(f"\n📊 Token 使用情况:")
        print(f"   输入 tokens: {response.usage_metadata.prompt_token_count}")
        print(f"   输出 tokens: {response.usage_metadata.candidates_token_count}")
        print(f"   总计 tokens: {response.usage_metadata.total_token_count}")

    return response


# ==================== 第三部分：理解消息角色 ====================


def understand_message_roles():
    """理解 system、user 角色的作用"""
    print("\n" + "=" * 60)
    print("第三部分：理解消息角色")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    print("""
消息角色说明（Gemini 版本）：
┌─────────────────┬────────────────────────────────────┐
│ 角色            │ 作用                               │
├─────────────────┼────────────────────────────────────┤
│ system_instruction │ 设定 AI 的角色、性格和行为规则  │
│ user            │ 用户的输入                         │
│ model           │ AI 的历史回复（用于多轮对话）      │
└─────────────────┴────────────────────────────────────┘
    """)

    # 示例：使用 system_instruction 设定 AI 身份
    print("\n📌 示例：使用 system_instruction 设定 AI 为翻译官")

    # Gemini 在创建模型时设置系统指令
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        system_instruction="你是一个专业的中英翻译官。用户输入中文时翻译成英文，输入英文时翻译成中文。只输出翻译结果，不要解释。",
    )

    response = model.generate_content("今天天气很好")

    print(f"   输入: 今天天气很好")
    print(f"   翻译: {response.text}")

    # 对比：不使用 system_instruction
    print("\n📌 对比：不使用 system_instruction 的情况")

    model2 = genai.GenerativeModel("gemini-2.0-flash")
    response2 = model2.generate_content("今天天气很好")

    print(f"   输入: 今天天气很好")
    print(f"   回复: {response2.text}")

    print("\n💡 结论：system_instruction 可以有效地控制 AI 的行为模式")


# ==================== 第四部分：多轮对话 ====================


def multi_turn_conversation():
    """实现多轮对话"""
    print("\n" + "=" * 60)
    print("第四部分：多轮对话")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    print("""
多轮对话原理：
- Gemini 使用 start_chat() 创建对话会话
- 会话会自动维护对话历史
- 无需手动管理消息列表
    """)

    # 创建模型和对话
    model = genai.GenerativeModel(
        "gemini-2.0-flash", system_instruction="你是一个友好的助手，回答简洁明了。"
    )
    chat = model.start_chat(history=[])

    # 模拟多轮对话
    conversations = ["我叫小明", "我喜欢编程", "你还记得我叫什么名字吗？"]

    print("📝 多轮对话演示：")
    print("-" * 40)

    for user_input in conversations:
        response = chat.send_message(user_input)
        print(f"\n👤 用户: {user_input}")
        print(f"🤖 助手: {response.text}")

    print("\n" + "-" * 40)
    print(f"📊 对话历史共有 {len(chat.history)} 条消息")
    print("💡 Gemini 的 chat 对象会自动管理对话历史")


# ==================== 第五部分：响应结构解析 ====================


def parse_response_structure():
    """详细解析 API 响应结构"""
    print("\n" + "=" * 60)
    print("第五部分：响应结构解析")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content("说 hello")

    print("\n📦 Gemini 响应结构：")
    print(f"""
response.text            = {response.text}
response.candidates      = 候选回复列表

response.candidates[0]:
  .content.parts[0].text = {response.candidates[0].content.parts[0].text}
  .finish_reason         = {response.candidates[0].finish_reason}
  .safety_ratings        = 安全评分列表

response.usage_metadata:
  .prompt_token_count    = {response.usage_metadata.prompt_token_count if hasattr(response, "usage_metadata") else "N/A"}
  .candidates_token_count = {response.usage_metadata.candidates_token_count if hasattr(response, "usage_metadata") else "N/A"}
    """)

    print("💡 finish_reason 说明：")
    print("   - 'STOP': 正常完成")
    print("   - 'MAX_TOKENS': 达到 token 限制")
    print("   - 'SAFETY': 被安全过滤器阻止")


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    exercises_text = """
练习 1：修改 system_instruction
    尝试将 AI 设定为不同的角色（如：诗人、程序员、厨师），
    观察相同问题下回复的差异。

练习 2：实现一个简单的命令行聊天机器人
    使用 while 循环和 input() 实现真正的交互式对话。
    提示：参考 multi_turn_conversation() 的实现。

练习 3：对比 OpenAI 和 Gemini 的差异
    如果有 OpenAI API Key，对比两者的：
    - API 调用方式
    - 响应格式
    - 速度和质量

思考题：
    1. Gemini 的 chat 对象自动管理历史，这与手动管理相比有什么优缺点？
    2. system_instruction 和 chat history 中的 system 消息有什么区别？
    """
    print(exercises_text)


# ==================== 主函数 ====================


def main():
    """主函数 - 按顺序执行所有部分"""
    print("🚀 LLM API 基础课程 (Gemini 版本)")
    print("=" * 60)
    print("💡 本课程使用 Google Gemini API（免费额度较多）")
    print("预估消耗：约 500-1000 tokens")
    print("=" * 60)

    # 检查环境
    if not check_environment():
        return

    # 按顺序执行各部分
    try:
        basic_api_call()
        understand_message_roles()
        multi_turn_conversation()
        parse_response_structure()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("请检查网络连接和 API Key 是否正确")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！")
    print("下一步：02-openai-parameters.py（API 参数详解）")
    print("=" * 60)


if __name__ == "__main__":
    main()
