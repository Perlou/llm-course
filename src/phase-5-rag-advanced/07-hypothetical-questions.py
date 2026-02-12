"""
假设问题嵌入 (HyDE)
=================

学习目标：
    1. 理解 HyDE 技术原理
    2. 掌握假设文档生成
    3. 学会 HyDE 与其他技术结合

核心概念：
    - HyDE：Hypothetical Document Embeddings
    - 用假设答案而非问题去检索
    - 弥合问题-文档的语义鸿沟

前置知识：
    - 06-self-query-retrieval.py

环境要求：
    - pip install langchain langchain-google-genai chromadb python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：HyDE 概念 ====================


def hyde_concept():
    """HyDE 概念"""
    print("=" * 60)
    print("第一部分：HyDE 概念")
    print("=" * 60)

    print("""
    问题与文档的语义鸿沟：
    ─────────────────────
    
    问题：「什么是梯度下降？」
    文档：「梯度下降是一种优化算法，通过迭代更新参数...」
    
    问题是疑问句，文档是陈述句
    两者语义表示可能差异较大
    
    HyDE 解决方案：
    ───────────────
    
    1. 让 LLM 生成一个「假设性答案」
    2. 用这个假设答案的嵌入去检索
    3. 假设答案与真实文档语义更接近！
    
    ┌─────────────────────────────────────────────────────┐
    │                                                     │
    │   问题: 什么是梯度下降？                             │
    │               │                                     │
    │               ▼                                     │
    │      ┌───────────────────┐                         │
    │      │   LLM 生成假设答案  │                         │
    │      └───────────────────┘                         │
    │               │                                     │
    │               ▼                                     │
    │   假设答案: 梯度下降是一种常用的                      │
    │   优化算法，用于最小化损失函数...                    │
    │               │                                     │
    │               ▼                                     │
    │      ┌───────────────────┐                         │
    │      │  Embedding Model  │                         │
    │      └───────────────────┘                         │
    │               │                                     │
    │               ▼                                     │
    │      [用假设答案向量检索]                            │
    │               │                                     │
    │               ▼                                     │
    │        更好的检索结果！                              │
    │                                                     │
    └─────────────────────────────────────────────────────┘
    """)


# ==================== 第二部分：HyDE 实现 ====================


def hyde_implementation():
    """HyDE 实现"""
    print("\n" + "=" * 60)
    print("第二部分：HyDE 实现")
    print("=" * 60)

    try:
        from langchain_google_genai import (
            ChatGoogleGenerativeAI,
            GoogleGenerativeAIEmbeddings,
        )
        from langchain_chroma import Chroma
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.documents import Document

        # 准备文档
        docs = [
            Document(
                page_content="梯度下降是一种迭代优化算法，通过计算损失函数的梯度来更新模型参数，逐步找到函数的最小值。"
            ),
            Document(
                page_content="反向传播算法用于计算神经网络中每层参数的梯度，是训练深度学习模型的核心技术。"
            ),
            Document(
                page_content="学习率是梯度下降中的超参数，控制每次参数更新的步长大小。"
            ),
        ]

        # 创建向量存储
        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
        vectorstore = Chroma.from_documents(docs, embeddings)

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

        # 传统检索
        query = "什么是梯度下降"
        print(f"📌 查询: '{query}'")

        traditional_results = vectorstore.similarity_search(query, k=2)
        print("\n【传统检索结果】")
        for doc in traditional_results:
            print(f"  - {doc.page_content[:50]}...")

        # HyDE 检索
        hyde_prompt = ChatPromptTemplate.from_template("""
请写一段可能出现在技术文档中的内容来回答这个问题。
不需要完全准确，但要包含相关术语和概念。

问题: {question}

文档内容:""")

        response = llm.invoke(hyde_prompt.format_messages(question=query))
        hypothetical_doc = response.content

        print(f"\n【假设文档】\n  {hypothetical_doc[:100]}...")

        # 用假设文档检索
        hyde_results = vectorstore.similarity_search(hypothetical_doc, k=2)
        print("\n【HyDE 检索结果】")
        for doc in hyde_results:
            print(f"  - {doc.page_content[:50]}...")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第三部分：LangChain HypotheticalDocumentEmbedder ====================


def langchain_hyde():
    """LangChain HypotheticalDocumentEmbedder"""
    print("\n" + "=" * 60)
    print("第三部分：LangChain HypotheticalDocumentEmbedder")
    print("=" * 60)

    try:
        from langchain.chains import HypotheticalDocumentEmbedder
        from langchain_google_genai import (
            ChatGoogleGenerativeAI,
            GoogleGenerativeAIEmbeddings,
        )
        from langchain_core.prompts import ChatPromptTemplate

        # 创建 HyDE embedder
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        base_embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

        prompt = ChatPromptTemplate.from_template("""
请根据以下问题，写一段可能出现在相关文档中的回答。

问题: {question}

文档内容:""")

        hyde_embeddings = HypotheticalDocumentEmbedder.from_llm(
            llm=llm, base_embeddings=base_embeddings, prompt_key="question"
        )

        # 获取嵌入
        query = "Python 的 GIL 是什么"
        embedding = hyde_embeddings.embed_query(query)

        print(f"📌 查询: '{query}'")
        print(f"\nHyDE 嵌入维度: {len(embedding)}")
        print("现在可以用这个嵌入进行向量检索")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：HyDE 变体 ====================


def hyde_variants():
    """HyDE 变体"""
    print("\n" + "=" * 60)
    print("第四部分：HyDE 变体")
    print("=" * 60)

    print("""
    HyDE 的变体和扩展：
    ──────────────────
    
    1. 多假设 HyDE
       - 生成多个假设文档
       - 取平均嵌入或分别检索后融合
    
    2. 领域特定 HyDE
       - 针对特定领域定制提示
       - 使用领域术语和风格
    
    3. 分步 HyDE
       - 先分解问题
       - 对每个子问题生成假设
    """)

    code_example = '''
class MultiHyDE:
    """多假设 HyDE"""
    
    def __init__(self, llm, embeddings, n_hypotheses=3):
        self.llm = llm
        self.embeddings = embeddings
        self.n = n_hypotheses
    
    def get_embedding(self, query: str):
        # 生成多个假设文档
        hypotheses = self._generate_hypotheses(query)
        
        # 获取每个假设的嵌入
        all_embeddings = [
            self.embeddings.embed_query(h)(h)
            for h in hypotheses
        ]
        
        # 平均嵌入
        import numpy as np
        avg_embedding = np.mean(all_embeddings, axis=0)
        
        return avg_embedding.tolist()
    
    def _generate_hypotheses(self, query: str):
        prompt = f"""
生成 {self.n} 个不同角度的假设性文档来回答：{query}
每个段落换行分隔。
"""
        response = self.llm.predict(prompt)
        return response.strip().split("\\n\\n")
'''
    print("📌 多假设 HyDE 示例：")
    print(code_example)


# ==================== 第五部分：HyDE 最佳实践 ====================


def hyde_best_practices():
    """HyDE 最佳实践"""
    print("\n" + "=" * 60)
    print("第五部分：HyDE 最佳实践")
    print("=" * 60)

    print("""
    ✅ 适用场景：
    ─────────────
    - 问题与文档表述差异大
    - 技术问答
    - 概念解释类查询
    
    ❌ 不适用场景：
    ───────────────
    - 关键词检索（人名、编号等）
    - 实时性要求高
    - 成本敏感场景
    
    优化技巧：
    ──────────
    1. 使用更小的 LLM 生成假设
    2. 缓存常见问题的假设文档
    3. 结合传统检索做双路召回
    4. 针对领域定制提示模板
    """)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：对比实验
        对比 HyDE 和传统检索的效果差异。

        ✅ 参考答案：
        ```python
        from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
        from langchain_chroma import Chroma
        import time

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

        def traditional_retrieval(query: str):
            return vectorstore.similarity_search(query, k=3)

        def hyde_retrieval(query: str):
            # 生成假设文档
            prompt = f"请回答以下问题（详细完整）：{query}"
            hypothetical_doc = llm.invoke(prompt).content
            
            # 用假设文档检索
            return vectorstore.similarity_search(hypothetical_doc, k=3)

        # 对比测试
        test_queries = ["什么是机器学习？", "如何优化 Python 性能？"]
        for query in test_queries:
            print(f"\\n查询: {query}")
            
            start = time.time()
            trad_results = traditional_retrieval(query)
            trad_time = time.time() - start
            
            start = time.time()
            hyde_results = hyde_retrieval(query)
            hyde_time = time.time() - start
            
            print(f"传统检索 ({trad_time:.2f}s): {[d.page_content[:30] for d in trad_results]}")
            print(f"HyDE ({hyde_time:.2f}s): {[d.page_content[:30] for d in hyde_results]}")
        ```

    练习 2：领域定制
        为特定领域（如法律、医疗）定制 HyDE 提示。

        ✅ 参考答案：
        ```python
        HYDE_PROMPTS = {
            "medical": '''
            作为专业医生，请详细回答以下医学问题。
            包括：病因、症状、诊断方法、治疗方案。
            问题：{query}
            ''',
            "legal": '''
            作为资深律师，请回答以下法律问题。
            包括：相关法条、判例、实务建议。
            问题：{query}
            ''',
            "tech": '''
            作为技术专家，请详细解答以下技术问题。
            包括：概念解释、实现方法、代码示例、最佳实践。
            问题：{query}
            ''',
        }

        def domain_hyde(query: str, domain: str = "tech"):
            prompt = HYDE_PROMPTS.get(domain, HYDE_PROMPTS["tech"])
            hypothetical = llm.invoke(prompt.format(query=query)).content
            return vectorstore.similarity_search(hypothetical, k=3)
        ```

    练习 3：成本优化
        实现假设文档缓存机制。

        ✅ 参考答案：
        ```python
        import hashlib
        from functools import lru_cache

        class HyDECache:
            def __init__(self, max_size: int = 100):
                self.cache = {}
                self.max_size = max_size

            def _hash_query(self, query: str) -> str:
                return hashlib.md5(query.encode()).hexdigest()

            def get_hypothetical(self, query: str, llm):
                key = self._hash_query(query)
                
                if key in self.cache:
                    return self.cache[key]
                
                # 生成新的假设文档
                hypothetical = llm.invoke(f"回答：{query}").content
                
                # 缓存（LRU 策略）
                if len(self.cache) >= self.max_size:
                    oldest = next(iter(self.cache))
                    del self.cache[oldest]
                
                self.cache[key] = hypothetical
                return hypothetical

        # 或使用 LRU 装饰器
        @lru_cache(maxsize=100)
        def cached_hyde(query: str) -> str:
            return llm.invoke(f"回答：{query}").content
        ```

    思考题：
        1. HyDE 会增加多少延迟？
           
           ✅ 答案：
           - LLM 调用：~500ms-2s（取决于模型和输出长度）
           - 额外的 Embedding 计算：~100ms
           - 总延迟增加：约 1-3 倍
           - 优化：缓存、异步预生成、使用更快的模型

        2. 假设文档错误会导致什么问题？
           
           ✅ 答案：
           - 检索偏移：错误信息导向错误的文档
           - 幻觉传播：LLM 幻觉影响检索质量
           - 上下文污染：最终回答可能被误导
           - 解决方案：用传统检索作为兜底、结果验证
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 假设问题嵌入 (HyDE)")
    print("=" * 60)

    try:
        hyde_concept()
        hyde_implementation()
        langchain_hyde()
        hyde_variants()
        hyde_best_practices()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：08-contextual-compression.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
