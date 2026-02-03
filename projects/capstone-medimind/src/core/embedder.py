"""
MediMind - 向量嵌入器

使用 sentence-transformers 生成文本向量嵌入。
"""

from typing import List, Union, TYPE_CHECKING

from src.utils import get_settings, log

if TYPE_CHECKING:
    import numpy as np


class Embedder:
    """向量嵌入器"""

    def __init__(
        self,
        model_name: str = None,
        device: str = None,
    ):
        settings = get_settings()
        embedding = settings.embedding
        
        self.model_name = model_name or embedding.model
        self.device = device or embedding.device
        self.model = None
        self._dimension = None

    def _load_model(self):
        """延迟加载模型"""
        if self.model is not None:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            
            log.info(f"加载嵌入模型: {self.model_name}")
            
            # 确定设备
            device = self._get_device()
            
            self.model = SentenceTransformer(
                self.model_name,
                device=device,
            )
            self._dimension = self.model.get_sentence_embedding_dimension()
            
            log.info(f"嵌入模型加载完成，维度: {self._dimension}，设备: {device}")
            
        except Exception as e:
            log.error(f"加载嵌入模型失败: {e}")
            raise

    def _get_device(self) -> str:
        """获取计算设备"""
        if self.device != "auto":
            return self.device
        
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass
        
        return "cpu"

    def embed(self, texts: Union[str, List[str]]) -> "np.ndarray":
        """
        生成文本向量嵌入
        
        Args:
            texts: 单个文本或文本列表
            
        Returns:
            嵌入向量 (numpy array)
        """
        self._load_model()
        
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,  # L2 归一化
            show_progress_bar=len(texts) > 100,
            batch_size=32,
        )
        
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """嵌入查询文本"""
        return self.embed(query)[0]

    def embed_documents(self, documents: List[str]) -> np.ndarray:
        """嵌入文档列表"""
        return self.embed(documents)

    @property
    def dimension(self) -> int:
        """获取嵌入维度"""
        self._load_model()
        return self._dimension


# 单例
_embedder = None


def get_embedder() -> Embedder:
    """获取嵌入器单例"""
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder
