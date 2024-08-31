from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import PasswordChangeView
from accounts.forms import (
    CustomUserCreationForm,
    CustomUserUpdateForm,
    UserProfileUpdateForm,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


def index(request):
    return render(request, "layout/layouts.html")


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("accounts:login")


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"


class CustomUserUpdateView(LoginRequiredMixin, View):
    template_name = "accounts/personal_info.html"

    def get(self, request, *args, **kwargs):
        user_form = CustomUserUpdateForm(instance=request.user)
        profile_form = UserProfileUpdateForm(instance=request.user.userprofile)
        return render(
            request,
            self.template_name,
            {"user_form": user_form, "profile_form": profile_form},
        )

    def post(self, request, *args, **kwargs):
        user_form = CustomUserUpdateForm(
            request.POST, request.FILES, instance=request.user
        )
        profile_form = UserProfileUpdateForm(
            request.POST, instance=request.user.userprofile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, "프로필이 성공적으로 업데이트되었습니다.")
            return HttpResponseRedirect(self.get_success_url())
        else:
            self.form_invalid(user_form, profile_form)

        return render(
            request,
            self.template_name,
            {"user_form": user_form, "profile_form": profile_form},
        )

    def form_invalid(self, user_form, profile_form):
        for form in [user_form, profile_form]:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        self.request, f"{form.fields[field].label or field}: {error}"
                    )
        return render(
            self.request,
            self.template_name,
            {"user_form": user_form, "profile_form": profile_form},
        )

    def get_success_url(self):
        return reverse_lazy(
            "accounts:profile_edit", kwargs={"user_id": self.request.user.pk}
        )


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/personal_info.html"

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
