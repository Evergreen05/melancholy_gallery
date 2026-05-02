from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils.html import format_html
from .models import Profile, Image, Comment, Like, Favorite, Video, VideoComment, VideoLike, VideoFavorite, Follow, Message


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = '用户资料'
    fields = ('avatar', 'avatar_preview', 'bio', 'can_upload', 'can_comment')
    readonly_fields = ('avatar_preview',)

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="width:60px;height:60px;border-radius:50%;object-fit:cover;">', obj.avatar.url)
        return '-'
    avatar_preview.short_description = '头像预览'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        'username', 'email', 'is_active', 'is_staff',
        'get_can_upload', 'get_can_comment',
        'get_image_count', 'get_video_count', 'get_follower_count',
        'date_joined',
    )
    list_filter = ('is_active', 'is_staff', 'profile__can_upload', 'profile__can_comment', 'date_joined')
    search_fields = ('username', 'email')
    actions = [
        'ban_users', 'unban_users',
        'disable_upload', 'enable_upload',
        'disable_comment', 'enable_comment',
    ]

    def get_can_upload(self, obj):
        return obj.profile.can_upload
    get_can_upload.short_description = '上传'
    get_can_upload.boolean = True

    def get_can_comment(self, obj):
        return obj.profile.can_comment
    get_can_comment.short_description = '评论'
    get_can_comment.boolean = True

    def get_image_count(self, obj):
        return obj.images.count()
    get_image_count.short_description = '图画数'
    get_image_count.admin_order_field = 'image_count'

    def get_video_count(self, obj):
        return obj.videos.count()
    get_video_count.short_description = '视频数'
    get_video_count.admin_order_field = 'video_count'

    def get_follower_count(self, obj):
        return obj.followers.count()
    get_follower_count.short_description = '粉丝数'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            image_count=Count('images', distinct=True),
            video_count=Count('videos', distinct=True),
        )

    @admin.action(description='禁用选中用户')
    def ban_users(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'已禁用 {count} 个用户')

    @admin.action(description='启用选中用户')
    def unban_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'已启用 {count} 个用户')

    @admin.action(description='禁止上传')
    def disable_upload(self, request, queryset):
        count = Profile.objects.filter(user__in=queryset).update(can_upload=False)
        self.message_user(request, f'已禁止 {count} 个用户上传')

    @admin.action(description='允许上传')
    def enable_upload(self, request, queryset):
        count = Profile.objects.filter(user__in=queryset).update(can_upload=True)
        self.message_user(request, f'已允许 {count} 个用户上传')

    @admin.action(description='禁止评论')
    def disable_comment(self, request, queryset):
        count = Profile.objects.filter(user__in=queryset).update(can_comment=False)
        self.message_user(request, f'已禁止 {count} 个用户评论')

    @admin.action(description='允许评论')
    def enable_comment(self, request, queryset):
        count = Profile.objects.filter(user__in=queryset).update(can_comment=True)
        self.message_user(request, f'已允许 {count} 个用户评论')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('author', 'content', 'created_at')
    readonly_fields = ('created_at',)
    max_num = 10


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'like_count', 'comment_count', 'image_preview')
    list_filter = ('created_at',)
    search_fields = ('title', 'description', 'author__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('image_preview',)
    inlines = [CommentInline]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:100px;border-radius:8px;">', obj.image.url)
        return '-'
    image_preview.short_description = '预览'


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'like_count', 'comment_count', 'video_preview')
    list_filter = ('created_at',)
    search_fields = ('title', 'description', 'author__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('video_preview',)

    def video_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="max-height:60px;border-radius:4px;">', obj.thumbnail.url)
        return '-'
    video_preview.short_description = '封面'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'image', 'content_short', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username')

    def content_short(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_short.short_description = '内容'


@admin.register(VideoComment)
class VideoCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'video', 'content_short', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username')

    def content_short(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_short.short_description = '内容'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'created_at')
    list_filter = ('created_at',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'created_at')
    list_filter = ('created_at',)


@admin.register(VideoLike)
class VideoLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'created_at')
    list_filter = ('created_at',)


@admin.register(VideoFavorite)
class VideoFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'created_at')
    list_filter = ('created_at',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content_short', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'content')
    actions = ['mark_as_read', 'mark_as_unread']

    def content_short(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_short.short_description = '内容'

    @admin.action(description='标记为已读')
    def mark_as_read(self, request, queryset):
        count = queryset.update(is_read=True)
        self.message_user(request, f'已标记 {count} 条为已读')

    @admin.action(description='标记为未读')
    def mark_as_unread(self, request, queryset):
        count = queryset.update(is_read=False)
        self.message_user(request, f'已标记 {count} 条为未读')


admin.site.site_header = '忧郁画廊 · 管理后台'
admin.site.site_title = '忧郁画廊'
admin.site.index_title = '管理面板'
