---
name: run-project
description: 运行和测试 MediMind 健康助手项目
---

# 运行项目技能

此技能用于运行和测试 MediMind 智能健康助手项目。

## 项目路径

```
/Users/perlou/Desktop/personal/llm-course/projects/capstone-medimind
```

## 快速启动

### 1. 进入项目目录

```bash
cd /Users/perlou/Desktop/personal/llm-course/projects/capstone-medimind
```

### 2. 激活虚拟环境

```bash
source venv/bin/activate
# 如果没有虚拟环境，先创建：
# python -m venv venv && source venv/bin/activate
```

### 3. 安装后端依赖

```bash
pip install -r requirements.txt
```

### 4. 安装前端依赖

```bash
cd frontend && pnpm install && cd ..
```

### 5. 初始化数据库

```bash
python scripts/init_db.py
```

## 启动服务

### 启动后端 (FastAPI)

```bash
# 开发模式（热重载）
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 启动前端 (Turborepo)

```bash
cd frontend

# 开发模式（所有应用）
pnpm dev

# 仅启动 web 应用
pnpm --filter @medimind/web dev

# 构建所有应用
pnpm build
```

### 同时启动

**终端 1 - 后端**:

```bash
uvicorn src.api.main:app --reload --port 8000
```

**终端 2 - 前端**:

```bash
cd frontend && pnpm dev
```

## 访问服务

| 服务     | 地址                                       |
| -------- | ------------------------------------------ |
| 前端界面 | http://localhost:5173                      |
| API 文档 | http://localhost:8000/docs                 |
| 健康检查 | http://localhost:8000/api/v1/system/health |

## 运行测试

### 后端测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_guardrails.py -v
pytest tests/test_rag.py -v
pytest tests/test_triage.py -v

# 显示覆盖率
pytest tests/ -v --cov=src --cov-report=html
```

### 前端测试

```bash
cd frontend
pnpm test
pnpm lint
```

## 使用 curl 测试 API

```bash
# 健康检查
curl http://localhost:8000/api/v1/system/health

# 健康问答
curl -X POST http://localhost:8000/api/v1/health/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "高血压应该注意什么？"}'

# 药品搜索
curl "http://localhost:8000/api/v1/drug/search?q=阿司匹林"
```

## 环境变量

```bash
# .env 文件
GEMINI_API_KEY=your_api_key
DATABASE_URL=postgresql://user:pass@localhost:5432/medimind
USE_OLLAMA=false
OLLAMA_HOST=http://localhost:11434
```

## 常见问题

### 端口被占用

```bash
lsof -i :8000
kill -9 <PID>
```

### 模块导入错误

```bash
export PYTHONPATH="${PYTHONPATH}:/Users/perlou/Desktop/personal/llm-course/projects/capstone-medimind"
```

### 重置数据库

```bash
rm -rf data/db/
python scripts/init_db.py
```
