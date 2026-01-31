"""
测试文本分割器
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from text_splitter import TextSplitter
from langchain.schema import Document


class TestTextSplitter:
    """文本分割器测试"""

    def test_split_text(self):
        """测试纯文本分割"""
        splitter = TextSplitter(chunk_size=100, chunk_overlap=20)

        text = "这是一段测试文本。" * 50  # 创建足够长的文本
        chunks = splitter.split_text(text)

        assert len(chunks) > 1
        assert all(len(chunk) <= 100 for chunk in chunks)

    def test_split_documents(self):
        """测试文档分割"""
        splitter = TextSplitter(chunk_size=100, chunk_overlap=20)

        docs = [
            Document(
                page_content="这是第一段很长的测试内容。" * 20,
                metadata={"source": "test1.txt"},
            ),
            Document(
                page_content="这是第二段很长的测试内容。" * 20,
                metadata={"source": "test2.txt"},
            ),
        ]

        chunks = splitter.split_documents(docs)

        assert len(chunks) > 2
        # 验证元数据保留
        assert all("source" in chunk.metadata for chunk in chunks)
        # 验证添加了分块索引
        assert all("chunk_index" in chunk.metadata for chunk in chunks)

    def test_short_text_no_split(self):
        """测试短文本不分割"""
        splitter = TextSplitter(chunk_size=500, chunk_overlap=100)

        text = "这是短文本"
        chunks = splitter.split_text(text)

        assert len(chunks) == 1

    def test_get_stats(self):
        """测试统计信息"""
        splitter = TextSplitter(chunk_size=100, chunk_overlap=20)

        docs = [
            Document(page_content="测试内容" * 30, metadata={}),
        ]

        chunks = splitter.split_documents(docs)
        stats = splitter.get_stats(chunks)

        assert "total_chunks" in stats
        assert "avg_length" in stats
        assert stats["total_chunks"] > 0

    def test_empty_input(self):
        """测试空输入"""
        splitter = TextSplitter()

        chunks = splitter.split_documents([])
        stats = splitter.get_stats(chunks)

        assert stats["total_chunks"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
