---
name: add-workflow-node
description: 为 Mini-Dify 工作流引擎添加新的节点类型
---

# 添加工作流节点技能

此技能用于为 Mini-Dify 工作流引擎添加新的节点类型。工作流是 Mini-Dify 的核心亮点功能。

## 架构概览

```
前端 (React Flow)                    后端 (LangGraph)
┌──────────────────────┐            ┌──────────────────────┐
│ 节点 UI 组件          │   JSON    │ 节点执行器            │
│ 节点配置面板          │ ──────→   │ LangGraph StateGraph  │
│ 画布渲染              │            │ 条件路由              │
│                      │   SSE     │                      │
│ 执行状态高亮          │ ←──────   │ 流式返回              │
└──────────────────────┘            └──────────────────────┘
```

## 已有节点类型

| 类型      | 标识        | 说明         |
| --------- | ----------- | ------------ |
| 开始节点  | `start`     | 工作流入口   |
| LLM 节点  | `llm`       | 调用大模型   |
| 知识检索  | `knowledge` | 知识库检索   |
| 条件分支  | `condition` | 条件路由     |
| 代码执行  | `code`      | Python 代码  |
| HTTP 请求 | `http`      | 调用外部 API |
| 结束节点  | `end`       | 工作流出口   |

## 添加新节点步骤

### 1. 后端：定义节点类型

```python
# app/core/workflow_engine.py
from enum import Enum

class NodeType(str, Enum):
    START = "start"
    LLM = "llm"
    KNOWLEDGE = "knowledge"
    CONDITION = "condition"
    CODE = "code"
    HTTP = "http"
    END = "end"
    NEW_NODE = "new_node"   # ← 新增
```

### 2. 后端：实现节点执行器

```python
# app/core/node_handlers/new_node_handler.py
"""
Mini-Dify - 新节点执行器
"""

from typing import Any


class NewNodeHandler:
    """新节点处理器"""

    def __init__(self, config: dict):
        """
        config 示例:
        {
            "param1": "value1",
            "param2": 42
        }
        """
        self.config = config

    async def __call__(self, state: dict) -> dict:
        """
        执行节点逻辑

        Args:
            state: 工作流状态 (包含上游节点的输出)

        Returns:
            更新后的状态
        """
        # 1. 从 state 获取输入
        input_data = state.get("last_output", "")

        # 2. 执行业务逻辑
        result = await self._process(input_data)

        # 3. 返回更新的状态
        return {
            **state,
            "last_output": result,
            f"node_{self.config.get('node_id')}_output": result,
        }

    async def _process(self, input_data: str) -> str:
        """核心处理逻辑"""
        # 实现具体业务逻辑
        return f"Processed: {input_data}"
```

### 3. 后端：注册到工作流引擎

```python
# app/core/workflow_engine.py

from app.core.node_handlers.new_node_handler import NewNodeHandler

class WorkflowEngine:
    NODE_HANDLERS = {
        NodeType.LLM: LLMNodeHandler,
        NodeType.KNOWLEDGE: KnowledgeNodeHandler,
        NodeType.CONDITION: ConditionNodeHandler,
        NodeType.CODE: CodeNodeHandler,
        NodeType.HTTP: HTTPNodeHandler,
        NodeType.NEW_NODE: NewNodeHandler,   # ← 注册
    }

    def _get_node_handler(self, node_type: str):
        handler_class = self.NODE_HANDLERS.get(NodeType(node_type))
        if not handler_class:
            raise ValueError(f"Unknown node type: {node_type}")
        return handler_class
```

### 4. 前端：创建节点 UI 组件

```tsx
// src/pages/Workflow/nodes/NewNode.tsx
import { Handle, Position, NodeProps } from "reactflow";

export function NewNode({ data, selected }: NodeProps) {
  return (
    <div
      className={`
        px-4 py-3 rounded-lg border-2 bg-white min-w-[180px]
        ${selected ? "border-indigo-500 shadow-lg" : "border-slate-200"}
      `}
    >
      {/* 输入锚点 */}
      <Handle
        type="target"
        position={Position.Left}
        className="!bg-indigo-500"
      />

      {/* 节点内容 */}
      <div className="flex items-center gap-2">
        <span className="text-lg">🆕</span>
        <div>
          <div className="text-sm font-medium text-slate-800">
            {data.label || "新节点"}
          </div>
          <div className="text-xs text-slate-500">
            {data.config?.param1 || "未配置"}
          </div>
        </div>
      </div>

      {/* 输出锚点 */}
      <Handle
        type="source"
        position={Position.Right}
        className="!bg-indigo-500"
      />
    </div>
  );
}
```

### 5. 前端：创建配置面板

```tsx
// src/pages/Workflow/panels/NewNodePanel.tsx
interface NewNodePanelProps {
  nodeId: string;
  config: any;
  onChange: (config: any) => void;
}

export function NewNodePanel({ nodeId, config, onChange }: NewNodePanelProps) {
  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-slate-800">新节点配置</h3>

      <div>
        <label className="block text-sm font-medium text-slate-600 mb-1">
          参数 1
        </label>
        <input
          type="text"
          value={config?.param1 || ""}
          onChange={(e) => onChange({ ...config, param1: e.target.value })}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          placeholder="请输入..."
        />
      </div>
    </div>
  );
}
```

### 6. 前端：注册节点类型

```tsx
// src/pages/Workflow/Editor.tsx
import { NewNode } from "./nodes/NewNode";

const nodeTypes = {
  start: StartNode,
  llm: LLMNode,
  knowledge: KnowledgeNode,
  condition: ConditionNode,
  code: CodeNode,
  http: HTTPNode,
  end: EndNode,
  new_node: NewNode,   // ← 注册
};

// React Flow 组件
<ReactFlow nodeTypes={nodeTypes} ... />
```

### 7. 更新节点面板（拖拽列表）

```tsx
// src/pages/Workflow/NodePanel.tsx
const nodeList = [
  // 已有节点...
  { type: "new_node", icon: "🆕", label: "新节点", description: "节点描述" },
];
```

## 节点开发规范

### 后端规范

1. **纯函数风格**: Handler 的 `__call__` 方法接收 state 返回新 state
2. **不可变状态**: 返回新 dict，不修改输入 state
3. **错误处理**: 异常时在 state 中设置 `error` 字段
4. **超时控制**: 长时间操作需设置超时

### 前端规范

1. **统一样式**: 使用 indigo 主色，圆角 `rounded-lg`
2. **锚点位置**: 输入在左 (Left)，输出在右 (Right)
3. **状态指示**: 运行时高亮边框，完成时显示✅
4. **反馈**: 配置面板实时预览

## 节点执行状态

```python
# SSE 事件格式
{"node_id": "node_1", "status": "running", "type": "new_node"}
{"node_id": "node_1", "status": "completed", "output": "结果..."}
{"node_id": "node_1", "status": "failed", "error": "错误信息"}
```
