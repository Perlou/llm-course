"""
Mini-Dify - Agent、工具和关联表
"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    ForeignKey,
    Table,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP, ARRAY
from sqlalchemy.orm import relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


# Agent-工具 多对多关联表
agent_tools = Table(
    "agent_tools",
    Base.metadata,
    Column(
        "agent_id",
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tool_id",
        UUID(as_uuid=True),
        ForeignKey("tools.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Tool(UUIDMixin, Base):
    __tablename__ = "tools"

    name = Column(String(100), unique=True, nullable=False, comment="工具名称")
    description = Column(Text, nullable=True, comment="工具描述")
    tool_type = Column(String(20), nullable=False, comment="类型: builtin/custom")
    parameters = Column(JSONB, default=dict, comment="参数 Schema")
    code = Column(Text, nullable=True, comment="自定义工具代码")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )

    # 关系
    agents = relationship("Agent", secondary=agent_tools, back_populates="tools")

    def __repr__(self):
        return f"<Tool(name={self.name}, type={self.tool_type})>"


class Agent(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "agents"

    name = Column(String(200), nullable=False, comment="Agent 名称")
    description = Column(Text, nullable=True, comment="描述")
    system_prompt = Column(Text, nullable=False, comment="系统提示词")
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=True)
    model_name = Column(String(100), nullable=False, comment="模型名称")
    temperature = Column(Float, default=0.7, comment="温度")
    max_tokens = Column(Integer, default=2048, comment="最大 Token")
    strategy = Column(
        String(20), default="react", comment="策略: react/function_calling"
    )
    dataset_ids = Column(
        ARRAY(UUID(as_uuid=True)), default=list, comment="关联知识库 ID 数组"
    )

    # 关系
    provider = relationship("Provider", back_populates="agents")
    tools = relationship("Tool", secondary=agent_tools, back_populates="agents")

    def __repr__(self):
        return f"<Agent(name={self.name}, model={self.model_name})>"
