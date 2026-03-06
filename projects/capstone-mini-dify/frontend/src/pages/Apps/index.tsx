import { AppWindow, Plus } from "lucide-react";

export default function AppsPage() {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">📱 应用管理</h1>
          <p className="text-sm text-slate-500 mt-1">
            创建和管理 Chatbot、Completion、Workflow 应用
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors">
          <Plus className="w-4 h-4" />
          创建应用
        </button>
      </div>
      <div className="text-center py-16 text-slate-400">
        <AppWindow className="w-12 h-12 mx-auto mb-3 opacity-50" />
        <p>暂无应用</p>
        <p className="text-sm mt-1">点击"创建应用"开始</p>
      </div>
    </div>
  );
}
