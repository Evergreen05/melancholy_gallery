from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Image, Comment, Like, Favorite, Video, VideoComment, VideoLike, VideoFavorite, Follow, Message


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = '用户资料'
    fields = ('avatar', 'bio', 'can_upload', 'can_comment')


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'is_active', 'is_staff', 'get_can_upload', 'get_can_comment', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'profile__can_upload', 'profile__can_comment')
    actions = ['ban_users', 'unban_users', 'disable_upload', 'enable_upload', 'disable_comment', 'enable_comment']

    def get_can_upload(self, obj):
        return obj.profile.can_upload
    get_can_upload.short_description = '允许上传'
    get_can_upload.boolean = True

    def get_can_comment(self, obj):
        return obj.profile.can_comment
    get_can_comment.short_description = '允许评论'
    get_can_comment.boolean = True

    @admin.action(description='禁用选中用户')
    def ban_users(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description='启用选中用户')
    def unban_users(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='禁止上传')
    def disable_upload(self, request, queryset):
        Profile.objects.filter(user__in=queryset).update(can_upload=False)

    @admin.action(description='允许上传')
    def enable_upload(self, request, queryset):
        Profile.objects.filter(user__in=queryset).update(can_upload=True)

    @admin.action(description='禁止评论')
    def disable_comment(self, request, queryset):
        Profile.objects.filter(user__in=queryset).update(can_comment=False)

    @admin.action(description='允许评论')
    def enable_comment(self, request, queryset):
        Profile.objects.filter(user__in=queryset).update(can_comment=True)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'like_count', 'comment_count')
    list_filter = ('created_at',)
    search_fields = ('title', 'description', 'author__username')
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'image', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'created_at')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'created_at')


admin.site.site_header = '忧郁画廊 · 管理后台'
admin.site.site_title = '忧郁画廊'
admin.site.index_title = '管理面板'


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'like_count', 'comment_count')
    list_filter = ('created_at',)
    search_fields = ('title', 'description', 'author__username')
    date_hierarchy = 'created_at'


@admin.register(VideoComment)
class VideoCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'video', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username')


@admin.register(VideoLike)
class VideoLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'created_at')


@admin.register(VideoFavorite)
class VideoFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'created_at')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'content')
    actions = ['mark_as_read']

    @admin.action(description='标记为已读')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
