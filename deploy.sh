#!/bin/bash
set -e

echo "=========================================="
echo "AnimeHub VPS 一键部署脚本"
echo "=========================================="
echo ""

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

# 配置变量
PROJECT_DIR="/home/animehub"
DOMAIN="YOUR_DOMAIN"  # 修改为你的域名
GITHUB_REPO=""        # 如果有 Git 仓库，填写此处
ALLOWED_ORIGINS="https://$DOMAIN,https://www.$DOMAIN"  # CORS 允许来源，按需修改
SSH_PORT="${SSH_PORT:-22}"  # SSH 端口，默认22；部署前防火墙会放行，避免开启防火墙后断开远程连接

# 防止使用占位域名上线
if [ "$DOMAIN" = "YOUR_DOMAIN" ]; then
    echo "❌ 请先将 deploy.sh 顶部的 DOMAIN 修改为真实域名后再执行部署。"
    exit 1
fi

echo "【1/8】更新系统并安装基础依赖"
echo "----------------------------------------"
apt update
apt install -y python3 python3-venv python3-pip caddy git curl sudo postgresql postgresql-contrib

# 检查 Node.js 版本，不满足则安装 Node.js 20 LTS
echo ""
echo "检查 Node.js 版本..."
NODE_MAJOR=$(node -v 2>/dev/null | cut -d'v' -f2 | cut -d'.' -f1 || echo "0")
if [ "$NODE_MAJOR" -lt 18 ]; then
    echo "Node.js 版本过低或未安装，安装 Node.js 20 LTS..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
else
    echo "Node.js 版本满足要求: $(node -v)"
fi

echo "Node.js 版本: $(node -v)"
echo "npm 版本: $(npm -v)"

# 获取 npm 实际路径（用于 systemd）
NPM_PATH=$(which npm)
echo "npm 路径: $NPM_PATH"

echo ""
echo "【2/8】创建项目目录"
echo "----------------------------------------"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

echo ""
echo "【3/8】上传项目代码"
echo "----------------------------------------"
if [ -n "$GITHUB_REPO" ]; then
    echo "从 Git 仓库克隆..."
    git clone $GITHUB_REPO .
else
    echo ""
    echo "请上传项目文件到 $PROJECT_DIR"
    echo "推荐方式："
    echo "  本地打包：tar -czf animehub-deploy.tar.gz --exclude=node_modules --exclude=.next --exclude='*.db' --exclude=.venv --exclude='*__pycache__*' --exclude='_tmp*' --exclude='fix_*' anime_data.json backend frontend package-lock.json .env.example README.md"
    echo "  上传：scp animehub-deploy.tar.gz root@$(curl -s ifconfig.me):$PROJECT_DIR/"
    echo ""
        # SKIP_UPLOAD_WAIT=1 用于非交互部署（CI/自动化），跳过等待确认
    if [ -z "$SKIP_UPLOAD_WAIT" ]; then
        read -p "是否已上传完成？(y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo "跳过上传确认（SKIP_UPLOAD_WAIT=1）"
    fi

    # 自动解压上传的压缩包
    if [ -f "$PROJECT_DIR/animehub-deploy.tar.gz" ]; then
        echo "检测到压缩包，自动解压..."
        tar -xzf $PROJECT_DIR/animehub-deploy.tar.gz -C $PROJECT_DIR
    fi

    # 验证项目文件是否存在
    if [ ! -d "$PROJECT_DIR/backend" ] || [ ! -d "$PROJECT_DIR/frontend" ]; then
        echo "❌ 项目文件不存在，请检查上传"
        exit 1
    fi
fi

echo ""
echo "【4/8】配置后端"
echo "----------------------------------------"
cd $PROJECT_DIR/backend

# 生成/读取 SECRET_KEY：已设环境变量则沿用；否则生成并持久化到 /root/.animehub_secret_key
# （避免每次执行脚本重新生成密钥导致已签发 token 全部失效）
if [ -z "$SECRET_KEY" ]; then
    if [ -f /root/.animehub_secret_key ]; then
        SECRET_KEY=$(cat /root/.animehub_secret_key)
    else
        SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n')
        echo "$SECRET_KEY" > /root/.animehub_secret_key
        chmod 600 /root/.animehub_secret_key
    fi
fi
echo "SECRET_KEY 已配置"

# 初始化 PostgreSQL 数据库（幂等：存在则跳过）
echo "初始化 PostgreSQL 数据库..."
service postgresql start 2>/dev/null || true
PG_USER="animehub"
PG_DB="animehub"
PG_PASSWORD_FILE="/root/.animehub_pg_password"
if [ -z "$POSTGRES_PASSWORD" ]; then
    if [ -f "$PG_PASSWORD_FILE" ]; then
        POSTGRES_PASSWORD=$(cat "$PG_PASSWORD_FILE")
    else
        POSTGRES_PASSWORD=$(openssl rand -hex 16 2>/dev/null || head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n')
        echo "$POSTGRES_PASSWORD" > "$PG_PASSWORD_FILE"
        chmod 600 "$PG_PASSWORD_FILE"
    fi
fi
PG_DATABASE_URL="postgresql+psycopg2://$PG_USER:$POSTGRES_PASSWORD@127.0.0.1:5432/$PG_DB"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$PG_USER'" | grep -q 1 \
    || sudo -u postgres psql -c "CREATE USER $PG_USER WITH PASSWORD '$POSTGRES_PASSWORD'"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$PG_DB'" | grep -q 1 \
    || sudo -u postgres psql -c "CREATE DATABASE $PG_DB OWNER $PG_USER;"
echo "PostgreSQL 初始化完成"

# 创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境并安装依赖
echo "安装 Python 依赖..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# 创建 systemd 服务
echo "创建 animehub-api.service..."
cat > /etc/systemd/system/animehub-api.service <<EOF
[Unit]
Description=AnimeHub API Service
After=network.target

[Service]
Type=simple
WorkingDirectory=$PROJECT_DIR/backend
ExecStart=$PROJECT_DIR/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
Environment="PATH=$PROJECT_DIR/backend/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
Environment="ENVIRONMENT=production"
Environment="SECRET_KEY=$SECRET_KEY"
Environment="ALLOWED_ORIGINS=$ALLOWED_ORIGINS"
Environment="DATABASE_URL=$PG_DATABASE_URL"

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "【5/8】配置前端"
echo "----------------------------------------"
cd $PROJECT_DIR/frontend

# 安装依赖
echo "安装 Node.js 依赖..."
npm install

# 生产构建
echo "开始生产构建..."
NEXT_PUBLIC_SITE_URL=https://$DOMAIN \
NEXT_PUBLIC_API_URL=http://localhost:8000 \
npm run build

# 创建 systemd 服务
echo "创建 animehub-frontend.service..."
cat > /etc/systemd/system/animehub-frontend.service <<EOF
[Unit]
Description=AnimeHub Frontend Service
After=network.target animehub-api.service

[Service]
Type=simple
WorkingDirectory=$PROJECT_DIR/frontend
ExecStart=$NPM_PATH start
Restart=always
RestartSec=5
Environment="NODE_ENV=production"
Environment="NEXT_PUBLIC_SITE_URL=https://$DOMAIN"
Environment="NEXT_PUBLIC_API_URL=http://localhost:8000"

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "【6/8】配置 Caddy（HTTPS）"
echo "----------------------------------------"
cat > /etc/caddy/Caddyfile <<EOF
$DOMAIN {
    reverse_proxy localhost:3000
    encode gzip
    header {
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        X-XSS-Protection "1; mode=block"
    }
}

www.$DOMAIN {
    redir https://$DOMAIN{uri} permanent
}
EOF

echo ""
echo "【7/8】启动所有服务"
echo "----------------------------------------"
# 重载 systemd
systemctl daemon-reload

# 启用并启动后端
systemctl enable --now animehub-api
echo "✅ 后端服务已启动"

# 启用并启动前端
systemctl enable --now animehub-frontend
echo "✅ 前端服务已启动"

# 启用并启动 Caddy
systemctl enable --now caddy
echo "✅ Caddy 已启动（HTTPS 自动配置）"

echo ""
echo "【8/8】防火墙配置"
echo "----------------------------------------"
# 在开启防火墙前先放行 SSH，避免防火墙导致远程连接断开
ufw allow ${SSH_PORT}/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "访问地址："
echo "  主页：https://$DOMAIN"
echo "  Sitemap：https://$DOMAIN/sitemap.xml"
echo "  Robots：https://$DOMAIN/robots.txt"
echo ""
echo "服务状态："
echo "  后端：sudo systemctl status animehub-api"
echo "  前端：sudo systemctl status animehub-frontend"
echo "  Caddy：sudo systemctl status caddy"
echo ""
echo "日志查看："
echo "  后端：sudo journalctl -u animehub-api -f"
echo "  前端：sudo journalctl -u animehub-frontend -f"
echo "  Caddy：sudo journalctl -u caddy -f"
echo ""
echo "下一步："
echo "  1. 访问 https://$DOMAIN 确认网站正常"
echo "  2. 访问 https://$DOMAIN/sitemap.xml 确认 sitemap 正常"
echo "  3. 在 Google Search Console 提交 sitemap"
echo ""