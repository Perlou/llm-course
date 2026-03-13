import { useState, useEffect } from "react";
import {
  ArrowLeft,
  Key,
  Plus,
  Trash2,
  Copy,
  Check,
  Globe,
  Shield,
  Code,
} from "lucide-react";
import { appApi } from "../../services/api";

interface AppData {
  id: string;
  name: string;
  description: string | null;
  app_type: string;
  config: Record<string, unknown>;
  is_published: boolean;
}

interface ApiKeyItem {
  id: string;
  prefix: string;
  name: string;
  is_active: boolean;
  last_used: string | null;
  created_at: string;
}

interface AppDetailProps {
  appId: string;
  onBack: () => void;
}

export default function AppDetail({ appId, onBack }: AppDetailProps) {
  const [app, setApp] = useState<AppData | null>(null);
  const [apiKeys, setApiKeys] = useState<ApiKeyItem[]>([]);
  const [newKey, setNewKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [keyName, setKeyName] = useState("default");
  const [publishing, setPublishing] = useState(false);

  const loadApp = async () => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const data: any = await appApi.get(appId);
      setApp(data);
    } catch {
      /* empty */
    }
  };

  const loadApiKeys = async () => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const data: any = await appApi.listApiKeys(appId);
      setApiKeys(data);
    } catch {
      /* empty */
    }
  };

  useEffect(() => {
    loadApp();
    loadApiKeys();
  }, [appId]);

  const handlePublish = async () => {
    if (!app) return;
    setPublishing(true);
    try {
      if (app.is_published) {
        await appApi.unpublish(appId);
      } else {
        await appApi.publish(appId);
      }
      loadApp();
    } catch {
      /* empty */
    } finally {
      setPublishing(false);
    }
  };

  const handleCreateKey = async () => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const data: any = await appApi.createApiKey(appId, keyName);
      setNewKey(data.key);
      setKeyName("default");
      loadApiKeys();
    } catch {
      /* empty */
    }
  };

  const handleDeleteKey = async (keyId: string) => {
    if (!confirm("确定删除此 API Key？")) return;
    try {
      await appApi.deleteApiKey(appId, keyId);
      loadApiKeys();
    } catch {
      /* empty */
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!app) return <div className="p-6 text-slate-400">加载中...</div>;

  // Build gateway endpoint based on app type
  const gatewayEndpoint =
    app.app_type === "chatbot"
      ? "/api/v1/gateway/chat"
      : app.app_type === "completion"
        ? "/api/v1/gateway/completion"
        : "/api/v1/gateway/workflow";

  const curlExample =
    app.app_type === "workflow"
      ? `curl -X POST http://localhost:8000${gatewayEndpoint} \\
  -H "Authorization: Bearer <YOUR_API_KEY>" \\
  -H "Content-Type: application/json" \\
  -d '{"inputs": {"user_message": "你好"}}'`
      : app.app_type === "completion"
        ? `curl -X POST http://localhost:8000${gatewayEndpoint} \\
  -H "Authorization: Bearer <YOUR_API_KEY>" \\
  -H "Content-Type: application/json" \\
  -d '{"inputs": {"text": "你好"}}'`
        : `curl -X POST http://localhost:8000${gatewayEndpoint} \\
  -H "Authorization: Bearer <YOUR_API_KEY>" \\
  -H "Content-Type: application/json" \\
  -d '{"message": "你好"}'`;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <button onClick={onBack} className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors">
            <ArrowLeft className="w-5 h-5 text-slate-600" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-slate-800">{app.name}</h1>
            <p className="text-sm text-slate-500">
              {app.app_type === "chatbot" ? "💬 Chatbot" : app.app_type === "completion" ? "✍️ Completion" : "🔀 Workflow"}
              {app.description && ` · ${app.description}`}
            </p>
          </div>
        </div>
        <button
          onClick={handlePublish}
          disabled={publishing}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors text-sm ${
            app.is_published
              ? "bg-slate-100 text-slate-700 hover:bg-slate-200"
              : "bg-emerald-500 text-white hover:bg-emerald-600"
          }`}
        >
          <Globe className="w-4 h-4" />
          {app.is_published ? "取消发布" : "发布应用"}
        </button>
      </div>

      {/* Status */}
      <div className={`mb-6 p-4 rounded-lg border ${
        app.is_published
          ? "bg-emerald-50 border-emerald-200"
          : "bg-amber-50 border-amber-200"
      }`}>
        <div className="flex items-center gap-2">
          <Shield className={`w-4 h-4 ${app.is_published ? "text-emerald-600" : "text-amber-600"}`} />
          <span className={`text-sm font-medium ${app.is_published ? "text-emerald-700" : "text-amber-700"}`}>
            {app.is_published
              ? "应用已发布，可通过 API Key 调用"
              : "应用为草稿状态，请发布后使用 API Key 调用"}
          </span>
        </div>
      </div>

      {/* API Keys Section */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Key className="w-5 h-5 text-indigo-500" />
            <h2 className="font-semibold text-slate-800">API Keys</h2>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={keyName}
              onChange={(e) => setKeyName(e.target.value)}
              className="px-2.5 py-1.5 text-sm border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 outline-none w-32"
              placeholder="Key 名称"
            />
            <button
              onClick={handleCreateKey}
              className="flex items-center gap-1 px-3 py-1.5 bg-indigo-500 text-white rounded-md hover:bg-indigo-600 transition-colors text-sm"
            >
              <Plus className="w-3.5 h-3.5" />
              生成
            </button>
          </div>
        </div>

        {/* New Key Alert */}
        {newKey && (
          <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-xs text-amber-700 font-medium mb-2">
              ⚠️ 请保存此 API Key，它不会再次显示！
            </p>
            <div className="flex items-center gap-2">
              <code className="flex-1 text-xs bg-white px-2 py-1.5 rounded border border-amber-200 font-mono break-all">
                {newKey}
              </code>
              <button
                onClick={() => handleCopy(newKey)}
                className="p-1.5 hover:bg-amber-100 rounded transition-colors"
              >
                {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4 text-amber-600" />}
              </button>
            </div>
          </div>
        )}

        {/* Key List */}
        {apiKeys.length === 0 ? (
          <p className="text-sm text-slate-400 text-center py-4">暂无 API Key</p>
        ) : (
          <div className="space-y-2">
            {apiKeys.map((key) => (
              <div
                key={key.id}
                className="flex items-center justify-between p-3 bg-slate-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <Key className="w-4 h-4 text-slate-400" />
                  <div>
                    <div className="flex items-center gap-2">
                      <code className="text-sm font-mono text-slate-700">{key.prefix}...***</code>
                      <span className="text-xs text-slate-500">({key.name})</span>
                    </div>
                    <div className="text-xs text-slate-400 mt-0.5">
                      {key.last_used
                        ? `最后使用: ${new Date(key.last_used).toLocaleString()}`
                        : "未使用"}
                      {" · "}
                      创建于 {new Date(key.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs px-1.5 py-0.5 rounded ${
                      key.is_active ? "bg-emerald-100 text-emerald-600" : "bg-red-100 text-red-600"
                    }`}
                  >
                    {key.is_active ? "启用" : "禁用"}
                  </span>
                  <button
                    onClick={() => handleDeleteKey(key.id)}
                    className="p-1 hover:bg-slate-200 rounded transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5 text-red-400" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* API Usage Example */}
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <div className="flex items-center gap-2 mb-4">
          <Code className="w-5 h-5 text-slate-500" />
          <h2 className="font-semibold text-slate-800">调用示例</h2>
        </div>
        <div className="relative">
          <pre className="bg-slate-900 text-slate-100 text-xs p-4 rounded-lg overflow-x-auto font-mono leading-relaxed">
            {curlExample}
          </pre>
          <button
            onClick={() => handleCopy(curlExample)}
            className="absolute top-2 right-2 p-1.5 bg-slate-700 hover:bg-slate-600 rounded transition-colors"
          >
            <Copy className="w-3.5 h-3.5 text-slate-300" />
          </button>
        </div>
        <p className="text-xs text-slate-400 mt-2">
          将 {"<YOUR_API_KEY>"} 替换为上方生成的 API Key
        </p>
      </div>
    </div>
  );
}
