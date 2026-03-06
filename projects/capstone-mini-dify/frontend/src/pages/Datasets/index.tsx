import { Database, Plus } from "lucide-react";

export default function DatasetsPage() {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">📚 知识库</h1>
          <p className="text-sm text-slate-500 mt-1">
            管理文档知识库，支持向量检索和 RAG 问答
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors">
          <Plus className="w-4 h-4" />
          创建知识库
        </button>
      </div>
      <div className="text-center py-16 text-slate-400">
        <Database className="w-12 h-12 mx-auto mb-3 opacity-50" />
        <p>暂无知识库</p>
        <p className="text-sm mt-1">点击"创建知识库"开始</p>
      </div>
    </div>
  );
}
