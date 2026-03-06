"""
Mini-Dify - 知识库和文档
"""

from sqlalchemy import Column, String, Integer, BigInteger, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class Dataset(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "datasets"

    name = Column(String(200), nullable=False, comment="知识库名称")
    description = Column(Text, nullable=True, comment="描述")
    embedding_model = Column(
        String(100), default="bge-large-zh", comment="Embedding 模型"
    )
    chunk_size = Column(Integer, default=500, comment="切分大小")
    chunk_overlap = Column(Integer, default=50, comment="切分重叠")
    document_count = Column(Integer, default=0, comment="文档数量")
    chunk_count = Column(Integer, default=0, comment="总切片数")
    retrieval_config = Column(JSONB, default=dict, comment="检索配置")

    # 关系
    documents = relationship(
        "Document", back_populates="dataset", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Dataset(name={self.name}, docs={self.document_count})>"


class Document(UUIDMixin, Base):
    __tablename__ = "documents"

    dataset_id = Column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(500), nullable=False, comment="文件名")
    file_path = Column(String(1000), nullable=True, comment="文件存储路径")
    file_type = Column(String(20), nullable=False, comment="文件类型: pdf/md/txt/docx")
    file_size = Column(BigInteger, nullable=True, comment="文件大小 (bytes)")
    chunk_count = Column(Integer, default=0, comment="切片数量")
    metadata_ = Column("metadata", JSONB, default=dict, comment="文档元数据")
    status = Column(
        String(20),
        default="pending",
        comment="状态: pending/processing/completed/failed",
    )
    error_msg = Column(Text, nullable=True, comment="处理失败时的错误信息")
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )

    # 关系
    dataset = relationship("Dataset", back_populates="documents")

    def __repr__(self):
        return f"<Document(name={self.name}, status={self.status})>"
