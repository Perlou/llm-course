"""
父文档检索
==========

学习目标：
    1. 理解父文档检索的原理
    2. 掌握小块检索、大块返回策略
    3. 学会构建层次化文档结构

核心概念：
    - Parent Chunk：父块（大块，保留上下文）
    - Child Chunk：子块（小块，精确检索）
    - 双向映射：子块 → 父块

前置知识：
    - 02-reranking.py

环境要求：
    - pip install langchain langchain-openai chromadb python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：父文档检索概念 ====================


def parent_document_concept():
    """父文档检索概念"""
    print("=" * 60)
    print("第一部分：父文档检索概念")
    print("=" * 60)

    print("""
    小块检索的问题：
    ───────────────
    - 检索精确，但上下文不足
    - LLM 可能无法获得完整信息
    
    大块检索的问题：
    ───────────────
    - 上下文丰富，但检索不精确
    - 包含太多无关内容
    
    父文档检索策略：
    ───────────────
    小块检索 + 大块返回 = 最佳平衡！
    
    ┌─────────────────────────────────────────────────┐
    │  父文档 (2000 字符)                              │
    │  ┌─────────────────────────────────────────┐   │
    │  │ 包含完整上下文                            │   │
    │  │                                         │   │
    │  │   ┌────────┐ ┌────────┐ ┌────────┐     │   │
    │  │   │ 子块1  │ │ 子块2  │ │ 子块3  │     │   │
    │  │   │(400字) │ │(400字) │ │(400字) │     │   │
    │  │   └────────┘ └────────┘ └────────┘     │   │
    │  │       ▲           匹配！                  │   │
    │  └───────│─────────────────────────────────┘   │
    │          │                                     │
    │     Query 匹配子块2 → 返回整个父文档            │
    └─────────────────────────────────────────────────┘
    """)


# ==================== 第二部分：手动实现 ====================


def manual_implementation():
    """手动实现父文档检索"""
    print("\n" + "=" * 60)
    print("第二部分：手动实现")
    print("=" * 60)

    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document
    import uuid

    # 准备文档
    document = """
人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。

机器学习是人工智能的一个子领域。它使计算机能够从数据中学习，而无需明确编程。监督学习、无监督学习和强化学习是三种主要的机器学习方法。

深度学习是机器学习的一个分支，使用多层神经网络。卷积神经网络（CNN）用于图像处理，循环神经网络（RNN）用于序列数据处理。

自然语言处理（NLP）让机器理解人类语言。GPT、BERT 等模型在文本理解和生成方面取得了突破性进展。
"""

    # 创建父分割器
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)

    # 创建子分割器
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=20)

    # 分割并建立映射
    parent_chunks = parent_splitter.split_text(document)
    parent_docs = {}
    child_docs = []

    for parent_text in parent_chunks:
        parent_id = str(uuid.uuid4())
        parent_docs[parent_id] = parent_text

        # 创建子块
        child_texts = child_splitter.split_text(parent_text)
        for child_text in child_texts:
            child_docs.append(
                Document(page_content=child_text, metadata={"parent_id": parent_id})
            )

    print(f"📌 分割结果：")
    print(f"  父块数量: {len(parent_docs)}")
    print(f"  子块数量: {len(child_docs)}")

    print("\n父块示例：")
    for pid, ptext in list(parent_docs.items())[:1]:
        print(f"  [{pid[:8]}...] {ptext[:50]}...")

    print("\n子块示例：")
    for cdoc in child_docs[:2]:
        print(
            f"  [parent: {cdoc.metadata['parent_id'][:8]}...] {cdoc.page_content[:40]}..."
        )


# ==================== 第三部分：LangChain ParentDocumentRetriever ====================


def langchain_parent_retriever():
    """LangChain 父文档检索器"""
    print("\n" + "=" * 60)
    print("第三部分：LangChain ParentDocumentRetriever")
    print("=" * 60)

    try:
        from langchain.retrievers import ParentDocumentRetriever
        from langchain.storage import InMemoryStore
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_openai import OpenAIEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.documents import Document

        # 准备文档
        docs = [
            Document(
                page_content="""
Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年创建。它的设计哲学强调代码可读性，使用缩进来定义代码块。Python 支持多种编程范式，包括面向对象、命令式和函数式编程。
            """
            ),
            Document(
                page_content="""
机器学习是人工智能的一个分支，让计算机从数据中学习。监督学习使用标记数据，无监督学习发现数据中的模式。强化学习通过奖励信号优化策略。
            """
            ),
        ]

        # 创建存储
        store = InMemoryStore()

        # 创建分割器
        parent_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
        child_splitter = RecursiveCharacterTextSplitter(chunk_size=100)

        # 创建检索器
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma(
            collection_name="child_chunks", embedding_function=embeddings
        )

        retriever = ParentDocumentRetriever(
            vectorstore=vectorstore,
            docstore=store,
            child_splitter=child_splitter,
            parent_splitter=parent_splitter,
        )

        # 添加文档
        retriever.add_documents(docs)

        # 检索
        query = "Python 的设计理念"
        results = retriever.invoke(query)

        print(f"📌 查询: '{query}'")
        print(f"\n检索到 {len(results)} 个父文档：")
        for doc in results:
            print(f"  {doc.page_content[:80]}...")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：多级层次结构 ====================


def multi_level_hierarchy():
    """多级层次结构"""
    print("\n" + "=" * 60)
    print("第四部分：多级层次结构")
    print("=" * 60)

    print("""
    三级层次示例：
    ─────────────
    
    文档级 (完整文章)
        │
        ├── 章节级 (每章约 2000 字)
        │       │
        │       ├── 段落级 (每段约 500 字)
        │       │       │
        │       │       └── 句子级 (检索单元)
        │       │
        │       └── ...
        │
        └── ...
    
    检索策略：
    - 用句子级做精确匹配
    - 返回段落级或章节级
    - 根据需求灵活调整
    """)

    code_example = '''
class MultiLevelRetriever:
    """多级层次检索器"""
    
    def __init__(self, vectorstore, level_map):
        self.vectorstore = vectorstore
        self.level_map = level_map  # child_id -> parent_ids
    
    def retrieve(self, query, return_level="paragraph"):
        # 在句子级检索
        matches = self.vectorstore.similarity_search(query)
        
        # 根据需要返回的层级获取父文档
        parent_ids = set()
        for match in matches:
            chain = self.level_map[match.metadata["id"]]
            parent_ids.add(chain[return_level])
        
        return [self.get_doc(pid) for pid in parent_ids]
'''
    print("📌 多级检索器示例：")
    print(code_example)


# ==================== 第五部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：参数调优
        测试不同父块/子块大小对检索效果的影响。

    练习 2：持久化存储
        使用 Redis 或 SQLite 替代 InMemoryStore。

    练习 3：效果对比
        对比普通检索和父文档检索的回答质量。

    思考题：
        1. 子块应该多小？父块应该多大？
        2. 重叠率如何设置？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 父文档检索")
    print("=" * 60)

    try:
        parent_document_concept()
        manual_implementation()
        langchain_parent_retriever()
        multi_level_hierarchy()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：04-query-expansion.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
