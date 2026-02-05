"""
MediMind - 药品模型
"""

from typing import Optional, List

from sqlalchemy import String, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class Drug(BaseModel):
    """药品信息模型"""
    __tablename__ = "drugs"
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(255), comment="药品名称")
    generic_name: Mapped[Optional[str]] = mapped_column(String(255), comment="通用名")
    brand_names: Mapped[Optional[List[str]]] = mapped_column(JSON, comment="商品名列表")
    
    # 分类
    category: Mapped[Optional[str]] = mapped_column(String(100), comment="药品分类")
    is_otc: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否OTC")
    is_prescription: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否处方药")
    
    # 详细信息
    indications: Mapped[Optional[str]] = mapped_column(Text, comment="适应症")
    dosage: Mapped[Optional[str]] = mapped_column(Text, comment="用法用量")
    side_effects: Mapped[Optional[str]] = mapped_column(Text, comment="不良反应")
    contraindications: Mapped[Optional[str]] = mapped_column(Text, comment="禁忌")
    interactions: Mapped[Optional[str]] = mapped_column(Text, comment="药物相互作用")
    precautions: Mapped[Optional[str]] = mapped_column(Text, comment="注意事项")
    
    # 规格信息
    specifications: Mapped[Optional[str]] = mapped_column(String(255), comment="规格")
    manufacturer: Mapped[Optional[str]] = mapped_column(String(255), comment="生产厂家")
    approval_number: Mapped[Optional[str]] = mapped_column(String(100), comment="批准文号")
    
    # 向量嵌入标识
    has_embedding: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否已嵌入")
    
    def __repr__(self):
        return f"<Drug(id={self.id}, name='{self.name}')>"
