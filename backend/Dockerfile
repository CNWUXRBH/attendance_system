# 使用官方 Python 运行时作为父镜像
FROM python:3.12-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 设置 debconf 前端为非交互式
ENV DEBIAN_FRONTEND=noninteractive

# 安装系统依赖和 Microsoft ODBC Driver
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" | tee /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && ACCEPT_EULA=Y apt-get install -y mssql-tools18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置容器中的工作目录
WORKDIR /app

# 复制依赖文件并安装依赖
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 创建非root用户和logs目录
RUN adduser --disabled-password --gecos '' appuser && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app
USER appuser

# 复制应用程序代码
COPY --chown=appuser:appuser . .

# 暴露应用程序运行的端口
EXPOSE 3001

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3001/health || exit 1

# 定义运行应用程序的命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3001"]