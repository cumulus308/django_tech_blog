from django import forms


class ChatForm(forms.Form):
    text_input = forms.CharField(
        label="글 내용 요약",
        max_length=1000,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "요약할 내용을 입력하세요...",
                "rows": 4,
            }
        ),
        required=False,
    )
