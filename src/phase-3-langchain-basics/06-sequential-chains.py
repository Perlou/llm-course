"""
顺序链
======

学习目标：
    1. 理解顺序链的概念
    2. 掌握多步骤链的构建
    3. 学会在链之间传递数据

核心概念：
    - 顺序链：多个步骤按顺序执行
    - 数据传递：前一步输出作为后一步输入
    - 中间结果：保留链执行中的中间状态

前置知识：
    - 05-lcel-expressions.py

环境要求：
    - pip install langchain langchain-google-genai python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：顺序链概念 ====================


def sequential_concept():
    """顺序链概念"""
    print("=" * 60)
    print("第一部分：顺序链概念")
    print("=" * 60)

    print("""
    顺序链工作流程：
    
    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │  输入   │ ─▶ │ Step 1  │ ─▶ │ Step 2  │ ─▶ │  输出   │
    └─────────┘    └─────────┘    └─────────┘    └─────────┘
    
    典型应用：
    - 生成大纲 -> 写文章 -> 修改润色
    - 分析数据 -> 生成报告 -> 总结结论
    - 理解问题 -> 搜索资料 -> 生成答案
    """)


# ==================== 第二部分：构建多步骤链 ====================


def multi_step_chain():
    """构建多步骤链"""
    print("\n" + "=" * 60)
    print("第二部分：构建多步骤链")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnablePassthrough

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

        # 步骤1: 生成大纲
        outline_prompt = ChatPromptTemplate.from_template(
            "为'{topic}'生成一个3点的简短大纲"
        )

        # 步骤2: 扩展内容
        expand_prompt = ChatPromptTemplate.from_template(
            "基于以下大纲，写一段100字的介绍：\n{outline}"
        )

        # 构建顺序链
        chain = (
            {"topic": RunnablePassthrough()}
            | outline_prompt
            | llm
            | StrOutputParser()
            | {"outline": RunnablePassthrough()}
            | expand_prompt
            | llm
            | StrOutputParser()
        )

        print("📌 执行两步链: 生成大纲 -> 扩展内容")
        result = chain.invoke("Python编程")
        print(f"\n最终结果:\n{result}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第三部分：保留中间结果 ====================


def preserve_intermediate():
    """保留中间结果"""
    print("\n" + "=" * 60)
    print("第三部分：保留中间结果")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnablePassthrough, RunnableParallel

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

        # 步骤1: 生成大纲
        outline_chain = (
            ChatPromptTemplate.from_template("为'{topic}'生成3点大纲")
            | llm
            | StrOutputParser()
        )

        # 步骤2: 生成标题
        title_chain = (
            ChatPromptTemplate.from_template("为以下大纲起一个标题：\n{outline}")
            | llm
            | StrOutputParser()
        )

        # 保留中间结果
        def build_result(inputs):
            return {
                "topic": inputs["topic"],
                "outline": inputs["outline"],
                "title": inputs["title"],
            }

        chain = (
            RunnableParallel(topic=RunnablePassthrough())
            | RunnableParallel(
                topic=lambda x: x["topic"],
                outline=lambda x: outline_chain.invoke(x["topic"]),
            )
            | RunnableParallel(
                topic=lambda x: x["topic"],
                outline=lambda x: x["outline"],
                title=lambda x: title_chain.invoke({"outline": x["outline"]}),
            )
        )

        print("📌 执行链并保留所有中间结果")
        result = chain.invoke("机器学习")

        print(f"\n主题: {result['topic']}")
        print(f"\n大纲:\n{result['outline']}")
        print(f"\n标题: {result['title']}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：实战：文章生成流程 ====================


def article_generation():
    """实战：文章生成流程"""
    print("\n" + "=" * 60)
    print("第四部分：实战 - 文章生成流程")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

        # 完整流程
        prompts = {
            "outline": "为'{topic}'写一个3点大纲",
            "draft": "基于大纲写200字文章：\n{outline}",
            "polish": "润色以下文章，使其更流畅：\n{draft}",
        }

        print("📌 执行完整写作流程")
        print("   1. 生成大纲 -> 2. 撰写初稿 -> 3. 润色修改")

        # 步骤执行
        topic = "人工智能的应用"

        outline = (
            ChatPromptTemplate.from_template(prompts["outline"])
            | llm
            | StrOutputParser()
        ).invoke({"topic": topic})
        print(f"\n✓ 大纲完成")

        draft = (
            ChatPromptTemplate.from_template(prompts["draft"]) | llm | StrOutputParser()
        ).invoke({"outline": outline})
        print("✓ 初稿完成")

        final = (
            ChatPromptTemplate.from_template(prompts["polish"])
            | llm
            | StrOutputParser()
        ).invoke({"draft": draft})
        print("✓ 润色完成")

        print(f"\n最终文章:\n{final}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第五部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：翻译润色链
        创建：翻译成英文 -> 语法检查 -> 润色

    练习 2：代码审查链
        创建：分析代码 -> 找出问题 -> 给出建议

    练习 3：摘要生成链
        创建：理解文本 -> 提取要点 -> 生成摘要

    思考题：
        1. 何时需要保留中间结果？
        2. 步骤过多会有什么问题？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 顺序链")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
        return

    try:
        sequential_concept()
        multi_step_chain()
        preserve_intermediate()
        article_generation()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：07-memory-types.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
