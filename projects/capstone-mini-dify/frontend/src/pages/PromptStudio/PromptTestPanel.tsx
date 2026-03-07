import { useState } from "react";
import { Play, Loader2, X, Plus, Minus } from "lucide-react";
import { promptApi } from "../../services/api";

interface Provider {
  id: string;
  name: string;
  provider_type: string;
  models: string[];
  is_active: boolean;
}

interface TestResult {
  model: string;
  provider_id: string;
  response: string;
  input_tokens: number;
  output_tokens: number;
  latency_ms: number;
  error: string | null;
}

interface TestResponse {
  rendered_system_prompt: string;
  rendered_user_prompt: string;
  results: TestResult[];
}

interface Props {
  promptId: string;
  variables: string[];
  providers: Provider[];
  onClose: () => void;
}

export default function PromptTestPanel({
  promptId,
  variables,
  providers,
  onClose,
}: Props) {
  const [variableValues, setVariableValues] = useState<Record<string, string>>(
    Object.fromEntries(variables.map((v) => [v, ""])),
  );
  const [selectedModels, setSelectedModels] = useState<
    { providerId: string; model: string }[]
  >(
    providers.length > 0 && providers[0].models.length > 0
      ? [{ providerId: providers[0].id, model: providers[0].models[0] }]
      : [],
  );
  const [testing, setTesting] = useState(false);
  const [results, setResults] = useState<TestResponse | null>(null);

  const addModel = () => {
    if (providers.length === 0) return;
    const p = providers[0];
    setSelectedModels((prev) => [
      ...prev,
      { providerId: p.id, model: p.models[0] || "" },
    ]);
  };

  const removeModel = (index: number) => {
    setSelectedModels((prev) => prev.filter((_, i) => i !== index));
  };

  const handleTest = async () => {
    if (selectedModels.length === 0) return;
    setTesting(true);
    setResults(null);
    try {
      const data = (await promptApi.test(promptId, {
        variables: variableValues,
        model_configs: selectedModels.map((m) => ({
          provider_id: m.providerId,
          model: m.model,
        })),
      })) as unknown as TestResponse;
      setResults(data);
    } catch (err) {
      console.error("Test failed", err);
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="w-96 border-l border-slate-200 bg-slate-50 overflow-y-auto flex-shrink-0">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
        <h3 className="font-semibold text-sm text-slate-700">🧪 测试面板</h3>
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-slate-200 text-slate-400"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="p-4 space-y-4">
        {/* Variables */}
        {variables.length > 0 && (
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-2">
              变量值
            </label>
            <div className="space-y-2">
              {variables.map((v) => (
                <div key={v}>
                  <label className="block text-xs text-slate-500 mb-0.5 font-mono">
                    {`{{${v}}}`}
                  </label>
                  <input
                    value={variableValues[v] || ""}
                    onChange={(e) =>
                      setVariableValues((prev) => ({
                        ...prev,
                        [v]: e.target.value,
                      }))
                    }
                    placeholder={`输入 ${v} 的值...`}
                    className="w-full px-2.5 py-1.5 rounded-md border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400"
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Model Selection */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs font-medium text-slate-600">
              对比模型
            </label>
            <button
              onClick={addModel}
              className="flex items-center gap-0.5 text-xs text-indigo-500 hover:text-indigo-700"
            >
              <Plus className="w-3 h-3" />
              添加
            </button>
          </div>
          <div className="space-y-2">
            {selectedModels.map((sel, idx) => (
              <div key={idx} className="flex gap-1.5 items-center">
                <select
                  value={sel.providerId}
                  onChange={(e) => {
                    const p = providers.find((p) => p.id === e.target.value);
                    setSelectedModels((prev) =>
                      prev.map((m, i) =>
                        i === idx
                          ? {
                              providerId: e.target.value,
                              model: p?.models[0] || "",
                            }
                          : m,
                      ),
                    );
                  }}
                  className="flex-1 px-2 py-1.5 rounded-md border border-slate-200 text-xs bg-white focus:outline-none"
                >
                  {providers.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
                <select
                  value={sel.model}
                  onChange={(e) =>
                    setSelectedModels((prev) =>
                      prev.map((m, i) =>
                        i === idx ? { ...m, model: e.target.value } : m,
                      ),
                    )
                  }
                  className="flex-1 px-2 py-1.5 rounded-md border border-slate-200 text-xs bg-white focus:outline-none"
                >
                  {(
                    providers.find((p) => p.id === sel.providerId)?.models || []
                  ).map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
                {selectedModels.length > 1 && (
                  <button
                    onClick={() => removeModel(idx)}
                    className="p-1 text-slate-400 hover:text-red-500"
                  >
                    <Minus className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Run Button */}
        <button
          onClick={handleTest}
          disabled={testing || selectedModels.length === 0}
          className="w-full flex items-center justify-center gap-2 py-2 rounded-lg bg-emerald-500 text-white text-sm font-medium hover:bg-emerald-600 transition-colors disabled:opacity-50"
        >
          {testing ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          {testing ? "测试中..." : "运行测试"}
        </button>

        {/* Results */}
        {results && (
          <div className="space-y-3">
            {/* Rendered Prompts */}
            <div className="bg-white rounded-lg p-3 border border-slate-200">
              <p className="text-xs font-medium text-slate-600 mb-1">
                渲染后的 User Prompt
              </p>
              <pre className="text-xs text-slate-700 font-mono whitespace-pre-wrap bg-slate-50 p-2 rounded">
                {results.rendered_user_prompt}
              </pre>
            </div>

            {/* Model Results */}
            {results.results.map((r, i) => (
              <div
                key={i}
                className={`bg-white rounded-lg p-3 border ${
                  r.error ? "border-red-200" : "border-slate-200"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-slate-700">
                    {r.model}
                  </span>
                  {!r.error && (
                    <span className="text-xs text-slate-400">
                      {r.latency_ms}ms · {r.input_tokens}+{r.output_tokens}{" "}
                      tokens
                    </span>
                  )}
                </div>
                {r.error ? (
                  <p className="text-xs text-red-500">❌ {r.error}</p>
                ) : (
                  <pre className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
                    {r.response}
                  </pre>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
