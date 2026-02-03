---
name: setup-frontend
description: 初始化和配置 MediMind 前端 Turborepo 项目
---

# 初始化前端项目技能

此技能用于初始化 MediMind 前端 Turborepo Monorepo 项目结构。

## 完整项目结构

```
frontend/
├── turbo.json                    # Turborepo 配置
├── pnpm-workspace.yaml           # pnpm workspace
├── package.json                  # 根 package.json
├── .gitignore
├── .eslintrc.js
│
├── apps/
│   └── web/                      # Web 应用
│       ├── package.json
│       ├── vite.config.ts
│       ├── tailwind.config.js
│       ├── postcss.config.js
│       ├── tsconfig.json
│       ├── index.html
│       └── src/
│           ├── App.tsx
│           ├── main.tsx
│           ├── pages/
│           ├── routes/
│           ├── hooks/
│           └── styles/
│
└── packages/
    ├── ui/                       # @medimind/ui
    ├── api-client/               # @medimind/api-client
    ├── config/                   # @medimind/config
    └── types/                    # @medimind/types
```

## 初始化步骤

### 1. 创建根目录配置

```bash
cd /Users/perlou/Desktop/personal/llm-course/projects/capstone-medimind
mkdir -p frontend
cd frontend
```

#### pnpm-workspace.yaml

```yaml
packages:
  - "apps/*"
  - "packages/*"
```

#### package.json

```json
{
  "name": "medimind-frontend",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "dev": "turbo dev",
    "build": "turbo build",
    "lint": "turbo lint",
    "test": "turbo test",
    "clean": "turbo clean && rm -rf node_modules"
  },
  "devDependencies": {
    "turbo": "^2.0.0",
    "typescript": "^5.3.0"
  },
  "packageManager": "pnpm@8.15.0"
}
```

#### turbo.json

```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["build"]
    },
    "clean": {
      "cache": false
    }
  }
}
```

### 2. 创建 @medimind/config 包

```bash
mkdir -p packages/config
```

#### packages/config/package.json

```json
{
  "name": "@medimind/config",
  "version": "0.0.0",
  "private": true,
  "main": "./index.js",
  "files": ["*.js", "*.json"]
}
```

#### packages/config/tailwind-preset.js

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f0fdfa",
          100: "#ccfbf1",
          200: "#99f6e4",
          300: "#5eead4",
          400: "#2dd4bf",
          500: "#14b8a6",
          600: "#0d9488",
          700: "#0f766e",
          800: "#115e59",
          900: "#134e4a",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      borderRadius: {
        xl: "12px",
        "2xl": "16px",
      },
    },
  },
  plugins: [],
};
```

#### packages/config/eslint-preset.js

```javascript
module.exports = {
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "prettier",
  ],
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint", "react"],
  rules: {
    "react/react-in-jsx-scope": "off",
    "@typescript-eslint/no-explicit-any": "warn",
  },
  settings: {
    react: {
      version: "detect",
    },
  },
};
```

### 3. 创建 @medimind/types 包

```bash
mkdir -p packages/types/src
```

#### packages/types/package.json

```json
{
  "name": "@medimind/types",
  "version": "0.0.0",
  "private": true,
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "scripts": {
    "build": "tsc",
    "lint": "eslint src/"
  },
  "devDependencies": {
    "typescript": "^5.3.0"
  }
}
```

#### packages/types/src/index.ts

```typescript
export * from "./health";
export * from "./drug";
export * from "./report";
export * from "./common";
```

#### packages/types/src/health.ts

```typescript
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

### 4. 创建 @medimind/api-client 包

```bash
mkdir -p packages/api-client/src
```

#### packages/api-client/package.json

```json
{
  "name": "@medimind/api-client",
  "version": "0.0.0",
  "private": true,
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts",
    "dev": "tsup src/index.ts --format esm,cjs --dts --watch"
  },
  "dependencies": {
    "ky": "^1.2.0"
  },
  "devDependencies": {
    "@medimind/types": "workspace:*",
    "tsup": "^8.0.0",
    "typescript": "^5.3.0"
  }
}
```

#### packages/api-client/src/index.ts

```typescript
import ky from "ky";

const api = ky.create({
  prefixUrl: import.meta.env?.VITE_API_URL || "http://localhost:8000/api/v1",
  timeout: 30000,
});

export * from "./health";
export * from "./drug";
export * from "./report";
export * from "./triage";
export { api };
```

### 5. 创建 @medimind/ui 包

```bash
mkdir -p packages/ui/src/{components,primitives}
```

#### packages/ui/package.json

```json
{
  "name": "@medimind/ui",
  "version": "0.0.0",
  "private": true,
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "sideEffects": false,
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts --external react",
    "dev": "tsup src/index.ts --format esm,cjs --dts --watch --external react",
    "lint": "eslint src/"
  },
  "dependencies": {
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "lucide-react": "^0.312.0",
    "tailwind-merge": "^2.2.0"
  },
  "peerDependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@medimind/config": "workspace:*",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "tsup": "^8.0.0",
    "typescript": "^5.3.0"
  }
}
```

### 6. 创建 apps/web 应用

```bash
mkdir -p apps/web/src/{pages,routes,hooks,styles}
```

#### apps/web/package.json

```json
{
  "name": "@medimind/web",
  "version": "0.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src/"
  },
  "dependencies": {
    "@medimind/api-client": "workspace:*",
    "@medimind/types": "workspace:*",
    "@medimind/ui": "workspace:*",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.0",
    "react-dropzone": "^14.2.3"
  },
  "devDependencies": {
    "@medimind/config": "workspace:*",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.35",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.3.0",
    "vite": "^5.1.0"
  }
}
```

#### apps/web/vite.config.ts

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
```

#### apps/web/tailwind.config.js

```javascript
const preset = require("@medimind/config/tailwind-preset");

/** @type {import('tailwindcss').Config} */
module.exports = {
  presets: [preset],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "../../packages/ui/src/**/*.{js,ts,jsx,tsx}",
  ],
};
```

## 安装和运行

```bash
# 安装所有依赖
cd frontend
pnpm install

# 开发模式
pnpm dev

# 构建
pnpm build
```

## 注意事项

1. **workspace 依赖**：内部包使用 `workspace:*` 引用
2. **构建顺序**：Turborepo 自动处理依赖构建顺序
3. **共享配置**：ESLint 和 Tailwind 配置放在 @medimind/config
4. **类型共享**：所有类型定义放在 @medimind/types
5. **API 封装**：所有 API 调用通过 @medimind/api-client
