"""
Mini-Dify - 工作流执行引擎
基于 LangGraph 动态构建 StateGraph，支持 5 种节点类型
"""

import json
import asyncio
import math
import re
from datetime import datetime
from typing import Any, AsyncGenerator
from dataclasses import dataclass, field

from app.core.model_service import ModelService


# ==================== Workflow State ====================


@dataclass
class NodeResult:
    """单个节点的执行结果"""
    node_id: str
    node_type: str
    status: str = "pending"       # pending / running / completed / failed
    output: Any = None
    error: str | None = None
    duration_ms: int = 0


@dataclass
class WorkflowState:
    """工作流运行时状态"""
    inputs: dict = field(default_factory=dict)
    node_results: dict[str, NodeResult] = field(default_factory=dict)
    variables: dict[str, Any] = field(default_factory=dict)
    final_output: Any = None


# ==================== Node Executors ====================


class NodeExecutors:
    """5 种节点执行器"""

    @staticmethod
    async def execute_start(config: dict, state: WorkflowState) -> Any:
        """开始节点：透传输入变量"""
        # 将 inputs 写入 variables 供下游引用
        for key, value in state.inputs.items():
            state.variables[key] = value
        return state.inputs

    @staticmethod
    async def execute_llm(config: dict, state: WorkflowState) -> Any:
        """LLM 节点：调用大模型"""
        provider_type = config.get("provider_type", "openai")
        api_key = config.get("api_key", "")
        base_url = config.get("base_url")
        model_name = config.get("model", "gpt-4o-mini")
        temperature = config.get("temperature", 0.7)
        max_tokens = config.get("max_tokens", 2048)
        prompt_template = config.get("prompt", "")

        # 渲染 prompt 模板（支持 {{variable}} 引用上游输出）
        prompt = NodeExecutors._render_template(prompt_template, state.variables)

        system_prompt = config.get("system_prompt", "")
        if system_prompt:
            system_prompt = NodeExecutors._render_template(system_prompt, state.variables)

        from app.core.model_service import ChatMessage

        messages = []
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))
        messages.append(ChatMessage(role="user", content=prompt))

        result = await ModelService.chat(
            provider_type=provider_type,
            messages=messages,
            api_key=api_key,
            base_url=base_url,
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return result.content

    @staticmethod
    async def execute_knowledge(config: dict, state: WorkflowState) -> Any:
        """知识库检索节点"""
        dataset_id = config.get("dataset_id", "")
        query_template = config.get("query", "")
        top_k = config.get("top_k", 5)

        query = NodeExecutors._render_template(query_template, state.variables)

        from app.core.rag_service import retrieve

        results = await retrieve(
            dataset_id=dataset_id,
            query=query,
            top_k=top_k,
        )

        # 格式化检索结果
        parts = []
        for i, r in enumerate(results, 1):
            parts.append(f"[{i}] (相关度: {r['score']:.2%})\n{r['content']}")

        output = "\n\n".join(parts) if parts else "未找到相关内容"

        # 将检索结果写入 variables
        return output

    @staticmethod
    async def execute_code(config: dict, state: WorkflowState) -> Any:
        """代码执行节点（安全受限）"""
        code = config.get("code", "")

        # 安全白名单
        allowed_builtins = {
            "abs": abs, "round": round, "min": min, "max": max,
            "len": len, "str": str, "int": int, "float": float,
            "bool": bool, "list": list, "dict": dict, "tuple": tuple,
            "range": range, "enumerate": enumerate, "zip": zip,
            "sorted": sorted, "reversed": reversed,
            "print": lambda *a, **kw: None,  # 禁止输出
            "isinstance": isinstance,
            "type": type,
        }

        # 构建安全命名空间
        safe_globals = {"__builtins__": allowed_builtins}
        safe_locals = {
            "inputs": dict(state.variables),
            "math": math,
            "json": json,
            "datetime": datetime,
            "result": None,
        }

        try:
            # 超时执行
            loop = asyncio.get_event_loop()
            await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: exec(code, safe_globals, safe_locals)
                ),
                timeout=10.0,
            )

            return safe_locals.get("result", "代码执行完成（未设置 result 变量）")
        except asyncio.TimeoutError:
            raise RuntimeError("代码执行超时（限制 10 秒）")
        except Exception as e:
            raise RuntimeError(f"代码执行错误: {e}")

    @staticmethod
    async def execute_condition(config: dict, state: WorkflowState) -> str:
        """
        条件分支节点：返回分支名称。

        config 格式:
        {
            "conditions": [
                {"expression": "len(inputs.get('query', '')) > 10", "branch": "long_query"},
                {"expression": "True", "branch": "default"}
            ]
        }
        """
        conditions = config.get("conditions", [])

        safe_globals = {"__builtins__": {"len": len, "str": str, "int": int, "float": float, "bool": bool}}
        safe_locals = {"inputs": dict(state.variables)}

        for cond in conditions:
            expr = cond.get("expression", "True")
            branch = cond.get("branch", "default")
            try:
                if eval(expr, safe_globals, safe_locals):
                    return branch
            except Exception:
                continue

        return "default"

    @staticmethod
    def _render_template(template: str, variables: dict) -> str:
        """渲染 {{variable}} 模板"""
        def replacer(match):
            var_name = match.group(1).strip()
            return str(variables.get(var_name, match.group(0)))

        return re.sub(r"\{\{(\w+)\}\}", replacer, template)


# ==================== Workflow Engine ====================


class WorkflowEngine:
    """
    工作流引擎：解析 graph_data JSON，按拓扑顺序执行节点。
    使用简单的拓扑排序 + 依次执行，不依赖 LangGraph 运行时以降低复杂度。
    每个节点执行后通过 SSE yield 事件。
    """

    # 节点执行器映射
    NODE_EXECUTORS = {
        "start": NodeExecutors.execute_start,
        "llm": NodeExecutors.execute_llm,
        "knowledge": NodeExecutors.execute_knowledge,
        "code": NodeExecutors.execute_code,
        "condition": NodeExecutors.execute_condition,
        "end": None,  # end 节点只收集最终输出
    }

    @classmethod
    async def run(
        cls,
        graph_data: dict,
        inputs: dict,
        provider_configs: dict | None = None,
    ) -> AsyncGenerator[dict, None]:
        """
        执行工作流，SSE 流式返回每个节点的执行状态。

        Args:
            graph_data: 工作流的图定义 (nodes + edges)
            inputs: 工作流输入变量
            provider_configs: Provider 配置映射 {provider_id: {provider_type, api_key, base_url}}

        Yields:
            SSE 事件 dict:
              {"node_id": "...", "status": "running/completed/failed", "type": "...", "output": "..."}
              {"type": "workflow_completed", "final_output": "..."}
        """
        import time

        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        provider_configs = provider_configs or {}

        # 构建节点映射
        node_map = {n["id"]: n for n in nodes}

        # 构建邻接表
        adjacency: dict[str, list[str]] = {n["id"]: [] for n in nodes}
        for edge in edges:
            src = edge["source"]
            tgt = edge["target"]
            if src in adjacency:
                adjacency[src].append(tgt)

        # 拓扑排序
        execution_order = cls._topological_sort(nodes, edges)

        # 初始化状态
        state = WorkflowState(inputs=inputs)

        last_output = None

        for node_id in execution_order:
            node = node_map.get(node_id)
            if not node:
                continue

            node_type = node.get("type", "")
            config = dict(node.get("config", {}))

            # 注入 provider 配置到 LLM 节点
            if node_type == "llm" and provider_configs:
                pid = config.get("provider_id", "")
                if pid and pid in provider_configs:
                    pc = provider_configs[pid]
                    config["provider_type"] = pc.get("provider_type", "openai")
                    config["api_key"] = pc.get("api_key", "")
                    config["base_url"] = pc.get("base_url")

            # 条件节点特殊处理：检查是否应该执行此节点
            # (通过检查所有指向此节点的边的来源节点的条件分支是否匹配)

            executor = cls.NODE_EXECUTORS.get(node_type)

            # End 节点
            if node_type == "end":
                yield {
                    "node_id": node_id,
                    "status": "completed",
                    "type": "end",
                    "output": last_output,
                }
                state.final_output = last_output
                continue

            if executor is None:
                continue

            # 发送 running 事件
            yield {
                "node_id": node_id,
                "status": "running",
                "type": node_type,
            }

            start_time = time.time()

            try:
                output = await executor(config, state)
                duration = int((time.time() - start_time) * 1000)

                # 存储节点结果到 variables (用节点 ID 和可选的输出变量名)
                output_var = node.get("output_var", node_id)
                state.variables[output_var] = output
                last_output = output

                # 记录结果
                state.node_results[node_id] = NodeResult(
                    node_id=node_id,
                    node_type=node_type,
                    status="completed",
                    output=output,
                    duration_ms=duration,
                )

                yield {
                    "node_id": node_id,
                    "status": "completed",
                    "type": node_type,
                    "output": str(output) if output else "",  
                    "duration_ms": duration,
                }

                # 条件节点：记录选择的分支
                if node_type == "condition":
                    yield {
                        "node_id": node_id,
                        "status": "completed",
                        "type": "condition",
                        "branch": str(output),
                    }

            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                state.node_results[node_id] = NodeResult(
                    node_id=node_id,
                    node_type=node_type,
                    status="failed",
                    error=str(e),
                    duration_ms=duration,
                )

                yield {
                    "node_id": node_id,
                    "status": "failed",
                    "type": node_type,
                    "error": str(e),
                    "duration_ms": duration,
                }

                # 节点失败，终止工作流
                yield {
                    "type": "workflow_error",
                    "error": f"节点 {node_id} 执行失败: {e}",
                }
                return

        # 工作流执行完成
        yield {
            "type": "workflow_completed",
            "final_output": str(state.final_output) if state.final_output else "",
            "node_count": len(execution_order),
        }

    @staticmethod
    def _topological_sort(nodes: list[dict], edges: list[dict]) -> list[str]:
        """拓扑排序：确定节点执行顺序"""
        in_degree: dict[str, int] = {n["id"]: 0 for n in nodes}
        adjacency: dict[str, list[str]] = {n["id"]: [] for n in nodes}

        for edge in edges:
            src = edge["source"]
            tgt = edge["target"]
            if src in adjacency and tgt in in_degree:
                adjacency[src].append(tgt)
                in_degree[tgt] += 1

        # BFS 拓扑排序
        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            node_id = queue.pop(0)
            order.append(node_id)
            for neighbor in adjacency.get(node_id, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return order
