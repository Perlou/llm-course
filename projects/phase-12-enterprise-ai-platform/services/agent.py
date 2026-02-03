"""
Agent 服务
==========

工作流自动化 Agent，支持工具调用和任务编排。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool, tool
from langchain_core.language_models import BaseChatModel

import sys
sys.path.insert(0, str(__file__).rsplit("/", 1)[0].rsplit("/", 1)[0])
from config import config
from services.llm_provider import get_llm
from services.knowledge_base import get_kb_manager


@dataclass
class AgentStep:
    """Agent 执行步骤"""

    thought: str
    action: str
    action_input: Any
    observation: str


@dataclass
class AgentResult:
    """Agent 执行结果"""

    output: str
    steps: List[AgentStep] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None


# ==================== 内置工具 ====================


@tool
def search_knowledge_base(query: str, kb_id: str = None) -> str:
    """在知识库中搜索信息。

    Args:
        query: 搜索查询
        kb_id: 知识库 ID（可选，不指定则使用第一个知识库）
    """
    try:
        manager = get_kb_manager()
        kbs = manager.list_knowledge_bases()

        if not kbs:
            return "没有可用的知识库"

        if kb_id:
            kb = manager.get_knowledge_base(kb_id)
            if not kb:
                return f"知识库不存在: {kb_id}"
        else:
            kb = kbs[0]

        result = manager.query(kb.id, query)
        return f"回答: {result.answer}\n\n来源: {', '.join([s['filename'] for s in result.sources])}"

    except Exception as e:
        return f"搜索失败: {str(e)}"


@tool
def list_knowledge_bases() -> str:
    """列出所有可用的知识库。"""
    try:
        manager = get_kb_manager()
        kbs = manager.list_knowledge_bases()

        if not kbs:
            return "没有可用的知识库"

        result = "可用的知识库:\n"
        for kb in kbs:
            result += f"- {kb.name} (ID: {kb.id}, 文档数: {kb.document_count})\n"
        return result

    except Exception as e:
        return f"获取知识库列表失败: {str(e)}"


@tool
def calculate(expression: str) -> str:
    """计算数学表达式。

    Args:
        expression: 数学表达式，如 "2 + 2" 或 "100 * 0.15"
    """
    try:
        # 安全计算
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "表达式包含不允许的字符"

        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


@tool
def get_current_time() -> str:
    """获取当前日期和时间。"""
    from datetime import datetime
    now = datetime.now()
    return f"当前时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')}"


@tool
def summarize_text(text: str) -> str:
    """对文本进行摘要。

    Args:
        text: 需要摘要的文本
    """
    try:
        llm = get_llm(temperature=0.3)
        from langchain.prompts import ChatPromptTemplate
        from langchain.schema.output_parser import StrOutputParser

        prompt = ChatPromptTemplate.from_template(
            "请对以下文本进行简洁的摘要，保留关键信息：\n\n{text}\n\n摘要："
        )
        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"text": text})
    except Exception as e:
        return f"摘要失败: {str(e)}"


# ==================== Agent 实现 ====================


class WorkflowAgent:
    """工作流 Agent"""

    SYSTEM_PROMPT = """你是一个智能助手，可以使用工具来完成用户的任务。

可用工具:
{tools}

工具名称列表: {tool_names}

请按以下格式思考和行动:

Question: 用户的问题或任务
Thought: 思考如何完成任务
Action: 选择要使用的工具，必须是 [{tool_names}] 中的一个
Action Input: 工具的输入参数
Observation: 工具的返回结果
... (可以重复 Thought/Action/Action Input/Observation)
Thought: 我已完成任务
Final Answer: 最终答案

注意:
- 每次只能使用一个工具
- 仔细阅读工具描述，正确使用
- 如果任务不需要工具，直接给出 Final Answer

开始!

Question: {input}
Thought: {agent_scratchpad}"""

    def __init__(self, tools: List[BaseTool] = None):
        self.tools = tools or self._get_default_tools()
        self.llm = get_llm(temperature=0.3)
        self.agent_executor = self._create_agent()

    def _get_default_tools(self) -> List[BaseTool]:
        """获取默认工具集"""
        return [
            search_knowledge_base,
            list_knowledge_bases,
            calculate,
            get_current_time,
            summarize_text,
        ]

    def _create_agent(self) -> AgentExecutor:
        """创建 Agent"""
        prompt = PromptTemplate.from_template(self.SYSTEM_PROMPT)

        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt,
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

    def run(self, task: str) -> AgentResult:
        """执行任务"""
        try:
            result = self.agent_executor.invoke({"input": task})

            # 提取步骤
            steps = []
            for action, observation in result.get("intermediate_steps", []):
                step = AgentStep(
                    thought=getattr(action, "log", ""),
                    action=action.tool,
                    action_input=action.tool_input,
                    observation=str(observation)[:500],
                )
                steps.append(step)

            return AgentResult(
                output=result.get("output", ""),
                steps=steps,
                success=True,
            )

        except Exception as e:
            return AgentResult(
                output="",
                success=False,
                error=str(e),
            )


# 全局实例
_agent: Optional[WorkflowAgent] = None


def get_agent() -> WorkflowAgent:
    """获取 Agent 实例"""
    global _agent
    if _agent is None:
        _agent = WorkflowAgent()
    return _agent
