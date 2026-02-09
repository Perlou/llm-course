"""
上下文压缩
==========

学习目标：
    1. 理解上下文压缩的必要性
    2. 掌握提取式和生成式压缩
    3. 学会 LangChain 压缩组件

核心概念：
    - Context Compression：减少无关内容
    - 提取式：选择相关句子
    - 生成式：LLM 重写压缩

前置知识：
    - 07-hypothetical-questions.py

环境要求：
    - pip install langchain langchain-google-genai chromadb python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：上下文压缩概念 ====================


def compression_concept():
    """上下文压缩概念"""
    print("=" * 60)
    print("第一部分：上下文压缩概念")
    print("=" * 60)

    print("""
    为什么需要上下文压缩？
    ─────────────────────
    
    问题 1：检索到的文档包含无关内容
    问题 2：上下文太长，超出 token 限制
    问题 3：无关内容影响生成质量
    
    解决方案：上下文压缩
    ───────────────────
    
    ┌─────────────────────────────────────────────────────┐
    │                 原始检索结果                         │
    │  ┌─────────────────────────────────────────────┐   │
    │  │  这是一段很长的文档，包含了很多内容。        │   │
    │  │  其中有些是相关的，比如 Python 是一种         │   │
    │  │  编程语言。但也有很多无关的说明...           │   │
    │  └─────────────────────────────────────────────┘   │
    │                        │                           │
    │                        ▼                           │
    │              ┌───────────────────┐                │
    │              │   上下文压缩器     │                │
    │              └───────────────────┘                │
    │                        │                           │
    │                        ▼                           │
    │  ┌─────────────────────────────────────────────┐   │
    │  │ Python 是一种编程语言。                      │   │
    │  └─────────────────────────────────────────────┘   │
    │                 压缩后的上下文                      │
    └─────────────────────────────────────────────────────┘
    """)


# ==================== 第二部分：提取式压缩 ====================


def extractive_compression():
    """提取式压缩"""
    print("\n" + "=" * 60)
    print("第二部分：提取式压缩")
    print("=" * 60)

    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        import numpy as np

        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

        # 示例文档
        document = """
Python 是一种高级编程语言。它由 Guido van Rossum 创建。
今天天气很好。Python 支持多种编程范式。
咖啡是一种饮料。Python 有丰富的库生态系统。
"""

        query = "Python 的特点"

        # 分割成句子
        sentences = [s.strip() for s in document.split("。") if s.strip()]

        # 计算相似度
        query_emb = embeddings.embed_query(query)
        sent_embs = embeddings.embed_documents(sentences)

        def cosine_sim(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        similarities = [cosine_sim(query_emb, s) for s in sent_embs]

        # 选择相关句子
        threshold = 0.8
        relevant = [
            (s, sim) for s, sim in zip(sentences, similarities) if sim > threshold
        ]

        print(f"📌 查询: '{query}'")
        print(f"\n提取的相关句子（阈值={threshold}）：")
        for sent, sim in sorted(relevant, key=lambda x: -x[1]):
            print(f"  [{sim:.3f}] {sent}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第三部分：LangChain ContextualCompressionRetriever ====================


def langchain_compression():
    """LangChain 上下文压缩检索器"""
    print("\n" + "=" * 60)
    print("第三部分：LangChain ContextualCompressionRetriever")
    print("=" * 60)

    try:
        from langchain.retrievers import ContextualCompressionRetriever
        from langchain.retrievers.document_compressors import LLMChainExtractor
        from langchain_google_genai import (
            ChatGoogleGenerativeAI,
            GoogleGenerativeAIEmbeddings,
        )
        from langchain_chroma import Chroma
        from langchain_core.documents import Document

        # 准备文档
        docs = [
            Document(
                page_content="""
Python 是一种解释型编程语言。它以简洁的语法著称。
最近我去了一趟超市，买了很多水果。
Python 支持面向对象、函数式等多种编程范式。
今天的天气预报说会下雨。
Python 的标准库非常丰富，涵盖网络、文件处理等功能。
"""
            ),
        ]

        # 创建基础检索器
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vectorstore = Chroma.from_documents(docs, embeddings)
        base_retriever = vectorstore.as_retriever()

        # 创建压缩器
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        compressor = LLMChainExtractor.from_llm(llm)

        # 创建压缩检索器
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=base_retriever
        )

        # 检索
        query = "Python 有什么特点"
        results = compression_retriever.invoke(query)

        print(f"📌 查询: '{query}'")
        print("\n压缩后的结果：")
        for doc in results:
            print(f"  {doc.page_content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：生成式压缩 ====================


def generative_compression():
    """生成式压缩"""
    print("\n" + "=" * 60)
    print("第四部分：生成式压缩")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

        document = """
Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年创建。
它的设计强调代码可读性和简洁的语法。Python 支持多种编程范式，
包括面向对象、命令式、函数式和过程式编程。Python 的解释器
可以在多个平台上运行。Python 有一个全面的标准库，提供了
许多模块和工具。此外，Python 拥有活跃的社区和丰富的第三方库。
"""

        query = "Python 的核心特点"

        prompt = ChatPromptTemplate.from_template("""
请根据查询，压缩以下文档，只保留回答查询所必需的关键信息。
压缩后不超过 100 字。

查询: {query}
文档: {document}

压缩后的内容:""")

        chain = prompt | llm
        result = chain.invoke({"query": query, "document": document})

        print(f"📌 查询: '{query}'")
        print(f"\n原文长度: {len(document)} 字符")
        print(f"\n压缩后的内容：")
        print(f"  {result.content}")
        print(f"\n压缩后长度: {len(result.content)} 字符")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第五部分：过滤式压缩 ====================


def filter_compression():
    """过滤式压缩"""
    print("\n" + "=" * 60)
    print("第五部分：过滤式压缩")
    print("=" * 60)

    try:
        from langchain.retrievers.document_compressors import EmbeddingsFilter
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_core.documents import Document

        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

        # 创建相关性过滤器
        embeddings_filter = EmbeddingsFilter(
            embeddings=embeddings, similarity_threshold=0.75
        )

        # 模拟检索结果
        docs = [
            Document(page_content="Python 是一种编程语言"),
            Document(page_content="今天天气很好"),
            Document(page_content="Python 支持多种编程范式"),
        ]

        query = "Python 的特点"
        filtered = embeddings_filter.compress_documents(docs, query)

        print(f"📌 查询: '{query}'")
        print(f"\n过滤前: {len(docs)} 个文档")
        print(f"过滤后: {len(filtered)} 个文档")
        print("\n保留的文档：")
        for doc in filtered:
            print(f"  - {doc.page_content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第六部分：压缩管道 ====================


def compression_pipeline():
    """压缩管道"""
    print("\n" + "=" * 60)
    print("第六部分：压缩管道")
    print("=" * 60)

    code_example = """
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain.text_splitter import CharacterTextSplitter

# 创建压缩管道
splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0)
embeddings_filter = EmbeddingsFilter(embeddings=embeddings, similarity_threshold=0.76)
llm_extractor = LLMChainExtractor.from_llm(llm)

# 组合多个压缩器
pipeline = DocumentCompressorPipeline(
    transformers=[
        splitter,           # 1. 先分割
        embeddings_filter,  # 2. 过滤不相关
        llm_extractor,      # 3. 提取关键信息
    ]
)

# 使用管道
compression_retriever = ContextualCompressionRetriever(
    base_compressor=pipeline,
    base_retriever=base_retriever
)
"""
    print("📌 压缩管道示例：")
    print(code_example)


# ==================== 第七部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：对比实验
        对比压缩前后 RAG 的回答质量。

        ✅ 参考答案：
        ```python
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain.retrievers import ContextualCompressionRetriever
        from langchain.retrievers.document_compressors import LLMChainExtractor

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

        def compare_compression(query: str):
            # 无压缩检索
            raw_docs = base_retriever.invoke(query)
            raw_context = "\\n".join(d.page_content for d in raw_docs)
            
            # 压缩检索
            compressor = LLMChainExtractor.from_llm(llm)
            compression_retriever = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=base_retriever
            )
            compressed_docs = compression_retriever.invoke(query)
            compressed_context = "\\n".join(d.page_content for d in compressed_docs)
            
            print(f"原始上下文长度: {len(raw_context)} 字符")
            print(f"压缩后长度: {len(compressed_context)} 字符")
            print(f"压缩率: {len(compressed_context)/len(raw_context):.2%}")
            
            # 对比回答质量
            raw_answer = generate_answer(raw_context, query)
            compressed_answer = generate_answer(compressed_context, query)
            
            return {"raw": raw_answer, "compressed": compressed_answer}
        ```

    练习 2：阈值调优
        测试不同相似度阈值的过滤效果。

        ✅ 参考答案：
        ```python
        from langchain.retrievers.document_compressors import EmbeddingsFilter

        thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]
        query = "Python 性能优化"

        for threshold in thresholds:
            embeddings_filter = EmbeddingsFilter(
                embeddings=embeddings,
                similarity_threshold=threshold
            )
            
            compression_retriever = ContextualCompressionRetriever(
                base_compressor=embeddings_filter,
                base_retriever=base_retriever
            )
            
            results = compression_retriever.invoke(query)
            
            print(f"阈值={threshold}: {len(results)} 个文档被保留")
            for doc in results:
                print(f"  {doc.page_content[:50]}...")
        ```

    练习 3：自定义压缩器
        实现一个基于关键词的压缩器。

        ✅ 参考答案：
        ```python
        from langchain.retrievers.document_compressors import BaseDocumentCompressor
        from langchain_core.documents import Document
        import re

        class KeywordCompressor(BaseDocumentCompressor):
            def __init__(self, top_sentences: int = 3):
                self.top_sentences = top_sentences

            def compress_documents(self, documents, query, callbacks=None):
                # 提取查询关键词
                keywords = set(query.lower().split())
                
                compressed = []
                for doc in documents:
                    sentences = re.split(r'[。！？.!?]', doc.page_content)
                    
                    # 对每个句子打分
                    scored = []
                    for sent in sentences:
                        if sent.strip():
                            score = sum(1 for kw in keywords if kw in sent.lower())
                            scored.append((score, sent))
                    
                    # 取得分最高的句子
                    scored.sort(reverse=True)
                    top_sents = [s for _, s in scored[:self.top_sentences]]
                    
                    if top_sents:
                        compressed.append(Document(
                            page_content="。".join(top_sents),
                            metadata=doc.metadata
                        ))
                
                return compressed
        ```

    思考题：
        1. 压缩可能丢失哪些重要信息？
           
           ✅ 答案：
           - 上下文关联：前后文关系可能丢失
           - 隐式信息：需要推理才能得出的信息
           - 背景知识：理解答案所需的前置信息
           - 例子和细节：具体案例可能被过滤

        2. 如何平衡压缩率和信息保留？
           
           ✅ 答案：
           - 动态阈值：根据文档相似度调整压缩程度
           - 分层压缩：先粗过滤，再精提取
           - 保留元数据：即使压缩内容，保留来源信息
           - A/B 测试：找到最佳压缩率
           - 用户反馈：根据回答质量调整参数
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 上下文压缩")
    print("=" * 60)

    try:
        compression_concept()
        extractive_compression()
        langchain_compression()
        generative_compression()
        filter_compression()
        compression_pipeline()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：09-ensemble-retrieval.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
