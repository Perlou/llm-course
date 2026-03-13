"""
Mini-Dify - Pydantic Schema 验证测试
"""

import pytest
from pydantic import ValidationError
from app.schemas import (
    ProviderCreate,
    ProviderUpdate,
    PromptCreate,
    PromptUpdate,
    DatasetCreate,
    AgentCreate,
    AgentUpdate,
    WorkflowCreate,
    WorkflowUpdate,
    AppCreate,
    AppUpdate,
    AppResponse,
    ChatRequest,
)


# ==================== Provider Schemas ====================


class TestProviderSchemas:
    """模型供应商 Schema 测试"""

    def test_valid_provider_create(self):
        provider = ProviderCreate(
            name="OpenAI",
            provider_type="openai",
            api_key="sk-test",
            base_url="https://api.openai.com/v1",
        )
        assert provider.name == "OpenAI"
        assert provider.provider_type == "openai"

    def test_provider_create_all_types(self):
        """测试所有支持的 provider_type"""
        for ptype in ["openai", "anthropic", "google", "ollama"]:
            p = ProviderCreate(name=f"Test-{ptype}", provider_type=ptype)
            assert p.provider_type == ptype

    def test_provider_create_invalid_type(self):
        """不支持的 provider_type 应失败"""
        with pytest.raises(ValidationError):
            ProviderCreate(name="Test", provider_type="invalid")

    def test_provider_create_empty_name(self):
        with pytest.raises(ValidationError):
            ProviderCreate(name="", provider_type="openai")

    def test_provider_create_long_name(self):
        with pytest.raises(ValidationError):
            ProviderCreate(name="x" * 101, provider_type="openai")

    def test_provider_update_partial(self):
        update = ProviderUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.api_key is None
        assert update.is_active is None

    def test_provider_update_empty(self):
        """空更新应该被允许"""
        update = ProviderUpdate()
        assert update.name is None


# ==================== Prompt Schemas ====================


class TestPromptSchemas:
    """Prompt Schema 测试"""

    def test_valid_prompt_create(self):
        prompt = PromptCreate(
            name="翻译助手",
            content="将以下文本翻译为 {{target_language}}：\n{{text}}",
            description="多语言翻译",
        )
        assert prompt.name == "翻译助手"
        assert "{{target_language}}" in prompt.content

    def test_prompt_create_minimal(self):
        prompt = PromptCreate(name="Basic", content="Hello")
        assert prompt.description is None

    def test_prompt_create_empty_name(self):
        with pytest.raises(ValidationError):
            PromptCreate(name="", content="test")

    def test_prompt_create_empty_content(self):
        with pytest.raises(ValidationError):
            PromptCreate(name="Test", content="")

    def test_prompt_update_partial(self):
        update = PromptUpdate(name="Updated")
        assert update.name == "Updated"
        assert update.content is None


# ==================== Dataset Schemas ====================


class TestDatasetSchemas:
    """知识库 Schema 测试"""

    def test_valid_dataset_create(self):
        ds = DatasetCreate(
            name="技术文档库",
            description="公司内部技术文档",
        )
        assert ds.name == "技术文档库"

    def test_dataset_create_empty_name(self):
        with pytest.raises(ValidationError):
            DatasetCreate(name="")


# ==================== Agent Schemas ====================


class TestAgentSchemas:
    """Agent Schema 测试"""

    def test_valid_agent_create(self):
        agent = AgentCreate(
            name="客服助手",
            system_prompt="你是一个专业的客服助手",
            tools=["search", "calculator"],
        )
        assert agent.name == "客服助手"
        assert len(agent.tools) == 2

    def test_agent_create_empty_tools(self):
        agent = AgentCreate(
            name="Simple Bot",
            system_prompt="Hello",
            tools=[],
        )
        assert agent.tools == []

    def test_agent_create_empty_name(self):
        with pytest.raises(ValidationError):
            AgentCreate(name="", system_prompt="test", tools=[])

    def test_agent_update_partial(self):
        update = AgentUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.system_prompt is None
        assert update.tools is None


# ==================== Workflow Schemas ====================


class TestWorkflowSchemas:
    """工作流 Schema 测试"""

    def test_valid_workflow_create(self):
        wf = WorkflowCreate(
            name="翻译工作流",
            description="自动翻译流程",
            graph_data={
                "nodes": [{"id": "start", "type": "start"}],
                "edges": [],
            },
        )
        assert wf.name == "翻译工作流"
        assert len(wf.graph_data["nodes"]) == 1

    def test_workflow_create_empty_name(self):
        with pytest.raises(ValidationError):
            WorkflowCreate(name="", graph_data={})

    def test_workflow_update_partial(self):
        update = WorkflowUpdate(name="Updated Workflow")
        assert update.name == "Updated Workflow"
        assert update.graph_data is None


# ==================== App Schemas ====================


class TestAppSchemas:
    """应用 Schema 测试"""

    def test_valid_app_create_chatbot(self):
        app = AppCreate(
            name="智能客服",
            app_type="chatbot",
            config={"system_prompt": "你好"},
        )
        assert app.app_type == "chatbot"

    def test_valid_app_create_completion(self):
        app = AppCreate(
            name="文案生成",
            app_type="completion",
            config={"prompt": "生成一段关于 {{topic}} 的文案"},
        )
        assert app.app_type == "completion"

    def test_valid_app_create_workflow(self):
        app = AppCreate(
            name="数据分析",
            app_type="workflow",
            config={"workflow_id": "some-uuid"},
        )
        assert app.app_type == "workflow"

    def test_app_create_invalid_type(self):
        """无效的应用类型应失败"""
        with pytest.raises(ValidationError):
            AppCreate(name="Test", app_type="invalid", config={})

    def test_app_create_empty_name(self):
        with pytest.raises(ValidationError):
            AppCreate(name="", app_type="chatbot", config={})

    def test_app_update_publish(self):
        update = AppUpdate(is_published=True)
        assert update.is_published is True
        assert update.name is None

    def test_app_update_config(self):
        update = AppUpdate(config={"model": "gpt-4"})
        assert update.config == {"model": "gpt-4"}


# ==================== Chat Schemas ====================


class TestChatSchemas:
    """聊天 Schema 测试"""

    def test_valid_chat_request(self):
        req = ChatRequest(message="你好")
        assert req.message == "你好"
        assert req.conversation_id is None

    def test_chat_request_empty_message(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="")

    def test_chat_request_too_long(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="x" * 10001)
