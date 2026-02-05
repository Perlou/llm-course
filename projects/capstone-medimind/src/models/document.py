"""
MediMind - 医学文档模型
"""

from typing import Optional

from sqlalchemy import String, Text, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class MedicalDocument(BaseModel):
    """医学文档模型"""
    __tablename__ = "medical_documents"
    
    # 文档基本信息
    title: Mapped[str] = mapped_column(String(255), comment="文档标题")
    content: Mapped[str] = mapped_column(Text, comment="文档内容")
    source: Mapped[Optional[str]] = mapped_column(String(255), comment="来源")
    category: Mapped[Optional[str]] = mapped_column(String(100), comment="分类")
    
    # 元数据
    file_path: Mapped[Optional[str]] = mapped_column(String(500), comment="文件路径")
    file_type: Mapped[Optional[str]] = mapped_column(String(50), comment="文件类型")
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, comment="分块数量")
    
    # 扩展数据
    metadata_: Mapped[Optional[dict]] = mapped_column(JSON, name="metadata", comment="扩展元数据")
    
    def __repr__(self):
        return f"<MedicalDocument(id={self.id}, title='{self.title[:30]}...')>"
