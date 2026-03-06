import { NavLink, useLocation } from "react-router-dom";
import {
  Cpu,
  PenTool,
  Database,
  Bot,
  GitBranch,
  AppWindow,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from "lucide-react";
import { useState } from "react";

const navItems = [
  { icon: Cpu, label: "模型管理", path: "/models" },
  { icon: PenTool, label: "Prompt 工坊", path: "/prompts" },
  { icon: Database, label: "知识库", path: "/datasets" },
  { icon: Bot, label: "Agent", path: "/agents" },
  { icon: GitBranch, label: "工作流", path: "/workflows" },
  { icon: AppWindow, label: "应用管理", path: "/apps" },
  { icon: BarChart3, label: "监控面板", path: "/analytics" },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <aside
      className={`flex flex-col h-full transition-all duration-300 ${
        collapsed ? "w-16" : "w-56"
      }`}
      style={{ backgroundColor: "var(--color-sidebar-bg)" }}
    >
      {/* Logo */}
      <div className="flex items-center gap-2 px-4 h-14 border-b border-white/10">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center flex-shrink-0">
          <Sparkles className="w-4 h-4 text-white" />
        </div>
        {!collapsed && (
          <span className="text-white font-semibold text-lg tracking-tight">
            Mini-Dify
          </span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-3 px-2 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = location.pathname.startsWith(item.path);
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "bg-indigo-500/20 text-indigo-300"
                  : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
              }`}
              title={collapsed ? item.label : undefined}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          );
        })}
      </nav>

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center h-10 border-t border-white/10 text-slate-500 hover:text-slate-300 transition-colors"
      >
        {collapsed ? (
          <ChevronRight className="w-4 h-4" />
        ) : (
          <ChevronLeft className="w-4 h-4" />
        )}
      </button>
    </aside>
  );
}
