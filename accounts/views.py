from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.views import View
from django.views.generic import CreateView

from accounts.forms import (
    CustomUserCreationForm,
    CustomUserUpdateForm,
    UserProfileUpdateForm,
)


def index(request):
    """
    메인화면 뷰
    """
    return render(request, "layout/layouts.html")


class SignUpView(CreateView):
    """
    회원가입 뷰
    """

    form_class = CustomUserCreationForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("blogs:post_list")

    def form_valid(self, form):
        """유효한 폼 제출시 처리"""
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        """유효하지 않은 폼 제출시 처리"""
        return self.render_to_response(self.get_context_data(form=form))


class CustomLoginView(LoginView):
    """로그인"""

    template_name = "accounts/login.html"


class CustomUserUpdateView(LoginRequiredMixin, View):
    """CustomUser 및 UserProfile 정보 수정 뷰"""

    template_name = "accounts/personal_info.html"

    def get(self, request, *args, **kwargs):
        """
        GET 요청시 CustomUser 및 UserProfile 정보를 포함한 폼 렌더링
        """
        return self.render_forms(request)

    def post(self, request, *args, **kwargs):
        """
        CustomUser 및 UserProfile 정보 수정 폼을 처리

        유효한 폼 : 데이터 저장
        유효하지 않은 폼 : form_invalid을 호출
        """
        user_form, profile_form = self.get_forms(request)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "프로필이 성공적으로 업데이트되었습니다.")
            return HttpResponseRedirect(self.get_success_url())

        return self.form_invalid(user_form, profile_form)

    def get_forms(self, request):
        """
        GET과 POST 요청에 대해 각각 적절한 폼 인스턴스를 생성하여 반환
        """
        if request.method == "POST":
            user_form = CustomUserUpdateForm(
                request.POST, request.FILES, instance=request.user
            )
            profile_form = UserProfileUpdateForm(
                request.POST, instance=request.user.userprofile
            )
        else:
            user_form = CustomUserUpdateForm(instance=request.user)
            profile_form = UserProfileUpdateForm(instance=request.user.userprofile)

        return user_form, profile_form

    def render_forms(self, request):
        """
        폼들을 렌더링합니다.
        """
        user_form, profile_form = self.get_forms(request)
        return render(
            request,
            self.template_name,
            {"user_form": user_form, "profile_form": profile_form},
        )

    def form_invalid(self, user_form, profile_form):
        """
        폼이 유효하지 않을 때 에러 메시지를 추가하고 폼을 다시 렌더링
        """
        for form in [user_form, profile_form]:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        self.request, f"{form.fields[field].label or field}: {error}"
                    )
        return self.render_forms(self.request)

    def get_success_url(self):
        """
        정보 수정 후 연결될 페이지
        프로필 수정 페이지로 이동
        """
        return reverse_lazy(
            "accounts:profile_edit", kwargs={"user_id": self.request.user.pk}
        )


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """비밀번호 변경"""

    template_name = "accounts/personal_info.html"

    def form_valid(self, form):
        """
        유효한 폼 제출시 성공 메시지 표시
        """
        messages.success(self.request, "비밀번호가 성공적으로 변경되었습니다.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        유효하지 않은 폼 제출시 에러 메시지 표시
        """
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(
                    self.request, f"{form.fields[field].label or field}: {error}"
                )
        return super().form_invalid(form)

    def get_success_url(self):
        """
        비밀번호 변경 성공 시 연결될 페이지
        """
        return reverse_lazy(
            "accounts:profile_edit", kwargs={"user_id": self.request.user.pk}
        )
