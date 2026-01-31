"""
配置管理模块
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """应用配置"""

    # API 配置
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "")

    # 模型配置
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # RAG 参数
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    top_k: int = int(os.getenv("TOP_K", "5"))

    # 路径配置
    docs_dir: str = os.path.join(os.path.dirname(__file__), "docs")
    data_dir: str = os.path.join(os.path.dirname(__file__), "data")
    collection_name: str = "knowledge_base"

    def validate(self) -> bool:
        """验证配置"""
        if not self.openai_api_key:
            print("❌ 错误: 请设置 OPENAI_API_KEY 环境变量")
            return False
        return True


# 全局配置实例
config = Config()
