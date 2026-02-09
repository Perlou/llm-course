"""
问答链
======

学习目标：
    1. 理解 RAG 问答的完整流程
    2. 掌握问答链的构建方法
    3. 学会自定义提示词模板

核心概念：
    - RAG Chain：检索增强生成链
    - Context：检索到的上下文
    - Prompt Template：问答提示词模板

前置知识：
    - 08-retrieval-basics.py

环境要求：
    - pip install langchain langchain-google-genai chromadb python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：RAG 流程 ====================


def rag_overview():
    """RAG 流程概述"""
    print("=" * 60)
    print("第一部分：RAG 流程")
    print("=" * 60)

    print("""
    RAG (Retrieval-Augmented Generation)：
    ─────────────────────────────────────
    
    ┌─────────┐    ┌──────────┐    ┌───────────┐    ┌────────┐
    │  Query  │ ─▶ │ Retriever│ ─▶ │  Context  │ ─▶ │  LLM   │
    └─────────┘    └──────────┘    └───────────┘    └────────┘
                                         │              │
                                         └──────┬───────┘
                                                ▼
                                          ┌──────────┐
                                          │  Answer  │
                                          └──────────┘
    
    核心步骤：
    ─────────
    1. 用户提问
    2. 检索相关文档
    3. 将问题和文档组合成提示词
    4. LLM 生成回答
    """)


# ==================== 第二部分：基础 QA 链 ====================


def basic_qa_chain():
    """基础 QA 链"""
    print("\n" + "=" * 60)
    print("第二部分：基础 QA 链")
    print("=" * 60)

    try:
        from langchain_google_genai import (
            ChatGoogleGenerativeAI,
            GoogleGenerativeAIEmbeddings,
        )
        from langchain_chroma import Chroma
        from langchain_core.documents import Document
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnablePassthrough

        # 准备知识库
        docs = [
            Document(
                page_content="Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年创建。"
            ),
            Document(
                page_content="Python 的设计哲学强调代码可读性，使用空白缩进来定义代码块。"
            ),
            Document(
                page_content="Python 支持多种编程范式，包括面向对象、命令式、函数式编程。"
            ),
        ]

        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vectorstore = Chroma.from_documents(docs, embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

        # 构建 QA 链
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

        prompt = ChatPromptTemplate.from_template("""
基于以下信息回答问题。如果信息中没有相关内容，请说明无法回答。

相关信息：
{context}

问题：{question}

回答：""")

        def format_docs(docs):
            return "\n".join(doc.page_content for doc in docs)

        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        # 测试
        question = "Python 是谁创建的？"
        answer = chain.invoke(question)

        print(f"📌 问题: {question}")
        print(f"📌 回答: {answer}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第三部分：带源引用的 QA ====================


def qa_with_sources():
    """带源引用的 QA"""
    print("\n" + "=" * 60)
    print("第三部分：带源引用的 QA")
    print("=" * 60)

    try:
        from langchain_google_genai import (
            ChatGoogleGenerativeAI,
            GoogleGenerativeAIEmbeddings,
        )
        from langchain_chroma import Chroma
        from langchain_core.documents import Document
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        docs = [
            Document(
                page_content="AI 可以自动驾驶汽车", metadata={"source": "tech-news.txt"}
            ),
            Document(
                page_content="机器学习用于医疗诊断",
                metadata={"source": "health-report.pdf"},
            ),
        ]

        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vectorstore = Chroma.from_documents(docs, embeddings)
        retriever = vectorstore.as_retriever()

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

        prompt = ChatPromptTemplate.from_template("""
基于以下信息回答问题，并引用来源。

{context}

问题：{question}

请以"回答：...（来源：...）"的格式回复。""")

        def format_docs_with_source(docs):
            return "\n".join(
                f"内容: {d.page_content}\n来源: {d.metadata.get('source', 'unknown')}"
                for d in docs
            )

        # 检索并回答
        question = "AI 有什么应用？"
        docs = retriever.invoke(question)
        context = format_docs_with_source(docs)

        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})

        print(f"📌 问题: {question}")
        print(f"📌 回答: {answer}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：自定义提示词 ====================


def custom_prompts():
    """自定义提示词"""
    print("\n" + "=" * 60)
    print("第四部分：自定义提示词")
    print("=" * 60)

    print("""
    常用 QA 提示词模板：
    ──────────────────
    """)

    templates = {
        "标准问答": """
基于以下信息回答问题：
{context}

问题：{question}
回答：""",
        "严格模式": """
仅基于以下信息回答。如果信息不足，回复"根据提供的资料无法回答"。

资料：
{context}

问题：{question}
回答：""",
        "专业模式": """
你是一位专业顾问。基于以下资料，用专业但易懂的语言回答。

参考资料：
{context}

客户问题：{question}
专业解答：""",
    }

    for name, template in templates.items():
        print(f"📌 {name}:")
        print(template[:100] + "...")
        print()


# ==================== 第五部分：Stuff vs Map-Reduce ====================


def chain_types():
    """不同链类型"""
    print("\n" + "=" * 60)
    print("第五部分：链类型对比")
    print("=" * 60)

    print("""
    QA 链的不同策略：
    ────────────────
    
    1. Stuff（填充）
       - 将所有文档塞入一个提示词
       - 简单快速
       - 受上下文长度限制
    
    2. Map-Reduce
       - 先对每个文档单独回答
       - 再合并所有回答
       - 适合大量文档
    
    3. Refine（精炼）
       - 逐个文档迭代更新答案
       - 质量较高
       - 速度较慢
    
    4. Map-Rerank
       - 对每个文档生成答案和分数
       - 返回最高分答案
       - 适合有唯一答案的问题
    
    推荐：
    - 文档少于 4 个：Stuff
    - 文档多：Map-Reduce 或 Refine
    """)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：构建知识问答
        用自己的文档构建 QA 系统。

        ✅ 参考答案：
        ```python
        from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.documents import Document
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnablePassthrough

        # 加载文档
        docs = [
            Document(page_content="公司产品A支持...", metadata={"source": "product.txt"}),
            Document(page_content="退款政策：7天内...", metadata={"source": "policy.txt"}),
        ]

        # 构建向量库
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vectorstore = Chroma.from_documents(docs, embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        # 构建 QA 链
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        prompt = ChatPromptTemplate.from_template('''
        基于以下信息回答问题：
        {context}
        问题：{question}
        ''')

        def format_docs(docs):
            return "\\n".join(d.page_content for d in docs)

        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt | llm | StrOutputParser()
        )

        answer = chain.invoke("退款政策是什么？")
        ```

    练习 2：优化提示词
        测试不同提示词对回答质量的影响。

        ✅ 参考答案：
        ```python
        prompts = {
            "简洁": "基于信息回答：{context}\\n问题：{question}",
            "严格": "仅基于以下信息回答，无关信息回复'无法回答'：\\n{context}\\n问题：{question}",
            "专业": "作为专业客服，友好专业地回答：\\n参考资料：{context}\\n问题：{question}",
        }

        for name, template in prompts.items():
            prompt = ChatPromptTemplate.from_template(template)
            chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt | llm | StrOutputParser()
            )
            answer = chain.invoke("退款政策？")
            print(f"{name}: {answer[:100]}...")
        ```

    练习 3：添加来源追溯
        在回答中显示引用的文档来源。

        ✅ 参考答案：
        ```python
        def qa_with_sources(question: str):
            # 检索
            docs = retriever.invoke(question)
            
            # 格式化（带来源）
            context = "\\n".join([
                f"[{d.metadata.get('source', 'unknown')}] {d.page_content}"
                for d in docs
            ])
            
            prompt = ChatPromptTemplate.from_template('''
            基于以下资料回答问题，并在回答末尾标注引用来源。
            
            资料：
            {context}
            
            问题：{question}
            ''')
            
            answer = (prompt | llm | StrOutputParser()).invoke({
                "context": context, "question": question
            })
            
            return {
                "answer": answer,
                "sources": [d.metadata.get("source") for d in docs]
            }
        ```

    思考题：
        1. 如何处理检索到无关文档的情况？
           
           ✅ 答案：
           - 提示词中明确说明"如无相关信息则回复无法回答"
           - 使用相似度阈值过滤低分文档
           - 检索后用 LLM 判断文档是否相关
           - 结合多种检索策略（关键词+向量）

        2. 如何提高回答的准确性？
           
           ✅ 答案：
           - 改进文档分块策略
           - 优化 Embedding 模型选择
           - 使用 MMR 增加多样性
           - 提示词中强调"基于证据回答"
           - 实现答案验证/自我修正机制
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 问答链")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
        return

    try:
        rag_overview()
        basic_qa_chain()
        qa_with_sources()
        custom_prompts()
        chain_types()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：10-conversational-rag.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
