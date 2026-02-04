# 🤖 大模型应用开发课程 (LLM Application Development)

> **定制对象**：资深全栈工程师向大模型应用开发工程师转型  
> **学习方式**：基于 Python + LangChain/LlamaIndex 的理论与实践结合学习  
> **预计时长**：16-20 周（每周投入 10-15 小时）

---

## 🚀 快速开始

### 1. 环境设置

```bash
cd llm-course

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置 API Keys
cp .env.example .env
# 编辑 .env 填入你的 API Keys
```

### 2. 运行课程

```bash
# 激活虚拟环境后运行
source venv/bin/activate
python3 src/phase-1-llm-fundamentals/01-openai-api-basics.py
```

### 3. 常见问题

<details>
<summary><b>❌ 虚拟环境激活后仍提示 command not found: python</b></summary>

**原因**：虚拟环境损坏（通常由 Python 版本升级导致）

**解决方案**：

```bash
# 1. 退出并删除旧的虚拟环境
deactivate
rm -rf venv

# 2. 重新创建虚拟环境
python3 -m venv venv

# 3. 激活并验证
source venv/bin/activate
which python3  # 应该显示 /path/to/llm-course/venv/bin/python3

# 4. 安装依赖
pip install -r requirements.txt
```

</details>

<details>
<summary><b>❌ ModuleNotFoundError: No module named 'xxx'</b></summary>

**解决方案**：

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt
```

</details>

<details>
<summary><b>❌ Gemini API 限流 (429 Resource exhausted)</b></summary>

**解决方案**：

- 等待 1-2 分钟后重试
- 在代码中添加延迟：`time.sleep(2)`

</details>

---

## 📂 项目结构

```
llm-course/
├── README.md                    # 快速开始指南
├── ROADMAP.md                   # 学习路线图
├── LEARNING_PLAN.md             # 详细学习计划
├── CONCEPTS.md                  # 核心概念汇总
├── requirements.txt             # Python 依赖
├── .env.example                 # 环境变量模板
├── src/                         # 课程代码（按阶段组织）
│   ├── phase-1-llm-fundamentals/
│   ├── phase-2-prompt-engineering/
│   ├── phase-3-langchain-basics/
│   └── ...
├── notebooks/                   # Jupyter Notebooks
├── docs/                        # 学习笔记
└── projects/                    # 实战项目
```

**重要文档**：

- 📖 [ROADMAP.md](./ROADMAP.md) - 可视化学习路线
- 📝 [CONCEPTS.md](./CONCEPTS.md) - 核心概念速查
- 🗺️ [LEARNING_PLAN.md](./LEARNING_PLAN.md) - 完整计划

---

## 🛠️ 技术栈

- **Python 3.10+** - 核心开发语言
- **LangChain / LlamaIndex** - LLM 应用框架
- **Google Gemini / OpenAI** - LLM API
- **向量数据库** - Chroma、Pinecone、Weaviate
- **部署** - FastAPI、Docker、Kubernetes

---

## 📖 学习资源

- **ROADMAP.md** - 查看完整学习路径和阶段划分
- **LEARNING_PLAN.md** - 每个阶段的详细学习内容
- **CONCEPTS.md** - 核心概念速查手册
- 每个阶段目录下都有独立的 README.md 和示例代码

---

**Good luck! 🚀**

有任何问题随时记录在 `docs/` 中，养成持续学习和总结的习惯。
