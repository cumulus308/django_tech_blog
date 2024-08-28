from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class CustomUserCreationForm(UserCreationForm):
    usable_password = None
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ["username", "nickname", "email", "password1", "password2"]
