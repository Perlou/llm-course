"""
MediMind - 向量检索器

从向量库中检索相关文档。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.utils import get_settings, log


@dataclass
class RetrievalResult:
    """检索结果"""
    id: str
    content: str
    score: float
    doc_title: str = ""
    source: str = ""
    metadata: Dict[str, Any] = None


class Retriever:
    """向量检索器"""

    def __init__(
        self,
        top_k: int = None,
        score_threshold: float = None,
    ):
        settings = get_settings()
        retrieval = settings.retrieval
        
        self.top_k = top_k or retrieval.top_k
        self.score_threshold = score_threshold or retrieval.score_threshold
        
        # 延迟导入以避免循环依赖
        self._embedder = None
        self._vector_store = None

    @property
    def embedder(self):
        if self._embedder is None:
            from src.core.embedder import get_embedder
            self._embedder = get_embedder()
        return self._embedder

    @property
    def vector_store(self):
        if self._vector_store is None:
            from src.core.vector_store import get_vector_store
            self._vector_store = get_vector_store()
        return self._vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = None,
        filter_type: Optional[str] = None,
    ) -> List[RetrievalResult]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter_type: 过滤类型（如 'drug', 'lab_index'）
            
        Returns:
            检索结果列表
        """
        top_k = top_k or self.top_k
        
        # 生成查询向量
        query_embedding = self.embedder.embed_query(query)
        
        # 构建过滤条件
        where = None
        if filter_type:
            where = {"type": filter_type}
        
        # 检索
        results = self.vector_store.search(
            query_embedding=query_embedding.tolist(),
            top_k=top_k,
            where=where,
        )
        
        # 转换为结果对象并过滤低分结果
        retrieval_results = []
        for result in results:
            score = result.get("score", 0)
            if score >= self.score_threshold:
                retrieval_results.append(RetrievalResult(
                    id=result["id"],
                    content=result["content"],
                    score=score,
                    doc_title=result.get("doc_title", ""),
                    source=result.get("source", ""),
                    metadata=result,
                ))
        
        log.debug(f"检索完成: 查询='{query[:50]}...', 结果数={len(retrieval_results)}")
        return retrieval_results

    def retrieve_for_health_qa(self, query: str) -> List[RetrievalResult]:
        """
        健康问答检索
        
        优先检索医学文档，同时也搜索药品和检验指标。
        """
        # 综合检索所有类型
        results = self.retrieve(query, top_k=self.top_k * 2)
        
        # 按分数排序并取 top_k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:self.top_k]

    def retrieve_drugs(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """检索药品信息"""
        return self.retrieve(query, top_k=top_k, filter_type="drug")

    def retrieve_lab_indices(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """检索检验指标信息"""
        return self.retrieve(query, top_k=top_k, filter_type="lab_index")


# 单例
_retriever = None


def get_retriever() -> Retriever:
    """获取检索器单例"""
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever
