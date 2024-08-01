#!/bin/bash

# 读取环境变量
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env 文件不存在。"
    exit 1
fi

DOMAIN_NAME=$DOMAIN

# 确保 pyenv 正确加载
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# 定义变量
PROJECT_NAME="reflective_jornal"
PROJECT_DIR=$(pwd)
USER=$(whoami)

echo "使用域名: $DOMAIN_NAME"

# 安装 Python 和依赖
pyenv install 3.10.14
pyenv local 3.10.14
pip install --upgrade pip
pip install -r requirements.txt

# 数据库迁移
echo "开始数据库迁移..."
python manage.py makemigrations || { echo "makemigrations 失败"; exit 1; }
python manage.py migrate || { echo "migrate 失败"; exit 1; }
echo "数据库迁移完成"

# 收集静态文件
echo "开始收集静态文件..."
python manage.py collectstatic --noinput || { echo "收集静态文件失败"; exit 1; }
echo "静态文件收集完成"

# 创建gunicorn.socket文件
echo "创建 gunicorn.socket 文件..."
sudo tee /etc/systemd/system/gunicorn.socket > /dev/null <<EOF
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=${PROJECT_DIR}/gunicorn.sock

[Install]
WantedBy=sockets.target
EOF

# 创建gunicorn.service文件
echo "创建 gunicorn.service 文件..."
sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=${USER}
Group=www-data
WorkingDirectory=${PROJECT_DIR}
ExecStart=$(pyenv which gunicorn) \
          --access-logfile - \
          --workers 3 \
          --bind unix:${PROJECT_DIR}/gunicorn.sock \
          ${PROJECT_NAME}.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# 启动gunicorn
echo "启动 gunicorn..."
sudo systemctl start gunicorn.socket || { echo "启动 gunicorn.socket 失败"; exit 1; }
sudo systemctl enable gunicorn.socket || { echo "启用 gunicorn.socket 失败"; exit 1; }

# 配置nginx
echo "配置 Nginx..."
sudo tee /etc/nginx/sites-available/${PROJECT_NAME} > /dev/null <<EOF
server {
    listen 80;
    server_name ${DOMAIN_NAME};

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        alias ${PROJECT_DIR}/static/;
    }

    location /media/ {
        alias ${PROJECT_DIR}/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$(pwd)/gunicorn.sock;
    }
}
EOF

sudo rm -f /etc/nginx/sites-enabled/${PROJECT_NAME}
sudo ln -s /etc/nginx/sites-available/${PROJECT_NAME} /etc/nginx/sites-enabled || { echo "创建 Nginx 符号链接失败"; exit 1; }
sudo nginx -t || { echo "Nginx 配置测试失败"; exit 1; }
sudo systemctl restart nginx || { echo "重启 Nginx 失败"; exit 1; }

# 配置防火墙
echo "配置防火墙..."
sudo apt install ufw -y
sudo ufw enable || { echo "启用 ufw 失败"; exit 1; }
sudo ufw default deny
sudo ufw allow 'Nginx Full' || { echo "配置防火墙规则失败"; exit 1; }

# 安装 Certbot 并配置 HTTPS
echo "配置 HTTPS..."
sudo apt install certbot python3-certbot-nginx -y

# 提示用户输入邮箱地址
read -p "请输入您的邮箱地址（用于Let's Encrypt通知）: " EMAIL_ADDRESS

sudo certbot --nginx -d ${DOMAIN_NAME} --non-interactive --agree-tos --email $EMAIL_ADDRESS || { echo "获取 SSL 证书失败"; exit 1; }
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo "部署完成！"