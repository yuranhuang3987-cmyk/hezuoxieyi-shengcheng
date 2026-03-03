#!/bin/bash

# 启动后端
cd /app/backend
gunicorn -w 4 -b 127.0.0.1:5000 app:app &

# 启动 nginx
nginx -g 'daemon off;'
