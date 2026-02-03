---
name: add-react-component
description: 为 MediMind 添加新的 React 组件到 @medimind/ui 共享库
---

# 添加 React 组件技能

此技能用于在 MediMind 项目的 `@medimind/ui` 共享组件库中添加新组件。

## 组件库结构

```
frontend/packages/ui/
├── package.json
├── tailwind.config.js
├── src/
│   ├── index.ts                    # 导出入口
│   ├── utils.ts                    # 工具函数 (cn, etc.)
│   ├── primitives/                 # 基础 UI 组件
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   └── index.ts
│   └── components/                 # 业务组件
│       ├── ChatMessage.tsx         # 聊天消息
│       ├── SourceCard.tsx          # 来源卡片
│       ├── DrugCard.tsx            # 药品卡片
│       ├── ReportViewer.tsx        # 报告查看器
│       ├── EmergencyAlert.tsx      # 紧急提醒
│       ├── SafetyBanner.tsx        # 安全横幅
│       └── index.ts
└── tsconfig.json
```

## 创建新组件步骤

### 1. 创建组件文件

在 `src/components/` 或 `src/primitives/` 创建组件：

```tsx
// src/components/NewComponent.tsx
import React from "react";
import { cn } from "../utils";

export interface NewComponentProps {
  /** 组件标题 */
  title: string;
  /** 子内容 */
  children?: React.ReactNode;
  /** 自定义类名 */
  className?: string;
  /** 变体 */
  variant?: "default" | "success" | "warning" | "danger";
}

/**
 * NewComponent - 组件描述
 */
export function NewComponent({
  title,
  children,
  className,
  variant = "default",
}: NewComponentProps) {
  const variantStyles = {
    default: "bg-white border-gray-200",
    success: "bg-green-50 border-green-200",
    warning: "bg-yellow-50 border-yellow-200",
    danger: "bg-red-50 border-red-200",
  };

  return (
    <div
      className={cn(
        "rounded-xl border p-4 shadow-sm",
        variantStyles[variant],
        className,
      )}
    >
      <h3 className="font-semibold text-gray-900">{title}</h3>
      {children && <div className="mt-2 text-gray-600">{children}</div>}
    </div>
  );
}
```

### 2. 在 index.ts 导出

```tsx
// src/components/index.ts
export { NewComponent } from "./NewComponent";
export type { NewComponentProps } from "./NewComponent";
```

```tsx
// src/index.ts
export * from "./components";
export * from "./primitives";
export { cn } from "./utils";
```

## MediMind 业务组件模板

### ChatMessage - 聊天消息

```tsx
// src/components/ChatMessage.tsx
import React from "react";
import { cn } from "../utils";
import { Card } from "../primitives";

export interface ChatMessageProps {
  /** 消息内容 */
  content: string;
  /** 是否为用户消息 */
  isUser: boolean;
  /** 来源引用 */
  sources?: Array<{ title: string; page?: string }>;
  /** 是否正在加载 */
  isLoading?: boolean;
  /** 时间戳 */
  timestamp?: Date;
}

export function ChatMessage({
  content,
  isUser,
  sources,
  isLoading,
  timestamp,
}: ChatMessageProps) {
  return (
    <div
      className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-3",
          isUser ? "bg-teal-600 text-white" : "bg-gray-100 text-gray-900",
        )}
      >
        {isLoading ? (
          <div className="flex items-center gap-1">
            <span className="animate-bounce">●</span>
            <span className="animate-bounce delay-100">●</span>
            <span className="animate-bounce delay-200">●</span>
          </div>
        ) : (
          <>
            <p className="whitespace-pre-wrap">{content}</p>

            {/* 来源引用 */}
            {sources && sources.length > 0 && (
              <div className="mt-3 border-t border-gray-200 pt-2">
                <p className="text-xs text-gray-500 mb-1">参考来源：</p>
                <div className="flex flex-wrap gap-1">
                  {sources.map((source, i) => (
                    <span
                      key={i}
                      className="text-xs bg-white/20 px-2 py-0.5 rounded"
                    >
                      {source.title}
                      {source.page && ` (第${source.page}页)`}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {timestamp && (
          <p className="text-xs opacity-60 mt-1">
            {timestamp.toLocaleTimeString()}
          </p>
        )}
      </div>
    </div>
  );
}
```

### EmergencyAlert - 紧急提醒

```tsx
// src/components/EmergencyAlert.tsx
import React from "react";
import { AlertTriangle, Phone } from "lucide-react";
import { cn } from "../utils";

export interface EmergencyAlertProps {
  /** 是否显示 */
  show: boolean;
  /** 提示消息 */
  message?: string;
  /** 关闭回调 */
  onClose?: () => void;
}

export function EmergencyAlert({
  show,
  message = "如果您正在经历紧急症状，请立即拨打 120 急救电话！",
  onClose,
}: EmergencyAlertProps) {
  if (!show) return null;

  return (
    <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-full max-w-md">
      <div className="bg-red-600 text-white rounded-xl shadow-lg p-4 mx-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-6 h-6 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="font-bold">紧急提醒</h4>
            <p className="text-sm mt-1">{message}</p>
            <a
              href="tel:120"
              className="inline-flex items-center gap-2 mt-3 bg-white text-red-600 px-4 py-2 rounded-lg font-semibold hover:bg-red-50 transition"
            >
              <Phone className="w-4 h-4" />
              拨打 120
            </a>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="text-white/80 hover:text-white"
            >
              ✕
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
```

### SafetyBanner - 安全横幅

```tsx
// src/components/SafetyBanner.tsx
import React from "react";
import { Shield } from "lucide-react";

export function SafetyBanner() {
  return (
    <div className="bg-teal-50 border-b border-teal-100 px-4 py-2">
      <div className="max-w-4xl mx-auto flex items-center gap-2 text-sm text-teal-800">
        <Shield className="w-4 h-4" />
        <span>
          本平台提供健康信息服务，不构成医疗诊断。如有健康问题请咨询专业医生。
        </span>
      </div>
    </div>
  );
}
```

## 工具函数

```tsx
// src/utils.ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * 合并 Tailwind 类名
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

## 在应用中使用

```tsx
// apps/web/src/pages/ChatPage.tsx
import { ChatMessage, EmergencyAlert, SafetyBanner } from "@medimind/ui";

export function ChatPage() {
  return (
    <>
      <SafetyBanner />
      <EmergencyAlert show={isEmergency} />

      <div className="space-y-4">
        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            content={msg.content}
            isUser={msg.role === "user"}
            sources={msg.sources}
          />
        ))}
      </div>
    </>
  );
}
```

## MediMind 设计规范

### 颜色

| 用途 | 颜色         | 示例            |
| ---- | ------------ | --------------- |
| 主色 | Teal 600     | `bg-teal-600`   |
| 成功 | Green 500    | `bg-green-500`  |
| 警告 | Amber 500    | `bg-amber-500`  |
| 危险 | Red 600      | `bg-red-600`    |
| 背景 | Gray 50/100  | `bg-gray-50`    |
| 文字 | Gray 900/600 | `text-gray-900` |

### 圆角

- 按钮/标签: `rounded-lg` (8px)
- 卡片: `rounded-xl` (12px)
- 消息气泡: `rounded-2xl` (16px)

### 阴影

- 轻度: `shadow-sm`
- 中度: `shadow-md`
- 浮动: `shadow-lg`

## 注意事项

1. **医疗合规**：所有健康相关组件必须包含免责声明
2. **紧急提醒**：紧急情况组件必须醒目、可操作
3. **无障碍**：确保颜色对比度、键盘导航
4. **响应式**：使用 Tailwind 响应式类
5. **类型安全**：导出 Props 类型供应用使用
