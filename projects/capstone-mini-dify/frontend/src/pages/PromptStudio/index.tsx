import { PenTool, Plus } from "lucide-react";

export default function PromptStudioPage() {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">✏️ Prompt 工坊</h1>
          <p className="text-sm text-slate-500 mt-1">
            创建和管理 Prompt 模板，支持变量注入和多模型测试
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors">
          <Plus className="w-4 h-4" />
          新建模板
        </button>
      </div>

      <div className="text-center py-16 text-slate-400">
        <PenTool className="w-12 h-12 mx-auto mb-3 opacity-50" />
        <p>暂无 Prompt 模板</p>
        <p className="text-sm mt-1">点击"新建模板"创建第一个 Prompt</p>
      </div>
    </div>
  );
}
