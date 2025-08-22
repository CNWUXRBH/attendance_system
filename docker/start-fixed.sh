#!/bin/bash

# 考勤系统Docker部署脚本 - 修复版本
# 解决前后端通信问题

echo "🚀 开始部署考勤管理系统..."

# 检查Docker和Docker Compose是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 停止并清理现有容器
echo "🧹 清理现有容器..."
docker-compose down -v

# 清理Docker镜像缓存（可选）
read -p "是否清理Docker镜像缓存？这将重新构建所有镜像 (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️ 清理Docker镜像..."
    docker system prune -f
    docker-compose build --no-cache
fi

# 构建并启动服务
echo "🔨 构建并启动服务..."
docker-compose up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 检查服务健康状态
echo "🏥 检查服务健康状态..."
echo "前端服务状态:"
curl -f http://localhost/ > /dev/null 2>&1 && echo "✅ 前端服务正常" || echo "❌ 前端服务异常"

echo "后端服务状态:"
curl -f http://localhost:8000/health > /dev/null 2>&1 && echo "✅ 后端服务正常" || echo "❌ 后端服务异常"

echo "数据库连接状态:"
docker-compose exec mysql mysqladmin ping -h localhost -u root -p123456 > /dev/null 2>&1 && echo "✅ 数据库连接正常" || echo "❌ 数据库连接异常"

# 显示访问信息
echo ""
echo "🎉 部署完成！"
echo "📱 前端访问地址: http://localhost"
echo "🔧 后端API文档: http://localhost:8000/docs"
echo "🗄️ 数据库端口: localhost:3306"
echo ""
echo "📋 默认管理员账号:"
echo "   用户名: admin"
echo "   密码: admin123"
echo ""
echo "📝 查看日志命令:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 停止服务命令:"
echo "   docker-compose down"