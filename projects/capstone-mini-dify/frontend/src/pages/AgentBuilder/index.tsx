import { useState, useEffect, useCallback } from "react";
import {
  Bot,
  Plus,
  Trash2,
  Loader2,
  Settings,
  Play,
} from "lucide-react";
import { agentApi, providerApi } from "../../services/api";
import AgentConfig from "./AgentConfig";
import Playground from "./Playground";

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
  created_at: string;
  updated_at: string;
}

interface ProviderItem {
  id: string;
  name: string;
  provider_type: string;
  models: string[];
}

export default function AgentBuilderPage() {
  const [agents, setAgents] = useState<AgentItem[]>([]);
  const [providers, setProviders] = useState<ProviderItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [configAgent, setConfigAgent] = useState<AgentItem | null>(null);
  const [isNew, setIsNew] = useState(false);
  const [playAgent, setPlayAgent] = useState<AgentItem | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const fetchAgents = useCallback(async () => {
    try {
      setLoading(true);
      const [agentData, providerData] = await Promise.all([
        agentApi.list(),
        providerApi.list(),
      ]);
      setAgents(agentData as unknown as AgentItem[]);
      setProviders(providerData as unknown as ProviderItem[]);
    } catch (err) {
      console.error("Failed to fetch", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  const handleDelete = async (id: string) => {
    try {
      await agentApi.delete(id);
      setDeleteConfirm(null);
      fetchAgents();
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  const getProviderName = (pid: string | null) => {
    if (!pid) return "未配置";
    return providers.find((p) => p.id === pid)?.name || "未知";
  };

  // Playground 模式
  if (playAgent) {
    return (
      <Playground
        agent={playAgent}
        onBack={() => {
          setPlayAgent(null);
          fetchAgents();
        }}
      />
    );
  }

  // 配置模式
  if (configAgent || isNew) {
    return (
      <AgentConfig
        agent={configAgent}
        providers={providers}
        onSave={() => {
          setConfigAgent(null);
          setIsNew(false);
          fetchAgents();
        }}
        onCancel={() => {
          setConfigAgent(null);
          setIsNew(false);
        }}
      />
    );
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">🤖 Agent 构建</h1>
          <p className="text-sm text-slate-500 mt-1">
            创建和管理智能体，配置工具和 Playground 测试
          </p>
        </div>
        <button
          onClick={() => {
            setConfigAgent(null);
            setIsNew(true);
          }}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          新建 Agent
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20 text-slate-400">
          <Loader2 className="w-6 h-6 animate-spin mr-2" />
          加载中...
        </div>
      ) : agents.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          <Bot className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无 Agent</p>
          <p className="text-sm mt-1">点击 "新建 Agent" 创建第一个智能体</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className="card p-5 group relative hover:shadow-md transition-all"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-violet-50 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-violet-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800">
                      {agent.name}
                    </h3>
                    <span className="text-xs text-slate-400">
                      {agent.model_name}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => setPlayAgent(agent)}
                    className="p-1.5 rounded-md hover:bg-slate-100 text-slate-400 hover:text-green-500"
                    title="Playground"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setConfigAgent(agent)}
                    className="p-1.5 rounded-md hover:bg-slate-100 text-slate-400 hover:text-indigo-500"
                    title="配置"
                  >
                    <Settings className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setDeleteConfirm(agent.id)}
                    className="p-1.5 rounded-md hover:bg-slate-100 text-slate-400 hover:text-red-500"
                    title="删除"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {agent.description && (
                <p className="text-sm text-slate-500 line-clamp-2 mb-3">
                  {agent.description}
                </p>
              )}

              <div className="flex items-center gap-2 flex-wrap">
                <span className="px-2 py-0.5 rounded-full text-xs bg-violet-50 text-violet-600">
                  {agent.strategy}
                </span>
                <span className="px-2 py-0.5 rounded-full text-xs bg-blue-50 text-blue-600">
                  {getProviderName(agent.provider_id)}
                </span>
                {agent.dataset_ids.length > 0 && (
                  <span className="px-2 py-0.5 rounded-full text-xs bg-emerald-50 text-emerald-600">
                    {agent.dataset_ids.length} 知识库
                  </span>
                )}
              </div>

              {/* Delete confirm */}
              {deleteConfirm === agent.id && (
                <div className="absolute inset-0 bg-white/95 rounded-xl flex flex-col items-center justify-center gap-3 z-10">
                  <p className="text-sm text-slate-600">
                    确定删除 <strong>{agent.name}</strong>？
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setDeleteConfirm(null)}
                      className="px-3 py-1.5 text-sm rounded-md border border-slate-300 text-slate-600"
                    >
                      取消
                    </button>
                    <button
                      onClick={() => handleDelete(agent.id)}
                      className="px-3 py-1.5 text-sm rounded-md bg-red-500 text-white"
                    >
                      确认删除
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
