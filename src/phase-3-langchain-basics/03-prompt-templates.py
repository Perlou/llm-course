"""
提示词模板
==========

学习目标：
    1. 掌握 PromptTemplate 的使用
    2. 理解 ChatPromptTemplate 的消息结构
    3. 学会使用 MessagesPlaceholder 动态插入消息

核心概念：
    - PromptTemplate：纯文本模板
    - ChatPromptTemplate：对话消息模板
    - MessagesPlaceholder：动态消息占位符

前置知识：
    - 02-llm-models.py

环境要求：
    - pip install langchain langchain-openai python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：PromptTemplate 基础 ====================


def prompt_template_basics():
    """PromptTemplate 基础"""
    print("=" * 60)
    print("第一部分：PromptTemplate 基础")
    print("=" * 60)

    from langchain_core.prompts import PromptTemplate

    # 方式一：from_template
    print("\n📌 方式一：使用 from_template")
    template1 = PromptTemplate.from_template("请将{source}翻译成{target}：{text}")
    prompt = template1.format(source="中文", target="英文", text="你好")
    print(f"生成的提示词：{prompt}")

    # 方式二：构造函数
    print("\n📌 方式二：使用构造函数")
    template2 = PromptTemplate(
        input_variables=["topic"], template="请用一句话解释什么是{topic}"
    )
    prompt = template2.format(topic="机器学习")
    print(f"生成的提示词：{prompt}")

    # 带默认值
    print("\n📌 带默认值的模板")
    from langchain_core.prompts import PromptTemplate

    template3 = PromptTemplate.from_template(
        "用{style}的风格介绍{topic}", partial_variables={"style": "简洁"}
    )
    prompt = template3.format(topic="Python")
    print(f"生成的提示词：{prompt}")


# ==================== 第二部分：ChatPromptTemplate ====================


def chat_prompt_template_demo():
    """ChatPromptTemplate 演示"""
    print("\n" + "=" * 60)
    print("第二部分：ChatPromptTemplate")
    print("=" * 60)

    from langchain_core.prompts import ChatPromptTemplate

    # 基础用法
    print("\n📌 基础用法")
    chat_template = ChatPromptTemplate.from_messages(
        [("system", "你是一个{role}，擅长{skill}"), ("human", "{input}")]
    )

    messages = chat_template.format_messages(
        role="Python专家", skill="代码优化", input="如何提高代码性能？"
    )

    print("生成的消息：")
    for msg in messages:
        print(f"  [{type(msg).__name__}] {msg.content}")

    # 与 LLM 结合
    print("\n📌 与 LLM 结合使用")
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.output_parsers import StrOutputParser

        llm = ChatOpenAI(model="gpt-3.5-turbo")
        chain = chat_template | llm | StrOutputParser()

        result = chain.invoke(
            {"role": "产品经理", "skill": "需求分析", "input": "如何写好PRD？"}
        )
        print(f"回复：{result[:200]}...")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第三部分：MessagesPlaceholder ====================


def messages_placeholder_demo():
    """MessagesPlaceholder 演示"""
    print("\n" + "=" * 60)
    print("第三部分：MessagesPlaceholder")
    print("=" * 60)

    print("""
    MessagesPlaceholder 用于动态插入消息列表，常用于：
    - 注入对话历史
    - 动态添加示例
    """)

    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.messages import HumanMessage, AIMessage

    # 创建带历史的模板
    template = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一个有帮助的助手"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    # 模拟历史对话
    history = [
        HumanMessage(content="我叫张三"),
        AIMessage(content="你好张三！很高兴认识你！"),
    ]

    messages = template.format_messages(history=history, input="我叫什么名字？")

    print("\n生成的消息：")
    for msg in messages:
        role = type(msg).__name__.replace("Message", "")
        print(f"  [{role}] {msg.content}")

    # 实际调用
    print("\n📌 实际调用测试")
    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model="gpt-3.5-turbo")
        chain = template | llm

        response = chain.invoke({"history": history, "input": "我叫什么名字？"})
        print(f"回复：{response.content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：FewShotPromptTemplate ====================


def few_shot_demo():
    """Few-Shot 提示词模板"""
    print("\n" + "=" * 60)
    print("第四部分：FewShotPromptTemplate")
    print("=" * 60)

    from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate

    # 定义示例
    examples = [
        {"input": "开心", "output": "😊"},
        {"input": "悲伤", "output": "😢"},
        {"input": "愤怒", "output": "😠"},
    ]

    # 示例模板
    example_template = PromptTemplate.from_template("输入: {input}\n输出: {output}")

    # Few-Shot 模板
    few_shot_prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_template,
        prefix="将情感词转换为对应的emoji：",
        suffix="输入: {input}\n输出:",
        input_variables=["input"],
    )

    prompt = few_shot_prompt.format(input="惊讶")
    print("生成的提示词：")
    print(prompt)

    # 实际调用
    print("\n📌 实际调用测试")
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.output_parsers import StrOutputParser

        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        chain = few_shot_prompt | llm | StrOutputParser()

        result = chain.invoke({"input": "困惑"})
        print(f"结果：{result}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第五部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：创建翻译模板
        创建一个支持多语言翻译的模板。

    练习 2：带历史的对话
        使用 MessagesPlaceholder 实现多轮对话。

    练习 3：Few-Shot 分类
        创建一个 Few-Shot 模板用于文本分类。

    思考题：
        1. PromptTemplate 和 ChatPromptTemplate 的区别？
        2. MessagesPlaceholder 有什么应用场景？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 提示词模板")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 OPENAI_API_KEY")
        return

    try:
        prompt_template_basics()
        chat_prompt_template_demo()
        messages_placeholder_demo()
        few_shot_demo()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：04-chains-basics.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
