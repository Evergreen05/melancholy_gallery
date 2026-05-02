from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Image, Comment, Profile, Video, VideoComment, Message


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='邮箱')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = '用户名'
        self.fields['password1'].label = '密码'
        self.fields['password2'].label = '确认密码'
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被注册')
        return email


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('title', 'description', 'image')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '给这张图取个名字...'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': '写下此刻的心情...'}),
            'image': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
        }
        labels = {
            'title': '标题',
            'description': '描述',
            'image': '选择图画',
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 20 * 1024 * 1024:
                raise forms.ValidationError('图画大小不能超过20MB')
            valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp']
            if hasattr(image, 'content_type') and image.content_type not in valid_types:
                raise forms.ValidationError('仅支持 JPG、PNG、GIF、WebP、BMP 格式')
        return image


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': '写下你的感想...',
                'maxlength': 500,
            }),
        }
        labels = {
            'content': '评论',
        }


class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='用户名')

    class Meta:
        model = Profile
        fields = ('avatar', 'bio')
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': '写一句话介绍自己...', 'maxlength': 200}),
        }
        labels = {
            'avatar': '更换头像',
            'bio': '个性签名',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].initial = self.instance.user.username
        self.fields['username'].widget.attrs.update({'class': 'form-input', 'placeholder': '输入新用户名'})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exclude(pk=self.instance.user.pk).exists():
            raise forms.ValidationError('该用户名已被使用')
        return username

    def save(self, commit=True):
        profile = super().save(commit=commit)
        username = self.cleaned_data.get('username')
        if username and username != profile.user.username:
            profile.user.username = username
            profile.user.save()
        return profile


class UserAdminForm(forms.ModelForm):
    """管理员编辑用户权限"""
    can_upload = forms.BooleanField(required=False, label='允许上传')
    can_comment = forms.BooleanField(required=False, label='允许评论')

    class Meta:
        model = User
        fields = ('is_active', 'is_staff')


class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('title', 'description', 'video', 'thumbnail')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '给这个视频取个名字...'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': '写下此刻的心情...'}),
            'video': forms.FileInput(attrs={'class': 'form-input', 'accept': 'video/*'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
        }
        labels = {
            'title': '标题',
            'description': '描述',
            'video': '选择视频',
            'thumbnail': '封面图画（可选）',
        }

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            if video.size > 200 * 1024 * 1024:
                raise forms.ValidationError('视频大小不能超过200MB')
            valid_types = [
                'video/mp4', 'video/webm', 'video/ogg', 'video/quicktime',
                'video/x-msvideo', 'video/x-matroska', 'application/x-matroska',
                'video/avi', 'video/x-ms-wmv', 'video/mpeg',
            ]
            if hasattr(video, 'content_type'):
                if video.content_type not in valid_types:
                    name = getattr(video, 'name', '').lower()
                    if not any(name.endswith(ext) for ext in ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv', '.wmv']):
                        raise forms.ValidationError('仅支持 MP4、WebM、OGG、MOV、AVI、MKV 格式')
        return video

    def clean_thumbnail(self):
        thumbnail = self.cleaned_data.get('thumbnail')
        if thumbnail:
            if thumbnail.size > 10 * 1024 * 1024:
                raise forms.ValidationError('封面图画大小不能超过10MB')
        return thumbnail


class VideoCommentForm(forms.ModelForm):
    class Meta:
        model = VideoComment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': '写下你的感想...',
                'maxlength': 500,
            }),
        }
        labels = {
            'content': '评论',
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': '写点什么...',
                'maxlength': 2000,
            }),
        }
        labels = {
            'content': '消息内容',
        }
