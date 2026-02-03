"""
MediMind - 文本分块器

医学文档特化的分块策略。
"""

from typing import List
from dataclasses import dataclass

from src.utils import get_settings, log


@dataclass
class TextChunk:
    """文本块"""
    id: str
    content: str
    doc_id: str
    doc_title: str
    source: str
    chunk_index: int
    metadata: dict = None


class Chunker:
    """文本分块器"""

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        separators: List[str] = None,
    ):
        settings = get_settings()
        chunking = settings.chunking
        
        self.chunk_size = chunk_size or chunking.chunk_size
        self.chunk_overlap = chunk_overlap or chunking.chunk_overlap
        self.separators = separators or chunking.separators

    def chunk_text(self, text: str) -> List[str]:
        """
        将文本分块
        
        Args:
            text: 原始文本
            
        Returns:
            文本块列表
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            # 确定当前块的结束位置
            end_pos = min(current_pos + self.chunk_size, len(text))
            
            # 如果不是最后一块，尝试在分隔符处断开
            if end_pos < len(text):
                best_break = self._find_best_break(
                    text, current_pos, end_pos
                )
                if best_break > current_pos:
                    end_pos = best_break
            
            # 提取当前块
            chunk = text[current_pos:end_pos].strip()
            if chunk:
                chunks.append(chunk)
            
            # 计算下一块的起始位置（考虑重叠）
            current_pos = end_pos - self.chunk_overlap
            if current_pos <= 0 and end_pos < len(text):
                current_pos = end_pos  # 避免死循环
        
        return chunks

    def _find_best_break(
        self, 
        text: str, 
        start: int, 
        end: int
    ) -> int:
        """在指定范围内找到最佳分隔点"""
        best_pos = end
        
        # 按分隔符优先级查找
        for sep in self.separators:
            # 从后往前查找分隔符
            pos = text.rfind(sep, start, end)
            if pos > start:
                # 分隔符后移动到分隔符之后
                best_pos = pos + len(sep)
                break
        
        return best_pos

    def chunk_document(
        self,
        doc_id: str,
        doc_title: str,
        content: str,
        source: str,
        metadata: dict = None,
    ) -> List[TextChunk]:
        """
        对文档进行分块
        
        Args:
            doc_id: 文档 ID
            doc_title: 文档标题
            content: 文档内容
            source: 来源
            metadata: 元数据
            
        Returns:
            分块列表
        """
        text_chunks = self.chunk_text(content)
        
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            chunk = TextChunk(
                id=f"{doc_id}_chunk_{i:03d}",
                content=chunk_text,
                doc_id=doc_id,
                doc_title=doc_title,
                source=source,
                chunk_index=i,
                metadata={
                    **(metadata or {}),
                    "chunk_index": i,
                    "total_chunks": len(text_chunks),
                },
            )
            chunks.append(chunk)
        
        log.debug(f"文档 '{doc_title}' 分块完成，共 {len(chunks)} 个块")
        return chunks
