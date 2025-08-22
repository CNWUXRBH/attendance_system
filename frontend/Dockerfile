# 多阶段构建 - 构建阶段
FROM node:18-alpine AS build

# 设置工作目录
WORKDIR /app

# 接收构建时 API 基础路径参数并注入到环境变量，供 CRA 构建使用
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖（包括开发依赖）
RUN npm ci

# 复制项目文件
COPY . .

# 构建生产版本（会读取上面注入的 REACT_APP_API_URL）
RUN npm run build

# 生产阶段 - 使用nginx提供静态文件服务
FROM nginx:alpine

# 安装curl用于健康检查
RUN apk add --no-cache curl

# 复制构建好的文件到nginx目录
COPY --from=build /app/build /usr/share/nginx/html

# 复制nginx配置文件
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 3000

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]