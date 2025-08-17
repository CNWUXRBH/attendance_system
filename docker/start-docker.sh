#!/bin/bash

# 考勤系统Docker一键启动脚本

echo "🚀 正在启动考勤系统..."
echo "================================"

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker Desktop"
    exit 1
fi

# 停止并删除现有容器（如果存在）
echo "🧹 清理现有容器..."
docker-compose down

# 构建并启动服务
echo "🔨 构建并启动服务..."
docker-compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

echo "================================"
echo "✅ 考勤系统启动完成！"
echo "🌐 前端地址: http://localhost (或 http://your-server-ip)"
echo "🔧 后端API: http://localhost:8000 (或 http://your-server-ip:8000)"
echo "🗄️  数据库: localhost:3306 (或 your-server-ip:3306)"
echo "================================"
echo "💡 使用 'docker-compose logs -f' 查看日志"
echo "🛑 使用 'docker-compose down' 停止服务"