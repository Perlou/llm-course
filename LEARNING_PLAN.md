# 大模型应用开发完整学习计划

> **定制对象**：资深全栈工程师向大模型应用开发工程师转型  
> **前置条件**：已完成 deep-learning-course 课程（掌握 PyTorch、Transformer、LLM 基础原理）  
> **学习方式**：基于 Python + LangChain/LlamaIndex 的理论与实践结合学习  
> **预计时长**：16-20 周（每周投入 10-15 小时）  
> **当前进度**：🔄 准备开始第 1 阶段

---

## 📊 当前学习状态评估

### 🎯 学习目标

1. 掌握主流 LLM API 的使用方法
2. 熟练运用提示工程技术
3. 构建企业级 RAG 知识库系统
4. 设计和实现自主 Agent 系统
5. 掌握 LLM 微调与部署技术
6. 具备 LLM 应用全栈开发能力

---

## 🗺️ 详细学习计划

### 阶段 1：LLM 基础与 API 调用 (1 周)

> **目标**：掌握主流 LLM API 的调用方法

#### 第 1 周：API 调用基础

- [ ] **OpenAI API**
  - 创建 `01-openai-api-basics.py`：Chat Completions API
  - 创建 `02-openai-parameters.py`：temperature、top_p、max_tokens
  - 创建 `03-streaming-responses.py`：流式响应处理

- [ ] **其他 LLM 提供商**
  - 创建 `04-anthropic-claude.py`：Claude API 使用
  - 创建 `05-google-gemini.py`：Gemini API 使用
  - 创建 `06-local-llm-ollama.py`：使用 Ollama 本地部署

- [ ] **API 最佳实践**
  - 创建 `07-error-handling.py`：错误处理与重试机制
  - 创建 `08-rate-limiting.py`：速率限制与并发控制

- [ ] **实战项目**：多模型对比聊天应用

---

### 阶段 2：提示工程 (1-2 周)

> **目标**：掌握提示工程的核心技术

#### 第 2 周：基础提示技术

- [ ] **提示基础**
  - 创建 `01-prompt-anatomy.py`：提示词结构解析
  - 创建 `02-system-prompts.py`：系统提示词设计
  - 创建 `03-instruction-tuning.py`：指令优化技巧

- [ ] **进阶技术**
  - 创建 `04-few-shot-learning.py`：少样本学习
  - 创建 `05-chain-of-thought.py`：思维链提示
  - 创建 `06-self-consistency.py`：自洽性提示

#### 第 3 周：高级提示技术

- [ ] **结构化输出**
  - 创建 `07-json-output.py`：JSON 格式输出
  - 创建 `08-structured-extraction.py`：结构化信息提取

- [ ] **提示优化**
  - 创建 `09-prompt-templates.py`：提示词模板设计
  - 创建 `10-adversarial-prompting.py`：对抗性提示与防护

- [ ] **实战项目**：智能客服提示词系统

---

### 阶段 3：LangChain 基础 (1-2 周)

> **目标**：掌握 LangChain 框架核心组件

#### 第 4 周：LangChain 核心

- [ ] **基础组件**
  - 创建 `01-langchain-intro.py`：LangChain 架构概述
  - 创建 `02-llm-models.py`：LLM 模型封装
  - 创建 `03-prompt-templates.py`：提示词模板

- [ ] **链式调用**
  - 创建 `04-chains-basics.py`：Chain 基础
  - 创建 `05-lcel-expressions.py`：LCEL 表达式
  - 创建 `06-sequential-chains.py`：顺序链

- [ ] **记忆与状态**
  - 创建 `07-memory-types.py`：记忆类型详解
  - 创建 `08-conversation-memory.py`：会话记忆实现
  - 创建 `09-memory-persistence.py`：记忆持久化

- [ ] **输出解析**
  - 创建 `10-output-parsers.py`：输出解析器

- [ ] **实战项目**：多轮对话聊天机器人

---

### 阶段 4：RAG 基础 (1-2 周)

> **目标**：掌握 RAG 系统的核心原理与基础实现

#### 第 5 周：RAG 核心组件

- [ ] **文档处理**
  - 创建 `01-document-loaders.py`：文档加载器
  - 创建 `02-text-splitters.py`：文本分割策略
  - 创建 `03-document-transformers.py`：文档转换

- [ ] **向量存储**
  - 创建 `04-embeddings-basics.py`：Embedding 模型
  - 创建 `05-vector-stores-intro.py`：向量数据库概述
  - 创建 `06-chroma-basics.py`：Chroma 使用
  - 创建 `07-pinecone-basics.py`：Pinecone 使用

- [ ] **检索与生成**
  - 创建 `08-retrieval-basics.py`：基础检索
  - 创建 `09-qa-chains.py`：问答链
  - 创建 `10-conversational-rag.py`：对话式 RAG

- [ ] **实战项目**：个人知识库问答系统

---

### 阶段 5：RAG 进阶 (2 周)

> **目标**：掌握高级 RAG 技术

#### 第 6 周：检索优化

- [ ] **检索策略**
  - 创建 `01-hybrid-search.py`：混合检索
  - 创建 `02-reranking.py`：重排序技术
  - 创建 `03-parent-document-retriever.py`：父文档检索

- [ ] **查询优化**
  - 创建 `04-query-expansion.py`：查询扩展
  - 创建 `05-multi-query-retrieval.py`：多查询检索
  - 创建 `06-self-query-retrieval.py`：自查询检索

#### 第 7 周：高级 RAG 架构

- [ ] **高级技术**
  - 创建 `07-hypothetical-questions.py`：假设问题嵌入
  - 创建 `08-contextual-compression.py`：上下文压缩
  - 创建 `09-ensemble-retrieval.py`：集成检索

- [ ] **RAG 评估**
  - 创建 `10-rag-evaluation-metrics.py`：RAG 评估指标

- [ ] **实战项目**：企业级文档问答系统

---

### 阶段 6：Agent 与工具调用 (2 周)

> **目标**：掌握 Agent 设计与工具使用

#### 第 8 周：Agent 基础

- [ ] **Agent 概念**
  - 创建 `01-agent-fundamentals.py`：Agent 基础概念
  - 创建 `02-react-agent.py`：ReAct Agent
  - 创建 `03-agent-types.py`：Agent 类型对比

- [ ] **工具调用**
  - 创建 `04-tool-basics.py`：工具定义与调用
  - 创建 `05-custom-tools.py`：自定义工具开发
  - 创建 `06-openai-functions.py`：OpenAI Function Calling

#### 第 9 周：Agent 进阶

- [ ] **高级 Agent**
  - 创建 `07-plan-and-execute.py`：计划执行 Agent
  - 创建 `08-self-ask-agent.py`：自问自答 Agent
  - 创建 `09-tool-router.py`：工具路由

- [ ] **Agent 优化**
  - 创建 `10-agent-memory.py`：Agent 记忆管理

- [ ] **实战项目**：自动化研究助手

---

### 阶段 7：多 Agent 系统 (1-2 周)

> **目标**：掌握多 Agent 协作系统设计

#### 第 10 周：多 Agent 架构

- [ ] **多 Agent 基础**
  - 创建 `01-multi-agent-intro.py`：多 Agent 概述
  - 创建 `02-langgraph-basics.py`：LangGraph 基础
  - 创建 `03-agent-communication.py`：Agent 通信

- [ ] **协作模式**
  - 创建 `04-supervisor-agent.py`：主管 Agent 模式
  - 创建 `05-hierarchical-agents.py`：层级 Agent
  - 创建 `06-debate-agents.py`：辩论式 Agent

- [ ] **工作流设计**
  - 创建 `07-agent-workflows.py`：Agent 工作流
  - 创建 `08-human-in-the-loop.py`：人机协作

- [ ] **实战项目**：AI 内容创作团队

---

### 阶段 8：LLM 微调 (2 周)

> **目标**：掌握 LLM 微调技术

#### 第 11 周：微调基础

- [ ] **微调概述**
  - 创建 `01-finetuning-overview.py`：微调方法概述
  - 创建 `02-dataset-preparation.py`：数据集准备
  - 创建 `03-instruction-dataset.py`：指令数据集构建

- [ ] **参数高效微调**
  - 创建 `04-lora-basics.py`：LoRA 原理与实现
  - 创建 `05-qlora.py`：QLoRA 量化微调
  - 创建 `06-peft-library.py`：PEFT 库使用

#### 第 12 周：微调实践

- [ ] **微调实践**
  - 创建 `07-supervised-finetuning.py`：监督微调
  - 创建 `08-dpo-training.py`：DPO 训练
  - 创建 `09-model-merging.py`：模型合并

- [ ] **微调评估**
  - 创建 `10-finetuning-evaluation.py`：微调效果评估

- [ ] **实战项目**：领域特定助手微调

---

### 阶段 9：部署与生产化 (2 周)

> **目标**：掌握 LLM 应用的生产部署

#### 第 13 周：推理优化

- [ ] **推理加速**
  - 创建 `01-quantization-basics.py`：模型量化
  - 创建 `02-vllm-deployment.py`：vLLM 部署
  - 创建 `03-tgi-deployment.py`：TGI 部署

- [ ] **服务化**
  - 创建 `04-fastapi-llm-service.py`：FastAPI 服务
  - 创建 `05-async-processing.py`：异步处理
  - 创建 `06-batch-inference.py`：批量推理

#### 第 14 周：生产化

- [ ] **生产化**
  - 创建 `07-docker-deployment.py`：Docker 部署
  - 创建 `08-kubernetes-scaling.py`：K8s 扩展
  - 创建 `09-monitoring-logging.py`：监控与日志

- [ ] **安全与合规**
  - 创建 `10-security-guardrails.py`：安全护栏

- [ ] **实战项目**：LLM API 服务平台

---

### 阶段 10：评估与优化 (1-2 周)

> **目标**：掌握 LLM 应用的评估与优化方法

#### 第 15 周：评估体系

- [ ] **评估方法**
  - 创建 `01-evaluation-overview.py`：评估方法概述
  - 创建 `02-automatic-evaluation.py`：自动评估
  - 创建 `03-llm-as-judge.py`：LLM 作为评判者

- [ ] **RAG 评估**
  - 创建 `04-ragas-evaluation.py`：Ragas 评估框架
  - 创建 `05-contextual-relevance.py`：上下文相关性
  - 创建 `06-faithfulness.py`：忠实度评估

- [ ] **优化策略**
  - 创建 `07-prompt-optimization.py`：提示词优化
  - 创建 `08-cost-optimization.py`：成本优化

- [ ] **实战项目**：评估仪表板

---

### 阶段 11：多模态应用 (1-2 周)

> **目标**：掌握多模态 LLM 应用开发

#### 第 16 周：多模态技术

- [ ] **视觉语言模型**
  - 创建 `01-vision-llm-basics.py`：视觉 LLM 基础
  - 创建 `02-gpt4-vision.py`：GPT-4V 使用
  - 创建 `03-image-understanding.py`：图像理解

- [ ] **多模态应用**
  - 创建 `04-document-ocr.py`：文档 OCR 处理
  - 创建 `05-chart-analysis.py`：图表分析
  - 创建 `06-video-understanding.py`：视频理解

- [ ] **语音集成**
  - 创建 `07-speech-to-text.py`：语音转文字
  - 创建 `08-text-to-speech.py`：文字转语音

- [ ] **实战项目**：多模态文档助手

---

### 阶段 12：综合项目实战 (2-4 周)

> **目标**：整合所学知识完成企业级项目

#### 第 17-20 周：综合项目

- [ ] **项目 1：企业级知识库系统**
  - 创建 `01-knowledge-base-architecture.py`：架构设计
  - 创建 `02-knowledge-base-implementation.py`：完整实现

- [ ] **项目 2：AI 客服系统**
  - 创建 `03-customer-service-design.py`：系统设计
  - 创建 `04-customer-service-implementation.py`：完整实现

- [ ] **项目 3：代码助手**
  - 创建 `05-code-assistant-design.py`：系统设计
  - 创建 `06-code-assistant-implementation.py`：完整实现

- [ ] **项目 4：个人 AI 助理**
  - 综合运用 Agent、RAG、多模态能力

---

## 🎓 配套学习资源

### 必读文档

- [ ] OpenAI 官方文档
- [ ] Anthropic Claude 文档
- [ ] LangChain 官方文档
- [ ] LlamaIndex 官方文档

### 推荐阅读

- [ ] 《Building LLM Apps》- O'Reilly
- [ ] 《Prompt Engineering Guide》- DAIR.AI
- [ ] 《RAG Survey》- 相关论文

### 关键论文阅读

| 阶段    | 论文                                    | 必读程度   |
| ------- | --------------------------------------- | ---------- |
| Phase 2 | Chain-of-Thought Prompting              | ⭐⭐⭐⭐⭐ |
| Phase 4 | RAG: Retrieval-Augmented Generation     | ⭐⭐⭐⭐⭐ |
| Phase 6 | ReAct: Synergizing Reasoning and Acting | ⭐⭐⭐⭐⭐ |
| Phase 7 | LangGraph Paper                         | ⭐⭐⭐⭐   |
| Phase 8 | LoRA: Low-Rank Adaptation               | ⭐⭐⭐⭐⭐ |

---

## 📝 学习方法建议

### 1️⃣ 实践先行

每个概念先运行代码、观察结果，再深入理解原理。

### 2️⃣ 积累 Prompt 库

将所有有效的提示词模板收集到 `prompts/` 目录。

### 3️⃣ 项目驱动学习

每个阶段末尾完成对应实战项目，巩固所学。

### 4️⃣ 关注最新动态

LLM 领域发展迅速，定期阅读最新论文和博客。

### 5️⃣ 成本意识

学习使用开源模型（如 Llama、Qwen）减少 API 开支。

---

## 🎯 学习里程碑检查

### 第 4 周后（Phase 1-3 完成）

- [ ] 熟练调用主流 LLM API
- [ ] 掌握提示工程核心技术
- [ ] LangChain 基础组件熟练使用
- [ ] 完成多轮对话机器人项目

### 第 8 周后（Phase 4-5 完成）

- [ ] RAG 系统设计与实现能力
- [ ] 掌握检索优化技术
- [ ] 完成知识库问答项目

### 第 12 周后（Phase 6-8 完成）

- [ ] Agent 设计与工具调用能力
- [ ] 多 Agent 系统设计能力
- [ ] LLM 微调能力
- [ ] 完成研究助手项目

### 第 16 周后（Phase 9-11 完成）

- [ ] LLM 应用部署能力
- [ ] 评估与优化能力
- [ ] 多模态应用开发能力

### 第 20 周后（全部完成）

- [ ] 企业级 LLM 应用全栈开发能力
- [ ] 具备独立设计 LLM 系统的能力
- [ ] 完成多个综合实战项目

---

## 💼 职业发展建议

### 作品集建设

将以下项目放入 GitHub：

1. `llm-course`（学习笔记库）
2. 企业级知识库系统（RAG）
3. AI 客服系统（Agent）
4. 领域微调模型（Fine-tuning）
5. LLM API 服务平台（Deployment）

### 技能关键词（简历优化）

完成本计划后，可以突出：

- LangChain / LlamaIndex 开发
- RAG 系统设计与优化
- Agent 系统开发
- LLM 微调（LoRA/QLoRA）
- LLM 应用部署（vLLM/TGI）
- 提示工程

### 目标岗位

- 大模型应用开发工程师
- AI 产品工程师
- LLM 解决方案架构师
- AI 平台工程师

---

## 📊 进度追踪

| 周次  | 阶段     | 完成文件数 | 实战项目         | 状态      |
| ----- | -------- | ---------- | ---------------- | --------- |
| 1     | Phase 1  | 0/8        | 多模型对比应用   | ⏳ 待开始 |
| 2-3   | Phase 2  | 0/10       | 智能客服提示词   | ⏳ 待开始 |
| 4     | Phase 3  | 0/10       | 多轮对话机器人   | ⏳ 待开始 |
| 5     | Phase 4  | 0/10       | 个人知识库       | ⏳ 待开始 |
| 6-7   | Phase 5  | 0/10       | 企业文档问答     | ⏳ 待开始 |
| 8-9   | Phase 6  | 0/10       | 自动化研究助手   | ⏳ 待开始 |
| 10    | Phase 7  | 0/8        | AI 内容创作团队  | ⏳ 待开始 |
| 11-12 | Phase 8  | 0/10       | 领域特定助手     | ⏳ 待开始 |
| 13-14 | Phase 9  | 0/10       | LLM API 服务平台 | ⏳ 待开始 |
| 15    | Phase 10 | 0/8        | 评估仪表板       | ⏳ 待开始 |
| 16    | Phase 11 | 0/8        | 多模态文档助手   | ⏳ 待开始 |
| 17-20 | Phase 12 | 0/6        | 综合项目         | ⏳ 待开始 |

---

**Good luck! 🚀**

有任何问题随时在代码注释或 `docs/` 中记录，养成持续学习和总结的习惯。
