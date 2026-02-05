"""
MediMind - 提醒数据模型

慢病管理提醒相关的数据模型。
"""

from datetime import datetime, time
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Time, Text
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, Field
from enum import Enum

from src.models.base import Base


# ============ 枚举类型 ============


class ReminderType(str, Enum):
    """提醒类型"""

    MEDICATION = "medication"  # 用药提醒
    MEASUREMENT = "measurement"  # 测量提醒（血压、血糖等）
    CHECKUP = "checkup"  # 复查提醒
    OTHER = "other"  # 其他提醒


class RepeatType(str, Enum):
    """重复类型"""

    ONCE = "once"  # 单次
    DAILY = "daily"  # 每天
    WEEKLY = "weekly"  # 每周
    MONTHLY = "monthly"  # 每月


# ============ SQLAlchemy 模型 ============


class Reminder(Base):
    """提醒数据库模型"""

    __tablename__ = "reminders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # 基本信息
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reminder_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="other"
    )

    # 时间设置
    reminder_time: Mapped[time] = mapped_column(Time, nullable=False)
    repeat_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="daily"
    )
    days_of_week: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # "1,2,3,4,5"
    day_of_month: Mapped[Optional[int]] = mapped_column(nullable=True)  # 1-31

    # 状态
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    next_trigger_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    # 元数据
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


# ============ Pydantic 模型 ============


class ReminderCreateRequest(BaseModel):
    """创建提醒请求"""

    title: str = Field(..., min_length=1, max_length=100, description="提醒标题")
    description: Optional[str] = Field(None, max_length=500, description="描述")
    reminder_type: ReminderType = Field(ReminderType.OTHER, description="提醒类型")
    reminder_time: str = Field(..., description="提醒时间 (HH:MM)")
    repeat_type: RepeatType = Field(RepeatType.DAILY, description="重复类型")
    days_of_week: Optional[List[int]] = Field(None, description="周几 (1-7)")
    day_of_month: Optional[int] = Field(None, ge=1, le=31, description="每月几号")
    is_enabled: bool = Field(True, description="是否启用")


class ReminderUpdateRequest(BaseModel):
    """更新提醒请求"""

    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    reminder_type: Optional[ReminderType] = None
    reminder_time: Optional[str] = Field(None, description="提醒时间 (HH:MM)")
    repeat_type: Optional[RepeatType] = None
    days_of_week: Optional[List[int]] = None
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    is_enabled: Optional[bool] = None


class ReminderResponse(BaseModel):
    """提醒响应"""

    id: str
    title: str
    description: Optional[str] = None
    reminder_type: str
    reminder_time: str
    repeat_type: str
    days_of_week: Optional[List[int]] = None
    day_of_month: Optional[int] = None
    is_enabled: bool
    next_trigger_at: Optional[str] = None
    last_triggered_at: Optional[str] = None
    created_at: str
    updated_at: str
