"""
对话式 RAG
==========

学习目标：
    1. 理解对话式 RAG 的特点
    2. 掌握历史感知检索
    3. 构建多轮对话问答系统

核心概念：
    - 对话历史：保持多轮上下文
    - 问题改写：结合历史改写当前问题
    - 历史感知检索：用改写后的问题检索

前置知识：
    - 09-qa-chains.py

环境要求：
    - pip install langchain langchain-google-genai chromadb python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：对话式 RAG 概念 ====================


def conversational_rag_concept():
    """对话式 RAG 概念"""
    print("=" * 60)
    print("第一部分：对话式 RAG 概念")
    print("=" * 60)

    print("""
    普通 RAG vs 对话式 RAG：
    ─────────────────────────
    
    普通 RAG：
    用户: Python 是什么?
    AI: Python 是一种编程语言...
    
    用户: 它的优点是什么?  ← 问题指代不清
    AI: 什么的优点？（无法理解"它"指什么）
    
    对话式 RAG：
    用户: Python 是什么?
    AI: Python 是一种编程语言...
    
    用户: 它的优点是什么?
    系统改写: "Python 的优点是什么?"  ← 自动补全上下文
    AI: Python 的优点包括简洁易读...
    
    核心能力：
    ─────────
    1. 记住对话历史
    2. 理解代词指代
    3. 用完整问题检索
    """)


# ==================== 第二部分：问题改写 ====================


def question_rewriting():
    """问题改写"""
    print("\n" + "=" * 60)
    print("第二部分：问题改写")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

        rewrite_prompt = ChatPromptTemplate.from_template("""
基于对话历史，将用户的后续问题改写为独立的完整问题。

对话历史:
{history}

后续问题: {question}

改写后的独立问题:""")

        rewrite_chain = rewrite_prompt | llm | StrOutputParser()

        # 测试
        history = "用户: Python 是什么?\nAI: Python 是一种高级编程语言。"
        question = "它有什么优点？"

        rewritten = rewrite_chain.invoke({"history": history, "question": question})

        print(f"📌 原始问题: {question}")
        print(f"📌 改写后: {rewritten}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第三部分：完整对话式 RAG ====================


def conversational_rag_chain():
    """完整对话式 RAG"""
    print("\n" + "=" * 60)
    print("第三部分：完整对话式 RAG")
    print("=" * 60)

    try:
        from langchain_google_genai import (
            ChatGoogleGenerativeAI,
            GoogleGenerativeAIEmbeddings,
        )
        from langchain_chroma import Chroma
        from langchain_core.documents import Document
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.messages import HumanMessage, AIMessage

        # 准备知识库
        docs = [
            Document(page_content="Python 是一种高级编程语言，于 1991 年发布。"),
            Document(
                page_content="Python 的优点包括语法简洁、易于学习、拥有丰富的库。"
            ),
            Document(
                page_content="Python 广泛用于数据科学、机器学习、Web 开发等领域。"
            ),
        ]

        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
        vectorstore = Chroma.from_documents(docs, embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

        # 问题改写链
        rewrite_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "将用户问题改写为独立的完整问题。如果问题已经完整，直接返回原问题。",
                ),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}"),
            ]
        )

        # 问答链
        qa_prompt = ChatPromptTemplate.from_template("""
基于以下信息回答问题：

{context}

问题：{question}
回答：""")

        def format_docs(docs):
            return "\n".join(d.page_content for d in docs)

        # 模拟多轮对话
        history = []

        def chat(question):
            # 改写问题
            if history:
                rewrite_chain = rewrite_prompt | llm | StrOutputParser()
                standalone = rewrite_chain.invoke(
                    {"history": history, "question": question}
                )
            else:
                standalone = question

            # 检索
            docs = retriever.invoke(standalone)
            context = format_docs(docs)

            # 生成回答
            qa_chain = qa_prompt | llm | StrOutputParser()
            answer = qa_chain.invoke({"context": context, "question": standalone})

            # 更新历史
            history.append(HumanMessage(content=question))
            history.append(AIMessage(content=answer))

            return answer

        # 测试多轮对话
        questions = ["Python 是什么？", "它有什么优点？", "可以用来做什么？"]

        print("📌 多轮对话测试：")
        for q in questions:
            answer = chat(q)
            print(f"\n用户: {q}")
            print(f"AI: {answer}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：使用 LangChain 内置方案 ====================


def langchain_solution():
    """LangChain 内置方案"""
    print("\n" + "=" * 60)
    print("第四部分：LangChain 内置方案")
    print("=" * 60)

    code_example = """
    from langchain.chains import create_history_aware_retriever
    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain
    
    # 创建历史感知检索器
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    
    # 创建问答链
    question_answer_chain = create_stuff_documents_chain(
        llm, qa_prompt
    )
    
    # 组合成 RAG 链
    rag_chain = create_retrieval_chain(
        history_aware_retriever,
        question_answer_chain
    )
    
    # 使用
    response = rag_chain.invoke({
        "input": "它有什么优点?",
        "chat_history": [
            HumanMessage("Python 是什么?"),
            AIMessage("Python 是一种编程语言...")
        ]
    })
    """
    print("📌 使用 LangChain 内置函数：")
    print(code_example)


# ==================== 第五部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：完整实现
        实现一个完整的多轮对话知识问答系统。

        ✅ 参考答案：
        ```python
        from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.messages import HumanMessage, AIMessage

        class ConversationalRAG:
            def __init__(self, docs, embedding_model, llm_model):
                embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model)
                self.vectorstore = Chroma.from_documents(docs, embeddings)
                self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
                self.llm = ChatGoogleGenerativeAI(model=llm_model)
                self.history = []

            def chat(self, question: str) -> str:
                # 改写问题（如果有历史）
                if self.history:
                    standalone = self._rewrite_question(question)
                else:
                    standalone = question

                # 检索和回答
                docs = self.retriever.invoke(standalone)
                context = "\\n".join(d.page_content for d in docs)
                answer = self._generate_answer(context, question)

                # 更新历史
                self.history.append(HumanMessage(content=question))
                self.history.append(AIMessage(content=answer))
                
                return answer

            def _rewrite_question(self, q):
                # 使用 LLM 改写问题
                ...

            def _generate_answer(self, context, question):
                # 生成回答
                ...
        ```

    练习 2：历史管理
        限制历史长度，避免上下文过长。

        ✅ 参考答案：
        ```python
        class HistoryManager:
            def __init__(self, max_turns: int = 5):
                self.max_turns = max_turns
                self.history = []

            def add(self, user_msg: str, ai_msg: str):
                self.history.append(HumanMessage(content=user_msg))
                self.history.append(AIMessage(content=ai_msg))
                # 保持最近 N 轮
                if len(self.history) > self.max_turns * 2:
                    self.history = self.history[-self.max_turns * 2:]

            def get_history(self):
                return self.history

            def clear(self):
                self.history = []

            def summarize(self, llm):
                # 对历史进行摘要压缩
                if len(self.history) > 6:
                    old_history = self.history[:-4]
                    summary = llm.invoke(f"总结以下对话要点：{old_history}")
                    self.history = [AIMessage(content=f"[之前的对话摘要]{summary}")] + self.history[-4:]
        ```

    练习 3：交互界面
        添加命令行交互，支持持续对话。

        ✅ 参考答案：
        ```python
        def interactive_chat(rag_system):
            print("欢迎使用知识问答系统！输入 'quit' 退出, 'clear' 清空历史")
            
            while True:
                user_input = input("\\n你: ").strip()
                
                if user_input.lower() == 'quit':
                    print("再见！")
                    break
                elif user_input.lower() == 'clear':
                    rag_system.clear_history()
                    print("历史已清空")
                    continue
                elif not user_input:
                    continue
                
                answer = rag_system.chat(user_input)
                print(f"AI: {answer}")

        # 使用
        interactive_chat(my_rag)
        ```

    思考题：
        1. 历史太长时如何处理？
           
           ✅ 答案：
           - 滑动窗口：只保留最近 N 轮
           - 摘要压缩：用 LLM 压缩旧历史
           - Token 限制：按 token 数截断
           - 分层存储：重要信息持久化

        2. 如何评估对话式 RAG 的效果？
           
           ✅ 答案：
           - 回答准确性：人工标注评分
           - 上下文理解：代词解析正确率
           - 检索相关性：Recall@K
           - 对话连贯性：人工评估流畅度
           - 用户满意度：A/B 测试
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 对话式 RAG")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
        return

    try:
        conversational_rag_concept()
        question_rewriting()
        conversational_rag_chain()
        langchain_solution()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：11-project-knowledge-base.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
