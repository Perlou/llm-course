"""
Mini-Dify - 工作流引擎单元测试
测试 WorkflowEngine 核心逻辑（不依赖外部 LLM 调用）
"""

import pytest
from app.core.workflow_engine import (
    WorkflowState,
    NodeResult,
    NodeExecutors,
    WorkflowEngine,
)


# ==================== Data Classes ====================


class TestWorkflowState:
    """WorkflowState 数据类测试"""

    def test_default_state(self):
        state = WorkflowState()
        assert state.inputs == {}
        assert state.node_results == {}
        assert state.variables == {}
        assert state.final_output is None

    def test_state_with_inputs(self):
        state = WorkflowState(inputs={"name": "Alice", "age": 30})
        assert state.inputs["name"] == "Alice"
        assert state.inputs["age"] == 30

    def test_state_variables_mutation(self):
        state = WorkflowState()
        state.variables["key1"] = "value1"
        state.variables["key2"] = "value2"
        assert len(state.variables) == 2

    def test_state_node_results(self):
        state = WorkflowState()
        result = NodeResult(
            node_id="n1",
            node_type="start",
            status="completed",
            output="hello",
            duration_ms=10,
        )
        state.node_results["n1"] = result
        assert state.node_results["n1"].status == "completed"
        assert state.node_results["n1"].output == "hello"


class TestNodeResult:
    """NodeResult 数据类测试"""

    def test_default_values(self):
        result = NodeResult(node_id="n1", node_type="llm")
        assert result.status == "pending"
        assert result.output is None
        assert result.error is None
        assert result.duration_ms == 0

    def test_completed_result(self):
        result = NodeResult(
            node_id="n2",
            node_type="code",
            status="completed",
            output={"count": 42},
            duration_ms=150,
        )
        assert result.status == "completed"
        assert result.output == {"count": 42}
        assert result.duration_ms == 150

    def test_failed_result(self):
        result = NodeResult(
            node_id="n3",
            node_type="code",
            status="failed",
            error="代码执行超时",
            duration_ms=10000,
        )
        assert result.status == "failed"
        assert "超时" in result.error


# ==================== Template Rendering ====================


class TestRenderTemplate:
    """_render_template 模板渲染测试"""

    def test_simple_variable(self):
        result = NodeExecutors._render_template(
            "Hello, {{name}}!", {"name": "World"}
        )
        assert result == "Hello, World!"

    def test_multiple_variables(self):
        result = NodeExecutors._render_template(
            "{{greeting}}, {{name}}! You are {{age}} years old.",
            {"greeting": "Hi", "name": "Alice", "age": 30},
        )
        assert result == "Hi, Alice! You are 30 years old."

    def test_missing_variable_keeps_original(self):
        result = NodeExecutors._render_template(
            "Hello, {{undefined_var}}!", {}
        )
        assert result == "Hello, {{undefined_var}}!"

    def test_no_variables(self):
        result = NodeExecutors._render_template("No variables here.", {})
        assert result == "No variables here."

    def test_empty_template(self):
        result = NodeExecutors._render_template("", {"name": "Test"})
        assert result == ""

    def test_variable_with_spaces(self):
        result = NodeExecutors._render_template(
            "{{ name }}", {"name": "Alice"}
        )
        assert result == "Alice"

    def test_variable_type_coercion(self):
        """非字符串值应被转换为字符串"""
        result = NodeExecutors._render_template(
            "Count: {{count}}", {"count": 42}
        )
        assert result == "Count: 42"

    def test_nested_braces_not_matched(self):
        """不应匹配嵌套花括号"""
        result = NodeExecutors._render_template(
            "JSON: {{{key}}}", {"key": "value"}
        )
        assert "value" in result


# ==================== Start Node ====================


class TestStartNodeExecutor:
    """开始节点执行器测试"""

    @pytest.mark.anyio
    async def test_basic_start(self):
        state = WorkflowState(inputs={"user_message": "你好"})
        output = await NodeExecutors.execute_start({}, state)
        assert output == {"user_message": "你好"}
        assert state.variables["user_message"] == "你好"

    @pytest.mark.anyio
    async def test_start_with_multiple_inputs(self):
        state = WorkflowState(inputs={"a": 1, "b": "two", "c": [3]})
        output = await NodeExecutors.execute_start({}, state)
        assert len(output) == 3
        assert state.variables["a"] == 1
        assert state.variables["b"] == "two"
        assert state.variables["c"] == [3]

    @pytest.mark.anyio
    async def test_start_empty_inputs(self):
        state = WorkflowState(inputs={})
        output = await NodeExecutors.execute_start({}, state)
        assert output == {}
        assert state.variables == {}


# ==================== Code Node ====================


class TestCodeNodeExecutor:
    """代码执行节点测试"""

    @pytest.mark.anyio
    async def test_simple_code(self):
        state = WorkflowState()
        state.variables["x"] = 10
        output = await NodeExecutors.execute_code(
            {"code": "result = inputs['x'] * 2"}, state
        )
        assert output == 20

    @pytest.mark.anyio
    async def test_code_with_math(self):
        state = WorkflowState()
        output = await NodeExecutors.execute_code(
            {"code": "import math\nresult = math.sqrt(144)"}, state
        )
        # math is pre-loaded in safe_locals
        assert output == 12.0

    @pytest.mark.anyio
    async def test_code_list_operations(self):
        state = WorkflowState()
        state.variables["items"] = [3, 1, 4, 1, 5]
        output = await NodeExecutors.execute_code(
            {"code": "result = sorted(inputs['items'])"},
            state,
        )
        assert output == [1, 1, 3, 4, 5]

    @pytest.mark.anyio
    async def test_code_string_operations(self):
        state = WorkflowState()
        state.variables["text"] = "hello world"
        output = await NodeExecutors.execute_code(
            {"code": "result = inputs['text'].upper()"},
            state,
        )
        assert output == "HELLO WORLD"

    @pytest.mark.anyio
    async def test_code_no_result_variable(self):
        """未设置 result 变量时返回提示"""
        state = WorkflowState()
        output = await NodeExecutors.execute_code(
            {"code": "x = 42"}, state
        )
        assert "未设置 result" in str(output)

    @pytest.mark.anyio
    async def test_code_error_handling(self):
        """代码执行错误应抛出 RuntimeError"""
        state = WorkflowState()
        with pytest.raises(RuntimeError, match="代码执行错误"):
            await NodeExecutors.execute_code(
                {"code": "result = 1 / 0"}, state
            )

    @pytest.mark.anyio
    async def test_code_forbidden_imports(self):
        """禁止危险操作（__builtins__ 限制）"""
        state = WorkflowState()
        with pytest.raises(RuntimeError):
            await NodeExecutors.execute_code(
                {"code": "import os\nresult = os.listdir('/')"},
                state,
            )

    @pytest.mark.anyio
    async def test_code_dict_operations(self):
        state = WorkflowState()
        state.variables["data"] = {"a": 1, "b": 2}
        output = await NodeExecutors.execute_code(
            {"code": "result = len(inputs['data'])"},
            state,
        )
        assert output == 2


# ==================== Condition Node ====================


class TestConditionNodeExecutor:
    """条件分支节点测试"""

    @pytest.mark.anyio
    async def test_true_condition(self):
        state = WorkflowState()
        state.variables["query"] = "this is a long query text"
        branch = await NodeExecutors.execute_condition(
            {
                "conditions": [
                    {"expression": "len(inputs.get('query', '')) > 10", "branch": "long"},
                    {"expression": "True", "branch": "short"},
                ]
            },
            state,
        )
        assert branch == "long"

    @pytest.mark.anyio
    async def test_fallback_condition(self):
        state = WorkflowState()
        state.variables["query"] = "hi"
        branch = await NodeExecutors.execute_condition(
            {
                "conditions": [
                    {"expression": "len(inputs.get('query', '')) > 10", "branch": "long"},
                    {"expression": "True", "branch": "default"},
                ]
            },
            state,
        )
        assert branch == "default"

    @pytest.mark.anyio
    async def test_no_conditions(self):
        state = WorkflowState()
        branch = await NodeExecutors.execute_condition(
            {"conditions": []}, state
        )
        assert branch == "default"

    @pytest.mark.anyio
    async def test_invalid_expression_skipped(self):
        """无效表达式应被跳过，继续下一个"""
        state = WorkflowState()
        branch = await NodeExecutors.execute_condition(
            {
                "conditions": [
                    {"expression": "invalid_syntax(((", "branch": "bad"},
                    {"expression": "True", "branch": "fallback"},
                ]
            },
            state,
        )
        assert branch == "fallback"

    @pytest.mark.anyio
    async def test_numeric_comparison(self):
        state = WorkflowState()
        state.variables["score"] = 85
        branch = await NodeExecutors.execute_condition(
            {
                "conditions": [
                    {"expression": "inputs.get('score', 0) >= 90", "branch": "A"},
                    {"expression": "inputs.get('score', 0) >= 80", "branch": "B"},
                    {"expression": "True", "branch": "C"},
                ]
            },
            state,
        )
        assert branch == "B"


# ==================== Topological Sort ====================


class TestTopologicalSort:
    """拓扑排序测试"""

    def test_linear_graph(self):
        """线性图: start -> llm -> end"""
        nodes = [
            {"id": "start"}, {"id": "llm"}, {"id": "end"}
        ]
        edges = [
            {"source": "start", "target": "llm"},
            {"source": "llm", "target": "end"},
        ]
        order = WorkflowEngine._topological_sort(nodes, edges)
        assert order == ["start", "llm", "end"]

    def test_diamond_graph(self):
        """菱形图: start -> [a, b] -> end"""
        nodes = [
            {"id": "start"}, {"id": "a"}, {"id": "b"}, {"id": "end"}
        ]
        edges = [
            {"source": "start", "target": "a"},
            {"source": "start", "target": "b"},
            {"source": "a", "target": "end"},
            {"source": "b", "target": "end"},
        ]
        order = WorkflowEngine._topological_sort(nodes, edges)
        assert order[0] == "start"
        assert order[-1] == "end"
        assert set(order[1:3]) == {"a", "b"}

    def test_single_node(self):
        nodes = [{"id": "start"}]
        edges = []
        order = WorkflowEngine._topological_sort(nodes, edges)
        assert order == ["start"]

    def test_complex_graph(self):
        """复杂图: start -> a -> c -> end, start -> b -> c"""
        nodes = [
            {"id": "start"}, {"id": "a"}, {"id": "b"}, {"id": "c"}, {"id": "end"}
        ]
        edges = [
            {"source": "start", "target": "a"},
            {"source": "start", "target": "b"},
            {"source": "a", "target": "c"},
            {"source": "b", "target": "c"},
            {"source": "c", "target": "end"},
        ]
        order = WorkflowEngine._topological_sort(nodes, edges)
        assert order[0] == "start"
        assert order[-1] == "end"
        assert order.index("a") < order.index("c")
        assert order.index("b") < order.index("c")

    def test_empty_graph(self):
        order = WorkflowEngine._topological_sort([], [])
        assert order == []

    def test_parallel_branches(self):
        """并行分支: start -> [a, b, c]"""
        nodes = [
            {"id": "start"}, {"id": "a"}, {"id": "b"}, {"id": "c"}
        ]
        edges = [
            {"source": "start", "target": "a"},
            {"source": "start", "target": "b"},
            {"source": "start", "target": "c"},
        ]
        order = WorkflowEngine._topological_sort(nodes, edges)
        assert order[0] == "start"
        assert set(order[1:]) == {"a", "b", "c"}
