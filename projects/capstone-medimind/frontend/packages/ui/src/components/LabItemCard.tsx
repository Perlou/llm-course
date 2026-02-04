import React from "react";
import { clsx } from "clsx";
import { CheckCircle, AlertCircle, ArrowUp, ArrowDown } from "lucide-react";

export type IndicatorStatus = "normal" | "high" | "low" | "critical";

export interface LabItemCardProps {
  name: string;
  value: string;
  unit?: string;
  referenceRange?: string;
  status: IndicatorStatus;
  explanation?: string;
  className?: string;
}

const statusConfig = {
  normal: {
    icon: CheckCircle,
    label: "正常",
    borderColor: "border-l-medical-green",
    bgColor: "bg-white",
    labelBg: "bg-medical-green/10 text-medical-green",
  },
  high: {
    icon: ArrowUp,
    label: "偏高",
    borderColor: "border-l-alert-danger",
    bgColor: "bg-red-50/50",
    labelBg: "bg-alert-danger/10 text-alert-danger",
  },
  low: {
    icon: ArrowDown,
    label: "偏低",
    borderColor: "border-l-alert-warning",
    bgColor: "bg-orange-50/50",
    labelBg: "bg-alert-warning/10 text-alert-warning",
  },
  critical: {
    icon: AlertCircle,
    label: "异常",
    borderColor: "border-l-alert-danger",
    bgColor: "bg-red-50",
    labelBg: "bg-alert-danger/10 text-alert-danger",
  },
};

export const LabItemCard: React.FC<LabItemCardProps> = ({
  name,
  value,
  unit,
  referenceRange,
  status,
  explanation,
  className,
}) => {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <div
      className={clsx(
        "rounded-xl border border-border p-4",
        config.borderColor,
        config.bgColor,
        className,
      )}
      style={{ borderLeftWidth: "4px" }}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-text-primary">{name}</h4>
        <span
          className={clsx(
            "text-xs px-2 py-1 rounded-full flex items-center gap-1",
            config.labelBg,
          )}
        >
          <Icon className="w-3 h-3" />
          {config.label}
        </span>
      </div>

      {/* Value */}
      <div className="mt-2 flex items-baseline gap-2">
        <span
          className={clsx(
            "text-2xl font-bold",
            status === "normal" ? "text-medical-green" : "text-alert-danger",
          )}
        >
          {value}
        </span>
        {unit && <span className="text-sm text-text-secondary">{unit}</span>}
      </div>

      {/* Reference Range */}
      {referenceRange && (
        <p className="text-sm text-text-muted mt-1">
          参考范围: {referenceRange}
        </p>
      )}

      {/* Explanation */}
      {explanation && (
        <div className="mt-3 pt-3 border-t border-border/50">
          <p className="text-sm text-text-secondary leading-relaxed">
            <span className="font-medium">解读说明: </span>
            {explanation}
          </p>
        </div>
      )}
    </div>
  );
};

LabItemCard.displayName = "LabItemCard";
