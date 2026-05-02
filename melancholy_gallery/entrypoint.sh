#!/bin/bash
set -e

echo "🌙 忧郁画廊 · 启动中..."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ -z "$DJANGO_SUPERUSER_USERNAME" ]; then
    DJANGO_SUPERUSER_USERNAME="admin"
fi
if [ -z "$DJANGO_SUPERUSER_PASSWORD" ]; then
    DJANGO_SUPERUSER_PASSWORD="admin123"
fi

python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists():
    User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', 'admin@localhost', '${DJANGO_SUPERUSER_PASSWORD}')
    print('管理员已创建: ${DJANGO_SUPERUSER_USERNAME}')
else:
    print('管理员已存在')
"

mkdir -p /app/db
mkdir -p /app/media/avatars /app/media/images /app/media/videos

echo "启动 Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
