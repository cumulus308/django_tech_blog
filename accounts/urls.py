from django.urls import path
from .views import (
    CustomLoginView,
    CustomUserUpdateView,
    SignUpView,
    CustomPasswordChangeView,
)
from django.contrib.auth import views as auth_views

app_name = "accounts"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", SignUpView.as_view(), name="signup"),
    path(
        "profile/edit/<int:user_id>/",
        CustomUserUpdateView.as_view(),
        name="profile_edit",
    ),
    path(
        "password/change/", CustomPasswordChangeView.as_view(), name="password_change"
    ),
]
