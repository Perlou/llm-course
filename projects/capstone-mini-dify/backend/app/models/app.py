"""
Mini-Dify - 应用和 API 密钥
"""

from sqlalchemy import Column, String, Boolean, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class App(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "apps"

    name = Column(String(200), nullable=False, comment="应用名称")
    description = Column(Text, nullable=True, comment="描述")
    app_type = Column(
        String(20), nullable=False, comment="类型: chatbot/completion/workflow"
    )
    config = Column(JSONB, nullable=False, comment="应用配置")
    is_published = Column(Boolean, default=False, comment="是否已发布")

    # 关系
    api_keys = relationship(
        "AppApiKey", back_populates="app", cascade="all, delete-orphan"
    )
    conversation_logs = relationship(
        "ConversationLog", back_populates="app", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<App(name={self.name}, type={self.app_type})>"


class AppApiKey(UUIDMixin, Base):
    __tablename__ = "app_api_keys"

    app_id = Column(
        UUID(as_uuid=True), ForeignKey("apps.id", ondelete="CASCADE"), nullable=False
    )
    key_prefix = Column(String(10), nullable=False, comment="Key 前缀")
    key_hash = Column(String(255), nullable=False, unique=True, comment="Key 哈希")
    name = Column(String(100), nullable=True, comment="Key 名称")
    is_active = Column(Boolean, default=True, comment="是否启用")
    last_used = Column(TIMESTAMP(timezone=True), nullable=True, comment="最后使用时间")
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )

    # 关系
    app = relationship("App", back_populates="api_keys")

    def __repr__(self):
        return f"<AppApiKey(prefix={self.key_prefix}, active={self.is_active})>"
