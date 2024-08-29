from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import PasswordChangeView
from accounts.forms import CustomUserCreationForm, CustomUserUpdateForm
from .models import CustomUser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


# Create your views here.
def index(request):
    return render(request, "layout/layouts.html")


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:login")  # 회원가입 후 로그인 페이지로 리디렉션

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        # 추가적인 로직을 통해 다른 URL로 리디렉션할 수 있습니다.
        return reverse_lazy("accounts:login")


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"


class CustomUserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = "accounts/personal_info.html"

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "프로필이 성공적으로 업데이트되었습니다.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "accounts:profile_edit", kwargs={"user_id": self.request.user.pk}
        )


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/personal_info.html"
    success_url = reverse_lazy("accounts:profile_edit")

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(
                    self.request, f"{form.fields[field].label or field}: {error}"
                )
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "비밀번호가 성공적으로 변경되었습니다.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "accounts:profile_edit", kwargs={"user_id": self.request.user.pk}
        )
