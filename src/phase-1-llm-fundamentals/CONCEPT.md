# Phase 1: LLM 基础与 API 调用 - 核心概念

> 本文档汇总第一阶段的核心概念，随学习进度持续更新。

---

## 目录

1. [LLM 概述](#1-llm-概述)
2. [API 调用基础](#2-api-调用基础)
3. [核心参数](#3-核心参数)
4. [流式响应](#4-流式响应)
5. [本地模型部署](#5-本地模型部署)
6. [最佳实践](#6-最佳实践)

---

## 1. LLM 概述

### 1.1 什么是 LLM

**大型语言模型 (Large Language Model)** 是在海量文本数据上训练的神经网络模型，能够理解和生成人类语言。

```
训练数据 (TB级文本) → Transformer 架构 → 预训练模型 → 指令微调 → 对齐 → 部署
```

### 1.2 主流 LLM 提供商

| 提供商    | 模型              | 特点                     | API 端点                          |
| --------- | ----------------- | ------------------------ | --------------------------------- |
| OpenAI    | GPT-4, GPT-4o     | 最强综合能力，多模态     | api.openai.com                    |
| Anthropic | Claude 3.5 Sonnet | 长上下文 (200K)，强推理  | api.anthropic.com                 |
| Google    | Gemini 1.5        | 多模态原生，100万上下文  | generativelanguage.googleapis.com |
| Meta      | Llama 3.1         | 开源领先，可私有部署     | 自托管                            |
| 阿里      | Qwen 2.5          | 中文能力强，代码能力优秀 | dashscope.aliyuncs.com            |

### 1.3 模型选择指南

```
简单任务 → GPT-3.5 / Claude Haiku (低成本)
复杂推理 → GPT-4o / Claude Sonnet (高质量)
长文档   → Claude / Gemini (长上下文)
隐私敏感 → Llama / Qwen (本地部署)
中文场景 → Qwen / Claude (中文优化)
```

---

## 2. API 调用基础

### 2.1 Chat Completions API

现代 LLM API 统一使用 **Chat Completions** 格式：

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "你是一个有帮助的助手。"},
        {"role": "user", "content": "你好！"},
        {"role": "assistant", "content": "你好！有什么可以帮你的？"},
        {"role": "user", "content": "请介绍一下自己。"}
    ]
)

print(response.choices[0].message.content)
```

### 2.2 消息角色

| 角色        | 作用                 | 示例                    |
| ----------- | -------------------- | ----------------------- |
| `system`    | 设定 AI 的角色和行为 | "你是一个专业的翻译官"  |
| `user`      | 用户输入             | "请翻译这段话"          |
| `assistant` | AI 的回复（历史）    | "好的，这是翻译结果..." |

### 2.3 响应结构

```python
# 完整响应结构
{
    "id": "chatcmpl-xxx",
    "object": "chat.completion",
    "created": 1234567890,
    "model": "gpt-4",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "AI 的回复内容"
            },
            "finish_reason": "stop"  # stop | length | tool_calls
        }
    ],
    "usage": {
        "prompt_tokens": 50,
        "completion_tokens": 100,
        "total_tokens": 150
    }
}
```

---

## 3. 核心参数

### 3.1 Temperature

控制输出的**随机性/创造性**：

```
temperature = 0.0  →  确定性输出，每次相同
temperature = 0.7  →  平衡创造性和一致性（推荐）
temperature = 1.0  →  高创造性，更多变化
temperature = 2.0  →  非常随机，可能不连贯
```

**使用场景**：

- 代码生成：0.0 - 0.2（需要精确）
- 对话聊天：0.5 - 0.7（自然但可控）
- 创意写作：0.8 - 1.2（需要多样性）

### 3.2 Top_p (核采样)

另一种控制随机性的方式，与 temperature 二选一：

```python
# top_p = 0.1: 只从概率最高的 10% tokens 中采样
# top_p = 0.9: 从概率累计达 90% 的 tokens 中采样
# top_p = 1.0: 考虑所有 tokens
```

### 3.3 Max_tokens

限制输出的**最大 token 数**：

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    max_tokens=1000  # 限制输出不超过 1000 tokens
)
```

**注意**：设置过小可能导致回答被截断。

### 3.4 其他参数

| 参数                | 作用               | 范围       |
| ------------------- | ------------------ | ---------- |
| `frequency_penalty` | 降低重复词出现概率 | -2.0 ~ 2.0 |
| `presence_penalty`  | 鼓励讨论新话题     | -2.0 ~ 2.0 |
| `stop`              | 遇到指定字符串停止 | 字符串列表 |
| `n`                 | 生成多少个回复     | 整数       |

---

## 4. 流式响应

### 4.1 为什么使用流式

- **更快的首字延迟**：用户立即看到输出开始
- **更好的用户体验**：逐字输出更自然
- **节省等待时间**：无需等待完整响应

### 4.2 流式输出实现

```python
# 非流式：等待完整响应
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "讲个故事"}]
)
print(response.choices[0].message.content)

# 流式：逐块输出
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "讲个故事"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### 4.3 流式块结构

```python
# 每个 chunk 的结构
{
    "id": "chatcmpl-xxx",
    "choices": [
        {
            "index": 0,
            "delta": {
                "content": "一"  # 增量内容，可能只有一个字
            },
            "finish_reason": None  # 最后一个是 "stop"
        }
    ]
}
```

---

## 5. 本地模型部署

### 5.1 Ollama

最简单的本地 LLM 部署方案：

```bash
# 安装 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载并运行模型
ollama run llama3.1

# 查看可用模型
ollama list
```

### 5.2 使用 OpenAI 兼容接口

```python
from openai import OpenAI

# Ollama 提供 OpenAI 兼容接口
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # 任意值
)

response = client.chat.completions.create(
    model="llama3.1",
    messages=[{"role": "user", "content": "你好"}]
)
```

### 5.3 常用本地模型

| 模型          | 参数量 | 显存需求 | 特点           |
| ------------- | ------ | -------- | -------------- |
| Llama 3.1 8B  | 8B     | ~8GB     | 平衡性能和资源 |
| Qwen 2.5 7B   | 7B     | ~8GB     | 中文能力强     |
| Mistral 7B    | 7B     | ~8GB     | 速度快         |
| Llama 3.1 70B | 70B    | ~48GB    | 接近闭源模型   |

---

## 6. 最佳实践

### 6.1 API Key 安全

```python
# ✅ 正确：使用环境变量
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ❌ 错误：硬编码（安全风险！）
api_key = "sk-xxxx..."
```

### 6.2 错误处理

```python
from openai import OpenAI, APIError, RateLimitError, APIConnectionError

client = OpenAI()

try:
    response = client.chat.completions.create(...)
except RateLimitError:
    print("API 速率限制，请稍后重试")
except APIConnectionError:
    print("网络连接失败")
except APIError as e:
    print(f"API 错误: {e}")
```

### 6.3 重试机制

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def call_llm(prompt):
    return client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
```

### 6.4 成本控制

```python
# 计算 token 成本
def estimate_cost(prompt_tokens, completion_tokens, model="gpt-4"):
    prices = {
        "gpt-4": {"input": 0.03, "output": 0.06},      # per 1K tokens
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }
    price = prices.get(model, prices["gpt-4"])
    return (prompt_tokens * price["input"] + completion_tokens * price["output"]) / 1000
```

---

## 📝 本阶段学习检查

- [ ] 能够调用 OpenAI/Claude API
- [ ] 理解 temperature、top_p、max_tokens 参数的作用
- [ ] 掌握流式响应的处理方法
- [ ] 能够使用 Ollama 运行本地模型
- [ ] 了解 API Key 安全和错误处理最佳实践

---

> 📝 **注意**: 本文档将随着学习进度持续更新，完成每个课程后补充相应的概念内容。
