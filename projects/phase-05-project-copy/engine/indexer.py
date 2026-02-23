"""
数据库索引引擎
管理向量数据库 Chroma (用于存放用于召回的子切片) 和本地 KV 存储 (用于存放具有丰富上下文的父切片)
"""

import os
import json
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import chromadb

from config import config


class DocumentIndexer:
    def __init__(self):
        # 1. 挂载持久化向量数据库
        self.chroma_client = chromadb.PersistentClient(path=config.db_dir)
        self.collection_name = "enterprise_docs"
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name, metadata={"hnsw:space": "cosine"}
        )

        # 2. 实例化最新的嵌入向量模型
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=config.embedding_model, google_api_key=config.google_api_key
        )

        # 3. 设置本地的 Key-Value 字典存储，用于存放父段落文本
        self.parent_store_path = os.path.join(config.store_dir, "parent_store.json")
        self.parent_store = self._load_parent_store()

    def _load_parent_store(self) -> Dict[str, dict]:
        if os.path.exists(self.parent_store_path):
            with open(self.parent_store_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_parent_store(self):
        with open(self.parent_store_path, "w", encoding="utf-8") as f:
            json.dump(self.parent_store, f, ensure_ascii=False, indent=2)

    def index(self, parents: List[Document], children: List[Document]):
        """执行双写策略：同时存入父级 KV 存储和子级向量库。"""

        # 1. 存储完整的长文本到 KV 数据库中
        print(f"正在将 {len(parents)} 个父级全文段落封存入本地 KV 存储...")
        for p in parents:
            doc_id = p.metadata.get("doc_id")
            if doc_id:
                self.parent_store[doc_id] = {
                    "page_content": p.page_content,
                    "metadata": p.metadata,
                }
        self._save_parent_store()

        # 2. 对作为检索单元的子部分进行向量化计算并灌库
        if not children:
            print("未能找到准备构建索引的子节点。")
            return

        print(f"正在将 {len(children)} 个短切片片段计算向量并写入 ChromaDB...")
        texts = [c.page_content for c in children]
        metadatas = [c.metadata for c in children]
        ids = [
            str(i)
            for i in range(
                self.collection.count(), self.collection.count() + len(children)
            )
        ]

        # API 批量化并发控制措施 (兼容限流)
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            batch_metadatas = metadatas[i : i + batch_size]
            batch_ids = ids[i : i + batch_size]

            # 使用模型进行密集表征提取
            try:
                batch_embeddings = self.embeddings.embed_documents(batch_texts)

                self.collection.add(
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    documents=batch_texts,
                    metadatas=batch_metadatas,
                )
            except Exception as e:
                print(f"向数据库批次灌入数据时发生错误 {i}-{i + batch_size}: {e}")

        print("✔ 数据入库构建圆满完成。")

    def get_parent(self, parent_id: str) -> Document:
        """从 KV 存储中取回原始的长篇父节点信息"""
        data = self.parent_store.get(parent_id)
        if data:
            return Document(
                page_content=data["page_content"], metadata=data["metadata"]
            )
        return None
