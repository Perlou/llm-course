import { X } from "lucide-react";

interface WfNode {
  id: string;
  type?: string;
  data: Record<string, unknown>;
}

interface NodeConfigPanelProps {
  node: WfNode;
  providers: any[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onChange: (nodeId: string, config: any, label?: string) => void;
  onClose: () => void;
}

export default function NodeConfigPanel({
  node,
  providers,
  onChange,
  onClose,
}: NodeConfigPanelProps) {
  const config = node.data?.config || {};
  const nodeType = node.type || "start";

  const updateConfig = (key: string, value: any) => {
    const newConfig = { ...config, [key]: value };
    onChange(node.id, newConfig);
  };

  return (
    <div className="w-72 bg-white border-l border-slate-200 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-slate-200">
        <div>
          <h3 className="font-semibold text-sm text-slate-800">节点配置</h3>
          <p className="text-xs text-slate-500">
            {node.id} ({nodeType})
          </p>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-slate-100 rounded transition-colors"
        >
          <X className="w-4 h-4 text-slate-400" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {/* Common: Label */}
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">
            节点标签
          </label>
          <input
            type="text"
            value={String(node.data?.label || "")}
            onChange={(e) => onChange(node.id, config, e.target.value)}
            className="w-full px-2.5 py-1.5 text-sm border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 focus:border-transparent outline-none"
          />
        </div>

        {/* Type-specific config */}
        {nodeType === "llm" && (
          <LLMConfig
            config={config}
            providers={providers}
            onUpdate={updateConfig}
          />
        )}
        {nodeType === "knowledge" && (
          <KnowledgeConfig config={config} onUpdate={updateConfig} />
        )}
        {nodeType === "condition" && (
          <ConditionConfig config={config} onUpdate={updateConfig} />
        )}
        {nodeType === "code" && (
          <CodeConfig config={config} onUpdate={updateConfig} />
        )}
        {(nodeType === "start" || nodeType === "end") && (
          <div className="text-xs text-slate-400 text-center py-4">
            {nodeType === "start"
              ? "开始节点接收工作流输入变量"
              : "结束节点输出最终结果"}
          </div>
        )}

        {/* Output variable name */}
        {nodeType !== "start" && nodeType !== "end" && (
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">
              输出变量名
            </label>
            <input
              type="text"
              value={String(node.data?.output_var || node.id)}
              readOnly
              className="w-full px-2.5 py-1.5 text-sm border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 focus:border-transparent outline-none"
              placeholder={node.id}
            />
            <p className="text-xs text-slate-400 mt-1">
              下游节点可通过 {"{{变量名}}"} 引用此输出
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

// ==================== LLM Node Config ====================

function LLMConfig({
  config,
  providers,
  onUpdate,
}: {
  config: any;
  providers: any[];
  onUpdate: (key: string, value: any) => void;
}) {
  const selectedProvider = providers.find(
    (p: any) => p.id === config.provider_id
  );
  const models = selectedProvider?.models || [];

  return (
    <>
      <div>
        <label className="block text-xs font-medium text-slate-600 mb-1">
          供应商
        </label>
        <select
          value={config.provider_id || ""}
          onChange={(e) => onUpdate("provider_id", e.target.value)}
          className="w-full px-2.5 py-1.5 text-sm border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 outline-none"
        >
          <option value="">选择供应商</option>
          {providers.map((p: any) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-xs font-medium text-slate-600 mb-1">
          模型
        </label>
        <select
          value={config.model || ""}
          onChange={(e) => onUpdate("model", e.target.value)}
          className="w-full px-2.5 py-1.5 text-sm border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 outline-none"
        >
          <option value="">选择模型</option>
          {models.map((m: string) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-xs font-medium text-slate-600 mb-1">
          System Prompt
        </label>
        <textarea
          value={config.system_prompt || ""}
          onChange={(e) => onUpdate("system_prompt", e.target.value)}
          rows={3}
          className="w-full px-2.5 py-1.5 text-sm border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 outline-none font-mono"
          placeholder="系统提示词（可选）"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-slate-600 mb-1">
          Prompt
        </label>
        <textarea
          value={config.prompt || ""}
          onChange={(e) => onUpdate("prompt", e.target.value)}
          rows={4}
          className="w-full px-2.5 py-1.5 text-sm border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 outline-none font-mono"
          placeholder="输入 Prompt，可用 {{变量名}} 引用上游输出"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-slate-600 mb-1">
          温度 ({config.temperature ?? 0.7})
        </label>
        <input
          type="range"
          min="0"
          max="2"
          step="0.1"
          value={config.temperature ?? 0.7}
          onChange={(e) => onUpdate("temperature", parseFloat(e.target.value))}
          className="w-full"
        />
      </div>
    </>
  );
}

// ==================== Knowledge Node Config ====================

function KnowledgeConfig({
  config,
  onUpdate,
}: {
  config: any;
  onUpdate: (key: string, value: any) => void;
}) {
  return (
    <>
      <div>
        <label className="block text-xs font-medium text-slate-600 mb-1">
          知识库 ID
        </label>
        <input
          type="text"
          value={config.dataset_id || ""}
          onChange={(e) => onUpdate("dataset_id", e.target.value)}
          className="w-full px-2.5 py-1.5 text-sm border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 outline-none"
          placeholder="输入知识库 ID"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-slate-600 mb-1">
          查询模板
        </label>
        <textarea
          value={config.query || ""}
          onChange={(e) => onUpdate("query", e.target.value)}
          rows={3}
          className="w-full px-2.5 py-1.5 text-sm border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 outline-none font-mono"
          placeholder="输入查询内容，可用 {{变量名}} 引用"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-slate-600 mb-1">
          Top K ({config.top_k ?? 5})
        </label>
        <input
          type="number"
          min="1"
          max="20"
          value={config.top_k ?? 5}
          onChange={(e) => onUpdate("top_k", parseInt(e.target.value))}
          className="w-full px-2.5 py-1.5 text-sm border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 outline-none"
        />
      </div>
    </>
  );
}

// ==================== Condition Node Config ====================

function ConditionConfig({
  config,
  onUpdate,
}: {
  config: any;
  onUpdate: (key: string, value: any) => void;
}) {
  const conditions = config.conditions || [
    { expression: "True", branch: "default" },
  ];

  const updateCondition = (
    index: number,
    key: string,
    value: string
  ) => {
    const newConditions = [...conditions];
    newConditions[index] = { ...newConditions[index], [key]: value };
    onUpdate("conditions", newConditions);
  };

  const addCondition = () => {
    onUpdate("conditions", [
      ...conditions,
      { expression: "True", branch: `branch_${conditions.length}` },
    ]);
  };

  return (
    <>
      <div className="text-xs text-slate-500 mb-2">
        条件按顺序求值，第一个为 True 的分支将被执行
      </div>
      {conditions.map((cond: any, i: number) => (
        <div key={i} className="border border-slate-200 rounded-md p-2 space-y-2">
          <div>
            <label className="block text-xs text-slate-500 mb-0.5">
              表达式 #{i + 1}
            </label>
            <input
              type="text"
              value={cond.expression}
              onChange={(e) => updateCondition(i, "expression", e.target.value)}
              className="w-full px-2 py-1 text-xs border border-slate-300 rounded font-mono focus:ring-1 focus:ring-indigo-500 outline-none"
              placeholder="Python 表达式"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-0.5">分支名</label>
            <input
              type="text"
              value={cond.branch}
              onChange={(e) => updateCondition(i, "branch", e.target.value)}
              className="w-full px-2 py-1 text-xs border border-slate-300 rounded font-mono focus:ring-1 focus:ring-indigo-500 outline-none"
            />
          </div>
        </div>
      ))}
      <button
        onClick={addCondition}
        className="text-xs text-indigo-600 hover:text-indigo-700"
      >
        + 添加条件
      </button>
    </>
  );
}

// ==================== Code Node Config ====================

function CodeConfig({
  config,
  onUpdate,
}: {
  config: any;
  onUpdate: (key: string, value: any) => void;
}) {
  return (
    <>
      <div>
        <label className="block text-xs font-medium text-slate-600 mb-1">
          Python 代码
        </label>
        <textarea
          value={config.code || ""}
          onChange={(e) => onUpdate("code", e.target.value)}
          rows={10}
          className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 outline-none font-mono bg-slate-50"
          placeholder={`# 可用变量: inputs (dict)\n# 将结果赋值给 result\n\nresult = inputs.get("user_message", "").upper()`}
        />
        <p className="text-xs text-slate-400 mt-1">
          代码在安全沙箱中执行（限时 10 秒）。通过 inputs 访问上游变量，将结果赋值给
          result。
        </p>
      </div>
    </>
  );
}
