from pathlib import Path

from django import forms
from django.conf import settings

from .models import Post, Comment


def load_banned_words():
    file_path = Path(settings.BASE_DIR) / "tools" / "banned_words.txt"

    with open(file_path, "r", encoding="utf-8") as file:
        banned_words = [line.strip() for line in file.readlines()]

    return banned_words


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

    def clean_title(self):
        """
        title 필드의 유효성 검사를 진행합니다.
        """
        title = self.cleaned_data.get("title")
        banned_words = load_banned_words()

        for word in banned_words:
            if word in title:
                raise forms.ValidationError(f"{word}는 금지된 어휘입니다.")
        return title

    def clean_content(self):
        """
        content 필드의 유효성 검사를 진행합니다.
        """
        content = self.cleaned_data.get("content")
        banned_words = load_banned_words()
        for word in banned_words:
            if word in content:
                raise forms.ValidationError(f"{word}는 금지된 어휘입니다.")
        return content


class CommentForm(forms.ModelForm):
    parent = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ["content"]
        labels = {
            "content": (""),
        }
