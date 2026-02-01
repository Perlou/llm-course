"""
企业级知识库系统 - 完整实现
==========================

学习目标：
    1. 实现完整的知识库后端服务
    2. 掌握生产级代码组织方式
    3. 实现文档处理和 RAG 问答

本文件包含核心实现代码参考

环境要求：
    - pip install fastapi uvicorn langchain langchain-google-genai
    - pip install qdrant-client sqlalchemy redis celery
    - pip install python-multipart pydantic
"""

# ==================== 项目结构 ====================

PROJECT_STRUCTURE = """
knowledge-base/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 入口
│   ├── config.py               # 配置管理
│   ├── dependencies.py         # 依赖注入
│   │
│   ├── api/                    # API 路由
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── knowledge_base.py
│   │   │   ├── documents.py
│   │   │   └── chat.py
│   │
│   ├── services/               # 业务逻辑
│   │   ├── document_service.py
│   │   ├── rag_service.py
│   │   ├── vector_service.py
│   │   └── user_service.py
│   │
│   ├── models/                 # 数据模型
│   │   ├── database.py
│   │   ├── user.py
│   │   ├── knowledge_base.py
│   │   └── document.py
│   │
│   ├── schemas/                # Pydantic 模型
│   │   ├── chat.py
│   │   └── document.py
│   │
│   └── utils/                  # 工具函数
│       ├── document_parser.py
│       └── text_splitter.py
│
├── tests/
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
"""


# ==================== 核心配置 ====================

CONFIG_CODE = """
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Knowledge Base"
    DEBUG: bool = False

    # 数据库
    DATABASE_URL: str = "postgresql://user:pass@localhost/kb"
    REDIS_URL: str = "redis://localhost:6379"

    # 向量数据库
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # LLM
    GOOGLE_API_KEY: str
    EMBEDDING_MODEL: str = "models/embedding-001"
    CHAT_MODEL: str = "gemini-1.5-flash"

    # RAG 配置
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    TOP_K: int = 10

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()
"""

print("=" * 60)
print("第一部分：项目结构")
print("=" * 60)
print(PROJECT_STRUCTURE)

print("\n" + "=" * 60)
print("第二部分：配置管理")
print("=" * 60)
print(CONFIG_CODE)


# ==================== 文档服务 ====================

DOCUMENT_SERVICE = '''
# app/services/document_service.py
from langchain_community.document_loaders import (
    PyPDFLoader, Docx2txtLoader, UnstructuredExcelLoader, TextLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import get_settings

settings = get_settings()

class DocumentService:
    """文档处理服务"""

    LOADERS = {
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
        ".xlsx": UnstructuredExcelLoader,
        ".txt": TextLoader,
        ".md": TextLoader,
    }

    def __init__(self, vector_service):
        self.vector_service = vector_service
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\\n\\n", "\\n", "。", ".", " "]
        )

    async def process_document(self, file_path: str, kb_id: str, doc_id: str):
        """处理文档：解析 -> 分块 -> 向量化 -> 存储"""
        # 1. 解析文档
        ext = Path(file_path).suffix.lower()
        loader_class = self.LOADERS.get(ext)
        if not loader_class:
            raise ValueError(f"不支持的文件格式: {ext}")

        loader = loader_class(file_path)
        documents = loader.load()

        # 2. 分块
        chunks = self.splitter.split_documents(documents)

        # 3. 添加元数据
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "kb_id": kb_id,
                "doc_id": doc_id,
                "chunk_index": i
            })

        # 4. 向量化并存储
        await self.vector_service.add_documents(chunks, kb_id)

        return len(chunks)
'''

print("\n" + "=" * 60)
print("第三部分：文档服务")
print("=" * 60)
print(DOCUMENT_SERVICE)


# ==================== 向量服务 ====================

VECTOR_SERVICE = '''
# app/services/vector_service.py
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from app.config import get_settings

settings = get_settings()

class VectorService:
    """向量检索服务"""

    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL
        )
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )

    def get_vectorstore(self, kb_id: str) -> QdrantVectorStore:
        """获取指定知识库的向量存储"""
        collection_name = f"kb_{kb_id}"
        return QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=self.embeddings
        )

    async def add_documents(self, documents: list, kb_id: str):
        """添加文档到向量库"""
        vectorstore = self.get_vectorstore(kb_id)
        await vectorstore.aadd_documents(documents)

    async def search(self, query: str, kb_id: str, top_k: int = None) -> list:
        """向量检索"""
        vectorstore = self.get_vectorstore(kb_id)
        results = await vectorstore.asimilarity_search(
            query, k=top_k or settings.TOP_K
        )
        return results
'''

print("\n" + "=" * 60)
print("第四部分：向量服务")
print("=" * 60)
print(VECTOR_SERVICE)


# ==================== RAG 服务 ====================

RAG_SERVICE = '''
# app/services/rag_service.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from app.config import get_settings

settings = get_settings()

class RAGService:
    """RAG 问答服务"""

    PROMPT_TEMPLATE = """基于以下上下文回答问题。如果无法从上下文中找到答案，请说明。

上下文：
{context}

问题：{question}

请用中文回答，并在适当的地方标注信息来源。"""

    def __init__(self, vector_service):
        self.vector_service = vector_service
        self.llm = ChatGoogleGenerativeAI(
            model=settings.CHAT_MODEL,
            temperature=0.7
        )
        self.prompt = ChatPromptTemplate.from_template(self.PROMPT_TEMPLATE)

    async def query(self, question: str, kb_id: str):
        """执行 RAG 查询"""
        # 1. 检索相关文档
        docs = await self.vector_service.search(question, kb_id)

        # 2. 构建上下文
        context = "\\n\\n".join([doc.page_content for doc in docs])

        # 3. 构建链
        chain = (
            {"context": lambda x: context, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

        # 4. 生成回答
        response = await chain.ainvoke(question)

        return {
            "answer": response,
            "sources": [
                {
                    "content": doc.page_content[:200],
                    "metadata": doc.metadata
                }
                for doc in docs[:3]
            ]
        }

    async def stream_query(self, question: str, kb_id: str):
        """流式 RAG 查询"""
        docs = await self.vector_service.search(question, kb_id)
        context = "\\n\\n".join([doc.page_content for doc in docs])

        chain = (
            {"context": lambda x: context, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

        async for chunk in chain.astream(question):
            yield chunk
'''

print("\n" + "=" * 60)
print("第五部分：RAG 服务")
print("=" * 60)
print(RAG_SERVICE)


# ==================== API 路由 ====================

API_ROUTES = '''
# app/api/v1/chat.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import RAGService
from app.dependencies import get_rag_service

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """问答接口"""
    result = await rag_service.query(
        question=request.question,
        kb_id=request.kb_id
    )
    return ChatResponse(**result)

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """流式问答接口"""
    async def generate():
        async for chunk in rag_service.stream_query(
            question=request.question,
            kb_id=request.kb_id
        ):
            yield f"data: {chunk}\\n\\n"
        yield "data: [DONE]\\n\\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


# app/api/v1/documents.py
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from app.services.document_service import DocumentService
from app.dependencies import get_document_service

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks,
    doc_service: DocumentService = Depends(get_document_service)
):
    """上传文档"""
    # 保存文件
    file_path = f"uploads/{kb_id}/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # 后台处理文档
    doc_id = str(uuid.uuid4())
    background_tasks.add_task(
        doc_service.process_document,
        file_path, kb_id, doc_id
    )

    return {"doc_id": doc_id, "status": "processing"}
'''

print("\n" + "=" * 60)
print("第六部分：API 路由")
print("=" * 60)
print(API_ROUTES)


# ==================== 主入口 ====================

MAIN_APP = """
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, knowledge_base, documents, chat
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(knowledge_base.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
"""

print("\n" + "=" * 60)
print("第七部分：主入口")
print("=" * 60)
print(MAIN_APP)


# ==================== Docker 配置 ====================

DOCKER_CONFIG = """
# docker-compose.yml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db/kb
      - REDIS_URL=redis://redis:6379
      - QDRANT_HOST=qdrant
    depends_on:
      - db
      - redis
      - qdrant

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=kb
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
"""

print("\n" + "=" * 60)
print("第八部分：Docker 配置")
print("=" * 60)
print(DOCKER_CONFIG)


print("\n" + "=" * 60)
print("课程完成！下一步：03-customer-service-design.py")
print("=" * 60)
