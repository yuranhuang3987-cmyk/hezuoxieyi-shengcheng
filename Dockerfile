# 多阶段构建

# 阶段1：构建前端
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# 阶段2：最终镜像
FROM python:3.11-slim

# 安装 nginx，创建用户
RUN apt-get update && \
    apt-get install -y nginx && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -r -s /sbin/nologin nginx 2>/dev/null || true

WORKDIR /app

# 复制后端代码
COPY backend/ ./backend/

# 安装 Python 依赖（包括 gunicorn）
RUN pip install --no-cache-dir -r ./backend/requirements.txt gunicorn

# 复制前端构建产物
COPY --from=frontend-builder /app/frontend/build /var/www/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 复制启动脚本
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# 创建必要的目录
RUN mkdir -p /app/backend/uploads /app/backend/outputs /app/backend/templates /app/database /app/backend/flask_session

# 暴露端口
EXPOSE 80

# 启动命令
CMD ["/app/start.sh"]
