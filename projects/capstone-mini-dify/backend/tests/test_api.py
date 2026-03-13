"""
Mini-Dify - API 端到端测试
"""

import pytest


@pytest.mark.anyio
async def test_health_check(client):
    """测试健康检查端点"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert "services" in data


@pytest.mark.anyio
async def test_list_providers(client):
    """测试模型供应商列表"""
    response = await client.get("/api/v1/providers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_list_prompts(client):
    """测试 Prompt 列表"""
    response = await client.get("/api/v1/prompts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_list_datasets(client):
    """测试知识库列表"""
    response = await client.get("/api/v1/datasets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_list_agents(client):
    """测试 Agent 列表"""
    response = await client.get("/api/v1/agents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_list_workflows(client):
    """测试工作流列表"""
    response = await client.get("/api/v1/workflows")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_list_apps(client):
    """测试应用列表"""
    response = await client.get("/api/v1/apps")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_analytics_stats(client):
    """测试监控统计"""
    response = await client.get("/api/v1/analytics/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_calls" in data
    assert "today_calls" in data
    assert "total_tokens" in data
    assert "avg_latency_ms" in data


@pytest.mark.anyio
async def test_analytics_token_trend(client):
    """测试 Token 趋势"""
    response = await client.get("/api/v1/analytics/token-trend")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 7  # 默认 7 天


@pytest.mark.anyio
async def test_analytics_logs(client):
    """测试对话日志"""
    response = await client.get("/api/v1/analytics/logs")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert "page" in data


@pytest.mark.anyio
async def test_gateway_unauthorized(client):
    """测试网关未认证"""
    response = await client.post("/api/v1/gateway/chat", json={"message": "test"})
    assert response.status_code == 401


@pytest.mark.anyio
async def test_gateway_invalid_key(client):
    """测试网关无效 Key"""
    response = await client.post(
        "/api/v1/gateway/chat",
        json={"message": "test"},
        headers={"Authorization": "Bearer md-invalid-key"},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_create_app_validation(client):
    """测试应用创建校验 — 无效类型"""
    response = await client.post(
        "/api/v1/apps",
        json={
            "name": "test",
            "app_type": "invalid_type",
            "config": {},
        },
    )
    assert response.status_code == 422  # 校验失败
