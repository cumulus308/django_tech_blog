from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "category", "thumbnail"]
        labels = {
            "title": "제목",
            "content": "내용",
            "category": "카테고리",
            "thumbnail": "썸네일",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content", "parent"]
        labels = {
            "content": (""),
        }
