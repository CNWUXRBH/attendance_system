# 使用官方 Python 运行时作为父镜像
FROM python:3.12-slim

# 设置容器中的工作目录
WORKDIR /app

# 复制依赖文件并安装依赖
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序代码
COPY . .

# 暴露应用程序运行的端口
EXPOSE 8000

# 定义运行应用程序的命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]