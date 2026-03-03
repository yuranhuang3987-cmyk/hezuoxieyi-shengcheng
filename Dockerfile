# 多阶段构建

# 阶段1：构建前端
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# 阶段2：构建后端
FROM python:3.11-slim AS backend-builder

WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# 阶段3：最终镜像
FROM python:3.11-slim

# 安装 nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制后端代码和依赖
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY backend/ ./backend/

# 复制前端构建产物
COPY --from=frontend-builder /app/frontend/build /var/www/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 复制启动脚本
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# 创建必要的目录
RUN mkdir -p /app/backend/uploads /app/backend/outputs /app/backend/templates /app/database

# 暴露端口
EXPOSE 80

# 启动命令
CMD ["/app/start.sh"]
