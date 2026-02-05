"""
MediMind - 提醒功能测试

测试慢病管理提醒 CRUD 功能。
"""


class TestReminderAPI:
    """提醒 API 测试"""

    def _get_auth_token(self, test_client, email: str = "reminderuser@test.com"):
        """获取认证 Token"""
        response = test_client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123"},
        )
        return response.json()["data"]["access_token"]

    def test_get_reminders_empty(self, test_client):
        """测试获取空提醒列表"""
        token = self._get_auth_token(test_client, "emptyreminder@test.com")

        response = test_client.get(
            "/api/v1/reminder",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["reminders"] == []
        assert data["data"]["total"] == 0

    def test_create_reminder(self, test_client):
        """测试创建提醒"""
        token = self._get_auth_token(test_client, "createreminder@test.com")

        response = test_client.post(
            "/api/v1/reminder",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "服用降压药",
                "description": "每天早晚各一次",
                "reminder_type": "medication",
                "reminder_time": "08:00",
                "repeat_type": "daily",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == "服用降压药"
        assert data["data"]["reminder_type"] == "medication"
        assert data["data"]["reminder_time"] == "08:00"
        assert data["data"]["is_enabled"] is True

    def test_create_weekly_reminder(self, test_client):
        """测试创建周重复提醒"""
        token = self._get_auth_token(test_client, "weeklyreminder@test.com")

        response = test_client.post(
            "/api/v1/reminder",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "测量血压",
                "reminder_type": "measurement",
                "reminder_time": "09:00",
                "repeat_type": "weekly",
                "days_of_week": [1, 3, 5],  # 周一、三、五
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["repeat_type"] == "weekly"
        assert data["data"]["days_of_week"] == [1, 3, 5]

    def test_update_reminder(self, test_client):
        """测试更新提醒"""
        token = self._get_auth_token(test_client, "updatereminder@test.com")

        # 创建提醒
        create_response = test_client.post(
            "/api/v1/reminder",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "原标题",
                "reminder_type": "other",
                "reminder_time": "10:00",
                "repeat_type": "daily",
            },
        )
        reminder_id = create_response.json()["data"]["id"]

        # 更新提醒
        response = test_client.put(
            f"/api/v1/reminder/{reminder_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "新标题",
                "reminder_time": "11:00",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == "新标题"
        assert data["data"]["reminder_time"] == "11:00"

    def test_toggle_reminder(self, test_client):
        """测试启用/禁用提醒"""
        token = self._get_auth_token(test_client, "togglereminder@test.com")

        # 创建提醒
        create_response = test_client.post(
            "/api/v1/reminder",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "测试提醒",
                "reminder_type": "other",
                "reminder_time": "12:00",
                "repeat_type": "daily",
            },
        )
        reminder_id = create_response.json()["data"]["id"]
        assert create_response.json()["data"]["is_enabled"] is True

        # 禁用
        response = test_client.post(
            f"/api/v1/reminder/{reminder_id}/toggle",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["data"]["is_enabled"] is False

        # 再次启用
        response = test_client.post(
            f"/api/v1/reminder/{reminder_id}/toggle",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.json()["data"]["is_enabled"] is True

    def test_delete_reminder(self, test_client):
        """测试删除提醒"""
        token = self._get_auth_token(test_client, "deletereminder@test.com")

        # 创建提醒
        create_response = test_client.post(
            "/api/v1/reminder",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "待删除提醒",
                "reminder_type": "other",
                "reminder_time": "13:00",
                "repeat_type": "once",
            },
        )
        reminder_id = create_response.json()["data"]["id"]

        # 删除
        response = test_client.delete(
            f"/api/v1/reminder/{reminder_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

        # 确认已删除
        list_response = test_client.get(
            "/api/v1/reminder",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert list_response.json()["data"]["total"] == 0

    def test_delete_nonexistent_reminder(self, test_client):
        """测试删除不存在的提醒"""
        token = self._get_auth_token(test_client, "delnonexist@test.com")

        response = test_client.delete(
            "/api/v1/reminder/nonexistent_id",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    def test_filter_by_type(self, test_client):
        """测试按类型筛选"""
        token = self._get_auth_token(test_client, "filtertype@test.com")

        # 创建不同类型的提醒
        test_client.post(
            "/api/v1/reminder",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "用药",
                "reminder_type": "medication",
                "reminder_time": "08:00",
                "repeat_type": "daily",
            },
        )
        test_client.post(
            "/api/v1/reminder",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "测量",
                "reminder_type": "measurement",
                "reminder_time": "09:00",
                "repeat_type": "daily",
            },
        )

        # 筛选用药提醒
        response = test_client.get(
            "/api/v1/reminder",
            params={"reminder_type": "medication"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["reminders"]) == 1
        assert data["data"]["reminders"][0]["reminder_type"] == "medication"

    def test_unauthenticated_access(self, test_client):
        """测试未认证访问"""
        response = test_client.get("/api/v1/reminder")
        assert response.status_code == 401
