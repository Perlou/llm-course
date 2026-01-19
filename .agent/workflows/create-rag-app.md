---
description: 创建 RAG 应用的标准流程
---

# 创建 RAG 应用工作流

使用此工作流创建 RAG（检索增强生成）应用。

## 步骤

1. 在 `projects/` 目录下创建项目文件夹

```bash
mkdir -p projects/{project-name}
cd projects/{project-name}
```

2. 查看 `.agent/skills/create-rag-app/SKILL.md` 了解 RAG 架构和代码模板

3. 创建项目文件结构：
   - `main.py` - 主入口
   - `ingest.py` - 文档导入
   - `chains.py` - RAG 链定义
   - `app.py` - FastAPI 服务
   - `config.py` - 配置
   - `requirements.txt` - 依赖
   - `.env.example` - 环境变量模板

4. 实现文档导入脚本 (`ingest.py`)
   - 文档加载
   - 文本分割
   - 向量存储

5. 实现 RAG 链 (`chains.py`)
   - 检索器配置
   - 提示词模板
   - 链式调用

6. 实现 API 服务 (`app.py`)
   - FastAPI 路由
   - 请求响应模型

7. 测试运行

// turbo

```bash
source venv/bin/activate
pip install -r requirements.txt
python ingest.py  # 导入文档
python main.py    # 测试问答
```

8. 启动 API 服务

```bash
uvicorn app:app --reload
```

9. 编写 README.md 文档
