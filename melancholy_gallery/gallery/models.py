from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
import io
import logging

logger = logging.getLogger(__name__)


class Profile(models.Model):
    """扩展用户资料"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True)
    bio = models.TextField(max_length=200, blank=True, default='', verbose_name='个性签名')
    can_upload = models.BooleanField(default=True, verbose_name='允许上传')
    can_comment = models.BooleanField(default=True, verbose_name='允许评论')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.username} 的资料'

    def follower_count(self):
        return self.user.followers.count()

    def following_count(self):
        return self.user.following.count()

    def is_followed_by(self, user):
        if user.is_anonymous:
            return False
        return self.user.followers.filter(follower=user).exists()


class Follow(models.Model):
    """关注关系"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following', verbose_name='关注者')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers', verbose_name='被关注者')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']
        verbose_name = '关注'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.follower.username} 关注 {self.following.username}'


class Message(models.Model):
    """私信"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='发送者')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name='接收者')
    content = models.TextField(max_length=2000, verbose_name='内容')
    is_read = models.BooleanField(default=False, verbose_name='已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '私信'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.sender.username} → {self.receiver.username}: {self.content[:20]}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Image(models.Model):
    """图画"""
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(max_length=2000, blank=True, verbose_name='描述')
    image = models.ImageField(upload_to='images/%Y/%m/', verbose_name='图画')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images', verbose_name='作者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '图画'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()

    def is_liked_by(self, user):
        if user.is_anonymous:
            return False
        return self.likes.filter(user=user).exists()

    def is_favorited_by(self, user):
        if user.is_anonymous:
            return False
        return self.favorites.filter(user=user).exists()


class Video(models.Model):
    """视频"""
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(max_length=2000, blank=True, verbose_name='描述')
    video = models.FileField(upload_to='videos/%Y/%m/', verbose_name='视频')
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', blank=True, null=True, verbose_name='封面')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos', verbose_name='作者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '视频'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    def like_count(self):
        return self.video_likes.count()

    def comment_count(self):
        return self.video_comments.count()

    def is_liked_by(self, user):
        if user.is_anonymous:
            return False
        return self.video_likes.filter(user=user).exists()

    def is_favorited_by(self, user):
        if user.is_anonymous:
            return False
        return self.video_favorites.filter(user=user).exists()


class Comment(models.Model):
    """图画评论"""
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='comments', verbose_name='图画')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_comments', verbose_name='作者')
    content = models.TextField(max_length=500, verbose_name='内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '图画评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.author.username}: {self.content[:30]}'


class VideoComment(models.Model):
    """视频评论"""
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='video_comments', verbose_name='视频')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_comments', verbose_name='作者')
    content = models.TextField(max_length=500, verbose_name='内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '视频评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.author.username}: {self.content[:30]}'


class Like(models.Model):
    """图画点赞"""
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='likes', verbose_name='图画')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_likes', verbose_name='用户')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('image', 'user')
        verbose_name = '图画点赞'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.username} likes {self.image.title}'


class VideoLike(models.Model):
    """视频点赞"""
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='video_likes', verbose_name='视频')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_likes', verbose_name='用户')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('video', 'user')
        verbose_name = '视频点赞'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.username} likes {self.video.title}'


class Favorite(models.Model):
    """图画收藏"""
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='favorites', verbose_name='图画')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_favorites', verbose_name='用户')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('image', 'user')
        ordering = ['-created_at']
        verbose_name = '图画收藏'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.username} saved {self.image.title}'


class VideoFavorite(models.Model):
    """视频收藏"""
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='video_favorites', verbose_name='视频')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_favorites', verbose_name='用户')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('video', 'user')
        ordering = ['-created_at']
        verbose_name = '视频收藏'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.username} saved {self.video.title}'


@receiver(post_save, sender=Video)
def generate_video_thumbnail(sender, instance, created, **kwargs):
    """视频上传后自动生成封面（如果未提供）"""
    if instance.thumbnail:
        return
    try:
        from moviepy import VideoFileClip

        video_path = instance.video.path
        clip = VideoFileClip(video_path)
        frame = clip.get_frame(0.5)
        clip.close()

        from PIL import Image as PILImage
        img = PILImage.fromarray(frame)
        thumb_io = io.BytesIO()
        img.save(thumb_io, format='JPEG', quality=85)
        thumb_content = ContentFile(thumb_io.getvalue())

        filename = f'thumb_{instance.pk}.jpg'
        instance.thumbnail.save(filename, thumb_content, save=True)
    except Exception as e:
        logger.warning(f'Failed to generate thumbnail for video {instance.pk}: {e}')
