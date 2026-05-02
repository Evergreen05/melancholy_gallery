# 🌙 忧郁画廊 · Melancholy Gallery

一个动漫忧郁风格的图片在线浏览网站。

## 技术栈

- **后端**: Django 6 + SQLite + Gunicorn
- **前端**: Django 模板引擎 + 原生 CSS 动画
- **部署**: Gunicorn + Nginx (Ubuntu)

## 功能

- ✅ 用户注册 / 登录 / 登出 / 个人中心
- ✅ 头像上传
- ✅ 图片上传（仅图片格式，限 20MB）
- ✅ 图片标题 + 描述
- ✅ 游客可浏览，登录用户可上传
- ✅ 评论功能（1-500 字符）
- ✅ 点赞 / 取消点赞
- ✅ 收藏 / 取消收藏
- ✅ 个人中心查看收藏列表
- ✅ 权限控制：用户只能删除自己的内容
- ✅ 管理员可管理所有内容
- ✅ Django Admin 后台
- ✅ 管理员可控制用户上传/评论权限
- ✅ 动漫忧郁风格前端（雨滴 + 樱花 + 深蓝灰配色）

## 前端配色

| 用途 | 颜色 |
|------|------|
| 背景 | `#1a1b2e` 深蓝灰 |
| 主色 | `#6c6ea0` 紫蓝 |
| 辅色 | `#c08497` 冷粉 |
| 文字 | `#d4d4e8` 月光白 |

## 数据库模型

- **User**: Django 内置 + Profile 扩展（can_upload, can_comment）
- **Image**: 图片（标题、描述、作者、时间）
- **Comment**: 评论（关联图片和用户）
- **Like**: 点赞（用户-图片唯一约束）
- **Favorite**: 收藏（用户-图片唯一约束）

## 本地开发

```bash
pip install django pillow
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 部署到 Ubuntu 服务器

```bash
# 1. 上传项目到服务器
scp -r melancholy_gallery/ root@your-server:/opt/

# 2. 运行部署脚本
ssh root@your-server
cd /opt/melancholy_gallery
chmod +x deploy/deploy.sh
sudo bash deploy/deploy.sh
```

部署脚本会自动：
- 安装系统依赖（Python3、Nginx、SQLite）
- 创建虚拟环境
- 运行 Django 迁移
- 配置 Gunicorn systemd 服务
- 配置 Nginx 反向代理

## 默认管理员

- 用户名: `admin`
- 密码: `admin123`
- ⚠️ 请登录后立即修改密码！

## 目录结构

```
melancholy_gallery/
├── config/          # Django 项目配置
├── gallery/         # 主应用
├── templates/       # 模板
│   ├── base.html
│   ├── gallery/
│   └── registration/
├── static/          # 静态文件
│   ├── css/style.css
│   └── js/main.js
├── media/           # 用户上传
├── deploy/          # 部署配置
└── manage.py
```

## 管理后台

访问 `/admin/` 可以：
- 管理用户（禁用/删除）
- 管理图片和评论
- 控制用户上传/评论权限
- 批量操作（禁用用户、禁止上传等）
