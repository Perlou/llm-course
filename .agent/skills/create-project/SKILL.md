---
name: create-project
description: 创建 LLM 应用实战项目，包含完整的项目结构和代码
---

# 创建 LLM 实战项目技能

此技能用于在 `projects/` 目录下创建完整的 LLM 应用实战项目。

## 项目结构

```
projects/{project-name}/
├── README.md           # 项目说明文档
├── main.py             # 主入口文件
├── app.py              # 应用服务（FastAPI）
├── chains.py           # LangChain 链定义
├── prompts.py          # 提示词模板
├── tools.py            # 自定义工具（Agent 项目）
├── vectorstore.py      # 向量存储逻辑（RAG 项目）
├── config.py           # 配置参数
├── requirements.txt    # 项目依赖
├── .env.example        # 环境变量模板
└── data/               # 数据目录
    └── .gitkeep
```

## README.md 模板

````markdown
# {项目名称}

## 项目简介

简要描述项目目标和背景...

## 技术栈

- Python 3.10+
- LangChain 0.3+
- OpenAI GPT-4 / Claude
- 其他依赖...

## 快速开始

### 1. 环境准备

```bash
cd projects/{project-name}
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env 填入 API Key
```

### 3. 运行应用

```bash
python main.py
# 或启动 API 服务
uvicorn app:app --reload
```

## 系统架构

```
用户输入 → 预处理 → LLM/RAG/Agent → 后处理 → 输出
```

## 核心功能

1. 功能一
2. 功能二

## API 文档

### POST /chat

请求：

```json
{ "message": "用户消息" }
```

响应：

```json
{ "response": "AI 回复" }
```

## 学习要点

1. 要点一
2. 要点二

## 参考资料

- [相关文档](url)
````

## 创建步骤

1. **确定项目类型**：聊天机器人 / RAG 系统 / Agent 应用
2. **创建目录结构**：按上述结构创建目录和文件
3. **实现核心模块**：
   - `prompts.py`：定义提示词模板
   - `chains.py`：构建 LangChain 链
   - `app.py`：FastAPI 服务
4. **编写 README**：详细的项目文档
5. **测试运行**：确保代码可以正常运行

## 项目类型模板

### 1. 聊天机器人项目

```python
# chains.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def create_chat_chain():
    llm = ChatOpenAI(model="gpt-4")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个有帮助的助手。"),
        ("human", "{input}")
    ])
    return prompt | llm | StrOutputParser()
```

### 2. RAG 项目

```python
# vectorstore.py
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

def create_vectorstore(docs):
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    return vectorstore

def create_retriever(vectorstore, k=5):
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k}
    )
```

### 3. Agent 项目

```python
# tools.py
from langchain.tools import tool

@tool
def search_web(query: str) -> str:
    """搜索网络获取最新信息。

    Args:
        query: 搜索关键词
    """
    # 实现搜索逻辑
    return "搜索结果..."

@tool
def calculate(expression: str) -> str:
    """计算数学表达式。

    Args:
        expression: 数学表达式，如 "2 + 2"
    """
    return str(eval(expression))
```

## FastAPI 服务模板

```python
# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from chains import create_chat_chain

app = FastAPI(title="LLM Application")
chain = create_chat_chain()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response = chain.invoke({"input": request.message})
    return ChatResponse(response=response)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 注意事项

- 使用异步处理提升并发性能
- 添加适当的日志和错误处理
- 提供 API 文档（FastAPI 自动生成）
- 使用 Pydantic 进行数据验证
- 考虑 API 速率限制
