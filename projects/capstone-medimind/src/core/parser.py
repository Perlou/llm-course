"""
MediMind - 文档解析器

支持 Markdown、PDF 等格式的医学文档解析。
"""

import re
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from src.utils import log


@dataclass
class ParsedDocument:
    """解析后的文档"""
    id: str
    title: str
    content: str
    source: str
    file_type: str
    metadata: dict = None


class DocumentParser:
    """文档解析器"""

    def __init__(self):
        self.supported_types = [".md", ".txt", ".pdf"]

    def parse(self, file_path: str) -> Optional[ParsedDocument]:
        """
        解析文档
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析后的文档对象
        """
        path = Path(file_path)
        
        if not path.exists():
            log.warning(f"文件不存在: {file_path}")
            return None
        
        suffix = path.suffix.lower()
        
        if suffix in [".md", ".txt"]:
            return self._parse_markdown(path)
        elif suffix == ".pdf":
            return self._parse_pdf(path)
        else:
            log.warning(f"不支持的文件类型: {suffix}")
            return None

    def _parse_markdown(self, path: Path) -> ParsedDocument:
        """解析 Markdown 文件"""
        content = path.read_text(encoding="utf-8")
        
        # 提取标题（第一个 # 开头的行）
        title = path.stem
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
        
        # 清理 Markdown 语法，保留纯文本
        cleaned_content = self._clean_markdown(content)
        
        return ParsedDocument(
            id=f"doc_{path.stem}",
            title=title,
            content=cleaned_content,
            source=str(path),
            file_type="markdown",
            metadata={
                "filename": path.name,
                "size": path.stat().st_size,
            },
        )

    def _parse_pdf(self, path: Path) -> Optional[ParsedDocument]:
        """解析 PDF 文件"""
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(str(path))
            text_parts = []
            
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
            
            doc.close()
            
            content = "\n\n".join(text_parts)
            
            return ParsedDocument(
                id=f"doc_{path.stem}",
                title=path.stem,
                content=content,
                source=str(path),
                file_type="pdf",
                metadata={
                    "filename": path.name,
                    "pages": len(text_parts),
                },
            )
        except ImportError:
            log.warning("PDF 解析需要安装 PyMuPDF: pip install pymupdf")
            return None
        except Exception as e:
            log.error(f"PDF 解析失败: {e}")
            return None

    def _clean_markdown(self, text: str) -> str:
        """清理 Markdown 语法"""
        # 移除代码块
        text = re.sub(r"```[\s\S]*?```", "", text)
        # 移除行内代码
        text = re.sub(r"`[^`]+`", "", text)
        # 移除图片
        text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
        # 移除链接，保留文本
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        # 移除 HTML 注释
        text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
        # 移除水平线
        text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)
        # 清理标题标记，但保留文本
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
        # 移除加粗/斜体标记
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        # 清理多余空白
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        return text.strip()

    def parse_directory(self, dir_path: str) -> List[ParsedDocument]:
        """
        解析目录下的所有文档
        
        Args:
            dir_path: 目录路径
            
        Returns:
            文档列表
        """
        path = Path(dir_path)
        documents = []
        
        for file_path in path.rglob("*"):
            if file_path.suffix.lower() in self.supported_types:
                doc = self.parse(str(file_path))
                if doc:
                    documents.append(doc)
                    log.info(f"解析完成: {file_path.name}")
        
        log.info(f"共解析 {len(documents)} 个文档")
        return documents
