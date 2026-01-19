"""
OpenAI API 基础
===============

学习目标：
    1. 了解 OpenAI API 的基本结构
    2. 掌握 Chat Completions API 的使用方法
    3. 理解消息角色（system、user、assistant）的作用
    4. 学会构建多轮对话

核心概念：
    - Chat Completions API：OpenAI 的对话接口
    - Messages：消息列表，包含角色和内容
    - Response：API 返回的响应结构

前置知识：
    - Python 基础
    - 已配置 OPENAI_API_KEY 环境变量

环境要求：
    - pip install openai python-dotenv
    - 配置 OPENAI_API_KEY
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
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ 错误：未设置 OPENAI_API_KEY 环境变量")
        print("\n请按以下步骤配置：")
        print("1. 复制 .env.example 为 .env")
        print("2. 在 .env 中填入你的 API Key")
        print("3. 重新运行此脚本")
        return False
    
    # 仅显示前几位，保护隐私
    masked_key = api_key[:8] + "..." + api_key[-4:]
    print(f"✅ API Key 已配置: {masked_key}")
    return True


# ==================== 第二部分：基础 API 调用 ====================

def basic_api_call():
    """最简单的 API 调用示例"""
    print("\n" + "=" * 60)
    print("第二部分：基础 API 调用")
    print("=" * 60)
    
    from openai import OpenAI
    
    # 创建客户端（自动读取 OPENAI_API_KEY 环境变量）
    client = OpenAI()
    
    print("\n📤 发送请求...")
    print("消息: '你好，请用一句话介绍你自己。'")
    
    # 最简单的 API 调用
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # 使用较便宜的模型进行测试
        messages=[
            {"role": "user", "content": "你好，请用一句话介绍你自己。"}
        ]
    )
    
    # 获取回复内容
    reply = response.choices[0].message.content
    
    print(f"\n📥 收到回复:")
    print(f"   {reply}")
    
    # 显示 token 使用情况
    print(f"\n📊 Token 使用情况:")
    print(f"   输入 tokens: {response.usage.prompt_tokens}")
    print(f"   输出 tokens: {response.usage.completion_tokens}")
    print(f"   总计 tokens: {response.usage.total_tokens}")
    
    return response


# ==================== 第三部分：理解消息角色 ====================

def understand_message_roles():
    """理解 system、user、assistant 三种角色"""
    print("\n" + "=" * 60)
    print("第三部分：理解消息角色")
    print("=" * 60)
    
    from openai import OpenAI
    client = OpenAI()
    
    print("""
消息角色说明：
┌─────────────┬────────────────────────────────────┐
│ 角色        │ 作用                               │
├─────────────┼────────────────────────────────────┤
│ system      │ 设定 AI 的角色、性格和行为规则     │
│ user        │ 用户的输入                         │
│ assistant   │ AI 的历史回复（用于多轮对话）      │
└─────────────┴────────────────────────────────────┘
    """)
    
    # 示例：使用 system 角色设定 AI 身份
    print("\n📌 示例：使用 system 设定 AI 为翻译官")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的中英翻译官。用户输入中文时翻译成英文，输入英文时翻译成中文。只输出翻译结果，不要解释。"
            },
            {
                "role": "user",
                "content": "今天天气很好"
            }
        ]
    )
    
    print(f"   输入: 今天天气很好")
    print(f"   翻译: {response.choices[0].message.content}")
    
    # 对比：不使用 system
    print("\n📌 对比：不使用 system 的情况")
    
    response2 = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "今天天气很好"}
        ]
    )
    
    print(f"   输入: 今天天气很好")
    print(f"   回复: {response2.choices[0].message.content}")
    
    print("\n💡 结论：system 角色可以有效地控制 AI 的行为模式")


# ==================== 第四部分：多轮对话 ====================

def multi_turn_conversation():
    """实现多轮对话"""
    print("\n" + "=" * 60)
    print("第四部分：多轮对话")
    print("=" * 60)
    
    from openai import OpenAI
    client = OpenAI()
    
    print("""
多轮对话原理：
- API 本身是无状态的，每次调用都是独立的
- 要实现多轮对话，需要将历史消息一起发送
- 消息列表按时间顺序排列
    """)
    
    # 初始化对话历史
    messages = [
        {"role": "system", "content": "你是一个友好的助手，回答简洁明了。"}
    ]
    
    # 模拟多轮对话
    conversations = [
        "我叫小明",
        "我喜欢编程",
        "你还记得我叫什么名字吗？"
    ]
    
    print("📝 多轮对话演示：")
    print("-" * 40)
    
    for user_input in conversations:
        # 添加用户消息
        messages.append({"role": "user", "content": user_input})
        
        # 调用 API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        # 获取回复并添加到历史
        assistant_reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_reply})
        
        print(f"\n👤 用户: {user_input}")
        print(f"🤖 助手: {assistant_reply}")
    
    print("\n" + "-" * 40)
    print(f"📊 对话历史共有 {len(messages)} 条消息")
    print("💡 AI 能记住上下文，是因为我们发送了完整的对话历史")


# ==================== 第五部分：响应结构解析 ====================

def parse_response_structure():
    """详细解析 API 响应结构"""
    print("\n" + "=" * 60)
    print("第五部分：响应结构解析")
    print("=" * 60)
    
    from openai import OpenAI
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "说 hello"}]
    )
    
    print("\n📦 完整响应结构：")
    print(f"""
response.id          = {response.id}
response.model       = {response.model}
response.created     = {response.created}
response.object      = {response.object}

response.choices[0]:
  .index             = {response.choices[0].index}
  .message.role      = {response.choices[0].message.role}
  .message.content   = {response.choices[0].message.content}
  .finish_reason     = {response.choices[0].finish_reason}

response.usage:
  .prompt_tokens     = {response.usage.prompt_tokens}
  .completion_tokens = {response.usage.completion_tokens}
  .total_tokens      = {response.usage.total_tokens}
    """)
    
    print("💡 finish_reason 说明：")
    print("   - 'stop': 正常完成")
    print("   - 'length': 达到 max_tokens 限制")
    print("   - 'tool_calls': 模型请求调用工具")


# ==================== 第六部分：练习与思考 ====================

def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    exercises_text = """
练习 1：修改 system 提示词
    尝试将 AI 设定为不同的角色（如：诗人、程序员、厨师），
    观察相同问题下回复的差异。

练习 2：实现一个简单的命令行聊天机器人
    使用 while 循环和 input() 实现真正的交互式对话。
    提示：参考 multi_turn_conversation() 的实现。

练习 3：计算对话成本
    GPT-3.5 Turbo 的价格约为 $0.0005/1K 输入 tokens 和 $0.0015/1K 输出 tokens。
    修改代码，在每次对话后显示预估成本。

思考题：
    1. 为什么 API 需要发送完整的对话历史？这有什么优缺点？
    2. 如果对话历史太长，可能会遇到什么问题？如何解决？
    """
    print(exercises_text)


# ==================== 主函数 ====================

def main():
    """主函数 - 按顺序执行所有部分"""
    print("🚀 OpenAI API 基础课程")
    print("=" * 60)
    print("⚠️ 注意：本课程将调用 OpenAI API，会产生少量费用")
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
