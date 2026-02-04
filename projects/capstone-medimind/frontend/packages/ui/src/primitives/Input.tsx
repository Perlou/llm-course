import React, { forwardRef } from "react";
import { clsx } from "clsx";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  error?: string;
  containerClassName?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    { leftIcon, rightIcon, error, className, containerClassName, ...props },
    ref,
  ) => {
    return (
      <div className={clsx("relative", containerClassName)}>
        {leftIcon && (
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted">
            {leftIcon}
          </span>
        )}
        <input
          ref={ref}
          className={clsx(
            "w-full px-4 py-3 rounded-xl border border-border bg-white text-text-primary placeholder-text-muted",
            "focus:outline-none focus:ring-2 focus:ring-medical-blue/30 focus:border-medical-blue",
            "transition-all duration-200",
            leftIcon && "pl-10",
            rightIcon && "pr-10",
            error &&
              "border-alert-danger focus:ring-alert-danger/30 focus:border-alert-danger",
            className,
          )}
          {...props}
        />
        {rightIcon && (
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted">
            {rightIcon}
          </span>
        )}
        {error && <p className="mt-1 text-sm text-alert-danger">{error}</p>}
      </div>
    );
  },
);

Input.displayName = "Input";
