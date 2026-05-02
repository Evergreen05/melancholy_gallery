/* ═══════════════════════════════════════════
   忧郁画廊 · 动画 & 交互
   ═══════════════════════════════════════════ */

// ── 雨滴动画 ──
function createRain() {
    const container = document.getElementById('rain');
    if (!container) return;
    const count = 60;
    for (let i = 0; i < count; i++) {
        const drop = document.createElement('div');
        drop.className = 'raindrop';
        drop.style.left = Math.random() * 100 + '%';
        drop.style.height = (Math.random() * 20 + 10) + 'px';
        drop.style.animationDuration = (Math.random() * 1.5 + 1) + 's';
        drop.style.animationDelay = (Math.random() * 3) + 's';
        container.appendChild(drop);
    }
}

// ── 樱花飘落 ──
function createSakura() {
    const container = document.getElementById('sakura');
    if (!container) return;
    const petals = ['🌸', '✿', '❀'];
    const count = 15;
    for (let i = 0; i < count; i++) {
        const petal = document.createElement('div');
        petal.className = 'sakura';
        petal.textContent = petals[Math.floor(Math.random() * petals.length)];
        petal.style.left = Math.random() * 100 + '%';
        petal.style.fontSize = (Math.random() * 10 + 10) + 'px';
        petal.style.animationDuration = (Math.random() * 8 + 8) + 's';
        petal.style.animationDelay = (Math.random() * 10) + 's';
        petal.style.opacity = (Math.random() * 0.4 + 0.2).toString();
        container.appendChild(petal);
    }
}

// ── Tab 切换 ──
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            const el = document.getElementById(target);
            if (el) el.classList.add('active');
        });
    });
}

// ── 点赞/收藏 AJAX ──
function initActions() {
    document.querySelectorAll('[data-action]').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.dataset.url;
            const action = this.dataset.action;
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(r => r.json())
            .then(data => {
                if (action === 'like') {
                    this.classList.toggle('liked', data.liked);
                    const countEl = this.querySelector('.count');
                    if (countEl) countEl.textContent = data.count;
                } else if (action === 'favorite') {
                    this.classList.toggle('favorited', data.favorited);
                    const countEl = this.querySelector('.count');
                    if (countEl) countEl.textContent = data.count;
                }
            });
        });
    });
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// ── 消息自动消失 ──
function initMessages() {
    document.querySelectorAll('.msg').forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.5s';
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 4000);
    });
}

// ── 上传进度条 ──
function initUploadProgress() {
    document.querySelectorAll('.upload-form').forEach(form => {
        const bar = form.querySelector('.progress-bar');
        const fill = form.querySelector('.progress-fill');
        const text = form.querySelector('.progress-text');
        const submitBtn = form.querySelector('button[type=submit]');
        if (!bar) return;

        form.addEventListener('submit', function (e) {
            e.preventDefault();

            bar.style.display = 'block';
            submitBtn.disabled = true;
            submitBtn.textContent = '上传中...';
            fill.style.width = '0%';
            fill.style.background = '';
            text.textContent = '0%';

            const formData = new FormData(form);
            const xhr = new XMLHttpRequest();

            xhr.upload.addEventListener('progress', function (ev) {
                if (ev.lengthComputable) {
                    const pct = Math.round((ev.loaded / ev.total) * 100);
                    fill.style.width = pct + '%';
                    text.textContent = pct + '%';
                }
            });

            xhr.addEventListener('load', function () {
                fill.style.width = '100%';
                text.textContent = '上传完成';
                setTimeout(function () {
                    if (xhr.responseURL) {
                        window.location.href = xhr.responseURL;
                    } else {
                        window.location.reload();
                    }
                }, 300);
            });

            xhr.addEventListener('error', function () {
                fill.style.background = 'var(--accent)';
                text.textContent = '上传失败';
                submitBtn.disabled = false;
                submitBtn.textContent = '重试';
            });

            xhr.open('POST', form.action);
            xhr.send(formData);
        });
    });
}

// ── 文件选择预览 ──
function initFilePreview() {
    document.querySelectorAll('.upload-drop').forEach(drop => {
        const input = drop.parentElement.querySelector('input[type=file]');
        if (!input) return;

        input.addEventListener('change', function () {
            if (this.files.length > 0) {
                const size = (this.files[0].size / 1024 / 1024).toFixed(1);
                drop.querySelector('p').textContent = '已选择: ' + this.files[0].name + ' (' + size + 'MB)';
                drop.style.borderColor = 'var(--primary)';
            }
        });
    });
}

// ── 初始化 ──
document.addEventListener('DOMContentLoaded', () => {
    createRain();
    createSakura();
    initTabs();
    initActions();
    initMessages();
    initUploadProgress();
    initFilePreview();
});
