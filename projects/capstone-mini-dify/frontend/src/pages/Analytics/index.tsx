import { useState, useEffect } from "react";
import {
  BarChart3,
  TrendingUp,
  Clock,
  Coins,
  RefreshCw,
  User,
  Bot,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { analyticsApi } from "../../services/api";

interface Stats {
  total_calls: number;
  today_calls: number;
  total_tokens: number;
  total_input_tokens: number;
  total_output_tokens: number;
  avg_latency_ms: number;
}

interface TrendItem {
  date: string;
  input_tokens: number;
  output_tokens: number;
  count: number;
}

interface LogItem {
  id: string;
  app_id: string;
  conversation_id: string;
  role: string;
  content: string;
  provider_name: string | null;
  model_name: string | null;
  input_tokens: number;
  output_tokens: number;
  latency_ms: number | null;
  created_at: string | null;
}

interface LogsResponse {
  total: number;
  page: number;
  page_size: number;
  items: LogItem[];
}

export default function AnalyticsPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [trend, setTrend] = useState<TrendItem[]>([]);
  const [logsData, setLogsData] = useState<LogsResponse | null>(null);
  const [page, setPage] = useState(1);
  const [refreshing, setRefreshing] = useState(false);

  const loadStats = async () => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const data: any = await analyticsApi.stats();
      setStats(data);
    } catch {
      /* empty */
    }
  };

  const loadTrend = async () => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const data: any = await analyticsApi.tokenTrend(7);
      setTrend(data);
    } catch {
      /* empty */
    }
  };

  const loadLogs = async (p: number) => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const data: any = await analyticsApi.logs(p, 15);
      setLogsData(data);
    } catch {
      /* empty */
    }
  };

  const refresh = async () => {
    setRefreshing(true);
    await Promise.all([loadStats(), loadTrend(), loadLogs(page)]);
    setRefreshing(false);
  };

  useEffect(() => {
    refresh();
  }, []);

  useEffect(() => {
    loadLogs(page);
  }, [page]);

  // Compute max for trend chart
  const maxTokens = Math.max(
    1,
    ...trend.map((t) => t.input_tokens + t.output_tokens)
  );

  const formatNumber = (n: number) => {
    if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
    if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
    return n.toString();
  };

  const totalPages = logsData ? Math.ceil(logsData.total / logsData.page_size) : 0;

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">📊 监控面板</h1>
          <p className="text-sm text-slate-500 mt-1">查看应用调用统计和对话日志</p>
        </div>
        <button
          onClick={refresh}
          disabled={refreshing}
          className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors text-sm text-slate-700"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
          刷新
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-9 h-9 rounded-lg bg-indigo-50 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-indigo-500" />
            </div>
            <span className="text-sm text-slate-500">总调用次数</span>
          </div>
          <p className="text-2xl font-bold text-slate-800">
            {stats ? formatNumber(stats.total_calls) : "—"}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-9 h-9 rounded-lg bg-emerald-50 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-emerald-500" />
            </div>
            <span className="text-sm text-slate-500">今日调用</span>
          </div>
          <p className="text-2xl font-bold text-slate-800">
            {stats ? formatNumber(stats.today_calls) : "—"}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-9 h-9 rounded-lg bg-amber-50 flex items-center justify-center">
              <Clock className="w-5 h-5 text-amber-500" />
            </div>
            <span className="text-sm text-slate-500">平均延迟</span>
          </div>
          <p className="text-2xl font-bold text-slate-800">
            {stats ? `${stats.avg_latency_ms}ms` : "—"}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-9 h-9 rounded-lg bg-purple-50 flex items-center justify-center">
              <Coins className="w-5 h-5 text-purple-500" />
            </div>
            <span className="text-sm text-slate-500">总 Token 消耗</span>
          </div>
          <p className="text-2xl font-bold text-slate-800">
            {stats ? formatNumber(stats.total_tokens) : "—"}
          </p>
          {stats && stats.total_tokens > 0 && (
            <p className="text-xs text-slate-400 mt-1">
              ↑ {formatNumber(stats.total_input_tokens)} / ↓ {formatNumber(stats.total_output_tokens)}
            </p>
          )}
        </div>
      </div>

      {/* Token Trend Chart */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6">
        <h2 className="font-semibold text-slate-800 mb-4">📈 最近 7 天 Token 趋势</h2>
        {trend.length === 0 ? (
          <div className="text-center py-8 text-slate-400 text-sm">暂无数据</div>
        ) : (
          <div className="flex items-end gap-2 h-40">
            {trend.map((item) => {
              const total = item.input_tokens + item.output_tokens;
              const height = maxTokens > 0 ? (total / maxTokens) * 100 : 0;
              const inputPct = total > 0 ? (item.input_tokens / total) * 100 : 50;
              return (
                <div key={item.date} className="flex-1 flex flex-col items-center gap-1">
                  <div className="text-[10px] text-slate-400 mb-1">
                    {total > 0 ? formatNumber(total) : ""}
                  </div>
                  <div
                    className="w-full rounded-t-md overflow-hidden flex flex-col justify-end"
                    style={{ height: `${Math.max(height, 2)}%`, minHeight: "4px" }}
                  >
                    <div
                      className="bg-indigo-400 w-full"
                      style={{ height: `${inputPct}%`, minHeight: "2px" }}
                    />
                    <div
                      className="bg-purple-400 w-full"
                      style={{ height: `${100 - inputPct}%`, minHeight: "2px" }}
                    />
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1">
                    {new Date(item.date).toLocaleDateString("zh-CN", { month: "numeric", day: "numeric" })}
                  </div>
                </div>
              );
            })}
          </div>
        )}
        <div className="flex items-center gap-4 mt-3 text-xs text-slate-400">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-sm bg-indigo-400" />
            Input Tokens
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-sm bg-purple-400" />
            Output Tokens
          </div>
        </div>
      </div>

      {/* Conversation Logs */}
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-slate-800">💬 对话日志</h2>
          {logsData && (
            <span className="text-xs text-slate-400">共 {logsData.total} 条</span>
          )}
        </div>

        {!logsData || logsData.items.length === 0 ? (
          <div className="text-center py-8 text-slate-400">
            <p>暂无数据</p>
            <p className="text-sm mt-1">当应用开始使用后，日志将显示在这里</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="text-left py-2 px-3 text-slate-500 font-medium">时间</th>
                    <th className="text-left py-2 px-3 text-slate-500 font-medium">角色</th>
                    <th className="text-left py-2 px-3 text-slate-500 font-medium">内容</th>
                    <th className="text-left py-2 px-3 text-slate-500 font-medium">模型</th>
                    <th className="text-right py-2 px-3 text-slate-500 font-medium">Token</th>
                    <th className="text-right py-2 px-3 text-slate-500 font-medium">延迟</th>
                  </tr>
                </thead>
                <tbody>
                  {logsData.items.map((log) => (
                    <tr key={log.id} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="py-2 px-3 text-xs text-slate-400 whitespace-nowrap">
                        {log.created_at
                          ? new Date(log.created_at).toLocaleString("zh-CN", {
                              month: "2-digit", day: "2-digit",
                              hour: "2-digit", minute: "2-digit",
                            })
                          : "—"}
                      </td>
                      <td className="py-2 px-3">
                        <span className={`inline-flex items-center gap-1 text-xs px-1.5 py-0.5 rounded ${
                          log.role === "user"
                            ? "bg-blue-50 text-blue-600"
                            : "bg-emerald-50 text-emerald-600"
                        }`}>
                          {log.role === "user"
                            ? <><User className="w-3 h-3" /> 用户</>
                            : <><Bot className="w-3 h-3" /> 助手</>}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-slate-700 max-w-xs truncate" title={log.content}>
                        {log.content}
                      </td>
                      <td className="py-2 px-3 text-xs text-slate-400">
                        {log.model_name || "—"}
                      </td>
                      <td className="py-2 px-3 text-right text-xs text-slate-500">
                        {log.input_tokens + log.output_tokens > 0
                          ? `${log.input_tokens}/${log.output_tokens}`
                          : "—"}
                      </td>
                      <td className="py-2 px-3 text-right text-xs text-slate-500">
                        {log.latency_ms ? `${log.latency_ms}ms` : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-4">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page <= 1}
                  className="p-1.5 hover:bg-slate-100 rounded disabled:opacity-30 transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="text-sm text-slate-500">
                  {page} / {totalPages}
                </span>
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page >= totalPages}
                  className="p-1.5 hover:bg-slate-100 rounded disabled:opacity-30 transition-colors"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
