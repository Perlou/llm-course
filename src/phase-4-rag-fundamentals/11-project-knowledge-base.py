"""
实战项目：个人知识库问答系统
============================

学习目标：
    1. 综合运用 RAG 所学知识
    2. 构建完整的知识库系统
    3. 实现多轮对话问答

项目功能：
    - 文档加载和分割
    - 向量存储和检索
    - 多轮对话问答
    - 来源引用

环境要求：
    - pip install langchain langchain-openai chromadb python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 知识库系统类 ====================


class PersonalKnowledgeBase:
    """个人知识库问答系统"""

    def __init__(self, persist_directory: str = None):
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.messages import HumanMessage, AIMessage

        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model="gpt-3.5-turbo")
        self.persist_dir = persist_directory
        self.vectorstore = None
        self.history = []

        # 如果有持久化目录，尝试加载
        if persist_directory and os.path.exists(persist_directory):
            self.vectorstore = Chroma(
                persist_directory=persist_directory, embedding_function=self.embeddings
            )
            print(f"✅ 已加载知识库: {persist_directory}")

    def add_documents(self, file_paths: list):
        """添加文档到知识库"""
        from langchain_community.document_loaders import TextLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_chroma import Chroma

        all_docs = []

        for path in file_paths:
            if os.path.exists(path):
                loader = TextLoader(path, encoding="utf-8")
                docs = loader.load()
                all_docs.extend(docs)
                print(f"  ✓ 加载: {path}")

        if not all_docs:
            print("❌ 没有加载到任何文档")
            return

        # 分割
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(all_docs)
        print(f"  ✓ 分割为 {len(chunks)} 个块")

        # 存储
        if self.vectorstore:
            self.vectorstore.add_documents(chunks)
        else:
            self.vectorstore = Chroma.from_documents(
                chunks, self.embeddings, persist_directory=self.persist_dir
            )

        print(f"✅ 已添加 {len(chunks)} 个文档块")

    def _rewrite_question(self, question: str) -> str:
        """改写问题"""
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        if not self.history:
            return question

        prompt = ChatPromptTemplate.from_template("""
基于对话历史，将问题改写为独立的完整问题。

历史：
{history}

问题：{question}

独立问题：""")

        chain = prompt | self.llm | StrOutputParser()

        history_text = "\n".join(
            [
                f"{'用户' if i % 2 == 0 else 'AI'}: {msg.content}"
                for i, msg in enumerate(self.history[-4:])  # 只用最近2轮
            ]
        )

        return chain.invoke({"history": history_text, "question": question})

    def chat(self, question: str) -> dict:
        """问答"""
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.messages import HumanMessage, AIMessage

        if not self.vectorstore:
            return {"answer": "❌ 知识库为空，请先添加文档", "sources": []}

        # 改写问题
        standalone = self._rewrite_question(question)

        # 检索
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(standalone)

        if not docs:
            return {"answer": "未找到相关信息", "sources": []}

        # 构建上下文
        context = "\n\n".join(
            [f"[{i + 1}] {d.page_content}" for i, d in enumerate(docs)]
        )

        sources = [d.metadata.get("source", "unknown") for d in docs]

        # 生成回答
        prompt = ChatPromptTemplate.from_template("""
基于以下信息回答问题。在回答末尾标注引用的信息编号。

参考信息：
{context}

问题：{question}

回答：""")

        chain = prompt | self.llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": standalone})

        # 更新历史
        self.history.append(HumanMessage(content=question))
        self.history.append(AIMessage(content=answer))

        return {"answer": answer, "sources": list(set(sources))}

    def clear_history(self):
        """清空对话历史"""
        self.history = []
        print("✓ 对话历史已清空")


# ==================== 演示 ====================


def demo():
    """演示知识库系统"""
    print("=" * 60)
    print("🚀 个人知识库问答系统演示")
    print("=" * 60)

    import tempfile

    # 创建测试文档
    temp_dir = tempfile.mkdtemp()

    docs_content = {
        "python.txt": """
Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年创建。
Python 的设计哲学强调代码可读性，使用缩进来定义代码块。
Python 支持多种编程范式，包括面向对象、命令式、函数式编程。
Python 拥有丰富的标准库和第三方库生态系统。
""",
        "ml.txt": """
机器学习是人工智能的一个分支，让计算机从数据中学习。
监督学习使用带标签的数据进行训练。
无监督学习从无标签数据中发现模式。
深度学习使用多层神经网络处理复杂问题。
""",
    }

    for name, content in docs_content.items():
        with open(os.path.join(temp_dir, name), "w") as f:
            f.write(content)

    # 创建知识库
    print("\n📚 创建知识库...")
    kb = PersonalKnowledgeBase()

    # 添加文档
    print("\n📄 添加文档...")
    kb.add_documents([os.path.join(temp_dir, name) for name in docs_content])

    # 测试问答
    print("\n💬 多轮对话测试：")

    questions = [
        "Python 是什么？",
        "它是谁创建的？",
        "机器学习有哪些类型？",
    ]

    for q in questions:
        result = kb.chat(q)
        print(f"\n用户: {q}")
        print(f"AI: {result['answer']}")
        print(f"来源: {result['sources']}")

    # 清理
    import shutil

    shutil.rmtree(temp_dir)


# ==================== 交互模式代码 ====================


def interactive_code():
    """交互模式代码示例"""
    print("\n" + "=" * 60)
    print("交互模式代码示例")
    print("=" * 60)

    code = """
# 使用示例

from knowledge_base import PersonalKnowledgeBase

# 创建知识库（支持持久化）
kb = PersonalKnowledgeBase(persist_directory="./my_kb")

# 添加文档
kb.add_documents([
    "./docs/python.txt",
    "./docs/ml.txt",
])

# 交互式问答
print("知识库问答系统 (输入 'quit' 退出)")

while True:
    question = input("\\n你: ")
    
    if question.lower() == 'quit':
        break
    
    if question.lower() == 'clear':
        kb.clear_history()
        continue
    
    result = kb.chat(question)
    print(f"AI: {result['answer']}")
    print(f"来源: {', '.join(result['sources'])}")
"""
    print(code)


# ==================== 主函数 ====================


def main():
    """主函数"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 OPENAI_API_KEY")
        return

    try:
        demo()
        interactive_code()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback

        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("🎉 Phase 4 RAG 基础课程全部完成！")
    print("下一步：进入 Phase 5 学习 RAG 高级技术")
    print("=" * 60)


if __name__ == "__main__":
    main()
