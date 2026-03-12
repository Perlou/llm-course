import { useState, useEffect } from "react";
import { ArrowLeft, Save, Loader2 } from "lucide-react";
import { agentApi, toolApi, datasetApi } from "../../services/api";

interface AgentItem {
  id: string;
  name: string;
  description: string | null;
  system_prompt: string;
  provider_id: string | null;
  model_name: string;
  temperature: number;
  max_tokens: number;
  strategy: string;
  dataset_ids: string[];
}

interface ProviderItem {
  id: string;
  name: string;
  provider_type: string;
  models: string[];
}

interface ToolItem {
  id: string;
  name: string;
  description: string | null;
  tool_type: string;
  is_active: boolean;
}

interface DatasetItem {
  id: string;
  name: string;
  document_count: number;
}

interface Props {
  agent: AgentItem | null;
  providers: ProviderItem[];
  onSave: () => void;
  onCancel: () => void;
}

export default function AgentConfig({
  agent,
  providers,
  onSave,
  onCancel,
}: Props) {
  const isEdit = !!agent;
  const [saving, setSaving] = useState(false);
  const [tools, setTools] = useState<ToolItem[]>([]);
  const [datasets, setDatasets] = useState<DatasetItem[]>([]);

  const [form, setForm] = useState({
    name: agent?.name || "",
    description: agent?.description || "",
    system_prompt:
      agent?.system_prompt || "你是一个有用的 AI 助手。请用中文回答问题。",
    provider_id: agent?.provider_id || "",
    model_name: agent?.model_name || "gpt-4o-mini",
    temperature: agent?.temperature ?? 0.7,
    max_tokens: agent?.max_tokens ?? 2048,
    strategy: agent?.strategy || "react",
    tool_ids: [] as string[],
    dataset_ids: (agent?.dataset_ids || []) as string[],
  });

  useEffect(() => {
    const load = async () => {
      try {
        const [toolData, dsData] = await Promise.all([
          toolApi.list(),
          datasetApi.list(),
        ]);
        setTools(toolData as unknown as ToolItem[]);
        setDatasets(dsData as unknown as DatasetItem[]);
      } catch (err) {
        console.error("Load failed", err);
      }
    };
    load();
  }, []);

  const selectedProvider = providers.find((p) => p.id === form.provider_id);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...form,
        description: form.description || undefined,
        provider_id: form.provider_id || undefined,
      };
      if (isEdit) {
        await agentApi.update(agent!.id, payload);
      } else {
        await agentApi.create(payload);
      }
      onSave();
    } catch (err) {
      console.error("Save failed", err);
    } finally {
      setSaving(false);
    }
  };

  const toggleTool = (id: string) => {
    setForm((f) => ({
      ...f,
      tool_ids: f.tool_ids.includes(id)
        ? f.tool_ids.filter((t) => t !== id)
        : [...f.tool_ids, id],
    }));
  };

  const toggleDataset = (id: string) => {
    setForm((f) => ({
      ...f,
      dataset_ids: f.dataset_ids.includes(id)
        ? f.dataset_ids.filter((d) => d !== id)
        : [...f.dataset_ids, id],
    }));
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={onCancel}
          className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="text-2xl font-bold text-slate-800">
          {isEdit ? `编辑 ${agent!.name}` : "新建 Agent"}
        </h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Info */}
        <div className="card p-5 space-y-4">
          <h2 className="font-semibold text-slate-700">基本信息</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                名称
              </label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                策略
              </label>
              <select
                value={form.strategy}
                onChange={(e) => setForm({ ...form, strategy: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400"
              >
                <option value="react">ReAct</option>
                <option value="function_calling">Function Calling</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              描述
            </label>
            <input
              type="text"
              value={form.description}
              onChange={(e) =>
                setForm({ ...form, description: e.target.value })
              }
              placeholder="简述 Agent 用途..."
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400"
            />
          </div>
        </div>

        {/* Model Config */}
        <div className="card p-5 space-y-4">
          <h2 className="font-semibold text-slate-700">模型配置</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                供应商
              </label>
              <select
                value={form.provider_id}
                onChange={(e) =>
                  setForm({ ...form, provider_id: e.target.value })
                }
                className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400"
              >
                <option value="">-- 选择供应商 --</option>
                {providers.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.provider_type})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                模型
              </label>
              <select
                value={form.model_name}
                onChange={(e) =>
                  setForm({ ...form, model_name: e.target.value })
                }
                className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400"
              >
                {selectedProvider?.models.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
                {!selectedProvider && (
                  <option value={form.model_name}>{form.model_name}</option>
                )}
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                温度: {form.temperature}
              </label>
              <input
                type="range"
                value={form.temperature}
                onChange={(e) =>
                  setForm({
                    ...form,
                    temperature: parseFloat(e.target.value),
                  })
                }
                min={0}
                max={2}
                step={0.1}
                className="w-full accent-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                最大 Token
              </label>
              <input
                type="number"
                value={form.max_tokens}
                onChange={(e) =>
                  setForm({
                    ...form,
                    max_tokens: parseInt(e.target.value) || 2048,
                  })
                }
                min={1}
                max={128000}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400"
              />
            </div>
          </div>
        </div>

        {/* System Prompt */}
        <div className="card p-5 space-y-3">
          <h2 className="font-semibold text-slate-700">系统提示词</h2>
          <textarea
            value={form.system_prompt}
            onChange={(e) =>
              setForm({ ...form, system_prompt: e.target.value })
            }
            rows={5}
            className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 resize-y"
          />
        </div>

        {/* Tools */}
        <div className="card p-5 space-y-3">
          <h2 className="font-semibold text-slate-700">工具绑定</h2>
          {tools.length === 0 ? (
            <p className="text-sm text-slate-400">暂无工具</p>
          ) : (
            <div className="grid grid-cols-2 gap-2">
              {tools.map((t) => (
                <label
                  key={t.id}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg border cursor-pointer transition-colors ${
                    form.tool_ids.includes(t.id)
                      ? "border-indigo-300 bg-indigo-50"
                      : "border-slate-200 hover:bg-slate-50"
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={form.tool_ids.includes(t.id)}
                    onChange={() => toggleTool(t.id)}
                    className="accent-indigo-500"
                  />
                  <div>
                    <span className="text-sm font-medium text-slate-700">
                      {t.name}
                    </span>
                    <span className="ml-1.5 text-xs text-slate-400">
                      ({t.tool_type})
                    </span>
                  </div>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Datasets */}
        <div className="card p-5 space-y-3">
          <h2 className="font-semibold text-slate-700">知识库绑定</h2>
          {datasets.length === 0 ? (
            <p className="text-sm text-slate-400">暂无知识库</p>
          ) : (
            <div className="grid grid-cols-2 gap-2">
              {datasets.map((ds) => (
                <label
                  key={ds.id}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg border cursor-pointer transition-colors ${
                    form.dataset_ids.includes(ds.id)
                      ? "border-emerald-300 bg-emerald-50"
                      : "border-slate-200 hover:bg-slate-50"
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={form.dataset_ids.includes(ds.id)}
                    onChange={() => toggleDataset(ds.id)}
                    className="accent-emerald-500"
                  />
                  <div>
                    <span className="text-sm font-medium text-slate-700">
                      {ds.name}
                    </span>
                    <span className="ml-1.5 text-xs text-slate-400">
                      ({ds.document_count} 文档)
                    </span>
                  </div>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50"
          >
            取消
          </button>
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-1.5 px-5 py-2 text-sm rounded-lg bg-indigo-500 text-white hover:bg-indigo-600 disabled:opacity-50"
          >
            {saving ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            {isEdit ? "保存" : "创建"}
          </button>
        </div>
      </form>
    </div>
  );
}
