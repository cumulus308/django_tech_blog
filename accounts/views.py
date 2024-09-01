from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login
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
    사용자의 회원가입을 처리하는 뷰
    """

    form_class = CustomUserCreationForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("blogs:post_list")

    def form_valid(self, form):
        user = form.save()
        username = self.request.POST["username"]
        print(username)
        password = self.request.POST["password1"]
        print(password)
        user = authenticate(username=username, password=password)
        login(self.request, user)

        return super().form_valid(form)


class CustomLoginView(LoginView):
    """사용자 로그인 뷰"""

    template_name = "accounts/login.html"


class CustomUserUpdateView(LoginRequiredMixin, View):
    """CustomUser 및 UserProfile 정보를 수정하는 뷰"""

    template_name = "accounts/personal_info.html"

    def get(self, request, *args, **kwargs):
        """
        GET 요청시 CustomUser 및 UserProfile 정보를 포함한 폼 렌더링
        """
        return self.render_forms(request)

    def post(self, request, *args, **kwargs):
        """
        POST 요청을 처리하여 CustomUser 및 UserProfile 정보를 수정

        폼이 유효한 경우, 데이터를 저장하고 성공 메시지 표시
        폼이 유효하지 않은 경우, `form_invalid` 메서드를 호출하여 오류 메시지와 함께 폼을 다시 렌더링
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

        POST 요청일 경우, 전송된 데이터를 바탕으로 폼 인스턴스를 생성하고,
        GET 요청일 경우, 현재 사용자의 데이터를 기반으로 폼 인스턴스를 생성

        Args:
            request (HttpRequest): GET 또는 POST 요청 객체.

        Returns:
            tuple: CustomUserUpdateForm과 UserProfileUpdateForm 인스턴스의 튜플.
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
        사용자 정보 수정 폼들을 렌더링

        Args:
            request (HttpRequest): GET 요청 객체.

        Returns:
            HttpResponse: 폼이 렌더링된 템플릿 응답 객체.
        """
        user_form, profile_form = self.get_forms(request)
        return render(
            request,
            self.template_name,
            {"user_form": user_form, "profile_form": profile_form},
        )

    def form_invalid(self, user_form, profile_form):
        """
        폼이 유효하지 않을 때, 오류 메시지를 추가하고 폼을 다시 렌더링

        각 폼 필드의 오류를 메시지에 추가하여 사용자에게 표시

        Args:
            user_form (CustomUserUpdateForm): 유효하지 않은 CustomUser 폼 인스턴스.
            profile_form (UserProfileUpdateForm): 유효하지 않은 UserProfile 폼 인스턴스.

        Returns:
            HttpResponse: 오류 메시지가 추가된 상태로 폼이 다시 렌더링된 응답 객체.
        """
        for form in [user_form, profile_form]:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        self.request, f"{form.fields[field].label or field}: {error}"
                    )
        return self.render_forms(self.request)

    def get_success_url(self):
        return reverse_lazy(
            "accounts:profile_edit", kwargs={"user_id": self.request.user.pk}
        )


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """비밀번호 변경 뷰"""

    template_name = "accounts/personal_info.html"

    def get_success_url(self):
        """
        Returns:
            비밀번호 변경 후 리디렉션될 프로필 수정 페이지의 URL.
        """
        return reverse_lazy(
            "accounts:profile_edit", kwargs={"user_id": self.request.user.pk}
        )

    def form_valid(self, form):
        messages.success(self.request, "비밀번호가 성공적으로 변경되었습니다.")
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            field_label = form.fields[field].label or field
            for error in errors:
                messages.error(self.request, f"{field_label}: {error}")
        return super().form_invalid(form)
