"""
层级 Agent 架构 (Hierarchical Agents)
====================================

学习目标：
    1. 理解层级 Agent 架构
    2. 掌握多层级组织设计
    3. 实现团队嵌套结构

核心概念：
    - 层级组织结构
    - Manager-Team 模式
    - 跨层级通信

环境要求：
    - pip install openai python-dotenv
"""

import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid

load_dotenv()


# ==================== 第一部分：层级架构概述 ====================


def hierarchical_overview():
    """层级架构概述"""
    print("=" * 60)
    print("第一部分：层级 Agent 架构概述")
    print("=" * 60)

    print("""
    层级 Agent 架构
    ───────────────
    
                        ┌──────────────┐
            Level 0     │   Director   │  战略决策
                        └──────┬───────┘
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
    Level 1   │ Manager A│ │ Manager B│ │ Manager C│
              └────┬─────┘ └────┬─────┘ └────┬─────┘
              ┌────┼────┐     ┌─┴──┐     ┌───┼───┐
              ▼    ▼    ▼     ▼    ▼     ▼   ▼   ▼
            ┌───┐┌───┐┌───┐ ┌───┐┌───┐ ┌───┐┌───┐┌───┐
    Level 2 │W1 ││W2 ││W3 │ │W4 ││W5 │ │W6 ││W7 ││W8 │
            └───┘└───┘└───┘ └───┘└───┘ └───┘└───┘└───┘
    
    ┌────────────────┬─────────────────┬─────────────────┐
    │      特点      │     层级架构     │     扁平架构    │
    ├────────────────┼─────────────────┼─────────────────┤
    │  决策路径      │  较长           │   较短          │
    │  专业化程度    │  高             │   中            │
    │  可扩展性      │  好             │   有限          │
    └────────────────┴─────────────────┴─────────────────┘
    """)


# ==================== 第二部分：层级结构定义 ====================


def hierarchical_structure():
    """层级结构定义"""
    print("\n" + "=" * 60)
    print("第二部分：层级结构定义")
    print("=" * 60)

    class AgentLevel(Enum):
        DIRECTOR = 0
        MANAGER = 1
        WORKER = 2

    @dataclass
    class HierarchicalAgent:
        id: str
        name: str
        level: AgentLevel
        specialty: str
        parent: Optional["HierarchicalAgent"] = None
        children: List["HierarchicalAgent"] = field(default_factory=list)

        def add_child(self, child: "HierarchicalAgent"):
            child.parent = self
            self.children.append(child)

    print("\n📌 层级结构定义代码示例已展示")

    # 创建示例
    director = HierarchicalAgent("d1", "CEO", AgentLevel.DIRECTOR, "战略")
    mgr1 = HierarchicalAgent("m1", "Dev Mgr", AgentLevel.MANAGER, "研发")
    mgr2 = HierarchicalAgent("m2", "Prod Mgr", AgentLevel.MANAGER, "产品")
    director.add_child(mgr1)
    director.add_child(mgr2)

    def print_tree(agent, indent=0):
        print(
            "  " * indent
            + f"{'👔' if agent.level == AgentLevel.DIRECTOR else '👨‍💼' if agent.level == AgentLevel.MANAGER else '👷'} {agent.name}"
        )
        for c in agent.children:
            print_tree(c, indent + 1)

    print("\n🏢 组织架构：")
    print_tree(director)


# ==================== 第三部分：层级通信 ====================


def hierarchical_communication():
    """层级通信"""
    print("\n" + "=" * 60)
    print("第三部分：层级通信")
    print("=" * 60)

    print("""
    通信模式
    ────────
    1. 自顶向下 (Top-Down): Director → Manager → Worker
    2. 自底向上 (Bottom-Up): Worker → Manager → Director
    3. 水平通信 (Lateral): 同级 Agent 之间
    """)

    class CommunicatingAgent:
        def __init__(self, name: str, level: int):
            self.name = name
            self.level = level
            self.parent = None
            self.children = []

        def add_child(self, child):
            child.parent = self
            self.children.append(child)

        def send_down(self, content: str):
            for c in self.children:
                print(f"   ⬇️ {self.name} → {c.name}: {content[:30]}...")

        def send_up(self, content: str):
            if self.parent:
                print(f"   ⬆️ {self.name} → {self.parent.name}: {content[:30]}...")

    print("\n🚀 通信演示：")
    director = CommunicatingAgent("Director", 0)
    mgr = CommunicatingAgent("Manager", 1)
    worker = CommunicatingAgent("Worker", 2)
    director.add_child(mgr)
    mgr.add_child(worker)

    director.send_down("启动项目")
    mgr.send_down("开始开发")
    worker.send_up("开发完成")
    mgr.send_up("阶段报告")


# ==================== 第四部分：跨层级任务流 ====================


def cross_level_workflow():
    """跨层级任务流"""
    print("\n" + "=" * 60)
    print("第四部分：跨层级任务流")
    print("=" * 60)

    print("""
    任务流转: User → Director → Managers → Workers → 汇总 → User
    """)

    class HierarchicalWorkflow:
        def __init__(self):
            self.levels = {0: [], 1: [], 2: []}

        def execute(self, request: str) -> Dict:
            print(f"\n📥 收到请求: {request}")
            goals = [f"研究: {request}", f"开发: {request}"]
            print(f"🔷 Director 分解: {goals}")

            tasks = [f"任务1: {g[:15]}" for g in goals]
            print(f"🔶 Managers 分配: {tasks}")

            results = [f"完成 - {t}" for t in tasks]
            print(f"🔸 Workers 执行: {results}")

            return {"summary": f"完成 {len(results)} 个任务"}

    workflow = HierarchicalWorkflow()
    workflow.execute("构建智能客服")


# ==================== 第五部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现动态层级 - 动态添加/删除层级

        ✅ 参考答案：
        ```python
        class DynamicHierarchy:
            def __init__(self):
                self.nodes = {}  # id -> node
                self.children = {}  # parent_id -> [child_ids]
            
            def add_node(self, node_id: str, parent_id: str = None):
                self.nodes[node_id] = {"id": node_id, "parent": parent_id}
                if parent_id:
                    self.children.setdefault(parent_id, []).append(node_id)
            
            def remove_node(self, node_id: str):
                # 将子节点提升到父节点
                parent_id = self.nodes[node_id].get("parent")
                children = self.children.get(node_id, [])
                
                for child_id in children:
                    self.nodes[child_id]["parent"] = parent_id
                    if parent_id:
                        self.children[parent_id].append(child_id)
                
                # 删除节点
                del self.nodes[node_id]
                if node_id in self.children:
                    del self.children[node_id]
        ```

    练习 2：跨部门协作 - 不同 Manager 下 Worker 协作

        ✅ 参考答案：
        ```python
        class CrossDepartmentCoordinator:
            def __init__(self, departments: dict):
                self.departments = departments  # dept_name -> manager
            
            def collaborate(self, task: str, dept_names: list):
                '''跨部门协作执行任务'''
                results = {}
                shared_context = {"task": task}
                
                for dept in dept_names:
                    manager = self.departments[dept]
                    result = manager.process(task, shared_context)
                    results[dept] = result
                    shared_context[f"{dept}_result"] = result
                
                # 整合各部门结果
                return self.synthesize(results)
        ```

    练习 3：层级权限控制 - 不同层级不同权限

        ✅ 参考答案：
        ```python
        from enum import IntEnum

        class Permission(IntEnum):
            READ = 1
            WRITE = 2
            EXECUTE = 4
            ADMIN = 8

        class PermissionedHierarchy:
            def __init__(self):
                self.permissions = {}  # level -> permissions
            
            def set_level_permission(self, level: int, perm: Permission):
                self.permissions[level] = perm
            
            def can_execute(self, agent_level: int, required_perm: Permission):
                agent_perms = self.permissions.get(agent_level, Permission.READ)
                return agent_perms >= required_perm
            
            def execute_with_permission(self, agent, action, required_perm):
                if not self.can_execute(agent.level, required_perm):
                    raise PermissionError(f"Level {agent.level} 无权执行此操作")
                return action()
        ```
    
    思考题：
    1. 层级最佳深度？答：2-4 层

       ✅ 详细：层级过深导致通信延迟，过浅无法有效分工。
       根据组织规模和任务复杂度选择。

    2. 紧急跨层通信？答：设置紧急通道

       ✅ 详细：实现 bypass 机制，允许紧急消息直达顶层，
       同时通知中间层级。
    """)


def main():
    print("🏛️ 层级 Agent 架构")
    print("=" * 60)
    hierarchical_overview()
    hierarchical_structure()
    hierarchical_communication()
    cross_level_workflow()
    exercises()
    print("\n✅ 课程完成！下一步：06-debate-agents.py")


if __name__ == "__main__":
    main()
