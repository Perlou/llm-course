---
name: run-project
description: 运行和测试 Mini-Dify 平台项目（含 Docker 服务）
---

# 运行项目技能

此技能用于运行和测试 Mini-Dify 可视化 LLM 应用开发平台。

## 项目路径

```
/Users/perlou/Desktop/personal/llm-course/projects/capstone-mini-dify
```

## 基础服务启动

### 1. 启动 PostgreSQL + Milvus

```bash
cd /Users/perlou/Desktop/personal/llm-course/projects/capstone-mini-dify
docker compose -f docker/docker-compose.yaml up -d postgres milvus
```

### 2. 验证服务状态

```bash
# PostgreSQL
docker compose -f docker/docker-compose.yaml exec postgres pg_isready

# Milvus
curl http://localhost:9091/healthz
```

## 后端启动

### 1. 激活虚拟环境

```bash
cd /Users/perlou/Desktop/personal/llm-course/projects/capstone-mini-dify/backend
source venv/bin/activate
# 如果没有虚拟环境：
# python3.12 -m venv venv && source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 配置：
# DATABASE_URL=postgresql+asyncpg://mini_dify:mini_dify_secret@localhost:5432/mini_dify
# MILVUS_HOST=localhost
# MILVUS_PORT=19530
# OPENAI_API_KEY=sk-xxx (可选)
```

### 4. 执行数据库迁移

```bash
alembic upgrade head
```

### 5. 启动后端

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 前端启动

```bash
cd /Users/perlou/Desktop/personal/llm-course/projects/capstone-mini-dify/frontend
pnpm install
pnpm dev
```

## 同时启动

**终端 1 - 基础服务**:

```bash
cd /Users/perlou/Desktop/personal/llm-course/projects/capstone-mini-dify
docker compose -f docker/docker-compose.yaml up -d postgres milvus
```

**终端 2 - 后端**:

```bash
cd /Users/perlou/Desktop/personal/llm-course/projects/capstone-mini-dify/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**终端 3 - 前端**:

```bash
cd /Users/perlou/Desktop/personal/llm-course/projects/capstone-mini-dify/frontend
pnpm dev
```

## 访问服务

| 服务       | 地址                         |
| ---------- | ---------------------------- |
| 前端界面   | http://localhost:5173        |
| API 文档   | http://localhost:8000/docs   |
| 健康检查   | http://localhost:8000/health |
| PostgreSQL | localhost:5432               |
| Milvus     | localhost:19530              |

## 运行测试

```bash
cd /Users/perlou/Desktop/personal/llm-course/projects/capstone-mini-dify/backend

# 运行所有测试
pytest tests/ -v

# 特定模块
pytest tests/test_model_hub.py -v
pytest tests/test_rag.py -v
pytest tests/test_workflow.py -v

# 覆盖率
pytest tests/ -v --cov=app --cov-report=html
```

## Docker 一键部署

```bash
cd /Users/perlou/Desktop/personal/llm-course/projects/capstone-mini-dify
docker compose -f docker/docker-compose.yaml up -d
# 访问 http://localhost:5173
```

## 常见问题

### 端口被占用

```bash
lsof -i :8000  # 后端
lsof -i :5173  # 前端
lsof -i :5432  # PostgreSQL
kill -9 <PID>
```

### 数据库连接失败

```bash
# 检查 PostgreSQL 是否运行
docker compose -f docker/docker-compose.yaml ps postgres
# 重启
docker compose -f docker/docker-compose.yaml restart postgres
```

### 重置数据库

```bash
alembic downgrade base  # 回退所有迁移
alembic upgrade head    # 重新执行
```

### 重置 Milvus

```bash
docker compose -f docker/docker-compose.yaml down milvus
docker volume rm capstone-mini-dify_milvus_data
docker compose -f docker/docker-compose.yaml up -d milvus
```
