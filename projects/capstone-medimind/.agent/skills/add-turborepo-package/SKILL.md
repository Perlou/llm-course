---
name: add-turborepo-package
description: 为 MediMind 前端 Monorepo 添加新的共享包
---

# 添加 Turborepo 包技能

此技能用于在 MediMind 前端 Monorepo 中添加新的共享包。

## Monorepo 结构

```
frontend/
├── turbo.json                    # Turborepo 配置
├── pnpm-workspace.yaml           # pnpm workspace
├── package.json                  # 根 package.json
│
├── apps/                         # 应用层
│   └── web/                      # Web 应用
│
└── packages/                     # 共享包层
    ├── ui/                       # @medimind/ui 组件库
    ├── api-client/               # @medimind/api-client SDK
    ├── config/                   # @medimind/config 配置
    └── types/                    # @medimind/types 类型
```

## 创建新包步骤

### 1. 创建包目录

```bash
cd frontend/packages
mkdir new-package
cd new-package
```

### 2. 初始化 package.json

```json
{
  "name": "@medimind/new-package",
  "version": "0.0.0",
  "private": true,
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts",
    "dev": "tsup src/index.ts --format esm,cjs --dts --watch",
    "lint": "eslint src/",
    "test": "vitest"
  },
  "dependencies": {},
  "devDependencies": {
    "@medimind/config": "workspace:*",
    "typescript": "^5.3.0",
    "tsup": "^8.0.0"
  }
}
```

### 3. 创建 tsconfig.json

```json
{
  "extends": "@medimind/config/tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### 4. 创建源文件

```typescript
// src/index.ts
export * from "./utils";
export * from "./types";

// src/utils.ts
export function myUtility() {
  // ...
}

// src/types.ts
export interface MyType {
  // ...
}
```

## 包类型模板

### UI 组件包

```json
{
  "name": "@medimind/new-components",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0"
  },
  "peerDependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
```

组件示例：

```tsx
// src/components/Button.tsx
import React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-lg font-medium transition-colors",
  {
    variants: {
      variant: {
        primary: "bg-teal-600 text-white hover:bg-teal-700",
        secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200",
        danger: "bg-red-600 text-white hover:bg-red-700",
      },
      size: {
        sm: "h-8 px-3 text-sm",
        md: "h-10 px-4 text-base",
        lg: "h-12 px-6 text-lg",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  },
);

interface ButtonProps
  extends
    React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export function Button({ className, variant, size, ...props }: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size }), className)}
      {...props}
    />
  );
}
```

### API Client 包

```json
{
  "name": "@medimind/api-client",
  "dependencies": {
    "ky": "^1.2.0"
  }
}
```

SDK 示例：

```typescript
// src/index.ts
import ky from "ky";

const api = ky.create({
  prefixUrl: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
});

export const healthApi = {
  async chat(query: string) {
    return api.post("health/chat", { json: { query } }).json();
  },

  async streamChat(query: string) {
    return api.post("health/stream", { json: { query } });
  },
};

export const drugApi = {
  async search(keyword: string) {
    return api.get("drug/search", { searchParams: { q: keyword } }).json();
  },

  async getById(id: string) {
    return api.get(`drug/${id}`).json();
  },
};
```

### Types 包

```json
{
  "name": "@medimind/types",
  "dependencies": {}
}
```

类型示例：

```typescript
// src/health.ts
export interface ChatRequest {
  query: string;
  conversationId?: string;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  emergency?: boolean;
  disclaimer: string;
}

export interface Source {
  title: string;
  page?: string;
  url?: string;
}
```

## 在应用中使用包

### 安装依赖

```bash
cd frontend/apps/web
pnpm add @medimind/new-package
```

或在 package.json 添加：

```json
{
  "dependencies": {
    "@medimind/new-package": "workspace:*"
  }
}
```

### 导入使用

```typescript
import { MyComponent } from "@medimind/ui";
import { healthApi } from "@medimind/api-client";
import type { ChatResponse } from "@medimind/types";
```

## Turbo 配置

确保 `turbo.json` 包含构建配置：

```json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    }
  }
}
```

## 常用命令

```bash
# 在 frontend/ 目录下

# 安装所有依赖
pnpm install

# 构建所有包
pnpm build

# 开发模式
pnpm dev

# 仅构建特定包
pnpm --filter @medimind/ui build

# 添加依赖到特定包
pnpm --filter @medimind/ui add react-icons
```

## 注意事项

1. **命名规范**：所有包使用 `@medimind/` 命名空间
2. **版本**：内部包使用 `workspace:*` 引用
3. **类型导出**：确保导出 TypeScript 类型
4. **构建顺序**：Turborepo 自动处理依赖构建顺序
5. **Tree Shaking**：使用 ESM 格式支持 Tree Shaking
