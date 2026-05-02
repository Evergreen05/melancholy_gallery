#!/bin/bash
# ═══════════════════════════════════════════
# 忧郁画廊 · 一键更新到服务器
# 用法: bash update.sh 服务器IP
# ═══════════════════════════════════════════
set -e

SERVER=${1:?用法: bash update.sh 服务器IP}
REMOTE_DIR="/opt/melancholy_gallery"

echo "🌙 同步文件到 $SERVER ..."
rsync -avz \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='db.sqlite3' \
    --exclude='media' \
    --exclude='staticfiles' \
    --exclude='.idea' \
    --exclude='.git' \
    --exclude='*.pyc' \
    "$(dirname "$0")/" "root@$SERVER:$REMOTE_DIR/"

echo "🔨 重建并重启容器 ..."
ssh root@$SERVER "cd $REMOTE_DIR && docker compose up -d --build"

echo "✅ 更新完成！"
