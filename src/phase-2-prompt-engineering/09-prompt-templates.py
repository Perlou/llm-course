"""
提示词模板设计
==============

学习目标：
    1. 掌握提示词模板的设计方法
    2. 学会构建可复用的模板
    3. 了解模板变量和条件逻辑

核心概念：
    - 模板化：将提示词参数化
    - 变量替换：动态填充内容
    - 模板组合：复杂模板的构建

前置知识：
    - 08-structured-extraction.py

环境要求：
    - pip install openai python-dotenv
"""

import os
from string import Template
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# ==================== 第一部分：基础模板 ====================


def basic_template():
    """基础模板"""
    print("=" * 60)
    print("第一部分：基础模板")
    print("=" * 60)

    # 使用 Python Template
    translate_template = Template("""
请将以下${source_lang}文本翻译成${target_lang}：

${text}

要求：
- 保持原文风格
- 翻译自然流畅
""")

    prompt = translate_template.substitute(
        source_lang="中文", target_lang="英文", text="今天天气真好，适合出去散步。"
    )

    print("📌 模板化翻译提示词：")
    print(prompt)

    # 调用 API
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
    )
    print(f"\n翻译结果: {response.choices[0].message.content}")


# ==================== 第二部分：角色模板 ====================


def role_template():
    """角色模板"""
    print("\n" + "=" * 60)
    print("第二部分：角色模板")
    print("=" * 60)

    def create_expert_prompt(role, expertise, user_question):
        """创建专家角色提示词"""
        system = f"""你是一位资深的{role}，专长于{expertise}。
回答用户问题时：
- 使用专业但易懂的语言
- 给出具体可行的建议
- 必要时举例说明"""

        return system, user_question

    client = OpenAI()

    # 测试不同角色
    roles = [
        ("Python教练", "Python编程教学", "如何学好Python？"),
        ("投资顾问", "个人理财", "新手如何开始投资？"),
    ]

    for role, expertise, question in roles:
        system, user = create_expert_prompt(role, expertise, question)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=200,
        )

        print(f"\n📌 {role} 回答：")
        print(response.choices[0].message.content[:200] + "...")


# ==================== 第三部分：任务模板库 ====================


def task_templates():
    """任务模板库"""
    print("\n" + "=" * 60)
    print("第三部分：任务模板库")
    print("=" * 60)

    # 模板库
    TEMPLATES = {
        "summarize": """请总结以下文本的要点：

{text}

要求：
- 提取 {num_points} 个核心要点
- 每个要点一句话
- 使用{style}风格""",
        "rewrite": """请用{style}的风格重写以下文本：

原文：{text}

要求：保持原意，改变表达方式""",
        "qa": """基于以下信息回答问题：

信息：{context}

问题：{question}

要求：只基于提供的信息回答，如果信息不足请说明""",
    }

    def get_prompt(task_type, **kwargs):
        """获取格式化的提示词"""
        if task_type not in TEMPLATES:
            raise ValueError(f"未知任务类型: {task_type}")
        return TEMPLATES[task_type].format(**kwargs)

    # 使用示例
    print("📌 使用总结模板：")
    summary_prompt = get_prompt(
        "summarize", text="人工智能正在改变各行各业...", num_points=3, style="简洁"
    )
    print(summary_prompt)


# ==================== 第四部分：条件模板 ====================


def conditional_template():
    """条件模板"""
    print("\n" + "=" * 60)
    print("第四部分：条件模板")
    print("=" * 60)

    def build_analysis_prompt(text, options):
        """构建分析提示词"""
        base = f"请分析以下文本：\n\n{text}\n\n分析内容："

        tasks = []
        if options.get("sentiment"):
            tasks.append("1. 情感倾向（正面/负面/中性）")
        if options.get("summary"):
            tasks.append("2. 内容摘要（一句话）")
        if options.get("keywords"):
            tasks.append("3. 关键词（最多5个）")
        if options.get("entities"):
            tasks.append("4. 实体识别（人名、地名、机构名）")

        return base + "\n".join(tasks)

    # 使用
    prompt = build_analysis_prompt(
        "苹果公司CEO蒂姆·库克今天在发布会上宣布了新产品。",
        {"sentiment": True, "keywords": True, "entities": True},
    )

    print("📌 条件生成的提示词：")
    print(prompt)


# ==================== 第五部分：模板最佳实践 ====================


def template_best_practices():
    """模板最佳实践"""
    print("\n" + "=" * 60)
    print("第五部分：模板最佳实践")
    print("=" * 60)

    print("""
    模板设计原则：
    ─────────────
    
    1. 明确变量边界
       ✅ 使用 {variable} 或 ${variable}
       ❌ 混用多种占位符格式
    
    2. 提供默认值
       - 可选参数设置默认值
       - 避免空值导致的错误
    
    3. 验证输入
       - 检查必填参数
       - 验证参数类型
    
    4. 文档化
       - 注释说明每个变量用途
       - 提供使用示例
    
    5. 模块化
       - 拆分大模板为小组件
       - 支持模板组合
    """)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：创建邮件模板
        设计一个可定制收件人、主题、正文的邮件模板。

    练习 2：代码生成模板
        创建一个根据语言、功能生成代码的模板。

    练习 3：模板管理系统
        实现一个简单的模板存储和查询系统。

    思考题：
        1. 如何版本化管理模板？
        2. 模板过于复杂时如何处理？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 提示词模板设计")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 OPENAI_API_KEY")
        return

    try:
        basic_template()
        role_template()
        task_templates()
        conditional_template()
        template_best_practices()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：10-adversarial-prompting.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
