#!/bin/bash
# Mini-Dify 启动脚本

set -e

echo "🚀 启动 Mini-Dify..."

# 1. 启动基础服务
echo "📦 启动 PostgreSQL + Milvus..."
docker compose -f docker/docker-compose.yaml up -d postgres milvus

# 等待服务就绪
echo "⏳ 等待服务就绪..."
sleep 5

# 2. 启动后端
echo "🐍 启动后端..."
cd backend
source venv/bin/activate 2>/dev/null || (python3.12 -m venv venv && source venv/bin/activate)
pip install -r requirements.txt -q
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 3. 启动前端
echo "⚛️  启动前端..."
cd frontend
pnpm install -s
pnpm dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Mini-Dify 启动完成!"
echo "   前端: http://localhost:5173"
echo "   API:  http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker compose -f docker/docker-compose.yaml stop; exit 0" SIGINT SIGTERM
wait
