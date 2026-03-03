# Docker 部署指南

## 快速开始

### 方式一：使用 docker-compose（推荐）

```bash
# 构建并启动
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方式二：手动构建

```bash
# 构建镜像
docker build -t agreement-generator .

# 运行容器
docker run -d -p 80:80 --name agreement-generator agreement-generator

# 查看日志
docker logs -f agreement-generator

# 停止容器
docker stop agreement-generator
```

## 访问

- 前端：http://localhost
- 管理员登录：huang777 / huang777

## 数据持久化

docker-compose.yml 已配置数据持久化：
- `./data`：数据库文件
- `./uploads`：上传的 Excel 文件
- `./outputs`：生成的协议文件

## 常用命令

| 操作 | 命令 |
|-----|------|
| 启动服务 | `docker-compose up -d` |
| 停止服务 | `docker-compose down` |
| 重启服务 | `docker-compose restart` |
| 查看日志 | `docker-compose logs -f` |
| 进入容器 | `docker exec -it agreement-generator bash` |
| 重新构建 | `docker-compose up -d --build` |

## 服务器部署

### 1. 安装 Docker

```bash
curl -fsSL https://get.docker.com | bash
systemctl start docker
systemctl enable docker
```

### 2. 安装 docker-compose

```bash
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### 3. 克隆代码

```bash
git clone https://github.com/yuranhuang3987-cmyk/hezuoxieyi-shengcheng.git
cd hezuoxieyi-shengcheng
```

### 4. 启动服务

```bash
docker-compose up -d --build
```

### 5. 防火墙放行

```bash
ufw allow 80
ufw allow 443
```

## HTTPS 配置（可选）

### 使用 Caddy（自动 HTTPS）

```yaml
# docker-compose.yml 添加 Caddy 服务
version: '3.8'

services:
  caddy:
    image: caddy:2
    container_name: caddy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
    restart: unless-stopped

  agreement-generator:
    build: .
    container_name: agreement-generator
    expose:
      - "80"
    volumes:
      - ./data:/app/backend/data
      - ./uploads:/app/backend/uploads
      - ./outputs:/app/backend/outputs
    restart: unless-stopped

volumes:
  caddy_data:
```

### Caddyfile 示例

```
your-domain.com {
    reverse_proxy agreement-generator:80
}
```

启动：
```bash
docker-compose up -d
```

Caddy 会自动申请并续期 HTTPS 证书。
