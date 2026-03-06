"""
Mini-Dify - 对话日志
"""

from sqlalchemy import Column, String, Integer, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP

from app.models.base import Base, UUIDMixin


class ConversationLog(UUIDMixin, Base):
    __tablename__ = "conversation_logs"

    app_id = Column(
        UUID(as_uuid=True), ForeignKey("apps.id", ondelete="CASCADE"), nullable=False
    )
    conversation_id = Column(UUID(as_uuid=True), nullable=False, comment="对话 ID")
    role = Column(String(20), nullable=False, comment="角色: user/assistant")
    content = Column(Text, nullable=False, comment="消息内容")
    provider_name = Column(String(100), nullable=True, comment="模型供应商")
    model_name = Column(String(100), nullable=True, comment="模型名称")
    input_tokens = Column(Integer, default=0, comment="输入 Token 数")
    output_tokens = Column(Integer, default=0, comment="输出 Token 数")
    latency_ms = Column(Integer, nullable=True, comment="响应延迟 (ms)")
    metadata_ = Column("metadata", JSONB, default=dict, comment="扩展数据")
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )

    # 关系
    app = relationship("App", back_populates="conversation_logs")

    def __repr__(self):
        return f"<ConversationLog(role={self.role}, tokens={self.input_tokens}+{self.output_tokens})>"
