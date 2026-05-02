# 🌙 忧郁画廊 · Melancholy Gallery

一个动漫忧郁风格的图画与影像在线浏览平台。在孤独的雨夜里，每一帧画面都是一首未完的诗。

## 技术栈

- **后端**: Django 6 + SQLite + Gunicorn
- **前端**: Django 模板引擎 + 原生 CSS 动画 + 原生 JavaScript
- **视频处理**: MoviePy + FFmpeg（自动生成封面）
- **部署**: Docker + Nginx

## 功能一览

### 用户系统
- ✅ 邮箱注册 / 邮箱登录
- ✅ 修改用户名、头像、个性签名
- ✅ 用户互相关注 / 粉丝列表
- ✅ 私信系统（收件箱、对话气泡）
- ✅ 未读私信角标提醒

### 图画馆
- ✅ 图画上传（JPG / PNG / GIF / WebP，限 20MB）
- ✅ 图画标题 + 描述
- ✅ 上传进度条
- ✅ 图画馆按点赞量排序
- ✅ 首页展示最新 3 张

### 影像馆
- ✅ 视频上传（MP4 / WebM / OGG / MOV / AVI / MKV，限 200MB）
- ✅ 上传进度条
- ✅ 未传封面时自动截取视频首帧
- ✅ HTML5 在线播放器
- ✅ 影像馆按点赞量排序
- ✅ 首页展示最新 3 个

### 互动功能
- ✅ 评论功能（1-500 字符）
- ✅ 点赞 / 取消点赞（AJAX 无刷新）
- ✅ 收藏 / 取消收藏（AJAX 无刷新）
- ✅ 个人中心查看收藏列表

### 权限与管理
- ✅ 游客可浏览，登录用户可上传
- ✅ 用户只能删除自己的内容
- ✅ 管理员可管理所有内容
- ✅ 管理员可控制用户上传/评论权限
- ✅ Django Admin 后台

### 前端特效
- ✅ 雨滴动画背景
- ✅ 樱花飘落效果
- ✅ 动漫忧郁风格配色
- ✅ 响应式布局（支持手机端）

## 前端配色

| 用途 | 颜色 |
|------|------|
| 背景 | `#1a1b2e` 深蓝灰 |
| 主色 | `#6c6ea0` 紫蓝 |
| 辅色 | `#c08497` 冷粉 |
| 文字 | `#d4d4e8` 月光白 |

## 数据库模型

- **User**: Django 内置 + Profile 扩展（bio, avatar, can_upload, can_comment）
- **Image**: 图画（标题、描述、作者、时间）
- **Video**: 视频（标题、描述、视频文件、封面、作者、时间）
- **Comment / VideoComment**: 评论
- **Like / VideoLike**: 点赞（唯一约束）
- **Favorite / VideoFavorite**: 收藏（唯一约束）
- **Follow**: 关注关系（粉丝-被关注者唯一约束）
- **Message**: 私信（发送者、接收者、已读状态）

## 本地开发

```bash
# 安装依赖
pip install django pillow moviepy

# 迁移数据库
python manage.py migrate

# 创建管理员
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

## Docker 部署

### 一键部署

```bash
# 上传项目到服务器
scp -r melancholy_gallery/ root@your-server:/opt/

# SSH 登录服务器
ssh root@your-server
cd /opt/melancholy_gallery

# 创建配置文件
cp .env.example .env
# 编辑 .env 修改密码和密钥

# 启动
docker compose up -d --build
```

### 手动部署

```bash
# 构建并启动
docker compose build
docker compose up -d

# 查看日志
docker compose logs -f

# 停止
docker compose down

# 重启
docker compose restart
```

### 环境变量

在 `.env` 文件中配置：

```env
DJANGO_SECRET_KEY=your-very-long-random-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=your-secure-password
```

## 更新部署

本地修改代码后，同步到服务器：

```bash
# 传文件（替换改过的文件路径）
scp gallery/views.py gallery/forms.py root@your-server:/opt/melancholy_gallery/gallery/
scp templates/gallery/home.html root@your-server:/opt/melancholy_gallery/templates/gallery/

# 重启
ssh root@your-server "cd /opt/melancholy_gallery && docker compose up -d --build"
```

## 默认管理员

- 用户名: `admin`
- 密码: `admin123`
- ⚠️ 请登录后立即修改密码！

## 目录结构

```
melancholy_gallery/
├── config/              # Django 项目配置
├── gallery/             # 主应用
│   ├── models.py        # 数据模型
│   ├── views.py         # 视图函数
│   ├── forms.py         # 表单
│   ├── urls.py          # 路由
│   ├── admin.py         # 后台管理
│   ├── backends.py      # 邮箱登录后端
│   └── context_processors.py
├── templates/           # 模板
│   ├── base.html
│   ├── gallery/
│   └── registration/
├── static/              # 静态文件
│   ├── css/style.css
│   └── js/main.js
├── media/               # 用户上传
│   ├── avatars/
│   ├── images/
│   └── videos/
├── nginx/               # Nginx 配置
├── deploy/              # 部署脚本
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── .env.example
└── manage.py
```

## 管理后台

访问 `/admin/` 可以：
- 管理用户（禁用/删除/修改权限）
- 管理图画、视频和评论
- 管理关注关系和私信
- 控制用户上传/评论权限
- 批量操作（禁用用户、禁止上传等）

## 许可

仅供学习使用。
