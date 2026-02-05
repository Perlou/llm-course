"""
MediMind - 提醒管理路由

慢病管理提醒 CRUD 接口。
"""

from datetime import datetime, time, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional

from src.utils import log, generate_id
from src.models.reminder import (
    ReminderCreateRequest,
    ReminderUpdateRequest,
    ReminderResponse,
    RepeatType,
)
from src.core.auth import get_current_user

router = APIRouter(prefix="/reminder")

# 内存存储（生产环境应使用数据库）
_reminders_db: Dict[str, Dict[str, Any]] = {}  # reminder_id -> reminder


def _calculate_next_trigger(
    reminder_time: time,
    repeat_type: str,
    days_of_week: Optional[List[int]] = None,
    day_of_month: Optional[int] = None,
) -> Optional[datetime]:
    """计算下次触发时间"""
    now = datetime.now(timezone.utc)
    today = now.date()

    # 今天的触发时间 (需要添加时区)
    trigger_today = datetime.combine(today, reminder_time, tzinfo=timezone.utc)

    if repeat_type == RepeatType.ONCE:
        # 单次：如果今天时间已过，返回 None
        return trigger_today if trigger_today > now else None

    elif repeat_type == RepeatType.DAILY:
        # 每天：如果今天时间已过，明天触发
        if trigger_today > now:
            return trigger_today
        return trigger_today + timedelta(days=1)

    elif repeat_type == RepeatType.WEEKLY:
        # 每周：找到下一个匹配的周几
        if not days_of_week:
            days_of_week = [1, 2, 3, 4, 5, 6, 7]  # 默认每天

        current_weekday = now.isoweekday()  # 1-7

        for i in range(8):
            check_day = (current_weekday + i - 1) % 7 + 1
            if check_day in days_of_week:
                check_date = today + timedelta(days=i)
                check_trigger = datetime.combine(
                    check_date, reminder_time, tzinfo=timezone.utc
                )
                if check_trigger > now:
                    return check_trigger
        return None

    elif repeat_type == RepeatType.MONTHLY:
        # 每月：下一个月的指定日期
        target_day = day_of_month or 1

        # 尝试本月
        try:
            this_month_trigger = datetime(
                today.year,
                today.month,
                target_day,
                reminder_time.hour,
                reminder_time.minute,
                tzinfo=timezone.utc,
            )
            if this_month_trigger > now:
                return this_month_trigger
        except ValueError:
            pass  # 日期无效（如 2 月 30 日）

        # 下个月
        if today.month == 12:
            next_month = 1
            next_year = today.year + 1
        else:
            next_month = today.month + 1
            next_year = today.year

        try:
            return datetime(
                next_year,
                next_month,
                target_day,
                reminder_time.hour,
                reminder_time.minute,
                tzinfo=timezone.utc,
            )
        except ValueError:
            return None

    return None


def _serialize_reminder(reminder: Dict) -> ReminderResponse:
    """序列化提醒"""
    return ReminderResponse(
        id=reminder["id"],
        title=reminder["title"],
        description=reminder.get("description"),
        reminder_type=reminder["reminder_type"],
        reminder_time=reminder["reminder_time"].strftime("%H:%M"),
        repeat_type=reminder["repeat_type"],
        days_of_week=reminder.get("days_of_week"),
        day_of_month=reminder.get("day_of_month"),
        is_enabled=reminder["is_enabled"],
        next_trigger_at=reminder["next_trigger_at"].isoformat()
        if reminder.get("next_trigger_at")
        else None,
        last_triggered_at=reminder["last_triggered_at"].isoformat()
        if reminder.get("last_triggered_at")
        else None,
        created_at=reminder["created_at"].isoformat(),
        updated_at=reminder["updated_at"].isoformat(),
    )


@router.get("")
async def get_reminders(
    current_user: Dict = Depends(get_current_user),
    reminder_type: Optional[str] = Query(None, description="提醒类型筛选"),
):
    """
    获取提醒列表
    """
    user_id = current_user["user_id"]

    reminders = [r for r in _reminders_db.values() if r["user_id"] == user_id]

    # 筛选类型
    if reminder_type:
        reminders = [r for r in reminders if r["reminder_type"] == reminder_type]

    # 按时间排序
    reminders = sorted(reminders, key=lambda r: r["reminder_time"])

    return {
        "code": 200,
        "message": "success",
        "data": {
            "reminders": [_serialize_reminder(r) for r in reminders],
            "total": len(reminders),
        },
    }


@router.post("")
async def create_reminder(
    request: ReminderCreateRequest,
    current_user: Dict = Depends(get_current_user),
):
    """
    创建提醒
    """
    user_id = current_user["user_id"]
    now = datetime.now(timezone.utc)

    # 解析时间
    try:
        hour, minute = map(int, request.reminder_time.split(":"))
        reminder_time = time(hour, minute)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="时间格式错误，请使用 HH:MM 格式")

    # 计算下次触发时间
    next_trigger = _calculate_next_trigger(
        reminder_time,
        request.repeat_type.value,
        request.days_of_week,
        request.day_of_month,
    )

    reminder = {
        "id": generate_id("rem_"),
        "user_id": user_id,
        "title": request.title,
        "description": request.description,
        "reminder_type": request.reminder_type.value,
        "reminder_time": reminder_time,
        "repeat_type": request.repeat_type.value,
        "days_of_week": request.days_of_week,
        "day_of_month": request.day_of_month,
        "is_enabled": request.is_enabled,
        "next_trigger_at": next_trigger,
        "last_triggered_at": None,
        "created_at": now,
        "updated_at": now,
    }

    _reminders_db[reminder["id"]] = reminder

    log.info(f"创建提醒: {reminder['id']}, user={user_id}, title={request.title}")

    return {
        "code": 200,
        "message": "创建成功",
        "data": _serialize_reminder(reminder),
    }


@router.put("/{reminder_id}")
async def update_reminder(
    reminder_id: str,
    request: ReminderUpdateRequest,
    current_user: Dict = Depends(get_current_user),
):
    """
    更新提醒
    """
    user_id = current_user["user_id"]

    reminder = _reminders_db.get(reminder_id)
    if not reminder or reminder["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="提醒不存在")

    # 更新字段
    if request.title is not None:
        reminder["title"] = request.title
    if request.description is not None:
        reminder["description"] = request.description
    if request.reminder_type is not None:
        reminder["reminder_type"] = request.reminder_type.value
    if request.repeat_type is not None:
        reminder["repeat_type"] = request.repeat_type.value
    if request.days_of_week is not None:
        reminder["days_of_week"] = request.days_of_week
    if request.day_of_month is not None:
        reminder["day_of_month"] = request.day_of_month
    if request.is_enabled is not None:
        reminder["is_enabled"] = request.is_enabled

    # 更新时间
    if request.reminder_time is not None:
        try:
            hour, minute = map(int, request.reminder_time.split(":"))
            reminder["reminder_time"] = time(hour, minute)
        except (ValueError, AttributeError):
            raise HTTPException(status_code=400, detail="时间格式错误")

    # 重新计算下次触发时间
    reminder["next_trigger_at"] = _calculate_next_trigger(
        reminder["reminder_time"],
        reminder["repeat_type"],
        reminder.get("days_of_week"),
        reminder.get("day_of_month"),
    )

    reminder["updated_at"] = datetime.now(timezone.utc)

    log.info(f"更新提醒: {reminder_id}")

    return {
        "code": 200,
        "message": "更新成功",
        "data": _serialize_reminder(reminder),
    }


@router.delete("/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    current_user: Dict = Depends(get_current_user),
):
    """
    删除提醒
    """
    user_id = current_user["user_id"]

    reminder = _reminders_db.get(reminder_id)
    if not reminder or reminder["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="提醒不存在")

    del _reminders_db[reminder_id]

    log.info(f"删除提醒: {reminder_id}")

    return {
        "code": 200,
        "message": "删除成功",
        "data": {"deleted": reminder_id},
    }


@router.post("/{reminder_id}/toggle")
async def toggle_reminder(
    reminder_id: str,
    current_user: Dict = Depends(get_current_user),
):
    """
    启用/禁用提醒
    """
    user_id = current_user["user_id"]

    reminder = _reminders_db.get(reminder_id)
    if not reminder or reminder["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="提醒不存在")

    reminder["is_enabled"] = not reminder["is_enabled"]
    reminder["updated_at"] = datetime.now(timezone.utc)

    # 如果启用，重新计算下次触发时间
    if reminder["is_enabled"]:
        reminder["next_trigger_at"] = _calculate_next_trigger(
            reminder["reminder_time"],
            reminder["repeat_type"],
            reminder.get("days_of_week"),
            reminder.get("day_of_month"),
        )

    status = "启用" if reminder["is_enabled"] else "禁用"
    log.info(f"提醒{status}: {reminder_id}")

    return {
        "code": 200,
        "message": f"已{status}",
        "data": _serialize_reminder(reminder),
    }
