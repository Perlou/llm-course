# MediMind Frontend

基于 Turborepo 的前端 Monorepo 项目。

## 项目结构

```
frontend/
├── apps/
│   └── web/          # Web 应用 (Vite + React)
└── packages/
    ├── config/       # 共享配置 (ESLint, Tailwind)
    ├── types/        # TypeScript 类型定义
    ├── api-client/   # API 调用封装
    └── ui/           # 共享组件库
```

## 开发

```bash
# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 构建
pnpm build

# 代码检查
pnpm lint
```

## 技术栈

- **Monorepo**: Turborepo + pnpm
- **前端框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **图标**: Lucide React
