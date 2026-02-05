"""
MediMind - 用户认证测试

测试用户注册、登录、Token 验证等功能。
"""

from src.core.auth import create_access_token, decode_token


class TestJWTAuth:
    """JWT Token 测试"""

    def test_create_access_token(self):
        """测试创建 Access Token"""
        token = create_access_token("user_123", "test@example.com")

        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_token_valid(self):
        """测试解码有效 Token"""
        token = create_access_token("user_123", "test@example.com")
        payload = decode_token(token)

        assert payload is not None
        assert payload["sub"] == "user_123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"

    def test_decode_token_invalid(self):
        """测试解码无效 Token"""
        payload = decode_token("invalid.token.here")
        assert payload is None

    def test_decode_token_empty(self):
        """测试解码空 Token"""
        payload = decode_token("")
        assert payload is None


class TestAuthAPI:
    """认证 API 测试"""

    def test_register_success(self, test_client):
        """测试用户注册成功"""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@test.com",
                "password": "password123",
                "nickname": "新用户",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "access_token" in data["data"]
        assert data["data"]["user"]["email"] == "newuser@test.com"

    def test_register_duplicate_email(self, test_client):
        """测试重复邮箱注册"""
        # 先注册一个用户
        test_client.post(
            "/api/v1/auth/register",
            json={"email": "duplicate@test.com", "password": "password123"},
        )

        # 尝试重复注册
        response = test_client.post(
            "/api/v1/auth/register",
            json={"email": "duplicate@test.com", "password": "password456"},
        )

        assert response.status_code == 400
        assert "已被注册" in response.json()["detail"]

    def test_login_success(self, test_client):
        """测试用户登录成功"""
        # 先注册
        test_client.post(
            "/api/v1/auth/register",
            json={"email": "logintest@test.com", "password": "password123"},
        )

        # 登录
        response = test_client.post(
            "/api/v1/auth/login",
            json={"email": "logintest@test.com", "password": "password123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "access_token" in data["data"]

    def test_login_wrong_password(self, test_client):
        """测试密码错误登录"""
        # 先注册
        test_client.post(
            "/api/v1/auth/register",
            json={"email": "wrongpwd@test.com", "password": "password123"},
        )

        # 尝试错误密码登录
        response = test_client.post(
            "/api/v1/auth/login",
            json={"email": "wrongpwd@test.com", "password": "wrongpassword"},
        )

        assert response.status_code == 401

    def test_login_nonexistent_user(self, test_client):
        """测试不存在用户登录"""
        response = test_client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@test.com", "password": "password123"},
        )

        assert response.status_code == 401

    def test_get_me_authenticated(self, test_client):
        """测试获取当前用户信息（已认证）"""
        # 注册并获取 token
        register_response = test_client.post(
            "/api/v1/auth/register",
            json={"email": "authuser@test.com", "password": "password123"},
        )
        token = register_response.json()["data"]["access_token"]

        # 获取用户信息
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["email"] == "authuser@test.com"

    def test_get_me_unauthenticated(self, test_client):
        """测试获取当前用户信息（未认证）"""
        response = test_client.get("/api/v1/auth/me")

        assert response.status_code == 401

    def test_logout(self, test_client):
        """测试用户登出"""
        # 注册并获取 token
        register_response = test_client.post(
            "/api/v1/auth/register",
            json={"email": "logoutuser@test.com", "password": "password123"},
        )
        token = register_response.json()["data"]["access_token"]

        # 登出
        response = test_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["code"] == 200

    def test_update_me(self, test_client):
        """测试更新用户信息"""
        # 注册并获取 token
        register_response = test_client.post(
            "/api/v1/auth/register",
            json={"email": "updateuser@test.com", "password": "password123"},
        )
        token = register_response.json()["data"]["access_token"]

        # 更新用户信息
        response = test_client.put(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"nickname": "新昵称"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["nickname"] == "新昵称"
