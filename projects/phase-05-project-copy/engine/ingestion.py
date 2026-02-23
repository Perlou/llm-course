"""
企业解析引擎核心
负责处理文档并将它们规范化切分为父子 (Parent-Child) 结构片段。
"""

import os
import uuid
from typing import List, Dict, Any

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config import config


class DocumentIngestor:
    """
    负责读取原始文档并将其拆分为大段 (Parent) 和精细段 (Child) 。
    Parent Node (父节点): 用于提供给 LLM 具有完整上下文的较段文本（例如：1500 Tokens）。
    Child Node (子节点): 细粒度的短文本（例如：300 Tokens），专门用于向量/BM25的高精度检索召回。
    """

    def __init__(self):
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.parent_chunk_size,
            chunk_overlap=config.parent_chunk_overlap,
        )
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.child_chunk_size,
            chunk_overlap=config.child_chunk_overlap,
        )

    def load_documents(self, directory: str) -> List[Document]:
        """批量加载指定目录下所有支持格式的文档"""
        documents = []
        if not os.path.exists(directory):
            return documents

        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if not os.path.isfile(file_path):
                continue

            try:
                if filename.endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                    documents.extend(loader.load())
                elif filename.endswith(".md"):
                    loader = UnstructuredMarkdownLoader(file_path)
                    documents.extend(loader.load())
                elif filename.endswith(".txt"):
                    loader = TextLoader(file_path, encoding="utf-8")
                    documents.extend(loader.load())
                else:
                    print(f"不支持的文件格式，跳过加载: {filename}")
            except Exception as e:
                print(f"读取文件发生错误 {filename}: {e}")

        return documents

    def ingest(self, directory: str) -> Dict[str, Any]:
        """
        主执行流程: 读取 -> 切分为父节点 -> 在父节点基础上切分为子节点。
        返回字典结构:
        - `parents`: 父级文档对象列表
        - `children`: 子级文档对象列表 (附带有父级ID parent_id)
        """
        raw_docs = self.load_documents(directory)
        if not raw_docs:
            print("警告: 数据目录中未找到任何需处理的文档资料。")
            return {"parents": [], "children": []}

        # 生成父层级文档切片
        parent_docs = self.parent_splitter.split_documents(raw_docs)

        final_parents = []
        final_children = []

        for p_doc in parent_docs:
            # 赋予每一个父节点全局唯一的 ID 标识
            parent_id = str(uuid.uuid4())
            p_doc.metadata["doc_id"] = parent_id
            final_parents.append(p_doc)

            # 在该父节点的文本范围内，进一步切分生成子节点片段
            child_docs = self.child_splitter.split_documents([p_doc])
            for c_doc in child_docs:
                # 子节点继承原元数据，同时明确绑定其溯源父节点的 ID
                child_metadata = c_doc.metadata.copy()
                child_metadata["parent_id"] = parent_id
                child_metadata["chunk_type"] = "child"

                # 创建新的子节点对象
                final_child = Document(
                    page_content=c_doc.page_content, metadata=child_metadata
                )
                final_children.append(final_child)

        return {"parents": final_parents, "children": final_children}
