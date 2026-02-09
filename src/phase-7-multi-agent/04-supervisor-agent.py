"""
主管 Agent 模式 (Supervisor Pattern)
===================================

学习目标：
    1. 理解主管 Agent 模式的概念
    2. 掌握任务分解和分配策略
    3. 实现 Supervisor-Worker 架构
    4. 学会结果汇总和协调

核心概念：
    - Supervisor Agent：任务协调者
    - Worker Agent：任务执行者
    - 任务分解 (Task Decomposition)
    - 结果聚合 (Result Aggregation)

前置知识：
    - 01-03 课程内容
    - LangGraph 基础

环境要求：
    - pip install openai python-dotenv
"""

import os
import json
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import asyncio

load_dotenv()


# ==================== 第一部分：主管模式概述 ====================


def supervisor_pattern_overview():
    """主管模式概述"""
    print("=" * 60)
    print("第一部分：主管 Agent 模式概述")
    print("=" * 60)

    print("""
    主管 Agent 模式 (Supervisor Pattern)
    ─────────────────────────────────────
    
    一个 Supervisor Agent 负责：
    - 接收用户请求
    - 分解任务
    - 分配给 Worker Agents
    - 监督执行
    - 汇总结果
    
                    ┌─────────────────┐
                    │      User       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Supervisor    │
                    │   ┌─────────┐   │
                    │   │ 任务分解 │   │
                    │   │ 任务分配 │   │
                    │   │ 结果汇总 │   │
                    │   └─────────┘   │
                    └────────┬────────┘
                    ┌────────┼────────┐
                    ▼        ▼        ▼
               ┌────────┐ ┌────────┐ ┌────────┐
               │Worker A│ │Worker B│ │Worker C│
               │ 搜索   │ │ 分析   │ │ 写作   │
               └────────┘ └────────┘ └────────┘
    
    适用场景：
    ─────────
    ✅ 复杂任务可分解为独立子任务
    ✅ 不同子任务需要不同专业能力
    ✅ 需要统一协调和管理
    ✅ 需要质量控制和进度追踪
    """)


# ==================== 第二部分：Worker Agent 定义 ====================


def worker_agent_definition():
    """Worker Agent 定义"""
    print("\n" + "=" * 60)
    print("第二部分：Worker Agent 定义")
    print("=" * 60)

    class TaskStatus(Enum):
        """任务状态"""

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
        priority: int = 0

    class WorkerAgent:
        """工作者 Agent"""

        def __init__(self, name: str, specialty: str, skills: List[str]):
            self.name = name
            self.specialty = specialty
            self.skills = skills
            self.current_task: Optional[Task] = None

        def can_handle(self, task_type: str) -> bool:
            """检查是否能处理某类任务"""
            return task_type in self.skills

        def process(self, task: Task) -> Dict:
            """处理任务"""
            self.current_task = task
            task.status = TaskStatus.IN_PROGRESS

            print(f"      🔧 {self.name} 正在处理: {task.description[:30]}...")

            # 模拟任务处理（实际应用中调用 LLM）
            result = self._execute_task(task)

            task.status = TaskStatus.COMPLETED
            task.result = result
            self.current_task = None

            return result

        def _execute_task(self, task: Task) -> Dict:
            """执行任务（模拟）"""
            # 根据专业领域生成不同结果
            if self.specialty == "research":
                return {
                    "type": "research",
                    "findings": f"关于「{task.description}」的研究发现...",
                    "sources": ["source1", "source2"],
                }
            elif self.specialty == "analysis":
                return {
                    "type": "analysis",
                    "insights": f"关于「{task.description}」的分析...",
                    "metrics": {"score": 85},
                }
            elif self.specialty == "writing":
                return {
                    "type": "writing",
                    "content": f"关于「{task.description}」的内容...",
                    "word_count": 500,
                }
            else:
                return {"type": "general", "output": f"处理完成: {task.description}"}

    # 创建示例 Worker
    print("\n📌 定义 Worker Agents：")

    workers = [
        WorkerAgent("Researcher", "research", ["search", "collect", "verify"]),
        WorkerAgent("Analyst", "analysis", ["analyze", "compare", "evaluate"]),
        WorkerAgent("Writer", "writing", ["write", "edit", "format"]),
    ]

    for w in workers:
        print(f"   👷 {w.name}")
        print(f"      专长: {w.specialty}")
        print(f"      技能: {w.skills}")
        print()

    return WorkerAgent, Task, TaskStatus


# ==================== 第三部分：Supervisor Agent 实现 ====================


def supervisor_agent_implementation():
    """Supervisor Agent 实现"""
    print("\n" + "=" * 60)
    print("第三部分：Supervisor Agent 实现")
    print("=" * 60)

    class TaskStatus(Enum):
        PENDING = "pending"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        FAILED = "failed"

    @dataclass
    class Task:
        id: str
        description: str
        task_type: str = ""
        assigned_to: Optional[str] = None
        status: TaskStatus = TaskStatus.PENDING
        result: Any = None
        priority: int = 0

    class WorkerAgent:
        def __init__(self, name: str, specialty: str, skills: List[str]):
            self.name = name
            self.specialty = specialty
            self.skills = skills

        def can_handle(self, task_type: str) -> bool:
            return task_type in self.skills

        def process(self, task: Task) -> Dict:
            task.status = TaskStatus.IN_PROGRESS
            print(f"         🔧 {self.name} 处理: {task.description[:25]}...")

            # 模拟处理
            result = {
                "worker": self.name,
                "task_id": task.id,
                "output": f"[{self.specialty}] 完成: {task.description}",
            }

            task.status = TaskStatus.COMPLETED
            task.result = result
            return result

    class SupervisorAgent:
        """主管 Agent"""

        def __init__(self, name: str, workers: List[WorkerAgent]):
            self.name = name
            self.workers = {w.name: w for w in workers}
            self.task_queue: List[Task] = []
            self.completed_tasks: List[Task] = []

        def receive_request(self, request: str) -> Dict:
            """接收并处理用户请求"""
            print(f"\n📋 {self.name} 收到请求: {request}")
            print("-" * 40)

            # 1. 分解任务
            subtasks = self._decompose_task(request)
            print(f"\n🔍 任务分解为 {len(subtasks)} 个子任务:")
            for task in subtasks:
                print(f"   - [{task.task_type}] {task.description}")

            # 2. 分配任务
            assignments = self._assign_tasks(subtasks)
            print(f"\n📝 任务分配:")
            for worker_name, tasks in assignments.items():
                if tasks:
                    print(f"   {worker_name}: {len(tasks)} 个任务")

            # 3. 执行任务
            print(f"\n⚡ 执行任务:")
            results = self._execute_all(assignments)

            # 4. 汇总结果
            print(f"\n📊 汇总结果:")
            summary = self._aggregate_results(results)

            return summary

        def _decompose_task(self, request: str) -> List[Task]:
            """任务分解（模拟 LLM 分解）"""
            # 实际应用中使用 LLM 进行智能分解
            subtasks = [
                Task(
                    id="1",
                    description=f"搜索关于「{request}」的资料",
                    task_type="search",
                    priority=1,
                ),
                Task(
                    id="2",
                    description=f"分析「{request}」的关键要点",
                    task_type="analyze",
                    priority=2,
                ),
                Task(
                    id="3",
                    description=f"撰写「{request}」的总结报告",
                    task_type="write",
                    priority=3,
                ),
            ]
            return subtasks

        def _assign_tasks(self, tasks: List[Task]) -> Dict[str, List[Task]]:
            """任务分配"""
            assignments = {name: [] for name in self.workers}

            for task in tasks:
                # 找到最适合的 Worker
                assigned = False
                for name, worker in self.workers.items():
                    if worker.can_handle(task.task_type):
                        task.assigned_to = name
                        assignments[name].append(task)
                        assigned = True
                        break

                if not assigned:
                    # 分配给第一个 Worker 作为默认
                    first_worker = list(self.workers.keys())[0]
                    task.assigned_to = first_worker
                    assignments[first_worker].append(task)

            return assignments

        def _execute_all(self, assignments: Dict[str, List[Task]]) -> List[Dict]:
            """执行所有任务"""
            results = []

            for worker_name, tasks in assignments.items():
                worker = self.workers[worker_name]
                for task in tasks:
                    result = worker.process(task)
                    results.append(result)
                    self.completed_tasks.append(task)

            return results

        def _aggregate_results(self, results: List[Dict]) -> Dict:
            """汇总结果"""
            summary = {
                "total_tasks": len(results),
                "workers_used": list(set(r["worker"] for r in results)),
                "outputs": [r["output"] for r in results],
                "status": "completed",
            }

            print(f"   任务总数: {summary['total_tasks']}")
            print(f"   参与 Worker: {summary['workers_used']}")
            print(f"   状态: ✅ {summary['status']}")

            return summary

    # 演示
    print("\n🚀 主管模式演示：")
    print("=" * 50)

    # 创建 Workers
    workers = [
        WorkerAgent("Researcher", "research", ["search", "collect"]),
        WorkerAgent("Analyst", "analysis", ["analyze", "compare"]),
        WorkerAgent("Writer", "writing", ["write", "edit"]),
    ]

    # 创建 Supervisor
    supervisor = SupervisorAgent("Manager", workers)

    # 处理请求
    result = supervisor.receive_request("人工智能发展趋势分析报告")

    print("\n" + "=" * 50)
    print("📦 最终结果:")
    for output in result["outputs"]:
        print(f"   • {output[:50]}...")


# ==================== 第四部分：使用 LLM 的智能 Supervisor ====================


def llm_supervisor():
    """使用 LLM 的智能 Supervisor"""
    print("\n" + "=" * 60)
    print("第四部分：使用 LLM 的智能 Supervisor")
    print("=" * 60)

    print("""
    智能任务分解与分配
    ─────────────────
    
    使用 LLM 来智能地：
    1. 理解用户请求
    2. 分解任务
    3. 选择最佳 Worker
    4. 生成最终报告
    """)

    print("\n📌 LLM Supervisor 代码示例：")

    code_example = '''
    from openai import OpenAI

    class LLMSupervisorAgent:
        """使用 LLM 的主管 Agent"""

        def __init__(self, client: OpenAI, workers: List[WorkerAgent]):
            self.client = client
            self.workers = {w.name: w for w in workers}

        async def decompose_task(self, request: str) -> List[Dict]:
            """使用 LLM 分解任务"""
            worker_info = "\\n".join([
                f"- {w.name}: 专长={w.specialty}, 技能={w.skills}"
                for w in self.workers.values()
            ])

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""你是任务分解专家。
将用户请求分解为子任务，并分配给合适的 Worker。

可用 Workers:
{worker_info}

返回 JSON:
{{
    "subtasks": [
        {{"id": "1", "description": "任务描述", "worker": "Worker名", "priority": 1}}
    ]
}}"""
                    },
                    {"role": "user", "content": request}
                ],
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)["subtasks"]

        async def aggregate_results(self, request: str, results: List[Dict]) -> str:
            """使用 LLM 汇总结果"""
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "你是报告生成专家。根据各 Worker 的输出，生成完整报告。"
                    },
                    {
                        "role": "user",
                        "content": f"原始请求: {request}\\n\\n各 Worker 结果:\\n{results}"
                    }
                ]
            )

            return response.choices[0].message.content
    '''

    print(code_example)


# ==================== 第五部分：LangGraph 实现 ====================


def langgraph_supervisor():
    """使用 LangGraph 实现 Supervisor"""
    print("\n" + "=" * 60)
    print("第五部分：使用 LangGraph 实现 Supervisor")
    print("=" * 60)

    print("""
    LangGraph Supervisor 架构
    ─────────────────────────
    
                  ┌────────────┐
                  │   START    │
                  └─────┬──────┘
                        │
                        ▼
                  ┌────────────┐
                  │ Supervisor │ ◄─────────┐
                  └─────┬──────┘           │
                        │                  │
              ┌─────────┼─────────┐        │
              ▼         ▼         ▼        │
         ┌────────┐ ┌────────┐ ┌────────┐  │
         │Worker A│ │Worker B│ │Worker C│  │
         └────┬───┘ └────┬───┘ └────┬───┘  │
              │         │         │        │
              └─────────┼─────────┘        │
                        │                  │
                        ▼                  │
                  ┌────────────┐           │
                  │ 需要更多? ├────是──────┘
                  └─────┬──────┘
                        │否
                        ▼
                  ┌────────────┐
                  │    END     │
                  └────────────┘
    """)

    print("\n📌 LangGraph Supervisor 代码：")

    code_example = '''
    from typing import TypedDict, Annotated, Literal
    from langgraph.graph import StateGraph, END
    import operator

    # 定义状态
    class SupervisorState(TypedDict):
        messages: Annotated[list, operator.add]
        next_worker: str
        task_completed: bool
        results: list

    # Worker 节点
    def researcher_node(state: SupervisorState) -> dict:
        return {
            "messages": ["[Researcher] 完成研究..."],
            "results": [{"worker": "researcher", "output": "研究结果"}]
        }

    def analyst_node(state: SupervisorState) -> dict:
        return {
            "messages": ["[Analyst] 完成分析..."],
            "results": [{"worker": "analyst", "output": "分析结果"}]
        }

    def writer_node(state: SupervisorState) -> dict:
        return {
            "messages": ["[Writer] 完成写作..."],
            "results": [{"worker": "writer", "output": "写作结果"}]
        }

    # Supervisor 节点
    def supervisor_node(state: SupervisorState) -> dict:
        """决定下一步"""
        results = state.get("results", [])

        if len(results) == 0:
            return {"next_worker": "researcher", "task_completed": False}
        elif len(results) == 1:
            return {"next_worker": "analyst", "task_completed": False}
        elif len(results) == 2:
            return {"next_worker": "writer", "task_completed": False}
        else:
            return {"next_worker": "end", "task_completed": True}

    # 路由函数
    def route_to_worker(state: SupervisorState) -> Literal["researcher", "analyst", "writer", "end"]:
        return state["next_worker"]

    # 构建 Graph
    workflow = StateGraph(SupervisorState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("writer", writer_node)

    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_to_worker,
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "writer": "writer",
            "end": END
        }
    )

    # Worker 完成后返回 Supervisor
    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("analyst", "supervisor")
    workflow.add_edge("writer", "supervisor")

    app = workflow.compile()
    '''

    print(code_example)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：添加新 Worker
        为 Supervisor 系统添加一个 "Reviewer" Worker，
        负责在写作完成后审核内容。

        ✅ 参考答案：
        ```python
        class ReviewerWorker(BaseWorker):
            name = "reviewer"
            description = "审核和校对内容，检查质量和准确性"
            
            def execute(self, task: str, context: dict) -> str:
                content = context.get("writer_output", "")
                prompt = f'''
                作为审核员，请检查以下内容：
                1. 准确性和事实核查
                2. 语法和拼写错误
                3. 内容完整性
                
                内容：{content}
                
                审核报告：
                '''
                return self.llm.invoke(prompt).content

        # 添加到 Supervisor
        supervisor.register_worker(ReviewerWorker(llm))
        ```
    
    练习 2：实现优先级调度
        修改 Supervisor，使其能够：
        - 按优先级处理任务
        - 处理任务依赖关系

        ✅ 参考答案：
        ```python
        from dataclasses import dataclass
        import heapq

        @dataclass
        class Task:
            priority: int
            name: str
            dependencies: list = None
            
            def __lt__(self, other):
                return self.priority < other.priority

        class PrioritySupervisor:
            def __init__(self):
                self.task_queue = []
                self.completed = set()
            
            def add_task(self, task: Task):
                heapq.heappush(self.task_queue, task)
            
            def get_next_ready_task(self):
                temp = []
                result = None
                
                while self.task_queue:
                    task = heapq.heappop(self.task_queue)
                    deps = task.dependencies or []
                    
                    if all(d in self.completed for d in deps):
                        result = task
                        break
                    temp.append(task)
                
                for t in temp:
                    heapq.heappush(self.task_queue, t)
                
                return result
        ```
    
    练习 3：添加错误处理
        实现 Worker 失败时的处理：
        - 重试机制
        - 备选 Worker
        - 错误报告

        ✅ 参考答案：
        ```python
        class ResilientSupervisor:
            def __init__(self, max_retries: int = 3):
                self.max_retries = max_retries
                self.error_log = []
            
            def execute_with_retry(self, worker, task, context):
                for attempt in range(self.max_retries):
                    try:
                        return worker.execute(task, context)
                    except Exception as e:
                        self.error_log.append({
                            "worker": worker.name,
                            "attempt": attempt + 1,
                            "error": str(e)
                        })
                        if attempt == self.max_retries - 1:
                            # 尝试备选 Worker
                            backup = self.get_backup_worker(worker.name)
                            if backup:
                                return backup.execute(task, context)
                            raise
        ```
    
    练习 4：并行执行
        修改系统支持多个 Worker 并行处理独立任务。

        ✅ 参考答案：
        ```python
        import asyncio

        class ParallelSupervisor:
            def __init__(self):
                self.workers = {}
            
            async def execute_parallel(self, tasks: list):
                # 找出可以并行的独立任务
                independent = [t for t in tasks if not t.dependencies]
                
                async def run_task(task):
                    worker = self.select_worker(task)
                    return await asyncio.to_thread(worker.execute, task.content, {})
                
                results = await asyncio.gather(*[run_task(t) for t in independent])
                return dict(zip([t.name for t in independent], results))
        ```
    
    思考题：
    ────────
    1. Supervisor 如何决定任务分解的粒度？
       答：根据任务复杂度、Worker 能力、时间限制等因素，
       使用 LLM 智能判断或预设规则。

    2. 如何处理 Worker 负载不均？
       答：实现负载均衡算法：轮询、最少连接、
       基于能力的加权分配等。

    3. Supervisor 失败怎么办？
       答：实现 Supervisor 高可用：主备切换、
       状态持久化、检查点恢复。
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("👔 主管 Agent 模式")
    print("=" * 60)

    supervisor_pattern_overview()
    worker_agent_definition()
    supervisor_agent_implementation()
    llm_supervisor()
    langgraph_supervisor()
    exercises()

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：05-hierarchical-agents.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
