---
description: 启动 MediMind 前端开发服务器 (Turborepo)
---

# 启动前端开发服务器

1. 进入前端目录

```bash
cd /Users/perlou/Desktop/personal/llm-course/projects/capstone-medimind/frontend
```

2. 安装依赖（首次运行或依赖更新后）

```bash
pnpm install
```

3. 启动开发服务器
   // turbo

```bash
pnpm dev
```

服务启动后访问：

- Web 应用: http://localhost:5173

## 其他命令

仅启动 Web 应用：

```bash
pnpm --filter @medimind/web dev
```

构建所有包：

```bash
pnpm build
```

代码检查：

```bash
pnpm lint
```
