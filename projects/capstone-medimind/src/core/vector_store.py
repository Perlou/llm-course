"""
MediMind - 向量存储

使用 Chroma 作为向量数据库。
"""

from typing import List, Optional, Dict, Any
from pathlib import Path

from src.utils import get_settings, log


class VectorStore:
    """Chroma 向量存储"""

    def __init__(
        self,
        collection_name: str = "medical_knowledge",
        persist_dir: str = None,
    ):
        settings = get_settings()
        
        self.collection_name = collection_name
        self.persist_dir = persist_dir or settings.chroma_persist_dir
        self.client = None
        self.collection = None
        self._init_client()

    def _init_client(self):
        """初始化 Chroma 客户端"""
        try:
            import chromadb
            
            persist_path = Path(self.persist_dir)
            persist_path.mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(path=str(persist_path))
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            
            log.info(f"Chroma 向量库已初始化: {self.collection_name}")
            log.info(f"当前文档数量: {self.collection.count()}")
            
        except Exception as e:
            log.error(f"初始化 Chroma 失败: {e}")
            raise

    def add(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        添加文档到向量库
        
        Args:
            ids: 文档 ID 列表
            embeddings: 嵌入向量列表
            documents: 文档内容列表
            metadatas: 元数据列表
        """
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        log.info(f"已添加 {len(ids)} 个文档到向量库")

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        搜索相似文档
        
        Args:
            query_embedding: 查询向量
            top_k: 返回结果数量
            where: 过滤条件
            
        Returns:
            搜索结果列表
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
        )
        
        chunks = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                chunk = {
                    "id": doc_id,
                    "content": results["documents"][0][i] if results["documents"] else "",
                    "score": 1 - results["distances"][0][i] if results["distances"] else 0,
                }
                if results["metadatas"] and results["metadatas"][0]:
                    chunk.update(results["metadatas"][0][i])
                chunks.append(chunk)
        
        return chunks

    def delete(self, ids: List[str]):
        """删除文档"""
        self.collection.delete(ids=ids)
        log.info(f"已删除 {len(ids)} 个文档")

    def count(self) -> int:
        """获取文档数量"""
        return self.collection.count()

    def clear(self):
        """清空集合"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        log.info("向量库已清空")


# 单例
_vector_store = None


def get_vector_store() -> VectorStore:
    """获取向量存储单例"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
