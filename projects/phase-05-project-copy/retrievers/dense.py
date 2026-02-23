"""
稠密 (Dense) 向量检索通道
利用目前 Google 最新的 Embedding 生成技术将纯净短文本向量化之后，与开源免费的本地 ChromaDB 互动，从而获得超自然语言和长句匹配语法的近似匹配度。
"""

from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import chromadb

from config import config


class DenseRetriever:
    """基于纯数学语义相似度原理运行。"""

    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path=config.db_dir)
        self.collection_name = "enterprise_docs"

        # 装载或者寻找已经持久化存放于磁盘的数据池子
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name, metadata={"hnsw:space": "cosine"}
        )

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=config.embedding_model, google_api_key=config.google_api_key
        )

    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        启动与大规模数据库底层接口交互。
        返回的数据模型依旧统一对齐为结构化数组 List[Dict] 并在字典中赋予一个排名 Rank 用于接下来的 RRF (融合策略)。
        """
        if top_k is None:
            top_k = config.vector_top_k

        if self.collection.count() == 0:
            print("警告: 向量存储池子目前为空，将不会输出有效语义回答。")
            return []

        try:
            # 第一阶段，需要先把我们的找寻大目标化成密集表达的数字化数列空间座标映射
            query_embedding = self.embeddings.embed_query(query)

            # 开启 ChromaDB 自带底本索引
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )

            formatted_results = []
            if results and results["documents"] and results["documents"][0]:
                docs = results["documents"][0]
                metadatas = results["metadatas"][0]
                distances = results["distances"][0]

                for rank, (doc_text, metadata, dist) in enumerate(
                    zip(docs, metadatas, distances), 1
                ):
                    # ChromaDB 出于数学实现通常抛掷出欧几里得测距，或是正弦反向。针对它的模型机制。1减它刚好获得的是 相似分数(越大表示越雷同)
                    sim_score = 1.0 - dist

                    doc = Document(page_content=doc_text, metadata=metadata)
                    formatted_results.append(
                        {
                            "document": doc,
                            "score": sim_score,
                            "rank": rank,
                            "source": "dense",
                        }
                    )

            return formatted_results

        except Exception as e:
            print(f"语义向量化底层检索崩盘报错: {e}")
            return []
