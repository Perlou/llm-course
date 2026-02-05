#!/bin/bash
# MediMind 项目启动脚本
# 启动后端 API 和前端开发服务器

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 启动 MediMind..."

# 创建日志目录
mkdir -p logs

# 启动后端
echo "📡 启动后端 API (http://localhost:8000)..."
source venv/bin/activate
nohup python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > .backend.pid
echo "   后端 PID: $BACKEND_PID"

# 等待后端启动
sleep 2

# 启动前端
echo "🎨 启动前端 (http://localhost:5173)..."
cd frontend/apps/web
nohup npm run dev > ../../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../../../.frontend.pid
echo "   前端 PID: $FRONTEND_PID"

cd "$PROJECT_ROOT"

echo ""
echo "✅ MediMind 启动完成!"
echo ""
echo "📍 访问地址:"
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo ""
echo "📋 日志文件:"
echo "   后端: logs/backend.log"
echo "   前端: logs/frontend.log"
echo ""
echo "💡 停止服务: ./stop.sh"
