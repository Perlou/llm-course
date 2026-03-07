import { useState } from "react";
import { X, Loader2 } from "lucide-react";
import { providerApi } from "../../services/api";

interface Provider {
  id: string;
  name: string;
  provider_type: string;
  base_url: string | null;
  models: string[];
  config: Record<string, unknown>;
  is_active: boolean;
}

interface Props {
  provider: Provider | null;
  onClose: () => void;
  onSave: () => void;
}

const PROVIDER_TYPES = [
  {
    value: "openai",
    label: "OpenAI",
    defaultModels: "gpt-4o,gpt-4o-mini,gpt-3.5-turbo",
  },
  {
    value: "anthropic",
    label: "Anthropic",
    defaultModels: "claude-sonnet-4-20250514,claude-3-5-haiku-20241022",
  },
  {
    value: "google",
    label: "Google",
    defaultModels: "gemini-2.5-flash,gemini-2.5-pro",
  },
  { value: "ollama", label: "Ollama (本地)", defaultModels: "llama3,qwen2" },
];

export default function ProviderModal({ provider, onClose, onSave }: Props) {
  const isEdit = !!provider;
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    name: provider?.name || "",
    provider_type: provider?.provider_type || "openai",
    api_key: "",
    base_url: provider?.base_url || "",
    models_str: provider?.models?.join(",") || "",
  });

  const handleTypeChange = (type: string) => {
    const preset = PROVIDER_TYPES.find((t) => t.value === type);
    setForm((prev) => ({
      ...prev,
      provider_type: type,
      name: prev.name || (preset?.label ?? ""),
      models_str: prev.models_str || (preset?.defaultModels ?? ""),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        name: form.name,
        provider_type: form.provider_type,
        api_key: form.api_key || undefined,
        base_url: form.base_url || undefined,
        models: form.models_str
          .split(",")
          .map((m) => m.trim())
          .filter(Boolean),
      };
      if (isEdit) {
        await providerApi.update(provider!.id, payload);
      } else {
        await providerApi.create(payload);
      }
      onSave();
    } catch (err) {
      console.error("Save failed", err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h2 className="text-lg font-semibold text-slate-800">
            {isEdit ? "编辑供应商" : "添加供应商"}
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded-md hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          {/* Provider Type */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              供应商类型
            </label>
            <div className="grid grid-cols-4 gap-2">
              {PROVIDER_TYPES.map((t) => (
                <button
                  key={t.value}
                  type="button"
                  onClick={() => handleTypeChange(t.value)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium border transition-colors ${
                    form.provider_type === t.value
                      ? "border-indigo-400 bg-indigo-50 text-indigo-700"
                      : "border-slate-200 text-slate-600 hover:border-slate-300"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              名称
            </label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="例如：OpenAI 生产环境"
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 transition-colors"
              required
            />
          </div>

          {/* API Key */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              API Key
              {isEdit && (
                <span className="text-slate-400 font-normal ml-1">
                  (留空保持不变)
                </span>
              )}
            </label>
            <input
              type="password"
              value={form.api_key}
              onChange={(e) => setForm({ ...form, api_key: e.target.value })}
              placeholder={
                form.provider_type === "ollama"
                  ? "(Ollama 无需 API Key)"
                  : "sk-..."
              }
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 transition-colors font-mono"
            />
          </div>

          {/* Base URL */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Base URL
              <span className="text-slate-400 font-normal ml-1">(可选)</span>
            </label>
            <input
              type="text"
              value={form.base_url}
              onChange={(e) => setForm({ ...form, base_url: e.target.value })}
              placeholder={
                form.provider_type === "ollama"
                  ? "http://localhost:11434"
                  : "自定义 API 端点"
              }
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 transition-colors"
            />
          </div>

          {/* Models */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              可用模型
              <span className="text-slate-400 font-normal ml-1">
                (逗号分隔)
              </span>
            </label>
            <input
              type="text"
              value={form.models_str}
              onChange={(e) => setForm({ ...form, models_str: e.target.value })}
              placeholder="gpt-4o,gpt-4o-mini"
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 transition-colors font-mono"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-4 py-2 text-sm rounded-lg bg-indigo-500 text-white hover:bg-indigo-600 transition-colors disabled:opacity-50 flex items-center gap-1.5"
            >
              {saving && <Loader2 className="w-4 h-4 animate-spin" />}
              {isEdit ? "保存修改" : "添加"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
