"""
指令优化技巧 (Gemini 版本)
==========================

学习目标：
    1. 掌握清晰指令的编写方法
    2. 学会分解复杂任务
    3. 理解指令的优化迭代过程

核心概念：
    - 指令清晰度：明确、无歧义的表达
    - 任务分解：将复杂任务拆分为步骤
    - 迭代优化：根据结果调整指令

前置知识：
    - 02-system-prompts.py

环境要求：
    - pip install google-generativeai python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：指令清晰度 ====================


def instruction_clarity():
    """指令清晰度"""
    print("=" * 60)
    print("第一部分：指令清晰度")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    print("""
    模糊指令 vs 清晰指令：
    ─────────────────────
    
    ❌ 模糊：写点东西介绍 AI
    ✅ 清晰：写一段 100 字的科普文章，面向高中生，介绍人工智能的基本概念
    """)

    # 模糊指令
    print("📌 模糊指令：")
    r1 = model.generate_content(
        "写点东西介绍 AI", generation_config={"max_output_tokens": 200}
    )
    print(f"回复长度: {len(r1.text)} 字符")

    # 清晰指令
    print("\n📌 清晰指令：")
    r2 = model.generate_content(
        "写一段 100 字的科普文章，面向高中生，介绍人工智能的基本概念。要求通俗易懂，不使用专业术语。",
        generation_config={"max_output_tokens": 200},
    )
    print(f"回复：\n{r2.text}")


# ==================== 第二部分：使用分隔符 ====================


def use_delimiters():
    """使用分隔符"""
    print("\n" + "=" * 60)
    print("第二部分：使用分隔符")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    print("""
    分隔符的作用：
    ─────────────
    - 区分指令和数据
    - 防止注入攻击
    - 结构更清晰
    
    常用分隔符：```、\"\"\"、###、---、<tag></tag>
    """)

    # 使用分隔符
    prompt = '''请总结以下文章的要点：

"""
人工智能正在改变各行各业。从医疗诊断到自动驾驶，
AI技术的应用越来越广泛。专家预测，未来十年AI
将创造数百万个新工作岗位。
"""

请用3个要点总结。'''

    print("📌 使用分隔符隔离内容：")
    response = model.generate_content(
        prompt, generation_config={"max_output_tokens": 200}
    )
    print(f"回复：\n{response.text}")


# ==================== 第三部分：分步骤指令 ====================


def step_by_step():
    """分步骤指令"""
    print("\n" + "=" * 60)
    print("第三部分：分步骤指令")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    # 一次性复杂指令
    print("📌 复杂指令拆分为步骤：")

    step_prompt = """请按照以下步骤分析这段代码：

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

步骤1：解释代码功能
步骤2：分析时间复杂度
步骤3：指出潜在问题
步骤4：给出优化建议"""

    response = model.generate_content(
        step_prompt, generation_config={"max_output_tokens": 400}
    )
    print(f"回复：\n{response.text}")


# ==================== 第四部分：提供示例 ====================


def provide_examples():
    """提供示例"""
    print("\n" + "=" * 60)
    print("第四部分：提供示例")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    # 无示例
    print("📌 无示例 vs 有示例：")

    example_prompt = """请将情感词转换为表情符号。

示例：
- 开心 → 😊
- 悲伤 → 😢
- 愤怒 → 😠

现在转换：惊讶"""

    response = model.generate_content(
        example_prompt, generation_config={"max_output_tokens": 50}
    )
    print(f"回复: {response.text}")


# ==================== 第五部分：指定输出长度 ====================


def specify_length():
    """指定输出长度"""
    print("\n" + "=" * 60)
    print("第五部分：指定输出长度")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompts = [
        ("一句话", "用一句话解释机器学习"),
        ("三点", "用三个要点介绍深度学习，每点不超过20字"),
        ("段落", "用一段话（约100字）解释神经网络"),
    ]

    for name, prompt in prompts:
        response = model.generate_content(
            prompt, generation_config={"max_output_tokens": 200}
        )
        print(f"\n📌 {name}格式:")
        print(response.text)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：改写模糊指令
        将"帮我写个代码"改写成清晰的指令。

    练习 2：使用分隔符
        设计一个安全的文本摘要指令，防止内容注入。

    练习 3：分步骤任务
        设计一个分步骤的数据分析指令。

    思考题：
        1. 指令越详细越好吗？
        2. 如何判断指令是否足够清晰？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 指令优化技巧 (Gemini 版本)")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
        return

    try:
        instruction_clarity()
        use_delimiters()
        step_by_step()
        provide_examples()
        specify_length()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：04-few-shot-learning.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
