"""
MediMind - 医院服务测试

测试医院搜索和推荐功能。
"""

import pytest
from unittest.mock import patch, AsyncMock

from src.core.hospital_service import HospitalService, Hospital, get_hospital_service


class TestHospital:
    """医院数据类测试"""

    def test_hospital_to_dict(self):
        """测试医院数据转换为字典"""
        hospital = Hospital(
            id="test_001",
            name="测试医院",
            address="北京市测试区测试路1号",
            tel="010-12345678",
            distance=1500.0,
            type_name="综合医院",
            rating=4.5,
            location={"lat": 39.9, "lng": 116.4},
        )

        result = hospital.to_dict()

        assert result["id"] == "test_001"
        assert result["name"] == "测试医院"
        assert result["address"] == "北京市测试区测试路1号"
        assert result["tel"] == "010-12345678"
        assert result["distance"] == 1500.0
        assert result["rating"] == 4.5
        assert result["location"]["lat"] == 39.9


class TestHospitalService:
    """医院服务测试"""

    def test_get_hospital_service_singleton(self):
        """测试服务单例"""
        service1 = get_hospital_service()
        service2 = get_hospital_service()
        assert service1 is service2

    @pytest.mark.asyncio
    async def test_search_nearby_mock_data(self):
        """测试无 API Key 时返回模拟数据"""
        service = HospitalService()
        # 确保没有 API Key
        service.api_key = None

        result = await service.search_nearby(
            lat=39.9042,
            lng=116.4074,
            keyword="医院",
        )

        assert "hospitals" in result
        assert "total" in result
        assert "mock" in result  # 标记为模拟数据
        assert len(result["hospitals"]) > 0

        # 检查医院数据结构
        hospital = result["hospitals"][0]
        assert "id" in hospital
        assert "name" in hospital
        assert "address" in hospital

    @pytest.mark.asyncio
    async def test_recommend_by_department(self):
        """测试按科室推荐"""
        service = HospitalService()
        service.api_key = None  # 使用模拟数据

        result = await service.recommend_by_department(
            department="内科",
            lat=39.9042,
            lng=116.4074,
            limit=3,
        )

        assert isinstance(result, list)
        assert len(result) > 0

    def test_department_types_mapping(self):
        """测试科室类型映射"""
        service = HospitalService()

        # 检查常见科室映射
        assert "急诊科" in service.department_types
        assert "儿科" in service.department_types
        assert "中医科" in service.department_types


class TestHospitalAPI:
    """医院 API 测试"""

    def test_nearby_endpoint(self, test_client):
        """测试周边搜索接口"""
        response = test_client.get(
            "/api/v1/hospital/nearby", params={"lat": 39.9042, "lng": 116.4074}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "hospitals" in data["data"]

    def test_nearby_endpoint_validation(self, test_client):
        """测试参数验证"""
        # 缺少必填参数
        response = test_client.get("/api/v1/hospital/nearby")
        assert response.status_code == 422

        # 纬度超范围
        response = test_client.get(
            "/api/v1/hospital/nearby",
            params={"lat": 100, "lng": 116.4074},  # lat 超过 90
        )
        assert response.status_code == 422

    def test_recommend_endpoint(self, test_client):
        """测试推荐接口"""
        response = test_client.post(
            "/api/v1/hospital/recommend",
            json={
                "department": "内科",
                "location": {"lat": 39.9042, "lng": 116.4074},
                "limit": 5,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["department"] == "内科"
