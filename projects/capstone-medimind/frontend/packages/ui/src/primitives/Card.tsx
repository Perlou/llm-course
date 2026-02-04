import React from "react";
import { clsx } from "clsx";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "bordered" | "elevated";
  padding?: "none" | "sm" | "md" | "lg";
  hoverable?: boolean;
}

export const Card: React.FC<CardProps> = ({
  variant = "default",
  padding = "md",
  hoverable = false,
  className,
  children,
  ...props
}) => {
  const baseStyles = "bg-card rounded-xl transition-all duration-200";

  const variantStyles = {
    default: "border border-border",
    bordered: "border-2 border-border",
    elevated: "shadow-lg border border-border/50",
  };

  const paddingStyles = {
    none: "",
    sm: "p-3",
    md: "p-4",
    lg: "p-6",
  };

  const hoverStyles = hoverable
    ? "hover:border-medical-blue hover:shadow-md hover:-translate-y-0.5 cursor-pointer"
    : "";

  return (
    <div
      className={clsx(
        baseStyles,
        variantStyles[variant],
        paddingStyles[padding],
        hoverStyles,
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
};

Card.displayName = "Card";
