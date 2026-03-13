import { useState, useEffect } from "react";
import {
  AppWindow,
  Plus,
  Trash2,
  MessageCircle,
  FileText,
  GitBranch,
  X,
  Clock,
} from "lucide-react";
import { appApi, agentApi, workflowApi } from "../../services/api";
import AppDetail from "./AppDetail";

interface AppItem {
  id: string;
  name: string;
  description: string | null;
  app_type: string;
  config: Record<string, unknown>;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

const TYPE_META: Record<string, { icon: typeof MessageCircle; label: string; color: string }> = {
  chatbot: { icon: MessageCircle, label: "Chatbot", color: "text-blue-500" },
  completion: { icon: FileText, label: "Completion", color: "text-purple-500" },
  workflow: { icon: GitBranch, label: "Workflow", color: "text-amber-500" },
};

export default function AppsPage() {
  const [apps, setApps] = useState<AppItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedAppId, setSelectedAppId] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: "",
    description: "",
    app_type: "chatbot" as string,
    agent_id: "",
    workflow_id: "",
    provider_id: "",
    model: "",
    system_prompt: "",
    prompt: "",
  });
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [agents, setAgents] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [workflows, setWorkflows] = useState<any[]>([]);

  const loadApps = async () => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const data: any = await appApi.list();
      setApps(data);
    } catch {
      /* empty */
    } finally {
      setLoading(false);
    }
  };

  const loadResources = async () => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const [a, w]: any = await Promise.all([agentApi.list(), workflowApi.list()]);
      setAgents(a || []);
      setWorkflows(w || []);
    } catch {
      /* empty */
    }
  };

  useEffect(() => {
    loadApps();
    loadResources();
  }, []);

  const handleCreate = async () => {
    if (!form.name.trim()) return;
    const config: Record<string, unknown> = {};
    if (form.app_type === "chatbot") {
      if (form.agent_id) config.agent_id = form.agent_id;
      config.system_prompt = form.system_prompt;
    } else if (form.app_type === "completion") {
      config.prompt = form.prompt;
      config.system_prompt = form.system_prompt;
    } else if (form.app_type === "workflow") {
      config.workflow_id = form.workflow_id;
    }

    try {
      await appApi.create({
        name: form.name,
        description: form.description || null,
        app_type: form.app_type,
        config,
      });
      setForm({
        name: "", description: "", app_type: "chatbot",
        agent_id: "", workflow_id: "", provider_id: "",
        model: "", system_prompt: "", prompt: "",
      });
      setShowCreate(false);
      loadApps();
    } catch {
      /* empty */
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("确定删除此应用？")) return;
    try {
      await appApi.delete(id);
      loadApps();
    } catch {
      /* empty */
    }
  };

  // If viewing app detail
  if (selectedAppId) {
    return (
      <AppDetail
        appId={selectedAppId}
        onBack={() => {
          setSelectedAppId(null);
          loadApps();
        }}
      />
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">📱 应用管理</h1>
          <p className="text-sm text-slate-500 mt-1">
            创建和管理 Chatbot、Completion、Workflow 应用
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors"
        >
          <Plus className="w-4 h-4" />
          创建应用
        </button>
      </div>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-lg shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">创建应用</h2>
              <button onClick={() => setShowCreate(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">名称</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  placeholder="应用名称"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">描述</label>
                <input
                  type="text"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  placeholder="应用描述（可选）"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">类型</label>
                <div className="flex gap-2">
                  {(["chatbot", "completion", "workflow"] as const).map((t) => {
                    const meta = TYPE_META[t];
                    const Icon = meta.icon;
                    return (
                      <button
                        key={t}
                        onClick={() => setForm({ ...form, app_type: t })}
                        className={`flex-1 flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg border-2 transition-colors text-sm ${
                          form.app_type === t
                            ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                            : "border-slate-200 hover:border-slate-300 text-slate-600"
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                        {meta.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Type-specific config */}
              {form.app_type === "chatbot" && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    关联 Agent（可选）
                  </label>
                  <select
                    value={form.agent_id}
                    onChange={(e) => setForm({ ...form, agent_id: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  >
                    <option value="">不关联 Agent（直接 LLM 对话）</option>
                    {agents.map((a: { id: string; name: string }) => (
                      <option key={a.id} value={a.id}>{a.name}</option>
                    ))}
                  </select>
                </div>
              )}
              {form.app_type === "workflow" && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    关联工作流
                  </label>
                  <select
                    value={form.workflow_id}
                    onChange={(e) => setForm({ ...form, workflow_id: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  >
                    <option value="">选择工作流</option>
                    {workflows.map((w: { id: string; name: string }) => (
                      <option key={w.id} value={w.id}>{w.name}</option>
                    ))}
                  </select>
                </div>
              )}

              <div className="flex gap-3 justify-end pt-2">
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

      {/* App List */}
      {loading ? (
        <div className="text-center py-16 text-slate-400">加载中...</div>
      ) : apps.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <AppWindow className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无应用</p>
          <p className="text-sm mt-1">点击&quot;创建应用&quot;开始</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {apps.map((app) => {
            const meta = TYPE_META[app.app_type] || TYPE_META.chatbot;
            const Icon = meta.icon;
            return (
              <div
                key={app.id}
                onClick={() => setSelectedAppId(app.id)}
                className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow cursor-pointer group"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Icon className={`w-5 h-5 ${meta.color}`} />
                    <h3 className="font-semibold text-slate-800">{app.name}</h3>
                  </div>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full ${
                      app.is_published
                        ? "bg-emerald-100 text-emerald-700"
                        : "bg-slate-100 text-slate-600"
                    }`}
                  >
                    {app.is_published ? "🟢 已发布" : "⚪ 草稿"}
                  </span>
                </div>
                {app.description && (
                  <p className="text-sm text-slate-500 mb-3 line-clamp-2">{app.description}</p>
                )}
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="px-2 py-0.5 bg-slate-50 rounded">{meta.label}</span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(app.updated_at).toLocaleDateString()}
                  </span>
                </div>
                {/* Actions */}
                <div className="flex gap-2 mt-3 pt-3 border-t border-slate-100 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(app.id);
                    }}
                    className="flex items-center gap-1 text-xs text-red-500 hover:text-red-600"
                  >
                    <Trash2 className="w-3 h-3" />
                    删除
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
