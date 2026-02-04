"""
MediMind - 对话管理服务

提供对话历史的持久化和管理功能。
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from src.db import get_database
from src.models import Conversation, Message
from src.utils import log, generate_id


class ConversationService:
    """对话管理服务"""
    
    def __init__(self):
        self.db = get_database()
    
    def create_conversation(
        self,
        conversation_type: str = "health_qa",
        title: Optional[str] = None,
    ) -> Conversation:
        """
        创建新对话
        
        Args:
            conversation_type: 对话类型 (health_qa, triage, etc.)
            title: 对话标题
            
        Returns:
            新创建的对话对象
        """
        with self.db.get_session() as session:
            conversation = Conversation(
                id=generate_id("conv_"),
                type=conversation_type,
                title=title or f"对话 - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                is_complete=False,
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            
            log.info(f"创建对话: {conversation.id}")
            return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """获取对话"""
        with self.db.get_session() as session:
            return session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        sources: Optional[List[Dict[str, Any]]] = None,
    ) -> Message:
        """
        添加消息到对话
        
        Args:
            conversation_id: 对话 ID
            role: 角色 (user/assistant)
            content: 消息内容
            sources: 来源信息（可选）
            
        Returns:
            新创建的消息对象
        """
        with self.db.get_session() as session:
            # 检查对话是否存在
            conversation = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if not conversation:
                # 自动创建对话
                conversation = Conversation(
                    id=conversation_id,
                    type="health_qa",
                    title=f"对话 - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    is_complete=False,
                )
                session.add(conversation)
                session.flush()
            
            message = Message(
                id=generate_id("msg_"),
                conversation_id=conversation_id,
                role=role,
                content=content,
                sources=sources,
            )
            session.add(message)
            session.commit()
            session.refresh(message)
            
            return message
    
    def get_messages(
        self,
        conversation_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        获取对话消息列表
        
        Args:
            conversation_id: 对话 ID
            limit: 最大返回数量
            
        Returns:
            消息列表
        """
        with self.db.get_session() as session:
            messages = session.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.asc()).limit(limit).all()
            
            return [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "sources": msg.sources,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                }
                for msg in messages
            ]
    
    def get_recent_conversations(
        self,
        limit: int = 20,
        conversation_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取最近的对话列表
        
        Args:
            limit: 最大返回数量
            conversation_type: 对话类型筛选
            
        Returns:
            对话列表
        """
        with self.db.get_session() as session:
            query = session.query(Conversation)
            
            if conversation_type:
                query = query.filter(Conversation.type == conversation_type)
            
            conversations = query.order_by(
                Conversation.created_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    "id": conv.id,
                    "type": conv.type,
                    "title": conv.title,
                    "is_complete": conv.is_complete,
                    "created_at": conv.created_at.isoformat() if conv.created_at else None,
                }
                for conv in conversations
            ]
    
    def mark_complete(self, conversation_id: str) -> bool:
        """标记对话为已完成"""
        with self.db.get_session() as session:
            conversation = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if conversation:
                conversation.is_complete = True
                session.commit()
                return True
            return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """删除对话（级联删除消息）"""
        with self.db.get_session() as session:
            conversation = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if conversation:
                session.delete(conversation)
                session.commit()
                log.info(f"删除对话: {conversation_id}")
                return True
            return False


# 单例
_conversation_service: ConversationService = None


def get_conversation_service() -> ConversationService:
    """获取对话服务单例"""
    global _conversation_service
    if _conversation_service is None:
        _conversation_service = ConversationService()
    return _conversation_service
