"""
Mini-Dify - RAG 服务
文档解析 → 文本切分 → Embedding → Milvus 向量存储/检索
"""

import asyncio
from dataclasses import dataclass, field
from uuid import uuid4

from app.config import get_settings

settings = get_settings()


# ==================== Data Classes ====================


@dataclass
class TextChunk:
    content: str
    chunk_index: int
    document_id: str
    metadata: dict = field(default_factory=dict)


@dataclass
class RetrievalResult:
    content: str
    score: float
    document_id: str
    document_name: str = ""
    chunk_index: int = 0


# ==================== Document Parser ====================


class DocumentParser:
    """文档解析器：将文件转为纯文本"""

    SUPPORTED_TYPES = {"txt", "md", "pdf", "docx"}

    @classmethod
    async def parse(cls, file_path: str, file_type: str) -> str:
        """解析文件为纯文本"""
        file_type = file_type.lower()
        if file_type not in cls.SUPPORTED_TYPES:
            raise ValueError(f"不支持的文件类型: {file_type}")

        return await asyncio.to_thread(cls._parse_sync, file_path, file_type)

    @classmethod
    def _parse_sync(cls, file_path: str, file_type: str) -> str:
        if file_type in ("txt", "md"):
            return cls._parse_text(file_path)
        elif file_type == "pdf":
            return cls._parse_pdf(file_path)
        elif file_type == "docx":
            return cls._parse_docx(file_path)
        return ""

    @staticmethod
    def _parse_text(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    @staticmethod
    def _parse_pdf(file_path: str) -> str:
        """解析 PDF 文件"""
        try:
            import pdfplumber

            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            return "\n\n".join(text_parts)
        except ImportError:
            # 降级：尝试用 PyPDF2
            try:
                from PyPDF2 import PdfReader

                reader = PdfReader(file_path)
                return "\n\n".join(
                    page.extract_text() or "" for page in reader.pages
                )
            except ImportError:
                raise ImportError(
                    "需要安装 pdfplumber 或 PyPDF2 来解析 PDF 文件"
                )

    @staticmethod
    def _parse_docx(file_path: str) -> str:
        """解析 DOCX 文件"""
        try:
            from docx import Document as DocxDocument

            doc = DocxDocument(file_path)
            return "\n\n".join(para.text for para in doc.paragraphs if para.text)
        except ImportError:
            raise ImportError("需要安装 python-docx 来解析 DOCX 文件")


# ==================== Text Splitter ====================


class TextSplitter:
    """递归文本切分器"""

    SEPARATORS = ["\n\n", "\n", "。", "！", "？", ".", "!", "?", "；", ";", " "]

    @classmethod
    def split(
        cls, text: str, chunk_size: int = 500, chunk_overlap: int = 50
    ) -> list[str]:
        """将文本切分为 chunks"""
        if not text.strip():
            return []

        chunks = cls._recursive_split(text, cls.SEPARATORS, chunk_size)

        # 应用 overlap
        if chunk_overlap > 0 and len(chunks) > 1:
            overlapped = []
            for i, chunk in enumerate(chunks):
                if i > 0:
                    prev_tail = chunks[i - 1][-chunk_overlap:]
                    chunk = prev_tail + chunk
                overlapped.append(chunk)
            chunks = overlapped

        # 过滤空 chunks
        return [c.strip() for c in chunks if c.strip()]

    @classmethod
    def _recursive_split(
        cls, text: str, separators: list[str], chunk_size: int
    ) -> list[str]:
        if len(text) <= chunk_size:
            return [text]

        # 找第一个可用的分隔符
        separator = ""
        for sep in separators:
            if sep in text:
                separator = sep
                break

        if not separator:
            # 没有分隔符，硬切
            return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

        # 按分隔符切分
        parts = text.split(separator)
        chunks = []
        current = ""

        for part in parts:
            candidate = current + separator + part if current else part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                if len(part) > chunk_size:
                    # 递归用更细的分隔符
                    remaining_seps = separators[separators.index(separator) + 1 :]
                    if remaining_seps:
                        chunks.extend(
                            cls._recursive_split(part, remaining_seps, chunk_size)
                        )
                    else:
                        chunks.extend(
                            [part[i : i + chunk_size] for i in range(0, len(part), chunk_size)]
                        )
                    current = ""
                else:
                    current = part

        if current:
            chunks.append(current)

        return chunks


# ==================== Embedding Service ====================


class EmbeddingService:
    """Embedding 向量化服务"""

    _model = None

    @classmethod
    async def embed(cls, texts: list[str]) -> list[list[float]]:
        """将文本列表转为向量"""
        if settings.openai_api_key:
            return await cls._embed_openai(texts)
        return await cls._embed_local(texts)

    @classmethod
    async def _embed_openai(cls, texts: list[str]) -> list[list[float]]:
        """使用 OpenAI Embedding API"""
        from langchain_openai import OpenAIEmbeddings

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.openai_api_key,
        )
        return await asyncio.to_thread(embeddings.embed_documents, texts)

    @classmethod
    async def _embed_local(cls, texts: list[str]) -> list[list[float]]:
        """使用本地 sentence-transformers 模型"""
        if cls._model is None:
            from sentence_transformers import SentenceTransformer

            cls._model = SentenceTransformer(settings.embedding_model)
        vectors = await asyncio.to_thread(cls._model.encode, texts)
        return [v.tolist() for v in vectors]

    @classmethod
    async def get_dimension(cls) -> int:
        """获取 embedding 维度"""
        test_vec = await cls.embed(["test"])
        return len(test_vec[0])


# ==================== Milvus Vector Store ====================


class VectorStore:
    """Milvus 向量存储"""

    @classmethod
    def _get_connection_alias(cls) -> str:
        from pymilvus import connections

        alias = "default"
        try:
            connections.connect(
                alias=alias,
                host=settings.milvus_host,
                port=settings.milvus_port,
            )
        except Exception:
            pass  # 已连接
        return alias

    @classmethod
    async def create_collection(
        cls, collection_name: str, dimension: int = 1024
    ) -> None:
        """创建 Milvus Collection"""
        await asyncio.to_thread(cls._create_collection_sync, collection_name, dimension)

    @classmethod
    def _create_collection_sync(cls, collection_name: str, dimension: int) -> None:
        from pymilvus import (
            Collection,
            CollectionSchema,
            FieldSchema,
            DataType,
            utility,
        )

        cls._get_connection_alias()

        if utility.has_collection(collection_name):
            return

        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=36),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension),
        ]
        schema = CollectionSchema(fields=fields, description="Knowledge Base")
        collection = Collection(name=collection_name, schema=schema)
        collection.create_index(
            field_name="embedding",
            index_params={
                "index_type": "IVF_FLAT",
                "metric_type": "COSINE",
                "params": {"nlist": 128},
            },
        )

    @classmethod
    async def insert(
        cls,
        collection_name: str,
        chunks: list[TextChunk],
        embeddings: list[list[float]],
    ) -> None:
        """批量插入向量"""
        await asyncio.to_thread(
            cls._insert_sync, collection_name, chunks, embeddings
        )

    @classmethod
    def _insert_sync(
        cls,
        collection_name: str,
        chunks: list[TextChunk],
        embeddings: list[list[float]],
    ) -> None:
        from pymilvus import Collection

        cls._get_connection_alias()
        collection = Collection(name=collection_name)

        data = [
            [str(uuid4()) for _ in chunks],                    # id
            [c.content[:65530] for c in chunks],               # content
            [c.document_id for c in chunks],                   # document_id
            [c.chunk_index for c in chunks],                   # chunk_index
            embeddings,                                         # embedding
        ]
        collection.insert(data)
        collection.flush()

    @classmethod
    async def search(
        cls,
        collection_name: str,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict]:
        """向量检索"""
        return await asyncio.to_thread(
            cls._search_sync, collection_name, query_embedding, top_k
        )

    @classmethod
    def _search_sync(
        cls,
        collection_name: str,
        query_embedding: list[float],
        top_k: int,
    ) -> list[dict]:
        from pymilvus import Collection, utility

        cls._get_connection_alias()

        if not utility.has_collection(collection_name):
            return []

        collection = Collection(name=collection_name)
        collection.load()

        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param={"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit=top_k,
            output_fields=["content", "document_id", "chunk_index"],
        )

        hits = []
        for hit in results[0]:
            hits.append({
                "content": hit.entity.get("content", ""),
                "document_id": hit.entity.get("document_id", ""),
                "chunk_index": hit.entity.get("chunk_index", 0),
                "score": round(hit.score, 4),
            })
        return hits

    @classmethod
    async def delete_by_document(
        cls, collection_name: str, document_id: str
    ) -> None:
        """删除指定文档的所有向量"""
        await asyncio.to_thread(
            cls._delete_by_document_sync, collection_name, document_id
        )

    @classmethod
    def _delete_by_document_sync(
        cls, collection_name: str, document_id: str
    ) -> None:
        from pymilvus import Collection, utility

        cls._get_connection_alias()
        if not utility.has_collection(collection_name):
            return
        collection = Collection(name=collection_name)
        collection.delete(f'document_id == "{document_id}"')
        collection.flush()

    @classmethod
    async def drop_collection(cls, collection_name: str) -> None:
        """删除整个 Collection"""
        await asyncio.to_thread(cls._drop_collection_sync, collection_name)

    @classmethod
    def _drop_collection_sync(cls, collection_name: str) -> None:
        from pymilvus import utility

        cls._get_connection_alias()
        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)


# ==================== RAG Pipeline ====================


def get_collection_name(dataset_id: str) -> str:
    """知识库 ID -> Milvus Collection 名称"""
    return f"kb_{str(dataset_id).replace('-', '_')}"


async def process_document(
    file_path: str,
    file_type: str,
    document_id: str,
    dataset_id: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> int:
    """
    完整文档处理管线：解析 → 切分 → 嵌入 → 存入 Milvus
    返回切片数量
    """
    # 1. 解析文档
    text = await DocumentParser.parse(file_path, file_type)
    if not text.strip():
        return 0

    # 2. 文本切分
    chunk_texts = TextSplitter.split(text, chunk_size, chunk_overlap)
    if not chunk_texts:
        return 0

    chunks = [
        TextChunk(content=ct, chunk_index=i, document_id=document_id)
        for i, ct in enumerate(chunk_texts)
    ]

    # 3. Embedding
    embeddings = await EmbeddingService.embed(chunk_texts)
    dimension = len(embeddings[0])

    # 4. 确保 Milvus Collection 存在
    collection_name = get_collection_name(dataset_id)
    await VectorStore.create_collection(collection_name, dimension)

    # 5. 插入向量
    await VectorStore.insert(collection_name, chunks, embeddings)

    return len(chunks)


async def retrieve(
    dataset_id: str,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """
    向量检索
    """
    collection_name = get_collection_name(dataset_id)

    # Embed query
    query_embeddings = await EmbeddingService.embed([query])
    query_vec = query_embeddings[0]

    # Search
    results = await VectorStore.search(collection_name, query_vec, top_k)
    return results
