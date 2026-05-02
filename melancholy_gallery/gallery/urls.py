from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('images/', views.image_list, name='image_list'),
    path('image/<int:pk>/', views.image_detail, name='image_detail'),
    path('upload/', views.upload_view, name='upload'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='user_profile'),
    path('comment/<int:pk>/add/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('image/<int:pk>/delete/', views.delete_image, name='delete_image'),
    path('image/<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('image/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    # 视频
    path('videos/', views.video_list, name='video_list'),
    path('video/<int:pk>/', views.video_detail, name='video_detail'),
    path('video/upload/', views.video_upload, name='video_upload'),
    path('video/<int:pk>/delete/', views.delete_video, name='delete_video'),
    path('video/<int:pk>/like/', views.toggle_video_like, name='toggle_video_like'),
    path('video/<int:pk>/favorite/', views.toggle_video_favorite, name='toggle_video_favorite'),
    path('video/comment/<int:pk>/add/', views.add_video_comment, name='add_video_comment'),
    path('video/comment/<int:pk>/delete/', views.delete_video_comment, name='delete_video_comment'),
    # 关注
    path('user/<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
    path('user/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('user/<str:username>/following/', views.following_list, name='following_list'),
    # 私信
    path('messages/', views.inbox, name='inbox'),
    path('messages/<str:username>/', views.conversation, name='conversation'),
    path('messages/<str:username>/send/', views.send_message, name='send_message'),
]
