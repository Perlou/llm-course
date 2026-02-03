"""
MediMind - 工具函数
"""

import uuid
from datetime import datetime
from typing import Optional


def generate_id(prefix: str = "") -> str:
    """
    生成唯一 ID
    
    Args:
        prefix: ID 前缀，如 "doc_", "chat_", "drug_"
        
    Returns:
        格式为 {prefix}{短UUID} 的唯一ID
    """
    short_uuid = uuid.uuid4().hex[:12]
    return f"{prefix}{short_uuid}" if prefix else short_uuid


def get_timestamp() -> str:
    """获取当前时间戳字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 原文本
        max_length: 最大长度
        suffix: 截断后缀
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """
    清理文本（去除多余空白）
    
    Args:
        text: 原文本
        
    Returns:
        清理后的文本
    """
    import re
    # 替换多个空白为单个空格
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
