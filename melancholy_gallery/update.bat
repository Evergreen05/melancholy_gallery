@echo off
REM ═══════════════════════════════════════════
REM 忧郁画廊 · 一键更新到服务器 (Windows)
REM 用法: update.bat 服务器IP
REM ═══════════════════════════════════════════

if "%~1"=="" (
    echo 用法: update.bat 服务器IP
    exit /b 1
)

set SERVER=%~1
set REMOTE_DIR=/opt/melancholy_gallery

echo 🌙 同步文件到 %SERVER% ...

scp -r config gallery templates static nginx manage.py requirements.txt Dockerfile docker-compose.yml entrypoint.sh .dockerignore .env.example deploy root@%SERVER%:%REMOTE_DIR/

echo 🔨 重建并重启容器 ...
ssh root@%SERVER% "cd %REMOTE_DIR% && docker compose up -d --build"

echo ✅ 更新完成！
