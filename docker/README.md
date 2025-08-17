# 考勤系统 Docker 部署指南

## 概述

本目录包含考勤系统的生产环境Docker部署配置，使用多阶段构建优化前端性能，并通过nginx提供静态文件服务。

## 文件说明

- `docker-compose.yml` - Docker Compose配置文件
- `start-docker.sh` - 一键启动脚本
- `README.md` - 本说明文档

## 架构说明

### 前端服务
- **构建方式**: 多阶段构建
- **第一阶段**: 使用Node.js构建React应用
- **第二阶段**: 使用nginx提供静态文件服务
- **端口**: 80
- **特性**: 
  - Gzip压缩
  - 静态资源缓存
  - API代理到后端
  - React路由支持
  - 安全头配置

### 后端服务
- **技术栈**: Python + FastAPI
- **端口**: 8000
- **数据库**: MySQL 8.0

### 数据库服务
- **类型**: MySQL 8.0
- **端口**: 3306
- **持久化**: Docker volume

## 快速开始

### 前置要求

- Docker Desktop
- Docker Compose

### 一键启动

```bash
# 进入docker目录
cd docker

# 运行启动脚本
./start-docker.sh
```

### 手动启动

```bash
# 进入docker目录
cd docker

# 构建并启动所有服务
docker-compose up --build -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 访问地址

- **前端应用**: http://localhost
- **后端API**: http://localhost:8000
- **数据库**: localhost:3306

## 常用命令

```bash
# 停止所有服务
docker-compose down

# 重新构建并启动
docker-compose up --build

# 查看实时日志
docker-compose logs -f [service_name]

# 进入容器
docker-compose exec [service_name] sh

# 清理所有数据（包括数据库）
docker-compose down -v
```

## 生产环境优化

### 前端优化
- ✅ 多阶段构建减少镜像大小
- ✅ nginx静态文件服务
- ✅ Gzip压缩
- ✅ 静态资源缓存
- ✅ 安全头配置

### 后端优化
- ✅ 生产级WSGI服务器
- ✅ 环境变量配置
- ✅ 健康检查
- ✅ 自动重启

### 数据库优化
- ✅ 数据持久化
- ✅ 初始化脚本
- ✅ 用户权限配置

## 故障排除

### 常见问题

1. **端口冲突**
   - 确保80、8000、3306端口未被占用
   - 可在docker-compose.yml中修改端口映射

2. **构建失败**
   - 检查Docker Desktop是否正常运行
   - 清理Docker缓存: `docker system prune -a`

3. **数据库连接失败**
   - 等待MySQL完全启动（约30秒）
   - 检查数据库环境变量配置

4. **前端无法访问后端API**
   - 检查nginx配置中的代理设置
   - 确认后端服务正常运行

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs frontend
docker-compose logs backend
docker-compose logs mysql
```

## 环境变量配置

系统支持通过环境变量进行配置。生产环境配置文件位于 `.env.production`：

### 前端环境变量
- `REACT_APP_API_URL`: API服务地址，Docker环境中使用 `/api`（通过nginx代理）

### 后端环境变量
- `DATABASE_URL`: 数据库连接字符串，Docker环境中使用 `mysql+pymysql://root:123456@mysql:3306/attendance_system`
- `SECRET_KEY`: JWT密钥
- `ALGORITHM`: 加密算法
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token过期时间

### 数据库环境变量
- `MYSQL_ROOT_PASSWORD`: MySQL root密码
- `MYSQL_DATABASE`: 数据库名称

## 网络配置说明

### Docker容器间通信
- 前端容器通过nginx代理访问后端：`/api` -> `http://backend:8000`
- 后端容器通过服务名访问数据库：`mysql:3306`
- 所有服务在同一个Docker网络中，使用服务名进行通信

### 外部访问
- **本地开发**：`http://localhost`
- **服务器部署**：`http://your-server-ip`
- 端口映射：前端80端口，后端8000端口，数据库3306端口

### 生产环境部署注意事项
1. 修改 `.env.production` 中的敏感信息（密码、密钥等）
2. 如果部署到云服务器，确保防火墙开放相应端口
3. 建议使用域名和SSL证书进行HTTPS访问
4. 数据库建议使用外部托管服务或独立部署