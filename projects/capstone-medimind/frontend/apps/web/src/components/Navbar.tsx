import { Link, useLocation } from "react-router-dom";
import { clsx } from "clsx";
import { Heart, User } from "lucide-react";

export default function Navbar() {
  const location = useLocation();

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-border">
      <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-medical-blue to-medical-green flex items-center justify-center">
            <Heart className="w-4 h-4 text-white" fill="white" />
          </div>
          <span className="font-semibold text-text-primary">MediMind</span>
          <span className="text-xs text-text-muted hidden sm:inline">
            Health Assistant
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1">
          <NavLink to="/" label="首页" active={location.pathname === "/"} />
          <NavLink
            to="/health"
            label="健康问答"
            active={location.pathname === "/health"}
          />
          <NavLink
            to="/drug"
            label="药品查询"
            active={location.pathname === "/drug"}
          />
          <NavLink
            to="/report"
            label="报告解读"
            active={location.pathname === "/report"}
          />
          <NavLink
            to="/triage"
            label="智能导诊"
            active={location.pathname === "/triage"}
          />
        </nav>

        {/* User Menu */}
        <button className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-text-secondary hover:bg-slate-200 transition-colors">
          <User className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}

function NavLink({
  to,
  label,
  active,
}: {
  to: string;
  label: string;
  active: boolean;
}) {
  return (
    <Link
      to={to}
      className={clsx(
        "px-3 py-2 rounded-lg text-sm font-medium transition-colors",
        active
          ? "text-medical-blue bg-medical-blue/10"
          : "text-text-secondary hover:text-text-primary hover:bg-slate-100",
      )}
    >
      {label}
    </Link>
  );
}
