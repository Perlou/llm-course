"""
Mini-Dify - 工作流
"""

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import Base, UUIDMixin, TimestampMixin


class Workflow(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "workflows"

    name = Column(String(200), nullable=False, comment="工作流名称")
    description = Column(Text, nullable=True, comment="描述")
    graph_data = Column(JSONB, nullable=False, comment="工作流图定义")
    status = Column(String(20), default="draft", comment="状态: draft/published")

    def __repr__(self):
        return f"<Workflow(name={self.name}, status={self.status})>"
