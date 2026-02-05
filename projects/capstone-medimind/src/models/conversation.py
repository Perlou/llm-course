"""
MediMind - 对话模型
"""

from typing import Optional, List

from sqlalchemy import String, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from .base import BaseModel


class MessageRole(enum.Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationType(enum.Enum):
    """对话类型"""
    HEALTH_QA = "health_qa"     # 健康问答
    DRUG_QUERY = "drug_query"   # 药品查询
    TRIAGE = "triage"           # 智能导诊


class Conversation(BaseModel):
    """对话会话模型"""
    __tablename__ = "conversations"
    
    # 会话信息
    type: Mapped[str] = mapped_column(
        String(50),
        default=ConversationType.HEALTH_QA.value,
        comment="对话类型"
    )
    title: Mapped[Optional[str]] = mapped_column(String(255), comment="对话标题")
    
    # 状态
    is_complete: Mapped[bool] = mapped_column(default=False, comment="是否完成")
    
    # 元数据（如导诊收集的症状信息）
    context: Mapped[Optional[dict]] = mapped_column(JSON, comment="对话上下文")
    
    # 消息关联
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, type='{self.type}')>"


class Message(BaseModel):
    """对话消息模型"""
    __tablename__ = "messages"
    
    # 关联
    conversation_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        comment="对话 ID"
    )
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages"
    )
    
    # 消息内容
    role: Mapped[str] = mapped_column(
        String(20),
        default=MessageRole.USER.value,
        comment="角色"
    )
    content: Mapped[str] = mapped_column(Text, comment="消息内容")
    
    # 元数据
    sources: Mapped[Optional[List[dict]]] = mapped_column(JSON, comment="引用来源")
    tokens: Mapped[Optional[int]] = mapped_column(comment="token 数量")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}')>"
