# 🤖 大模型应用开发课程 (LLM Application Development)

> **定制对象**：资深全栈工程师向大模型应用开发工程师转型  
> **前置要求**：已完成 deep-learning-course 课程学习  
> **学习方式**：基于 Python + LangChain/LlamaIndex 的理论与实践结合学习  
> **预计时长**：16-20 周（每周投入 10-15 小时）

---

## 🚀 快速开始

### 1. 环境准备

```bash
cd /llm-course

# 创建并激活虚拟环境
python3 -m venv venv && source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置 API Keys（创建 .env 文件）
cp .env.example .env
# 编辑 .env 填入你的 API Keys
```

### 2. 按阶段学习

所有代码已按学习阶段组织，详见下方 [🎓 按阶段学习](#-按阶段学习) 部分。

```bash
# 第一个示例：LLM API 调用
python src/phase-1-llm-fundamentals/01-openai-api-basics.py

# 或使用 Jupyter Notebook
jupyter lab notebooks/
```

---

## 📂 项目结构

```
llm-course/
├── README.md                    # 课程介绍与快速开始
├── ROADMAP.md                   # 学习路线图（可视化）
├── LEARNING_PLAN.md             # 详细学习计划
├── CONCEPTS.md                  # 核心概念汇总文档
├── requirements.txt             # Python 依赖
├── .env.example                 # 环境变量模板
├── src/
│   ├── phase-1-llm-fundamentals/     # 第1阶段：LLM基础与API调用
│   ├── phase-2-prompt-engineering/   # 第2阶段：提示工程
│   ├── phase-3-langchain-basics/     # 第3阶段：LangChain基础
│   ├── phase-4-rag-fundamentals/     # 第4阶段：RAG基础
│   ├── phase-5-rag-advanced/         # 第5阶段：RAG进阶
│   ├── phase-6-agents-tools/         # 第6阶段：Agent与工具调用
│   ├── phase-7-multi-agent/          # 第7阶段：多Agent系统
│   ├── phase-8-llm-finetuning/       # 第8阶段：LLM微调
│   ├── phase-9-deployment/           # 第9阶段：部署与生产化
│   ├── phase-10-evaluation/          # 第10阶段：评估与优化
│   ├── phase-11-multimodal/          # 第11阶段：多模态应用
│   ├── phase-12-advanced-projects/   # 第12阶段：综合项目实战
│   └── utils/                        # 工具函数
├── notebooks/                   # Jupyter Notebooks
├── docs/                        # 学习笔记与论文阅读
├── data/                        # 数据集目录
└── projects/                    # 实战项目
```

**重要文档**：

- 📖 [ROADMAP.md](./ROADMAP.md) - 学习路线图
- 📝 [CONCEPTS.md](./CONCEPTS.md) - 核心概念文档
- 🗺️ [LEARNING_PLAN.md](./LEARNING_PLAN.md) - 完整学习计划

---

## 🎓 按阶段学习

每个阶段目录都包含独立的 README.md，详细说明该阶段的学习目标、核心概念和运行方式。

### 第 1 阶段：LLM 基础与 API 调用

```bash
python src/phase-1-llm-fundamentals/01-openai-api-basics.py
python src/phase-1-llm-fundamentals/02-claude-api-basics.py
python src/phase-1-llm-fundamentals/03-streaming-responses.py
```

查看详情：[phase-1-llm-fundamentals/README.md](./src/phase-1-llm-fundamentals/README.md)

### 第 2 阶段：提示工程

```bash
python src/phase-2-prompt-engineering/01-basic-prompting.py
python src/phase-2-prompt-engineering/02-few-shot-learning.py
python src/phase-2-prompt-engineering/03-chain-of-thought.py
```

查看详情：[phase-2-prompt-engineering/README.md](./src/phase-2-prompt-engineering/README.md)

### 第 3 阶段：LangChain 基础

```bash
python src/phase-3-langchain-basics/01-chains.py
python src/phase-3-langchain-basics/02-memory.py
python src/phase-3-langchain-basics/03-output-parsers.py
```

查看详情：[phase-3-langchain-basics/README.md](./src/phase-3-langchain-basics/README.md)

### 第 4-12 阶段

查看完整的后续学习计划：[LEARNING_PLAN.md](./LEARNING_PLAN.md)

---

## 🛠️ 技术栈

- **Python 3.10+**
- **LangChain / LlamaIndex**
- **OpenAI API / Anthropic Claude API**
- **向量数据库**：Chroma、Pinecone、Weaviate
- **LLM 框架**：vLLM、Ollama
- **部署**：FastAPI、Docker、Kubernetes
- **评估**：Ragas、DeepEval

---

## 📈 学习进度追踪

| 阶段     | 主题                | 文件数 | 状态      |
| -------- | ------------------- | ------ | --------- |
| Phase 1  | LLM 基础与 API 调用 | 0/8    | ⏳ 待开始 |
| Phase 2  | 提示工程            | 0/10   | ⏳ 待开始 |
| Phase 3  | LangChain 基础      | 0/10   | ⏳ 待开始 |
| Phase 4  | RAG 基础            | 0/10   | ⏳ 待开始 |
| Phase 5  | RAG 进阶            | 0/10   | ⏳ 待开始 |
| Phase 6  | Agent 与工具调用    | 0/10   | ⏳ 待开始 |
| Phase 7  | 多 Agent 系统       | 0/8    | ⏳ 待开始 |
| Phase 8  | LLM 微调            | 0/10   | ⏳ 待开始 |
| Phase 9  | 部署与生产化        | 0/10   | ⏳ 待开始 |
| Phase 10 | 评估与优化          | 0/8    | ⏳ 待开始 |
| Phase 11 | 多模态应用          | 0/8    | ⏳ 待开始 |
| Phase 12 | 综合项目实战        | 0/6    | ⏳ 待开始 |

---

## 💼 职业发展目标

完成本课程后，你将具备以下能力：

- **LLM 应用开发**：熟练使用 LangChain/LlamaIndex 构建应用
- **RAG 系统设计**：构建企业级知识库问答系统
- **Agent 开发**：设计和实现自主 Agent 系统
- **LLM 微调**：使用 LoRA/QLoRA 进行参数高效微调
- **生产部署**：将 LLM 应用部署到生产环境
- **性能优化**：评估和优化 LLM 应用性能

### 目标岗位

- 大模型应用开发工程师
- AI 产品工程师
- LLM 解决方案架构师
- AI 平台工程师

---

**Good luck! 🚀**

有任何问题随时在代码注释或 `docs/` 中记录，养成持续学习和总结的习惯。
