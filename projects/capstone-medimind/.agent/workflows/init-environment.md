---
description: 初始化 MediMind 项目开发环境
---

# 初始化开发环境

## 1. 后端环境

进入项目目录：

```bash
cd /Users/perlou/Desktop/personal/llm-course/projects/capstone-medimind
```

创建虚拟环境：

```bash
python -m venv venv
```

激活虚拟环境：

```bash
source venv/bin/activate
```

安装依赖：
// turbo

```bash
pip install -r requirements.txt
```

创建 .env 文件（如不存在）：

```bash
cp .env.example .env
```

初始化数据库：

```bash
python scripts/init_db.py
```

## 2. 前端环境

进入前端目录：

```bash
cd frontend
```

安装依赖：
// turbo

```bash
pnpm install
```

## 3. 验证环境

后端健康检查：

```bash
curl http://localhost:8000/api/v1/system/health
```

## 环境变量说明

在 `.env` 中配置：

```
GEMINI_API_KEY=your_api_key
DATABASE_URL=postgresql://user:pass@localhost:5432/medimind
USE_OLLAMA=false
OLLAMA_HOST=http://localhost:11434
```
