---
name: create-rag-app
description: 创建 RAG 应用，包含文档处理、向量存储和检索问答
---

# 创建 RAG 应用技能

此技能用于快速创建 RAG (Retrieval-Augmented Generation) 应用。

## RAG 应用架构

```
文档 → 文本分割 → Embedding → 向量存储
                                    ↓
查询 → Embedding → 检索 → 重排序 → 上下文 → LLM → 回答
```

## 核心组件

### 1. 文档加载

```python
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    DirectoryLoader
)

# 单文件加载
loader = PyPDFLoader("document.pdf")
docs = loader.load()

# 目录批量加载
loader = DirectoryLoader(
    "./documents",
    glob="**/*.pdf",
    loader_cls=PyPDFLoader
)
docs = loader.load()
```

### 2. 文本分割

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 推荐配置
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # 块大小
    chunk_overlap=200,      # 重叠大小
    length_function=len,
    separators=[
        "\n\n",  # 段落
        "\n",    # 换行
        "。",    # 中文句号
        "！",
        "？",
        "；",
        " ",
        ""
    ]
)

chunks = splitter.split_documents(docs)
```

### 3. 向量存储

```python
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# 创建向量存储
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

# 加载已有向量存储
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)
```

### 4. 检索器

```python
# 基础检索器
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

# MMR 检索（增加多样性）
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20,
        "lambda_mult": 0.5
    }
)

# 带阈值的检索
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 5,
        "score_threshold": 0.7
    }
)
```

### 5. RAG 链

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 提示词模板
template = """基于以下上下文回答问题。如果无法从上下文中找到答案，请说"我无法从提供的文档中找到相关信息"。

上下文：
{context}

问题：{question}

回答："""

prompt = ChatPromptTemplate.from_template(template)
llm = ChatOpenAI(model="gpt-4")

# 构建 RAG 链
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 使用
answer = rag_chain.invoke("你的问题")
```

## 进阶功能

### 对话式 RAG

```python
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder

# 上下文化问题
contextualize_prompt = ChatPromptTemplate.from_messages([
    ("system", "根据聊天历史将最新问题改写为独立问题"),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_prompt
)
```

### 带源引用的回答

```python
from langchain.chains.combine_documents import create_stuff_documents_chain

template = """基于以下文档回答问题，并在回答末尾列出参考来源。

文档：
{context}

问题：{input}

回答（包含来源引用）："""

prompt = ChatPromptTemplate.from_template(template)
document_chain = create_stuff_documents_chain(llm, prompt)
```

## 完整项目结构

```
rag-project/
├── main.py              # 主入口
├── app.py               # FastAPI 服务
├── ingest.py            # 文档导入脚本
├── chains.py            # RAG 链定义
├── config.py            # 配置
├── requirements.txt
├── .env.example
├── data/                # 源文档
│   └── documents/
└── chroma_db/           # 向量存储
```

## 评估指标

- **Faithfulness**：回答是否忠实于检索到的内容
- **Answer Relevancy**：回答与问题的相关性
- **Context Precision**：检索结果的精确度
- **Context Recall**：检索结果的召回率

## 注意事项

- 根据文档类型选择合适的 chunk_size
- 中文文档使用中文分隔符
- 定期更新向量库
- 监控检索质量
