# 多阶段构建

# 阶段1：构建前端
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm config set registry https://registry.npmmirror.com && npm install
COPY frontend/ ./
RUN npm run build

# 阶段2：最终镜像
FROM python:3.11-slim

# 设置时区为北京时间（东八区）——影响历史记录创建时间、日志等所有 datetime.now()
ENV TZ=Asia/Shanghai

# 使用阿里云 Debian 镜像
RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null || true

# 安装 nginx 与时区数据 tzdata，配置时区，创建用户
# DEBIAN_FRONTEND=noninteractive 避免 tzdata 安装时弹出地理区域选择导致构建卡住
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y nginx tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -r -s /sbin/nologin nginx 2>/dev/null || true

WORKDIR /app

# 复制后端代码
COPY backend/ ./backend/

# 安装 Python 依赖（包括 gunicorn），使用清华镜像
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r ./backend/requirements.txt gunicorn

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
