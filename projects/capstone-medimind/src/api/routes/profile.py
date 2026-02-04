"""
MediMind - 健康档案路由

健康档案和健康记录管理接口。
"""

import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional

from src.utils import log, generate_id
from src.models.health_profile import (
    HealthProfileRequest,
    HealthRecordRequest,
)
from src.core.auth import get_current_user

router = APIRouter(prefix="/profile")

# 内存存储（生产环境应使用数据库）
_profiles_db: Dict[str, Dict[str, Any]] = {}  # user_id -> profile
_records_db: Dict[str, List[Dict[str, Any]]] = {}  # user_id -> [records]


@router.get("")
async def get_profile(current_user: Dict = Depends(get_current_user)):
    """
    获取健康档案
    """
    user_id = current_user["user_id"]
    profile = _profiles_db.get(user_id)
    
    if not profile:
        # 创建默认档案
        profile = {
            "id": generate_id("profile_"),
            "user_id": user_id,
            "gender": None,
            "birth_date": None,
            "height_cm": None,
            "weight_kg": None,
            "blood_type": None,
            "allergies": [],
            "medical_history": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        _profiles_db[user_id] = profile
    
    return {
        "code": 200,
        "message": "success",
        "data": _serialize_profile(profile),
    }


@router.put("")
async def update_profile(
    request: HealthProfileRequest,
    current_user: Dict = Depends(get_current_user),
):
    """
    更新健康档案
    """
    user_id = current_user["user_id"]
    profile = _profiles_db.get(user_id)
    
    if not profile:
        profile = {
            "id": generate_id("profile_"),
            "user_id": user_id,
            "created_at": datetime.utcnow(),
        }
        _profiles_db[user_id] = profile
    
    # 更新字段
    if request.gender is not None:
        profile["gender"] = request.gender
    if request.birth_date is not None:
        profile["birth_date"] = request.birth_date
    if request.height_cm is not None:
        profile["height_cm"] = request.height_cm
    if request.weight_kg is not None:
        profile["weight_kg"] = request.weight_kg
    if request.blood_type is not None:
        profile["blood_type"] = request.blood_type
    if request.allergies is not None:
        profile["allergies"] = request.allergies
    if request.medical_history is not None:
        profile["medical_history"] = request.medical_history
    
    profile["updated_at"] = datetime.utcnow()
    
    log.info(f"健康档案更新: {user_id}")
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": _serialize_profile(profile),
    }


@router.get("/records")
async def get_records(
    current_user: Dict = Depends(get_current_user),
    record_type: Optional[str] = Query(None, description="记录类型"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    获取健康记录列表
    """
    user_id = current_user["user_id"]
    records = _records_db.get(user_id, [])
    
    # 筛选类型
    if record_type:
        records = [r for r in records if r["record_type"] == record_type]
    
    # 排序（时间倒序）
    records = sorted(records, key=lambda r: r["recorded_at"], reverse=True)
    
    # 分页
    total = len(records)
    records = records[offset:offset + limit]
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "records": [_serialize_record(r) for r in records],
            "total": total,
            "limit": limit,
            "offset": offset,
        },
    }


@router.post("/records")
async def add_record(
    request: HealthRecordRequest,
    current_user: Dict = Depends(get_current_user),
):
    """
    添加健康记录
    """
    user_id = current_user["user_id"]
    
    if user_id not in _records_db:
        _records_db[user_id] = []
    
    record = {
        "id": generate_id("rec_"),
        "user_id": user_id,
        "record_type": request.record_type,
        "value": request.value,
        "unit": request.unit,
        "recorded_at": request.recorded_at,
        "notes": request.notes,
        "created_at": datetime.utcnow(),
    }
    
    _records_db[user_id].append(record)
    
    log.info(f"健康记录添加: {user_id}, type={request.record_type}")
    
    return {
        "code": 200,
        "message": "添加成功",
        "data": _serialize_record(record),
    }


@router.delete("/records/{record_id}")
async def delete_record(
    record_id: str,
    current_user: Dict = Depends(get_current_user),
):
    """
    删除健康记录
    """
    user_id = current_user["user_id"]
    records = _records_db.get(user_id, [])
    
    for i, record in enumerate(records):
        if record["id"] == record_id:
            del records[i]
            log.info(f"健康记录删除: {record_id}")
            return {
                "code": 200,
                "message": "删除成功",
                "data": {"deleted": record_id},
            }
    
    raise HTTPException(status_code=404, detail="记录不存在")


def _serialize_profile(profile: Dict) -> Dict:
    """序列化档案"""
    return {
        "id": profile["id"],
        "user_id": profile["user_id"],
        "gender": profile.get("gender"),
        "birth_date": profile.get("birth_date").isoformat() if profile.get("birth_date") else None,
        "height_cm": profile.get("height_cm"),
        "weight_kg": profile.get("weight_kg"),
        "blood_type": profile.get("blood_type"),
        "allergies": profile.get("allergies", []),
        "medical_history": profile.get("medical_history", []),
        "created_at": profile["created_at"].isoformat(),
        "updated_at": profile["updated_at"].isoformat(),
    }


def _serialize_record(record: Dict) -> Dict:
    """序列化记录"""
    return {
        "id": record["id"],
        "record_type": record["record_type"],
        "value": record["value"],
        "unit": record.get("unit"),
        "recorded_at": record["recorded_at"].isoformat() if isinstance(record["recorded_at"], datetime) else record["recorded_at"],
        "notes": record.get("notes"),
        "created_at": record["created_at"].isoformat(),
    }
