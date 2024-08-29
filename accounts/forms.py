from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from accounts.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    usable_password = None
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "nickname",
            "last_name",
            "email",
            "password1",
            "password2",
        ]
        labels = {
            "username": "ID",
            "last_name": "name",
        }


class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["email", "nickname"]
