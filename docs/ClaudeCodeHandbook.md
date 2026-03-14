

# Claude Code 速查手册

> 📌 版本说明：基于 Claude Code 最新版本整理，持续更新中。

---

## 目录

- [1. 安装与初始化](#1-安装与初始化)
- [2. 启动与基本用法](#2-启动与基本用法)
- [3. CLI 命令行参数](#3-cli-命令行参数)
- [4. 斜杠命令 (Slash Commands)](#4-斜杠命令-slash-commands)
- [5. 快捷键](#5-快捷键)
- [6. 权限管理](#6-权限管理)
- [7. 记忆系统 (Memory / CLAUDE.md)](#7-记忆系统-memory--claudemd)
- [8. 配置文件与设置](#8-配置文件与设置)
- [9. MCP (Model Context Protocol)](#9-mcp-model-context-protocol)
- [10. 常用工作流与实战示例](#10-常用工作流与实战示例)
- [11. 非交互模式 (Headless / CI/CD)](#11-非交互模式-headless--cicd)
- [12. 多 Claude 协作模式](#12-多-claude-协作模式)
- [13. 自定义 Hooks](#13-自定义-hooks)
- [14. 调试与排障](#14-调试与排障)
- [15. 最佳实践](#15-最佳实践)
- [16. 费用与模型](#16-费用与模型)

---

## 1. 安装与初始化

### 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | macOS 10.15+、Ubuntu 20.04+/Debian 10+、Windows (通过 WSL2) |
| Node.js | **v18+** |
| 硬件 | 4GB+ RAM |
| 网络 | 需要联网 (连接 Anthropic API) |

### 安装

```bash
# 全局安装 (推荐)
npm install -g @anthropic-ai/claude-code

# 验证安装
claude --version

# 更新到最新版
npm update -g @anthropic-ai/claude-code
```

### 首次初始化

```bash
# 进入项目目录
cd your-project

# 启动 Claude Code（首次会引导登录认证）
claude
```

### 认证方式

```bash
# 方式1：交互式登录（默认，通过 OAuth 跳转浏览器）
claude

# 方式2：API Key 直接设置
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
claude

# 方式3：通过 Amazon Bedrock
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=xxxxx
export AWS_SECRET_ACCESS_KEY=xxxxx

# 方式4：通过 Google Vertex AI
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=us-east5
export ANTHROPIC_VERTEX_PROJECT_ID=your-project-id
```

---

## 2. 启动与基本用法

### 基础启动

```bash
# 在当前目录启动交互式会话
claude

# 带初始提示启动
claude "解释这个项目的架构"

# 以指定目录启动
cd /path/to/project && claude

# 继续上一次的对话
claude --continue
# 或简写
claude -c

# 从最近的会话中选择一个恢复
claude --resume
# 或简写
claude -r
```

### 管道输入 (Pipe)

```bash
# 管道输入文件内容
cat main.py | claude "review this code"

# 管道输入命令输出
git diff | claude "explain these changes"

# 管道输入 + 提示
echo "Hello World" | claude "translate to French"

# 管道输入日志分析
cat error.log | claude "分析这些错误日志，找出根因"

# 组合管道
git log --oneline -20 | claude "summarize recent changes"
```

### 输出控制

```bash
# 只输出结果文本（适合脚本使用）
claude -p "what is 2+2"

# 输出 JSON 格式
claude -p --output-format json "describe this project"

# 输出流式 JSON
claude -p --output-format stream-json "describe this project"
```

---

## 3. CLI 命令行参数

### 完整参数列表

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--help` | `-h` | 显示帮助信息 | `claude -h` |
| `--version` | `-v` | 显示版本号 | `claude -v` |
| `--print` | `-p` | 非交互模式，输出后退出 | `claude -p "hi"` |
| `--continue` | `-c` | 继续最近一次会话 | `claude -c` |
| `--resume` | `-r` | 选择一个历史会话恢复 | `claude -r` |
| `--output-format` | | 输出格式 (`text`/`json`/`stream-json`) | `claude -p --output-format json "hi"` |
| `--model` | | 指定模型 | `claude --model claude-sonnet-4-20250514` |
| `--permission-mode` | | 权限模式 | `claude --permission-mode plan` |
| `--allowedTools` | | 允许使用的工具列表 | `claude --allowedTools "Bash(git*)" "Read"` |
| `--disallowedTools` | | 禁止使用的工具列表 | `claude --disallowedTools "Bash" "Write"` |
| `--max-turns` | | 限制最大轮次（非交互模式） | `claude -p --max-turns 5 "fix bugs"` |
| `--system-prompt` | | 自定义系统提示（仅 `-p` 模式） | `claude -p --system-prompt "You are a Go expert" "review"` |
| `--append-system-prompt` | | 追加系统提示 | `claude -p --append-system-prompt "Be concise"` |
| `--input-format` | | 输入格式 (`text`/`stream-json`) | `claude -p --input-format stream-json` |
| `--verbose` | | 启用详细日志 | `claude --verbose` |
| `--no-cache` | | 禁用提示缓存 | `claude --no-cache` |

### 子命令

```bash
# 配置管理
claude config                    # 交互式配置
claude config list               # 列出所有配置
claude config get <key>          # 获取配置值
claude config set <key> <value>  # 设置配置值

# MCP 管理
claude mcp                            # 查看 MCP 帮助
claude mcp list                       # 列出已配置的 MCP 服务器
claude mcp add <name> <command> [args] # 添加 MCP 服务器
claude mcp remove <name>              # 移除 MCP 服务器

# 登录管理
claude login                     # 切换账号/重新登录
claude logout                    # 退出登录

# 诊断
claude doctor                    # 检查安装与健康状态

# API 调用
claude api ...                   # 直接调用 API 子命令
```

---

## 4. 斜杠命令 (Slash Commands)

在交互式会话中使用的内置命令：

### 会话管理

| 命令 | 说明 |
|------|------|
| `/clear` | 清除当前对话上下文（保留会话） |
| `/compact` | 压缩对话上下文（自定义压缩提示可选） |
| `/compact [instructions]` | 按指定指令压缩上下文 |

### 配置与状态

| 命令 | 说明 |
|------|------|
| `/config` | 查看/修改配置 |
| `/cost` | 显示当前会话的 token 用量和费用 |
| `/status` | 查看当前账户和会话状态 |
| `/model` | 切换/选择模型 |
| `/permissions` | 查看与管理权限设置 |

### 记忆与上下文

| 命令 | 说明 |
|------|------|
| `/memory` | 编辑项目 CLAUDE.md 记忆文件 |
| `/add-dir <path>` | 添加额外的工作目录到上下文 |

### 工具与调试

| 命令 | 说明 |
|------|------|
| `/tools` | 查看所有可用的工具列表 |
| `/mcp` | 查看已配置的 MCP 服务器和工具 |
| `/terminal-setup` | 安装 Shift+Enter 换行支持（iTerm2/VSCode） |

### 其他

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助信息 |
| `/doctor` | 检查 Claude Code 安装健康状态 |
| `/review` | 请求代码审查 |
| `/bug` | 报告 Bug |
| `/init` | 用 CLAUDE.md 初始化项目 |
| `/login` | 切换 Anthropic 账号 |
| `/logout` | 登出当前账号 |
| `/vim` | 进入 vim 编辑模式 |
| `/quit` | 退出 Claude Code（同 `Ctrl+C` 两次） |

---

## 5. 快捷键

### 交互式会话中的快捷键

| 快捷键 | 功能 |
|--------|------|
| `Enter` | 发送消息 |
| `Shift+Enter` | 换行（需要 `/terminal-setup` 设置） |
| `Ctrl+C` | 中断当前生成 / 取消当前输入 |
| `Ctrl+C` × 2 | 退出 Claude Code |
| `Ctrl+D` | 退出 Claude Code（EOF） |
| `Ctrl+L` | 清屏 |
| `↑` / `↓` | 浏览历史输入 |
| `Esc` | 中断当前操作 / 在 vim 模式下切换 |
| `Esc` × 3 | 清除当前输入内容 |
| `@` | 引用文件路径（自动补全） |

### 权限请求时的快键

| 按键 | 功能 |
|------|------|
| `y` | 允许一次 |
| `n` | 拒绝 |
| `a` | 本次会话内始终允许该工具 |
| `d` | 不再询问（写入 `.claude/settings.json`） |
| `Esc` | 取消 |

---

## 6. 权限管理

### 权限模式

```bash
# 以指定权限模式启动
claude --permission-mode default    # 默认模式（每次询问）
claude --permission-mode plan       # 规划模式（只读，不执行写入/命令）
claude --permission-mode trusted    # 信任模式（自动批准所有操作）⚠️
```

### 工具权限分类

| 类别 | 工具 | 默认行为 |
|------|------|----------|
| **只读（自动允许）** | `Read`, `Glob`, `Grep`, `LS`, `stat` | ✅ 自动允许 |
| **写入（需要确认）** | `Write`, `Edit`, `MultiEdit` | ❓ 每次询问 |
| **命令执行（需要确认）** | `Bash` | ❓ 每次询问 |
| **MCP 工具** | 自定义 MCP 工具 | ❓ 每次询问 |

### 配置权限规则

```bash
# 全局允许/拒绝工具
claude config set allowedTools '["Bash(git log*)", "Bash(npm test*)", "Read"]'
claude config set disallowedTools '["Bash(rm *)"]'

# 查看权限设置文件
cat .claude/settings.json
```

### settings.json 结构

```jsonc
// 项目级别：.claude/settings.json
// 用户级别：~/.claude/settings.json
{
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(npm test*)",
      "Bash(npx prettier*)",
      "Read",
      "Write"
    ],
    "deny": [
      "Bash(curl *)",
      "Bash(rm -rf *)"
    ]
  }
}
```

### Bash 权限规则模式

```bash
# 精确匹配命令前缀
"Bash(git commit*)"        # 允许 git commit 及其参数
"Bash(npm test*)"          # 允许 npm test 相关命令
"Bash(ls*)"                # 允许 ls 命令
"Bash(python *.py)"        # 允许运行 python 脚本
"Bash(docker compose*)"    # 允许 docker compose 相关命令

# 目录限制
"Read(src/*)"              # 只允许读取 src 目录
"Write(src/*)"             # 只允许写入 src 目录
```

---

## 7. 记忆系统 (Memory / CLAUDE.md)

### 文件层级与加载顺序

```
~/.claude/CLAUDE.md              ← 用户级（所有项目通用）
├── /project/CLAUDE.md           ← 项目根目录级（团队共享，提交到 git）
│   ├── /project/.claude/CLAUDE.md  ← 项目本地级（.gitignore 中）
│   ├── /project/src/CLAUDE.md      ← 子目录级（按需加载）
│   └── /project/src/utils/CLAUDE.md
```

### 各层级说明

| 文件路径 | 作用域 | 是否提交 Git | 说明 |
|----------|--------|-------------|------|
| `~/.claude/CLAUDE.md` | 全局 | ❌ | 个人偏好，适用所有项目 |
| `项目根/CLAUDE.md` | 项目 | ✅ 建议 | 团队共享的项目规范 |
| `项目根/.claude/CLAUDE.md` | 项目(个人) | ❌ | 个人在该项目的自定义 |
| `子目录/CLAUDE.md` | 子目录 | ✅ 可选 | 子模块专属说明 |

### CLAUDE.md 最佳内容模板

```markdown
# Project: MyApp

## 项目概述
这是一个基于 React + TypeScript 的 Web 应用...

## 技术栈
- Frontend: React 18, TypeScript, Tailwind CSS
- Backend: Node.js, Express, PostgreSQL
- Testing: Jest, React Testing Library

## 代码规范
- 使用 TypeScript strict 模式
- 函数命名使用 camelCase
- 组件命名使用 PascalCase
- 每个函数必须有 JSDoc 注释
- 优先使用函数式组件和 Hooks

## 常用命令
- `npm run dev` - 启动开发服务器
- `npm test` - 运行测试
- `npm run build` - 构建生产版本
- `npm run lint` - 代码检查

## 目录结构
src/
  components/  - React 组件
  hooks/       - 自定义 Hooks
  utils/       - 工具函数
  types/       - TypeScript 类型定义
  api/         - API 请求层

## 重要注意事项
- 数据库迁移前请先备份
- 不要直接修改 generated/ 目录下的文件
- API Key 禁止硬编码，使用环境变量
```

### 快速操作记忆

```bash
# 在交互式会话中编辑
/memory

# 让 Claude 自动初始化项目记忆
/init

# 对话中让 Claude 记住某事
"请把这个约定记录到 CLAUDE.md 中"
```

---

## 8. 配置文件与设置

### 配置命令

```bash
# 查看所有配置
claude config list

# 查看全局/项目配置
claude config list --global
claude config list --project

# 设置配置
claude config set theme dark
claude config set preferredNotifChannel terminal

# 获取配置值
claude config get theme
```

### 常用配置项

| 配置项 | 可选值 | 说明 |
|--------|--------|------|
| `theme` | `dark`, `light`, `light-daltonized`, `dark-daltonized` | 界面主题 |
| `verbose` | `true`/`false` | 详细输出 |
| `preferredNotifChannel` | `iterm2`, `terminal`, `iterm2_with_bell` | 通知方式 |
| `autoUpdaterStatus` | `on`/`off` | 自动更新 |

### 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 | `sk-ant-xxx` |
| `CLAUDE_CODE_USE_BEDROCK` | 使用 AWS Bedrock | `1` |
| `CLAUDE_CODE_USE_VERTEX` | 使用 Google Vertex AI | `1` |
| `ANTHROPIC_MODEL` | 默认模型覆盖 | `claude-sonnet-4-20250514` |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | 最大输出 token | `16384` |
| `ANTHROPIC_BASE_URL` | 自定义 API 端点 | `https://...` |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | 禁用遥测 | `1` |
| `CLAUDE_CODE_SKIP_CLAUDE_MD` | 跳过 CLAUDE.md | `1` |
| `HTTP_PROXY` / `HTTPS_PROXY` | 代理设置 | `http://proxy:8080` |
| `TMPDIR` | 临时文件目录 | `/tmp/claude` |

---

## 9. MCP (Model Context Protocol)

### 添加 MCP 服务器

```bash
# 基本语法
claude mcp add <name> <command> [args...]

# 添加 stdio 类型（默认）
claude mcp add my-server npx -y @example/my-mcp-server

# 添加带环境变量的服务器
claude mcp add my-server -e API_KEY=xxx npx -y @example/server

# 添加 SSE 类型
claude mcp add my-server --transport sse https://example.com/mcp/sse

# 添加为全局级别
claude mcp add my-server -s global npx -y @example/server

# 添加为项目级别
claude mcp add my-server -s project npx -y @example/server
```

### 管理 MCP 服务器

```bash
# 列出所有 MCP 服务器
claude mcp list

# 查看某个 MCP 服务器详情
claude mcp get <name>

# 移除 MCP 服务器
claude mcp remove <name>

# 在交互会话中查看
/mcp
```

### 常用 MCP 服务器示例

```bash
# 文件系统 MCP
claude mcp add filesystem npx -y @modelcontextprotocol/server-filesystem /path/to/dir

# GitHub MCP
claude mcp add github npx -y @modelcontextprotocol/server-github -e GITHUB_TOKEN=ghp_xxx

# PostgreSQL MCP
claude mcp add postgres npx -y @modelcontextprotocol/server-postgres "postgresql://user:pass@localhost/db"

# Puppeteer (浏览器自动化)
claude mcp add puppeteer npx -y @modelcontextprotocol/server-puppeteer

# Memory (知识图谱)
claude mcp add memory npx -y @modelcontextprotocol/server-memory

# Sentry (错误追踪)
claude mcp add sentry npx -y @modelcontextprotocol/server-sentry -e SENTRY_AUTH_TOKEN=xxx
```

### MCP 配置文件

配置存储在 `~/.claude/claude_desktop_config.json` 或项目的 `.mcp.json` 中：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/project"],
      "env": {}
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxx"
      }
    }
  }
}
```

### 项目级 `.mcp.json`

```json
{
  "mcpServers": {
    "my-tool": {
      "command": "node",
      "args": ["./tools/my-mcp-server.js"],
      "cwd": ".",
      "env": {
        "PORT": "3001"
      }
    }
  }
}
```

---

## 10. 常用工作流与实战示例

### 代码理解

```
解释一下这个项目的整体架构

src/auth/ 目录下的认证流程是怎样的？

找出所有调用了 UserService.create() 的地方

这个项目用了哪些设计模式？
```

### 代码编写

```
在 src/components/ 下创建一个 TodoList 组件，使用 TypeScript 和 Tailwind

实现一个 Redis 缓存中间件，支持 TTL 和自动序列化

根据 schema.prisma 生成对应的 CRUD API 路由

帮我实现用户注册接口，包括邮箱验证和密码加密
```

### 代码重构

```
将 src/utils/helpers.js 重构为 TypeScript，添加类型定义

把这个 class 组件重构为函数式组件 + Hooks

这个函数太长了，帮我拆分成更小的函数

移除所有未使用的 import 和变量
```

### Bug 修复

```
npm test 运行失败了，帮我看看什么问题

这个函数在输入为空数组时会崩溃，帮我修复

用户反馈登录后偶尔会被踢出，帮我排查

分析 error.log 中最近的报错并修复
```

### Git 操作

```
查看最近的改动，帮我写一个 commit message

帮我创建一个 feature/user-auth 分支并提交当前改动

比较 main 分支和当前分支的差异，给我一个 PR 描述

帮我解决当前的 merge conflict
```

### 测试

```
为 src/utils/validators.ts 编写单元测试

查看当前的测试覆盖率，补充缺失的测试用例

帮我写一个 E2E 测试，模拟用户注册登录流程

生成 mock 数据用于 API 测试
```

### 文档

```
为这个项目生成 README.md

为所有 public 函数添加 JSDoc 注释

生成 API 文档（OpenAPI/Swagger 格式）

更新 CHANGELOG.md
```

### 文件引用 (`@` 语法)

```
查看 @src/components/Header.tsx 并优化性能

对比 @package.json 和 @package-lock.json 的依赖差异

基于 @schema.prisma 生成 TypeScript 类型
```

---

## 11. 非交互模式 (Headless / CI/CD)

### 基本用法

```bash
# 单次执行并退出
claude -p "describe this project"

# 限制最大轮次
claude -p --max-turns 3 "fix the failing tests"

# 自定义系统提示
claude -p --system-prompt "You are a security auditor" "audit this codebase"

# JSON 输出（适合脚本解析）
claude -p --output-format json "list all TODO comments"
```

### CI/CD 集成示例

```yaml
# GitHub Actions 示例
name: Claude Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: '18'

      - run: npm install -g @anthropic-ai/claude-code

      - name: Code Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          git diff origin/main...HEAD | claude -p \
            --output-format json \
            "Review this PR diff. Focus on bugs, security issues, and performance."
```

### 管道与脚本集成

```bash
# 自动生成 commit message
git diff --staged | claude -p "Generate a conventional commit message for these changes. Output only the commit message."

# 代码审查脚本
#!/bin/bash
for file in $(git diff --name-only HEAD~1); do
  echo "=== Reviewing: $file ==="
  cat "$file" | claude -p "Review this file for potential issues"
  echo ""
done

# 自动修复 lint 错误
npm run lint 2>&1 | claude -p "Fix these lint errors in the project"

# 生成变更日志
git log --oneline v1.0.0..HEAD | claude -p "Generate a CHANGELOG entry from these commits"
```

### 流式 JSON 输入

```bash
# stream-json 格式允许多轮对话
echo '{"type":"user","content":"hello"}' | claude -p --input-format stream-json --output-format stream-json
```

---

## 12. 多 Claude 协作模式

### 使用 Task 工具 (子代理)

Claude Code 可以自动创建子任务代理来并行处理工作：

```
帮我同时完成以下任务：
1. 重构 auth 模块
2. 为 utils 写测试
3. 更新 API 文档
```

### 多实例协作 (手动)

```bash
# 终端1: Claude 负责后端
cd backend && claude "实现用户API"

# 终端2: Claude 负责前端
cd frontend && claude "实现用户界面"

# 终端3: Claude 负责测试
cd tests && claude "编写集成测试"
```

### 通过 Git worktree 并行

```bash
# 创建多个工作树
git worktree add ../project-feature-a feature-a
git worktree add ../project-feature-b feature-b

# 在不同工作树中启动 Claude
cd ../project-feature-a && claude "implement feature A"
cd ../project-feature-b && claude "implement feature B"
```

---

## 13. 自定义 Hooks

Hooks 允许在特定事件发生时运行自定义脚本。

### 配置位置

在 `.claude/settings.json` 或 `~/.claude/settings.json` 中：

```jsonc
{
  "hooks": {
    // 每次通知时运行
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Glass.aiff"
          }
        ]
      }
    ],
    // 写入文件前运行
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'About to write: $CLAUDE_FILE_PATH'"
          }
        ]
      }
    ],
    // 写入文件后运行
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write $CLAUDE_FILE_PATH 2>/dev/null || true"
          }
        ]
      }
    ],
    // 发送消息前
    "PreSubmit": [...],
    // Claude 停止时
    "Stop": [...]
  }
}
```

### Hook 事件类型

| 事件 | 触发时机 | 常见用途 |
|------|----------|----------|
| `PreToolUse` | 工具执行前 | 验证、拦截 |
| `PostToolUse` | 工具执行后 | 格式化、lint |
| `Notification` | 通知触发时 | 自定义通知 |
| `PreSubmit` | 消息发送前 | 输入预处理 |
| `Stop` | Claude 停止响应时 | 后处理、报告 |

### Hook 可用环境变量

| 变量 | 说明 |
|------|------|
| `$CLAUDE_FILE_PATH` | 当前操作的文件路径 |
| `$CLAUDE_TOOL_NAME` | 当前使用的工具名称 |
| `$CLAUDE_TOOL_INPUT` | 工具输入（JSON） |
| `$CLAUDE_SESSION_ID` | 当前会话 ID |
| `$CLAUDE_PROJECT_DIR` | 项目目录 |

### 实用 Hook 示例

```jsonc
{
  "hooks": {
    "PostToolUse": [
      {
        // 写入后自动格式化
        "matcher": "Write|Edit",
        "hooks": [{
          "type": "command",
          "command": "npx prettier --write \"$CLAUDE_FILE_PATH\" 2>/dev/null; npx eslint --fix \"$CLAUDE_FILE_PATH\" 2>/dev/null; true"
        }]
      }
    ],
    "Stop": [
      {
        // 完成后发送桌面通知
        "matcher": "",
        "hooks": [{
          "type": "command",
          "command": "osascript -e 'display notification \"Claude Code 任务完成\" with title \"Claude\"'"
        }]
      }
    ]
  }
}
```

---

## 14. 调试与排障

### 诊断命令

```bash
# 运行健康检查
claude doctor

# 详细日志模式启动
claude --verbose

# 查看当前会话状态
/status
/cost

# 查看可用工具
/tools
```

### 常见问题排查

| 问题 | 解决方案 |
|------|----------|
| `EACCES` 权限错误 | `sudo chown -R $(whoami) ~/.npm ~/.claude` |
| Node.js 版本不够 | 升级到 Node.js 18+: `nvm install 18` |
| 认证失败 | `claude logout` 后重新 `claude login` |
| API Key 无效 | 检查 `echo $ANTHROPIC_API_KEY`，确认未过期 |
| 响应缓慢/超时 | 检查网络/代理，设置 `HTTP_PROXY` |
| 上下文窗口满 | 使用 `/compact` 压缩或 `/clear` 清除 |
| MCP 服务器连不上 | `claude mcp list` 检查状态，重启服务 |
| 工具被拒绝 | 检查 `.claude/settings.json` 权限配置 |
| WSL 问题 | 确保使用 WSL2，`wsl --set-version Ubuntu 2` |

### 日志位置

```bash
# macOS
~/Library/Logs/claude/

# Linux
~/.local/share/claude/logs/

# 或查看
~/.claude/logs/
```

### 重置方法

```bash
# 清除所有配置
rm -rf ~/.claude

# 重新安装
npm uninstall -g @anthropic-ai/claude-code
npm install -g @anthropic-ai/claude-code

# 清除项目级配置
rm -rf .claude/
```

---

## 15. 最佳实践

### 💡 提示词技巧

```markdown
✅ 好的提示：
- "重构 src/auth/login.ts，将密码验证逻辑提取为独立函数，添加单元测试"
- "查看最近 5 次提交，找出可能引入 bug 的改动"
- "基于 @types/User.ts 的类型定义，创建一个用户注册的 REST API"

❌ 不够好的提示：
- "帮我写代码"（太模糊）
- "修复所有 bug"（范围太大）
- "重写整个项目"（不可控）
```

### 🏗️ 项目结构建议

```
project/
├── CLAUDE.md              ← 必备！项目说明和规范
├── .claude/
│   ├── settings.json      ← 权限和工具配置
│   └── CLAUDE.md          ← 个人项目笔记
├── .mcp.json              ← MCP 服务器配置
├── src/
│   ├── CLAUDE.md          ← 子目录特殊说明（可选）
│   └── ...
└── ...
```

### 🔒 安全注意事项

```markdown
1. 永远不要在 CLAUDE.md 中放置密钥/密码
2. 使用 .gitignore 排除 .claude/ 目录中的敏感文件
3. 在 CI/CD 中使用 secrets 管理 API Key
4. 使用 --disallowedTools 禁止危险操作
5. 不在 trusted 模式下运行不可信项目
6. 定期审查 .claude/settings.json 中的权限规则
```

### 🚀 效率提升技巧

```markdown
1. **先写好 CLAUDE.md** - 投入 10 分钟写好项目说明，节省大量对话时间
2. **用 @ 引用文件** - 比口述文件名更准确：`查看 @src/utils/auth.ts`
3. **善用 /compact** - 长对话后压缩上下文，保持响应质量
4. **配置权限白名单** - 避免反复确认常用命令 (git, npm test 等)
5. **管道输入** - `git diff | claude "review"` 比复制粘贴高效
6. **多终端并行** - 不同模块可以用不同 Claude 实例同时处理
7. **使用 -c 恢复会话** - 中断后不必从头开始
8. **Hook 自动化** - 写入后自动格式化/lint，减少手动步骤
9. **具体的指令** - "在第 42 行添加错误处理" 比 "加个错误处理" 好
10. **让 Claude 先读后写** - "先阅读相关文件，然后再修改" 能提高准确性
```

### 📐 上下文管理策略

```markdown
# 保持上下文高效的策略：

1. 单一职责对话 - 每个会话专注一个任务
2. 及时使用 /compact - token 超过 50% 时压缩
3. 大型重构分步进行 - 拆分为多个小会话
4. 利用 CLAUDE.md - 持久化知识减少重复说明
5. /clear 开始新话题 - 避免旧上下文干扰
```

---

## 16. 费用与模型

### 支持的模型

| 模型 | 用途 | 说明 |
|------|------|------|
| `claude-sonnet-4-20250514` | 默认模型 | 速度与能力均衡 |
| `claude-opus-4-20250514` | 复杂任务 | 最强能力，更慢更贵 |

### 查看费用

```bash
# 会话中查看当前费用
/cost

# 输出示例:
# ┌─────────────────────────────────────┐
# │ Input tokens:     45,231   ($0.14)  │
# │ Output tokens:    12,847   ($0.19)  │
# │ Cache read:       128,000  ($0.01)  │
# │ Cache write:      45,231   ($0.06)  │
# │ Total cost:                 $0.40   │
# └─────────────────────────────────────┘
```

### 费用优化建议

```markdown
1. 使用 /compact 减少重复 token 消耗
2. 精准描述需求，减少来回对话
3. 善用 CLAUDE.md 避免每次重复说明项目背景
4. 大文件操作时，指定具体行范围而非整个文件
5. 使用 --max-turns 限制自动化场景的轮次
6. 提示缓存会自动降低重复内容的费用
```

---

## 附录：命令速查表

```
┌──────────────────────────────────────────────────────────────────┐
│                    Claude Code 命令速查                          │
├──────────────────────────────────────────────────────────────────┤
│ 启动与会话                                                       │
│   claude                    启动交互式会话                        │
│   claude "prompt"           带初始提示启动                        │
│   claude -c                 继续上次会话                          │
│   claude -r                 恢复历史会话                          │
│   claude -p "prompt"        非交互执行                           │
├──────────────────────────────────────────────────────────────────┤
│ 会话内命令                                                       │
│   /help                     帮助                                 │
│   /compact                  压缩上下文                           │
│   /clear                    清除上下文                           │
│   /cost                     查看费用                             │
│   /model                    切换模型                             │
│   /memory                   编辑记忆                             │
│   /tools                    查看工具                             │
│   /mcp                      查看 MCP                             │
│   /permissions              管理权限                             │
│   /quit                     退出                                 │
├──────────────────────────────────────────────────────────────────┤
│ 配置管理                                                         │
│   claude config list        列出配置                             │
│   claude config set k v     设置配置                             │
│   claude mcp add            添加 MCP                             │
│   claude mcp list           列出 MCP                             │
│   claude doctor             健康检查                             │
├──────────────────────────────────────────────────────────────────┤
│ 快捷键                                                           │
│   Enter                     发送                                 │
│   Ctrl+C                    中断/取消                            │
│   Ctrl+C ×2                 退出                                 │
│   Esc ×3                    清除输入                             │
│   @filename                 引用文件                             │
└──────────────────────────────────────────────────────────────────┘
```

---

> 📝 **最后更新**: 2025 年 7 月
> 
> 💬 **提示**: 在 Claude Code 中输入 `/help` 随时可以查看内置帮助。
> 
> 🔗 **官方文档**: [docs.anthropic.com/claude-code](https://docs.anthropic.com/en/docs/claude-code)