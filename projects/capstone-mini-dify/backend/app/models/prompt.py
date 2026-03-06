"""
Mini-Dify - Prompt 模板和版本
"""

from sqlalchemy import Column, String, Integer, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP, ARRAY
from sqlalchemy.orm import relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class Prompt(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "prompts"

    name = Column(String(200), nullable=False, comment="模板名称")
    description = Column(Text, nullable=True, comment="模板描述")
    system_prompt = Column(Text, nullable=False, comment="System Prompt")
    user_prompt = Column(Text, nullable=False, comment="User Prompt 模板")
    variables = Column(JSONB, default=list, comment="变量定义")
    tags = Column(ARRAY(String), default=list, comment="标签数组")
    current_version = Column(Integer, default=1, comment="当前版本号")

    # 关系
    versions = relationship(
        "PromptVersion", back_populates="prompt", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Prompt(name={self.name}, v{self.current_version})>"


class PromptVersion(UUIDMixin, Base):
    __tablename__ = "prompt_versions"

    prompt_id = Column(
        UUID(as_uuid=True), ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False
    )
    version = Column(Integer, nullable=False, comment="版本号")
    system_prompt = Column(Text, nullable=False)
    user_prompt = Column(Text, nullable=False)
    change_note = Column(String(500), nullable=True, comment="变更说明")
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )

    # 关系
    prompt = relationship("Prompt", back_populates="versions")

    def __repr__(self):
        return f"<PromptVersion(prompt_id={self.prompt_id}, v{self.version})>"
