import { useState, useCallback, useRef, useEffect, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  type Connection,
  type Edge,
  type Node,
  type NodeTypes,
  type NodeProps,
  Handle,
  Position,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  ArrowLeft,
  Save,
  Play,
  Cpu,
  BookOpen,
  GitBranch,
  Code,
  CircleDot,
  CircleStop,
} from "lucide-react";

import { workflowApi } from "../../services/api";
import NodeConfigPanel from "./NodeConfigPanel";
import RunResultPanel from "./RunResultPanel";

// ==================== Types ====================

type WfNodeData = {
  label: string;
  config: Record<string, unknown>;
  output_var?: string;
  running?: boolean;
  completed?: boolean;
  failed?: boolean;
};

type WfNode = Node<WfNodeData>;
type WfEdge = Edge;

// ==================== Custom Nodes ====================

const NODE_STYLES: Record<
  string,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  { bg: string; border: string; icon: any; label: string }
> = {
  start: { bg: "bg-emerald-50", border: "border-emerald-300", icon: CircleDot, label: "开始" },
  llm: { bg: "bg-blue-50", border: "border-blue-300", icon: Cpu, label: "LLM" },
  knowledge: { bg: "bg-purple-50", border: "border-purple-300", icon: BookOpen, label: "知识库检索" },
  condition: { bg: "bg-amber-50", border: "border-amber-300", icon: GitBranch, label: "条件分支" },
  code: { bg: "bg-slate-50", border: "border-slate-300", icon: Code, label: "代码执行" },
  end: { bg: "bg-red-50", border: "border-red-300", icon: CircleStop, label: "结束" },
};

function CustomNode({ data, type }: NodeProps<WfNode>) {
  const style = NODE_STYLES[type || "start"] || NODE_STYLES.start;
  const Icon = style.icon;
  const isStart = type === "start";
  const isEnd = type === "end";

  return (
    <div
      className={`px-4 py-3 rounded-lg border-2 ${style.bg} ${style.border} shadow-sm min-w-[140px] ${
        data.running ? "ring-2 ring-indigo-400 animate-pulse" : ""
      } ${data.completed ? "ring-2 ring-emerald-400" : ""} ${data.failed ? "ring-2 ring-red-400" : ""}`}
    >
      {!isStart && (
        <Handle type="target" position={Position.Left} className="!w-3 !h-3 !bg-slate-400" />
      )}
      <div className="flex items-center gap-2">
        <Icon className="w-4 h-4 text-slate-600" />
        <span className="text-sm font-medium text-slate-700">{data.label || style.label}</span>
      </div>
      {data.output_var && (
        <div className="text-xs text-slate-400 mt-1">→ {data.output_var}</div>
      )}
      {!isEnd && (
        <Handle type="source" position={Position.Right} className="!w-3 !h-3 !bg-slate-400" />
      )}
    </div>
  );
}

const nodeTypes: NodeTypes = {
  start: CustomNode,
  llm: CustomNode,
  knowledge: CustomNode,
  condition: CustomNode,
  code: CustomNode,
  end: CustomNode,
};

// ==================== Node Palette (Left Panel) ====================

const PALETTE_ITEMS = [
  { type: "start", label: "开始", icon: CircleDot, color: "text-emerald-500" },
  { type: "llm", label: "LLM", icon: Cpu, color: "text-blue-500" },
  { type: "knowledge", label: "知识库检索", icon: BookOpen, color: "text-purple-500" },
  { type: "condition", label: "条件分支", icon: GitBranch, color: "text-amber-500" },
  { type: "code", label: "代码执行", icon: Code, color: "text-slate-500" },
  { type: "end", label: "结束", icon: CircleStop, color: "text-red-500" },
];

// ==================== Editor Component ====================

interface EditorProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  providers: any[];
  workflowId: string;
  onBack: () => void;
}

export default function WorkflowEditor({ workflowId, providers, onBack }: EditorProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<WfNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<WfEdge>([]);
  const [workflowName, setWorkflowName] = useState("");
  const [selectedNode, setSelectedNode] = useState<WfNode | null>(null);
  const [saving, setSaving] = useState(false);
  const [showRunPanel, setShowRunPanel] = useState(false);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const nodeIdCounter = useRef(0);

  // Load workflow
  useEffect(() => {
    const load = async () => {
      try {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const data: any = await workflowApi.get(workflowId);
        setWorkflowName(data.name);

        const graphData = data.graph_data || { nodes: [], edges: [] };

        // Convert backend nodes to React Flow nodes
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const rfNodes: WfNode[] = (graphData.nodes || []).map((n: any) => ({
          id: n.id,
          type: n.type,
          position: n.position || { x: 0, y: 0 },
          data: {
            label: n.config?.label || NODE_STYLES[n.type]?.label || n.type,
            config: n.config || {},
            output_var: n.output_var,
          },
        }));

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const rfEdges: WfEdge[] = (graphData.edges || []).map((e: any, i: number) => ({
          id: e.id || `e-${e.source}-${e.target}-${i}`,
          source: e.source,
          target: e.target,
          animated: true,
          style: { stroke: "#94a3b8", strokeWidth: 2 },
        }));

        setNodes(rfNodes);
        setEdges(rfEdges);

        // Set counter based on existing nodes
        const maxId = rfNodes.reduce((max: number, n: WfNode) => {
          const match = n.id.match(/_(\d+)$/);
          return match ? Math.max(max, parseInt(match[1])) : max;
        }, 0);
        nodeIdCounter.current = maxId;
      } catch {
        /* empty */
      }
    };
    load();
  }, [workflowId, setNodes, setEdges]);

  // Handle connections
  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds: WfEdge[]) =>
        addEdge(
          {
            ...connection,
            animated: true,
            style: { stroke: "#94a3b8", strokeWidth: 2 },
          },
          eds
        )
      );
    },
    [setEdges]
  );

  // Handle node selection
  const onNodeClick = useCallback((_: React.MouseEvent, node: WfNode) => {
    setSelectedNode(node);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  // Save workflow
  const handleSave = async () => {
    setSaving(true);
    try {
      const graphData = {
        nodes: nodes.map((n: WfNode) => ({
          id: n.id,
          type: n.type,
          position: n.position,
          config: n.data?.config || {},
          output_var: n.data?.output_var,
        })),
        edges: edges.map((e: WfEdge) => ({
          id: e.id,
          source: e.source,
          target: e.target,
        })),
      };
      await workflowApi.update(workflowId, { graph_data: graphData });
    } catch {
      /* empty */
    } finally {
      setSaving(false);
    }
  };

  // Add node from palette
  const handleAddNode = (type: string) => {
    nodeIdCounter.current += 1;
    const id = `${type}_${nodeIdCounter.current}`;
    const newNode: WfNode = {
      id,
      type,
      position: { x: 300 + Math.random() * 100, y: 150 + Math.random() * 100 },
      data: {
        label: NODE_STYLES[type]?.label || type,
        config: {},
        output_var: id,
      },
    };
    setNodes((nds: WfNode[]) => [...nds, newNode]);
  };

  // Update node config from config panel
  const handleNodeConfigChange = useCallback(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (nodeId: string, config: any, label?: string) => {
      setNodes((nds: WfNode[]) =>
        nds.map((n: WfNode) =>
          n.id === nodeId
            ? {
                ...n,
                data: {
                  ...n.data,
                  config,
                  label: label || n.data.label,
                },
              }
            : n
        )
      );
      setSelectedNode((prev: WfNode | null) =>
        prev && prev.id === nodeId
          ? { ...prev, data: { ...prev.data, config, label: label || prev.data.label } }
          : prev
      );
    },
    [setNodes]
  );

  // Handle delete key
  const onKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if ((e.key === "Delete" || e.key === "Backspace") && selectedNode) {
        setNodes((nds: WfNode[]) => nds.filter((n: WfNode) => n.id !== selectedNode.id));
        setEdges((eds: WfEdge[]) =>
          eds.filter((edge: WfEdge) => edge.source !== selectedNode.id && edge.target !== selectedNode.id)
        );
        setSelectedNode(null);
      }
    },
    [selectedNode, setNodes, setEdges]
  );

  // Drag and drop support
  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const type = event.dataTransfer.getData("application/reactflow");
      if (!type) return;

      const bounds = reactFlowWrapper.current?.getBoundingClientRect();
      if (!bounds) return;

      nodeIdCounter.current += 1;
      const id = `${type}_${nodeIdCounter.current}`;

      const newNode: WfNode = {
        id,
        type,
        position: {
          x: event.clientX - bounds.left - 70,
          y: event.clientY - bounds.top - 20,
        },
        data: {
          label: NODE_STYLES[type]?.label || type,
          config: {},
          output_var: id,
        },
      };
      setNodes((nds: WfNode[]) => [...nds, newNode]);
    },
    [setNodes]
  );

  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData("application/reactflow", nodeType);
    event.dataTransfer.effectAllowed = "move";
  };

  // Default viewport
  const defaultViewport = useMemo(() => ({ x: 50, y: 50, zoom: 1 }), []);

  return (
    <div className="flex flex-col h-[calc(100vh-2rem)]" onKeyDown={onKeyDown} tabIndex={0}>
      {/* Top Bar */}
      <div className="flex items-center justify-between px-4 py-3 bg-white border-b border-slate-200">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-slate-600" />
          </button>
          <span className="text-sm text-slate-500">工作流 /</span>
          <span className="font-semibold text-slate-800">{workflowName}</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowRunPanel(!showRunPanel)}
            className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors text-sm"
          >
            <Play className="w-4 h-4" />
            运行
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 px-3 py-1.5 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors text-sm disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {saving ? "保存中..." : "保存"}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Node Palette */}
        <div className="w-44 bg-white border-r border-slate-200 p-3 flex flex-col gap-1">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
            节点
          </div>
          {PALETTE_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.type}
                draggable
                onDragStart={(e) => onDragStart(e, item.type)}
                onClick={() => handleAddNode(item.type)}
                className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-slate-50 cursor-grab active:cursor-grabbing transition-colors text-sm"
              >
                <Icon className={`w-4 h-4 ${item.color}`} />
                <span className="text-slate-700">{item.label}</span>
              </div>
            );
          })}
        </div>

        {/* Center: React Flow Canvas */}
        <div className="flex-1 relative" ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            onDragOver={onDragOver}
            onDrop={onDrop}
            nodeTypes={nodeTypes}
            defaultViewport={defaultViewport}
            fitView={false}
            deleteKeyCode={null}
            className="bg-slate-50"
          >
            <Background color="#cbd5e1" gap={20} size={1} />
            <Controls className="!bg-white !border-slate-200 !shadow-sm" />
            <MiniMap
              className="!bg-white !border-slate-200"
              nodeColor={() => "#94a3b8"}
            />
          </ReactFlow>
        </div>

        {/* Right: Node Config Panel */}
        {selectedNode && (
          <NodeConfigPanel
            node={selectedNode}
            providers={providers}
            onChange={handleNodeConfigChange}
            onClose={() => setSelectedNode(null)}
          />
        )}
      </div>

      {/* Bottom: Run Result Panel */}
      {showRunPanel && (
        <RunResultPanel
          workflowId={workflowId}
          onNodeStatus={(status: Record<string, { status: string }>) => {
            // Update node visual states
            setNodes((nds: WfNode[]) =>
              nds.map((n: WfNode) => ({
                ...n,
                data: {
                  ...n.data,
                  running: status[n.id]?.status === "running",
                  completed: status[n.id]?.status === "completed",
                  failed: status[n.id]?.status === "failed",
                },
              }))
            );
          }}
          onClose={() => {
            setShowRunPanel(false);
            // Clear visual states
            setNodes((nds: WfNode[]) =>
              nds.map((n: WfNode) => ({
                ...n,
                data: { ...n.data, running: false, completed: false, failed: false },
              }))
            );
          }}
        />
      )}
    </div>
  );
}
