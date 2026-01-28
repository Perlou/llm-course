"""
人机协作 (Human-in-the-Loop)
============================

学习目标：
    1. 理解人机协作的重要性
    2. 实现审批和确认机制
    3. 设计人机交互接口

核心概念：
    - 人工审核点
    - 中断和恢复
    - 反馈循环

环境要求：
    - pip install openai python-dotenv
"""

import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

load_dotenv()


def hitl_overview():
    """人机协作概述"""
    print("=" * 60)
    print("第一部分：人机协作概述")
    print("=" * 60)

    print("""
    Human-in-the-Loop (HITL)
    ────────────────────────
    
    在关键节点引入人类判断，确保 AI 决策的安全性和准确性。
    
         ┌─────────┐      ┌─────────┐      ┌─────────┐
         │ Agent A │ ───► │ 人工审核 │ ───► │ Agent B │
         └─────────┘      │ 检查点  │      └─────────┘
                          └────┬────┘
                               │
                          ↙    ↓    ↘
                       批准   修改   拒绝
    
    何时需要人机协作？
    ─────────────────
    ✅ 高风险操作（删除数据、发送邮件）
    ✅ 需要专业判断的决策
    ✅ 涉及敏感信息的处理
    ✅ 不确定性较高的情况
    ✅ 法律或合规要求
    """)


def approval_workflow():
    """审批工作流"""
    print("\n" + "=" * 60)
    print("第二部分：审批工作流")
    print("=" * 60)

    class ApprovalStatus(Enum):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"
        MODIFIED = "modified"

    @dataclass
    class ApprovalRequest:
        id: str
        action: str
        details: Dict
        status: ApprovalStatus = ApprovalStatus.PENDING
        feedback: str = ""

    class HumanApprovalPoint:
        """人工审批点"""

        def __init__(self, name: str, description: str):
            self.name = name
            self.description = description
            self.pending_requests: List[ApprovalRequest] = []

        def request_approval(self, action: str, details: Dict) -> ApprovalRequest:
            """发起审批请求"""
            import uuid

            request = ApprovalRequest(
                id=str(uuid.uuid4())[:8], action=action, details=details
            )
            self.pending_requests.append(request)
            print(f"   📋 审批请求 [{request.id}]: {action}")
            return request

        def approve(self, request_id: str) -> bool:
            """批准"""
            for req in self.pending_requests:
                if req.id == request_id:
                    req.status = ApprovalStatus.APPROVED
                    print(f"   ✅ 已批准: {request_id}")
                    return True
            return False

        def reject(self, request_id: str, reason: str) -> bool:
            """拒绝"""
            for req in self.pending_requests:
                if req.id == request_id:
                    req.status = ApprovalStatus.REJECTED
                    req.feedback = reason
                    print(f"   ❌ 已拒绝: {request_id} ({reason})")
                    return True
            return False

    class HITLWorkflow:
        """人机协作工作流"""

        def __init__(self):
            self.approval_points: Dict[str, HumanApprovalPoint] = {}

        def add_approval_point(self, name: str, description: str):
            self.approval_points[name] = HumanApprovalPoint(name, description)

        def run_with_approval(self, steps: List[Dict]) -> Dict:
            """运行带审批的工作流"""
            results = []

            for step in steps:
                print(f"\n▶️ 步骤: {step['name']}")

                if step.get("requires_approval"):
                    point = self.approval_points.get(step["approval_point"])
                    if point:
                        req = point.request_approval(
                            step["name"], step.get("details", {})
                        )
                        # 模拟自动批准
                        point.approve(req.id)

                        if req.status != ApprovalStatus.APPROVED:
                            print(f"   ⏸️ 工作流暂停，等待审批")
                            break

                result = step.get("action", lambda: "OK")()
                results.append({"step": step["name"], "result": result})

            return {"completed": True, "results": results}

    # 演示
    print("\n🚀 审批工作流演示：")
    print("-" * 40)

    workflow = HITLWorkflow()
    workflow.add_approval_point("sensitive_action", "敏感操作审批")

    steps = [
        {"name": "数据分析", "action": lambda: "分析完成"},
        {"name": "生成报告", "action": lambda: "报告生成"},
        {
            "name": "发送邮件",
            "requires_approval": True,
            "approval_point": "sensitive_action",
            "details": {"recipients": ["user@example.com"]},
            "action": lambda: "邮件发送",
        },
    ]

    result = workflow.run_with_approval(steps)
    print(f"\n📦 结果: {result}")


def interrupt_resume():
    """中断和恢复"""
    print("\n" + "=" * 60)
    print("第三部分：中断和恢复机制")
    print("=" * 60)

    print("""
    中断恢复模式
    ───────────
    
    工作流可以在任意点暂停，保存状态，待人工处理后恢复。
    
         执行 → 保存状态 → 等待人工 → 恢复执行
                   │
                   └─► 持久化存储
    """)

    @dataclass
    class WorkflowState:
        """工作流状态"""

        current_step: int
        data: Dict
        is_paused: bool = False
        pause_reason: str = ""

    class ResumableWorkflow:
        """可恢复的工作流"""

        def __init__(self):
            self.state = WorkflowState(current_step=0, data={})
            self.steps = []

        def add_step(self, name: str, func, pause_before: bool = False):
            self.steps.append(
                {"name": name, "func": func, "pause_before": pause_before}
            )

        def run(self) -> Dict:
            while self.state.current_step < len(self.steps):
                step = self.steps[self.state.current_step]

                if step["pause_before"] and not self.state.is_paused:
                    self.state.is_paused = True
                    self.state.pause_reason = f"步骤 '{step['name']}' 需要确认"
                    print(f"   ⏸️ 暂停: {self.state.pause_reason}")
                    return {"paused": True, "state": self.state}

                print(f"   ▶️ 执行: {step['name']}")
                result = step["func"](self.state.data)
                self.state.data.update(result or {})
                self.state.current_step += 1
                self.state.is_paused = False

            return {"completed": True, "data": self.state.data}

        def resume(self):
            """恢复执行"""
            print("   ▶️ 恢复执行...")
            self.state.is_paused = False
            return self.run()

    # 演示
    print("\n🚀 中断恢复演示：")

    workflow = ResumableWorkflow()
    workflow.add_step("准备数据", lambda d: {"prepared": True})
    workflow.add_step("敏感操作", lambda d: {"executed": True}, pause_before=True)
    workflow.add_step("完成清理", lambda d: {"cleaned": True})

    result1 = workflow.run()
    print(f"   状态: {result1}")

    if result1.get("paused"):
        print("\n   [用户确认继续]")
        result2 = workflow.resume()
        print(f"   最终: {result2}")


def feedback_loop():
    """反馈循环"""
    print("\n" + "=" * 60)
    print("第四部分：人工反馈循环")
    print("=" * 60)

    class FeedbackWorkflow:
        """反馈循环工作流"""

        def __init__(self, max_iterations: int = 3):
            self.max_iterations = max_iterations

        def run(self, initial_content: str) -> str:
            content = initial_content

            for i in range(self.max_iterations):
                print(f"\n🔁 迭代 {i + 1}")
                print(f"   内容: {content[:30]}...")

                # 模拟人工反馈
                feedback = self._simulate_feedback(i)
                print(f"   反馈: {feedback}")

                if feedback == "approved":
                    print("   ✅ 内容已批准")
                    return content

                # 根据反馈修改
                content = self._improve(content, feedback)

            print("   ⚠️ 达到最大迭代次数")
            return content

        def _simulate_feedback(self, iteration: int) -> str:
            feedbacks = ["需要更详细", "语气需调整", "approved"]
            return feedbacks[min(iteration, len(feedbacks) - 1)]

        def _improve(self, content: str, feedback: str) -> str:
            return f"{content} [根据'{feedback}'改进]"

    print("\n🚀 反馈循环演示：")
    workflow = FeedbackWorkflow()
    final = workflow.run("初始内容草稿")
    print(f"\n📦 最终内容: {final[:50]}...")


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现多级审批 - 不同操作需要不同级别审批
    练习 2：状态持久化 - 将工作流状态保存到文件
    练习 3：超时机制 - 审批超时自动处理
    
    思考题：
    1. 如何在紧急情况下绕过审批？
    2. 如何记录和审计所有人工决策？
    """)


def main():
    print("🤝 人机协作 (Human-in-the-Loop)")
    print("=" * 60)
    hitl_overview()
    approval_workflow()
    interrupt_resume()
    feedback_loop()
    exercises()
    print("\n✅ 课程完成！下一步：09-agent-skills-intro.py")


if __name__ == "__main__":
    main()
