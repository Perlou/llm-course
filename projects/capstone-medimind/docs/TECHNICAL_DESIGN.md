# MediMind - 技术架构设计文档

> 版本: v1.0  
> 更新日期: 2026-02-03  
> 项目类型: LLM 课程毕业项目

---

## 1. 系统架构总览

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MediMind 系统架构                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        Presentation Layer                         │   │
│  │  ┌──────────────────────────────────────────────────────────────┐│   │
│  │  │                     React Frontend                           ││   │
│  │  │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   ││   │
│  │  │   │ 健康问答  │  │ 药品查询  │  │ 报告解读  │  │ 智能导诊  │   ││   │
│  │  │   └──────────┘  └──────────┘  └──────────┘  └──────────┘   ││   │
│  │  └──────────────────────────────────────────────────────────────┘│   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                          API Layer                                │   │
│  │  ┌──────────────────────────────────────────────────────────────┐│   │
│  │  │                     FastAPI Backend                          ││   │
│  │  │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   ││   │
│  │  │   │ /health  │  │ /drug    │  │ /report  │  │ /triage  │   ││   │
│  │  │   └──────────┘  └──────────┘  └──────────┘  └──────────┘   ││   │
│  │  └──────────────────────────────────────────────────────────────┘│   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      Guardrails Layer                             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │   │
│  │  │ 输入安全检查  │  │ 输出合规检查 │  │ 紧急情况检测 │           │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        Service Layer                              │   │
│  │                                                                   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │   │
│  │  │ RAG Service  │  │ Agent Service│  │ Multimodal   │           │   │
│  │  │              │  │              │  │ Service      │           │   │
│  │  │ · 知识检索   │  │ · 导诊对话    │  │ · 图像识别   │           │   │
│  │  │ · 问答生成   │  │ · 症状分析    │  │ · 报告解读   │           │   │
│  │  │ · 来源引用   │  │ · 科室推荐    │  │ · 指标提取   │           │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                         Core Layer                                │   │
│  │                                                                   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │   │
│  │  │ Embedder     │  │ VectorStore  │  │ LLM Engine   │           │   │
│  │  │              │  │              │  │              │           │   │
│  │  │ BGE-Large-ZH │  │ Chroma       │  │ Gemini Flash │           │   │
│  │  │              │  │              │  │ / Qwen       │           │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        Storage Layer                              │   │
│  │                                                                   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │   │
│  │  │ PostgreSQL   │  │ Chroma Index │  │ File System  │           │   │
│  │  │              │  │              │  │              │           │   │
│  │  │ 元数据存储   │  │ 向量索引     │  │ 医学文档     │           │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 技术选型

| 层级   | 组件            | 技术选型            | 选型理由                       |
| ------ | --------------- | ------------------- | ------------------------------ |
| 前端   | Monorepo        | Turborepo + pnpm    | 多端复用、统一构建、高效缓存   |
| 前端   | Web UI          | React + TypeScript  | 现代化、类型安全、组件化       |
| 前端   | UI 框架         | Tailwind CSS        | 高效开发、一致性、响应式       |
| 前端   | 组件库          | @medimind/ui 内部包 | 跨应用复用、设计系统统一       |
| 后端   | API Server      | FastAPI             | 高性能、自动文档、异步支持     |
| 嵌入   | Embedding Model | bge-large-zh-v1.5   | 中文效果优秀、开源免费         |
| 向量库 | Vector Store    | Chroma              | 轻量级、易集成、支持元数据过滤 |
| LLM    | Remote Model    | Gemini 2.0 Flash    | 多模态支持、响应快、成本低     |
| LLM    | Local Model     | Qwen2.5-7B (Ollama) | 本地备选、数据私有             |
| 数据库 | Metadata DB     | PostgreSQL          | 生产级、功能丰富               |
| 多模态 | Vision Model    | Gemini Vision       | 图像理解能力强                 |

---

## 2. 核心模块设计

### 2.1 安全护栏模块 (Guardrails)

> [!IMPORTANT]
> 安全护栏是 MediMind 的核心安全机制，所有请求和响应都必须经过护栏检查。

#### 2.1.1 输入检查器

```python
class InputGuardrail:
    """输入安全检查"""

    # 危险意图关键词
    DANGEROUS_PATTERNS = [
        r"如何自杀", r"如何自残", r"如何堕胎",
        r"帮我诊断", r"告诉我得了什么病",
        r"怎么买处方药", r"哪里可以买到.*处方",
    ]

    # 紧急症状关键词
    EMERGENCY_PATTERNS = [
        r"胸口剧烈疼痛", r"呼吸困难", r"意识模糊",
        r"大出血", r"昏迷", r"心跳停止",
    ]

    def check(self, query: str) -> GuardrailResult:
        # 1. 检测危险意图
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, query):
                return GuardrailResult(
                    passed=False,
                    action="BLOCK",
                    message="抱歉，这个问题我无法回答。建议您咨询专业医生。"
                )

        # 2. 检测紧急情况
        for pattern in self.EMERGENCY_PATTERNS:
            if re.search(pattern, query):
                return GuardrailResult(
                    passed=True,
                    action="EMERGENCY_ALERT",
                    message="⚠️ 如果您正在经历紧急症状，请立即拨打 120 急救电话！"
                )

        return GuardrailResult(passed=True)
```

#### 2.1.2 输出检查器

```python
class OutputGuardrail:
    """输出合规检查"""

    # 禁止出现的诊断性语言
    DIAGNOSTIC_PATTERNS = [
        r"您患有", r"您得了", r"确诊为",
        r"需要服用.*药", r"建议您用.*治疗",
    ]

    def check(self, response: str) -> GuardrailResult:
        # 1. 检测诊断性语言
        for pattern in self.DIAGNOSTIC_PATTERNS:
            if re.search(pattern, response):
                # 自动改写为建议性语言
                return GuardrailResult(
                    passed=False,
                    action="REWRITE",
                    rewritten=self._make_advisory(response)
                )

        # 2. 确保包含免责声明
        if not self._has_disclaimer(response):
            response += "\n\n⚕️ 以上信息仅供参考，如有健康问题请咨询专业医生。"

        return GuardrailResult(passed=True, content=response)
```

### 2.2 RAG 服务模块

#### 2.2.1 医学知识检索

```python
class MedicalRAGService:
    """健康知识问答服务"""

    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        llm: BaseLLM,
        guardrail: Guardrail
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.llm = llm
        self.guardrail = guardrail

    async def answer(self, query: str) -> HealthAnswer:
        # 1. 输入安全检查
        input_check = self.guardrail.check_input(query)
        if not input_check.passed:
            return HealthAnswer(
                content=input_check.message,
                sources=[],
                emergency=input_check.action == "EMERGENCY_ALERT"
            )

        # 2. 检索相关知识
        query_embedding = self.embedder.embed_query(query)
        chunks = self.vector_store.search(
            query_embedding,
            top_k=5,
            filter={"category": ["disease", "nutrition", "prevention"]}
        )

        # 3. 构建 Prompt
        prompt = self._build_prompt(query, chunks)

        # 4. 生成回答
        response = await self.llm.generate(prompt)

        # 5. 输出合规检查
        output_check = self.guardrail.check_output(response)
        final_response = output_check.content if output_check.passed else output_check.rewritten

        # 6. 提取来源
        sources = self._extract_sources(chunks)

        return HealthAnswer(
            content=final_response,
            sources=sources,
            emergency=input_check.action == "EMERGENCY_ALERT"
        )
```

#### 2.2.2 RAG Prompt 模板

```python
HEALTH_QA_PROMPT = """你是一个专业的健康信息助手。请基于以下参考内容回答用户的健康问题。

## 参考资料
{context}

## 重要注意事项
1. 只基于参考资料回答，不要编造医学信息
2. 使用通俗易懂的语言解释医学概念
3. 如果参考资料无法回答，请明确说明并建议咨询医生
4. 回答时标注信息来源：【来源: 文档名】
5. 不要给出诊断或处方建议
6. 适当建议用户在必要时就医

## 用户问题
{question}

## 回答
"""
```

### 2.3 导诊 Agent 模块

#### 2.3.1 Agent 架构

```python
from langgraph.graph import StateGraph, END

class TriageState(TypedDict):
    """导诊状态"""
    messages: List[Message]
    symptoms: List[str]
    duration: Optional[str]
    severity: Optional[str]
    history: List[str]
    recommendation: Optional[str]
    department: Optional[str]
    is_emergency: bool

class TriageAgent:
    """智能导诊 Agent"""

    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(TriageState)

        # 添加节点
        workflow.add_node("analyze_symptoms", self.analyze_symptoms)
        workflow.add_node("check_emergency", self.check_emergency)
        workflow.add_node("ask_duration", self.ask_duration)
        workflow.add_node("ask_severity", self.ask_severity)
        workflow.add_node("recommend_department", self.recommend_department)
        workflow.add_node("generate_advice", self.generate_advice)

        # 定义边
        workflow.set_entry_point("analyze_symptoms")
        workflow.add_edge("analyze_symptoms", "check_emergency")
        workflow.add_conditional_edges(
            "check_emergency",
            self.should_emergency_exit,
            {
                "emergency": END,
                "continue": "ask_duration"
            }
        )
        workflow.add_edge("ask_duration", "ask_severity")
        workflow.add_edge("ask_severity", "recommend_department")
        workflow.add_edge("recommend_department", "generate_advice")
        workflow.add_edge("generate_advice", END)

        return workflow.compile()

    async def analyze_symptoms(self, state: TriageState) -> TriageState:
        """分析用户描述的症状"""
        user_message = state["messages"][-1].content

        prompt = f"""请从以下描述中提取症状关键词：

        描述：{user_message}

        以 JSON 格式返回症状列表。"""

        response = await self.llm.generate(prompt)
        symptoms = json.loads(response)

        return {**state, "symptoms": symptoms}

    async def check_emergency(self, state: TriageState) -> TriageState:
        """检测是否为紧急情况"""
        EMERGENCY_SYMPTOMS = [
            "胸痛", "呼吸困难", "意识障碍", "大出血",
            "剧烈头痛", "昏迷", "心悸", "抽搐"
        ]

        is_emergency = any(
            symptom in state["symptoms"]
            for symptom in EMERGENCY_SYMPTOMS
        )

        return {**state, "is_emergency": is_emergency}
```

### 2.4 多模态报告解读模块

#### 2.4.1 图像处理流程

```
┌─────────────────────────────────────────────────────────────┐
│                    报告解读流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   用户上传报告图片                                           │
│         │                                                   │
│         ▼                                                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │   图像预处理 (PIL + OpenCV)                         │   │
│   │   · 旋转校正                                         │   │
│   │   · 对比度增强                                       │   │
│   └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │   Gemini Vision 识别                                 │   │
│   │   · 表格结构识别                                     │   │
│   │   · 指标数值提取                                     │   │
│   │   · 单位识别                                         │   │
│   └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │   指标分析                                           │   │
│   │   · 与正常范围对比                                   │   │
│   │   · 异常标记                                         │   │
│   │   · 科普解释                                         │   │
│   └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │   生成解读报告                                       │   │
│   │   · 正常指标简述                                     │   │
│   │   · 异常指标详解                                     │   │
│   │   · 就医建议                                         │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 2.4.2 服务实现

```python
class ReportAnalysisService:
    """体检报告解读服务"""

    def __init__(
        self,
        vision_model: GeminiVision,
        lab_index_db: LabIndexDatabase,
        guardrail: Guardrail
    ):
        self.vision = vision_model
        self.lab_db = lab_index_db
        self.guardrail = guardrail

    async def analyze_report(self, image: bytes) -> ReportAnalysis:
        # 1. 使用视觉模型提取报告内容
        extraction_prompt = """请识别这张体检/化验报告图片中的所有检测项目。

        对于每个项目，提取：
        - 项目名称
        - 检测数值
        - 单位
        - 参考范围（如有）

        以 JSON 数组格式返回。"""

        raw_data = await self.vision.analyze(image, extraction_prompt)
        items = json.loads(raw_data)

        # 2. 解析每个指标
        analyzed_items = []
        for item in items:
            # 从数据库查询指标信息
            index_info = self.lab_db.get_by_name(item["name"])

            if index_info:
                status = self._check_status(
                    item["value"],
                    index_info.normal_range
                )

                analyzed_items.append(LabItem(
                    name=item["name"],
                    value=item["value"],
                    unit=item["unit"],
                    normal_range=index_info.normal_range,
                    status=status,
                    explanation=index_info.description,
                    high_meaning=index_info.high_meaning if status == "HIGH" else None,
                    low_meaning=index_info.low_meaning if status == "LOW" else None
                ))

        # 3. 生成综合解读
        summary = await self._generate_summary(analyzed_items)

        # 4. 输出检查
        summary = self.guardrail.check_output(summary).content

        return ReportAnalysis(
            items=analyzed_items,
            summary=summary,
            abnormal_count=len([i for i in analyzed_items if i.status != "NORMAL"]),
            should_consult_doctor=self._should_consult(analyzed_items)
        )
```

---

## 3. 目录结构设计

```
capstone-medimind/
├── configs/                          # 配置文件
│   ├── config.yaml                   # 主配置文件
│   ├── prompts.yaml                  # Prompt 模板
│   └── guardrails.yaml               # 安全规则配置
│
├── src/                              # 后端源代码
│   ├── __init__.py
│   │
│   ├── api/                          # FastAPI 接口
│   │   ├── __init__.py
│   │   ├── main.py                   # 应用入口
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── health_qa.py          # 健康问答接口
│   │   │   ├── drug.py               # 药品查询接口
│   │   │   ├── report.py             # 报告解读接口
│   │   │   └── triage.py             # 智能导诊接口
│   │   ├── schemas/                  # Pydantic 模型
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   ├── drug.py
│   │   │   └── report.py
│   │   ├── middleware/
│   │   │   └── guardrail.py          # 安全中间件
│   │   └── dependencies.py           # 依赖注入
│   │
│   ├── core/                         # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── embedder.py               # 嵌入模型
│   │   ├── vector_store.py           # 向量存储
│   │   ├── llm_engine.py             # LLM 推理
│   │   ├── rag_service.py            # RAG 服务
│   │   ├── triage_agent.py           # 导诊 Agent
│   │   ├── report_analyzer.py        # 报告分析
│   │   └── guardrails.py             # 安全护栏
│   │
│   ├── models/                       # 数据模型
│   │   ├── __init__.py
│   │   ├── database.py               # 数据库初始化
│   │   └── entities.py               # ORM 实体
│   │
│   ├── parsers/                      # 文档解析器
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── pdf_parser.py
│   │   └── medical_doc_parser.py
│   │
│   └── utils/                        # 工具函数
│       ├── __init__.py
│       ├── logger.py
│       └── helpers.py
│
├── frontend/                         # 前端 Monorepo (Turborepo)
│   ├── turbo.json                    # Turborepo 配置
│   ├── pnpm-workspace.yaml           # pnpm workspace 配置
│   ├── package.json                  # 根 package.json
│   │
│   ├── apps/                         # 应用层
│   │   ├── web/                      # Web 应用
│   │   │   ├── package.json
│   │   │   ├── vite.config.ts
│   │   │   ├── tailwind.config.js
│   │   │   ├── src/
│   │   │   │   ├── App.tsx
│   │   │   │   ├── main.tsx
│   │   │   │   ├── pages/
│   │   │   │   │   ├── HomePage.tsx
│   │   │   │   │   ├── HealthQAPage.tsx
│   │   │   │   │   ├── DrugSearchPage.tsx
│   │   │   │   │   ├── ReportPage.tsx
│   │   │   │   │   └── TriagePage.tsx
│   │   │   │   └── routes/
│   │   │   └── public/
│   │   │
│   │   └── mobile/                   # (未来) React Native 应用
│   │       └── placeholder.md
│   │
│   └── packages/                     # 共享包层
│       ├── ui/                       # @medimind/ui 组件库
│       │   ├── package.json
│       │   ├── src/
│       │   │   ├── index.ts
│       │   │   ├── components/
│       │   │   │   ├── ChatMessage.tsx
│       │   │   │   ├── SourceCard.tsx
│       │   │   │   ├── DrugCard.tsx
│       │   │   │   ├── ReportViewer.tsx
│       │   │   │   ├── EmergencyAlert.tsx
│       │   │   │   └── SafetyBanner.tsx
│       │   │   └── primitives/
│       │   │       ├── Button.tsx
│       │   │       ├── Card.tsx
│       │   │       └── Input.tsx
│       │   └── tailwind.config.js
│       │
│       ├── api-client/               # @medimind/api-client SDK
│       │   ├── package.json
│       │   └── src/
│       │       ├── index.ts
│       │       ├── health.ts
│       │       ├── drug.ts
│       │       ├── report.ts
│       │       └── triage.ts
│       │
│       ├── config/                   # @medimind/config 共享配置
│       │   ├── package.json
│       │   ├── eslint-preset.js
│       │   └── tailwind-preset.js
│       │
│       └── types/                    # @medimind/types 类型定义
│           ├── package.json
│           └── src/
│               ├── index.ts
│               ├── health.ts
│               ├── drug.ts
│               └── report.ts
│
├── data/                             # 数据目录
│   ├── medical_docs/                 # 医学文档
│   ├── drug_db/                      # 药品数据
│   ├── lab_indices/                  # 检验指标
│   └── chroma_index/                 # 向量索引
│
├── tests/                            # 后端测试
│   ├── test_guardrails.py
│   ├── test_rag.py
│   ├── test_triage.py
│   └── test_report.py
│
├── scripts/                          # 脚本
│   ├── init_db.py
│   ├── load_medical_data.py
│   ├── start_backend.sh
│   └── start_frontend.sh
│
├── docker/                           # Docker 配置
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yaml
│
├── docs/                             # 项目文档
│   ├── PRD.md
│   ├── TECHNICAL_DESIGN.md
│   ├── API_DESIGN.md
│   └── PROGRESS_TRACKER.md
│
├── designs/                          # UI 设计稿
│   └── UI_DESIGN_SPEC.md
│
├── requirements.txt
└── README.md
```

### 3.1 前端 Monorepo 架构说明

#### 为什么选择 Turborepo

| 优势     | 说明                                        |
| -------- | ------------------------------------------- |
| 多端复用 | 为未来移动端 (React Native)、桌面端打下基础 |
| 代码共享 | UI 组件、API Client、类型定义跨应用共享     |
| 统一构建 | 一条命令构建所有应用                        |
| 增量构建 | 智能缓存，只构建变更部分                    |
| 依赖管理 | pnpm workspace 高效管理依赖                 |

#### 包职责划分

| 包名                   | 路径                  | 职责                      |
| ---------------------- | --------------------- | ------------------------- |
| `@medimind/web`        | `apps/web`            | Web 应用主入口            |
| `@medimind/ui`         | `packages/ui`         | 共享 UI 组件库            |
| `@medimind/api-client` | `packages/api-client` | 后端 API 调用封装         |
| `@medimind/types`      | `packages/types`      | TypeScript 类型定义       |
| `@medimind/config`     | `packages/config`     | 共享 ESLint/Tailwind 配置 |

#### Turborepo 配置示例

```json
// frontend/turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["build"]
    }
  }
}
```

```yaml
# frontend/pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
```

---

## 4. API 设计概览

### 4.1 健康问答 API

```yaml
POST /api/v1/health/chat
  Request:
    query: string
    conversation_id?: string
  Response:
    answer: string
    sources: Source[]
    emergency_alert?: string
    conversation_id: string
```

### 4.2 药品查询 API

```yaml
GET /api/v1/drug/search?q={keyword}
  Response:
    drugs: Drug[]

GET /api/v1/drug/{drug_id}
  Response:
    drug: DrugDetail

POST /api/v1/drug/interaction
  Request:
    drug_ids: string[]
  Response:
    interactions: Interaction[]
```

### 4.3 报告解读 API

```yaml
POST /api/v1/report/analyze
  Request:
    image: File (multipart/form-data)
  Response:
    items: LabItem[]
    summary: string
    abnormal_count: number
    should_consult: boolean
```

### 4.4 智能导诊 API

```yaml
POST /api/v1/triage/start
  Response:
    session_id: string
    message: string

POST /api/v1/triage/chat
  Request:
    session_id: string
    message: string
  Response:
    message: string
    is_complete: boolean
    recommendation?: TriageResult
```

---

## 5. 部署架构

### 5.1 Docker 部署

```yaml
# docker-compose.yaml
version: "3.8"

services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/medimind
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - USE_OLLAMA=${USE_OLLAMA:-false}
    depends_on:
      - db
    volumes:
      - ./data:/app/data

  frontend:
    build:
      context: ./src/frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000

  db:
    image: postgres:16
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=medimind
    volumes:
      - postgres_data:/var/lib/postgresql/data

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    profiles:
      - local-llm

volumes:
  postgres_data:
  ollama_data:
```

---

## 附录

### A. 依赖列表

```txt
# requirements.txt

# Web Framework
fastapi>=0.109.0
uvicorn>=0.27.0
python-multipart>=0.0.6

# LLM & Embedding
google-generativeai>=0.5.0
langchain>=0.1.0
langgraph>=0.0.20
sentence-transformers>=2.3.0

# Vector Store
chromadb>=0.4.0

# Database
sqlalchemy>=2.0.0
asyncpg>=0.29.0
psycopg2-binary>=2.9.0

# Image Processing
pillow>=10.0.0
opencv-python>=4.9.0

# Utils
pydantic>=2.5.0
pyyaml>=6.0.0
python-dotenv>=1.0.0
httpx>=0.26.0
```

### B. 课程技术应用映射

| 课程阶段  | 技术             | 项目应用             |
| --------- | ---------------- | -------------------- |
| Phase 1   | API 调用         | Gemini/Ollama 集成   |
| Phase 2   | 提示工程         | 医疗问答 Prompt 设计 |
| Phase 3   | LangChain        | 链式调用、输出解析   |
| Phase 4-5 | RAG              | 医学知识库问答       |
| Phase 6   | Agent + 工具调用 | 导诊 Agent           |
| Phase 7   | Multi-Agent      | 多轮问诊对话         |
| Phase 9   | 部署             | Docker 生产化部署    |
| Phase 10  | 评估             | 问答质量评估         |
| Phase 11  | 多模态           | 报告图像解读         |
