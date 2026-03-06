"""
Mini-Dify - 模型供应商 (Provider)
"""

from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class Provider(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "providers"

    name = Column(String(100), unique=True, nullable=False, comment="供应商名称")
    provider_type = Column(
        String(50), nullable=False, comment="类型: openai/anthropic/google/ollama"
    )
    api_key = Column(String, nullable=True, comment="加密存储的 API Key")
    base_url = Column(String(500), nullable=True, comment="自定义 Base URL")
    models = Column(JSONB, default=list, comment="可用模型列表")
    config = Column(JSONB, default=dict, comment="供应商特有配置")
    is_active = Column(Boolean, default=True, comment="是否启用")

    # 关系
    agents = relationship("Agent", back_populates="provider")

    def __repr__(self):
        return f"<Provider(name={self.name}, type={self.provider_type})>"
