"""
MediMind - 健康档案模型

健康档案和健康记录数据模型。
"""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Date, Numeric, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, Field
from enum import Enum

from src.models.base import Base


# ============ 枚举类型 ============


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class RecordType(str, Enum):
    BLOOD_PRESSURE = "blood_pressure"  # 血压
    BLOOD_SUGAR = "blood_sugar"  # 血糖
    HEART_RATE = "heart_rate"  # 心率
    WEIGHT = "weight"  # 体重
    TEMPERATURE = "temperature"  # 体温


# ============ SQLAlchemy 模型 ============


class HealthProfile(Base):
    """健康档案数据库模型"""

    __tablename__ = "health_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, index=True
    )
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    height_cm: Mapped[Optional[float]] = mapped_column(Numeric(5, 1), nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(Numeric(5, 1), nullable=True)
    blood_type: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    allergies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    medical_history: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class HealthRecord(Base):
    """健康记录数据库模型"""

    __tablename__ = "health_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    record_type: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[str] = mapped_column(String(100), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ============ Pydantic 模型 ============


class HealthProfileRequest(BaseModel):
    """健康档案请求"""

    gender: Optional[str] = Field(None, description="性别 (male/female)")
    birth_date: Optional[date] = Field(None, description="出生日期")
    height_cm: Optional[float] = Field(None, ge=50, le=300, description="身高 (cm)")
    weight_kg: Optional[float] = Field(None, ge=10, le=500, description="体重 (kg)")
    blood_type: Optional[str] = Field(None, description="血型")
    allergies: Optional[List[str]] = Field(None, description="过敏史")
    medical_history: Optional[List[str]] = Field(None, description="病史")


class HealthProfileResponse(BaseModel):
    """健康档案响应"""

    id: str
    user_id: str
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    blood_type: Optional[str] = None
    allergies: Optional[List[str]] = None
    medical_history: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HealthRecordRequest(BaseModel):
    """健康记录请求"""

    record_type: str = Field(..., description="记录类型")
    value: str = Field(..., description="数值")
    unit: Optional[str] = Field(None, description="单位")
    recorded_at: datetime = Field(..., description="记录时间")
    notes: Optional[str] = Field(None, description="备注")


class HealthRecordResponse(BaseModel):
    """健康记录响应"""

    id: str
    record_type: str
    value: str
    unit: Optional[str] = None
    recorded_at: datetime
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
