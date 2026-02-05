"""
MediMind - 配置管理

基于 Pydantic Settings 的配置管理，支持环境变量和 YAML 配置文件。
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


class DatabaseSettings(BaseSettings):
    """数据库配置"""

    url: str = Field(
        default="sqlite:///./data/medimind.db", description="数据库连接 URL"
    )
    pool_size: int = Field(default=5, description="连接池大小")
    max_overflow: int = Field(default=10, description="最大溢出连接数")


class EmbeddingSettings(BaseSettings):
    """嵌入模型配置"""

    model: str = Field(default="BAAI/bge-large-zh-v1.5", description="嵌入模型名称")
    device: str = Field(default="auto", description="设备: auto, cpu, cuda")
    batch_size: int = Field(default=32, description="批处理大小")


class LLMSettings(BaseSettings):
    """LLM 配置"""

    provider: str = Field(default="gemini", description="LLM 提供商: gemini, ollama")
    gemini_model: str = Field(default="gemini-2.0-flash", description="Gemini 模型")
    ollama_model: str = Field(default="qwen2.5:7b", description="Ollama 模型")
    ollama_host: str = Field(
        default="http://localhost:11434", description="Ollama 服务地址"
    )
    temperature: float = Field(default=0.7, description="生成温度")
    max_tokens: int = Field(default=2048, description="最大 token 数")


class ChunkingSettings(BaseSettings):
    """文本分块配置"""

    chunk_size: int = Field(default=500, description="分块大小")
    chunk_overlap: int = Field(default=100, description="分块重叠")
    separators: list = Field(
        default=["\n\n", "\n", "。", "；", "！", "？"], description="分隔符列表"
    )


class RetrievalSettings(BaseSettings):
    """检索配置"""

    top_k: int = Field(default=5, description="返回结果数量")
    score_threshold: float = Field(default=0.5, description="最小相似度分数")
    min_score: float = Field(default=0.5, description="最小相似度分数（别名）")
    rerank: bool = Field(default=False, description="是否重排序")


class AmapSettings(BaseSettings):
    """高德地图 API 配置"""

    api_key: Optional[str] = Field(default=None, description="高德地图 API Key")
    base_url: str = Field(
        default="https://restapi.amap.com/v3", description="API 基础 URL"
    )
    poi_types: str = Field(default="090100|090200", description="POI 类型：医院|诊所")
    search_radius: int = Field(default=5000, description="搜索半径（米）")


class Settings(BaseSettings):
    """MediMind 应用配置"""

    model_config = SettingsConfigDict(
        env_prefix="MEDIMIND_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用配置
    app_name: str = Field(default="MediMind", description="应用名称")
    app_version: str = Field(default="0.1.0", description="应用版本")
    app_env: str = Field(default="development", alias="APP_ENV", description="环境")
    debug: bool = Field(default=True, alias="DEBUG", description="调试模式")

    # API Keys
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    amap_api_key: Optional[str] = Field(default=None, alias="AMAP_API_KEY")

    # LLM 切换
    use_ollama: bool = Field(default=False, alias="USE_OLLAMA")

    # 数据目录
    data_dir: str = Field(default="./data", description="数据目录")
    chroma_persist_dir: str = Field(
        default="./data/chroma_index", description="Chroma 持久化目录"
    )

    # 日志
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # 子配置
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    chunking: ChunkingSettings = Field(default_factory=ChunkingSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    amap: AmapSettings = Field(default_factory=AmapSettings)

    @property
    def database_url(self) -> str:
        """获取数据库 URL（便捷属性）"""
        return self.database.url

    @property
    def gemini(self):
        """获取 Gemini 配置"""

        class GeminiConfig:
            def __init__(self, settings):
                self.model = settings.llm.gemini_model
                self.temperature = settings.llm.temperature
                self.max_tokens = settings.llm.max_tokens

        return GeminiConfig(self)

    @property
    def ollama(self):
        """获取 Ollama 配置"""

        class OllamaConfig:
            def __init__(self, settings):
                self.model = settings.llm.ollama_model
                self.base_url = settings.llm.ollama_host
                self.temperature = settings.llm.temperature

        return OllamaConfig(self)

    @classmethod
    def from_yaml(cls, config_path: str = "configs/config.yaml") -> "Settings":
        """从 YAML 文件加载配置"""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                yaml_config = yaml.safe_load(f)
                # 合并 YAML 配置和环境变量
                return cls(**yaml_config) if yaml_config else cls()
        return cls()


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
