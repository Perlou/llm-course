"""
LCEL 表达式
===========

学习目标：
    1. 深入理解 LCEL 语法
    2. 掌握 RunnableParallel 并行执行
    3. 学会使用 RunnableBranch 条件分支

核心概念：
    - RunnableParallel：并行执行多个链
    - RunnableBranch：条件分支选择
    - bind()：绑定参数

前置知识：
    - 04-chains-basics.py

环境要求：
    - pip install langchain langchain-google-genai python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：LCEL 核心语法 ====================


def lcel_syntax():
    """LCEL 核心语法"""
    print("=" * 60)
    print("第一部分：LCEL 核心语法")
    print("=" * 60)

    print("""
    LCEL 核心操作符：
    
    | 操作符 | 类型   | 说明                    |
    |-------|-------|------------------------|
    |   |   | 管道符 | 串联组件，前一个输出是后一个输入 |
    |  {}   | 字典   | 构造字典，可并行执行多个分支   |
    
    核心 Runnable：
    - RunnablePassthrough: 透传输入
    - RunnableLambda: 自定义函数
    - RunnableParallel: 并行执行
    - RunnableBranch: 条件分支
    """)


# ==================== 第二部分：RunnableParallel 并行执行 ====================


def runnable_parallel():
    """RunnableParallel 并行执行"""
    print("\n" + "=" * 60)
    print("第二部分：RunnableParallel 并行执行")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnableParallel

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

        # 创建并行链
        parallel_chain = RunnableParallel(
            summary=ChatPromptTemplate.from_template("用一句话总结{topic}")
            | llm
            | StrOutputParser(),
            keywords=ChatPromptTemplate.from_template("列出{topic}的3个关键词")
            | llm
            | StrOutputParser(),
            question=ChatPromptTemplate.from_template("针对{topic}提一个问题")
            | llm
            | StrOutputParser(),
        )

        print("📌 并行执行三个任务...")
        result = parallel_chain.invoke({"topic": "人工智能"})

        print(f"\n总结: {result['summary']}")
        print(f"\n关键词: {result['keywords']}")
        print(f"\n问题: {result['question']}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第三部分：RunnableBranch 条件分支 ====================


def runnable_branch():
    """RunnableBranch 条件分支"""
    print("\n" + "=" * 60)
    print("第三部分：RunnableBranch 条件分支")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnableBranch

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

        # 分类函数
        def is_technical(x):
            keywords = ["代码", "编程", "技术", "API", "算法"]
            return any(k in x["input"] for k in keywords)

        # 条件分支链
        branch_chain = RunnableBranch(
            (
                is_technical,
                ChatPromptTemplate.from_template("作为技术专家回答: {input}")
                | llm
                | StrOutputParser(),
            ),
            # 默认分支
            ChatPromptTemplate.from_template("作为通用助手回答: {input}")
            | llm
            | StrOutputParser(),
        )

        print("📌 技术问题路由到技术专家")
        result1 = branch_chain.invoke({"input": "如何优化Python代码性能？"})
        print(f"结果: {result1}")

        print("\n📌 通用问题路由到通用助手")
        result2 = branch_chain.invoke({"input": "今天天气怎么样？"})
        print(f"结果: {result2}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：bind 绑定参数 ====================


def bind_parameters():
    """bind 绑定参数"""
    print("\n" + "=" * 60)
    print("第四部分：bind 绑定参数")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

        # 绑定停止词
        llm_with_stop = llm.bind(stop=["\n\n"])

        prompt = ChatPromptTemplate.from_template("列出{topic}的优点：")
        chain = prompt | llm_with_stop | StrOutputParser()

        print("📌 使用 bind 绑定停止词")
        result = chain.invoke({"topic": "Python"})
        print(f"结果: {result}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第五部分：with_fallbacks 回退机制 ====================


def fallbacks_demo():
    """with_fallbacks 回退机制"""
    print("\n" + "=" * 60)
    print("第五部分：with_fallbacks 回退机制")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        # 主模型和回退模型（都使用 Gemini）
        primary = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
        fallback = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

        # 配置回退
        llm_with_fallback = primary.with_fallbacks([fallback])

        prompt = ChatPromptTemplate.from_template("解释{concept}")
        chain = prompt | llm_with_fallback | StrOutputParser()

        print("📌 使用 with_fallbacks 配置回退")
        result = chain.invoke({"concept": "量子计算"})
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
    练习 1：并行分析
        使用 RunnableParallel 同时分析文本的情感和摘要。

        ✅ 参考答案：
        ```python
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnableParallel

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

        analysis_chain = RunnableParallel(
            sentiment=ChatPromptTemplate.from_template(
                "分析以下文本的情感倾向（正面/负面/中性）：{text}"
            ) | llm | StrOutputParser(),
            summary=ChatPromptTemplate.from_template(
                "用一句话总结以下文本：{text}"
            ) | llm | StrOutputParser(),
            keywords=ChatPromptTemplate.from_template(
                "提取以下文本的3个关键词：{text}"
            ) | llm | StrOutputParser(),
        )

        result = analysis_chain.invoke({"text": "这款产品质量非常好，值得推荐"})
        print(f"情感: {result['sentiment']}")
        print(f"摘要: {result['summary']}")
        print(f"关键词: {result['keywords']}")
        ```

    练习 2：智能路由
        使用 RunnableBranch 根据问题类型选择不同处理。

        ✅ 参考答案：
        ```python
        from langchain_core.runnables import RunnableBranch

        def is_math_question(x):
            keywords = ["计算", "求", "等于", "+", "-", "*", "/"]
            return any(k in x["input"] for k in keywords)

        def is_code_question(x):
            keywords = ["代码", "程序", "函数", "bug", "错误"]
            return any(k in x["input"] for k in keywords)

        smart_router = RunnableBranch(
            (is_math_question,
             ChatPromptTemplate.from_template("作为数学专家解答: {input}") | llm | StrOutputParser()),
            (is_code_question,
             ChatPromptTemplate.from_template("作为编程专家解答: {input}") | llm | StrOutputParser()),
            # 默认
            ChatPromptTemplate.from_template("回答: {input}") | llm | StrOutputParser()
        )
        ```

    练习 3：回退链
        配置多个回退模型确保服务可用性。

        ✅ 参考答案：
        ```python
        # 主模型
        primary = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
        
        # 回退模型（可以用不同配置或不同模型）
        fallback1 = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
        fallback2 = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.5)

        # 配置回退链
        robust_llm = primary.with_fallbacks([fallback1, fallback2])

        # 在链中使用
        chain = prompt | robust_llm | StrOutputParser()
        ```

    思考题：
        1. 并行执行有什么性能优势？
           
           ✅ 答案：
           - 减少总耗时：多个 API 调用同时进行
           - 提高吞吐量：充分利用网络 I/O
           - 适合独立任务：各分支互不依赖时效果最佳
           - 注意：并行会消耗更多 token 配额

        2. 条件分支有什么应用场景？
           
           ✅ 答案：
           - 智能问答路由：技术/生活/学习问题分发
           - 多模型选择：根据任务复杂度选模型
           - 语言检测：自动选择对应语言处理
           - 敏感内容过滤：敏感问题特殊处理
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 LCEL 表达式")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
        return

    try:
        lcel_syntax()
        runnable_parallel()
        runnable_branch()
        bind_parameters()
        fallbacks_demo()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：06-sequential-chains.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
