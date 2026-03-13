import { useState, useEffect } from "react";
import { GitBranch, Plus, Trash2, Edit3, Play, Clock, X } from "lucide-react";
import { workflowApi, providerApi } from "../../services/api";
import WorkflowEditor from "./Editor";

interface Workflow {
  id: string;
  name: string;
  description: string | null;
  graph_data: { nodes?: any[]; edges?: any[] };
  status: string;
  created_at: string;
  updated_at: string;
}

export default function WorkflowPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", description: "" });
  const [providers, setProviders] = useState<any[]>([]);

  const loadWorkflows = async () => {
    try {
      const data: any = await workflowApi.list();
      setWorkflows(data);
    } catch {
      /* empty */
    } finally {
      setLoading(false);
    }
  };

  const loadProviders = async () => {
    try {
      const data: any = await providerApi.list();
      setProviders(data);
    } catch {
      /* empty */
    }
  };

  useEffect(() => {
    loadWorkflows();
    loadProviders();
  }, []);

  const handleCreate = async () => {
    if (!form.name.trim()) return;
    try {
      await workflowApi.create({
        name: form.name,
        description: form.description || null,
        graph_data: {
          nodes: [
            {
              id: "start_1",
              type: "start",
              position: { x: 100, y: 200 },
              config: {},
            },
            {
              id: "end_1",
              type: "end",
              position: { x: 600, y: 200 },
              config: {},
            },
          ],
          edges: [{ source: "start_1", target: "end_1" }],
        },
      });
      setForm({ name: "", description: "" });
      setShowCreate(false);
      loadWorkflows();
    } catch {
      /* empty */
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("确定删除此工作流？")) return;
    try {
      await workflowApi.delete(id);
      loadWorkflows();
    } catch {
      /* empty */
    }
  };

  // If editing a workflow, show the editor
  if (editingId) {
    return (
      <WorkflowEditor
        workflowId={editingId}
        providers={providers}
        onBack={() => {
          setEditingId(null);
          loadWorkflows();
        }}
      />
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">🔀 工作流</h1>
          <p className="text-sm text-slate-500 mt-1">
            可视化拖拽编排 LLM 工作流
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors"
        >
          <Plus className="w-4 h-4" />
          新建工作流
        </button>
      </div>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">新建工作流</h2>
              <button
                onClick={() => setShowCreate(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  名称
                </label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  placeholder="输入工作流名称"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  描述
                </label>
                <textarea
                  value={form.description}
                  onChange={(e) =>
                    setForm({ ...form, description: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  placeholder="输入工作流描述（可选）"
                  rows={3}
                />
              </div>
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setShowCreate(false)}
                  className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  取消
                </button>
                <button
                  onClick={handleCreate}
                  className="px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors"
                >
                  创建
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Workflow List */}
      {loading ? (
        <div className="text-center py-16 text-slate-400">加载中...</div>
      ) : workflows.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <GitBranch className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无工作流</p>
          <p className="text-sm mt-1">
            点击&quot;新建工作流&quot;创建第一个工作流
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {workflows.map((wf) => (
            <div
              key={wf.id}
              className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow cursor-pointer group"
              onClick={() => setEditingId(wf.id)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <GitBranch className="w-5 h-5 text-indigo-500" />
                  <h3 className="font-semibold text-slate-800">{wf.name}</h3>
                </div>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full ${
                    wf.status === "published"
                      ? "bg-emerald-100 text-emerald-700"
                      : "bg-slate-100 text-slate-600"
                  }`}
                >
                  {wf.status === "published" ? "已发布" : "草稿"}
                </span>
              </div>
              {wf.description && (
                <p className="text-sm text-slate-500 mb-3 line-clamp-2">
                  {wf.description}
                </p>
              )}
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="flex items-center gap-1">
                  <Play className="w-3 h-3" />
                  {wf.graph_data?.nodes?.length || 0} 个节点
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {new Date(wf.updated_at).toLocaleDateString()}
                </span>
              </div>
              {/* Actions */}
              <div className="flex gap-2 mt-3 pt-3 border-t border-slate-100 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditingId(wf.id);
                  }}
                  className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-700"
                >
                  <Edit3 className="w-3 h-3" />
                  编辑
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(wf.id);
                  }}
                  className="flex items-center gap-1 text-xs text-red-500 hover:text-red-600"
                >
                  <Trash2 className="w-3 h-3" />
                  删除
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
