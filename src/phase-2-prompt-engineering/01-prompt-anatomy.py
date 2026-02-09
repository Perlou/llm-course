"""
提示词结构解析 (Gemini 版本)
============================

学习目标：
    1. 理解提示词的基本组成部分
    2. 掌握 CLEAR 原则设计高质量提示词
    3. 学会结构化组织复杂提示词
    4. 理解上下文和约束的重要性

核心概念：
    - 提示词结构：角色、上下文、任务、输入、输出格式、示例
    - CLEAR 原则：清晰、逻辑、明确、适应、相关
    - 约束设定：内容约束、格式约束、质量约束

前置知识：
    - Phase 1 LLM 基础
    - Gemini API 基础使用

环境要求：
    - pip install google-generativeai python-dotenv
    - 配置 GOOGLE_API_KEY
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


# ==================== 第一部分：提示词的重要性 ====================


def introduction():
    """提示词工程介绍"""
    print("=" * 60)
    print("第一部分：提示词工程概述")
    print("=" * 60)

    intro_text = """
    什么是提示词工程（Prompt Engineering）？
    ──────────────────────────────────────
    
    提示词工程是设计和优化输入文本（提示词）的技术与艺术，
    旨在引导大型语言模型生成期望输出的系统性方法。
    
    ┌─────────────────────────────────────────────────────────┐
    │                    提示词工程流程                         │
    ├─────────────────────────────────────────────────────────┤
    │                                                         │
    │   用户意图  →  提示词设计  →  LLM处理  →  输出结果        │
    │      ↑                                      │           │
    │      └──────────── 评估与迭代 ←─────────────┘           │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
    
    为什么提示词工程重要？
    ──────────────────────
    
    | 方面         | 影响                           |
    |-------------|-------------------------------|
    | 输出质量     | 好的提示词可将输出质量提升数倍   |
    | 效率提升     | 减少来回修正的次数              |
    | 成本控制     | 减少 Token 消耗，降低 API 成本  |
    | 一致性       | 确保输出格式和风格的一致性       |
    | 解锁能力     | 挖掘模型的隐藏潜力              |
    """
    print(intro_text)


# ==================== 第二部分：提示词的六大组成部分 ====================


def prompt_structure():
    """提示词的完整结构"""
    print("\n" + "=" * 60)
    print("第二部分：提示词的六大组成部分")
    print("=" * 60)

    structure_text = """
    完整提示词结构：
    ──────────────
    
    ┌─────────────────────────────────────────┐
    │         完整提示词结构                    │
    ├─────────────────────────────────────────┤
    │ 1. 角色设定 (Role)                       │
    │    └─ 定义 AI 应该扮演的角色              │
    │                                         │
    │ 2. 上下文 (Context)                      │
    │    └─ 提供背景信息和约束条件              │
    │                                         │
    │ 3. 任务指令 (Instruction)                │
    │    └─ 明确说明需要完成的任务              │
    │                                         │
    │ 4. 输入数据 (Input)                      │
    │    └─ 需要处理的具体内容                  │
    │                                         │
    │ 5. 输出格式 (Output Format)              │
    │    └─ 期望的输出格式和结构                │
    │                                         │
    │ 6. 示例 (Examples) [可选]                │
    │    └─ 输入输出的参考示例                  │
    └─────────────────────────────────────────┘
    """
    print(structure_text)

    # 实际演示
    print("\n📌 实际示例对比：")
    print("-" * 40)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    # 简单的提示词
    simple_prompt = "帮我写个代码审查反馈"

    print("\n❌ 简单提示词：")
    print(f'   "{simple_prompt}"')

    response1 = model.generate_content(
        simple_prompt, generation_config={"max_output_tokens": 200}
    )
    print(f"\n   回复（截取）：{response1.text[:150]}...")

    # 结构化的提示词
    structured_prompt = """# 角色设定
你是一位资深的 Python 技术专家，擅长代码审查和优化。

# 上下文
我正在开发一个高并发的 Web 应用，需要确保代码质量和性能。

# 任务指令
请审查以下代码，指出问题并提供优化建议。

# 输入数据
```python
def get_user(id):
    users = db.query("SELECT * FROM users")
    for user in users:
        if user.id == id:
            return user
    return None
```

# 输出格式
请按以下格式输出：
1. 问题列表（按严重程度排序）
2. 优化后的代码
3. 优化说明"""

    print("\n\n✅ 结构化提示词：")
    print("   （包含角色、上下文、任务、输入、输出格式）")

    response2 = model.generate_content(
        structured_prompt, generation_config={"max_output_tokens": 500}
    )
    print(f"\n   回复：\n{response2.text}")

    print("\n💡 结论：结构化的提示词能获得更专业、更符合需求的回复")


# ==================== 第三部分：CLEAR 原则 ====================


def clear_principles():
    """CLEAR 原则详解"""
    print("\n" + "=" * 60)
    print("第三部分：CLEAR 原则")
    print("=" * 60)

    principles_text = """
    CLEAR 原则是设计高质量提示词的五大核心原则：
    ─────────────────────────────────────────────
    
    C - Clear（清晰）
        使用明确、无歧义的语言
        
    L - Logical（逻辑）
        保持逻辑连贯性
        
    E - Explicit（明确）
        明确说明期望的输出
        
    A - Adaptive（适应）
        根据结果调整优化
        
    R - Relevant（相关）
        只包含相关信息
    """
    print(principles_text)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    # 演示：具体 vs 模糊
    print("\n📌 原则一：具体而非模糊")
    print("-" * 40)

    vague_prompt = "帮我写点东西介绍人工智能"
    specific_prompt = """请撰写一篇 200 字的科普文章，面向没有技术背景的读者，
介绍人工智能的三个核心概念：机器学习、深度学习和神经网络。
使用生活中的类比来解释这些概念。"""

    print(f'\n❌ 模糊: "{vague_prompt}"')
    print(f'\n✅ 具体: "{specific_prompt}"')

    response = model.generate_content(
        specific_prompt, generation_config={"max_output_tokens": 400}
    )
    print(f"\n📤 具体提示词的回复：\n{response.text}")

    # 演示：分步骤拆解
    print("\n\n📌 原则二：分步骤拆解复杂任务")
    print("-" * 40)

    step_by_step_prompt = """请按以下步骤分析这段销售数据的关键点：

数据：某电商店铺月销售额分别为 10万、12万、8万、15万、20万、18万

步骤：
1. 首先，找出最高和最低的月份
2. 然后，计算平均月销售额
3. 接着，识别增长和下降的趋势
4. 最后，给出 2 条业务建议"""

    print(f"✅ 分步骤提示词：")
    print(step_by_step_prompt)

    response2 = model.generate_content(
        step_by_step_prompt, generation_config={"max_output_tokens": 400}
    )
    print(f"\n📤 回复：\n{response2.text}")


# ==================== 第四部分：约束与边界设定 ====================


def constraints_demo():
    """约束与边界设定演示"""
    print("\n" + "=" * 60)
    print("第四部分：约束与边界设定")
    print("=" * 60)

    constraints_text = """
    约束类型：
    ─────────
    
    1. 内容约束
       - 字数限制：控制输出长度
       - 主题范围：限定讨论范围
       - 排除内容：明确不应包含的内容
    
    2. 格式约束
       - 结构要求：标题、段落、列表等
       - 语言风格：正式/非正式、技术/通俗
       - 特殊格式：JSON、表格、代码等
    
    3. 质量约束
       - 准确性要求
       - 原创性要求
       - 引用要求
    """
    print(constraints_text)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    # 带约束的提示词
    constrained_prompt = """请写一段产品介绍，主题是"智能手表"。

【内容约束】
- 字数：100-150 字
- 必须包含：健康监测、运动追踪、消息通知
- 不要包含：价格信息、与竞品对比

【格式约束】
- 使用简洁有力的短句
- 开头要有吸引眼球的引言
- 结尾要有行动号召

【语言风格】
- 面向年轻消费者
- 活泼但不失专业"""

    print("\n📌 带约束的提示词演示：")
    print(constrained_prompt)

    response = model.generate_content(
        constrained_prompt, generation_config={"max_output_tokens": 300}
    )
    print(f"\n📤 回复：\n{response.text}")

    # 验证字数
    reply = response.text
    char_count = len(reply.replace(" ", "").replace("\n", ""))
    print(f"\n📊 字符数统计：{char_count} 个字符")


# ==================== 第五部分：实战对比 ====================


def practical_comparison():
    """实战对比：优化前后的提示词"""
    print("\n" + "=" * 60)
    print("第五部分：实战对比")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    # 场景：客服回复
    print("\n📌 场景：电商客服回复")
    print("-" * 40)

    customer_complaint = "我买的手机壳两天就裂了，太差了！"

    # 未优化的提示词
    bad_prompt = f"回复这个客户投诉：{customer_complaint}"

    print(f'\n❌ 未优化提示词："{bad_prompt}"')

    response1 = model.generate_content(
        bad_prompt, generation_config={"max_output_tokens": 200}
    )
    print(f"   回复：{response1.text}")

    # 优化后的提示词
    good_prompt = f"""你是电商平台客服"小智"，处理客户投诉。

【客服原则】
1. 先共情，表示理解
2. 真诚道歉
3. 提供解决方案
4. 确保客户满意

【回复要求】
- 语气：温和、专业
- 长度：50-100 字
- 必须包含：道歉 + 解决方案

客户反馈：{customer_complaint}

请生成回复："""

    print(f"\n✅ 优化后提示词：")
    print(good_prompt)

    response2 = model.generate_content(
        good_prompt, generation_config={"max_output_tokens": 200}
    )
    print(f"\n   回复：{response2.text}")


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    exercises_text = """
    练习 1：改写简单提示词
        将以下简单提示词改写成结构化的完整提示词：
        "帮我写个邮件请假"
        
        提示：添加角色、上下文、具体要求、输出格式

        ✅ 参考答案：
        ```
        # 角色设定
        你是一位专业的职场邮件撰写助手。

        # 上下文
        我是一名公司职员，因身体不适需要向主管请假一天。

        # 任务指令
        请帮我撰写一封正式的请假邮件。

        # 具体要求
        - 请假日期：明天（2024年1月15日）
        - 请假原因：身体不适，需要休息
        - 语气：礼貌、正式
        - 长度：100-150字

        # 输出格式
        包含：邮件标题、称呼、正文、落款
        ```

    练习 2：应用 CLEAR 原则
        评估以下提示词，指出违反了哪些 CLEAR 原则：
        "写个好看的网页，要有动画效果，还要响应式，
         最好用最新的技术，但不要太复杂。"

        ✅ 参考答案：
        违反的原则：
        - C（Clear）：\"好看\"是主观且模糊的描述
        - E（Explicit）：没有明确网页用途、页面数量、具体功能
        - R（Relevant）：\"最新技术\"范围太广，缺乏具体技术栈要求
        - 矛盾点：\"动画效果\"和\"不要太复杂\"可能冲突
        
        改进版本：
        \"请用 HTML/CSS/JavaScript 创建一个单页个人简历网站，
         包含：导航栏、个人介绍、技能列表、联系方式四个区块。
         要求：使用 CSS 过渡动画实现平滑滚动，响应式适配手机端。\"

    练习 3：设计约束条件
        为以下任务设计完整的约束条件：
        任务：让 AI 为儿童写一个睡前故事
        
        思考：需要哪些内容约束、格式约束、安全约束？

        ✅ 参考答案：
        【内容约束】
        - 主题：温馨、治愈的冒险故事
        - 字数：300-500 字
        - 角色：可爱的小动物作为主角
        - 结局：必须是美好、积极的结局
        - 排除：不能有暴力、恐怖、悲伤的情节

        【格式约束】
        - 开头：以 \"从前...\" 或 \"在一个...\" 开始
        - 段落：分成 3-4 个短段落
        - 语言：使用简单词汇，适合 3-8 岁儿童
        - 对话：包含适量对话，增加趣味性

        【安全约束】
        - 不包含任何可能引起恐惧的元素
        - 不涉及分离焦虑相关内容
        - 传递正面价值观（友善、勇气、分享）

    思考题：
        1. 提示词越长越好吗？什么时候简短的提示词更有效？
           
           ✅ 答案：不是越长越好。
           - 简短提示词适用场景：简单任务、模型能力强、创意性任务
           - 长提示词适用场景：复杂任务、需要精确控制、专业领域
           - 关键是信息密度，而非长度本身

        2. 如何判断一个提示词是否"足够好"？
           
           ✅ 答案：可以从以下维度评估：
           - 输出质量：是否满足预期？
           - 一致性：多次运行结果是否稳定？
           - 效率：token 消耗是否合理？
           - 可维护性：他人是否容易理解和修改？

        3. 不同的 LLM 模型对提示词的敏感度相同吗？
           
           ✅ 答案：不相同。
           - GPT-4 对格式要求更敏感，遵循性强
           - Claude 对长上下文处理更好
           - Gemini 对多模态提示支持更好
           - 开源模型通常需要更明确的指令
           - 建议：针对目标模型进行提示词调优
    """
    print(exercises_text)


# ==================== 主函数 ====================


def main():
    """主函数 - 按顺序执行所有部分"""
    print("🚀 提示词结构解析 (Gemini 版本)")
    print("=" * 60)
    print("💡 本课程使用 Google Gemini API（免费额度较多）")
    print("预估消耗：约 2000-3000 tokens")
    print("=" * 60)

    # 检查环境
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY 环境变量")
        return

    print(f"✅ API Key 已配置: {api_key[:8]}...{api_key[-4:]}")

    # 按顺序执行各部分
    try:
        introduction()
        prompt_structure()
        clear_principles()
        constraints_demo()
        practical_comparison()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback

        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！")
    print("下一步：02-system-prompts.py（系统提示词设计）")
    print("=" * 60)


if __name__ == "__main__":
    main()
