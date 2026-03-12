"""
Mini-Dify - Agent 运行时服务
工具注册 + LangChain Agent 执行 + RAG 检索集成
"""

import json
import asyncio
import math
from datetime import datetime
from typing import AsyncGenerator

from app.config import get_settings
from app.core.model_service import ModelService

settings = get_settings()


# ==================== Built-in Tools ====================


BUILTIN_TOOLS = [
    {
        "name": "calculator",
        "description": "数学计算工具。输入一个数学表达式，返回计算结果。支持加减乘除、幂运算、三角函数等。",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，例如: 2+3*4, sqrt(16), sin(3.14)",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "current_time",
        "description": "获取当前日期和时间。无需输入参数。",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "knowledge_search",
        "description": "从关联知识库中搜索相关信息。输入查询问题，返回最相关的文档片段。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询内容",
                }
            },
            "required": ["query"],
        },
    },
]


class ToolExecutor:
    """工具执行器"""

    @staticmethod
    async def execute(tool_name: str, arguments: dict, context: dict | None = None) -> str:
        """执行工具并返回结果"""
        if tool_name == "calculator":
            return ToolExecutor._calc(arguments.get("expression", ""))
        elif tool_name == "current_time":
            return ToolExecutor._current_time()
        elif tool_name == "knowledge_search":
            return await ToolExecutor._knowledge_search(
                arguments.get("query", ""),
                context or {},
            )
        else:
            return f"未知工具: {tool_name}"

    @staticmethod
    def _calc(expression: str) -> str:
        """安全数学计算"""
        try:
            allowed_names = {
                "abs": abs, "round": round, "min": min, "max": max,
                "sqrt": math.sqrt, "pow": pow, "log": math.log,
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "pi": math.pi, "e": math.e,
            }
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return str(result)
        except Exception as e:
            return f"计算错误: {e}"

    @staticmethod
    def _current_time() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

    @staticmethod
    async def _knowledge_search(query: str, context: dict) -> str:
        """RAG 知识库检索"""
        dataset_ids = context.get("dataset_ids", [])
        if not dataset_ids:
            return "未绑定知识库"

        from app.core.rag_service import retrieve

        all_results = []
        for dataset_id in dataset_ids:
            try:
                results = await retrieve(
                    dataset_id=str(dataset_id),
                    query=query,
                    top_k=3,
                )
                all_results.extend(results)
            except Exception:
                continue

        if not all_results:
            return "未找到相关信息"

        # 按分数排序取前 5
        all_results.sort(key=lambda x: x["score"], reverse=True)
        top = all_results[:5]

        parts = []
        for i, r in enumerate(top, 1):
            parts.append(f"[{i}] (相关度: {r['score']:.2%})\n{r['content']}")
        return "\n\n".join(parts)


# ==================== Agent Runner ====================


class AgentRunner:
    """Agent 运行时: 构建 LangChain Agent 并执行对话"""

    @staticmethod
    async def chat_stream(
        provider_config: dict,
        agent_config: dict,
        messages: list[dict],
        tool_names: list[str],
        dataset_ids: list[str],
    ) -> AsyncGenerator[dict, None]:
        """
        流式 Agent 对话

        Yields SSE events:
          {"event": "thought", "data": "..."}     - Agent 思考过程
          {"event": "tool_call", "data": {...}}    - 工具调用
          {"event": "tool_result", "data": {...}}  - 工具结果
          {"event": "message", "data": "..."}      - 最终回答(增量)
          {"event": "done", "data": {...}}         - 完成
          {"event": "error", "data": "..."}        - 错误
        """
        try:
            system_prompt = agent_config.get("system_prompt", "You are a helpful assistant.")
            model_name = agent_config.get("model_name", "gpt-4o-mini")
            temperature = agent_config.get("temperature", 0.7)
            max_tokens = agent_config.get("max_tokens", 2048)

            # 构建工具描述
            available_tools = []
            for t in BUILTIN_TOOLS:
                if t["name"] in tool_names:
                    available_tools.append(t)

            # 如果有知识库绑定，自动添加 knowledge_search 工具
            if dataset_ids and "knowledge_search" not in tool_names:
                for t in BUILTIN_TOOLS:
                    if t["name"] == "knowledge_search":
                        available_tools.append(t)
                        break

            context = {"dataset_ids": dataset_ids}

            # 构建 system prompt，附带工具信息
            tool_descriptions = ""
            if available_tools:
                tool_list = []
                for t in available_tools:
                    params_desc = json.dumps(t["parameters"], ensure_ascii=False)
                    tool_list.append(f"- {t['name']}: {t['description']}\n  参数: {params_desc}")
                tool_descriptions = "\n\n## 可用工具\n\n" + "\n".join(tool_list)
                tool_descriptions += "\n\n当需要使用工具时，请用以下格式:\n```tool_call\n{\"name\": \"工具名\", \"arguments\": {参数}}\n```\n工具返回结果后继续回答用户问题。"

            full_system = system_prompt + tool_descriptions

            # 构建消息列表
            chat_messages = [{"role": "system", "content": full_system}]
            for msg in messages:
                chat_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

            # 调用 LLM
            yield {"event": "thought", "data": "正在思考..."}

            full_response = ""
            try:
                llm = ModelService.create_llm(
                    provider_type=provider_config.get("provider_type", "openai"),
                    api_key=provider_config.get("api_key", ""),
                    model_name=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    base_url=provider_config.get("base_url"),
                )

                # 使用流式输出
                from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

                lc_messages = []
                for m in chat_messages:
                    if m["role"] == "system":
                        lc_messages.append(SystemMessage(content=m["content"]))
                    elif m["role"] == "user":
                        lc_messages.append(HumanMessage(content=m["content"]))
                    elif m["role"] == "assistant":
                        lc_messages.append(AIMessage(content=m["content"]))

                async for chunk in llm.astream(lc_messages):
                    token = chunk.content if hasattr(chunk, "content") else str(chunk)
                    if token:
                        full_response += token
                        yield {"event": "message", "data": token}

            except Exception as e:
                # 降级到非流式
                try:
                    response = await ModelService.chat(
                        provider_type=provider_config.get("provider_type", "openai"),
                        api_key=provider_config.get("api_key", ""),
                        model_name=model_name,
                        messages=chat_messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        base_url=provider_config.get("base_url"),
                    )
                    full_response = response
                    yield {"event": "message", "data": response}
                except Exception as e2:
                    yield {"event": "error", "data": str(e2)}
                    return

            # 检查是否有工具调用
            tool_call_result = AgentRunner._extract_tool_call(full_response)
            if tool_call_result and available_tools:
                tool_name = tool_call_result["name"]
                tool_args = tool_call_result["arguments"]

                yield {"event": "tool_call", "data": json.dumps(
                    {"name": tool_name, "arguments": tool_args}, ensure_ascii=False
                )}

                # 执行工具
                result = await ToolExecutor.execute(tool_name, tool_args, context)
                yield {"event": "tool_result", "data": json.dumps(
                    {"name": tool_name, "result": result}, ensure_ascii=False
                )}

                # 将工具结果追加，再次调用 LLM
                chat_messages.append({"role": "assistant", "content": full_response})
                chat_messages.append({"role": "user", "content": f"工具 {tool_name} 返回结果:\n{result}\n\n请根据以上结果继续回答。"})

                try:
                    followup = await ModelService.chat(
                        provider_type=provider_config.get("provider_type", "openai"),
                        api_key=provider_config.get("api_key", ""),
                        model_name=model_name,
                        messages=chat_messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        base_url=provider_config.get("base_url"),
                    )
                    yield {"event": "message", "data": "\n\n" + followup}
                    full_response += "\n\n" + followup
                except Exception:
                    pass

            yield {"event": "done", "data": json.dumps(
                {"total_length": len(full_response)}, ensure_ascii=False
            )}

        except Exception as e:
            yield {"event": "error", "data": str(e)}

    @staticmethod
    def _extract_tool_call(text: str) -> dict | None:
        """从 LLM 回复中提取工具调用"""
        import re

        pattern = r"```tool_call\s*\n(.*?)\n```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
        return None
