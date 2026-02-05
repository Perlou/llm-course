#!/bin/bash
# MediMind 项目状态检查脚本

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📊 MediMind 服务状态"
echo ""

# 检查后端
BACKEND_RUNNING=false
if lsof -ti:8000 > /dev/null 2>&1; then
    BACKEND_RUNNING=true
    echo "✅ 后端 API: 运行中 (http://localhost:8000)"
else
    echo "❌ 后端 API: 未运行"
fi

# 检查前端
FRONTEND_RUNNING=false
if lsof -ti:5173 > /dev/null 2>&1; then
    FRONTEND_RUNNING=true
    echo "✅ 前端 Web: 运行中 (http://localhost:5173)"
else
    echo "❌ 前端 Web: 未运行"
fi

echo ""
if $BACKEND_RUNNING && $FRONTEND_RUNNING; then
    echo "🟢 所有服务正常运行"
elif $BACKEND_RUNNING || $FRONTEND_RUNNING; then
    echo "🟡 部分服务运行中"
else
    echo "🔴 服务未启动，运行 ./scripts/start.sh 启动"
fi
