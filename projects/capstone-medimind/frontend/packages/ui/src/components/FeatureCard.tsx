import React from "react";
import { clsx } from "clsx";
import { ChevronRight } from "lucide-react";

export interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  titleEn?: string;
  description: string;
  color?: "blue" | "green" | "purple" | "orange";
  onClick?: () => void;
  className?: string;
}

const colorConfig = {
  blue: {
    bg: "bg-gradient-to-br from-sky-50 to-blue-50",
    iconBg: "bg-gradient-to-br from-medical-blue/20 to-sky-100",
    iconColor: "text-medical-blue",
  },
  green: {
    bg: "bg-gradient-to-br from-emerald-50 to-green-50",
    iconBg: "bg-gradient-to-br from-medical-green/20 to-emerald-100",
    iconColor: "text-medical-green",
  },
  purple: {
    bg: "bg-gradient-to-br from-violet-50 to-purple-50",
    iconBg: "bg-gradient-to-br from-medical-purple/20 to-violet-100",
    iconColor: "text-medical-purple",
  },
  orange: {
    bg: "bg-gradient-to-br from-orange-50 to-amber-50",
    iconBg: "bg-gradient-to-br from-alert-warning/20 to-orange-100",
    iconColor: "text-alert-warning",
  },
};

export const FeatureCard: React.FC<FeatureCardProps> = ({
  icon,
  title,
  titleEn,
  description,
  color = "blue",
  onClick,
  className,
}) => {
  const config = colorConfig[color];

  return (
    <div
      className={clsx(
        "rounded-2xl p-4 cursor-pointer transition-all duration-200",
        "hover:shadow-lg hover:-translate-y-1",
        config.bg,
        className,
      )}
      onClick={onClick}
    >
      {/* Icon */}
      <div
        className={clsx(
          "w-12 h-12 rounded-xl flex items-center justify-center mb-3",
          config.iconBg,
        )}
      >
        <span className={config.iconColor}>{icon}</span>
      </div>

      {/* Title */}
      <div className="flex items-center justify-between">
        <div>
          {titleEn && (
            <p className="text-xs text-text-muted uppercase tracking-wide">
              {titleEn}
            </p>
          )}
          <h3 className="font-semibold text-text-primary">{title}</h3>
        </div>
        <ChevronRight className="w-5 h-5 text-text-muted" />
      </div>

      {/* Description */}
      <p className="text-sm text-text-secondary mt-1 line-clamp-2">
        {description}
      </p>
    </div>
  );
};

FeatureCard.displayName = "FeatureCard";
