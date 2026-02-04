import React from "react";
import { clsx } from "clsx";
import { AlertTriangle, AlertCircle, Info } from "lucide-react";

export interface SafetyBannerProps {
  variant?: "warning" | "emergency" | "info";
  children: React.ReactNode;
  className?: string;
  onClose?: () => void;
}

const icons = {
  warning: AlertTriangle,
  emergency: AlertCircle,
  info: Info,
};

export const SafetyBanner: React.FC<SafetyBannerProps> = ({
  variant = "warning",
  children,
  className,
  onClose,
}) => {
  const Icon = icons[variant];

  const variantStyles = {
    warning:
      "bg-gradient-to-r from-amber-50 to-yellow-50 border-yellow-300 text-amber-800",
    emergency:
      "bg-gradient-to-r from-red-50 to-rose-50 border-red-300 text-red-800",
    info: "bg-gradient-to-r from-blue-50 to-sky-50 border-sky-300 text-sky-800",
  };

  return (
    <div
      className={clsx(
        "flex items-center gap-2 px-4 py-3 rounded-lg border",
        variantStyles[variant],
        className,
      )}
      role="alert"
    >
      <Icon className="w-5 h-5 flex-shrink-0" />
      <span className="text-sm font-medium flex-1">{children}</span>
      {onClose && (
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-black/5 transition-colors"
          aria-label="关闭"
        >
          ×
        </button>
      )}
    </div>
  );
};

SafetyBanner.displayName = "SafetyBanner";
