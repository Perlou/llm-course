"""
思维链提示 (Chain of Thought) - Gemini 版本
==========================================

学习目标：
    1. 理解思维链提示的原理
    2. 掌握 CoT 提示词设计
    3. 学会引导模型逐步推理

核心概念：
    - CoT：让模型展示推理过程
    - 逐步思考：分解问题为小步骤
    - 推理轨迹：可追溯的思考过程

前置知识：
    - 04-few-shot-learning.py

环境要求：
    - pip install google-generativeai python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：CoT 概念 ====================


def cot_concept():
    """CoT 概念"""
    print("=" * 60)
    print("第一部分：思维链 (CoT) 概念")
    print("=" * 60)

    print("""
    思维链提示 (Chain of Thought)：
    ──────────────────────────────
    
    让模型在给出答案前，先展示推理过程。
    
    传统方式：
    问：小明有5个苹果，吃了2个，又买了3个，现在有几个？
    答：6个
    
    CoT方式：
    问：...让我们一步步思考...
    答：1) 小明最初有5个苹果
        2) 吃了2个，剩下5-2=3个
        3) 又买了3个，3+3=6个
        4) 所以现在有6个苹果
    
    优势：
    - 提高复杂推理准确性
    - 便于验证和调试
    - 减少"跳跃式"错误
    """)


# ==================== 第二部分：Zero-Shot CoT ====================


def zero_shot_cot():
    """Zero-Shot CoT"""
    print("\n" + "=" * 60)
    print("第二部分：Zero-Shot CoT")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    problem = "一个水池有两个进水管和一个出水管。进水管A每小时进水10升，进水管B每小时进水15升，出水管每小时放水8升。如果水池初始有100升水，2小时后水池有多少升水？"

    # 无 CoT
    print("📌 无 CoT：")
    r1 = model.generate_content(problem, generation_config={"max_output_tokens": 100})
    print(f"回复: {r1.text}")

    # Zero-Shot CoT
    print("\n📌 Zero-Shot CoT（添加'让我们一步步思考'）：")
    cot_prompt = problem + "\n\n让我们一步步思考："
    r2 = model.generate_content(
        cot_prompt, generation_config={"max_output_tokens": 300}
    )
    print(f"回复：\n{r2.text}")


# ==================== 第三部分：Few-Shot CoT ====================


def few_shot_cot():
    """Few-Shot CoT"""
    print("\n" + "=" * 60)
    print("第三部分：Few-Shot CoT")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    few_shot_prompt = """解决数学问题，展示思考过程。

问题：小明有8个苹果，给了小红3个，又从小李那获得5个，现在有几个？
思考过程：
1. 小明最初有8个苹果
2. 给了小红3个后：8-3=5个
3. 从小李获得5个后：5+5=10个
答案：10个

问题：一个班有40个学生，男生比女生多8人，男生有多少人？
思考过程：
1. 设女生有x人，则男生有x+8人
2. 总人数：x+(x+8)=40
3. 解方程：2x+8=40，2x=32，x=16
4. 男生人数：16+8=24人
答案：24人

问题：火车从A站到B站需要3小时，速度是80公里/小时。如果速度提高到100公里/小时，需要多长时间？
思考过程："""

    response = model.generate_content(
        few_shot_prompt, generation_config={"max_output_tokens": 200}
    )
    print(f"回复：\n{response.text}")


# ==================== 第四部分：代码问题 CoT ====================


def code_cot():
    """代码问题 CoT"""
    print("\n" + "=" * 60)
    print("第四部分：代码问题 CoT")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    code_prompt = """分析这段代码的问题，逐步思考：

```python
def find_max(numbers):
    max_num = 0
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

result = find_max([-5, -2, -8, -1])
print(result)  # 输出：0
```

让我们一步步分析：
1. 首先理解代码的预期功能
2. 然后追踪代码执行过程
3. 找出问题所在
4. 给出修复建议"""

    response = model.generate_content(
        code_prompt, generation_config={"max_output_tokens": 400}
    )
    print(f"回复：\n{response.text}")


# ==================== 第五部分：CoT 使用技巧 ====================


def cot_tips():
    """CoT 使用技巧"""
    print("\n" + "=" * 60)
    print("第五部分：CoT 使用技巧")
    print("=" * 60)

    print("""
    何时使用 CoT：
    ─────────────
    ✅ 数学计算和推理
    ✅ 逻辑问题
    ✅ 代码调试
    ✅ 多步骤决策
    ❌ 简单事实查询
    ❌ 创意写作
    
    常用触发短语：
    ─────────────
    - "让我们一步步思考"
    - "请展示推理过程"
    - "逐步分析这个问题"
    - "详细解释你的思考"
    - "Think step by step"
    
    优化技巧：
    ─────────
    1. 明确要求展示步骤
    2. 提供推理示例
    3. 要求最后给出结论
    4. 复杂问题先分解
    """)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：数学应用题
        用 CoT 解决一个年龄问题。

        ✅ 参考答案：
        ```
        问题：小明今年 12 岁，他爸爸的年龄是小明的 3 倍。
              5 年后，他爸爸比小明大多少岁？

        让我们一步步思考：

        步骤 1：计算爸爸现在的年龄
        爸爸年龄 = 小明年龄 × 3 = 12 × 3 = 36 岁

        步骤 2：计算 5 年后各自的年龄
        5 年后小明：12 + 5 = 17 岁
        5 年后爸爸：36 + 5 = 41 岁

        步骤 3：计算年龄差
        年龄差 = 41 - 17 = 24 岁

        答案：5 年后，爸爸比小明大 24 岁。
        
        （注：年龄差始终不变，也可直接用 36-12=24）
        ```

    练习 2：逻辑推理
        用 CoT 解决一个排列组合问题。

        ✅ 参考答案：
        ```
        问题：5 个人排成一排照相，小明必须站在最中间，
              有多少种不同的排列方式？

        让我们一步步分析：

        步骤 1：确定约束条件
        - 共 5 个人，5 个位置
        - 小明固定在第 3 个位置（最中间）

        步骤 2：分析剩余情况
        - 剩下 4 个人
        - 剩下 4 个位置（1、2、4、5）

        步骤 3：计算排列数
        - 4 个人排 4 个位置
        - P(4,4) = 4! = 4 × 3 × 2 × 1 = 24

        答案：共有 24 种不同的排列方式。
        ```

    练习 3：代码调试
        用 CoT 分析一段有 bug 的代码。

        ✅ 参考答案：
        ```
        代码：
        def average(numbers):
            total = 0
            for n in numbers:
                total += n
            return total / len(numbers)

        让我们逐步分析可能的问题：

        步骤 1：功能理解
        这个函数计算列表中数字的平均值。

        步骤 2：正常情况测试
        average([1,2,3]) → 2.0 ✓

        步骤 3：边界情况检查
        - 空列表：average([]) → ZeroDivisionError ❌
        - None：average(None) → TypeError ❌

        步骤 4：问题定位
        1. 没有处理空列表（除以零错误）
        2. 没有类型检查

        步骤 5：修复建议
        def average(numbers):
            if not numbers:
                return 0  # 或 raise ValueError
            return sum(numbers) / len(numbers)
        ```

    思考题：
        1. CoT 会增加 token 消耗吗？
           
           ✅ 答案：会。
           - 输出更长，消耗更多 output tokens
           - 但对于复杂推理任务，准确率提升带来的价值
             通常大于额外的 token 成本
           - 优化：使用简洁的推理步骤

        2. 什么情况下 CoT 反而会降低准确性？
           
           ✅ 答案：
           - 简单任务：无需推理的直接问答
           - 事实查询：需要记忆而非推理的问题
           - 创意任务：过度推理可能限制创意
           - 错误累积：中间步骤出错会影响最终结果
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 思维链提示 (Chain of Thought) - Gemini 版本")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
        return

    try:
        cot_concept()
        zero_shot_cot()
        few_shot_cot()
        code_cot()
        cot_tips()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：06-self-consistency.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
