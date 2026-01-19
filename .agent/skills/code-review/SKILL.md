---
name: code-review
description: 审查 LLM 应用代码，提供最佳实践建议
---

# LLM 应用代码审查技能

此技能用于审查 LLM 应用相关代码，确保代码质量和最佳实践。

## 审查维度

### 1. API 调用最佳实践

```python
# ✅ 正确：使用环境变量存储 API Key
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ❌ 错误：硬编码 API Key（安全风险！）
api_key = "sk-xxxx..."
```

```python
# ✅ 正确：使用错误处理和重试
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_llm(prompt):
    return client.chat.completions.create(...)

# ❌ 错误：无错误处理
def call_llm(prompt):
    return client.chat.completions.create(...)  # 可能因网络问题失败
```

### 2. LangChain 最佳实践

```python
# ✅ 正确：使用 LCEL 链式调用
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

chain = prompt | llm | output_parser
result = chain.invoke({"question": "..."})

# ❌ 过时：使用旧版 LLMChain
from langchain.chains import LLMChain  # 已弃用
chain = LLMChain(llm=llm, prompt=prompt)
```

```python
# ✅ 正确：使用 RunnableParallel 并行处理
from langchain_core.runnables import RunnableParallel

parallel_chain = RunnableParallel(
    summary=summary_chain,
    keywords=keywords_chain
)

# ❌ 低效：串行调用
summary = summary_chain.invoke(...)
keywords = keywords_chain.invoke(...)
```

### 3. RAG 最佳实践

```python
# ✅ 正确：合理的文档分割
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,  # 有重叠防止上下文断裂
    separators=["\n\n", "\n", "。", "！", "？", " ", ""]
)

# ❌ 问题：分割过小或无重叠
splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,  # 太小，上下文不足
    chunk_overlap=0   # 无重叠，可能断裂
)
```

```python
# ✅ 正确：使用适合场景的检索策略
retriever = vectorstore.as_retriever(
    search_type="mmr",  # 增加多样性
    search_kwargs={"k": 5, "fetch_k": 20}
)

# ⚠️ 一般：默认相似度检索
retriever = vectorstore.as_retriever()  # 可能返回重复内容
```

### 4. Agent 最佳实践

```python
# ✅ 正确：详细的工具描述
@tool
def search_database(query: str) -> str:
    """搜索产品数据库。

    当用户询问产品信息、价格或库存时使用此工具。

    Args:
        query: 搜索关键词，如产品名称或类别

    Returns:
        包含产品信息的 JSON 字符串
    """
    return search(query)

# ❌ 问题：描述不清晰
@tool
def search(q: str) -> str:
    """搜索"""  # LLM 不知道什么时候使用
    return search(q)
```

### 5. 性能与成本优化

```python
# ✅ 正确：使用缓存减少 API 调用
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache

set_llm_cache(InMemoryCache())

# ✅ 正确：使用流式输出提升用户体验
for chunk in chain.stream({"question": "..."}):
    print(chunk, end="", flush=True)

# ✅ 正确：批量处理
results = chain.batch([{"q": q} for q in questions])
```

## 审查模板

```markdown
## LLM 应用代码审查报告

### 📁 文件: {文件名}

### ✅ 优点

1. ...
2. ...

### ⚠️ 建议改进

1. **问题描述**
   - 位置: 第 X 行
   - 当前代码: `...`
   - 建议修改: `...`
   - 原因: ...

### 🔒 安全检查

- [ ] API Key 是否使用环境变量
- [ ] 是否有提示注入防护
- [ ] 用户输入是否有验证

### 💰 成本检查

- [ ] 是否使用了缓存
- [ ] 是否有不必要的 API 调用
- [ ] Token 使用是否优化

### 📊 评分

- 安全性: ⭐⭐⭐⭐⭐
- 可维护性: ⭐⭐⭐⭐
- 性能: ⭐⭐⭐
- 总体: 4/5
```

## 常见问题清单

### API 调用

- [ ] API Key 是否安全存储
- [ ] 是否有错误处理和重试机制
- [ ] 是否使用了请求超时

### 提示词

- [ ] 系统提示是否清晰
- [ ] 是否有输出格式规范
- [ ] 是否有防护措施

### RAG

- [ ] 文档分割策略是否合理
- [ ] Embedding 模型是否合适
- [ ] 检索结果数量是否适当

### Agent

- [ ] 工具描述是否清晰
- [ ] 是否有最大迭代次数限制
- [ ] 是否处理了工具调用错误
