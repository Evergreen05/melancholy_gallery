from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from .models import Image, Comment, Like, Favorite, Profile, Video, VideoComment, VideoLike, VideoFavorite, Follow, Message
from .forms import RegisterForm, ImageUploadForm, CommentForm, ProfileForm, VideoUploadForm, VideoCommentForm, MessageForm


def home(request):
    """首页 - 最新图画和视频"""
    images = Image.objects.select_related('author').annotate(
        like_total=Count('likes', distinct=True),
        comment_total=Count('comments', distinct=True),
    ).order_by('-created_at')[:3]
    videos = Video.objects.select_related('author').annotate(
        like_total=Count('video_likes', distinct=True),
        comment_total=Count('video_comments', distinct=True),
    ).order_by('-created_at')[:3]
    return render(request, 'gallery/home.html', {'images': images, 'videos': videos})


def image_list(request):
    """图画馆 - 按点赞量排序"""
    images = Image.objects.select_related('author').annotate(
        like_total=Count('likes', distinct=True),
        comment_total=Count('comments', distinct=True),
    ).order_by('-like_total')
    query = request.GET.get('q', '')
    if query:
        images = images.filter(title__icontains=query)
    return render(request, 'gallery/image_list.html', {'images': images, 'query': query})


def image_detail(request, pk):
    """图画详情"""
    image = get_object_or_404(Image.objects.select_related('author'), pk=pk)
    comments = image.comments.select_related('author__profile').all()
    comment_form = CommentForm()
    is_liked = image.is_liked_by(request.user)
    is_favorited = image.is_favorited_by(request.user)
    return render(request, 'gallery/image_detail.html', {
        'image': image,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
        'is_favorited': is_favorited,
    })


def register_view(request):
    """注册"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '欢迎来到这个世界。')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def upload_view(request):
    """上传图画"""
    profile = request.user.profile
    if not profile.can_upload:
        messages.error(request, '你暂时没有上传权限。')
        return redirect('home')
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.author = request.user
            image.save()
            messages.success(request, '图画已上传。')
            return redirect('image_detail', pk=image.pk)
    else:
        form = ImageUploadForm()
    return render(request, 'gallery/upload.html', {'form': form})


@login_required
def profile_view(request, username=None):
    """个人中心"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    images = user.images.all()
    videos = user.videos.all()
    favorites = user.image_favorites.select_related('image').all()
    video_favorites = user.video_favorites.select_related('video').all()
    is_own = (user == request.user)
    is_following = False
    if not is_own and request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    followers = user.followers.select_related('follower__profile').all()
    followings = user.following.select_related('following__profile').all()
    return render(request, 'gallery/profile.html', {
        'profile_user': user,
        'images': images,
        'videos': videos,
        'favorites': favorites,
        'video_favorites': video_favorites,
        'is_own': is_own,
        'is_following': is_following,
        'followers': followers,
        'followings': followings,
    })


@login_required
def edit_profile(request):
    """编辑资料 / 修改头像"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, '资料已更新。')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'gallery/edit_profile.html', {'form': form})


@login_required
@require_POST
def add_comment(request, pk):
    """添加评论"""
    image = get_object_or_404(Image, pk=pk)
    profile = request.user.profile
    if not profile.can_comment:
        messages.error(request, '你暂时没有评论权限。')
        return redirect('image_detail', pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.image = image
        comment.author = request.user
        comment.save()
    return redirect('image_detail', pk=pk)


@login_required
@require_POST
def delete_comment(request, pk):
    """删除评论"""
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author == request.user or request.user.is_staff:
        image_pk = comment.image.pk
        comment.delete()
        messages.success(request, '评论已删除。')
        return redirect('image_detail', pk=image_pk)
    messages.error(request, '你没有权限删除此评论。')
    return redirect('home')


@login_required
@require_POST
def delete_image(request, pk):
    """删除图画"""
    image = get_object_or_404(Image, pk=pk)
    if image.author == request.user or request.user.is_staff:
        image.delete()
        messages.success(request, '图画已删除。')
        return redirect('home')
    messages.error(request, '你没有权限删除此图画。')
    return redirect('home')


@login_required
@require_POST
def toggle_like(request, pk):
    """点赞/取消点赞"""
    image = get_object_or_404(Image, pk=pk)
    like, created = Like.objects.get_or_create(image=image, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'count': image.like_count()})
    return redirect('image_detail', pk=pk)


@login_required
@require_POST
def toggle_favorite(request, pk):
    """收藏/取消收藏"""
    image = get_object_or_404(Image, pk=pk)
    fav, created = Favorite.objects.get_or_create(image=image, user=request.user)
    if not created:
        fav.delete()
        favorited = False
    else:
        favorited = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'favorited': favorited, 'count': image.favorites.count()})
    return redirect('image_detail', pk=pk)


# ── 视频相关视图 ──

def video_list(request):
    """影像馆 - 按点赞量排序"""
    videos = Video.objects.select_related('author').annotate(
        like_total=Count('video_likes', distinct=True),
        comment_total=Count('video_comments', distinct=True),
    ).order_by('-like_total')
    query = request.GET.get('q', '')
    if query:
        videos = videos.filter(title__icontains=query)
    return render(request, 'gallery/video_list.html', {'videos': videos, 'query': query})


def video_detail(request, pk):
    """视频详情"""
    video = get_object_or_404(Video.objects.select_related('author'), pk=pk)
    comments = video.video_comments.select_related('author__profile').all()
    comment_form = VideoCommentForm()
    is_liked = video.is_liked_by(request.user)
    is_favorited = video.is_favorited_by(request.user)
    return render(request, 'gallery/video_detail.html', {
        'video': video,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
        'is_favorited': is_favorited,
    })


@login_required
def video_upload(request):
    """上传视频"""
    profile = request.user.profile
    if not profile.can_upload:
        messages.error(request, '你暂时没有上传权限。')
        return redirect('video_list')
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.author = request.user
            video.save()
            messages.success(request, '视频已上传。')
            return redirect('video_detail', pk=video.pk)
    else:
        form = VideoUploadForm()
    return render(request, 'gallery/video_upload.html', {'form': form})


@login_required
@require_POST
def delete_video(request, pk):
    """删除视频"""
    video = get_object_or_404(Video, pk=pk)
    if video.author == request.user or request.user.is_staff:
        video.delete()
        messages.success(request, '视频已删除。')
        return redirect('video_list')
    messages.error(request, '你没有权限删除此视频。')
    return redirect('video_list')


@login_required
@require_POST
def add_video_comment(request, pk):
    """添加视频评论"""
    video = get_object_or_404(Video, pk=pk)
    profile = request.user.profile
    if not profile.can_comment:
        messages.error(request, '你暂时没有评论权限。')
        return redirect('video_detail', pk=pk)
    form = VideoCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.video = video
        comment.author = request.user
        comment.save()
    return redirect('video_detail', pk=pk)


@login_required
@require_POST
def delete_video_comment(request, pk):
    """删除视频评论"""
    comment = get_object_or_404(VideoComment, pk=pk)
    if comment.author == request.user or request.user.is_staff:
        video_pk = comment.video.pk
        comment.delete()
        messages.success(request, '评论已删除。')
        return redirect('video_detail', pk=video_pk)
    messages.error(request, '你没有权限删除此评论。')
    return redirect('video_list')


@login_required
@require_POST
def toggle_video_like(request, pk):
    """视频点赞/取消点赞"""
    video = get_object_or_404(Video, pk=pk)
    like, created = VideoLike.objects.get_or_create(video=video, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'count': video.like_count()})
    return redirect('video_detail', pk=pk)


@login_required
@require_POST
def toggle_video_favorite(request, pk):
    """视频收藏/取消收藏"""
    video = get_object_or_404(Video, pk=pk)
    fav, created = VideoFavorite.objects.get_or_create(video=video, user=request.user)
    if not created:
        fav.delete()
        favorited = False
    else:
        favorited = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'favorited': favorited, 'count': video.video_favorites.count()})
    return redirect('video_detail', pk=pk)


# ── 关注相关视图 ──

@login_required
@require_POST
def toggle_follow(request, username):
    """关注/取消关注"""
    target = get_object_or_404(User, username=username)
    if target == request.user:
        messages.error(request, '不能关注自己。')
        return redirect('user_profile', username=username)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        follow.delete()
        messages.success(request, f'已取消关注 {target.username}。')
    else:
        messages.success(request, f'已关注 {target.username}。')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'following': created, 'count': target.followers.count()})
    return redirect('user_profile', username=username)


@login_required
def followers_list(request, username):
    """粉丝列表"""
    user = get_object_or_404(User, username=username)
    followers = user.followers.select_related('follower__profile').all()
    return render(request, 'gallery/follow_list.html', {
        'profile_user': user,
        'users': [f.follower for f in followers],
        'list_type': '粉丝',
    })


@login_required
def following_list(request, username):
    """关注列表"""
    user = get_object_or_404(User, username=username)
    followings = user.following.select_related('following__profile').all()
    return render(request, 'gallery/follow_list.html', {
        'profile_user': user,
        'users': [f.following for f in followings],
        'list_type': '关注',
    })


# ── 私信相关视图 ──

@login_required
def inbox(request):
    """收件箱 - 按对方用户分组显示最新消息"""
    received = Message.objects.filter(receiver=request.user).select_related('sender__profile')
    sent = Message.objects.filter(sender=request.user).select_related('receiver__profile')

    conversations = {}
    for msg in received:
        other = msg.sender
        if other not in conversations or msg.created_at > conversations[other]['last_time']:
            conversations[other] = {
                'last_msg': msg.content,
                'last_time': msg.created_at,
                'unread': not msg.is_read,
            }
    for msg in sent:
        other = msg.receiver
        if other not in conversations or msg.created_at > conversations[other]['last_time']:
            conversations[other] = {
                'last_msg': msg.content,
                'last_time': msg.created_at,
                'unread': False,
            }

    conv_list = sorted(
        [{'user': k, **v} for k, v in conversations.items()],
        key=lambda x: x['last_time'],
        reverse=True,
    )
    return render(request, 'gallery/inbox.html', {'conversations': conv_list})


@login_required
def conversation(request, username):
    """与某人的对话"""
    other = get_object_or_404(User, username=username)
    if other == request.user:
        return redirect('inbox')

    Message.objects.filter(sender=other, receiver=request.user, is_read=False).update(is_read=True)

    msgs = Message.objects.filter(
        Q(sender=request.user, receiver=other) |
        Q(sender=other, receiver=request.user)
    ).select_related('sender__profile').order_by('created_at')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = other
            msg.save()
            return redirect('conversation', username=username)
    else:
        form = MessageForm()

    return render(request, 'gallery/conversation.html', {
        'other': other,
        'msg_list': msgs,
        'form': form,
    })


@login_required
def send_message(request, username):
    """从个人主页发送私信"""
    other = get_object_or_404(User, username=username)
    if other == request.user:
        messages.error(request, '不能给自己发私信。')
        return redirect('profile')
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = other
            msg.save()
            messages.success(request, '私信已发送。')
            return redirect('conversation', username=username)
    else:
        form = MessageForm()
    return render(request, 'gallery/send_message.html', {'other': other, 'form': form})
