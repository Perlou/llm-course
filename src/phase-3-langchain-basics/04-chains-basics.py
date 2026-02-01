"""
Chain 基础
==========

学习目标：
    1. 理解 Chain 的概念和作用
    2. 掌握 LCEL 管道符语法
    3. 学会组合多个组件构建链

核心概念：
    - Chain：将多个组件串联执行的处理流程
    - LCEL：使用 | 管道符构建链
    - Runnable：所有可执行组件的基类

前置知识：
    - 03-prompt-templates.py

环境要求：
    - pip install langchain langchain-google-genai python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Chain 概念 ====================


def chain_concept():
    """Chain 概念介绍"""
    print("=" * 60)
    print("第一部分：Chain 概念")
    print("=" * 60)

    print("""
    什么是 Chain？
    ─────────────
    
    Chain 是将多个组件串联起来的执行流程：
    
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │  Prompt  │ ─▶ │   LLM    │ ─▶ │  Parser  │
    └──────────┘    └──────────┘    └──────────┘
    
    LCEL 语法：chain = prompt | llm | parser
    
    核心方法：
    - invoke()  : 同步执行
    - stream()  : 流式执行
    - batch()   : 批量执行
    - ainvoke() : 异步执行
    """)


# ==================== 第二部分：构建基础链 ====================


def basic_chain():
    """构建基础链"""
    print("\n" + "=" * 60)
    print("第二部分：构建基础链")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        # 创建组件
        prompt = ChatPromptTemplate.from_template("用一句话解释{concept}")
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        parser = StrOutputParser()

        # 使用 | 构建链
        chain = prompt | llm | parser

        print("📌 链已构建: prompt | llm | parser")

        # 执行链
        result = chain.invoke({"concept": "微服务架构"})
        print(f"\n结果: {result}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第三部分：链的核心方法 ====================


def chain_methods():
    """链的核心方法"""
    print("\n" + "=" * 60)
    print("第三部分：链的核心方法")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        prompt = ChatPromptTemplate.from_template("用一句话描述{topic}")
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        chain = prompt | llm | StrOutputParser()

        # 1. invoke - 同步调用
        print("\n📌 1. invoke() - 同步调用")
        result = chain.invoke({"topic": "Python"})
        print(f"结果: {result}")

        # 2. stream - 流式调用
        print("\n📌 2. stream() - 流式调用")
        print("结果: ", end="")
        for chunk in chain.stream({"topic": "JavaScript"}):
            print(chunk, end="", flush=True)
        print()

        # 3. batch - 批量调用
        print("\n📌 3. batch() - 批量调用")
        topics = [{"topic": "Java"}, {"topic": "Rust"}]
        results = chain.batch(topics)
        for topic, result in zip(topics, results):
            print(f"  {topic['topic']}: {result}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：RunnablePassthrough ====================


def runnable_passthrough():
    """RunnablePassthrough 使用"""
    print("\n" + "=" * 60)
    print("第四部分：RunnablePassthrough")
    print("=" * 60)

    print("""
    RunnablePassthrough 用于：
    - 传递输入到下一步
    - 在链中保留原始输入
    """)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnablePassthrough

        # 示例: 保留原始问题
        prompt = ChatPromptTemplate.from_template("问题: {question}\n\n请简洁回答。")
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

        chain = {"question": RunnablePassthrough()} | prompt | llm | StrOutputParser()

        result = chain.invoke("什么是深度学习？")
        print(f"结果: {result}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第五部分：RunnableLambda ====================


def runnable_lambda():
    """RunnableLambda 使用"""
    print("\n" + "=" * 60)
    print("第五部分：RunnableLambda")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnableLambda

        # 自定义处理函数
        def preprocess(text: str) -> str:
            return text.strip().upper()

        def postprocess(text: str) -> str:
            return f"【总结】{text}"

        prompt = ChatPromptTemplate.from_template("解释: {input}")
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

        chain = (
            RunnableLambda(preprocess)
            | {"input": RunnableLambda(lambda x: x)}
            | prompt
            | llm
            | StrOutputParser()
            | RunnableLambda(postprocess)
        )

        result = chain.invoke("  machine learning  ")
        print(f"结果: {result}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：构建翻译链
        创建一个中英互译的链。

    练习 2：带预处理的链
        使用 RunnableLambda 清理输入后再处理。

    练习 3：批量处理
        使用 batch() 同时翻译多段文本。

    思考题：
        1. LCEL 相比传统链有什么优势？
        2. 何时使用 stream() 而不是 invoke()？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 Chain 基础")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
        return

    try:
        chain_concept()
        basic_chain()
        chain_methods()
        runnable_passthrough()
        runnable_lambda()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：05-lcel-expressions.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
