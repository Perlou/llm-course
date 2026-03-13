"""
Mini-Dify - 模型服务单元测试
"""

from app.core.model_service import ChatMessage, ChatResult, HealthCheckResult, ModelService


# ==================== Data Classes ====================


class TestChatMessage:
    """ChatMessage 数据类测试"""

    def test_user_message(self):
        msg = ChatMessage(role="user", content="你好")
        assert msg.role == "user"
        assert msg.content == "你好"

    def test_system_message(self):
        msg = ChatMessage(role="system", content="你是一个助手")
        assert msg.role == "system"

    def test_assistant_message(self):
        msg = ChatMessage(role="assistant", content="你好！")
        assert msg.role == "assistant"


class TestChatResult:
    """ChatResult 数据类测试"""

    def test_default_values(self):
        result = ChatResult(content="Hello!")
        assert result.content == "Hello!"
        assert result.input_tokens == 0
        assert result.output_tokens == 0
        assert result.latency_ms == 0
        assert result.finish_reason == "stop"

    def test_with_token_counts(self):
        result = ChatResult(
            content="Test response",
            input_tokens=100,
            output_tokens=50,
            latency_ms=350,
        )
        assert result.input_tokens == 100
        assert result.output_tokens == 50
        assert result.latency_ms == 350

    def test_empty_content(self):
        result = ChatResult(content="")
        assert result.content == ""


class TestHealthCheckResult:
    """HealthCheckResult 数据类测试"""

    def test_healthy(self):
        result = HealthCheckResult(status="healthy", latency_ms=120)
        assert result.status == "healthy"
        assert result.error is None

    def test_unhealthy(self):
        result = HealthCheckResult(
            status="unhealthy",
            latency_ms=0,
            error="Connection refused",
        )
        assert result.status == "unhealthy"
        assert result.error == "Connection refused"


# ==================== ModelService ====================


class TestModelServiceConstants:
    """ModelService 常量和配置测试"""

    def test_supported_providers(self):
        assert "openai" in ModelService.SUPPORTED_PROVIDERS
        assert "anthropic" in ModelService.SUPPORTED_PROVIDERS
        assert "google" in ModelService.SUPPORTED_PROVIDERS
        assert "ollama" in ModelService.SUPPORTED_PROVIDERS

    def test_unsupported_provider_not_listed(self):
        assert "huggingface" not in ModelService.SUPPORTED_PROVIDERS
        assert "cohere" not in ModelService.SUPPORTED_PROVIDERS
