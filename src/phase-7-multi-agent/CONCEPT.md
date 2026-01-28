# Phase 7: 多 Agent 系统

> 掌握多 Agent 协作系统设计与 Agent Skill

---

## 目录

1. [多 Agent 系统概述](#1-多-agent-系统概述)
2. [Agent Skill 技能设计](#2-agent-skill-技能设计)
3. [多 Agent 协作架构](#3-多-agent-协作架构)
4. [Agent 通信机制](#4-agent-通信机制)
5. [实战：构建多 Agent 系统](#5-实战构建多-agent-系统)
6. [高级模式与最佳实践](#6-高级模式与最佳实践)

---

## 1. 多 Agent 系统概述

### 1.1 什么是多 Agent 系统

```
┌─────────────────────────────────────────────────────────────────┐
│                    Multi-Agent System (MAS)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    ┌─────────┐      ┌─────────┐      ┌─────────┐              │
│    │ Agent A │◄────►│ Agent B │◄────►│ Agent C │              │
│    │ (规划)  │      │ (执行)  │      │ (验证)  │              │
│    └────┬────┘      └────┬────┘      └────┬────┘              │
│         │                │                │                     │
│         ▼                ▼                ▼                     │
│    ┌─────────────────────────────────────────────┐             │
│    │              共享环境/知识库                 │             │
│    └─────────────────────────────────────────────┘             │
│                                                                 │
│    特点: 自主性 | 协作性 | 分布式 | 专业化                      │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 单 Agent vs 多 Agent

```
┌────────────────────────────────────────────────────────────────┐
│                         对比分析                                │
├──────────────────┬─────────────────┬───────────────────────────┤
│      维度        │    单 Agent     │       多 Agent            │
├──────────────────┼─────────────────┼───────────────────────────┤
│  任务复杂度      │  简单到中等     │   复杂任务                 │
│  专业性         │  通用型         │   各司其职                 │
│  可扩展性       │  有限           │   高度可扩展               │
│  容错能力       │  单点故障       │   分布式容错               │
│  开发复杂度     │  低             │   中到高                   │
│  通信开销       │  无             │   需要协调                 │
│  适用场景       │  问答、简单任务  │   软件开发、研究、创作     │
└──────────────────┴─────────────────┴───────────────────────────┘
```

### 1.3 多 Agent 系统的核心组件

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid

class AgentRole(Enum):
    """Agent 角色类型"""
    COORDINATOR = "coordinator"    # 协调者
    EXECUTOR = "executor"          # 执行者
    VALIDATOR = "validator"        # 验证者
    RESEARCHER = "researcher"      # 研究者
    CRITIC = "critic"              # 评审者

@dataclass
class Message:
    """Agent 间通信消息"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    receiver: str = ""  # 空字符串表示广播
    content: Any = None
    msg_type: str = "text"
    metadata: Dict = field(default_factory=dict)

@dataclass
class AgentState:
    """Agent 状态"""
    status: str = "idle"  # idle, working, waiting, completed
    current_task: Optional[str] = None
    memory: List[Dict] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)

class BaseAgent(ABC):
    """Agent 基类"""

    def __init__(self, name: str, role: AgentRole, description: str = ""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.description = description
        self.state = AgentState()
        self.inbox: List[Message] = []
        self.outbox: List[Message] = []

    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """处理输入数据"""
        pass

    @abstractmethod
    async def receive_message(self, message: Message):
        """接收消息"""
        pass

    def send_message(self, receiver: str, content: Any, msg_type: str = "text"):
        """发送消息"""
        message = Message(
            sender=self.name,
            receiver=receiver,
            content=content,
            msg_type=msg_type
        )
        self.outbox.append(message)
        return message

    def update_state(self, **kwargs):
        """更新状态"""
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
```

---

## 2. Agent Skill 技能设计

### 2.1 Skill 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Skill 架构                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Skill Registry                         │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │  │
│  │  │ 搜索    │ │ 代码    │ │ 数据    │ │ 通信    │        │  │
│  │  │ Skills  │ │ Skills  │ │ Skills  │ │ Skills  │        │  │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘        │  │
│  └───────┼──────────┼──────────┼──────────┼────────────────┘  │
│          │          │          │          │                    │
│          ▼          ▼          ▼          ▼                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Skill Executor                          │  │
│  │  • 参数验证  • 权限检查  • 执行监控  • 结果处理           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   External Tools                          │  │
│  │  API | Database | File System | Third-party Services     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Skill 基础框架

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import asyncio
import inspect

@dataclass
class SkillParameter:
    """技能参数定义"""
    name: str
    type: type
    description: str
    required: bool = True
    default: Any = None

@dataclass
class SkillMetadata:
    """技能元数据"""
    name: str
    description: str
    category: str
    parameters: List[SkillParameter]
    returns: str
    examples: List[str] = field(default_factory=list)
    requires_auth: bool = False
    rate_limit: Optional[int] = None  # 每分钟调用次数限制

class Skill(ABC):
    """技能基类"""

    def __init__(self):
        self.metadata = self._get_metadata()

    @abstractmethod
    def _get_metadata(self) -> SkillMetadata:
        """获取技能元数据"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """执行技能"""
        pass

    def validate_params(self, **kwargs) -> bool:
        """验证参数"""
        for param in self.metadata.parameters:
            if param.required and param.name not in kwargs:
                raise ValueError(f"Missing required parameter: {param.name}")
            if param.name in kwargs:
                if not isinstance(kwargs[param.name], param.type):
                    raise TypeError(
                        f"Parameter {param.name} should be {param.type}, "
                        f"got {type(kwargs[param.name])}"
                    )
        return True

    def to_function_schema(self) -> Dict:
        """转换为 OpenAI Function 格式"""
        properties = {}
        required = []

        for param in self.metadata.parameters:
            properties[param.name] = {
                "type": self._python_type_to_json(param.type),
                "description": param.description
            }
            if param.required:
                required.append(param.name)

        return {
            "name": self.metadata.name,
            "description": self.metadata.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

    def _python_type_to_json(self, python_type: type) -> str:
        """Python 类型转 JSON Schema 类型"""
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object"
        }
        return type_map.get(python_type, "string")
```

### 2.3 常用 Skill 实现

```python
import aiohttp
import subprocess
from pathlib import Path

# ==================== 搜索技能 ====================
class WebSearchSkill(Skill):
    """网络搜索技能"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        super().__init__()

    def _get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="web_search",
            description="搜索互联网获取最新信息",
            category="search",
            parameters=[
                SkillParameter("query", str, "搜索查询词"),
                SkillParameter("num_results", int, "返回结果数量", False, 5)
            ],
            returns="搜索结果列表，包含标题、链接和摘要",
            examples=["搜索最新的AI新闻", "查找Python教程"]
        )

    async def execute(self, query: str, num_results: int = 5) -> List[Dict]:
        self.validate_params(query=query, num_results=num_results)

        # 模拟搜索 API 调用
        async with aiohttp.ClientSession() as session:
            # 实际项目中替换为真实的搜索 API
            results = [
                {
                    "title": f"Result {i} for: {query}",
                    "url": f"https://example.com/{i}",
                    "snippet": f"This is a snippet about {query}..."
                }
                for i in range(num_results)
            ]
        return results


# ==================== 代码执行技能 ====================
class CodeExecutionSkill(Skill):
    """代码执行技能"""

    def __init__(self, allowed_languages: List[str] = None):
        self.allowed_languages = allowed_languages or ["python", "javascript"]
        super().__init__()

    def _get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="execute_code",
            description="在安全沙箱中执行代码",
            category="code",
            parameters=[
                SkillParameter("code", str, "要执行的代码"),
                SkillParameter("language", str, "编程语言"),
                SkillParameter("timeout", int, "超时时间(秒)", False, 30)
            ],
            returns="代码执行结果或错误信息"
        )

    async def execute(self, code: str, language: str, timeout: int = 30) -> Dict:
        self.validate_params(code=code, language=language, timeout=timeout)

        if language not in self.allowed_languages:
            return {"error": f"Language {language} not supported"}

        try:
            if language == "python":
                result = await self._execute_python(code, timeout)
            else:
                result = {"error": f"Language {language} not implemented"}
            return result
        except Exception as e:
            return {"error": str(e)}

    async def _execute_python(self, code: str, timeout: int) -> Dict:
        """执行 Python 代码"""
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            process = await asyncio.create_subprocess_exec(
                'python', temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            return {
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "return_code": process.returncode
            }
        finally:
            os.unlink(temp_file)


# ==================== 文件操作技能 ====================
class FileOperationSkill(Skill):
    """文件操作技能"""

    def __init__(self, workspace: str = "./workspace"):
        self.workspace = Path(workspace)
        self.workspace.mkdir(exist_ok=True)
        super().__init__()

    def _get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="file_operation",
            description="读写文件",
            category="file",
            parameters=[
                SkillParameter("operation", str, "操作类型: read/write/list"),
                SkillParameter("path", str, "文件路径"),
                SkillParameter("content", str, "写入内容(仅write需要)", False, "")
            ],
            returns="操作结果"
        )

    async def execute(self, operation: str, path: str, content: str = "") -> Dict:
        file_path = self.workspace / path

        # 安全检查：防止路径遍历
        if not str(file_path.resolve()).startswith(str(self.workspace.resolve())):
            return {"error": "Access denied: path outside workspace"}

        if operation == "read":
            if file_path.exists():
                return {"content": file_path.read_text()}
            return {"error": "File not found"}

        elif operation == "write":
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return {"success": True, "path": str(file_path)}

        elif operation == "list":
            if file_path.is_dir():
                files = [str(f.relative_to(self.workspace)) for f in file_path.iterdir()]
                return {"files": files}
            return {"error": "Not a directory"}

        return {"error": f"Unknown operation: {operation}"}


# ==================== 数据分析技能 ====================
class DataAnalysisSkill(Skill):
    """数据分析技能"""

    def _get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="analyze_data",
            description="分析数据并生成统计报告",
            category="analysis",
            parameters=[
                SkillParameter("data", list, "要分析的数据列表"),
                SkillParameter("analysis_type", str, "分析类型: summary/correlation/trend")
            ],
            returns="分析结果报告"
        )

    async def execute(self, data: list, analysis_type: str) -> Dict:
        import statistics

        if not data:
            return {"error": "Empty data"}

        if analysis_type == "summary":
            numeric_data = [x for x in data if isinstance(x, (int, float))]
            if not numeric_data:
                return {"error": "No numeric data found"}

            return {
                "count": len(numeric_data),
                "mean": statistics.mean(numeric_data),
                "median": statistics.median(numeric_data),
                "stdev": statistics.stdev(numeric_data) if len(numeric_data) > 1 else 0,
                "min": min(numeric_data),
                "max": max(numeric_data)
            }

        return {"error": f"Analysis type {analysis_type} not implemented"}
```

### 2.4 Skill 注册中心

```python
class SkillRegistry:
    """技能注册中心"""

    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        self._categories: Dict[str, List[str]] = {}

    def register(self, skill: Skill) -> None:
        """注册技能"""
        name = skill.metadata.name
        category = skill.metadata.category

        self._skills[name] = skill

        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(name)

        print(f"✅ Registered skill: {name} (category: {category})")

    def unregister(self, skill_name: str) -> bool:
        """注销技能"""
        if skill_name in self._skills:
            skill = self._skills.pop(skill_name)
            category = skill.metadata.category
            self._categories[category].remove(skill_name)
            return True
        return False

    def get(self, skill_name: str) -> Optional[Skill]:
        """获取技能"""
        return self._skills.get(skill_name)

    def list_all(self) -> List[str]:
        """列出所有技能"""
        return list(self._skills.keys())

    def list_by_category(self, category: str) -> List[str]:
        """按分类列出技能"""
        return self._categories.get(category, [])

    def get_all_schemas(self) -> List[Dict]:
        """获取所有技能的 Function Schema"""
        return [skill.to_function_schema() for skill in self._skills.values()]

    def search(self, query: str) -> List[Skill]:
        """搜索技能"""
        results = []
        query_lower = query.lower()

        for skill in self._skills.values():
            if (query_lower in skill.metadata.name.lower() or
                query_lower in skill.metadata.description.lower()):
                results.append(skill)

        return results

    async def execute(self, skill_name: str, **kwargs) -> Any:
        """执行技能"""
        skill = self.get(skill_name)
        if not skill:
            raise ValueError(f"Skill {skill_name} not found")

        return await skill.execute(**kwargs)


# 使用示例
def create_skill_registry() -> SkillRegistry:
    """创建并初始化技能注册中心"""
    registry = SkillRegistry()

    # 注册各种技能
    registry.register(WebSearchSkill(api_key="your-api-key"))
    registry.register(CodeExecutionSkill())
    registry.register(FileOperationSkill())
    registry.register(DataAnalysisSkill())

    return registry
```

---

## 3. 多 Agent 协作架构

### 3.1 常见架构模式

```
┌─────────────────────────────────────────────────────────────────┐
│                    多 Agent 架构模式对比                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 层级式 (Hierarchical)          2. 扁平式 (Flat/Peer)        │
│                                                                 │
│       ┌─────────┐                   ┌───┐ ┌───┐ ┌───┐          │
│       │Supervisor│                  │ A │◄─►│ B │◄─►│ C │        │
│       └────┬────┘                   └─┬─┘ └─┬─┘ └─┬─┘          │
│      ┌─────┼─────┐                    └─────┼─────┘              │
│      ▼     ▼     ▼                          ▼                   │
│   ┌───┐ ┌───┐ ┌───┐                  所有Agent平等协作            │
│   │ A │ │ B │ │ C │                                             │
│   └───┘ └───┘ └───┘                                             │
│                                                                 │
│  3. 流水线式 (Pipeline)             4. 混合式 (Hybrid)          │
│                                                                 │
│   ┌───┐   ┌───┐   ┌───┐               ┌─────────┐               │
│   │ A │──►│ B │──►│ C │               │Orchestrator│            │
│   └───┘   └───┘   └───┘               └─────┬───┘               │
│     │       │       │                       │                   │
│     ▼       ▼       ▼                 ┌─────┴─────┐             │
│  Stage1  Stage2  Stage3              ▼           ▼              │
│                                   ┌─────┐     ┌─────┐           │
│                                   │Team A│     │Team B│          │
│                                   └─────┘     └─────┘           │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 层级式架构实现

```python
from typing import Dict, List, Any, Optional
import asyncio
from enum import Enum
from openai import AsyncOpenAI

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    """任务定义"""
    id: str
    description: str
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    dependencies: List[str] = field(default_factory=list)
    priority: int = 0

class SupervisorAgent(BaseAgent):
    """主管 Agent - 负责任务分解和分配"""

    def __init__(self, name: str, workers: List['WorkerAgent'], llm_client: AsyncOpenAI):
        super().__init__(name, AgentRole.COORDINATOR, "负责协调和分配任务")
        self.workers = {w.name: w for w in workers}
        self.client = llm_client
        self.task_queue: List[Task] = []
        self.completed_tasks: Dict[str, Task] = {}

    async def process(self, input_data: str) -> Dict:
        """处理用户请求"""
        # 1. 分解任务
        subtasks = await self._decompose_task(input_data)

        # 2. 分配任务给 Workers
        assignments = await self._assign_tasks(subtasks)

        # 3. 监督执行
        results = await self._supervise_execution(assignments)

        # 4. 汇总结果
        final_result = await self._aggregate_results(results)

        return final_result

    async def _decompose_task(self, task: str) -> List[Task]:
        """使用 LLM 分解任务"""
        worker_descriptions = "\n".join([
            f"- {name}: {w.description}, skills: {w.state.skills}"
            for name, w in self.workers.items()
        ])

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""你是一个任务分解专家。根据用户需求，将任务分解为子任务。

可用的工作者:
{worker_descriptions}

请以 JSON 格式返回子任务列表:
[
    {{"id": "task_1", "description": "子任务描述", "suggested_worker": "worker名称", "priority": 1}},
    ...
]"""
                },
                {"role": "user", "content": task}
            ],
            response_format={"type": "json_object"}
        )

        import json
        subtasks_data = json.loads(response.choices[0].message.content)

        return [
            Task(
                id=t["id"],
                description=t["description"],
                assigned_to=t.get("suggested_worker"),
                priority=t.get("priority", 0)
            )
            for t in subtasks_data.get("tasks", [])
        ]

    async def _assign_tasks(self, tasks: List[Task]) -> Dict[str, List[Task]]:
        """分配任务给 Workers"""
        assignments = {name: [] for name in self.workers}

        # 按优先级排序
        sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)

        for task in sorted_tasks:
            if task.assigned_to and task.assigned_to in self.workers:
                assignments[task.assigned_to].append(task)
            else:
                # 选择任务最少的 worker
                min_worker = min(assignments, key=lambda w: len(assignments[w]))
                assignments[min_worker].append(task)
                task.assigned_to = min_worker

        return assignments

    async def _supervise_execution(self, assignments: Dict[str, List[Task]]) -> Dict[str, Any]:
        """监督任务执行"""
        results = {}

        # 并行执行各 Worker 的任务
        async def execute_worker_tasks(worker_name: str, tasks: List[Task]):
            worker = self.workers[worker_name]
            worker_results = []

            for task in tasks:
                task.status = TaskStatus.IN_PROGRESS
                self.send_message(worker_name, task, "task")

                result = await worker.process(task)
                task.status = TaskStatus.COMPLETED
                task.result = result
                worker_results.append(result)

            return worker_name, worker_results

        # 并行执行
        coroutines = [
            execute_worker_tasks(name, tasks)
            for name, tasks in assignments.items() if tasks
        ]

        completed = await asyncio.gather(*coroutines)

        for worker_name, worker_results in completed:
            results[worker_name] = worker_results

        return results

    async def _aggregate_results(self, results: Dict[str, Any]) -> Dict:
        """汇总结果"""
        all_results = []
        for worker_name, worker_results in results.items():
            for result in worker_results:
                all_results.append({
                    "worker": worker_name,
                    "result": result
                })

        # 使用 LLM 生成最终总结
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个结果汇总专家。请将各个工作者的结果整合成一个连贯的最终报告。"
                },
                {"role": "user", "content": f"各工作者的结果:\n{all_results}"}
            ]
        )

        return {
            "summary": response.choices[0].message.content,
            "details": results
        }

    async def receive_message(self, message: Message):
        """接收消息"""
        self.inbox.append(message)
        # 处理来自 Worker 的状态更新等


class WorkerAgent(BaseAgent):
    """工作者 Agent"""

    def __init__(self, name: str, role: AgentRole, description: str,
                 skills: List[str], skill_registry: SkillRegistry,
                 llm_client: AsyncOpenAI):
        super().__init__(name, role, description)
        self.state.skills = skills
        self.skill_registry = skill_registry
        self.client = llm_client

    async def process(self, task: Task) -> Any:
        """处理任务"""
        # 1. 理解任务并规划执行步骤
        plan = await self._create_plan(task)

        # 2. 执行计划
        results = []
        for step in plan:
            result = await self._execute_step(step)
            results.append(result)

        # 3. 生成任务结果
        final_result = await self._generate_result(task, results)

        return final_result

    async def _create_plan(self, task: Task) -> List[Dict]:
        """创建执行计划"""
        available_skills = [
            self.skill_registry.get(s).metadata.description
            for s in self.state.skills
            if self.skill_registry.get(s)
        ]

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""你是 {self.name}，{self.description}。

你可使用的技能: {self.state.skills}
技能描述: {available_skills}

请为任务创建执行计划，返回 JSON:
{{"steps": [{{"skill": "技能名", "params": {{参数}}, "description": "步骤描述"}}]}}"""
                },
                {"role": "user", "content": f"任务: {task.description}"}
            ],
            response_format={"type": "json_object"}
        )

        import json
        plan = json.loads(response.choices[0].message.content)
        return plan.get("steps", [])

    async def _execute_step(self, step: Dict) -> Any:
        """执行单个步骤"""
        skill_name = step.get("skill")
        params = step.get("params", {})

        if skill_name in self.state.skills:
            result = await self.skill_registry.execute(skill_name, **params)
            return result
        else:
            return {"error": f"Skill {skill_name} not available"}

    async def _generate_result(self, task: Task, step_results: List) -> str:
        """生成最终结果"""
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "根据执行步骤的结果，生成任务的最终结果报告。"
                },
                {
                    "role": "user",
                    "content": f"任务: {task.description}\n执行结果: {step_results}"
                }
            ]
        )
        return response.choices[0].message.content

    async def receive_message(self, message: Message):
        """接收消息"""
        self.inbox.append(message)
```

### 3.3 流水线式架构实现

```python
class PipelineStage:
    """流水线阶段"""

    def __init__(self, agent: BaseAgent, next_stage: Optional['PipelineStage'] = None):
        self.agent = agent
        self.next_stage = next_stage

    async def process(self, input_data: Any) -> Any:
        # 当前阶段处理
        result = await self.agent.process(input_data)

        # 传递给下一阶段
        if self.next_stage:
            return await self.next_stage.process(result)

        return result


class Pipeline:
    """多 Agent 流水线"""

    def __init__(self):
        self.stages: List[PipelineStage] = []
        self.head: Optional[PipelineStage] = None

    def add_stage(self, agent: BaseAgent) -> 'Pipeline':
        """添加阶段"""
        stage = PipelineStage(agent)

        if self.stages:
            self.stages[-1].next_stage = stage
        else:
            self.head = stage

        self.stages.append(stage)
        return self

    async def execute(self, input_data: Any) -> Any:
        """执行流水线"""
        if not self.head:
            raise ValueError("Pipeline is empty")

        return await self.head.process(input_data)

    def visualize(self) -> str:
        """可视化流水线"""
        if not self.stages:
            return "Empty Pipeline"

        names = [stage.agent.name for stage in self.stages]
        return " → ".join(names)


# 使用示例：代码审查流水线
async def create_code_review_pipeline(client: AsyncOpenAI, registry: SkillRegistry):
    """创建代码审查流水线"""

    # 阶段1: 代码分析 Agent
    analyzer = WorkerAgent(
        name="CodeAnalyzer",
        role=AgentRole.EXECUTOR,
        description="分析代码结构和质量",
        skills=["execute_code", "file_operation"],
        skill_registry=registry,
        llm_client=client
    )

    # 阶段2: 安全审查 Agent
    security_reviewer = WorkerAgent(
        name="SecurityReviewer",
        role=AgentRole.VALIDATOR,
        description="检查代码安全漏洞",
        skills=["web_search"],
        skill_registry=registry,
        llm_client=client
    )

    # 阶段3: 报告生成 Agent
    reporter = WorkerAgent(
        name="ReportGenerator",
        role=AgentRole.EXECUTOR,
        description="生成审查报告",
        skills=["file_operation"],
        skill_registry=registry,
        llm_client=client
    )

    # 构建流水线
    pipeline = Pipeline()
    pipeline.add_stage(analyzer)
    pipeline.add_stage(security_reviewer)
    pipeline.add_stage(reporter)

    print(f"Pipeline: {pipeline.visualize()}")
    return pipeline
```

---

## 4. Agent 通信机制

### 4.1 消息总线架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      Message Bus Architecture                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐                  │
│   │ Agent A │     │ Agent B │     │ Agent C │                  │
│   └────┬────┘     └────┬────┘     └────┬────┘                  │
│        │               │               │                        │
│   ┌────┴────┐     ┌────┴────┐     ┌────┴────┐                  │
│   │ Mailbox │     │ Mailbox │     │ Mailbox │                  │
│   └────┬────┘     └────┬────┘     └────┬────┘                  │
│        │               │               │                        │
│   ─────┴───────────────┴───────────────┴─────                  │
│                        │                                        │
│              ┌─────────┴─────────┐                             │
│              │    Message Bus     │                             │
│              │  ┌─────────────┐  │                             │
│              │  │ Topic: tasks │  │                             │
│              │  │ Topic: events│  │                             │
│              │  │ Topic: status│  │                             │
│              │  └─────────────┘  │                             │
│              └───────────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 消息总线实现

```python
from typing import Callable, Awaitable
import asyncio
from collections import defaultdict

class MessageBus:
    """异步消息总线"""

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False

    def subscribe(self, topic: str, handler: Callable[[Message], Awaitable[None]]):
        """订阅主题"""
        self.subscribers[topic].append(handler)
        print(f"📥 Subscribed to topic: {topic}")

    def unsubscribe(self, topic: str, handler: Callable):
        """取消订阅"""
        if handler in self.subscribers[topic]:
            self.subscribers[topic].remove(handler)

    async def publish(self, topic: str, message: Message):
        """发布消息"""
        await self.message_queue.put((topic, message))

    async def start(self):
        """启动消息总线"""
        self.running = True
        print("🚀 Message bus started")

        while self.running:
            try:
                topic, message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )

                # 分发消息给订阅者
                handlers = self.subscribers.get(topic, [])
                if handlers:
                    await asyncio.gather(*[h(message) for h in handlers])

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Message bus error: {e}")

    def stop(self):
        """停止消息总线"""
        self.running = False
        print("🛑 Message bus stopped")


class AgentCommunicator:
    """Agent 通信器"""

    def __init__(self, agent: BaseAgent, message_bus: MessageBus):
        self.agent = agent
        self.bus = message_bus
        self._setup_subscriptions()

    def _setup_subscriptions(self):
        """设置消息订阅"""
        # 订阅发给自己的消息
        self.bus.subscribe(f"agent.{self.agent.name}", self._handle_direct_message)
        # 订阅广播消息
        self.bus.subscribe("broadcast", self._handle_broadcast)
        # 订阅角色相关消息
        self.bus.subscribe(f"role.{self.agent.role.value}", self._handle_role_message)

    async def _handle_direct_message(self, message: Message):
        """处理直接消息"""
        await self.agent.receive_message(message)

    async def _handle_broadcast(self, message: Message):
        """处理广播消息"""
        if message.sender != self.agent.name:
            await self.agent.receive_message(message)

    async def _handle_role_message(self, message: Message):
        """处理角色相关消息"""
        await self.agent.receive_message(message)

    async def send_to_agent(self, target: str, content: Any, msg_type: str = "text"):
        """发送消息给指定 Agent"""
        message = Message(
            sender=self.agent.name,
            receiver=target,
            content=content,
            msg_type=msg_type
        )
        await self.bus.publish(f"agent.{target}", message)

    async def broadcast(self, content: Any, msg_type: str = "text"):
        """广播消息"""
        message = Message(
            sender=self.agent.name,
            receiver="",
            content=content,
            msg_type=msg_type
        )
        await self.bus.publish("broadcast", message)

    async def send_to_role(self, role: AgentRole, content: Any, msg_type: str = "text"):
        """发送消息给特定角色"""
        message = Message(
            sender=self.agent.name,
            receiver=role.value,
            content=content,
            msg_type=msg_type
        )
        await self.bus.publish(f"role.{role.value}", message)
```

### 4.3 共享状态管理

```python
import threading
from datetime import datetime

class SharedState:
    """多 Agent 共享状态"""

    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._history: List[Dict] = []
        self._lock = asyncio.Lock()
        self._observers: Dict[str, List[Callable]] = defaultdict(list)

    async def get(self, key: str, default: Any = None) -> Any:
        """获取状态"""
        async with self._lock:
            return self._state.get(key, default)

    async def set(self, key: str, value: Any, agent_id: str = "system"):
        """设置状态"""
        async with self._lock:
            old_value = self._state.get(key)
            self._state[key] = value

            # 记录历史
            self._history.append({
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id,
                "key": key,
                "old_value": old_value,
                "new_value": value
            })

            # 通知观察者
            for observer in self._observers.get(key, []):
                await observer(key, value, old_value)

    def observe(self, key: str, callback: Callable):
        """观察状态变化"""
        self._observers[key].append(callback)

    async def get_all(self) -> Dict[str, Any]:
        """获取所有状态"""
        async with self._lock:
            return self._state.copy()

    def get_history(self, key: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """获取状态变更历史"""
        if key:
            return [h for h in self._history if h["key"] == key][-limit:]
        return self._history[-limit:]


class Blackboard:
    """黑板模式 - Agent 共享知识库"""

    def __init__(self):
        self.sections: Dict[str, Dict[str, Any]] = {
            "goals": {},        # 目标
            "facts": {},        # 事实
            "hypotheses": {},   # 假设
            "solutions": {},    # 解决方案
            "actions": {}       # 待执行动作
        }
        self._lock = asyncio.Lock()

    async def write(self, section: str, key: str, value: Any,
                    confidence: float = 1.0, author: str = "unknown"):
        """写入黑板"""
        async with self._lock:
            if section not in self.sections:
                raise ValueError(f"Unknown section: {section}")

            self.sections[section][key] = {
                "value": value,
                "confidence": confidence,
                "author": author,
                "timestamp": datetime.now().isoformat()
            }

    async def read(self, section: str, key: Optional[str] = None) -> Any:
        """读取黑板"""
        async with self._lock:
            if key:
                return self.sections.get(section, {}).get(key)
            return self.sections.get(section, {})

    async def find_by_confidence(self, section: str,
                                  min_confidence: float = 0.5) -> List[Dict]:
        """按置信度筛选"""
        async with self._lock:
            items = self.sections.get(section, {})
            return [
                {"key": k, **v}
                for k, v in items.items()
                if v["confidence"] >= min_confidence
            ]

    def visualize(self) -> str:
        """可视化黑板内容"""
        lines = ["=" * 50, "BLACKBOARD", "=" * 50]

        for section, items in self.sections.items():
            lines.append(f"\n📋 {section.upper()}")
            lines.append("-" * 30)

            for key, data in items.items():
                conf = data.get("confidence", 0)
                lines.append(f"  • {key}: {data['value'][:50]}... (conf: {conf:.2f})")

        return "\n".join(lines)
```

---

## 5. 实战：构建多 Agent 系统

### 5.1 软件开发团队模拟

```python
"""
多 Agent 软件开发团队
======================
- PM Agent: 需求分析和任务分解
- Developer Agent: 代码编写
- Reviewer Agent: 代码审查
- Tester Agent: 测试验证
"""

class SoftwareTeam:
    """软件开发团队"""

    def __init__(self, llm_client: AsyncOpenAI):
        self.client = llm_client
        self.skill_registry = create_skill_registry()
        self.message_bus = MessageBus()
        self.blackboard = Blackboard()
        self.agents = self._create_agents()
        self.communicators = self._setup_communication()

    def _create_agents(self) -> Dict[str, BaseAgent]:
        """创建团队 Agents"""

        # PM Agent
        pm = WorkerAgent(
            name="PM",
            role=AgentRole.COORDINATOR,
            description="产品经理，负责需求分析和任务分解",
            skills=["web_search"],
            skill_registry=self.skill_registry,
            llm_client=self.client
        )

        # Developer Agent
        developer = WorkerAgent(
            name="Developer",
            role=AgentRole.EXECUTOR,
            description="开发工程师，负责编写代码",
            skills=["execute_code", "file_operation"],
            skill_registry=self.skill_registry,
            llm_client=self.client
        )

        # Reviewer Agent
        reviewer = WorkerAgent(
            name="Reviewer",
            role=AgentRole.CRITIC,
            description="代码审查员，负责审查代码质量",
            skills=["file_operation", "execute_code"],
            skill_registry=self.skill_registry,
            llm_client=self.client
        )

        # Tester Agent
        tester = WorkerAgent(
            name="Tester",
            role=AgentRole.VALIDATOR,
            description="测试工程师，负责测试验证",
            skills=["execute_code", "file_operation"],
            skill_registry=self.skill_registry,
            llm_client=self.client
        )

        return {
            "PM": pm,
            "Developer": developer,
            "Reviewer": reviewer,
            "Tester": tester
        }

    def _setup_communication(self) -> Dict[str, AgentCommunicator]:
        """设置通信"""
        communicators = {}
        for name, agent in self.agents.items():
            communicators[name] = AgentCommunicator(agent, self.message_bus)
        return communicators

    async def develop(self, requirement: str) -> Dict:
        """开发流程"""
        print(f"📋 收到需求: {requirement}\n")

        # 启动消息总线
        bus_task = asyncio.create_task(self.message_bus.start())

        try:
            # 阶段1: PM 分析需求
            print("=" * 50)
            print("阶段1: 需求分析")
            print("=" * 50)

            specs = await self._pm_analyze(requirement)
            await self.blackboard.write("goals", "specifications", specs,
                                        confidence=0.9, author="PM")
            print(f"✅ PM 完成需求分析")

            # 阶段2: Developer 编写代码
            print("\n" + "=" * 50)
            print("阶段2: 代码开发")
            print("=" * 50)

            code = await self._developer_code(specs)
            await self.blackboard.write("solutions", "code", code,
                                        confidence=0.8, author="Developer")
            print(f"✅ Developer 完成代码编写")

            # 阶段3: Reviewer 审查代码
            print("\n" + "=" * 50)
            print("阶段3: 代码审查")
            print("=" * 50)

            review = await self._reviewer_review(code)
            await self.blackboard.write("hypotheses", "review_result", review,
                                        confidence=0.85, author="Reviewer")
            print(f"✅ Reviewer 完成代码审查")

            # 如果需要修改，返回开发阶段
            if review.get("needs_revision"):
                print("\n⚠️ 需要修改代码...")
                code = await self._developer_revise(code, review["suggestions"])
                await self.blackboard.write("solutions", "code_v2", code,
                                            confidence=0.85, author="Developer")

            # 阶段4: Tester 测试
            print("\n" + "=" * 50)
            print("阶段4: 测试验证")
            print("=" * 50)

            test_result = await self._tester_test(code, specs)
            await self.blackboard.write("facts", "test_result", test_result,
                                        confidence=0.95, author="Tester")
            print(f"✅ Tester 完成测试")

            # 汇总结果
            return {
                "requirement": requirement,
                "specifications": specs,
                "code": code,
                "review": review,
                "test_result": test_result,
                "blackboard": self.blackboard.visualize()
            }

        finally:
            self.message_bus.stop()
            bus_task.cancel()

    async def _pm_analyze(self, requirement: str) -> Dict:
        """PM 分析需求"""
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """你是产品经理。分析需求并输出技术规格。
返回 JSON 格式:
{
    "summary": "需求摘要",
    "features": ["功能列表"],
    "tech_stack": ["技术栈"],
    "acceptance_criteria": ["验收标准"]
}"""
                },
                {"role": "user", "content": requirement}
            ],
            response_format={"type": "json_object"}
        )

        import json
        return json.loads(response.choices[0].message.content)

    async def _developer_code(self, specs: Dict) -> Dict:
        """Developer 编写代码"""
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """你是开发工程师。根据规格编写代码。
返回 JSON 格式:
{
    "language": "编程语言",
    "files": [{"name": "文件名", "content": "代码内容"}],
    "dependencies": ["依赖列表"],
    "run_command": "运行命令"
}"""
                },
                {"role": "user", "content": f"规格: {specs}"}
            ],
            response_format={"type": "json_object"}
        )

        import json
        return json.loads(response.choices[0].message.content)

    async def _reviewer_review(self, code: Dict) -> Dict:
        """Reviewer 审查代码"""
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """你是代码审查员。审查代码质量。
返回 JSON 格式:
{
    "score": 0-100,
    "issues": [{"severity": "high/medium/low", "description": "问题描述"}],
    "suggestions": ["改进建议"],
    "needs_revision": true/false
}"""
                },
                {"role": "user", "content": f"代码: {code}"}
            ],
            response_format={"type": "json_object"}
        )

        import json
        return json.loads(response.choices[0].message.content)

    async def _developer_revise(self, code: Dict, suggestions: List[str]) -> Dict:
        """Developer 修改代码"""
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "你是开发工程师。根据审查意见修改代码。返回相同的 JSON 格式。"
                },
                {
                    "role": "user",
                    "content": f"原代码: {code}\n\n修改建议: {suggestions}"
                }
            ],
            response_format={"type": "json_object"}
        )

        import json
        return json.loads(response.choices[0].message.content)

    async def _tester_test(self, code: Dict, specs: Dict) -> Dict:
        """Tester 测试代码"""
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """你是测试工程师。为代码编写测试并验证。
返回 JSON 格式:
{
    "test_cases": [{"name": "测试名", "status": "pass/fail", "details": "详情"}],
    "coverage": "覆盖率百分比",
    "overall_status": "pass/fail",
    "summary": "测试总结"
}"""
                },
                {
                    "role": "user",
                    "content": f"代码: {code}\n验收标准: {specs.get('acceptance_criteria')}"
                }
            ],
            response_format={"type": "json_object"}
        )

        import json
        return json.loads(response.choices[0].message.content)
```

### 5.2 研究助手团队

```python
class ResearchTeam:
    """研究助手团队"""

    def __init__(self, llm_client: AsyncOpenAI):
        self.client = llm_client
        self.skill_registry = create_skill_registry()
        self.shared_state = SharedState()

    async def research(self, topic: str, depth: str = "medium") -> Dict:
        """执行研究任务"""

        print(f"🔬 开始研究主题: {topic}")
        print(f"📊 研究深度: {depth}\n")

        # 1. 信息收集
        print("📥 阶段1: 信息收集...")
        raw_info = await self._gather_information(topic)
        await self.shared_state.set("raw_info", raw_info, "Researcher")

        # 2. 信息分析
        print("🔍 阶段2: 信息分析...")
        analysis = await self._analyze_information(raw_info)
        await self.shared_state.set("analysis", analysis, "Analyst")

        # 3. 批判性审查
        print("⚖️ 阶段3: 批判性审查...")
        critique = await self._critical_review(analysis)
        await self.shared_state.set("critique", critique, "Critic")

        # 4. 综合报告
        print("📝 阶段4: 生成报告...")
        report = await self._synthesize_report(topic, analysis, critique)

        return {
            "topic": topic,
            "raw_info": raw_info,
            "analysis": analysis,
            "critique": critique,
            "report": report
        }

    async def _gather_information(self, topic: str) -> Dict:
        """信息收集 Agent"""
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """你是研究信息收集专家。收集主题相关信息。
返回 JSON:
{
    "key_facts": ["关键事实"],
    "sources": ["信息来源"],
    "timeline": ["时间线事件"],
    "stakeholders": ["相关方"]
}"""
                },
                {"role": "user", "content": f"研究主题: {topic}"}
            ],
            response_format={"type": "json_object"}
        )

        import json
        return json.loads(response.choices[0].message.content)

    async def _analyze_information(self, info: Dict) -> Dict:
        """信息分析 Agent"""
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """你是研究分析专家。深入分析信息。
返回 JSON:
{
    "patterns": ["发现的模式"],
    "insights": ["深入见解"],
    "correlations": ["相关性"],
    "gaps": ["信息缺口"]
}"""
                },
                {"role": "user", "content": f"待分析信息: {info}"}
            ],
            response_format={"type": "json_object"}
        )

        import json
        return json.loads(response.choices[0].message.content)

    async def _critical_review(self, analysis: Dict) -> Dict:
        """批判性审查 Agent"""
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """你是批判性思维专家。审视分析的有效性。
返回 JSON:
{
    "strengths": ["分析优点"],
    "weaknesses": ["分析缺陷"],
    "biases": ["潜在偏见"],
    "alternative_views": ["替代观点"],
    "confidence_score": 0.0-1.0
}"""
                },
                {"role": "user", "content": f"待审查分析: {analysis}"}
            ],
            response_format={"type": "json_object"}
        )

        import json
        return json.loads(response.choices[0].message.content)

    async def _synthesize_report(self, topic: str, analysis: Dict, critique: Dict) -> str:
        """综合报告 Agent"""
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """你是研究报告撰写专家。
综合所有信息，生成一份结构清晰、论证有力的研究报告。
包含: 摘要、背景、主要发现、分析讨论、局限性、结论与建议。"""
                },
                {
                    "role": "user",
                    "content": f"""
主题: {topic}
分析结果: {analysis}
批判性审查: {critique}

请生成研究报告。"""
                }
            ]
        )

        return response.choices[0].message.content
```

### 5.3 完整运行示例

```python
async def main():
    """主函数"""
    from openai import AsyncOpenAI

    client = AsyncOpenAI()

    # 示例1: 软件开发团队
    print("=" * 60)
    print("🏗️  软件开发团队演示")
    print("=" * 60)

    dev_team = SoftwareTeam(client)
    result = await dev_team.develop(
        "开发一个简单的待办事项（Todo）API，支持增删改查操作"
    )

    print("\n" + "=" * 60)
    print("📦 最终交付物")
    print("=" * 60)
    print(f"规格: {result['specifications']}")
    print(f"代码: {result['code']}")
    print(f"审查: {result['review']}")
    print(f"测试: {result['test_result']}")

    # 示例2: 研究团队
    print("\n" + "=" * 60)
    print("🔬 研究助手团队演示")
    print("=" * 60)

    research_team = ResearchTeam(client)
    research_result = await research_team.research(
        "大语言模型在医疗领域的应用前景与挑战"
    )

    print("\n" + "=" * 60)
    print("📑 研究报告")
    print("=" * 60)
    print(research_result["report"])


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 6. 高级模式与最佳实践

### 6.1 动态 Agent 生成

```python
class AgentFactory:
    """Agent 工厂 - 动态生成 Agent"""

    def __init__(self, llm_client: AsyncOpenAI, skill_registry: SkillRegistry):
        self.client = llm_client
        self.registry = skill_registry

    async def create_agent_for_task(self, task_description: str) -> WorkerAgent:
        """根据任务动态创建 Agent"""

        # 使用 LLM 决定 Agent 配置
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""根据任务创建合适的 Agent 配置。
可用技能: {self.registry.list_all()}

返回 JSON:
{{
    "name": "Agent名称",
    "role": "coordinator/executor/validator/researcher/critic",
    "description": "Agent描述",
    "skills": ["所需技能列表"],
    "reasoning": "选择理由"
}}"""
                },
                {"role": "user", "content": f"任务: {task_description}"}
            ],
            response_format={"type": "json_object"}
        )

        import json
        config = json.loads(response.choices[0].message.content)

        role_map = {
            "coordinator": AgentRole.COORDINATOR,
            "executor": AgentRole.EXECUTOR,
            "validator": AgentRole.VALIDATOR,
            "researcher": AgentRole.RESEARCHER,
            "critic": AgentRole.CRITIC
        }

        agent = WorkerAgent(
            name=config["name"],
            role=role_map.get(config["role"], AgentRole.EXECUTOR),
            description=config["description"],
            skills=config["skills"],
            skill_registry=self.registry,
            llm_client=self.client
        )

        print(f"🤖 动态创建 Agent: {config['name']}")
        print(f"   理由: {config['reasoning']}")

        return agent
```

### 6.2 冲突解决机制

```python
class ConflictResolver:
    """多 Agent 冲突解决器"""

    def __init__(self, llm_client: AsyncOpenAI):
        self.client = llm_client

    async def resolve(self, conflicts: List[Dict]) -> Dict:
        """解决 Agent 间的冲突"""

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """你是冲突解决专家。分析多个 Agent 的分歧，给出公正的决策。

返回 JSON:
{
    "decision": "最终决策",
    "reasoning": "决策理由",
    "consensus_points": ["共识点"],
    "compromise_suggestions": ["妥协建议"]
}"""
                },
                {"role": "user", "content": f"冲突详情: {conflicts}"}
            ],
            response_format={"type": "json_object"}
        )

        import json
        return json.loads(response.choices[0].message.content)


class VotingMechanism:
    """投票机制"""

    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents

    async def vote(self, proposal: str, options: List[str]) -> Dict:
        """Agent 投票"""
        votes = {}

        for agent in self.agents:
            # 每个 Agent 选择一个选项
            vote = await self._get_agent_vote(agent, proposal, options)
            votes[agent.name] = vote

        # 统计投票结果
        result = self._count_votes(votes, options)

        return {
            "proposal": proposal,
            "votes": votes,
            "result": result
        }

    async def _get_agent_vote(self, agent: BaseAgent,
                              proposal: str, options: List[str]) -> str:
        """获取 Agent 的投票"""
        # 简化实现：随机选择
        import random
        return random.choice(options)

    def _count_votes(self, votes: Dict[str, str], options: List[str]) -> Dict:
        """统计投票"""
        counts = {opt: 0 for opt in options}
        for vote in votes.values():
            if vote in counts:
                counts[vote] += 1

        winner = max(counts, key=counts.get)
        return {
            "counts": counts,
            "winner": winner,
            "unanimous": len(set(votes.values())) == 1
        }
```

### 6.3 最佳实践总结

```
┌─────────────────────────────────────────────────────────────────┐
│                    多 Agent 系统最佳实践                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📐 架构设计                                                     │
│  ├─ 明确 Agent 职责边界，避免功能重叠                            │
│  ├─ 选择合适的协作模式（层级/扁平/流水线）                        │
│  ├─ 设计可扩展的通信机制                                         │
│  └─ 预留监控和调试接口                                           │
│                                                                 │
│  🔧 Skill 设计                                                   │
│  ├─ 保持 Skill 原子性，单一职责                                  │
│  ├─ 完善参数验证和错误处理                                       │
│  ├─ 提供清晰的元数据和文档                                       │
│  └─ 考虑权限控制和资源限制                                       │
│                                                                 │
│  💬 通信机制                                                     │
│  ├─ 使用异步消息传递，避免阻塞                                    │
│  ├─ 定义标准消息格式                                             │
│  ├─ 实现消息确认和重试机制                                       │
│  └─ 考虑消息优先级和过期策略                                      │
│                                                                 │
│  🛡️ 容错与可靠性                                                 │
│  ├─ 实现 Agent 健康检查                                          │
│  ├─ 设计任务超时和重试策略                                       │
│  ├─ 保存检查点支持任务恢复                                       │
│  └─ 日志记录便于问题排查                                         │
│                                                                 │
│  📊 性能优化                                                     │
│  ├─ 合理设置并发限制                                             │
│  ├─ 缓存频繁使用的结果                                           │
│  ├─ 批处理相似任务                                               │
│  └─ 监控 Token 使用和成本                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.4 调试与监控

```python
import logging
from functools import wraps
import time

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)

class AgentMonitor:
    """Agent 监控器"""

    def __init__(self):
        self.metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "total_messages": 0,
            "agent_stats": {}
        }
        self.logger = logging.getLogger("AgentMonitor")

    def track_task(self, agent_name: str, task_id: str, status: str,
                   duration: float = 0):
        """追踪任务"""
        self.metrics["total_tasks"] += 1

        if status == "completed":
            self.metrics["completed_tasks"] += 1
        elif status == "failed":
            self.metrics["failed_tasks"] += 1

        if agent_name not in self.metrics["agent_stats"]:
            self.metrics["agent_stats"][agent_name] = {
                "tasks": 0,
                "avg_duration": 0,
                "errors": 0
            }

        stats = self.metrics["agent_stats"][agent_name]
        stats["tasks"] += 1
        stats["avg_duration"] = (
            (stats["avg_duration"] * (stats["tasks"] - 1) + duration)
            / stats["tasks"]
        )

        self.logger.info(
            f"Task {task_id} | Agent: {agent_name} | Status: {status} | "
            f"Duration: {duration:.2f}s"
        )

    def track_message(self, sender: str, receiver: str, msg_type: str):
        """追踪消息"""
        self.metrics["total_messages"] += 1
        self.logger.debug(f"Message: {sender} -> {receiver} ({msg_type})")

    def get_report(self) -> Dict:
        """生成监控报告"""
        return {
            "summary": {
                "total_tasks": self.metrics["total_tasks"],
                "success_rate": (
                    self.metrics["completed_tasks"] / max(self.metrics["total_tasks"], 1)
                ),
                "total_messages": self.metrics["total_messages"]
            },
            "agent_stats": self.metrics["agent_stats"]
        }

    def print_report(self):
        """打印报告"""
        report = self.get_report()
        print("\n" + "=" * 50)
        print("📊 Agent 系统监控报告")
        print("=" * 50)
        print(f"总任务数: {report['summary']['total_tasks']}")
        print(f"成功率: {report['summary']['success_rate']:.1%}")
        print(f"消息总数: {report['summary']['total_messages']}")
        print("\n各 Agent 统计:")
        for name, stats in report["agent_stats"].items():
            print(f"  {name}: {stats['tasks']} 任务, "
                  f"平均耗时 {stats['avg_duration']:.2f}s")


def monitor_execution(monitor: AgentMonitor):
    """执行监控装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            task_id = str(uuid.uuid4())[:8]
            start_time = time.time()

            try:
                result = await func(self, *args, **kwargs)
                duration = time.time() - start_time
                monitor.track_task(self.name, task_id, "completed", duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.track_task(self.name, task_id, "failed", duration)
                raise

        return wrapper
    return decorator
```

---

## 总结

```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 7 学习总结                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ 核心概念                                                     │
│     • 多 Agent 系统的定义与优势                                  │
│     • Agent Skill 的设计与实现                                   │
│     • 常见协作架构模式                                           │
│                                                                 │
│  ✅ 关键技能                                                     │
│     • Skill 基类设计与注册中心                                   │
│     • 层级式/流水线/扁平式架构                                   │
│     • 消息总线与共享状态管理                                     │
│     • 黑板模式知识共享                                           │
│                                                                 │
│  ✅ 实战应用                                                     │
│     • 软件开发团队模拟                                           │
│     • 研究助手团队                                               │
│     • 动态 Agent 生成                                            │
│                                                                 │
│  ✅ 最佳实践                                                     │
│     • 架构设计原则                                               │
│     • 通信机制优化                                               │
│     • 容错与监控                                                 │
│                                                                 │
│  📚 延伸学习                                                     │
│     • AutoGen: 微软多 Agent 框架                                 │
│     • CrewAI: 多 Agent 协作平台                                  │
│     • LangGraph: Agent 工作流编排                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

> 📖 **下一步**: 学习具体框架（AutoGen、CrewAI）的使用，并尝试构建更复杂的多 Agent 应用场景。
