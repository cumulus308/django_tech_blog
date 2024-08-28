from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import login
from django.contrib.auth.views import LoginView

from accounts.forms import CustomUserCreationForm


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
