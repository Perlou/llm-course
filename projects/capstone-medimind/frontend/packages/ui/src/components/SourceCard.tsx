import React from "react";
import { clsx } from "clsx";
import { BookOpen, ExternalLink } from "lucide-react";

export interface SourceCardProps {
  title: string;
  source?: string;
  score?: number;
  onClick?: () => void;
  className?: string;
}

export const SourceCard: React.FC<SourceCardProps> = ({
  title,
  source,
  score,
  onClick,
  className,
}) => {
  return (
    <div
      className={clsx(
        "bg-slate-50 border-l-3 border-l-medical-blue rounded-r-lg px-3 py-2 cursor-pointer",
        "hover:bg-slate-100 transition-colors",
        className,
      )}
      onClick={onClick}
      style={{ borderLeftWidth: "3px" }}
    >
      <div className="flex items-start gap-2">
        <BookOpen className="w-4 h-4 text-medical-blue flex-shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-medical-blue truncate">
            {title}
          </div>
          {source && (
            <div className="text-xs text-text-muted mt-0.5 flex items-center gap-1">
              <span className="truncate">{source}</span>
              <ExternalLink className="w-3 h-3 flex-shrink-0" />
            </div>
          )}
        </div>
        {score !== undefined && (
          <span className="text-xs text-text-muted bg-white px-1.5 py-0.5 rounded">
            {Math.round(score * 100)}%
          </span>
        )}
      </div>
    </div>
  );
};

SourceCard.displayName = "SourceCard";
