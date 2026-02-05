"""
MediMind - 医院搜索服务

基于高德地图 POI API 实现周边医院搜索和推荐功能。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import httpx

from src.utils import get_settings, log


@dataclass
class Hospital:
    """医院信息"""

    id: str
    name: str
    address: str
    tel: Optional[str] = None
    distance: Optional[float] = None  # 米
    type_name: Optional[str] = None
    rating: Optional[float] = None
    location: Optional[Dict[str, float]] = None  # {"lat": ..., "lng": ...}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "tel": self.tel,
            "distance": self.distance,
            "type_name": self.type_name,
            "rating": self.rating,
            "location": self.location,
        }


class HospitalService:
    """
    医院搜索服务

    使用高德 POI 周边搜索 API 获取附近医院信息。
    """

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.amap_api_key
        self.base_url = self.settings.amap.base_url
        self.default_radius = self.settings.amap.search_radius
        self.poi_types = self.settings.amap.poi_types

        # 科室到 POI 类型的映射
        self.department_types = {
            "急诊科": "090101",  # 综合医院
            "内科": "090101",
            "外科": "090101",
            "儿科": "090103",  # 儿童医院
            "妇产科": "090104",  # 妇幼保健院
            "心内科": "090101",
            "神经内科": "090101",
            "骨科": "090101",
            "眼科": "090105",  # 眼科医院
            "耳鼻喉科": "090101",
            "口腔科": "090106",  # 口腔医院
            "皮肤科": "090101",
            "精神科": "090107",  # 精神病专科医院
            "中医科": "090102",  # 中医医院
            "康复科": "090101",
        }

    async def search_nearby(
        self,
        lat: float,
        lng: float,
        keyword: Optional[str] = None,
        types: Optional[str] = None,
        radius: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        搜索周边医院

        Args:
            lat: 纬度
            lng: 经度
            keyword: 搜索关键词（可选）
            types: POI 类型（可选，默认使用配置的医院类型）
            radius: 搜索半径（米，可选）
            page: 页码
            page_size: 每页数量

        Returns:
            包含医院列表和元数据的字典
        """
        if not self.api_key:
            log.warning("未配置高德地图 API Key，返回模拟数据")
            return self._get_mock_data(lat, lng)

        # 构建请求参数
        location = f"{lng},{lat}"  # 高德用 经度,纬度 格式
        params = {
            "key": self.api_key,
            "location": location,
            "types": types or self.poi_types,
            "radius": radius or self.default_radius,
            "offset": page_size,
            "page": page,
            "extensions": "all",  # 返回详细信息
            "sortrule": "distance",  # 按距离排序
        }

        if keyword:
            params["keywords"] = keyword

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/place/around",
                    params=params,
                )
                response.raise_for_status()
                data = response.json()

            if data.get("status") != "1":
                log.error(f"高德 API 错误: {data.get('info', 'Unknown error')}")
                return self._get_mock_data(lat, lng)

            # 解析结果
            hospitals = []
            for poi in data.get("pois", []):
                hospital = self._parse_poi(poi)
                if hospital:
                    hospitals.append(hospital)

            return {
                "hospitals": [h.to_dict() for h in hospitals],
                "total": int(data.get("count", 0)),
                "page": page,
                "page_size": page_size,
                "center": {"lat": lat, "lng": lng},
                "radius": radius or self.default_radius,
            }

        except httpx.HTTPError as e:
            log.error(f"高德 API 请求失败: {e}")
            return self._get_mock_data(lat, lng)

    async def get_hospital_detail(self, poi_id: str) -> Optional[Dict[str, Any]]:
        """
        获取医院详情

        Args:
            poi_id: 高德 POI ID

        Returns:
            医院详情字典
        """
        if not self.api_key:
            log.warning("未配置高德地图 API Key")
            return None

        params = {
            "key": self.api_key,
            "id": poi_id,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/place/detail",
                    params=params,
                )
                response.raise_for_status()
                data = response.json()

            if data.get("status") != "1" or not data.get("pois"):
                return None

            poi = data["pois"][0]
            hospital = self._parse_poi(poi)
            return hospital.to_dict() if hospital else None

        except httpx.HTTPError as e:
            log.error(f"高德 API 请求失败: {e}")
            return None

    async def recommend_by_department(
        self,
        department: str,
        lat: float,
        lng: float,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        根据科室推荐医院

        Args:
            department: 推荐科室名称
            lat: 用户纬度
            lng: 用户经度
            limit: 返回数量

        Returns:
            推荐医院列表
        """
        # 获取科室对应的 POI 类型
        poi_type = self.department_types.get(department, "090100")  # 默认综合医院

        # 搜索附近医院
        result = await self.search_nearby(
            lat=lat,
            lng=lng,
            keyword=department,
            types=poi_type,
            page_size=limit,
        )

        return result.get("hospitals", [])

    def _parse_poi(self, poi: Dict[str, Any]) -> Optional[Hospital]:
        """解析高德 POI 数据"""
        try:
            # 解析位置
            location_str = poi.get("location", "")
            location = None
            if location_str:
                lng, lat = location_str.split(",")
                location = {"lat": float(lat), "lng": float(lng)}

            # 解析距离
            distance = poi.get("distance")
            if distance:
                distance = float(distance)

            # 解析评分
            rating = None
            biz_ext = poi.get("biz_ext", {})
            if isinstance(biz_ext, dict):
                rating_str = biz_ext.get("rating")
                if rating_str and rating_str != "[]":
                    try:
                        rating = float(rating_str)
                    except (ValueError, TypeError):
                        pass

            return Hospital(
                id=poi.get("id", ""),
                name=poi.get("name", ""),
                address=poi.get("address", "")
                or poi.get("pname", "")
                + poi.get("cityname", "")
                + poi.get("adname", ""),
                tel=poi.get("tel")
                if poi.get("tel") and poi.get("tel") != "[]"
                else None,
                distance=distance,
                type_name=poi.get("typecode", ""),
                rating=rating,
                location=location,
            )
        except Exception as e:
            log.warning(f"解析 POI 数据失败: {e}")
            return None

    def _get_mock_data(self, lat: float, lng: float) -> Dict[str, Any]:
        """返回模拟数据（用于测试或无 API Key 时的降级）"""
        mock_hospitals = [
            Hospital(
                id="mock_001",
                name="北京协和医院",
                address="北京市东城区帅府园1号",
                tel="010-69156114",
                distance=1200,
                type_name="三级甲等综合医院",
                rating=4.8,
                location={"lat": lat + 0.01, "lng": lng + 0.01},
            ),
            Hospital(
                id="mock_002",
                name="北京大学第一医院",
                address="北京市西城区西什库大街8号",
                tel="010-83572211",
                distance=2500,
                type_name="三级甲等综合医院",
                rating=4.7,
                location={"lat": lat + 0.02, "lng": lng - 0.01},
            ),
            Hospital(
                id="mock_003",
                name="北京朝阳医院",
                address="北京市朝阳区工人体育场南路8号",
                tel="010-85231000",
                distance=3800,
                type_name="三级甲等综合医院",
                rating=4.6,
                location={"lat": lat - 0.01, "lng": lng + 0.02},
            ),
        ]

        return {
            "hospitals": [h.to_dict() for h in mock_hospitals],
            "total": len(mock_hospitals),
            "page": 1,
            "page_size": 20,
            "center": {"lat": lat, "lng": lng},
            "radius": self.default_radius,
            "mock": True,  # 标记为模拟数据
        }


# 单例
_hospital_service: Optional[HospitalService] = None


def get_hospital_service() -> HospitalService:
    """获取医院服务单例"""
    global _hospital_service
    if _hospital_service is None:
        _hospital_service = HospitalService()
    return _hospital_service
