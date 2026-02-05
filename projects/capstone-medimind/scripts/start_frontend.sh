#!/bin/bash
# MediMind 前端启动脚本
# 运行前端开发服务器（前台运行，不退出）

set -e

# 获取项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

FRONTEND_DIR="$PROJECT_ROOT/frontend/apps/web"

# 检查前端目录
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ 错误: 前端目录不存在: $FRONTEND_DIR"
    exit 1
fi

cd "$FRONTEND_DIR"

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    pnpm install
    echo ""
fi

echo "🚀 启动 MediMind 前端..."
echo ""
echo "🎨 前端开发服务器"
echo "   地址: http://localhost:5173"
echo ""
echo "💡 按 Ctrl+C 停止服务"
echo ""
echo "----------------------------------------"
echo ""

# 前台运行前端（不退出）
exec pnpm run dev
