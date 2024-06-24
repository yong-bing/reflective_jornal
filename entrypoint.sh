#!/bin/bash
set -e

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "开始部署流程"

# 从环境变量加载配置
source /app/.env
log "已加载环境变量"

# 配置 Nginx
envsubst < /app/nginx.conf.template > /etc/nginx/nginx.conf
log "已生成 Nginx 配置"

# 创建日志目录
mkdir -p /app/logs
log "已创建日志目录"

# 应用数据库迁移
log "开始应用数据库迁移"
python manage.py migrate
log "数据库迁移完成"

# 收集静态文件
log "开始收集静态文件"
python manage.py collectstatic --noinput
log "静态文件收集完成"

# 启动 Gunicorn
log "启动 Gunicorn"
gunicorn your_project.wsgi:application --bind 0.0.0.0:8000 \
    --access-logfile /app/logs/gunicorn-access.log \
    --error-logfile /app/logs/gunicorn-error.log \
    --capture-output \
    --log-level info &

# 启动 Nginx
log "启动 Nginx"
nginx -g 'daemon off;'