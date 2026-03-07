"""
Mini-Dify - Pydantic Schemas (请求/响应)
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ==================== 通用 ====================


class ApiResponse(BaseModel):
    """统一响应格式"""

    code: int = 200
    message: str = "success"
    data: Optional[dict | list] = None


class PaginatedResponse(BaseModel):
    """分页响应"""

    items: list
    total: int
    page: int
    page_size: int


# ==================== Provider ====================


class ProviderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    provider_type: str = Field(..., pattern="^(openai|anthropic|google|ollama)$")
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    models: list = Field(default_factory=list)
    config: dict = Field(default_factory=dict)


class ProviderUpdate(BaseModel):
    name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    models: Optional[list] = None
    config: Optional[dict] = None
    is_active: Optional[bool] = None


class ProviderResponse(BaseModel):
    id: UUID
    name: str
    provider_type: str
    base_url: Optional[str]
    models: list
    config: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== Prompt ====================


class PromptCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    system_prompt: str = Field(..., min_length=1)
    user_prompt: str = Field(..., min_length=1)
    variables: list = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class PromptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    variables: Optional[list] = None
    tags: Optional[list[str]] = None


class PromptResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    system_prompt: str
    user_prompt: str
    variables: list
    tags: list[str]
    current_version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== Dataset ====================


class DatasetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    embedding_model: str = "bge-large-zh"
    chunk_size: int = Field(default=500, ge=100, le=2000)
    chunk_overlap: int = Field(default=50, ge=0, le=500)


class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    retrieval_config: Optional[dict] = None


class DatasetResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    document_count: int
    chunk_count: int
    retrieval_config: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    name: str
    file_type: str
    file_size: Optional[int]
    chunk_count: int
    status: str
    error_msg: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ==================== Agent ====================


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    system_prompt: str = Field(..., min_length=1)
    provider_id: Optional[UUID] = None
    model_name: str = Field(..., min_length=1)
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=2048, ge=1, le=128000)
    strategy: str = Field(default="react", pattern="^(react|function_calling)$")
    tool_ids: list[UUID] = Field(default_factory=list)
    dataset_ids: list[UUID] = Field(default_factory=list)


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    provider_id: Optional[UUID] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    strategy: Optional[str] = None
    tool_ids: Optional[list[UUID]] = None
    dataset_ids: Optional[list[UUID]] = None


class AgentResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    system_prompt: str
    provider_id: Optional[UUID]
    model_name: str
    temperature: float
    max_tokens: int
    strategy: str
    dataset_ids: list[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== Tool ====================


class ToolCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parameters: dict = Field(default_factory=dict)
    code: Optional[str] = None


class ToolResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    tool_type: str
    parameters: dict
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ==================== Workflow ====================


class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    graph_data: dict = Field(...)


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    graph_data: Optional[dict] = None
    status: Optional[str] = None


class WorkflowResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    graph_data: dict
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== App ====================


class AppCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    app_type: str = Field(..., pattern="^(chatbot|completion|workflow)$")
    config: dict = Field(...)


class AppUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[dict] = None
    is_published: Optional[bool] = None


class AppResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    app_type: str
    config: dict
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== Chat ====================


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[UUID] = None


class ChatResponse(BaseModel):
    message: str
    conversation_id: UUID
    provider_name: Optional[str] = None
    model_name: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0


# ==================== Model Hub (Health / Chat) ====================


class HealthCheckResponse(BaseModel):
    status: str
    latency_ms: int = 0
    error: Optional[str] = None


class ModelChatMessage(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str = Field(..., min_length=1)


class ModelChatRequest(BaseModel):
    provider_id: UUID
    model: str = Field(..., min_length=1)
    messages: list[ModelChatMessage] = Field(..., min_length=1)
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=2048, ge=1, le=128000)
    stream: bool = False


# ==================== Prompt Version & Test ====================


class PromptVersionResponse(BaseModel):
    id: UUID
    prompt_id: UUID
    version: int
    system_prompt: str
    user_prompt: str
    change_note: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class PromptTestModelConfig(BaseModel):
    provider_id: UUID
    model: str = Field(..., min_length=1)


class PromptTestRequest(BaseModel):
    variables: dict = Field(default_factory=dict)
    model_configs: list[PromptTestModelConfig] = Field(..., min_length=1)


class PromptTestResultItem(BaseModel):
    model: str
    provider_id: UUID
    response: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    error: Optional[str] = None


class PromptTestResponse(BaseModel):
    rendered_system_prompt: str
    rendered_user_prompt: str
    results: list[PromptTestResultItem]
