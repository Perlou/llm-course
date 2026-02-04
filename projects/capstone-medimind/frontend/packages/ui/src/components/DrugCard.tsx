import React from "react";
import { clsx } from "clsx";
import { Pill, AlertTriangle, ShieldCheck } from "lucide-react";

export interface DrugCardProps {
  id: string;
  name: string;
  genericName?: string;
  category?: string;
  isOtc?: boolean;
  indications?: string;
  onClick?: () => void;
  className?: string;
}

export const DrugCard: React.FC<DrugCardProps> = ({
  name,
  genericName,
  category,
  isOtc = true,
  indications,
  onClick,
  className,
}) => {
  return (
    <div
      className={clsx(
        "bg-white border border-border rounded-xl p-4 cursor-pointer",
        "hover:border-medical-blue hover:shadow-md transition-all",
        className,
      )}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-medical-green/20 to-emerald-100 flex items-center justify-center">
          <Pill className="w-5 h-5 text-medical-green" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-text-primary truncate">{name}</h3>
            <span
              className={clsx(
                "text-xs px-2 py-0.5 rounded-full",
                isOtc
                  ? "bg-medical-green/10 text-medical-green"
                  : "bg-alert-warning/10 text-alert-warning",
              )}
            >
              {isOtc ? "OTC" : "处方药"}
            </span>
          </div>

          {genericName && (
            <p className="text-sm text-text-secondary mt-0.5">{genericName}</p>
          )}

          {category && (
            <span className="inline-block text-xs text-text-muted bg-slate-100 px-2 py-0.5 rounded mt-1">
              {category}
            </span>
          )}

          {indications && (
            <p className="text-sm text-text-secondary mt-2 line-clamp-2">
              {indications}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

DrugCard.displayName = "DrugCard";
