import { useState, useEffect, useCallback } from "react";
import {
  Cpu,
  Plus,
  Trash2,
  Edit,
  RefreshCw,
  CheckCircle,
  XCircle,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { providerApi } from "../../services/api";
import ProviderModal from "./ProviderModal";
import ChatTest from "./ChatTest";

interface Provider {
  id: string;
  name: string;
  provider_type: string;
  base_url: string | null;
  models: string[];
  config: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface HealthStatus {
  status: "healthy" | "unhealthy" | "checking" | "unknown";
  latency_ms?: number;
  error?: string;
}

const PROVIDER_ICONS: Record<string, string> = {
  openai: "🟢",
  anthropic: "🟠",
  google: "🔵",
  ollama: "🦙",
};

export default function ModelHubPage() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProvider, setEditingProvider] = useState<Provider | null>(null);
  const [healthStatuses, setHealthStatuses] = useState<
    Record<string, HealthStatus>
  >({});
  const [chatProvider, setChatProvider] = useState<Provider | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const fetchProviders = useCallback(async () => {
    try {
      setLoading(true);
      const data = await providerApi.list();
      setProviders(data as unknown as Provider[]);
    } catch (err) {
      console.error("Failed to fetch providers", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProviders();
  }, [fetchProviders]);

  const handleHealthCheck = async (provider: Provider) => {
    setHealthStatuses((prev) => ({
      ...prev,
      [provider.id]: { status: "checking" },
    }));
    try {
      const result = (await providerApi.healthCheck(
        provider.id,
      )) as unknown as HealthStatus;
      setHealthStatuses((prev) => ({
        ...prev,
        [provider.id]: result,
      }));
    } catch {
      setHealthStatuses((prev) => ({
        ...prev,
        [provider.id]: { status: "unhealthy", error: "请求失败" },
      }));
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await providerApi.delete(id);
      setDeleteConfirm(null);
      fetchProviders();
    } catch (err) {
      console.error("Failed to delete provider", err);
    }
  };

  const handleSave = async () => {
    setModalOpen(false);
    setEditingProvider(null);
    fetchProviders();
  };

  const getStatusBadge = (id: string) => {
    const status = healthStatuses[id];
    if (!status || status.status === "unknown") {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-slate-100 text-slate-500">
          <AlertCircle className="w-3 h-3" />
          未检测
        </span>
      );
    }
    if (status.status === "checking") {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-blue-50 text-blue-500">
          <Loader2 className="w-3 h-3 animate-spin" />
          检测中
        </span>
      );
    }
    if (status.status === "healthy") {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-emerald-50 text-emerald-600">
          <CheckCircle className="w-3 h-3" />
          连接正常 · {status.latency_ms}ms
        </span>
      );
    }
    return (
      <span
        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-red-50 text-red-500 cursor-help"
        title={status.error}
      >
        <XCircle className="w-3 h-3" />
        连接失败
      </span>
    );
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">🔌 模型管理</h1>
          <p className="text-sm text-slate-500 mt-1">
            统一管理 LLM 供应商和模型配置
          </p>
        </div>
        <button
          onClick={() => {
            setEditingProvider(null);
            setModalOpen(true);
          }}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          添加供应商
        </button>
      </div>

      {/* Provider Cards */}
      {loading ? (
        <div className="flex items-center justify-center py-20 text-slate-400">
          <Loader2 className="w-6 h-6 animate-spin mr-2" />
          加载中...
        </div>
      ) : providers.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          <Cpu className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无模型供应商</p>
          <p className="text-sm mt-1">点击"添加供应商"开始配置</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {providers.map((provider) => (
            <div
              key={provider.id}
              className="card p-5 group relative hover:shadow-md transition-all duration-200"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center text-xl">
                    {PROVIDER_ICONS[provider.provider_type] || "🤖"}
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800">
                      {provider.name}
                    </h3>
                    <span className="text-xs text-slate-500 capitalize">
                      {provider.provider_type}
                    </span>
                  </div>
                </div>
                {/* Actions */}
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => handleHealthCheck(provider)}
                    className="p-1.5 rounded-md hover:bg-slate-100 text-slate-400 hover:text-blue-500 transition-colors"
                    title="健康检查"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => {
                      setEditingProvider(provider);
                      setModalOpen(true);
                    }}
                    className="p-1.5 rounded-md hover:bg-slate-100 text-slate-400 hover:text-indigo-500 transition-colors"
                    title="编辑"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setDeleteConfirm(provider.id)}
                    className="p-1.5 rounded-md hover:bg-slate-100 text-slate-400 hover:text-red-500 transition-colors"
                    title="删除"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Info */}
              <div className="flex items-center gap-2 flex-wrap">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-slate-100 text-slate-600">
                  {provider.models.length} 模型
                </span>
                {getStatusBadge(provider.id)}
              </div>

              {/* Models list */}
              {provider.models.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1">
                  {provider.models.slice(0, 4).map((model) => (
                    <span
                      key={model}
                      className="text-xs px-2 py-0.5 rounded bg-indigo-50 text-indigo-600"
                    >
                      {model}
                    </span>
                  ))}
                  {provider.models.length > 4 && (
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-50 text-slate-500">
                      +{provider.models.length - 4}
                    </span>
                  )}
                </div>
              )}

              {/* Chat test button */}
              <button
                onClick={() => setChatProvider(provider)}
                className="mt-3 w-full text-sm py-1.5 rounded-md border border-slate-200 text-slate-500 hover:border-indigo-300 hover:text-indigo-500 hover:bg-indigo-50/50 transition-colors"
              >
                对话测试
              </button>

              {/* Delete confirm overlay */}
              {deleteConfirm === provider.id && (
                <div className="absolute inset-0 bg-white/95 rounded-xl flex flex-col items-center justify-center gap-3 backdrop-blur-sm z-10">
                  <p className="text-sm text-slate-600">
                    确定删除 <strong>{provider.name}</strong>？
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setDeleteConfirm(null)}
                      className="px-3 py-1.5 text-sm rounded-md border border-slate-300 text-slate-600 hover:bg-slate-50"
                    >
                      取消
                    </button>
                    <button
                      onClick={() => handleDelete(provider.id)}
                      className="px-3 py-1.5 text-sm rounded-md bg-red-500 text-white hover:bg-red-600"
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

      {/* Provider Modal */}
      {modalOpen && (
        <ProviderModal
          provider={editingProvider}
          onClose={() => {
            setModalOpen(false);
            setEditingProvider(null);
          }}
          onSave={handleSave}
        />
      )}

      {/* Chat Test Panel */}
      {chatProvider && (
        <ChatTest
          provider={chatProvider}
          onClose={() => setChatProvider(null)}
        />
      )}
    </div>
  );
}
