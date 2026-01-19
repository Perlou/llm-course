---
description: 创建 Agent 应用的标准流程
---

# 创建 Agent 应用工作流

使用此工作流创建 LLM Agent 应用。

## 步骤

1. 在 `projects/` 目录下创建项目文件夹

```bash
mkdir -p projects/{project-name}
cd projects/{project-name}
```

2. 参考 `.agent/skills/create-project/SKILL.md` 了解 Agent 项目结构

3. 创建项目文件结构：
   - `main.py` - 主入口
   - `agent.py` - Agent 定义
   - `tools.py` - 自定义工具
   - `prompts.py` - 系统提示词
   - `app.py` - FastAPI 服务
   - `requirements.txt` - 依赖
   - `.env.example` - 环境变量模板

4. 定义工具 (`tools.py`)
   - 使用 `@tool` 装饰器
   - 编写清晰的工具描述
   - 实现工具逻辑

5. 创建 Agent (`agent.py`)
   - 选择 Agent 类型（ReAct、Plan-and-Execute 等）
   - 配置工具列表
   - 设置系统提示词

6. 实现 API 服务 (`app.py`)
   - 处理流式输出
   - 错误处理

7. 测试运行

// turbo

```bash
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

8. 验证 Agent 行为
   - 测试工具调用
   - 测试推理过程
   - 检查错误处理

9. 编写 README.md 文档
