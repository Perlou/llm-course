"""
少样本学习 (Few-Shot Learning) - Gemini 版本
=============================================

学习目标：
    1. 理解少样本学习的原理
    2. 掌握 Few-Shot 提示词设计
    3. 学会选择和组织示例

核心概念：
    - Zero-Shot：无示例直接提问
    - One-Shot：提供一个示例
    - Few-Shot：提供多个示例

前置知识：
    - 03-instruction-tuning.py

环境要求：
    - pip install google-generativeai python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Few-Shot 概念 ====================


def few_shot_concept():
    """Few-Shot 概念"""
    print("=" * 60)
    print("第一部分：Few-Shot 概念")
    print("=" * 60)

    print("""
    Few-Shot Learning（少样本学习）：
    ────────────────────────────────
    
    通过在提示词中提供少量示例，让模型学习任务模式。
    
    ┌─────────────────────────────────────────────┐
    │  Zero-Shot    │  无示例，直接问问题          │
    ├─────────────────────────────────────────────┤
    │  One-Shot     │  提供 1 个示例              │
    ├─────────────────────────────────────────────┤
    │  Few-Shot     │  提供 2-5 个示例            │
    └─────────────────────────────────────────────┘
    
    示例效果：
    - 帮助模型理解任务格式
    - 提供输出的参照标准
    - 减少歧义和误解
    """)


# ==================== 第二部分：Zero-Shot vs Few-Shot ====================


def zero_vs_few_shot():
    """Zero-Shot vs Few-Shot 对比"""
    print("\n" + "=" * 60)
    print("第二部分：Zero-Shot vs Few-Shot 对比")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    # Zero-Shot
    print("📌 Zero-Shot（无示例）：")
    zero_prompt = "判断这句话的情感是正面还是负面：今天天气真糟糕"
    r1 = model.generate_content(
        zero_prompt, generation_config={"max_output_tokens": 50}
    )
    print(f"回复: {r1.text}")

    # Few-Shot
    print("\n📌 Few-Shot（有示例）：")
    few_shot_prompt = """判断句子的情感倾向。

示例：
句子：这个产品太棒了！
情感：正面

句子：服务态度很差
情感：负面

句子：价格还可以
情感：中性

句子：今天天气真糟糕
情感："""

    r2 = model.generate_content(
        few_shot_prompt, generation_config={"max_output_tokens": 20}
    )
    print(f"回复: {r2.text}")


# ==================== 第三部分：分类任务 ====================


def classification_task():
    """分类任务演示"""
    print("\n" + "=" * 60)
    print("第三部分：分类任务")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    classify_prompt = """将客户反馈分类为以下类别之一：产品问题、物流问题、服务问题、其他

示例：
反馈：手机屏幕有划痕
分类：产品问题

反馈：快递员态度很差
分类：物流问题

反馈：客服电话一直打不通
分类：服务问题

反馈：包装发货很慢，等了一周才到
分类："""

    response = model.generate_content(
        classify_prompt, generation_config={"max_output_tokens": 20}
    )
    print(f"分类结果: {response.text}")


# ==================== 第四部分：格式转换 ====================


def format_conversion():
    """格式转换任务"""
    print("\n" + "=" * 60)
    print("第四部分：格式转换")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    format_prompt = """将自然语言转换为 SQL 查询。

示例：
问题：查找所有年龄大于30的用户
SQL：SELECT * FROM users WHERE age > 30

问题：统计每个城市的用户数量
SQL：SELECT city, COUNT(*) FROM users GROUP BY city

问题：找出购买金额最高的前10个订单
SQL："""

    response = model.generate_content(
        format_prompt, generation_config={"max_output_tokens": 50}
    )
    print(f"SQL: {response.text}")


# ==================== 第五部分：示例选择技巧 ====================


def example_selection():
    """示例选择技巧"""
    print("\n" + "=" * 60)
    print("第五部分：示例选择技巧")
    print("=" * 60)

    print("""
    选择好示例的原则：
    ─────────────────
    
    1. 代表性：覆盖常见情况
    2. 多样性：涵盖不同类别
    3. 清晰性：避免歧义案例
    4. 相关性：与目标任务相似
    5. 数量适中：通常 2-5 个
    
    示例排列顺序：
    ─────────────
    
    - 简单到复杂
    - 常见到罕见
    - 最相关的放最后（recency bias）
    """)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：情感分析
        设计一个 3-shot 的情感分析提示词。

        ✅ 参考答案：
        ```
        请分析以下句子的情感倾向（正面/负面/中性）。

        示例 1：
        句子：这家餐厅的服务太棒了，下次还会再来！
        情感：正面

        示例 2：
        句子：等了一个小时菜还没上，太失望了。
        情感：负面

        示例 3：
        句子：这个手机壳质量一般，价格也一般。
        情感：中性

        现在分析：
        句子：{用户输入}
        情感：
        ```

    练习 2：实体提取
        用 Few-Shot 从新闻中提取人名、地点、时间。

        ✅ 参考答案：
        ```
        从新闻文本中提取实体信息。

        示例 1：
        新闻：马斯克于 2024 年 3 月访问了北京。
        人名：马斯克
        地点：北京
        时间：2024年3月

        示例 2：
        新闻：苹果公司 CEO 库克将于下周一在纽约发布新品。
        人名：库克
        地点：纽约
        时间：下周一

        现在提取：
        新闻：{用户输入}
        人名：
        地点：
        时间：
        ```

    练习 3：风格转换
        用 Few-Shot 将正式文本转换为口语化表达。

        ✅ 参考答案：
        ```
        将正式书面语转换为轻松的口语表达。

        示例 1：
        正式：请您务必在截止日期前提交相关材料。
        口语：记得在截止日期前把材料交了哦~

        示例 2：
        正式：经研究决定，本次会议延期举行。
        口语：会议改期了，具体时间再通知大家。

        示例 3：
        正式：感谢您对本公司产品的支持与信赖。
        口语：谢谢你支持我们！

        现在转换：
        正式：{用户输入}
        口语：
        ```

    思考题：
        1. 示例数量越多越好吗？
           
           ✅ 答案：不是。需要考虑：
           - 边际效益：通常 3-5 个示例效果最佳
           - 上下文限制：示例太多会占用 token 配额
           - 过拟合风险：示例过多可能导致模型过度模仿
           - 建议：选择高质量、有代表性的示例

        2. 错误示例会产生什么影响？
           
           ✅ 答案：
           - 模型会学习错误模式
           - 输出可能包含同类错误
           - 降低整体任务准确率
           - 建议：严格审核示例质量

        3. 如何处理边界情况？
           
           ✅ 答案：
           - 在示例中包含边界案例
           - 明确说明如何处理模糊情况
           - 添加"如果无法判断，输出'不确定'"的指令
           - 提供多个类别的边界示例
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 少样本学习 (Few-Shot Learning) - Gemini 版本")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
        return

    try:
        few_shot_concept()
        zero_vs_few_shot()
        classification_task()
        format_conversion()
        example_selection()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：05-chain-of-thought.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
