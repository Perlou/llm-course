"""
MediMind - RAG 单元测试
"""

import pytest
from pathlib import Path


class TestDocumentParser:
    """文档解析器测试"""

    def test_parse_markdown(self):
        """测试 Markdown 解析"""
        from src.core.parser import DocumentParser
        
        parser = DocumentParser()
        
        # 创建测试文件
        test_content = """# 测试文档

这是一个测试文档的内容。

## 第一节

一些测试文本。
"""
        test_file = Path("/tmp/test_doc.md")
        test_file.write_text(test_content)
        
        doc = parser.parse(str(test_file))
        
        assert doc is not None
        assert doc.title == "测试文档"
        assert "测试文档" in doc.content
        assert doc.file_type == "markdown"
        
        # 清理
        test_file.unlink()

    def test_parse_nonexistent_file(self):
        """测试解析不存在的文件"""
        from src.core.parser import DocumentParser
        
        parser = DocumentParser()
        doc = parser.parse("/nonexistent/file.md")
        
        assert doc is None


class TestChunker:
    """文本分块器测试"""

    def test_chunk_short_text(self):
        """测试短文本分块"""
        from src.core.chunker import Chunker
        
        chunker = Chunker(chunk_size=100, chunk_overlap=20)
        
        short_text = "这是一段很短的文本。"
        chunks = chunker.chunk_text(short_text)
        
        assert len(chunks) == 1
        assert chunks[0] == short_text

    def test_chunk_long_text(self):
        """测试长文本分块"""
        from src.core.chunker import Chunker
        
        chunker = Chunker(chunk_size=50, chunk_overlap=10)
        
        long_text = "这是一段很长的文本。" * 20
        chunks = chunker.chunk_text(long_text)
        
        assert len(chunks) > 1
        # 验证每个块的长度
        for chunk in chunks:
            assert len(chunk) <= 50 + 20  # chunk_size + some tolerance

    def test_chunk_document(self):
        """测试文档分块"""
        from src.core.chunker import Chunker
        
        chunker = Chunker(chunk_size=100, chunk_overlap=20)
        
        chunks = chunker.chunk_document(
            doc_id="test_doc",
            doc_title="测试文档",
            content="这是测试内容。" * 50,
            source="/test/path",
        )
        
        assert len(chunks) > 0
        assert all(c.doc_id == "test_doc" for c in chunks)
        assert all(c.doc_title == "测试文档" for c in chunks)


class TestPrompts:
    """Prompt 模板测试"""

    def test_health_qa_prompt_format(self):
        """测试健康问答 Prompt 格式化"""
        from src.core.prompts import HEALTH_QA_USER_PROMPT
        
        formatted = HEALTH_QA_USER_PROMPT.format(
            query="什么是高血压？",
            context="高血压是一种常见的慢性疾病...",
        )
        
        assert "什么是高血压" in formatted
        assert "高血压是一种常见的慢性疾病" in formatted

    def test_medical_disclaimer(self):
        """测试医学免责声明"""
        from src.core.prompts import MEDICAL_DISCLAIMER
        
        assert "免责声明" in MEDICAL_DISCLAIMER
        assert "仅供" in MEDICAL_DISCLAIMER


class TestRAGServiceIntegration:
    """RAG 服务集成测试"""

    @pytest.mark.skipif(
        True,  # 跳过需要依赖的测试
        reason="需要安装 sentence-transformers 和 chromadb"
    )
    def test_rag_query(self):
        """测试 RAG 查询"""
        from src.core.rag_service import RAGService
        
        service = RAGService()
        response = service.query("什么是高血压？")
        
        assert response.answer is not None
        assert response.conversation_id is not None

    def test_emergency_detection(self):
        """测试紧急情况检测"""
        from src.core.rag_service import RAGService
        
        service = RAGService()
        
        # 测试紧急关键词检测
        assert service._check_emergency("我胸痛很厉害")
        assert service._check_emergency("呼吸困难怎么办")
        assert not service._check_emergency("感冒了怎么办")


class TestAPIRoutes:
    """API 路由测试"""

    def test_drug_search_local(self):
        """测试药品本地搜索"""
        from src.api.routes.drug import get_drugs_data
        
        drugs = get_drugs_data()
        
        # 验证数据加载
        assert isinstance(drugs, list)
        if len(drugs) > 0:
            assert "id" in drugs[0]
            assert "name" in drugs[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
