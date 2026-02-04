import { Link, useLocation } from "react-router-dom";
import { clsx } from "clsx";
import { Home, MessageCircle, Pill, FileText, Stethoscope } from "lucide-react";

interface BottomNavProps {
  className?: string;
}

const navItems = [
  { to: "/", icon: Home, label: "首页" },
  { to: "/health", icon: MessageCircle, label: "问答" },
  { to: "/drug", icon: Pill, label: "药品" },
  { to: "/report", icon: FileText, label: "报告" },
  { to: "/triage", icon: Stethoscope, label: "导诊" },
];

export default function BottomNav({ className }: BottomNavProps) {
  const location = useLocation();

  return (
    <nav
      className={clsx(
        "fixed bottom-0 left-0 right-0 bg-white border-t border-border safe-area-inset-bottom",
        className,
      )}
    >
      <div className="flex items-center justify-around py-2 pb-safe">
        {navItems.map(({ to, icon: Icon, label }) => {
          const isActive = location.pathname === to;
          return (
            <Link
              key={to}
              to={to}
              className={clsx(
                "flex flex-col items-center gap-0.5 px-3 py-1",
                isActive ? "text-medical-blue" : "text-text-muted",
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="text-xs">{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
