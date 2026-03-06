import { Cpu, Plus, Settings } from "lucide-react";

export default function ModelHubPage() {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">🔌 模型管理</h1>
          <p className="text-sm text-slate-500 mt-1">
            统一管理 LLM 供应商和模型配置
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors">
          <Plus className="w-4 h-4" />
          添加供应商
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {["OpenAI", "Anthropic", "Google", "Ollama"].map((name) => (
          <div key={name} className="card p-5 cursor-pointer group">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center">
                  <Cpu className="w-5 h-5 text-indigo-500" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-800">{name}</h3>
                  <span className="text-xs text-slate-500">未配置</span>
                </div>
              </div>
              <Settings className="w-4 h-4 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <div className="flex items-center gap-2 mt-2">
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-slate-100 text-slate-600">
                0 模型
              </span>
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-red-50 text-red-500">
                未连接
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
