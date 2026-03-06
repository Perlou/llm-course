# Mini-Dify - 简化版 LLM 应用开发平台

> 🤖 可视化构建 AI 应用的开发平台 | LLM 课程毕业项目  
> 灵感来源: [Dify](https://github.com/langgenius/dify)

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)
![React](https://img.shields.io/badge/react-18.x-61dafb)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

---

## ✨ 核心功能

| 功能               | 说明                                  | 技术                   |
| ------------------ | ------------------------------------- | ---------------------- |
| 🔌 **模型管理**    | 统一管理 OpenAI/Claude/Gemini/Ollama  | LangChain 统一接口     |
| ✏️ **Prompt 工坊** | Prompt 模板编辑、变量注入、多模型测试 | Jinja2 + 版本管理      |
| 📚 **知识库**      | 文档上传 → 切分 → 索引 → 检索         | Milvus + BGE Embedding |
| 🤖 **Agent**       | 配置 Agent + 工具，Playground 测试    | LangGraph ReAct Agent  |
| 🔀 **工作流**      | 可视化拖拽编排 LLM 工作流             | React Flow + LangGraph |
| 📱 **应用管理**    | 创建 Chatbot/Completion/Workflow 应用 | 多类型应用工厂         |
| 🔑 **API 网关**    | 为应用生成 API Key，对外提供 REST API | FastAPI + SSE          |
| 📊 **监控面板**    | Token 统计、成本分析、对话日志        | Recharts 可视化        |

---

## 🚀 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+
- Docker + Docker Compose (用于 PostgreSQL 和 Milvus)
- pnpm / npm

### 启动项目

```bash
# 1. 克隆项目
git clone <repo-url> && cd capstone-mini-dify

# 2. 启动基础服务 (PostgreSQL + Milvus)
docker compose -f docker/docker-compose.yaml up -d postgres milvus

# 3. 后端
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 配置 API Key 和数据库连接
alembic upgrade head  # 执行数据库迁移

# 4. 前端
cd ../frontend
pnpm install

# 5. 启动
cd ..
./scripts/start.sh

# 访问: http://localhost:5173
```

---

## 🛠️ 技术栈

### 后端

| 技术                 | 用途         |
| -------------------- | ------------ |
| FastAPI              | Web 框架     |
| SQLAlchemy + Alembic | ORM + 迁移   |
| PostgreSQL           | 关系型数据库 |
| Milvus               | 向量数据库   |
| LangChain            | LLM 框架     |
| LangGraph            | 工作流引擎   |

### 前端

| 技术        | 用途       |
| ----------- | ---------- |
| React 18    | UI 框架    |
| TypeScript  | 类型安全   |
| TailwindCSS | 样式框架   |
| React Flow  | 工作流画布 |
| Recharts    | 图表库     |
| Zustand     | 状态管理   |
| Vite        | 构建工具   |

---

## 📁 项目结构

```
capstone-mini-dify/
├── backend/                # Python 后端
│   ├── app/
│   │   ├── api/           # FastAPI 路由
│   │   ├── core/          # 核心业务逻辑
│   │   ├── models/        # 数据模型
│   │   └── utils/         # 工具函数
│   └── tests/             # 测试
├── frontend/               # React 前端
│   └── src/
│       ├── pages/         # 页面组件
│       ├── components/    # 通用组件
│       ├── services/      # API 客户端
│       └── stores/        # 状态管理
├── data/                   # 数据存储
├── docs/                   # 项目文档
├── scripts/                # 运维脚本
└── docker/                 # Docker 配置
```

---

## 📊 课程知识覆盖

| 课程阶段               | Mini-Dify 对应模块   |
| ---------------------- | -------------------- |
| Phase 1: LLM API       | Model Hub            |
| Phase 2: Prompt 工程   | Prompt Studio        |
| Phase 3: LangChain     | 全局基础设施         |
| Phase 4-5: RAG         | Knowledge Base       |
| Phase 6: Agent & Tools | Agent Builder        |
| Phase 7: Multi-Agent   | Workflow Engine      |
| Phase 9: 部署          | API Gateway + Docker |
| Phase 10: 评估         | Monitoring Dashboard |

---

## 📚 文档目录

| 文档                                     | 说明               |
| ---------------------------------------- | ------------------ |
| [产品需求文档](docs/PRD.md)              | 功能需求与验收标准 |
| [技术架构设计](docs/TECHNICAL_DESIGN.md) | 系统架构与技术选型 |
| [数据库设计](docs/DATABASE_DESIGN.md)    | 表结构与 ER 关系图 |
| [API 设计文档](docs/API_DESIGN.md)       | 接口规范           |
| [前端页面设计](docs/UI_DESIGN.md)        | 页面线框图与规范   |
| [开发进度表](docs/PROGRESS_TRACKER.md)   | 开发计划与进度     |

---

## 📄 License

MIT License

---

**开发状态**: 📝 设计规划中  
**最后更新**: 2026-03-06
