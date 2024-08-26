from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "writer"]
        labels = {
            "title": "제목",
            "content": "내용",
            "writer" : '작성자'
        }