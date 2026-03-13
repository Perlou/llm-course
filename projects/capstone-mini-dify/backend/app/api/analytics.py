"""
Mini-Dify - 监控统计 API
"""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.log import ConversationLog

router = APIRouter(prefix="/analytics", tags=["监控统计"])


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    统计概览 — 总调用 / 今日调用 / 总 Token / 平均延迟
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # 总调用次数（仅 assistant 回复计数）
    total_result = await db.execute(
        select(func.count(ConversationLog.id)).where(
            ConversationLog.role == "assistant"
        )
    )
    total_calls = total_result.scalar() or 0

    # 今日调用
    today_result = await db.execute(
        select(func.count(ConversationLog.id)).where(
            ConversationLog.role == "assistant",
            ConversationLog.created_at >= today_start,
        )
    )
    today_calls = today_result.scalar() or 0

    # 总 Token
    token_result = await db.execute(
        select(
            func.coalesce(func.sum(ConversationLog.input_tokens), 0),
            func.coalesce(func.sum(ConversationLog.output_tokens), 0),
        )
    )
    row = token_result.one()
    total_input_tokens = row[0]
    total_output_tokens = row[1]
    total_tokens = total_input_tokens + total_output_tokens

    # 平均延迟 (仅 assistant)
    latency_result = await db.execute(
        select(func.avg(ConversationLog.latency_ms)).where(
            ConversationLog.role == "assistant",
            ConversationLog.latency_ms.isnot(None),
        )
    )
    avg_latency = latency_result.scalar()
    avg_latency = round(avg_latency, 1) if avg_latency else 0

    return {
        "total_calls": total_calls,
        "today_calls": today_calls,
        "total_tokens": total_tokens,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "avg_latency_ms": avg_latency,
    }


@router.get("/token-trend")
async def get_token_trend(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    """
    最近 N 天每日 Token 消耗趋势
    """
    now = datetime.now(timezone.utc)
    start_date = (now - timedelta(days=days)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    result = await db.execute(
        select(
            cast(ConversationLog.created_at, Date).label("date"),
            func.coalesce(func.sum(ConversationLog.input_tokens), 0).label(
                "input_tokens"
            ),
            func.coalesce(func.sum(ConversationLog.output_tokens), 0).label(
                "output_tokens"
            ),
            func.count(ConversationLog.id).label("count"),
        )
        .where(ConversationLog.created_at >= start_date)
        .group_by(cast(ConversationLog.created_at, Date))
        .order_by(cast(ConversationLog.created_at, Date))
    )
    rows = result.all()

    # Fill in missing dates
    trend = []
    for i in range(days):
        d = (now - timedelta(days=days - 1 - i)).date()
        matched = next((r for r in rows if r.date == d), None)
        trend.append(
            {
                "date": d.isoformat(),
                "input_tokens": matched.input_tokens if matched else 0,
                "output_tokens": matched.output_tokens if matched else 0,
                "count": matched.count if matched else 0,
            }
        )

    return trend


@router.get("/logs")
async def get_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    对话日志列表（分页）
    """
    query = select(ConversationLog).order_by(ConversationLog.created_at.desc())

    if role:
        query = query.where(ConversationLog.role == role)

    # Count
    count_query = select(func.count(ConversationLog.id))
    if role:
        count_query = count_query.where(ConversationLog.role == role)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    logs = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": str(log.id),
                "app_id": str(log.app_id),
                "conversation_id": str(log.conversation_id),
                "role": log.role,
                "content": (
                    log.content[:200] + "..." if len(log.content) > 200 else log.content
                ),
                "provider_name": log.provider_name,
                "model_name": log.model_name,
                "input_tokens": log.input_tokens,
                "output_tokens": log.output_tokens,
                "latency_ms": log.latency_ms,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
    }
