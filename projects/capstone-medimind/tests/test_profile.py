"""
MediMind - 健康档案测试

测试健康档案和健康记录管理功能。
"""

# 健康档案测试


class TestProfileAPI:
    """健康档案 API 测试"""

    def _get_auth_token(self, test_client, email: str = "profileuser@test.com"):
        """获取认证 Token（辅助方法）"""
        response = test_client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123"},
        )
        return response.json()["data"]["access_token"]

    def test_get_profile_default(self, test_client):
        """测试获取默认档案"""
        token = self._get_auth_token(test_client, "getprofile@test.com")

        response = test_client.get(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["user_id"] is not None
        # 默认值应为空
        assert data["data"]["gender"] is None

    def test_update_profile(self, test_client):
        """测试更新档案"""
        token = self._get_auth_token(test_client, "updateprofile@test.com")

        # 更新档案
        response = test_client.put(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "gender": "male",
                "height_cm": 175,
                "weight_kg": 70,
                "blood_type": "A",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["gender"] == "male"
        assert data["data"]["height_cm"] == 175
        assert data["data"]["weight_kg"] == 70
        assert data["data"]["blood_type"] == "A"

    def test_update_profile_partial(self, test_client):
        """测试部分更新档案"""
        token = self._get_auth_token(test_client, "partialprofile@test.com")

        # 只更新部分字段
        response = test_client.put(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {token}"},
            json={"gender": "female"},
        )

        assert response.status_code == 200
        assert response.json()["data"]["gender"] == "female"

    def test_get_profile_unauthenticated(self, test_client):
        """测试未认证获取档案"""
        response = test_client.get("/api/v1/profile")
        assert response.status_code == 401


class TestRecordsAPI:
    """健康记录 API 测试"""

    def _get_auth_token(self, test_client, email: str):
        """获取认证 Token（辅助方法）"""
        response = test_client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123"},
        )
        return response.json()["data"]["access_token"]

    def test_get_records_empty(self, test_client):
        """测试获取空记录列表"""
        token = self._get_auth_token(test_client, "emptyrecords@test.com")

        response = test_client.get(
            "/api/v1/profile/records",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["records"] == []
        assert data["data"]["total"] == 0

    def test_add_record(self, test_client):
        """测试添加健康记录"""
        token = self._get_auth_token(test_client, "addrecord@test.com")

        response = test_client.post(
            "/api/v1/profile/records",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "record_type": "blood_pressure",
                "value": "120/80",
                "unit": "mmHg",
                "recorded_at": "2026-02-05T10:00:00",
                "notes": "早晨测量",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["record_type"] == "blood_pressure"
        assert data["data"]["value"] == "120/80"
        assert data["data"]["unit"] == "mmHg"

    def test_add_multiple_records(self, test_client):
        """测试添加多条记录"""
        token = self._get_auth_token(test_client, "multirecords@test.com")

        # 添加多条记录
        for i in range(3):
            test_client.post(
                "/api/v1/profile/records",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "record_type": "heart_rate",
                    "value": str(70 + i),
                    "unit": "bpm",
                    "recorded_at": f"2026-02-0{5 - i}T10:00:00",
                },
            )

        # 获取记录列表
        response = test_client.get(
            "/api/v1/profile/records",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 3

    def test_filter_records_by_type(self, test_client):
        """测试按类型筛选记录"""
        token = self._get_auth_token(test_client, "filterrecords@test.com")

        # 添加不同类型的记录
        test_client.post(
            "/api/v1/profile/records",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "record_type": "blood_pressure",
                "value": "120/80",
                "recorded_at": "2026-02-05T10:00:00",
            },
        )
        test_client.post(
            "/api/v1/profile/records",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "record_type": "heart_rate",
                "value": "72",
                "recorded_at": "2026-02-05T10:00:00",
            },
        )

        # 筛选血压记录
        response = test_client.get(
            "/api/v1/profile/records",
            params={"record_type": "blood_pressure"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["records"]) == 1
        assert data["data"]["records"][0]["record_type"] == "blood_pressure"

    def test_delete_record(self, test_client):
        """测试删除记录"""
        token = self._get_auth_token(test_client, "deleterecord@test.com")

        # 添加记录
        add_response = test_client.post(
            "/api/v1/profile/records",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "record_type": "weight",
                "value": "70",
                "recorded_at": "2026-02-05T10:00:00",
            },
        )
        record_id = add_response.json()["data"]["id"]

        # 删除记录
        response = test_client.delete(
            f"/api/v1/profile/records/{record_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

        # 确认已删除
        list_response = test_client.get(
            "/api/v1/profile/records",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert list_response.json()["data"]["total"] == 0

    def test_delete_nonexistent_record(self, test_client):
        """测试删除不存在的记录"""
        token = self._get_auth_token(test_client, "delnonexist@test.com")

        response = test_client.delete(
            "/api/v1/profile/records/nonexistent_id",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    def test_pagination(self, test_client):
        """测试分页功能"""
        token = self._get_auth_token(test_client, "pagination@test.com")

        # 添加 5 条记录
        for i in range(5):
            test_client.post(
                "/api/v1/profile/records",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "record_type": "temperature",
                    "value": str(36.5 + i * 0.1),
                    "recorded_at": f"2026-02-0{i + 1}T10:00:00",
                },
            )

        # 获取前 2 条
        response = test_client.get(
            "/api/v1/profile/records",
            params={"limit": 2, "offset": 0},
            headers={"Authorization": f"Bearer {token}"},
        )

        data = response.json()
        assert len(data["data"]["records"]) == 2
        assert data["data"]["total"] == 5
