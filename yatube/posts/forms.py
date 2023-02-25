from django import forms
from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма создания нового поста."""
    class Meta:
        model = Post
        fields = {'text', 'group', 'image'}


class CommentForm(forms.ModelForm):
    """Форма создания нового поста."""
    class Meta:
        model = Comment
        fields = {'text'}
