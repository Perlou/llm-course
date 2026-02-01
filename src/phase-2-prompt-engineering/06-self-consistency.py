"""
自洽性提示 (Self-Consistency) - Gemini 版本
==========================================

学习目标：
    1. 理解自洽性提示的原理
    2. 掌握多路径采样方法
    3. 学会结果聚合策略

核心概念：
    - 多次采样：用相同问题多次询问
    - 多样性：使用较高 temperature
    - 投票聚合：选择最常见的答案

前置知识：
    - 05-chain-of-thought.py

环境要求：
    - pip install google-generativeai python-dotenv
"""

import os
from collections import Counter
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：自洽性概念 ====================


def self_consistency_concept():
    """自洽性概念"""
    print("=" * 60)
    print("第一部分：自洽性提示概念")
    print("=" * 60)

    print("""
    自洽性提示 (Self-Consistency)：
    ──────────────────────────────
    
    核心思想：多次采样 + 多数投票
    
    ┌─────────────────────────────────────────────┐
    │                   问题                       │
    │                    │                        │
    │        ┌───────────┼───────────┐            │
    │        ▼           ▼           ▼            │
    │    ┌───────┐  ┌───────┐  ┌───────┐         │
    │    │ 推理1  │  │ 推理2  │  │ 推理3  │         │
    │    │ 答案A  │  │ 答案A  │  │ 答案B  │         │
    │    └───────┘  └───────┘  └───────┘         │
    │        │           │           │            │
    │        └───────────┼───────────┘            │
    │                    ▼                        │
    │              多数投票: A                     │
    └─────────────────────────────────────────────┘
    
    优势：
    - 减少随机错误
    - 提高可靠性
    - 适合有唯一正确答案的问题
    """)


# ==================== 第二部分：基础实现 ====================


def basic_self_consistency():
    """基础自洽性实现"""
    print("\n" + "=" * 60)
    print("第二部分：基础实现")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    problem = """问题：一个班有45名学生，男生比女生多9人。男生有多少人？

请一步步思考并给出答案。最后用"答案是：X人"的格式给出最终答案。"""

    print("📌 进行5次采样：")
    answers = []

    for i in range(5):
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            problem,
            generation_config={
                "temperature": 0.7,  # 增加多样性
                "max_output_tokens": 200,
            },
        )

        content = response.text
        # 提取答案
        if "答案是" in content:
            answer = content.split("答案是")[-1].strip()[:10]
        else:
            answer = content.split()[-1] if content else "未知"

        answers.append(answer)
        print(f"  采样 {i + 1}: {answer}")

    # 投票
    print(f"\n📊 投票结果：")
    vote_count = Counter(answers)
    for ans, count in vote_count.most_common():
        print(f"  {ans}: {count} 票")

    final = vote_count.most_common(1)[0][0]
    print(f"\n✅ 最终答案: {final}")


# ==================== 第三部分：带 CoT 的自洽性 ====================


def cot_self_consistency():
    """带 CoT 的自洽性"""
    print("\n" + "=" * 60)
    print("第三部分：CoT + Self-Consistency")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    problem = """逻辑问题：
小明说："我不在周一和周三工作。"
小红说："小明周二肯定工作。"
小李说："小明周四或周五工作。"

已知三人中只有一个人说的是真话。小明哪天一定工作？

让我们逐一假设每个人说真话来推理。最后给出答案，格式："答案是周X"。"""

    print("📌 进行3次 CoT 采样：")
    answers = []

    for i in range(3):
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            problem, generation_config={"temperature": 0.8, "max_output_tokens": 400}
        )

        content = response.text
        print(f"\n--- 采样 {i + 1} ---")
        print(content[:200] + "..." if len(content) > 200 else content)

        # 提取答案
        if "答案是" in content:
            answer = content.split("答案是")[-1].strip()[:5]
            answers.append(answer)

    if answers:
        vote_count = Counter(answers)
        print(f"\n📊 投票: {dict(vote_count)}")


# ==================== 第四部分：实用函数封装 ====================


def self_consistency_function():
    """实用函数封装"""
    print("\n" + "=" * 60)
    print("第四部分：实用函数封装")
    print("=" * 60)

    code_example = '''
def self_consistent_answer(
    prompt: str, 
    n_samples: int = 5,
    answer_extractor = None
) -> str:
    """
    使用自洽性方法获取答案
    
    Args:
        prompt: 问题提示词
        n_samples: 采样次数
        answer_extractor: 答案提取函数
    
    Returns:
        最可能的答案
    """
    import google.generativeai as genai
    from collections import Counter
    
    answers = []
    
    for _ in range(n_samples):
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 300
            }
        )
        
        content = response.text
        if answer_extractor:
            answer = answer_extractor(content)
        else:
            answer = content
        answers.append(answer)
    
    # 投票
    vote_count = Counter(answers)
    return vote_count.most_common(1)[0][0]
    '''
    print("📌 封装好的函数：")
    print(code_example)


# ==================== 第五部分：使用场景 ====================


def use_cases():
    """使用场景"""
    print("\n" + "=" * 60)
    print("第五部分：使用场景")
    print("=" * 60)

    print("""
    适合使用自洽性的场景：
    ─────────────────────
    ✅ 数学计算题
    ✅ 逻辑推理题
    ✅ 选择题/判断题
    ✅ 有唯一正确答案的问题
    
    不太适合的场景：
    ───────────────
    ❌ 创意写作
    ❌ 开放性问题
    ❌ 主观评价
    
    参数建议：
    ─────────
    - 采样次数：3-10 次
    - temperature：0.5-1.0
    - 成本考虑：次数 × 单次成本
    """)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：数学问题
        用自洽性解决一个应用题，对比单次和多次结果。

    练习 2：实现投票函数
        编写一个通用的自洽性答案提取函数。

    练习 3：成本分析
        计算使用自洽性的 token 成本增加比例。

    思考题：
        1. 采样次数如何影响准确性和成本？
        2. 如何处理平票情况？
        3. temperature 设置过低会怎样？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 自洽性提示 (Self-Consistency) - Gemini 版本")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
        return

    try:
        self_consistency_concept()
        basic_self_consistency()
        cot_self_consistency()
        self_consistency_function()
        use_cases()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：07-json-output.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
