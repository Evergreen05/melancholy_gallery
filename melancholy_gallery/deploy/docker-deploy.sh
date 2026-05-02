#!/bin/bash
# ═══════════════════════════════════════════
# 忧郁画廊 · Docker 一键部署脚本
# 适用于 Ubuntu 22.04 / 24.04
# ═══════════════════════════════════════════
set -e

echo "🌙 忧郁画廊 · Docker 部署"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. 安装 Docker
if ! command -v docker &> /dev/null; then
    echo "📦 安装 Docker..."
    apt-get update
    apt-get install -y ca-certificates curl gnupg
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl enable docker
    systemctl start docker
    echo "✅ Docker 安装完成"
else
    echo "✅ Docker 已安装"
fi

# 2. 进入项目目录
cd "$(dirname "$0")"

# 3. 创建 .env（如果不存在）
if [ ! -f .env ]; then
    echo "📝 创建 .env 配置..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    cat > .env << EOF
DJANGO_SECRET_KEY=${SECRET_KEY}
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=*
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=admin123
EOF
    echo "   默认管理员: admin / admin123"
    echo "   ⚠️  请修改 .env 中的密码！"
fi

# 4. 构建并启动
echo "🔨 构建 Docker 镜像..."
docker compose build

echo "🚀 启动服务..."
docker compose up -d

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 部署完成！"
echo ""
echo "🌐 访问地址: http://$(hostname -I | awk '{print $1}')"
echo "🔧 管理后台: http://$(hostname -I | awk '{print $1}')/admin/"
echo ""
echo "常用命令:"
echo "  查看日志: docker compose logs -f"
echo "  停止服务: docker compose down"
echo "  重启服务: docker compose restart"
echo "  进入容器: docker compose exec web bash"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
