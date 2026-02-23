"""
核心配置管理模块
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """企业搜索引擎架构配置 (V2)"""

    # API 密钥配置
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")

    # 调用的模型资源
    llm_model: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")

    # 检索条数与参数限制
    bm25_top_k: int = int(os.getenv("BM25_TOP_K", "20"))
    vector_top_k: int = int(os.getenv("VECTOR_TOP_K", "20"))
    fusion_k: int = int(os.getenv("FUSION_K", "60"))  # 用于融合算法 RRF 的常量
    rerank_top_n: int = int(os.getenv("RERANK_TOP_N", "5"))

    # 文档切块策略 (父子文档机制 Parent-Child)
    parent_chunk_size: int = 1500
    parent_chunk_overlap: int = 200
    child_chunk_size: int = 300
    child_chunk_overlap: int = 50

    # 数据持久化与缓存路径
    base_dir: str = os.path.dirname(os.path.abspath(__file__))
    docs_dir: str = os.path.join(base_dir, "docs")
    data_dir: str = os.path.join(base_dir, "data")
    db_dir: str = os.path.join(data_dir, "chroma_db")
    store_dir: str = os.path.join(data_dir, "doc_store")

    # 重排器配置
    # 使用轻量级但效果极佳的多语言重排模型 bge-reranker-base
    reranker_model: str = "BAAI/bge-reranker-base"

    def validate(self):
        """Validates critical configurations at startup."""
        if not self.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY must be set in the environment or .env file."
            )

        # 确保系统需要的基础目录已存在
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.db_dir, exist_ok=True)
        os.makedirs(self.store_dir, exist_ok=True)


config = Config()
