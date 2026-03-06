import { BarChart3, TrendingUp, Clock, Coins } from "lucide-react";

export default function AnalyticsPage() {
  const stats = [
    { icon: BarChart3, label: "总调用次数", value: "0", color: "indigo" },
    { icon: TrendingUp, label: "今日调用", value: "0", color: "emerald" },
    { icon: Clock, label: "平均延迟", value: "0ms", color: "amber" },
    { icon: Coins, label: "总 Token 消耗", value: "0", color: "purple" },
  ];

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-slate-800 mb-6">📊 监控面板</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat) => (
          <div key={stat.label} className="card p-5">
            <div className="flex items-center gap-3 mb-2">
              <div
                className={`w-9 h-9 rounded-lg bg-${stat.color}-50 flex items-center justify-center`}
              >
                <stat.icon className={`w-5 h-5 text-${stat.color}-500`} />
              </div>
              <span className="text-sm text-slate-500">{stat.label}</span>
            </div>
            <p className="text-2xl font-bold text-slate-800">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="card p-6">
        <h2 className="font-semibold text-slate-800 mb-4">最近对话日志</h2>
        <div className="text-center py-8 text-slate-400">
          <p>暂无数据</p>
          <p className="text-sm mt-1">当应用开始使用后，日志将显示在这里</p>
        </div>
      </div>
    </div>
  );
}
