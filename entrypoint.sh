#!/bin/bash
set -e

# 配置
LOG_DIR="./logs"
GUNICORN_WORKERS=${GUNICORN_WORKERS:-3}
GUNICORN_PORT=${GUNICORN_PORT:-8000}

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# 错误处理函数
handle_error() {
    log "错误: $1"
    exit 1
}

# 等待数据库准备就绪
wait_for_db() {
    log "等待数据库就绪..."
    for i in {1..30}; do
        if python ./manage.py check --database default > /dev/null 2>&1; then
            log "数据库就绪"
            return 0
        fi
        log "数据库未就绪，等待 5 秒..."
        sleep 5
    done
    handle_error "数据库连接超时"
}


# 主函数
main() {
    log "开始部署"

    # 创建必要的目录
    mkdir -p $LOG_DIR
    log "已创建日志目录"

    # 应用数据库迁移
    log "开始应用数据库迁移"
    wait_for_db
    python ./manage.py makemigrations || handle_error "创建数据库迁移失败"
    python ./manage.py migrate || handle_error "应用数据库迁移失败"
    log "数据库迁移完成"

    # 收集静态文件
    log "开始收集静态文件"
    python ./manage.py collectstatic --noinput || handle_error "收集静态文件失败"
    log "静态文件收集完成"

    # 清理旧的 Gunicorn 进程
    pkill gunicorn || true
    log "已清理旧的 Gunicorn 进程"

    # 启动 Gunicorn
    log "启动 Gunicorn"
    exec gunicorn reflective_jornal.wsgi:application \
        --bind 0.0.0.0:$GUNICORN_PORT \
        --workers $GUNICORN_WORKERS \
        --access-logfile $LOG_DIR/gunicorn-access.log \
        --error-logfile $LOG_DIR/gunicorn-error.log \
        --capture-output \
        --log-level info
}

# 运行主函数
main