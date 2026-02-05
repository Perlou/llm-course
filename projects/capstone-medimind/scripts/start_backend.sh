#!/bin/bash
# MediMind 后端启动脚本
# 运行后端 API 服务器（前台运行，不退出）

set -e

# 获取项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 启动 MediMind 后端..."
echo ""

# 创建日志目录
mkdir -p logs

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 错误: 虚拟环境不存在，请先运行 python -m venv venv"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

echo "📡 后端 API 服务器"
echo "   地址: http://localhost:8000"
echo "   文档: http://localhost:8000/docs"
echo ""
echo "💡 按 Ctrl+C 停止服务"
echo ""
echo "----------------------------------------"
echo ""

# 前台运行后端（不退出）
exec python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
