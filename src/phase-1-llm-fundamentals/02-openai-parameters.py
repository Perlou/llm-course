"""
LLM API 参数详解 (Gemini 版本)
==============================

学习目标：
    1. 理解 temperature 参数对输出的影响
    2. 掌握 top_p 核采样的原理
    3. 学会使用 max_output_tokens 控制输出长度
    4. 了解 Gemini 特有的参数设置

核心概念：
    - Temperature：控制输出的随机性/创造性
    - Top_p：核采样，另一种控制随机性的方式
    - Max_output_tokens：限制输出的最大 token 数
    - Top_k：Gemini 特有，限制候选词数量

前置知识：
    - 完成 01-openai-api-basics.py

环境要求：
    - pip install google-generativeai python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Temperature 参数 ====================


def explore_temperature():
    """探索 temperature 参数的影响"""
    print("=" * 60)
    print("第一部分：Temperature 参数")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    print("""
Temperature 参数说明：
┌────────────────┬─────────────────────────────────────┐
│ 值             │ 效果                                 │
├────────────────┼─────────────────────────────────────┤
│ 0.0            │ 确定性输出，每次结果相同             │
│ 0.5 - 0.7      │ 平衡创造性和一致性（推荐默认值）     │
│ 1.0            │ 更具创造性，输出多样                 │
│ 1.5 - 2.0      │ 高度随机，可能不连贯                 │
└────────────────┴─────────────────────────────────────┘
    """)

    prompt = "用一个词描述太阳"
    temperatures = [0.0, 0.5, 1.0, 1.5]

    print(f"📝 测试提示词: '{prompt}'")
    print("-" * 40)

    for temp in temperatures:
        print(f"\n🌡️ Temperature = {temp}")

        model = genai.GenerativeModel("gemini-2.0-flash")

        # 同一个 temperature 调用 3 次，观察一致性
        results = []
        for i in range(3):
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temp,
                    max_output_tokens=20,
                ),
            )
            results.append(response.text.strip())

        for i, result in enumerate(results, 1):
            print(f"   第{i}次: {result}")

    print("\n💡 观察：temperature=0 时，输出完全一致；值越高，变化越大")


# ==================== 第二部分：Top_p 核采样 ====================


def explore_top_p():
    """探索 top_p 参数"""
    print("\n" + "=" * 60)
    print("第二部分：Top_p 核采样")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    print("""
Top_p 参数说明：
- 也称为"核采样"(nucleus sampling)
- 控制从概率最高的 tokens 中采样
- top_p=0.1: 只从累计概率前 10% 的 tokens 采样
- top_p=1.0: 考虑所有 tokens

⚠️ 注意：一般只调整 temperature 或 top_p 其中之一
    """)

    prompt = "写一个关于月亮的短句"
    top_p_values = [0.1, 0.5, 0.9]

    print(f"📝 测试提示词: '{prompt}'")
    print("-" * 40)

    model = genai.GenerativeModel("gemini-2.0-flash")

    for top_p in top_p_values:
        print(f"\n🎯 Top_p = {top_p}")

        for i in range(2):
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=1.0,  # 固定 temperature
                    top_p=top_p,
                    max_output_tokens=30,
                ),
            )
            print(f"   第{i + 1}次: {response.text.strip()}")

    print("\n💡 top_p 越小，输出越保守；越大，越多样")


# ==================== 第三部分：Max_output_tokens 参数 ====================


def explore_max_tokens():
    """探索 max_output_tokens 参数"""
    print("\n" + "=" * 60)
    print("第三部分：Max_output_tokens 参数")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    print("""
Max_output_tokens 参数说明：
- 限制 AI 回复的最大 token 数
- 如果回复被截断，finish_reason 会是 'MAX_TOKENS'
- 1 个中文字符约 1-2 tokens
- 1 个英文单词约 1-2 tokens
    """)

    prompt = "请详细解释什么是人工智能，包括其历史、应用和未来发展。"
    max_tokens_values = [20, 50, 200]

    print(f"📝 测试提示词: '{prompt}'")
    print("-" * 40)

    model = genai.GenerativeModel("gemini-2.0-flash")

    for max_tokens in max_tokens_values:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
            ),
        )

        content = response.text
        finish_reason = response.candidates[0].finish_reason.name

        print(f"\n📏 Max_output_tokens = {max_tokens}")
        print(f"   回复: {content[:100]}{'...' if len(content) > 100 else ''}")
        if hasattr(response, "usage_metadata"):
            print(f"   实际 tokens: {response.usage_metadata.candidates_token_count}")
        print(f"   结束原因: {finish_reason}")

        if finish_reason == "MAX_TOKENS":
            print("   ⚠️ 回复被截断!")


# ==================== 第四部分：Top_k 参数 (Gemini 特有) ====================


def explore_top_k():
    """探索 top_k 参数 (Gemini 特有)"""
    print("\n" + "=" * 60)
    print("第四部分：Top_k 参数 (Gemini 特有)")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    print("""
Top_k 参数说明：
- Gemini 特有的采样参数
- 只从概率最高的 k 个 tokens 中采样
- top_k=1: 相当于贪婪采样 (只选最高概率)
- top_k=40: 从前 40 个候选中采样

与 top_p 的区别：
- top_k 是固定数量
- top_p 是累计概率
    """)

    prompt = "给这只猫起一个有趣的名字"
    top_k_values = [1, 10, 40]

    print(f"📝 测试提示词: '{prompt}'")
    print("-" * 40)

    model = genai.GenerativeModel("gemini-2.0-flash")

    for top_k in top_k_values:
        print(f"\n🔢 Top_k = {top_k}")

        for i in range(2):
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=1.0,
                    top_k=top_k,
                    max_output_tokens=20,
                ),
            )
            print(f"   第{i + 1}次: {response.text.strip()}")


# ==================== 第五部分：参数组合建议 ====================


def parameter_recommendations():
    """不同场景下的参数组合建议"""
    print("\n" + "=" * 60)
    print("第五部分：参数组合建议")
    print("=" * 60)

    print("""
📋 不同场景推荐参数 (Gemini)：

┌──────────────────┬─────────────┬────────┬────────┬──────────────────┐
│ 场景             │ temperature │ top_p  │ top_k  │ 说明             │
├──────────────────┼─────────────┼────────┼────────┼──────────────────┤
│ 代码生成         │ 0.0 - 0.2   │ 1.0    │ 40     │ 需要精确性       │
│ 数据提取/解析    │ 0.0         │ 1.0    │ 1      │ 需要确定性结果   │
│ 翻译             │ 0.2 - 0.4   │ 1.0    │ 40     │ 保持准确但有灵活 │
│ 客服对话         │ 0.5 - 0.7   │ 1.0    │ 40     │ 自然但可控       │
│ 创意写作         │ 0.8 - 1.2   │ 0.9    │ 100    │ 需要多样性       │
│ 头脑风暴         │ 1.0 - 1.5   │ 0.8    │ 100    │ 最大创造性       │
└──────────────────┴─────────────┴────────┴────────┴──────────────────┘

💡 小贴士：
1. 先从默认值开始（temperature=1.0）
2. 根据需要调整一个参数，不要同时调整多个
3. 代码和数据任务用低 temperature
4. 创意任务可以提高 temperature 和 top_k
5. 使用 max_output_tokens 防止输出过长

📝 OpenAI vs Gemini 参数对比：
┌────────────────────┬────────────────────────┐
│ OpenAI             │ Gemini                 │
├────────────────────┼────────────────────────┤
│ temperature        │ temperature            │
│ top_p              │ top_p                  │
│ max_tokens         │ max_output_tokens      │
│ frequency_penalty  │ (无直接对应)           │
│ presence_penalty   │ (无直接对应)           │
│ (无)               │ top_k                  │
└────────────────────┴────────────────────────┘
    """)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    exercises_text = """
练习 1：参数对比实验
    选择一个任务（如写诗、写代码、回答问题），
    分别使用不同的 temperature 值（0, 0.5, 1.0, 1.5），
    记录输出质量和一致性的变化。

练习 2：找到最佳参数
    假设你要构建一个代码生成助手，
    实验找出最适合生成 Python 代码的参数组合。

练习 3：Top_k vs Top_p
    使用相同的提示词，对比 top_k 和 top_p 的效果差异。
    思考：什么场景下用 top_k 更好？

思考题：
    1. 为什么 temperature=0 时仍然叫"采样"？
    2. top_k 和 top_p 可以同时使用吗？效果如何？
    3. Gemini 没有 penalty 参数，如何避免输出重复？
    """
    print(exercises_text)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 LLM API 参数详解 (Gemini 版本)")
    print("=" * 60)
    print("⚠️ 注意：本课程将多次调用 API，预估消耗约 2000-3000 tokens")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 请先配置 GOOGLE_API_KEY 环境变量")
        return

    try:
        explore_temperature()
        explore_top_p()
        explore_max_tokens()
        explore_top_k()
        parameter_recommendations()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！")
    print("下一步：03-streaming-responses.py（流式响应）")
    print("=" * 60)


if __name__ == "__main__":
    main()
