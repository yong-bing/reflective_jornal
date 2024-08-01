# #!/bin/bash

sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install git nginx -y
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
     libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev \
     xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
     libmysqlclient-dev default-libmysqlclient-dev pkg-config

# 安装 pyenv
curl https://pyenv.run | bash

# 将 pyenv 相关的设置添加到 .bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

echo "pyenv 已安装。请运行以下命令来完成设置："
echo "source ~/.bashrc"
echo "然后运行 deploy.sh 脚本来完成剩余的部署步骤。"