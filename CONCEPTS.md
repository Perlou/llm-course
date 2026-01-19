# 大模型应用开发核心概念汇总

> 本文档汇总大模型应用开发的核心概念，随学习进度持续更新。

---

## 目录

1. [LLM 基础](#1-llm-基础)
2. [提示工程](#2-提示工程)
3. [LangChain 框架](#3-langchain-框架)
4. [RAG 系统](#4-rag-系统)
5. [Agent 系统](#5-agent-系统)
6. [LLM 微调](#6-llm-微调)
7. [部署与优化](#7-部署与优化)
8. [评估方法](#8-评估方法)
9. [多模态](#9-多模态)

---

## 1. LLM 基础

### 1.1 主流 LLM 提供商

| 提供商    | 模型         | 特点                     |
| --------- | ------------ | ------------------------ |
| OpenAI    | GPT-4/GPT-4o | 最强通用能力，多模态支持 |
| Anthropic | Claude 3.5   | 长上下文，强推理能力     |
| Google    | Gemini       | 多模态原生，长上下文     |
| Meta      | Llama 3      | 开源领先，可本地部署     |
| 阿里      | Qwen         | 中文能力强，代码能力优秀 |

### 1.2 核心 API 参数

```python
# OpenAI Chat Completions API 关键参数
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    temperature=0.7,    # 控制随机性 [0-2]
    top_p=0.95,         # 核采样
    max_tokens=1000,    # 最大生成长度
    frequency_penalty=0,  # 频率惩罚
    presence_penalty=0,   # 存在惩罚
)
```

### 1.3 Token 与定价

- **Token**：LLM 处理文本的基本单位
- 中文约 1-2 字符 = 1 token
- 英文约 4 字符 = 1 token
- 定价通常按 1K 或 1M tokens 计算

---

## 2. 提示工程

### 2.1 提示词结构

```
[System Prompt]     # 定义角色和行为
│
├── [Context]       # 背景信息
├── [Instruction]   # 具体指令
├── [Examples]      # 示例（Few-shot）
└── [Output Format] # 输出格式要求
```

### 2.2 核心技术

| 技术             | 描述               | 适用场景   |
| ---------------- | ------------------ | ---------- |
| Zero-shot        | 无示例直接提问     | 简单任务   |
| Few-shot         | 提供少量示例       | 格式化输出 |
| Chain-of-Thought | 引导逐步推理       | 复杂推理   |
| Self-Consistency | 多次采样取一致结果 | 提高准确性 |
| ReAct            | 推理+行动交替进行  | Agent 任务 |

### 2.3 思维链示例

```
Q: 一个农场有17只羊，死了9只，又买了5只，现在有几只？

A: 让我一步步思考：
1. 初始羊数：17只
2. 死亡后：17 - 9 = 8只
3. 购买后：8 + 5 = 13只
所以现在有 13 只羊。
```

---

## 3. LangChain 框架

### 3.1 核心组件

```
LangChain
├── Models          # LLM 模型封装
├── Prompts         # 提示词模板
├── Chains          # 链式调用
├── Memory          # 记忆管理
├── Agents          # 自主代理
├── Tools           # 工具集
└── Retrievers      # 检索器
```

### 3.2 LCEL (LangChain Expression Language)

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 链式组合
chain = prompt | llm | output_parser

# 运行
result = chain.invoke({"question": "..."})
```

### 3.3 记忆类型

| 类型    | 描述             | 适用场景 |
| ------- | ---------------- | -------- |
| Buffer  | 存储完整对话历史 | 短对话   |
| Window  | 保留最近 K 轮    | 长对话   |
| Summary | 对话摘要         | 超长对话 |
| Entity  | 实体信息提取     | 角色扮演 |

---

## 4. RAG 系统

### 4.1 RAG 流程

```
文档 → 分割 → 嵌入 → 向量存储
                          ↓
查询 → 嵌入 → 检索 → 重排序 → 上下文 → LLM → 回答
```

### 4.2 核心组件

| 组件      | 作用           | 常用工具            |
| --------- | -------------- | ------------------- |
| Loader    | 加载文档       | PyPDF, Unstructured |
| Splitter  | 文档分割       | RecursiveCharacter  |
| Embedding | 文本向量化     | OpenAI, BGE         |
| VectorDB  | 向量存储与检索 | Chroma, Pinecone    |
| Retriever | 检索策略       | Similarity, MMR     |
| Reranker  | 重排序         | Cohere, BGE         |

### 4.3 分割策略

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # 块大小
    chunk_overlap=200,    # 重叠大小
    separators=["\n\n", "\n", " ", ""]  # 分隔符优先级
)
```

### 4.4 检索优化

- **Hybrid Search**: 结合关键词检索和语义检索
- **HyDE**: 先生成假设答案再检索
- **Parent Document**: 检索小块，返回大块
- **Multi-Query**: 查询改写后多次检索

---

## 5. Agent 系统

### 5.1 ReAct 模式

```
Thought: 我需要先搜索相关信息...
Action: search("关键词")
Observation: 搜索结果...
Thought: 根据结果，我需要...
Action: calculate(...)
Observation: 计算结果...
Thought: 现在我可以回答了
Answer: 最终答案
```

### 5.2 工具定义

```python
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """搜索网络信息。当需要获取最新信息时使用。

    Args:
        query: 搜索关键词
    """
    return search_engine.search(query)
```

### 5.3 多 Agent 架构

| 模式          | 描述         | 适用场景   |
| ------------- | ------------ | ---------- |
| Supervisor    | 主管分配任务 | 任务分解   |
| Hierarchical  | 层级结构     | 复杂工作流 |
| Debate        | 辩论达成共识 | 决策场景   |
| Collaborative | 平等协作     | 创意任务   |

---

## 6. LLM 微调

### 6.1 微调方法对比

| 方法             | 参数量 | 显存占用 | 适用场景   |
| ---------------- | ------ | -------- | ---------- |
| Full Fine-tuning | 100%   | 极高     | 资源充足   |
| LoRA             | ~0.1%  | 低       | 单 GPU     |
| QLoRA            | ~0.1%  | 极低     | 消费级 GPU |
| Prompt Tuning    | <0.1%  | 最低     | 特定任务   |

### 6.2 LoRA 原理

```
原始权重: W ∈ R^(d×k)
LoRA 分解: W' = W + BA
  - B ∈ R^(d×r)
  - A ∈ R^(r×k)
  - r << min(d, k) (低秩)

可训练参数: r × (d + k) << d × k
```

### 6.3 训练数据格式

```json
{
  "instruction": "将以下句子翻译成英文",
  "input": "今天天气很好",
  "output": "The weather is nice today."
}
```

---

## 7. 部署与优化

### 7.1 推理优化技术

| 技术         | 描述                  | 效果     |
| ------------ | --------------------- | -------- |
| Quantization | 降低精度（FP16→INT8） | 显存减半 |
| KV Cache     | 缓存注意力键值        | 加速生成 |
| Batching     | 批量处理请求          | 提高吞吐 |
| Speculative  | 预测性解码            | 降低延迟 |

### 7.2 部署框架

| 框架   | 特点                   | 适用场景 |
| ------ | ---------------------- | -------- |
| vLLM   | PagedAttention, 高吞吐 | 生产环境 |
| TGI    | HuggingFace 官方       | 快速部署 |
| Ollama | 本地易用               | 开发测试 |
| GGML   | CPU 推理               | 边缘设备 |

---

## 8. 评估方法

### 8.1 RAG 评估指标

| 指标              | 描述                 | 计算方式     |
| ----------------- | -------------------- | ------------ |
| Faithfulness      | 答案对上下文的忠实度 | LLM 判断     |
| Relevance         | 答案与问题的相关性   | LLM 判断     |
| Context Precision | 上下文精确度         | 检索结果排序 |
| Context Recall    | 上下文召回率         | 覆盖程度     |

### 8.2 LLM 评估方法

- **自动评估**: BLEU, ROUGE, BERTScore
- **LLM-as-Judge**: 用 LLM 评估 LLM
- **人工评估**: 人工打分与偏好对比

---

## 9. 多模态

### 9.1 多模态模型

| 模型     | 能力                    |
| -------- | ----------------------- |
| GPT-4V   | 图像理解、OCR、图表分析 |
| Claude 3 | 视觉推理、文档理解      |
| Gemini   | 原生多模态、视频理解    |
| LLaVA    | 开源视觉语言模型        |

### 9.2 应用场景

- 文档 OCR 与理解
- 图表/图像分析
- 视频内容理解
- 语音对话系统

---

> 📝 **注意**: 本文档将随着学习进度持续更新，每完成一个阶段都会补充相应的概念内容。
