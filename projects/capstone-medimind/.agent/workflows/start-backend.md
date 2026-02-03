---
description: 启动 MediMind 后端开发服务器
---

# 启动后端开发服务器

1. 进入项目目录

```bash
cd /Users/perlou/Desktop/personal/llm-course/projects/capstone-medimind
```

2. 激活虚拟环境

```bash
source venv/bin/activate
```

3. 启动 FastAPI 开发服务器
   // turbo

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问：

- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/v1/system/health
