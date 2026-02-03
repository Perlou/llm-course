---
description: 运行 MediMind 后端测试
---

# 运行后端测试

1. 进入项目目录

```bash
cd /Users/perlou/Desktop/personal/llm-course/projects/capstone-medimind
```

2. 激活虚拟环境

```bash
source venv/bin/activate
```

3. 运行所有测试
   // turbo

```bash
pytest tests/ -v
```

## 其他测试命令

运行特定模块测试：

```bash
pytest tests/test_guardrails.py -v
pytest tests/test_rag.py -v
pytest tests/test_triage.py -v
pytest tests/test_report.py -v
```

显示测试覆盖率：

```bash
pytest tests/ -v --cov=src --cov-report=html
```

运行单个测试：

```bash
pytest tests/test_guardrails.py::TestGuardrails::test_block_dangerous_input -v
```
