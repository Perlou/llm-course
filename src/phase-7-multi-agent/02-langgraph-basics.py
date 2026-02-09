"""
LangGraph 基础
==============

学习目标：
    1. 理解 LangGraph 的核心概念
    2. 掌握 StateGraph 和状态管理
    3. 学会创建简单的 Graph 工作流
    4. 理解节点和边的概念

核心概念：
    - StateGraph：状态图，管理工作流状态
    - Node：节点，执行具体操作
    - Edge：边，定义节点间的转换关系
    - Conditional Edge：条件边，基于状态的动态路由

前置知识：
    - Phase 6: Agent 基础
    - 01-multi-agent-intro.py

环境要求：
    - pip install langgraph langchain-openai python-dotenv
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List, Literal
import operator

load_dotenv()


# ==================== 第一部分：LangGraph 简介 ====================


def langgraph_introduction():
    """LangGraph 简介"""
    print("=" * 60)
    print("第一部分：LangGraph 简介")
    print("=" * 60)

    print("""
    LangGraph 是什么？
    ─────────────────
    
    LangGraph 是 LangChain 团队开发的图工作流框架，
    专门用于构建复杂的多 Agent 应用和工作流。
    
    ┌─────────────────────────────────────────────────────┐
    │                   LangGraph 核心概念                 │
    │                                                     │
    │   ┌─────────────────────────────────────────────┐   │
    │   │                 StateGraph                   │   │
    │   │                                             │   │
    │   │    ┌───────┐         ┌───────┐             │   │
    │   │    │ Node A│────────►│ Node B│             │   │
    │   │    └───────┘         └───┬───┘             │   │
    │   │                          │                 │   │
    │   │                    ┌─────┴─────┐           │   │
    │   │                    ▼           ▼           │   │
    │   │              ┌───────┐   ┌───────┐         │   │
    │   │              │ Node C│   │ Node D│         │   │
    │   │              └───────┘   └───────┘         │   │
    │   │                                             │   │
    │   └─────────────────────────────────────────────┘   │
    │                                                     │
    │   State: 在节点间流动的数据状态                      │
    │   Node: 执行操作的单元（可以是 Agent）               │
    │   Edge: 连接节点的边（可以是条件）                   │
    └─────────────────────────────────────────────────────┘
    
    为什么使用 LangGraph？
    ────────────────────
    ✅ 声明式定义工作流结构
    ✅ 内置状态管理和持久化
    ✅ 支持条件分支和循环
    ✅ 容易调试和可视化
    ✅ 与 LangChain 生态系统集成
    """)


# ==================== 第二部分：State 状态定义 ====================


def state_definition():
    """状态定义"""
    print("\n" + "=" * 60)
    print("第二部分：State 状态定义")
    print("=" * 60)

    print("""
    State 是 LangGraph 的核心
    ─────────────────────────
    
    State 定义了在 Graph 中流动的数据结构。
    每个节点可以读取和修改 State。
    
    State 定义方式：
    ───────────────
    1. TypedDict：简单的类型定义
    2. Annotated：带有 reducer 的复杂状态
    """)

    # 示例 1：简单状态
    print("\n📌 示例 1：简单状态定义")

    class SimpleState(TypedDict):
        """简单状态定义"""

        input: str  # 输入内容
        output: str  # 输出内容
        current_step: str  # 当前步骤

    print("""
    class SimpleState(TypedDict):
        input: str           # 输入内容
        output: str          # 输出内容
        current_step: str    # 当前步骤
    """)

    # 示例 2：带 Reducer 的状态
    print("\n📌 示例 2：带 Reducer 的状态（累积消息）")

    class MessagesState(TypedDict):
        """带消息累积的状态"""

        messages: Annotated[List[str], operator.add]  # 消息会累积
        current_agent: str

    print("""
    class MessagesState(TypedDict):
        # 使用 Annotated + operator.add，消息会自动累积
        messages: Annotated[List[str], operator.add]
        current_agent: str
    
    # Reducer 的作用：
    # - operator.add: 列表追加
    # - 自定义函数: 更复杂的合并逻辑
    """)

    # 演示 Reducer 效果
    print("\n📌 演示 Reducer 效果：")
    print("""
    # 假设初始状态
    state = {"messages": ["Hello"], "current_agent": "A"}
    
    # 节点返回新消息
    return {"messages": ["World"]}
    
    # 结果状态（messages 被追加，而不是替换）
    state = {"messages": ["Hello", "World"], "current_agent": "A"}
    """)


# ==================== 第三部分：创建简单 Graph ====================


def simple_graph_demo():
    """创建简单 Graph"""
    print("\n" + "=" * 60)
    print("第三部分：创建简单 Graph")
    print("=" * 60)

    print("""
    Graph 创建步骤
    ─────────────
    1. 定义 State
    2. 创建 StateGraph
    3. 添加节点（add_node）
    4. 添加边（add_edge）
    5. 设置入口点（set_entry_point）
    6. 设置结束点（set_finish_point）
    7. 编译 Graph（compile）
    """)

    print("\n📌 代码演示：问候 Graph")

    # 由于可能没有安装 langgraph，我们模拟实现
    class MockStateGraph:
        """模拟 StateGraph 用于演示"""

        def __init__(self, state_class):
            self.state_class = state_class
            self.nodes = {}
            self.edges = {}
            self.entry_point = None
            self.finish_point = None

        def add_node(self, name: str, func):
            self.nodes[name] = func
            print(f"   ✅ 添加节点: {name}")

        def add_edge(self, from_node: str, to_node: str):
            self.edges[from_node] = to_node
            print(f"   ✅ 添加边: {from_node} → {to_node}")

        def set_entry_point(self, name: str):
            self.entry_point = name
            print(f"   ✅ 设置入口: {name}")

        def set_finish_point(self, name: str):
            self.finish_point = name
            print(f"   ✅ 设置结束: {name}")

        def compile(self):
            print("   ✅ 编译完成!")
            return CompiledGraph(self)

    class CompiledGraph:
        """编译后的 Graph"""

        def __init__(self, graph):
            self.graph = graph

        def invoke(self, initial_state: dict) -> dict:
            """执行 Graph"""
            state = initial_state.copy()
            current = self.graph.entry_point

            while current and current != self.graph.finish_point:
                if current in self.graph.nodes:
                    result = self.graph.nodes[current](state)
                    state.update(result)
                current = self.graph.edges.get(current)

            # 执行最后一个节点
            if current and current in self.graph.nodes:
                result = self.graph.nodes[current](state)
                state.update(result)

            return state

    # 定义状态
    class GreetingState(TypedDict):
        name: str
        greeting: str
        farewell: str

    # 定义节点函数
    def greet_node(state: GreetingState) -> dict:
        """问候节点"""
        name = state.get("name", "朋友")
        return {"greeting": f"你好, {name}! 欢迎来到 LangGraph 的世界!"}

    def farewell_node(state: GreetingState) -> dict:
        """告别节点"""
        name = state.get("name", "朋友")
        return {"farewell": f"再见, {name}! 祝你学习愉快!"}

    # 创建并演示 Graph
    print("\n🔧 创建 Graph:")
    print("-" * 40)

    graph = MockStateGraph(GreetingState)
    graph.add_node("greet", greet_node)
    graph.add_node("farewell", farewell_node)
    graph.add_edge("greet", "farewell")
    graph.set_entry_point("greet")
    graph.set_finish_point("farewell")

    compiled = graph.compile()

    print("\n🚀 执行 Graph:")
    print("-" * 40)

    result = compiled.invoke({"name": "小明", "greeting": "", "farewell": ""})
    print(f"   输入: name = '小明'")
    print(f"   问候: {result['greeting']}")
    print(f"   告别: {result['farewell']}")


# ==================== 第四部分：条件边 ====================


def conditional_edges():
    """条件边"""
    print("\n" + "=" * 60)
    print("第四部分：条件边 (Conditional Edges)")
    print("=" * 60)

    print("""
    条件边允许基于状态动态决定下一个节点
    ─────────────────────────────────────
    
                ┌───────┐
                │ Start │
                └───┬───┘
                    │
              ┌─────┴─────┐
              ▼           ▼
         ┌───────┐   ┌───────┐
         │Task A │   │Task B │
         └───┬───┘   └───┬───┘
             │           │
             └─────┬─────┘
                   ▼
              ┌───────┐
              │  End  │
              └───────┘
    
    使用方法：add_conditional_edges(
        source_node,        # 源节点
        router_function,    # 路由函数
        path_map            # 路径映射
    )
    """)

    print("\n📌 代码示例：基于任务类型的路由")

    # 模拟条件边
    class TaskState(TypedDict):
        task_type: str
        input: str
        result: str

    def router(state: TaskState) -> str:
        """路由函数：决定下一个节点"""
        task_type = state.get("task_type", "")
        if task_type == "translate":
            return "translator"
        elif task_type == "summarize":
            return "summarizer"
        else:
            return "default_handler"

    def translate_node(state: TaskState) -> dict:
        return {"result": f"[翻译结果] {state['input']}"}

    def summarize_node(state: TaskState) -> dict:
        return {"result": f"[摘要结果] {state['input'][:20]}..."}

    def default_node(state: TaskState) -> dict:
        return {"result": f"[默认处理] {state['input']}"}

    print("""
    def router(state: TaskState) -> str:
        \"\"\"路由函数：返回下一个节点名称\"\"\"
        task_type = state.get("task_type", "")
        if task_type == "translate":
            return "translator"
        elif task_type == "summarize":
            return "summarizer"
        else:
            return "default_handler"

    # 在 Graph 中使用
    graph.add_conditional_edges(
        "input_node",     # 从哪个节点出发
        router,           # 路由函数
        {                 # 路径映射
            "translator": "translator",
            "summarizer": "summarizer",
            "default_handler": "default_handler"
        }
    )
    """)

    # 演示
    print("\n🚀 条件路由演示:")
    print("-" * 40)

    test_cases = [
        {"task_type": "translate", "input": "Hello World"},
        {"task_type": "summarize", "input": "这是一段很长的文本需要总结..."},
        {"task_type": "unknown", "input": "一些内容"},
    ]

    for case in test_cases:
        next_node = router(case)
        if next_node == "translator":
            result = translate_node(case)
        elif next_node == "summarizer":
            result = summarize_node(case)
        else:
            result = default_node(case)

        print(f"   任务类型: {case['task_type']}")
        print(f"   路由到: {next_node}")
        print(f"   结果: {result['result']}")
        print()


# ==================== 第五部分：循环与迭代 ====================


def loops_and_iteration():
    """循环与迭代"""
    print("\n" + "=" * 60)
    print("第五部分：循环与迭代")
    print("=" * 60)

    print("""
    LangGraph 支持循环结构
    ─────────────────────
    
    这对于 Agent 的"思考-行动-观察"循环非常重要。
    
              ┌───────────────────────────────┐
              │                               │
              ▼                               │
         ┌───────┐                            │
         │ Think │  思考                       │
         └───┬───┘                            │
             │                                │
             ▼                                │
         ┌───────┐     ┌───────┐             │
         │ Act   │────►│Observe│─────────────┘
         └───────┘     └───┬───┘      继续循环
           执行             │
                           │ 完成
                           ▼
                      ┌───────┐
                      │  End  │
                      └───────┘
    
    关键点：
    ─────
    1. 使用条件边控制是否继续循环
    2. 设置最大迭代次数防止无限循环
    3. 在状态中跟踪迭代计数
    """)

    print("\n📌 代码示例：迭代改进循环")

    class IterationState(TypedDict):
        content: str
        quality_score: int
        iteration_count: int
        max_iterations: int

    def improve_content(state: IterationState) -> dict:
        """改进内容"""
        content = state["content"]
        improved = f"{content} [改进 #{state['iteration_count'] + 1}]"
        return {"content": improved, "iteration_count": state["iteration_count"] + 1}

    def evaluate_quality(state: IterationState) -> dict:
        """评估质量"""
        # 模拟评分，实际应用中由 LLM 判断
        score = min(100, state["quality_score"] + 25)
        return {"quality_score": score}

    def should_continue(state: IterationState) -> str:
        """决定是否继续循环"""
        if state["iteration_count"] >= state["max_iterations"]:
            return "end"
        if state["quality_score"] >= 80:
            return "end"
        return "continue"

    # 模拟循环执行
    print("""
    def should_continue(state) -> str:
        if state["iteration_count"] >= state["max_iterations"]:
            return "end"
        if state["quality_score"] >= 80:
            return "end"
        return "continue"

    # 添加条件边
    graph.add_conditional_edges(
        "evaluate",
        should_continue,
        {
            "continue": "improve",  # 继续改进
            "end": END              # 结束
        }
    )
    """)

    # 演示循环
    print("\n🔄 迭代循环演示:")
    print("-" * 40)

    state = {
        "content": "初始内容",
        "quality_score": 30,
        "iteration_count": 0,
        "max_iterations": 5,
    }

    while True:
        print(f"   迭代 {state['iteration_count'] + 1}:")
        state.update(improve_content(state))
        state.update(evaluate_quality(state))
        print(f"      内容: {state['content'][:40]}...")
        print(f"      评分: {state['quality_score']}")

        decision = should_continue(state)
        if decision == "end":
            print(
                f"   ✅ 完成! (原因: {'达到质量标准' if state['quality_score'] >= 80 else '达到最大迭代次数'})"
            )
            break
        print()


# ==================== 第六部分：LangGraph 实际代码 ====================


def langgraph_real_code():
    """LangGraph 实际代码示例"""
    print("\n" + "=" * 60)
    print("第六部分：LangGraph 实际代码示例")
    print("=" * 60)

    print("""
    使用真实 LangGraph 库的代码示例
    （需要安装: pip install langgraph）
    
    ───────────────────────────────────────────────────────────
    
    from typing import TypedDict, Annotated
    from langgraph.graph import StateGraph, END
    import operator
    
    # 1. 定义状态
    class AgentState(TypedDict):
        messages: Annotated[list, operator.add]
        current_step: str
    
    # 2. 定义节点函数
    def research_node(state: AgentState) -> dict:
        # 执行研究任务
        return {
            "messages": ["[Research] 收集了相关资料..."],
            "current_step": "research_done"
        }
    
    def write_node(state: AgentState) -> dict:
        # 执行写作任务
        return {
            "messages": ["[Write] 完成内容撰写..."],
            "current_step": "write_done"
        }
    
    def review_node(state: AgentState) -> dict:
        # 执行审核任务
        return {
            "messages": ["[Review] 审核通过!"],
            "current_step": "complete"
        }
    
    # 3. 创建 Graph
    workflow = StateGraph(AgentState)
    
    # 4. 添加节点
    workflow.add_node("research", research_node)
    workflow.add_node("write", write_node)
    workflow.add_node("review", review_node)
    
    # 5. 添加边
    workflow.set_entry_point("research")
    workflow.add_edge("research", "write")
    workflow.add_edge("write", "review")
    workflow.add_edge("review", END)
    
    # 6. 编译
    app = workflow.compile()
    
    # 7. 执行
    result = app.invoke({
        "messages": ["开始任务"],
        "current_step": "start"
    })
    
    print(result["messages"])
    # 输出:
    # ["开始任务",
    #  "[Research] 收集了相关资料...",
    #  "[Write] 完成内容撰写...",
    #  "[Review] 审核通过!"]
    
    ───────────────────────────────────────────────────────────
    """)


# ==================== 第七部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：创建一个翻译工作流
        设计一个 Graph，包含：
        - 检测语言节点
        - 翻译节点
        - 校对节点

        ✅ 参考答案：
        ```python
        from langgraph.graph import StateGraph, END
        from typing import TypedDict

        class TranslateState(TypedDict):
            text: str
            source_lang: str
            target_lang: str
            translated: str
            proofread: str

        def detect_language(state):
            # 模拟语言检测
            text = state["text"]
            lang = "zh" if any('\\u4e00' <= c <= '\\u9fff' for c in text) else "en"
            return {"source_lang": lang}

        def translate(state):
            prompt = f"将以下{state['source_lang']}翻译为{state['target_lang']}：{state['text']}"
            translated = llm.invoke(prompt).content
            return {"translated": translated}

        def proofread(state):
            prompt = f"校对并优化以下翻译：{state['translated']}"
            proofread = llm.invoke(prompt).content
            return {"proofread": proofread}

        graph = StateGraph(TranslateState)
        graph.add_node("detect", detect_language)
        graph.add_node("translate", translate)
        graph.add_node("proofread", proofread)
        graph.add_edge("detect", "translate")
        graph.add_edge("translate", "proofread")
        graph.add_edge("proofread", END)
        graph.set_entry_point("detect")
        ```
    
    练习 2：实现条件分支
        创建一个客服工作流：
        - 根据问题类型路由到不同的处理节点
        - 技术问题 → 技术支持
        - 账单问题 → 财务支持
        - 一般咨询 → 客服

        ✅ 参考答案：
        ```python
        def classify_question(state):
            prompt = f"分类问题类型（tech/billing/general）：{state['question']}"
            category = llm.invoke(prompt).content.strip().lower()
            return {"category": category}

        def route_question(state):
            category = state["category"]
            if "tech" in category:
                return "tech_support"
            elif "billing" in category:
                return "billing_support"
            else:
                return "general_support"

        graph = StateGraph(CustomerState)
        graph.add_node("classify", classify_question)
        graph.add_node("tech_support", handle_tech)
        graph.add_node("billing_support", handle_billing)
        graph.add_node("general_support", handle_general)

        graph.add_conditional_edges("classify", route_question)
        graph.add_edge("tech_support", END)
        graph.add_edge("billing_support", END)
        graph.add_edge("general_support", END)
        ```
    
    练习 3：实现循环改进
        创建一个代码审查 Graph：
        - 代码检查节点
        - 如果发现问题，返回修改节点
        - 最多循环 3 次

        ✅ 参考答案：
        ```python
        class CodeReviewState(TypedDict):
            code: str
            issues: list
            iteration: int
            max_iterations: int

        def check_code(state):
            prompt = f"检查代码问题：{state['code']}"
            issues = llm.invoke(prompt).content
            return {"issues": issues.split("\\n") if issues else []}

        def fix_code(state):
            prompt = f"修复以下问题：{state['issues']}\\n代码：{state['code']}"
            fixed = llm.invoke(prompt).content
            return {"code": fixed, "iteration": state["iteration"] + 1}

        def should_continue(state):
            if not state["issues"]:
                return "end"
            if state["iteration"] >= state["max_iterations"]:
                return "end"
            return "fix"

        graph = StateGraph(CodeReviewState)
        graph.add_node("check", check_code)
        graph.add_node("fix", fix_code)
        graph.add_conditional_edges("check", should_continue, {"fix": "fix", "end": END})
        graph.add_edge("fix", "check")  # 循环回检查
        ```
    
    思考题：
    ────────
    1. LangGraph 的状态管理与普通变量有什么区别？
       答：LangGraph 状态是持久化的、可追踪的，支持 reducer 
       来定义合并策略，适合复杂工作流。

    2. 什么时候应该使用条件边？
       答：当下一步操作依赖于当前状态或执行结果时，
       如任务分类、错误处理、循环控制等。

    3. 如何防止 Graph 中的无限循环？
       答：设置最大迭代次数、在状态中跟踪迭代计数、
       设计明确的终止条件。
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🔗 LangGraph 基础")
    print("=" * 60)

    langgraph_introduction()
    state_definition()
    simple_graph_demo()
    conditional_edges()
    loops_and_iteration()
    langgraph_real_code()
    exercises()

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：03-agent-communication.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
