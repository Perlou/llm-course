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
    - pip install langchain langchain-google-genai python-dotenv
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
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.output_parsers import StrOutputParser

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
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
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
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
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.output_parsers import StrOutputParser

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
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

        ✅ 参考答案：
        ```python
        from langchain_core.prompts import ChatPromptTemplate

        translation_template = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业翻译，擅长 {source_lang} 和 {target_lang} 互译"),
            ("human", "请将以下{source_lang}翻译成{target_lang}：\\n{text}")
        ])

        # 使用
        messages = translation_template.format_messages(
            source_lang="中文",
            target_lang="英文",
            text="人工智能正在改变世界"
        )
        ```

    练习 2：带历史的对话
        使用 MessagesPlaceholder 实现多轮对话。

        ✅ 参考答案：
        ```python
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.messages import HumanMessage, AIMessage

        chat_template = ChatPromptTemplate.from_messages([
            ("system", "你是一个友好的助手，记住用户告诉你的所有信息"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        # 模拟历史
        history = [
            HumanMessage(content="我叫张三，喜欢编程"),
            AIMessage(content="你好张三！编程是个很棒的爱好！")
        ]

        messages = chat_template.format_messages(
            history=history,
            input="你还记得我的信息吗？"
        )
        ```

    练习 3：Few-Shot 分类
        创建一个 Few-Shot 模板用于文本分类。

        ✅ 参考答案：
        ```python
        from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate

        examples = [
            {"text": "这个产品太棒了！", "label": "正面"},
            {"text": "服务态度很差", "label": "负面"},
            {"text": "东西收到了", "label": "中性"},
        ]

        example_template = PromptTemplate.from_template(
            "文本: {text}\\n分类: {label}"
        )

        classifier = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_template,
            prefix="请对以下文本进行情感分类（正面/负面/中性）：",
            suffix="文本: {input}\\n分类:",
            input_variables=["input"]
        )
        ```

    思考题：
        1. PromptTemplate 和 ChatPromptTemplate 的区别？
           
           ✅ 答案：
           | 特性 | PromptTemplate | ChatPromptTemplate |
           |------|---------------|-------------------|
           | 输出 | 纯字符串 | 消息列表 |
           | 角色 | 无角色概念 | 支持 system/human/ai |
           | 适用 | 简单任务 | 对话场景 |
           | 格式 | 单个模板 | 多消息组合 |

        2. MessagesPlaceholder 有什么应用场景？
           
           ✅ 答案：
           - 注入对话历史，实现多轮记忆
           - 动态添加 Few-Shot 示例
           - 插入检索到的上下文（RAG）
           - 条件性添加系统指令
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 提示词模板")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
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
