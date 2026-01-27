# 高级RAG技术深度解析：从入门到精通

## 📚 目录

1. [RAG基础回顾](#1-rag基础回顾)
2. [高级分块策略](#2-高级分块策略)
3. [查询理解与优化](#3-查询理解与优化)
4. [高级检索技术](#4-高级检索技术)
5. [重排序技术](#5-重排序技术)
6. [上下文压缩与优化](#6-上下文压缩与优化)
7. [多跳推理RAG](#7-多跳推理rag)
8. [知识图谱增强RAG](#8-知识图谱增强rag)
9. [自适应RAG](#9-自适应rag)
10. [RAG评估体系](#10-rag评估体系)
11. [生产环境最佳实践](#11-生产环境最佳实践)

---

## 1. RAG基础回顾

### 1.1 什么是RAG？

**RAG（Retrieval-Augmented Generation）** 是一种将信息检索与大语言模型生成能力结合的技术架构。

```
┌─────────────────────────────────────────────────────────────────┐
│                      RAG 基础架构                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐    ┌──────────────┐    ┌─────────────────────┐  │
│   │  用户查询  │───▶│   检索器      │───▶│   向量数据库         │  │
│   └──────────┘    └──────────────┘    └─────────────────────┘  │
│         │                │                       │              │
│         │                ▼                       │              │
│         │         相关文档块                       │              │
│         │                │                       │              │
│         ▼                ▼                       │              │
│   ┌──────────────────────────────┐               │              │
│   │          提示词构建            │               │              │
│   │   Query + Retrieved Context  │               │              │
│   └──────────────────────────────┘               │              │
│                    │                             │              │
│                    ▼                             │              │
│   ┌──────────────────────────────┐               │              │
│   │           LLM 生成            │               │              │
│   └──────────────────────────────┘               │              │
│                    │                             │              │
│                    ▼                             │              │
│   ┌──────────────────────────────┐               │              │
│   │          最终回答             │               │              │
│   └──────────────────────────────┘               │              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Naive RAG vs Advanced RAG

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    RAG 演进路线图                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐             │
│  │  Naive RAG  │─────▶│ Advanced RAG│─────▶│ Modular RAG │             │
│  └─────────────┘      └─────────────┘      └─────────────┘             │
│        │                    │                    │                      │
│        ▼                    ▼                    ▼                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │ • 简单分块    │    │ • 查询优化    │    │ • 可插拔模块  │              │
│  │ • 直接检索    │    │ • 混合检索    │    │ • 自适应路由  │              │
│  │ • 无重排序    │    │ • 重排序      │    │ • 多策略融合  │              │
│  │ • 基础生成    │    │ • 上下文压缩  │    │ • 知识图谱    │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.3 基础实现

```python
# 基础 RAG 实现
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

class NaiveRAG:
    """基础RAG实现"""

    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.vectorstore = None

    def index_documents(self, documents: list[str], chunk_size: int = 500):
        """索引文档"""
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        # 简单分块
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=50
        )
        chunks = splitter.create_documents(documents)

        # 创建向量存储
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)

    def query(self, question: str, k: int = 4) -> str:
        """查询"""
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": k})
        )
        return qa_chain.run(question)
```

---

## 2. 高级分块策略

### 2.1 分块策略对比

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      分块策略全景图                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │   固定大小分块    │  │   语义分块       │  │   结构化分块     │         │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤         │
│  │ • 按字符数切分   │  │ • 基于嵌入相似度 │  │ • 按文档结构    │         │
│  │ • 简单高效      │  │ • 语义边界清晰   │  │ • 保留层次关系  │         │
│  │ • 可能切断句子  │  │ • 计算成本较高   │  │ • 需要解析器    │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │   递归分块       │  │   父子分块       │  │   滑动窗口分块   │         │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤         │
│  │ • 多级分隔符    │  │ • 小块检索      │  │ • 重叠保留上下文│         │
│  │ • 尊重文档结构  │  │ • 大块返回      │  │ • 信息冗余      │         │
│  │ • 最常用方案    │  │ • 兼顾精确和上下文│ │ • 实现简单      │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 语义分块实现

````python
import numpy as np
from sentence_transformers import SentenceTransformer

class SemanticChunker:
    """基于语义的智能分块器"""

    def __init__(self,
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 breakpoint_threshold: float = 0.5):
        self.model = SentenceTransformer(model_name)
        self.breakpoint_threshold = breakpoint_threshold

    def chunk(self, text: str) -> list[str]:
        """
        基于语义相似度的分块
        在语义断点处切分文档
        """
        # 1. 按句子分割
        sentences = self._split_sentences(text)
        if len(sentences) <= 1:
            return [text]

        # 2. 计算每个句子的嵌入
        embeddings = self.model.encode(sentences)

        # 3. 计算相邻句子的余弦相似度
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = self._cosine_similarity(embeddings[i], embeddings[i+1])
            similarities.append(sim)

        # 4. 找到语义断点（相似度低于阈值的位置）
        breakpoints = self._find_breakpoints(similarities)

        # 5. 根据断点分割
        chunks = self._split_by_breakpoints(sentences, breakpoints)

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """分割句子"""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """计算余弦相似度"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def _find_breakpoints(self, similarities: list[float]) -> list[int]:
        """找到语义断点"""
        breakpoints = []

        # 方法1: 固定阈值
        for i, sim in enumerate(similarities):
            if sim < self.breakpoint_threshold:
                breakpoints.append(i + 1)

        # 方法2: 基于百分位数（更自适应）
        # threshold = np.percentile(similarities, 25)
        # breakpoints = [i+1 for i, sim in enumerate(similarities) if sim < threshold]

        return breakpoints

    def _split_by_breakpoints(self, sentences: list[str],
                               breakpoints: list[int]) -> list[str]:
        """根据断点分割文本"""
        chunks = []
        start = 0

        for bp in breakpoints:
            chunk = ' '.join(sentences[start:bp])
            if chunk:
                chunks.append(chunk)
            start = bp

        # 最后一个块
        if start < len(sentences):
            chunks.append(' '.join(sentences[start:]))

        return chunks


class AdaptiveChunker:
    """自适应分块器 - 根据内容类型选择策略"""

    def __init__(self):
        self.semantic_chunker = SemanticChunker()

    def chunk(self, text: str, content_type: str = "auto") -> list[str]:
        """根据内容类型选择分块策略"""

        if content_type == "auto":
            content_type = self._detect_content_type(text)

        if content_type == "code":
            return self._chunk_code(text)
        elif content_type == "markdown":
            return self._chunk_markdown(text)
        elif content_type == "table":
            return self._chunk_table(text)
        else:
            return self.semantic_chunker.chunk(text)

    def _detect_content_type(self, text: str) -> str:
        """检测内容类型"""
        # 简单的规则检测
        if "```" in text or "def " in text or "class " in text:
            return "code"
        elif text.startswith("#") or "##" in text:
            return "markdown"
        elif "|" in text and "-|-" in text:
            return "table"
        return "text"

    def _chunk_code(self, text: str) -> list[str]:
        """代码分块 - 按函数/类分割"""
        import re

        # 匹配函数和类定义
        pattern = r'((?:def|class)\s+\w+[^:]*:(?:\n(?:[ \t]+[^\n]*|\n))*)'
        matches = re.findall(pattern, text)

        if matches:
            return matches
        return [text]

    def _chunk_markdown(self, text: str) -> list[str]:
        """Markdown分块 - 按标题分割"""
        import re

        # 按一级和二级标题分割
        sections = re.split(r'\n(?=#{1,2}\s)', text)
        return [s.strip() for s in sections if s.strip()]

    def _chunk_table(self, text: str) -> list[str]:
        """表格分块 - 保持表格完整"""
        # 表格通常应该保持完整
        return [text]
````

### 2.3 父子分块（Parent-Child Chunking）

```python
from dataclasses import dataclass
from typing import Optional
import uuid

@dataclass
class ChunkNode:
    """分块节点"""
    id: str
    content: str
    parent_id: Optional[str]
    children_ids: list[str]
    level: int  # 0 = root, 1 = parent, 2 = child

class HierarchicalChunker:
    """
    层次化分块器
    实现小块检索、大块返回的策略
    """

    def __init__(self,
                 parent_chunk_size: int = 2000,
                 child_chunk_size: int = 400,
                 child_overlap: int = 50):
        self.parent_chunk_size = parent_chunk_size
        self.child_chunk_size = child_chunk_size
        self.child_overlap = child_overlap
        self.nodes: dict[str, ChunkNode] = {}

    def chunk(self, document: str) -> tuple[list[ChunkNode], list[ChunkNode]]:
        """
        创建层次化分块
        返回: (父块列表, 子块列表)
        """
        parent_chunks = []
        child_chunks = []

        # 1. 创建父块
        parent_texts = self._create_chunks(
            document,
            self.parent_chunk_size,
            overlap=100
        )

        for parent_text in parent_texts:
            parent_id = str(uuid.uuid4())

            # 2. 为每个父块创建子块
            child_texts = self._create_chunks(
                parent_text,
                self.child_chunk_size,
                self.child_overlap
            )

            children_ids = []
            for child_text in child_texts:
                child_id = str(uuid.uuid4())
                child_node = ChunkNode(
                    id=child_id,
                    content=child_text,
                    parent_id=parent_id,
                    children_ids=[],
                    level=2
                )
                self.nodes[child_id] = child_node
                child_chunks.append(child_node)
                children_ids.append(child_id)

            parent_node = ChunkNode(
                id=parent_id,
                content=parent_text,
                parent_id=None,
                children_ids=children_ids,
                level=1
            )
            self.nodes[parent_id] = parent_node
            parent_chunks.append(parent_node)

        return parent_chunks, child_chunks

    def _create_chunks(self, text: str, chunk_size: int,
                       overlap: int = 0) -> list[str]:
        """创建固定大小的分块"""
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # 尝试在句子边界处切分
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > chunk_size * 0.5:
                    chunk = chunk[:last_period + 1]
                    end = start + last_period + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return chunks

    def get_parent(self, child_id: str) -> Optional[ChunkNode]:
        """获取子块的父块"""
        child = self.nodes.get(child_id)
        if child and child.parent_id:
            return self.nodes.get(child.parent_id)
        return None


class ParentChildRetriever:
    """父子检索器 - 小块检索，大块返回"""

    def __init__(self, chunker: HierarchicalChunker, vectorstore):
        self.chunker = chunker
        self.vectorstore = vectorstore

    def retrieve(self, query: str, k: int = 4) -> list[str]:
        """
        1. 用子块进行检索（更精确）
        2. 返回对应的父块（更完整的上下文）
        """
        # 检索子块
        child_results = self.vectorstore.similarity_search(query, k=k)

        # 获取对应的父块，去重
        parent_contents = []
        seen_parent_ids = set()

        for result in child_results:
            child_id = result.metadata.get("chunk_id")
            parent = self.chunker.get_parent(child_id)

            if parent and parent.id not in seen_parent_ids:
                parent_contents.append(parent.content)
                seen_parent_ids.add(parent.id)

        return parent_contents
```

---

## 3. 查询理解与优化

### 3.1 查询优化策略概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       查询优化策略                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                        ┌──────────────┐                                 │
│                        │   原始查询    │                                 │
│                        └──────┬───────┘                                 │
│                               │                                         │
│              ┌────────────────┼────────────────┐                        │
│              │                │                │                        │
│              ▼                ▼                ▼                        │
│     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                 │
│     │   查询重写    │ │   查询扩展    │ │   查询分解    │                 │
│     ├──────────────┤ ├──────────────┤ ├──────────────┤                 │
│     │ HyDE         │ │ 同义词扩展   │ │ 子问题分解   │                 │
│     │ Step-back    │ │ LLM扩展     │ │ 多跳问题     │                 │
│     │ 意图明确化    │ │ 多语言扩展   │ │ 树状分解     │                 │
│     └──────────────┘ └──────────────┘ └──────────────┘                 │
│              │                │                │                        │
│              └────────────────┼────────────────┘                        │
│                               ▼                                         │
│                      ┌──────────────┐                                  │
│                      │  优化后查询   │                                  │
│                      └──────────────┘                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 HyDE（Hypothetical Document Embedding）

```python
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings

class HyDEQueryTransformer:
    """
    HyDE: 假设性文档嵌入

    原理: 先让LLM生成一个假设性答案，
    用这个答案（而非原始问题）去检索
    """

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        self.embeddings = OpenAIEmbeddings()

    def transform(self, query: str) -> str:
        """生成假设性文档"""

        prompt = f"""请针对以下问题，写一段可能出现在相关文档中的回答。
不需要完全准确，但要包含可能的关键信息和术语。

问题: {query}

假设性文档内容:"""

        response = self.llm.predict(prompt)
        return response

    def get_embedding(self, query: str) -> list[float]:
        """获取HyDE嵌入"""
        # 生成假设性文档
        hypothetical_doc = self.transform(query)

        # 使用假设性文档的嵌入
        return self.embeddings.embed_query(hypothetical_doc)

    def retrieve_with_hyde(self, query: str, vectorstore, k: int = 4):
        """使用HyDE进行检索"""
        hyde_embedding = self.get_embedding(query)

        # 使用假设性文档嵌入进行检索
        results = vectorstore.similarity_search_by_vector(
            hyde_embedding,
            k=k
        )
        return results
```

### 3.3 Multi-Query（多查询策略）

```python
class MultiQueryRetriever:
    """
    多查询检索器

    从多个角度生成查询，合并检索结果
    提高召回率
    """

    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    def generate_queries(self, original_query: str, n: int = 3) -> list[str]:
        """生成多个查询变体"""

        prompt = f"""你是一个查询优化专家。给定一个用户问题，请生成{n}个不同角度的相关查询。
这些查询应该帮助检索到更全面的相关信息。

原始问题: {original_query}

请生成{n}个查询，每行一个:"""

        response = self.llm.predict(prompt)
        queries = [q.strip() for q in response.strip().split('\n') if q.strip()]

        # 包含原始查询
        return [original_query] + queries[:n]

    def retrieve(self, query: str, k: int = 4) -> list:
        """多查询检索"""
        # 1. 生成多个查询
        queries = self.generate_queries(query)

        # 2. 对每个查询进行检索
        all_results = []
        seen_contents = set()

        for q in queries:
            results = self.vectorstore.similarity_search(q, k=k)
            for doc in results:
                # 去重
                if doc.page_content not in seen_contents:
                    all_results.append(doc)
                    seen_contents.add(doc.page_content)

        return all_results


class QueryDecomposer:
    """
    查询分解器

    将复杂问题分解为简单子问题
    分别检索后合并
    """

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)

    def decompose(self, complex_query: str) -> list[str]:
        """分解复杂查询"""

        prompt = f"""请将以下复杂问题分解为更简单的子问题。
每个子问题应该独立可回答，且回答所有子问题能帮助回答原始问题。

原始问题: {complex_query}

子问题列表（每行一个）:"""

        response = self.llm.predict(prompt)
        sub_queries = [q.strip().lstrip('0123456789.-) ')
                       for q in response.strip().split('\n')
                       if q.strip()]

        return sub_queries

    def retrieve_and_merge(self, query: str, vectorstore, k: int = 2):
        """分解检索并合并"""
        sub_queries = self.decompose(query)

        all_results = []
        query_results = {}

        for sub_q in sub_queries:
            results = vectorstore.similarity_search(sub_q, k=k)
            query_results[sub_q] = results
            all_results.extend(results)

        return query_results, all_results
```

### 3.4 Step-Back Prompting

```python
class StepBackRetriever:
    """
    Step-Back Prompting

    对于具体问题，先退一步问更抽象的问题
    获取更多背景知识
    """

    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)

    def generate_stepback_query(self, query: str) -> str:
        """生成step-back查询"""

        prompt = f"""你是一个问题抽象专家。给定一个具体问题，
请生成一个更抽象、更基础的问题，这个问题的答案能提供回答原始问题所需的背景知识。

原始问题: {query}

抽象问题:"""

        return self.llm.predict(prompt).strip()

    def retrieve(self, query: str, k: int = 4):
        """Step-back检索"""
        # 1. 生成抽象问题
        stepback_query = self.generate_stepback_query(query)

        # 2. 检索原始问题相关文档
        original_results = self.vectorstore.similarity_search(query, k=k)

        # 3. 检索抽象问题相关文档（背景知识）
        stepback_results = self.vectorstore.similarity_search(stepback_query, k=k//2)

        # 4. 合并结果，背景知识放前面
        return {
            'background': stepback_results,
            'specific': original_results,
            'stepback_query': stepback_query
        }
```

---

## 4. 高级检索技术

### 4.1 混合检索（Hybrid Search）

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        混合检索架构                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                         ┌──────────────┐                               │
│                         │    Query     │                               │
│                         └──────┬───────┘                               │
│                                │                                        │
│                 ┌──────────────┴──────────────┐                        │
│                 │                             │                         │
│                 ▼                             ▼                         │
│        ┌──────────────┐              ┌──────────────┐                  │
│        │  稀疏检索     │              │   稠密检索    │                  │
│        │  (BM25)      │              │  (Embedding) │                  │
│        └──────┬───────┘              └──────┬───────┘                  │
│               │                             │                          │
│               │  关键词匹配                   │  语义相似                │
│               │  精确匹配强                   │  模糊匹配强              │
│               │                             │                          │
│               └──────────────┬──────────────┘                          │
│                              │                                         │
│                              ▼                                         │
│                     ┌──────────────┐                                   │
│                     │   分数融合    │                                   │
│                     │  (RRF/加权)  │                                   │
│                     └──────┬───────┘                                   │
│                            │                                           │
│                            ▼                                           │
│                     ┌──────────────┐                                   │
│                     │   最终结果    │                                   │
│                     └──────────────┘                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

```python
from rank_bm25 import BM25Okapi
import numpy as np
from typing import List, Tuple

class HybridRetriever:
    """
    混合检索器
    结合BM25（稀疏）和向量（稠密）检索
    """

    def __init__(self,
                 documents: list[str],
                 embeddings_model,
                 vectorstore,
                 alpha: float = 0.5):
        """
        alpha: 稠密检索的权重 (0-1)
               0 = 纯BM25, 1 = 纯向量
        """
        self.documents = documents
        self.embeddings_model = embeddings_model
        self.vectorstore = vectorstore
        self.alpha = alpha

        # 初始化BM25
        tokenized_docs = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)

    def search(self, query: str, k: int = 10) -> list[Tuple[str, float]]:
        """混合检索"""
        # 1. BM25 检索
        bm25_scores = self._bm25_search(query)

        # 2. 向量检索
        vector_scores = self._vector_search(query)

        # 3. 分数融合
        final_scores = self._fuse_scores(bm25_scores, vector_scores)

        # 4. 排序返回
        sorted_results = sorted(final_scores.items(),
                               key=lambda x: x[1],
                               reverse=True)

        return [(self.documents[idx], score)
                for idx, score in sorted_results[:k]]

    def _bm25_search(self, query: str) -> dict[int, float]:
        """BM25检索"""
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)

        # 归一化分数
        max_score = max(scores) if max(scores) > 0 else 1
        normalized = {i: score/max_score for i, score in enumerate(scores)}

        return normalized

    def _vector_search(self, query: str) -> dict[int, float]:
        """向量检索"""
        results = self.vectorstore.similarity_search_with_score(
            query,
            k=len(self.documents)
        )

        # 转换为索引->分数映射
        scores = {}
        for doc, score in results:
            idx = self.documents.index(doc.page_content)
            # 将距离转换为相似度（假设是L2距离）
            scores[idx] = 1 / (1 + score)

        return scores

    def _fuse_scores(self,
                     bm25_scores: dict[int, float],
                     vector_scores: dict[int, float]) -> dict[int, float]:
        """分数融合"""
        fused = {}
        all_indices = set(bm25_scores.keys()) | set(vector_scores.keys())

        for idx in all_indices:
            bm25 = bm25_scores.get(idx, 0)
            vector = vector_scores.get(idx, 0)

            # 加权融合
            fused[idx] = (1 - self.alpha) * bm25 + self.alpha * vector

        return fused

    def search_with_rrf(self, query: str, k: int = 10,
                        rrf_k: int = 60) -> list[Tuple[str, float]]:
        """
        使用 Reciprocal Rank Fusion (RRF) 融合
        RRF对排名更鲁棒
        """
        # 获取两个检索器的排名
        bm25_ranking = self._get_bm25_ranking(query)
        vector_ranking = self._get_vector_ranking(query)

        # RRF 公式: score = sum(1 / (k + rank))
        rrf_scores = {}

        for idx, rank in bm25_ranking.items():
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (rrf_k + rank)

        for idx, rank in vector_ranking.items():
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (rrf_k + rank)

        # 排序
        sorted_results = sorted(rrf_scores.items(),
                               key=lambda x: x[1],
                               reverse=True)

        return [(self.documents[idx], score)
                for idx, score in sorted_results[:k]]

    def _get_bm25_ranking(self, query: str) -> dict[int, int]:
        """获取BM25排名"""
        scores = self._bm25_search(query)
        sorted_indices = sorted(scores.keys(),
                               key=lambda x: scores[x],
                               reverse=True)
        return {idx: rank for rank, idx in enumerate(sorted_indices)}

    def _get_vector_ranking(self, query: str) -> dict[int, int]:
        """获取向量检索排名"""
        scores = self._vector_search(query)
        sorted_indices = sorted(scores.keys(),
                               key=lambda x: scores[x],
                               reverse=True)
        return {idx: rank for rank, idx in enumerate(sorted_indices)}
```

### 4.2 多向量检索

```python
from typing import List, Dict, Any

class MultiVectorRetriever:
    """
    多向量检索器
    为每个文档生成多个向量表示
    """

    def __init__(self, embeddings_model, llm):
        self.embeddings = embeddings_model
        self.llm = llm
        self.doc_store = {}  # doc_id -> original document
        self.vector_store = None  # 存储多个向量

    def add_documents(self, documents: list[str]):
        """
        为每个文档创建多个向量:
        1. 原文档向量
        2. 摘要向量
        3. 问题向量（假设性问题）
        """
        all_vectors = []
        all_metadata = []

        for i, doc in enumerate(documents):
            doc_id = f"doc_{i}"
            self.doc_store[doc_id] = doc

            # 1. 原文档向量
            all_vectors.append({
                'text': doc,
                'doc_id': doc_id,
                'vector_type': 'original'
            })

            # 2. 生成摘要并创建向量
            summary = self._generate_summary(doc)
            all_vectors.append({
                'text': summary,
                'doc_id': doc_id,
                'vector_type': 'summary'
            })

            # 3. 生成假设性问题
            questions = self._generate_questions(doc)
            for q in questions:
                all_vectors.append({
                    'text': q,
                    'doc_id': doc_id,
                    'vector_type': 'question'
                })

        # 创建向量存储
        self._build_vector_store(all_vectors)

    def _generate_summary(self, doc: str) -> str:
        """生成文档摘要"""
        prompt = f"请用1-2句话总结以下文本的核心内容:\n\n{doc}"
        return self.llm.predict(prompt)

    def _generate_questions(self, doc: str, n: int = 3) -> list[str]:
        """生成可以用该文档回答的问题"""
        prompt = f"""基于以下文档，生成{n}个可以用该文档回答的问题:

文档: {doc}

问题列表:"""

        response = self.llm.predict(prompt)
        questions = [q.strip().lstrip('0123456789.-) ')
                    for q in response.split('\n') if q.strip()]
        return questions[:n]

    def _build_vector_store(self, vectors: list[dict]):
        """构建向量存储"""
        # 使用LangChain或其他向量数据库
        from langchain.vectorstores import FAISS
        from langchain.schema import Document

        docs = [
            Document(
                page_content=v['text'],
                metadata={'doc_id': v['doc_id'], 'type': v['vector_type']}
            )
            for v in vectors
        ]

        self.vector_store = FAISS.from_documents(docs, self.embeddings)

    def retrieve(self, query: str, k: int = 4) -> list[str]:
        """检索原始文档"""
        # 检索相关向量
        results = self.vector_store.similarity_search(query, k=k*3)

        # 获取唯一的文档ID
        seen_doc_ids = set()
        final_docs = []

        for result in results:
            doc_id = result.metadata['doc_id']
            if doc_id not in seen_doc_ids:
                final_docs.append(self.doc_store[doc_id])
                seen_doc_ids.add(doc_id)

                if len(final_docs) >= k:
                    break

        return final_docs
```

---

## 5. 重排序技术

### 5.1 重排序架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         重排序流程                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────┐                                                     │
│   │    Query     │                                                     │
│   └──────┬───────┘                                                     │
│          │                                                             │
│          ▼                                                             │
│   ┌──────────────┐     ┌──────────────────────────────────────┐       │
│   │  初始检索     │────▶│  候选文档集合 (top-100)                │       │
│   │  (召回阶段)   │     │  D1, D2, D3, ... D100                │       │
│   └──────────────┘     └──────────────────┬───────────────────┘       │
│                                           │                            │
│                                           ▼                            │
│   ┌────────────────────────────────────────────────────────────┐      │
│   │                     重排序模型                               │      │
│   │  ┌────────────────────────────────────────────────────┐   │      │
│   │  │  Cross-Encoder: 同时编码 query 和 document         │   │      │
│   │  │  比 Bi-Encoder 更精确，但更慢                       │   │      │
│   │  └────────────────────────────────────────────────────┘   │      │
│   │                                                            │      │
│   │  输入: (query, doc) pairs                                  │      │
│   │  输出: relevance score                                     │      │
│   └────────────────────────────────┬───────────────────────────┘      │
│                                    │                                   │
│                                    ▼                                   │
│   ┌──────────────────────────────────────────────────────────┐        │
│   │  重排序后的结果 (top-k)                                     │        │
│   │  按相关性得分重新排列                                        │        │
│   └──────────────────────────────────────────────────────────┘        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Cross-Encoder 重排序

```python
from sentence_transformers import CrossEncoder
from typing import List, Tuple

class CrossEncoderReranker:
    """
    Cross-Encoder 重排序器

    与 Bi-Encoder 的区别:
    - Bi-Encoder: 分别编码query和doc，计算向量相似度
    - Cross-Encoder: 同时编码query和doc，直接预测相关性分数

    Cross-Encoder更精确，但速度更慢
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self,
               query: str,
               documents: list[str],
               top_k: int = None) -> list[Tuple[str, float]]:
        """
        重排序文档

        Args:
            query: 查询
            documents: 待排序文档列表
            top_k: 返回前k个结果

        Returns:
            排序后的 (文档, 分数) 列表
        """
        # 创建 query-document pairs
        pairs = [[query, doc] for doc in documents]

        # 获取相关性分数
        scores = self.model.predict(pairs)

        # 排序
        doc_scores = list(zip(documents, scores))
        doc_scores.sort(key=lambda x: x[1], reverse=True)

        if top_k:
            doc_scores = doc_scores[:top_k]

        return doc_scores


class ColBERTReranker:
    """
    ColBERT 风格的重排序

    使用 late interaction:
    - 分别编码query和document的每个token
    - 计算token级别的最大相似度
    - 更高效的cross-encoder替代方案
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def rerank(self,
               query: str,
               documents: list[str],
               top_k: int = None) -> list[Tuple[str, float]]:
        """使用MaxSim进行重排序"""

        # 获取query的token嵌入
        query_embedding = self.model.encode(
            query,
            output_value='token_embeddings'
        )

        doc_scores = []

        for doc in documents:
            # 获取document的token嵌入
            doc_embedding = self.model.encode(
                doc,
                output_value='token_embeddings'
            )

            # 计算MaxSim分数
            score = self._compute_maxsim(query_embedding, doc_embedding)
            doc_scores.append((doc, score))

        # 排序
        doc_scores.sort(key=lambda x: x[1], reverse=True)

        if top_k:
            doc_scores = doc_scores[:top_k]

        return doc_scores

    def _compute_maxsim(self, query_emb, doc_emb) -> float:
        """
        计算 MaxSim 分数
        对query中每个token，找到doc中最相似的token
        然后求和
        """
        import numpy as np

        # 计算所有token对的相似度矩阵
        sim_matrix = np.dot(query_emb, doc_emb.T)

        # 对每个query token取最大相似度
        max_sims = sim_matrix.max(axis=1)

        # 求和作为最终分数
        return float(max_sims.sum())
```

### 5.3 LLM 重排序

```python
class LLMReranker:
    """
    使用LLM进行重排序

    优点: 可以理解复杂的语义关系
    缺点: 成本较高，速度较慢
    """

    def __init__(self, llm):
        self.llm = llm

    def rerank(self,
               query: str,
               documents: list[str],
               top_k: int = 5) -> list[Tuple[str, float]]:
        """使用LLM进行重排序"""

        # 方法1: Pointwise - 对每个文档单独评分
        return self._pointwise_rerank(query, documents, top_k)

    def _pointwise_rerank(self, query: str, documents: list[str],
                          top_k: int) -> list[Tuple[str, float]]:
        """逐点评分"""
        scored_docs = []

        for doc in documents:
            score = self._score_document(query, doc)
            scored_docs.append((doc, score))

        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return scored_docs[:top_k]

    def _score_document(self, query: str, document: str) -> float:
        """为单个文档评分"""
        prompt = f"""请评估以下文档与查询的相关性。

查询: {query}

文档: {document}

请给出1-10的相关性评分，其中:
- 1-3: 不相关
- 4-6: 部分相关
- 7-10: 高度相关

只输出数字分数:"""

        response = self.llm.predict(prompt)

        try:
            score = float(response.strip())
            return min(max(score, 1), 10)  # 限制在1-10范围
        except:
            return 5.0  # 默认中等分数

    def listwise_rerank(self, query: str, documents: list[str],
                        top_k: int = 5) -> list[str]:
        """
        列表级重排序
        一次性对所有文档排序
        更高效但可能受上下文长度限制
        """

        # 为文档编号
        doc_list = "\n".join([f"[{i}] {doc[:200]}..."
                              for i, doc in enumerate(documents)])

        prompt = f"""请根据与查询的相关性，对以下文档进行排序。

查询: {query}

文档列表:
{doc_list}

请按相关性从高到低输出文档编号，用逗号分隔:"""

        response = self.llm.predict(prompt)

        # 解析排序结果
        try:
            indices = [int(x.strip().strip('[]'))
                      for x in response.split(',')]
            reranked = [documents[i] for i in indices if i < len(documents)]
            return reranked[:top_k]
        except:
            return documents[:top_k]
```

---

## 6. 上下文压缩与优化

### 6.1 上下文压缩策略

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      上下文压缩策略                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    检索到的文档                                   │   │
│  │  [很长的文档1] [很长的文档2] [很长的文档3] ...                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼                                          │
│           ┌──────────────────────────────────────┐                     │
│           │            压缩策略选择               │                     │
│           └──────────────────────────────────────┘                     │
│                              │                                          │
│        ┌─────────────────────┼─────────────────────┐                   │
│        │                     │                     │                    │
│        ▼                     ▼                     ▼                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐             │
│  │   提取式压缩   │    │   生成式压缩   │    │  过滤式压缩   │             │
│  ├──────────────┤    ├──────────────┤    ├──────────────┤             │
│  │ • 句子抽取    │    │ • LLM摘要    │    │ • 相关性过滤  │             │
│  │ • 关键段落    │    │ • 信息压缩    │    │ • 冗余删除    │             │
│  │ • 保持原文    │    │ • 语义保持    │    │ • 去噪        │             │
│  └──────────────┘    └──────────────┘    └──────────────┘             │
│        │                     │                     │                    │
│        └─────────────────────┼─────────────────────┘                   │
│                              ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    压缩后的上下文                                  │   │
│  │  [精简内容1] [精简内容2] [精简内容3]                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 实现

```python
from typing import List
import re

class ContextCompressor:
    """上下文压缩器"""

    def __init__(self, llm):
        self.llm = llm

    def extract_relevant_sentences(self,
                                    query: str,
                                    document: str,
                                    max_sentences: int = 5) -> str:
        """提取式压缩 - 抽取最相关的句子"""

        # 分割句子
        sentences = re.split(r'(?<=[.!?])\s+', document)

        # 使用LLM选择最相关的句子
        prompt = f"""给定查询和文档，请选择最相关的{max_sentences}个句子。

查询: {query}

文档句子:
{chr(10).join([f'{i}. {s}' for i, s in enumerate(sentences)])}

请输出相关句子的编号，用逗号分隔:"""

        response = self.llm.predict(prompt)

        try:
            indices = [int(x.strip()) for x in response.split(',')]
            selected = [sentences[i] for i in indices if i < len(sentences)]
            return ' '.join(selected)
        except:
            return document[:1000]  # 失败时返回截断内容

    def abstractive_compress(self,
                             query: str,
                             document: str,
                             max_tokens: int = 200) -> str:
        """生成式压缩 - LLM重写"""

        prompt = f"""请根据查询压缩以下文档，只保留回答查询所需的关键信息。
压缩后的内容不超过{max_tokens}词。

查询: {query}

原始文档: {document}

压缩后的内容:"""

        return self.llm.predict(prompt)

    def filter_irrelevant(self,
                          query: str,
                          documents: list[str],
                          threshold: float = 0.5) -> list[str]:
        """过滤式压缩 - 删除不相关文档"""

        filtered = []

        for doc in documents:
            # 使用LLM判断相关性
            prompt = f"""文档与查询是否相关？只回答"是"或"否"。

查询: {query}
文档: {doc[:500]}

回答:"""

            response = self.llm.predict(prompt).strip().lower()

            if '是' in response or 'yes' in response:
                filtered.append(doc)

        return filtered


class LongContextOptimizer:
    """长上下文优化器"""

    def __init__(self, llm):
        self.llm = llm

    def reorder_documents(self, documents: list[str]) -> list[str]:
        """
        Lost in the Middle 优化

        研究表明LLM对中间位置的内容注意力较低
        将重要文档放在开头和结尾
        """
        n = len(documents)
        if n <= 2:
            return documents

        # 假设文档按相关性降序排列
        reordered = []

        # 交替放置：开头和结尾
        for i, doc in enumerate(documents):
            if i % 2 == 0:
                reordered.insert(0, doc)  # 放开头
            else:
                reordered.append(doc)      # 放结尾

        return reordered

    def create_hierarchical_context(self,
                                     query: str,
                                     documents: list[str]) -> str:
        """创建层次化上下文"""

        # 为每个文档生成一行摘要
        summaries = []
        for i, doc in enumerate(documents):
            summary = self._summarize_short(doc)
            summaries.append(f"[文档{i+1}摘要]: {summary}")

        context = f"""以下是检索到的相关文档：

=== 文档概览 ===
{chr(10).join(summaries)}

=== 详细内容 ===
"""

        for i, doc in enumerate(documents):
            context += f"\n[文档{i+1}]\n{doc}\n"

        return context

    def _summarize_short(self, text: str) -> str:
        """生成简短摘要"""
        prompt = f"用一句话总结: {text[:500]}"
        return self.llm.predict(prompt)
```

---

## 7. 多跳推理RAG

### 7.1 多跳推理架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       多跳推理 RAG                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  复杂问题: "苹果公司CEO出生在哪个国家的首都？"                            │
│                                                                         │
│         ┌───────────────────────────────────────────────┐              │
│         │               第一跳                           │              │
│         │  问题分解: "苹果公司的CEO是谁？"                │              │
│         │  检索 → 答案: Tim Cook                        │              │
│         └───────────────────────┬───────────────────────┘              │
│                                 │                                       │
│                                 ▼                                       │
│         ┌───────────────────────────────────────────────┐              │
│         │               第二跳                           │              │
│         │  问题: "Tim Cook 出生在哪个城市？"             │              │
│         │  检索 → 答案: Mobile, Alabama                 │              │
│         └───────────────────────┬───────────────────────┘              │
│                                 │                                       │
│                                 ▼                                       │
│         ┌───────────────────────────────────────────────┐              │
│         │               第三跳                           │              │
│         │  问题: "Mobile 是哪个国家的首都？"             │              │
│         │  检索 → 答案: 不是首都 (需要调整推理)          │              │
│         └───────────────────────┬───────────────────────┘              │
│                                 │                                       │
│                                 ▼                                       │
│         ┌───────────────────────────────────────────────┐              │
│         │            综合推理生成答案                     │              │
│         │  基于收集的所有信息生成最终回答                 │              │
│         └───────────────────────────────────────────────┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 迭代式 RAG 实现

```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class ReasoningStep:
    """推理步骤"""
    thought: str          # 思考过程
    action: str           # 动作类型 (search/lookup/finish)
    action_input: str     # 动作输入
    observation: str      # 观察结果

class IterativeRAG:
    """
    迭代式 RAG (ReAct 风格)

    思考 → 行动 → 观察 → 思考 → ...
    """

    def __init__(self, retriever, llm, max_iterations: int = 5):
        self.retriever = retriever
        self.llm = llm
        self.max_iterations = max_iterations

    def query(self, question: str) -> tuple[str, list[ReasoningStep]]:
        """迭代式问答"""

        steps: List[ReasoningStep] = []
        context = ""

        for i in range(self.max_iterations):
            # 构建提示
            prompt = self._build_prompt(question, steps)

            # 获取下一步动作
            response = self.llm.predict(prompt)

            # 解析响应
            thought, action, action_input = self._parse_response(response)

            if action == "Finish":
                # 完成推理
                final_answer = action_input
                steps.append(ReasoningStep(
                    thought=thought,
                    action=action,
                    action_input=action_input,
                    observation="完成"
                ))
                return final_answer, steps

            elif action == "Search":
                # 执行检索
                results = self.retriever.search(action_input)
                observation = self._format_results(results)

            elif action == "Lookup":
                # 在已有上下文中查找
                observation = self._lookup_in_context(action_input, context)

            else:
                observation = "未知动作"

            steps.append(ReasoningStep(
                thought=thought,
                action=action,
                action_input=action_input,
                observation=observation
            ))

            context += f"\n{observation}"

        return "达到最大迭代次数", steps

    def _build_prompt(self, question: str, steps: list[ReasoningStep]) -> str:
        """构建ReAct风格的提示"""

        prompt = f"""你是一个推理助手。使用以下格式回答问题：

问题：需要回答的问题
思考：分析问题，决定下一步
动作：Search[查询] 或 Lookup[关键词] 或 Finish[最终答案]
观察：动作的结果

问题: {question}
"""

        for step in steps:
            prompt += f"""
思考: {step.thought}
动作: {step.action}[{step.action_input}]
观察: {step.observation}
"""

        prompt += "\n思考:"

        return prompt

    def _parse_response(self, response: str) -> tuple[str, str, str]:
        """解析LLM响应"""
        import re

        thought = response.split("动作:")[0].strip()

        action_match = re.search(r'动作:\s*(\w+)\[(.+?)\]', response)
        if action_match:
            action = action_match.group(1)
            action_input = action_match.group(2)
        else:
            action = "Finish"
            action_input = response

        return thought, action, action_input

    def _format_results(self, results: list) -> str:
        """格式化检索结果"""
        if not results:
            return "未找到相关信息"
        return "\n".join([f"- {r}" for r in results[:3]])

    def _lookup_in_context(self, keyword: str, context: str) -> str:
        """在上下文中查找"""
        sentences = context.split('.')
        relevant = [s for s in sentences if keyword.lower() in s.lower()]
        return '. '.join(relevant[:2]) if relevant else "未找到相关内容"


class SelfRAG:
    """
    Self-RAG: 自我反思增强的RAG

    决定是否需要检索，并对结果进行自我评估
    """

    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm

    def query(self, question: str) -> dict:
        """带自我反思的问答"""

        # 1. 判断是否需要检索
        needs_retrieval = self._check_retrieval_need(question)

        if not needs_retrieval:
            # 直接回答
            answer = self._generate_answer(question, "")
            return {
                'answer': answer,
                'retrieved': False,
                'sources': []
            }

        # 2. 检索
        documents = self.retriever.search(question)

        # 3. 评估每个文档的相关性
        relevant_docs = []
        for doc in documents:
            if self._is_relevant(question, doc):
                relevant_docs.append(doc)

        # 4. 生成答案
        context = "\n\n".join(relevant_docs)
        answer = self._generate_answer(question, context)

        # 5. 自我评估答案质量
        is_supported = self._check_support(answer, relevant_docs)
        is_useful = self._check_usefulness(question, answer)

        return {
            'answer': answer,
            'retrieved': True,
            'sources': relevant_docs,
            'is_supported': is_supported,
            'is_useful': is_useful
        }

    def _check_retrieval_need(self, question: str) -> bool:
        """判断是否需要检索"""
        prompt = f"""这个问题是否需要查询外部知识来回答？

问题: {question}

回答"是"或"否":"""

        response = self.llm.predict(prompt)
        return '是' in response.lower() or 'yes' in response.lower()

    def _is_relevant(self, question: str, document: str) -> bool:
        """判断文档是否相关"""
        prompt = f"""这个文档是否与问题相关？

问题: {question}
文档: {document[:500]}

回答"是"或"否":"""

        response = self.llm.predict(prompt)
        return '是' in response.lower() or 'yes' in response.lower()

    def _generate_answer(self, question: str, context: str) -> str:
        """生成答案"""
        if context:
            prompt = f"""基于以下信息回答问题:

信息: {context}

问题: {question}

回答:"""
        else:
            prompt = f"回答问题: {question}"

        return self.llm.predict(prompt)

    def _check_support(self, answer: str, documents: list[str]) -> bool:
        """检查答案是否有文档支持"""
        context = "\n".join(documents)
        prompt = f"""检查答案是否有文档支持。

文档: {context[:1000]}
答案: {answer}

答案是否有充分的文档支持？回答"是"或"否":"""

        response = self.llm.predict(prompt)
        return '是' in response.lower()

    def _check_usefulness(self, question: str, answer: str) -> bool:
        """检查答案是否有用"""
        prompt = f"""评估答案是否真正回答了问题。

问题: {question}
答案: {answer}

答案是否有用且相关？回答"是"或"否":"""

        response = self.llm.predict(prompt)
        return '是' in response.lower()
```

## 8. 知识图谱增强RAG

### 8.1 Graph RAG 架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Knowledge Graph + RAG                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                      知识图谱层                                   │  │
│   │                                                                   │  │
│   │        [公司]                        [人物]                       │  │
│   │          │                             │                         │  │
│   │          │  创始人                      │  就职于                  │  │
│   │          ▼                             ▼                         │  │
│   │       ┌─────┐    CEO     ┌─────┐    工作于    ┌─────┐            │  │
│   │       │Apple│◄──────────│Tim  │──────────▶│ 产品 │            │  │
│   │       └─────┘           │Cook │           └─────┘            │  │
│   │          │              └─────┘              │                │  │
│   │          │ 产品                               │                │  │
│   │          ▼                                   ▼                │  │
│   │       ┌─────┐                           ┌─────┐              │  │
│   │       │iPhone│                          │Vision│              │  │
│   │       └─────┘                           │ Pro │              │  │
│   │                                         └─────┘              │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                   │                                     │
│                                   ▼                                     │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                      检索融合层                                   │  │
│   │                                                                   │  │
│   │   ┌──────────────────┐         ┌──────────────────┐             │  │
│   │   │    向量检索        │    +    │    图谱遍历        │             │  │
│   │   │  (语义相似)        │         │  (结构化关系)      │             │  │
│   │   └──────────────────┘         └──────────────────┘             │  │
│   │                                                                   │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 GraphRAG 实现

```python
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
import networkx as nx

@dataclass
class Entity:
    """实体"""
    id: str
    name: str
    type: str
    properties: Dict[str, any]

@dataclass
class Relation:
    """关系"""
    source: str
    target: str
    type: str
    properties: Dict[str, any]

class KnowledgeGraph:
    """知识图谱"""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.entities: Dict[str, Entity] = {}

    def add_entity(self, entity: Entity):
        """添加实体"""
        self.entities[entity.id] = entity
        self.graph.add_node(
            entity.id,
            name=entity.name,
            type=entity.type,
            **entity.properties
        )

    def add_relation(self, relation: Relation):
        """添加关系"""
        self.graph.add_edge(
            relation.source,
            relation.target,
            type=relation.type,
            **relation.properties
        )

    def get_neighbors(self, entity_id: str,
                      hop: int = 1) -> List[Tuple[str, dict]]:
        """获取邻居节点"""
        neighbors = []
        visited = {entity_id}
        queue = [(entity_id, 0)]

        while queue:
            node, depth = queue.pop(0)
            if depth >= hop:
                continue

            for neighbor in self.graph.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    edge_data = self.graph[node][neighbor]
                    neighbors.append((neighbor, edge_data))
                    queue.append((neighbor, depth + 1))

        return neighbors

    def get_subgraph(self, entity_ids: List[str]) -> nx.DiGraph:
        """获取子图"""
        return self.graph.subgraph(entity_ids).copy()

    def find_path(self, source: str, target: str) -> List[str]:
        """查找两个实体之间的路径"""
        try:
            return nx.shortest_path(self.graph, source, target)
        except nx.NetworkXNoPath:
            return []


class GraphRAG:
    """
    图增强的RAG
    结合知识图谱和向量检索
    """

    def __init__(self,
                 knowledge_graph: KnowledgeGraph,
                 vectorstore,
                 llm,
                 embeddings):
        self.kg = knowledge_graph
        self.vectorstore = vectorstore
        self.llm = llm
        self.embeddings = embeddings

    def query(self, question: str, k: int = 5) -> dict:
        """图增强检索问答"""

        # 1. 提取问题中的实体
        entities = self._extract_entities(question)

        # 2. 在知识图谱中查找相关信息
        graph_context = self._get_graph_context(entities)

        # 3. 向量检索
        vector_results = self.vectorstore.similarity_search(question, k=k)
        vector_context = "\n\n".join([r.page_content for r in vector_results])

        # 4. 合并上下文
        combined_context = self._merge_contexts(graph_context, vector_context)

        # 5. 生成答案
        answer = self._generate_answer(question, combined_context)

        return {
            'answer': answer,
            'entities': entities,
            'graph_context': graph_context,
            'vector_context': vector_context
        }

    def _extract_entities(self, text: str) -> List[str]:
        """从文本中提取实体"""
        prompt = f"""请从以下文本中提取关键实体（人名、组织、产品等）。

文本: {text}

请列出实体，每行一个:"""

        response = self.llm.predict(prompt)
        entities = [e.strip() for e in response.split('\n') if e.strip()]

        # 在知识图谱中匹配
        matched = []
        for entity in entities:
            for eid, e in self.kg.entities.items():
                if entity.lower() in e.name.lower():
                    matched.append(eid)

        return matched

    def _get_graph_context(self, entity_ids: List[str]) -> str:
        """从知识图谱获取上下文"""
        context_parts = []

        for eid in entity_ids:
            entity = self.kg.entities.get(eid)
            if not entity:
                continue

            # 实体信息
            context_parts.append(f"实体: {entity.name} (类型: {entity.type})")

            # 获取邻居
            neighbors = self.kg.get_neighbors(eid, hop=2)
            for neighbor_id, edge_data in neighbors:
                neighbor = self.kg.entities.get(neighbor_id)
                if neighbor:
                    rel_type = edge_data.get('type', '相关')
                    context_parts.append(
                        f"  - {rel_type} → {neighbor.name}"
                    )

        return "\n".join(context_parts)

    def _merge_contexts(self, graph_ctx: str, vector_ctx: str) -> str:
        """合并图谱和向量检索的上下文"""
        return f"""=== 结构化知识 ===
{graph_ctx}

=== 相关文档 ===
{vector_ctx}"""

    def _generate_answer(self, question: str, context: str) -> str:
        """生成答案"""
        prompt = f"""基于以下信息回答问题。

{context}

问题: {question}

回答:"""

        return self.llm.predict(prompt)


class EntityLinker:
    """实体链接器 - 将文本中的实体链接到知识图谱"""

    def __init__(self, kg: KnowledgeGraph, embeddings):
        self.kg = kg
        self.embeddings = embeddings
        self.entity_embeddings = {}

        # 预计算所有实体的嵌入
        for eid, entity in kg.entities.items():
            self.entity_embeddings[eid] = embeddings.embed_query(entity.name)

    def link(self, mention: str, threshold: float = 0.7) -> Optional[str]:
        """将提及链接到知识图谱实体"""
        import numpy as np

        mention_emb = self.embeddings.embed_query(mention)

        best_match = None
        best_score = 0

        for eid, emb in self.entity_embeddings.items():
            score = np.dot(mention_emb, emb) / (
                np.linalg.norm(mention_emb) * np.linalg.norm(emb)
            )
            if score > best_score:
                best_score = score
                best_match = eid

        if best_score >= threshold:
            return best_match
        return None
```

## 9. 自适应RAG

### 9.1 自适应检索策略

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        自适应 RAG 决策流程                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                         ┌──────────────┐                               │
│                         │   用户查询    │                               │
│                         └──────┬───────┘                               │
│                                │                                        │
│                                ▼                                        │
│                    ┌───────────────────────┐                           │
│                    │      查询分类器        │                           │
│                    │  (分析查询复杂度和类型) │                           │
│                    └───────────┬───────────┘                           │
│                                │                                        │
│        ┌───────────────────────┼───────────────────────┐               │
│        │                       │                       │                │
│        ▼                       ▼                       ▼                │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐          │
│  │  直接回答     │      │  单次检索     │      │  多跳推理     │          │
│  │  (简单事实)   │      │  (标准RAG)   │      │  (复杂问题)   │          │
│  └──────┬───────┘      └──────┬───────┘      └──────┬───────┘          │
│         │                     │                     │                   │
│         │                     ▼                     │                   │
│         │           ┌───────────────────┐           │                   │
│         │           │   策略选择器      │           │                   │
│         │           │ • 检索源选择     │           │                   │
│         │           │ • 分块策略选择   │           │                   │
│         │           │ • 重排序策略选择 │           │                   │
│         │           └───────────────────┘           │                   │
│         │                     │                     │                   │
│         └─────────────────────┼─────────────────────┘                   │
│                               │                                         │
│                               ▼                                         │
│                    ┌───────────────────────┐                            │
│                    │     自信度评估         │                            │
│                    │  (是否需要重试/改进)   │                            │
│                    └───────────────────────┘                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 9.2 自适应RAG实现

```python
from enum import Enum
from typing import Callable, Dict, Any

class QueryType(Enum):
    """查询类型"""
    SIMPLE_FACT = "simple_fact"      # 简单事实，可能不需要检索
    STANDARD = "standard"             # 标准问题，单次检索
    COMPLEX = "complex"               # 复杂问题，需要多跳
    COMPARISON = "comparison"         # 比较类问题
    AGGREGATION = "aggregation"       # 聚合类问题

class AdaptiveRAG:
    """
    自适应RAG系统
    根据查询特征自动选择最佳策略
    """

    def __init__(self,
                 llm,
                 retriever,
                 multi_hop_retriever=None,
                 graph_retriever=None):
        self.llm = llm
        self.retriever = retriever
        self.multi_hop_retriever = multi_hop_retriever
        self.graph_retriever = graph_retriever

        # 策略注册
        self.strategies: Dict[QueryType, Callable] = {
            QueryType.SIMPLE_FACT: self._handle_simple,
            QueryType.STANDARD: self._handle_standard,
            QueryType.COMPLEX: self._handle_complex,
            QueryType.COMPARISON: self._handle_comparison,
            QueryType.AGGREGATION: self._handle_aggregation,
        }

    def query(self, question: str) -> Dict[str, Any]:
        """自适应问答"""

        # 1. 分类查询
        query_type = self._classify_query(question)

        # 2. 选择策略并执行
        strategy = self.strategies.get(query_type, self._handle_standard)
        result = strategy(question)

        # 3. 评估结果质量
        confidence = self._evaluate_confidence(question, result)

        # 4. 如果信心不足，尝试升级策略
        if confidence < 0.7:
            result = self._retry_with_enhanced_strategy(
                question, query_type, result
            )

        return {
            'answer': result['answer'],
            'query_type': query_type.value,
            'confidence': confidence,
            'sources': result.get('sources', []),
            'strategy_used': result.get('strategy', 'unknown')
        }

    def _classify_query(self, question: str) -> QueryType:
        """分类查询类型"""

        prompt = f"""分析以下问题的类型。

问题: {question}

类型选项:
1. simple_fact: 简单事实问题（如"什么是...的首都"）
2. standard: 标准问题（需要检索单一文档）
3. complex: 复杂问题（需要综合多个信息源）
4. comparison: 比较类问题（需要对比多个实体）
5. aggregation: 聚合类问题（需要汇总多个信息）

请只输出类型名称:"""

        response = self.llm.predict(prompt).strip().lower()

        type_map = {
            'simple_fact': QueryType.SIMPLE_FACT,
            'standard': QueryType.STANDARD,
            'complex': QueryType.COMPLEX,
            'comparison': QueryType.COMPARISON,
            'aggregation': QueryType.AGGREGATION,
        }

        return type_map.get(response, QueryType.STANDARD)

    def _handle_simple(self, question: str) -> dict:
        """处理简单问题 - 可能不需要检索"""

        # 先尝试直接回答
        prompt = f"""如果你确定知道答案，请直接回答。如果不确定，请回答"需要检索"。

问题: {question}

回答:"""

        response = self.llm.predict(prompt)

        if "需要检索" in response:
            # 降级到标准检索
            return self._handle_standard(question)

        return {
            'answer': response,
            'strategy': 'direct_answer',
            'sources': []
        }

    def _handle_standard(self, question: str) -> dict:
        """标准RAG处理"""

        # 检索
        docs = self.retriever.search(question)
        context = "\n\n".join(docs)

        # 生成
        prompt = f"""基于以下信息回答问题:

{context}

问题: {question}

回答:"""

        answer = self.llm.predict(prompt)

        return {
            'answer': answer,
            'strategy': 'standard_rag',
            'sources': docs
        }

    def _handle_complex(self, question: str) -> dict:
        """处理复杂问题 - 使用多跳推理"""

        if self.multi_hop_retriever:
            answer, steps = self.multi_hop_retriever.query(question)
            return {
                'answer': answer,
                'strategy': 'multi_hop',
                'sources': [s.observation for s in steps],
                'reasoning_steps': steps
            }

        # 降级到标准策略
        return self._handle_standard(question)

    def _handle_comparison(self, question: str) -> dict:
        """处理比较类问题"""

        # 提取比较对象
        entities = self._extract_comparison_entities(question)

        # 分别检索每个实体的信息
        all_docs = []
        for entity in entities:
            docs = self.retriever.search(entity)
            all_docs.extend(docs)

        context = "\n\n".join(all_docs)

        prompt = f"""请比较分析以下实体的信息，回答问题:

相关信息:
{context}

问题: {question}

请结构化地进行比较分析:"""

        answer = self.llm.predict(prompt)

        return {
            'answer': answer,
            'strategy': 'comparison',
            'sources': all_docs,
            'compared_entities': entities
        }

    def _handle_aggregation(self, question: str) -> dict:
        """处理聚合类问题"""

        # 扩大检索范围
        docs = self.retriever.search(question, k=10)

        # 汇总信息
        context = "\n\n".join(docs)

        prompt = f"""这是一个需要汇总多方信息的问题。

相关信息:
{context}

问题: {question}

请综合所有相关信息给出全面的回答:"""

        answer = self.llm.predict(prompt)

        return {
            'answer': answer,
            'strategy': 'aggregation',
            'sources': docs
        }

    def _extract_comparison_entities(self, question: str) -> list[str]:
        """提取比较实体"""
        prompt = f"""从以下问题中提取需要比较的实体:

问题: {question}

请列出实体，用逗号分隔:"""

        response = self.llm.predict(prompt)
        return [e.strip() for e in response.split(',')]

    def _evaluate_confidence(self, question: str, result: dict) -> float:
        """评估答案置信度"""

        answer = result.get('answer', '')
        sources = result.get('sources', [])

        # 简单评估规则
        score = 0.5

        # 有来源加分
        if sources:
            score += 0.2

        # 答案长度适中加分
        if 50 < len(answer) < 1000:
            score += 0.1

        # 使用LLM评估
        prompt = f"""评估这个回答的质量（0-1分）:

问题: {question}
回答: {answer}

只输出分数:"""

        try:
            llm_score = float(self.llm.predict(prompt).strip())
            score = (score + llm_score) / 2
        except:
            pass

        return min(score, 1.0)

    def _retry_with_enhanced_strategy(self,
                                       question: str,
                                       original_type: QueryType,
                                       original_result: dict) -> dict:
        """使用增强策略重试"""

        # 升级策略映射
        upgrade_map = {
            QueryType.SIMPLE_FACT: QueryType.STANDARD,
            QueryType.STANDARD: QueryType.COMPLEX,
            QueryType.COMPLEX: QueryType.AGGREGATION,
        }

        upgraded_type = upgrade_map.get(original_type)

        if upgraded_type:
            strategy = self.strategies.get(upgraded_type)
            if strategy:
                result = strategy(question)
                result['upgraded_from'] = original_type.value
                return result

        return original_result
```

## 10. RAG评估体系

### 10.1 评估维度

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        RAG 评估框架                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                    检索质量评估                                  │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │    │
│  │  │   召回率      │ │   精确率      │ │   MRR/NDCG   │           │    │
│  │  │  Recall@K    │ │ Precision@K  │ │   排序质量    │           │    │
│  │  └──────────────┘ └──────────────┘ └──────────────┘           │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                    生成质量评估                                  │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │    │
│  │  │   忠实度      │ │   相关性      │ │   完整性      │           │    │
│  │  │ Faithfulness │ │  Relevance   │ │ Completeness │           │    │
│  │  └──────────────┘ └──────────────┘ └──────────────┘           │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                    端到端评估                                    │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │    │
│  │  │   答案正确性   │ │   用户满意度   │ │   延迟/成本   │           │    │
│  │  │  Correctness │ │ User Rating  │ │   Latency    │           │    │
│  │  └──────────────┘ └──────────────┘ └──────────────┘           │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 10.2 评估实现

```python
from dataclasses import dataclass
from typing import List, Optional
import numpy as np

@dataclass
class RAGEvalResult:
    """RAG评估结果"""
    # 检索指标
    retrieval_precision: float
    retrieval_recall: float
    retrieval_mrr: float

    # 生成指标
    faithfulness: float
    answer_relevance: float
    context_relevance: float

    # 端到端指标
    answer_correctness: float
    latency_ms: float

class RAGEvaluator:
    """RAG系统评估器"""

    def __init__(self, llm):
        self.llm = llm

    def evaluate(self,
                 question: str,
                 answer: str,
                 contexts: List[str],
                 ground_truth: Optional[str] = None,
                 relevant_docs: Optional[List[str]] = None) -> RAGEvalResult:
        """全面评估RAG系统"""

        # 检索评估
        if relevant_docs:
            precision = self._calc_precision(contexts, relevant_docs)
            recall = self._calc_recall(contexts, relevant_docs)
            mrr = self._calc_mrr(contexts, relevant_docs)
        else:
            precision = recall = mrr = None

        # 生成评估
        faithfulness = self._eval_faithfulness(answer, contexts)
        answer_relevance = self._eval_answer_relevance(question, answer)
        context_relevance = self._eval_context_relevance(question, contexts)

        # 答案正确性
        if ground_truth:
            correctness = self._eval_correctness(answer, ground_truth)
        else:
            correctness = None

        return RAGEvalResult(
            retrieval_precision=precision,
            retrieval_recall=recall,
            retrieval_mrr=mrr,
            faithfulness=faithfulness,
            answer_relevance=answer_relevance,
            context_relevance=context_relevance,
            answer_correctness=correctness,
            latency_ms=0  # 需要外部测量
        )

    def _calc_precision(self, retrieved: List[str],
                        relevant: List[str]) -> float:
        """计算精确率"""
        if not retrieved:
            return 0.0

        relevant_set = set(relevant)
        hits = sum(1 for doc in retrieved if doc in relevant_set)
        return hits / len(retrieved)

    def _calc_recall(self, retrieved: List[str],
                     relevant: List[str]) -> float:
        """计算召回率"""
        if not relevant:
            return 0.0

        retrieved_set = set(retrieved)
        hits = sum(1 for doc in relevant if doc in retrieved_set)
        return hits / len(relevant)

    def _calc_mrr(self, retrieved: List[str],
                  relevant: List[str]) -> float:
        """计算Mean Reciprocal Rank"""
        relevant_set = set(relevant)

        for i, doc in enumerate(retrieved):
            if doc in relevant_set:
                return 1.0 / (i + 1)
        return 0.0

    def _eval_faithfulness(self, answer: str, contexts: List[str]) -> float:
        """
        评估忠实度
        答案是否能从上下文中推导出来
        """
        context = "\n\n".join(contexts)

        prompt = f"""评估回答是否忠实于给定的上下文。
忠实意味着回答中的所有信息都可以从上下文中找到或推导出来。

上下文:
{context}

回答: {answer}

评分标准:
1-3: 包含上下文中没有的信息（幻觉）
4-6: 部分信息可以追溯到上下文
7-10: 所有信息都可以从上下文中找到

只输出分数(1-10):"""

        try:
            score = float(self.llm.predict(prompt).strip())
            return score / 10
        except:
            return 0.5

    def _eval_answer_relevance(self, question: str, answer: str) -> float:
        """评估答案相关性"""

        prompt = f"""评估回答与问题的相关性。

问题: {question}
回答: {answer}

评分标准:
1-3: 回答与问题无关
4-6: 部分回答了问题
7-10: 完全回答了问题

只输出分数(1-10):"""

        try:
            score = float(self.llm.predict(prompt).strip())
            return score / 10
        except:
            return 0.5

    def _eval_context_relevance(self, question: str,
                                 contexts: List[str]) -> float:
        """评估上下文相关性"""
        scores = []

        for ctx in contexts:
            prompt = f"""评估这段上下文与问题的相关性。

问题: {question}
上下文: {ctx[:500]}

只输出分数(1-10):"""

            try:
                score = float(self.llm.predict(prompt).strip())
                scores.append(score / 10)
            except:
                scores.append(0.5)

        return np.mean(scores) if scores else 0.5

    def _eval_correctness(self, answer: str, ground_truth: str) -> float:
        """评估答案正确性"""

        prompt = f"""比较生成的答案与标准答案。

标准答案: {ground_truth}
生成答案: {answer}

评分标准:
1-3: 答案错误或完全不同
4-6: 部分正确
7-10: 完全正确（可以表述不同）

只输出分数(1-10):"""

        try:
            score = float(self.llm.predict(prompt).strip())
            return score / 10
        except:
            return 0.5


class RAGBenchmark:
    """RAG基准测试"""

    def __init__(self, rag_system, evaluator: RAGEvaluator):
        self.rag = rag_system
        self.evaluator = evaluator

    def run_benchmark(self, test_cases: List[dict]) -> dict:
        """运行基准测试"""

        results = []

        for case in test_cases:
            question = case['question']
            ground_truth = case.get('answer')
            relevant_docs = case.get('relevant_docs', [])

            # 运行RAG
            import time
            start = time.time()
            rag_result = self.rag.query(question)
            latency = (time.time() - start) * 1000

            # 评估
            eval_result = self.evaluator.evaluate(
                question=question,
                answer=rag_result['answer'],
                contexts=rag_result.get('sources', []),
                ground_truth=ground_truth,
                relevant_docs=relevant_docs
            )
            eval_result.latency_ms = latency

            results.append(eval_result)

        # 汇总统计
        return self._aggregate_results(results)

    def _aggregate_results(self, results: List[RAGEvalResult]) -> dict:
        """汇总评估结果"""

        def safe_mean(values):
            valid = [v for v in values if v is not None]
            return np.mean(valid) if valid else None

        return {
            'retrieval': {
                'precision': safe_mean([r.retrieval_precision for r in results]),
                'recall': safe_mean([r.retrieval_recall for r in results]),
                'mrr': safe_mean([r.retrieval_mrr for r in results]),
            },
            'generation': {
                'faithfulness': safe_mean([r.faithfulness for r in results]),
                'answer_relevance': safe_mean([r.answer_relevance for r in results]),
                'context_relevance': safe_mean([r.context_relevance for r in results]),
            },
            'end_to_end': {
                'correctness': safe_mean([r.answer_correctness for r in results]),
                'avg_latency_ms': safe_mean([r.latency_ms for r in results]),
            },
            'num_samples': len(results)
        }
```

## 11. 生产环境最佳实践

### 11.1 系统架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     生产级 RAG 系统架构                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│    ┌─────────────────────────────────────────────────────────────────┐ │
│    │                          网关层                                  │ │
│    │  [API Gateway] ─── [Rate Limiter] ─── [Auth] ─── [Load Balancer]│ │
│    └─────────────────────────────────────────────────────────────────┘ │
│                                    │                                    │
│    ┌─────────────────────────────────────────────────────────────────┐ │
│    │                         服务层                                   │ │
│    │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │ │
│    │  │  Query   │  │Retrieval │  │ Rerank   │  │Generation│        │ │
│    │  │ Service  │  │ Service  │  │ Service  │  │ Service  │        │ │
│    │  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │ │
│    └─────────────────────────────────────────────────────────────────┘ │
│                                    │                                    │
│    ┌─────────────────────────────────────────────────────────────────┐ │
│    │                        数据层                                    │ │
│    │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │ │
│    │  │ Vector   │  │  Graph   │  │  Cache   │  │ Document │        │ │
│    │  │   DB     │  │    DB    │  │ (Redis)  │  │  Store   │        │ │
│    │  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │ │
│    └─────────────────────────────────────────────────────────────────┘ │
│                                    │                                    │
│    ┌─────────────────────────────────────────────────────────────────┐ │
│    │                       监控层                                     │ │
│    │  [Metrics] ─── [Logging] ─── [Tracing] ─── [Alerting]          │ │
│    └─────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 11.2 优化策略

```python
import asyncio
from functools import lru_cache
import hashlib
from typing import List, Dict, Any
import redis

class ProductionRAG:
    """生产级RAG系统"""

    def __init__(self, config: dict):
        self.config = config
        self.cache = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379)
        )
        self.cache_ttl = config.get('cache_ttl', 3600)

        # 初始化组件
        self._init_components()

    def _init_components(self):
        """初始化各组件"""
        # 向量数据库连接池
        # 重排序模型预加载
        # LLM客户端初始化
        pass

    async def query(self,
                    question: str,
                    user_id: str = None,
                    session_id: str = None) -> Dict[str, Any]:
        """
        生产级查询接口

        Features:
        - 缓存层
        - 异步处理
        - 错误处理
        - 监控埋点
        """

        # 1. 检查缓存
        cache_key = self._get_cache_key(question)
        cached = self._get_from_cache(cache_key)
        if cached:
            return {**cached, 'cached': True}

        try:
            # 2. 异步执行检索
            retrieval_task = asyncio.create_task(
                self._async_retrieve(question)
            )

            # 3. 并行执行查询分析
            analysis_task = asyncio.create_task(
                self._analyze_query(question)
            )

            # 等待结果
            docs, analysis = await asyncio.gather(
                retrieval_task,
                analysis_task
            )

            # 4. 根据分析选择策略
            if analysis['needs_rerank']:
                docs = await self._async_rerank(question, docs)

            # 5. 生成答案
            answer = await self._async_generate(question, docs)

            result = {
                'answer': answer,
                'sources': docs[:3],  # 限制返回的源
                'query_type': analysis['type'],
                'cached': False
            }

            # 6. 存入缓存
            self._set_cache(cache_key, result)

            # 7. 记录监控指标
            self._record_metrics(question, result)

            return result

        except Exception as e:
            # 错误处理
            self._record_error(e, question)
            return {
                'answer': "抱歉，处理您的问题时出现了错误。请稍后重试。",
                'error': str(e),
                'cached': False
            }

    def _get_cache_key(self, question: str) -> str:
        """生成缓存键"""
        return f"rag:query:{hashlib.md5(question.encode()).hexdigest()}"

    def _get_from_cache(self, key: str) -> dict:
        """从缓存获取"""
        try:
            import json
            cached = self.cache.get(key)
            if cached:
                return json.loads(cached)
        except:
            pass
        return None

    def _set_cache(self, key: str, value: dict):
        """设置缓存"""
        try:
            import json
            self.cache.setex(
                key,
                self.cache_ttl,
                json.dumps(value, ensure_ascii=False)
            )
        except:
            pass

    async def _async_retrieve(self, question: str) -> List[str]:
        """异步检索"""
        # 实现异步检索逻辑
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._sync_retrieve,
            question
        )

    def _sync_retrieve(self, question: str) -> List[str]:
        """同步检索（在线程池中执行）"""
        # 实际的检索逻辑
        return []

    async def _analyze_query(self, question: str) -> dict:
        """分析查询"""
        return {
            'type': 'standard',
            'needs_rerank': True,
            'estimated_complexity': 'medium'
        }

    async def _async_rerank(self, question: str,
                            docs: List[str]) -> List[str]:
        """异步重排序"""
        return docs

    async def _async_generate(self, question: str,
                              docs: List[str]) -> str:
        """异步生成"""
        return "生成的答案"

    def _record_metrics(self, question: str, result: dict):
        """记录监控指标"""
        # 发送到监控系统
        pass

    def _record_error(self, error: Exception, question: str):
        """记录错误"""
        # 发送到错误追踪系统
        pass


class RAGOptimizer:
    """RAG系统优化器"""

    @staticmethod
    def optimize_embedding_calls(texts: List[str],
                                  embeddings_model,
                                  batch_size: int = 32) -> List[List[float]]:
        """批量优化嵌入调用"""
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = embeddings_model.embed_documents(batch)
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

    @staticmethod
    def create_index_with_metadata(documents: List[dict],
                                    vectorstore_class,
                                    embeddings_model) -> any:
        """
        创建带元数据的索引
        支持更精细的过滤
        """
        from langchain.schema import Document

        docs = [
            Document(
                page_content=d['content'],
                metadata={
                    'source': d.get('source', ''),
                    'category': d.get('category', ''),
                    'timestamp': d.get('timestamp', ''),
                    'author': d.get('author', ''),
                }
            )
            for d in documents
        ]

        return vectorstore_class.from_documents(docs, embeddings_model)

    @staticmethod
    def setup_fallback_strategy(primary_retriever,
                                 secondary_retriever,
                                 threshold: float = 0.5):
        """设置检索失败回退策略"""

        def retrieve_with_fallback(query: str, k: int = 4):
            # 尝试主检索器
            results = primary_retriever.search(query, k=k)

            # 检查结果质量
            if not results or len(results) < k // 2:
                # 回退到备用检索器
                backup_results = secondary_retriever.search(query, k=k)
                results = results + backup_results

            return results[:k]

        return retrieve_with_fallback
```

### 11.3 性能优化清单

┌─────────────────────────────────────────────────────────────────────────┐
│ 性能优化检查清单 │
├─────────────────────────────────────────────────────────────────────────┤
│ │
│ ✅ 索引优化 │
│ □ 使用合适的向量索引类型 (HNSW, IVF, etc.) │
│ □ 调整索引参数 (ef_construction, M, nlist) │
│ □ 定期重建索引优化性能 │
│ │
│ ✅ 缓存策略 │
│ □ 实现查询结果缓存 │
│ □ 嵌入向量缓存 │
│ □ LLM响应缓存（相似查询） │
│ │
│ ✅ 批处理优化 │
│ □ 批量嵌入计算 │
│ □ 批量LLM调用 │
│ □ 异步并行处理 │
│ │
│ ✅ 模型优化 │
│ □ 使用量化模型减少内存 │
│ □ 选择合适大小的嵌入模型 │
│ □ 考虑使用本地模型 │
│ │
│ ✅ 资源管理 │
│ □ 连接池管理 │
│ □ 内存使用监控 │
│ □ GPU资源优化 │
│ │
│ ✅ 监控告警 │
│ □ 延迟监控 (P50, P95, P99) │
│ □ 准确率监控 │
│ □ 错误率监控 │
│ □ 成本监控 │
│ │
└─────────────────────────────────────────────────────────────────────────┘

📚 总结
核心技术栈
技术领域 关键技术 推荐工具
分块 语义分块、父子分块 LangChain, LlamaIndex
检索 混合检索、多向量检索 FAISS, Milvus, Pinecone
重排序 Cross-Encoder, ColBERT sentence-transformers
查询优化 HyDE, Multi-Query LangChain
评估 RAGAS, TruLens RAGAS, DeepEval
知识图谱 Graph RAG Neo4j, LlamaIndex

## 学习路径

```
第一阶段: 基础掌握
├── 理解 RAG 基本原理
├── 实现简单的 RAG 系统
└── 学习向量数据库使用

第二阶段: 进阶提升
├── 实现高级分块策略
├── 掌握混合检索
├── 实现重排序机制
└── 学习查询优化技术

第三阶段: 高级应用
├── 多跳推理 RAG
├── 知识图谱增强
├── 自适应 RAG 系统
└── 生产环境部署

第四阶段: 专家级
├── 自定义评估体系
├── 性能优化调优
├── 特定领域适配
└── 前沿技术跟踪
```
