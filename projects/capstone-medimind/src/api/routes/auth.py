"""
MediMind - 用户认证路由

用户注册、登录、信息管理接口。
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from src.utils import log, generate_id
from src.models.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserUpdateRequest,
    hash_password,
    verify_password,
)
from src.core.auth import create_access_token, get_current_user

router = APIRouter(prefix="/auth")

# 内存存储（生产环境应使用数据库）
_users_db: Dict[str, Dict[str, Any]] = {}
_users_by_email: Dict[str, str] = {}  # email -> user_id


@router.post("/register")
async def register(request: UserRegisterRequest):
    """
    用户注册
    
    创建新用户账号。
    """
    # 检查邮箱是否已注册
    if request.email.lower() in _users_by_email:
        raise HTTPException(
            status_code=400,
            detail="该邮箱已被注册",
        )
    
    # 创建用户
    user_id = generate_id("user_")
    now = datetime.utcnow()
    
    user_data = {
        "id": user_id,
        "email": request.email.lower(),
        "password_hash": hash_password(request.password),
        "nickname": request.nickname or request.email.split("@")[0],
        "avatar_url": None,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "last_login_at": None,
    }
    
    _users_db[user_id] = user_data
    _users_by_email[request.email.lower()] = user_id
    
    log.info(f"新用户注册: {request.email}")
    
    # 生成 Token
    access_token = create_access_token(user_id, request.email)
    
    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600 * 24 * 7,
            "user": {
                "id": user_id,
                "email": user_data["email"],
                "nickname": user_data["nickname"],
                "avatar_url": user_data["avatar_url"],
                "is_active": user_data["is_active"],
                "created_at": user_data["created_at"].isoformat(),
            },
        },
    }


@router.post("/login")
async def login(request: UserLoginRequest):
    """
    用户登录
    
    验证用户凭据并返回 Token。
    """
    email = request.email.lower()
    
    # 查找用户
    user_id = _users_by_email.get(email)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="邮箱或密码错误",
        )
    
    user = _users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="邮箱或密码错误",
        )
    
    # 验证密码
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="邮箱或密码错误",
        )
    
    # 检查账号状态
    if not user["is_active"]:
        raise HTTPException(
            status_code=403,
            detail="账号已被禁用",
        )
    
    # 更新登录时间
    user["last_login_at"] = datetime.utcnow()
    
    log.info(f"用户登录: {email}")
    
    # 生成 Token
    access_token = create_access_token(user_id, email)
    
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600 * 24 * 7,
            "user": {
                "id": user_id,
                "email": user["email"],
                "nickname": user["nickname"],
                "avatar_url": user["avatar_url"],
                "is_active": user["is_active"],
                "created_at": user["created_at"].isoformat(),
                "last_login_at": user["last_login_at"].isoformat() if user["last_login_at"] else None,
            },
        },
    }


@router.post("/logout")
async def logout(current_user: Dict = Depends(get_current_user)):
    """
    用户登出
    
    客户端应删除本地存储的 Token。
    """
    log.info(f"用户登出: {current_user['email']}")
    
    return {
        "code": 200,
        "message": "登出成功",
        "data": None,
    }


@router.get("/me")
async def get_me(current_user: Dict = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    user = _users_db.get(current_user["user_id"])
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在",
        )
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": user["id"],
            "email": user["email"],
            "nickname": user["nickname"],
            "avatar_url": user["avatar_url"],
            "is_active": user["is_active"],
            "created_at": user["created_at"].isoformat(),
            "last_login_at": user["last_login_at"].isoformat() if user["last_login_at"] else None,
        },
    }


@router.put("/me")
async def update_me(
    request: UserUpdateRequest,
    current_user: Dict = Depends(get_current_user),
):
    """
    更新当前用户信息
    """
    user = _users_db.get(current_user["user_id"])
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在",
        )
    
    # 更新字段
    if request.nickname is not None:
        user["nickname"] = request.nickname
    if request.avatar_url is not None:
        user["avatar_url"] = request.avatar_url
    
    user["updated_at"] = datetime.utcnow()
    
    log.info(f"用户信息更新: {current_user['email']}")
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": {
            "id": user["id"],
            "email": user["email"],
            "nickname": user["nickname"],
            "avatar_url": user["avatar_url"],
            "is_active": user["is_active"],
            "created_at": user["created_at"].isoformat(),
            "updated_at": user["updated_at"].isoformat(),
        },
    }
