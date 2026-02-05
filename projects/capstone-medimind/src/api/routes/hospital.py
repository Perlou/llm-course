"""
MediMind - 医院搜索路由

周边医院搜索和推荐接口。
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

from src.core.hospital_service import get_hospital_service

router = APIRouter(prefix="/hospital")


class Location(BaseModel):
    """位置信息"""

    lat: float = Field(..., ge=-90, le=90, description="纬度")
    lng: float = Field(..., ge=-180, le=180, description="经度")


class RecommendRequest(BaseModel):
    """推荐请求"""

    department: str = Field(..., min_length=1, max_length=50, description="推荐科室")
    location: Location = Field(..., description="用户位置")
    limit: int = Field(default=5, ge=1, le=20, description="返回数量")


@router.get("/nearby")
async def search_nearby_hospitals(
    lat: float = Query(..., ge=-90, le=90, description="纬度"),
    lng: float = Query(..., ge=-180, le=180, description="经度"),
    keyword: Optional[str] = Query(None, max_length=50, description="搜索关键词"),
    radius: int = Query(5000, ge=500, le=50000, description="搜索半径（米）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=50, description="每页数量"),
):
    """
    搜索周边医院

    根据用户位置搜索附近的医院，支持关键词过滤。
    使用高德地图 POI 周边搜索 API。
    """
    service = get_hospital_service()

    result = await service.search_nearby(
        lat=lat,
        lng=lng,
        keyword=keyword,
        radius=radius,
        page=page,
        page_size=page_size,
    )

    return {
        "code": 0,
        "message": "success",
        "data": result,
        "disclaimer": "🏥 医院信息来源于高德地图，仅供参考。就医前请电话确认。",
    }


@router.get("/{poi_id}")
async def get_hospital_detail(poi_id: str):
    """
    获取医院详情

    根据高德 POI ID 获取医院详细信息。
    """
    service = get_hospital_service()

    hospital = await service.get_hospital_detail(poi_id)

    if not hospital:
        raise HTTPException(status_code=404, detail="医院不存在或无法获取详情")

    return {
        "code": 0,
        "message": "success",
        "data": hospital,
        "disclaimer": "🏥 医院信息来源于高德地图，仅供参考。就医前请电话确认。",
    }


@router.post("/recommend")
async def recommend_hospitals(request: RecommendRequest):
    """
    基于科室推荐医院

    根据导诊推荐的科室，搜索附近对应类型的医院。
    """
    service = get_hospital_service()

    hospitals = await service.recommend_by_department(
        department=request.department,
        lat=request.location.lat,
        lng=request.location.lng,
        limit=request.limit,
    )

    return {
        "code": 0,
        "message": "success",
        "data": {
            "department": request.department,
            "hospitals": hospitals,
            "total": len(hospitals),
        },
        "disclaimer": "🏥 医院推荐仅供参考，请根据实际情况选择就医。",
    }
