#!/bin/bash
# ═══════════════════════════════════════════
# 忧郁画廊 · 一键部署脚本
# 适用于 Ubuntu 22.04 / 24.04
# ═══════════════════════════════════════════
set -e

APP_DIR="/opt/melancholy_gallery"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🌙 忧郁画廊 · 部署开始"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. 系统依赖
echo "📦 安装系统依赖..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv nginx sqlite3

# 2. 创建应用目录
echo "📂 复制项目文件..."
mkdir -p "$APP_DIR"
rsync -av --exclude='venv' --exclude='__pycache__' --exclude='db.sqlite3' \
    "$REPO_DIR/" "$APP_DIR/"

# 3. Python 虚拟环境
echo "🐍 创建虚拟环境..."
cd "$APP_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --quiet django pillow gunicorn

# 4. Django 初始化
echo "⚙️  Django 初始化..."
python manage.py collectstatic --noinput 2>/dev/null || true
python manage.py migrate --noinput

# 5. 创建超级用户（如果不存在）
if ! python -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists()" 2>/dev/null | grep -q True; then
    echo "👤 创建管理员账号..."
    DJANGO_SUPERUSER_PASSWORD=admin123 python manage.py createsuperuser --username admin --email admin@localhost --noinput
    echo "   默认管理员: admin / admin123"
    echo "   ⚠️  请登录后立即修改密码！"
fi

# 6. 文件权限
echo "🔒 设置文件权限..."
chown -R www-data:www-data "$APP_DIR/media"
chmod -R 755 "$APP_DIR/media"

# 7. Gunicorn 服务
echo "🚀 配置 Gunicorn..."
cp "$APP_DIR/deploy/gunicorn-melancholy.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable gunicorn-melancholy
systemctl restart gunicorn-melancholy

# 8. Nginx 配置
echo "🌐 配置 Nginx..."
cp "$APP_DIR/deploy/melancholy-nginx.conf" /etc/nginx/sites-available/melancholy
ln -sf /etc/nginx/sites-available/melancholy /etc/nginx/sites-enabled/melancholy
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 部署完成！"
echo ""
echo "🌐 访问地址: http://$(hostname -I | awk '{print $1}')"
echo "🔧 管理后台: http://$(hostname -I | awk '{print $1}')/admin/"
echo "👤 管理账号: admin / admin123"
echo ""
echo "📁 应用目录: $APP_DIR"
echo "📊 查看日志: journalctl -u gunicorn-melancholy -f"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
