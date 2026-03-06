import { GitBranch, Plus } from "lucide-react";

export default function WorkflowPage() {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">🔀 工作流</h1>
          <p className="text-sm text-slate-500 mt-1">
            可视化拖拽编排 LLM 工作流
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors">
          <Plus className="w-4 h-4" />
          新建工作流
        </button>
      </div>
      <div className="text-center py-16 text-slate-400">
        <GitBranch className="w-12 h-12 mx-auto mb-3 opacity-50" />
        <p>暂无工作流</p>
        <p className="text-sm mt-1">点击"新建工作流"创建第一个工作流</p>
      </div>
    </div>
  );
}
