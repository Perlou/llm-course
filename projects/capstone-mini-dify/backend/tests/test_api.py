"""
Mini-Dify - API 端到端测试
"""

import pytest


# ==================== 健康检查 ====================


@pytest.mark.anyio
async def test_health_check(client):
    """测试健康检查端点"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert "services" in data
    assert "database" in data["services"]
    assert "milvus" in data["services"]


# ==================== 模型供应商 API ====================


@pytest.mark.anyio
async def test_list_providers(client):
    """测试模型供应商列表"""
    response = await client.get("/api/v1/providers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_create_provider_validation(client):
    """测试创建供应商 — 无效类型"""
    response = await client.post(
        "/api/v1/providers",
        json={"name": "Bad", "provider_type": "invalid_type"},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_provider_missing_name(client):
    """测试创建供应商 — 缺少名称"""
    response = await client.post(
        "/api/v1/providers",
        json={"provider_type": "openai"},
    )
    assert response.status_code == 422


# ==================== Prompt API ====================


@pytest.mark.anyio
async def test_list_prompts(client):
    """测试 Prompt 列表"""
    response = await client.get("/api/v1/prompts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_create_prompt_validation(client):
    """测试创建 Prompt — 缺少内容"""
    response = await client.post(
        "/api/v1/prompts",
        json={"name": "Test"},
    )
    assert response.status_code == 422


# ==================== 知识库 API ====================


@pytest.mark.anyio
async def test_list_datasets(client):
    """测试知识库列表"""
    response = await client.get("/api/v1/datasets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_create_dataset_validation(client):
    """测试创建知识库 — 空名称"""
    response = await client.post(
        "/api/v1/datasets",
        json={"name": ""},
    )
    assert response.status_code == 422


# ==================== Agent API ====================


@pytest.mark.anyio
async def test_list_agents(client):
    """测试 Agent 列表"""
    response = await client.get("/api/v1/agents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_create_agent_validation(client):
    """测试创建 Agent — 缺少必填字段"""
    response = await client.post(
        "/api/v1/agents",
        json={"name": "Bot"},
    )
    assert response.status_code == 422


# ==================== 工作流 API ====================


@pytest.mark.anyio
async def test_list_workflows(client):
    """测试工作流列表"""
    response = await client.get("/api/v1/workflows")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ==================== 应用 API ====================


@pytest.mark.anyio
async def test_list_apps(client):
    """测试应用列表"""
    response = await client.get("/api/v1/apps")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_create_app_validation_invalid_type(client):
    """测试应用创建校验 — 无效类型"""
    response = await client.post(
        "/api/v1/apps",
        json={"name": "test", "app_type": "invalid_type", "config": {}},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_app_validation_missing_config(client):
    """测试应用创建校验 — 缺少 config"""
    response = await client.post(
        "/api/v1/apps",
        json={"name": "test", "app_type": "chatbot"},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_app_validation_empty_name(client):
    """测试应用创建校验 — 空名称"""
    response = await client.post(
        "/api/v1/apps",
        json={"name": "", "app_type": "chatbot", "config": {}},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_nonexistent_app(client):
    """测试获取不存在的应用"""
    response = await client.get(
        "/api/v1/apps/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_publish_nonexistent_app(client):
    """测试发布不存在的应用"""
    response = await client.post(
        "/api/v1/apps/00000000-0000-0000-0000-000000000000/publish"
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_unpublish_nonexistent_app(client):
    """测试取消发布不存在的应用"""
    response = await client.post(
        "/api/v1/apps/00000000-0000-0000-0000-000000000000/unpublish"
    )
    assert response.status_code == 404


# ==================== 监控统计 API ====================


@pytest.mark.anyio
async def test_analytics_stats(client):
    """测试监控统计"""
    response = await client.get("/api/v1/analytics/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_calls" in data
    assert "today_calls" in data
    assert "total_tokens" in data
    assert "total_input_tokens" in data
    assert "total_output_tokens" in data
    assert "avg_latency_ms" in data
    # 初始状态所有值应为 0
    assert data["total_calls"] >= 0
    assert data["total_tokens"] >= 0


@pytest.mark.anyio
async def test_analytics_token_trend_default(client):
    """测试 Token 趋势 — 默认 7 天"""
    response = await client.get("/api/v1/analytics/token-trend")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 7


@pytest.mark.anyio
async def test_analytics_token_trend_custom_days(client):
    """测试 Token 趋势 — 自定义天数"""
    response = await client.get("/api/v1/analytics/token-trend?days=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@pytest.mark.anyio
async def test_analytics_token_trend_each_item_structure(client):
    """测试 Token 趋势 — 每条数据结构"""
    response = await client.get("/api/v1/analytics/token-trend?days=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    item = data[0]
    assert "date" in item
    assert "input_tokens" in item
    assert "output_tokens" in item
    assert "count" in item


@pytest.mark.anyio
async def test_analytics_logs(client):
    """测试对话日志"""
    response = await client.get("/api/v1/analytics/logs")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert "page" in data
    assert "page_size" in data


@pytest.mark.anyio
async def test_analytics_logs_pagination(client):
    """测试对话日志分页参数"""
    response = await client.get("/api/v1/analytics/logs?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 5


@pytest.mark.anyio
async def test_analytics_logs_role_filter(client):
    """测试对话日志角色筛选"""
    response = await client.get("/api/v1/analytics/logs?role=assistant")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)


# ==================== 网关 API ====================


@pytest.mark.anyio
async def test_gateway_chat_no_auth(client):
    """测试网关 — 无认证"""
    response = await client.post("/api/v1/gateway/chat", json={"message": "test"})
    assert response.status_code == 401


@pytest.mark.anyio
async def test_gateway_chat_invalid_key(client):
    """测试网关 — 无效 Key"""
    response = await client.post(
        "/api/v1/gateway/chat",
        json={"message": "test"},
        headers={"Authorization": "Bearer md-invalid-key-12345"},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_gateway_chat_non_bearer(client):
    """测试网关 — 非 Bearer 认证"""
    response = await client.post(
        "/api/v1/gateway/chat",
        json={"message": "test"},
        headers={"Authorization": "Basic dXNlcjpwYXNz"},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_gateway_chat_non_md_key(client):
    """测试网关 — 非 md- 前缀的 Key"""
    response = await client.post(
        "/api/v1/gateway/chat",
        json={"message": "test"},
        headers={"Authorization": "Bearer sk-regular-api-key"},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_gateway_completion_no_auth(client):
    """测试 Completion 网关 — 无认证"""
    response = await client.post(
        "/api/v1/gateway/completion",
        json={"inputs": {"text": "test"}},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_gateway_workflow_no_auth(client):
    """测试 Workflow 网关 — 无认证"""
    response = await client.post(
        "/api/v1/gateway/workflow",
        json={"inputs": {}},
    )
    assert response.status_code == 401

