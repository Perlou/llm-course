---
name: add-ui-primitive
description: 为 MediMind 添加基础 UI 原子组件（Button, Input, Card等）
---

# 添加 UI 原子组件技能

此技能用于在 MediMind 的 `@medimind/ui` 包中添加基础原子组件。

## 原子组件目录

```
frontend/packages/ui/src/primitives/
├── index.ts              # 导出入口
├── Button.tsx            # 按钮
├── Input.tsx             # 输入框
├── Card.tsx              # 卡片
├── Badge.tsx             # 徽章
├── Spinner.tsx           # 加载动画
├── Avatar.tsx            # 头像
├── Modal.tsx             # 模态框
└── Tooltip.tsx           # 工具提示
```

## 组件模板

### Button - 按钮

```tsx
// src/primitives/Button.tsx
import React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../utils";
import { Loader2 } from "lucide-react";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed",
  {
    variants: {
      variant: {
        primary: "bg-teal-600 text-white hover:bg-teal-700 focus:ring-teal-500",
        secondary:
          "bg-gray-100 text-gray-900 hover:bg-gray-200 focus:ring-gray-500",
        outline:
          "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-gray-500",
        ghost: "text-gray-700 hover:bg-gray-100 focus:ring-gray-500",
        danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
      },
      size: {
        sm: "h-8 px-3 text-sm",
        md: "h-10 px-4 text-base",
        lg: "h-12 px-6 text-lg",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  },
);

export interface ButtonProps
  extends
    React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  /** 加载状态 */
  loading?: boolean;
}

export function Button({
  className,
  variant,
  size,
  loading,
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size }), className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Loader2 className="w-4 h-4 animate-spin" />}
      {children}
    </button>
  );
}
```

### Input - 输入框

```tsx
// src/primitives/Input.tsx
import React from "react";
import { cn } from "../utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  /** 错误状态 */
  error?: boolean;
  /** 错误信息 */
  errorMessage?: string;
  /** 左侧图标 */
  leftIcon?: React.ReactNode;
  /** 右侧图标 */
  rightIcon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, errorMessage, leftIcon, rightIcon, ...props }, ref) => {
    return (
      <div className="w-full">
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            className={cn(
              "w-full h-10 px-4 rounded-lg border bg-white text-gray-900",
              "placeholder:text-gray-400",
              "focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent",
              "disabled:bg-gray-100 disabled:cursor-not-allowed",
              error ? "border-red-500" : "border-gray-300",
              leftIcon && "pl-10",
              rightIcon && "pr-10",
              className,
            )}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
              {rightIcon}
            </div>
          )}
        </div>
        {errorMessage && (
          <p className="mt-1 text-sm text-red-500">{errorMessage}</p>
        )}
      </div>
    );
  },
);

Input.displayName = "Input";
```

### Card - 卡片

```tsx
// src/primitives/Card.tsx
import React from "react";
import { cn } from "../utils";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** 变体 */
  variant?: "default" | "bordered" | "elevated";
  /** 是否可点击 */
  clickable?: boolean;
}

export function Card({
  className,
  variant = "default",
  clickable,
  children,
  ...props
}: CardProps) {
  const variantStyles = {
    default: "bg-white border border-gray-200",
    bordered: "bg-white border-2 border-gray-300",
    elevated: "bg-white shadow-lg",
  };

  return (
    <div
      className={cn(
        "rounded-xl",
        variantStyles[variant],
        clickable && "cursor-pointer hover:shadow-md transition-shadow",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}

// 子组件
Card.Header = function CardHeader({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("px-6 py-4 border-b border-gray-200", className)}
      {...props}
    >
      {children}
    </div>
  );
};

Card.Body = function CardBody({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("px-6 py-4", className)} {...props}>
      {children}
    </div>
  );
};

Card.Footer = function CardFooter({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-xl",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
};
```

### Badge - 徽章

```tsx
// src/primitives/Badge.tsx
import React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
  {
    variants: {
      variant: {
        default: "bg-gray-100 text-gray-800",
        primary: "bg-teal-100 text-teal-800",
        success: "bg-green-100 text-green-800",
        warning: "bg-yellow-100 text-yellow-800",
        danger: "bg-red-100 text-red-800",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps
  extends
    React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}
```

### Spinner - 加载动画

```tsx
// src/primitives/Spinner.tsx
import React from "react";
import { cn } from "../utils";

export interface SpinnerProps {
  /** 尺寸 */
  size?: "sm" | "md" | "lg";
  /** 颜色 */
  color?: "primary" | "white" | "gray";
  /** 自定义类名 */
  className?: string;
}

export function Spinner({
  size = "md",
  color = "primary",
  className,
}: SpinnerProps) {
  const sizeStyles = {
    sm: "w-4 h-4 border-2",
    md: "w-6 h-6 border-2",
    lg: "w-8 h-8 border-3",
  };

  const colorStyles = {
    primary: "border-teal-600 border-t-transparent",
    white: "border-white border-t-transparent",
    gray: "border-gray-400 border-t-transparent",
  };

  return (
    <div
      className={cn(
        "rounded-full animate-spin",
        sizeStyles[size],
        colorStyles[color],
        className,
      )}
    />
  );
}
```

### Textarea - 文本域

```tsx
// src/primitives/Textarea.tsx
import React from "react";
import { cn } from "../utils";

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  /** 错误状态 */
  error?: boolean;
  /** 错误信息 */
  errorMessage?: string;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, error, errorMessage, ...props }, ref) => {
    return (
      <div className="w-full">
        <textarea
          ref={ref}
          className={cn(
            "w-full min-h-[100px] px-4 py-3 rounded-lg border bg-white text-gray-900",
            "placeholder:text-gray-400 resize-y",
            "focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent",
            "disabled:bg-gray-100 disabled:cursor-not-allowed",
            error ? "border-red-500" : "border-gray-300",
            className,
          )}
          {...props}
        />
        {errorMessage && (
          <p className="mt-1 text-sm text-red-500">{errorMessage}</p>
        )}
      </div>
    );
  },
);

Textarea.displayName = "Textarea";
```

## 导出配置

```tsx
// src/primitives/index.ts
export { Button } from "./Button";
export type { ButtonProps } from "./Button";

export { Input } from "./Input";
export type { InputProps } from "./Input";

export { Textarea } from "./Textarea";
export type { TextareaProps } from "./Textarea";

export { Card } from "./Card";
export type { CardProps } from "./Card";

export { Badge } from "./Badge";
export type { BadgeProps } from "./Badge";

export { Spinner } from "./Spinner";
export type { SpinnerProps } from "./Spinner";
```

```tsx
// src/index.ts
export * from "./primitives";
export * from "./components";
export { cn } from "./utils";
```

## MediMind 设计 Token

### 颜色

| 名称    | 值           | 用途           |
| ------- | ------------ | -------------- |
| Primary | Teal 600     | 主要按钮、链接 |
| Success | Green 500    | 成功状态       |
| Warning | Amber 500    | 警告状态       |
| Danger  | Red 600      | 错误、危险     |
| Neutral | Gray 100-900 | 背景、文字     |

### 尺寸

| 名称 | 高度 | 用途     |
| ---- | ---- | -------- |
| sm   | 32px | 紧凑场景 |
| md   | 40px | 默认     |
| lg   | 48px | 突出场景 |

### 圆角

| 名称 | 值     | 用途       |
| ---- | ------ | ---------- |
| sm   | 4px    | 徽章       |
| md   | 8px    | 按钮、输入 |
| lg   | 12px   | 卡片       |
| xl   | 16px   | 模态框     |
| full | 9999px | 药丸形状   |

## 注意事项

1. **CVA 使用**：使用 class-variance-authority 管理变体
2. **Ref 转发**：表单元素需支持 forwardRef
3. **类型导出**：同时导出组件和 Props 类型
4. **无障碍**：确保 focus 状态可见
5. **暗色模式**：预留 dark: 类名扩展
