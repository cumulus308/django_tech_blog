import json

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.db.models import Q, F
from django.views import View
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from accounts.models import CustomUser, Follow
from .models import Bookmark, Category, Like, Post, Comment
from .forms import CommentForm, PostForm


class PostListView(ListView):
    """
    Post를 정렬하고 목록을 표시하는 뷰

    이 뷰는 사용자가 제공한 검색어와 정렬 기준에 따라 Post 객체를 필터링하고,
    페이지네이션을 적용하여 화면에 표시
    """

    model = Post
    template_name = "blogs/post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        """
        q와 order_by 파라미터를 기반으로 쿼리셋을 필터링
        """
        queryset = super().get_queryset()
        q = self.request.GET.get("q", "")
        order_by = self.request.GET.get("order_by", "-created_at")

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(content__icontains=q)
            ).distinct()

        valid_order_fields = ["-created_at", "-hit", "-like_count"]
        queryset = queryset.order_by(
            order_by if order_by in valid_order_fields else "-created_at"
        )

        return queryset

    def get_paginate_by(self, queryset):
        """
        페이지당 표시할 Post의 수를 결정

        Returns:
            한 페이지에 표시할 Post의 개수
        """
        return self.request.GET.get("per_page", 12)

    def get_context_data(self, **kwargs):
        """
        템플릿에서 사용할 추가 컨텍스트 데이터를 제공

        Returns:
            템플릿에서 사용할 컨텍스트 데이터(is_paginated, current_order, page_range)
        """
        context = super().get_context_data(**kwargs)
        paginator = context.get("paginator")
        page = context.get("page_obj")

        if paginator and page:
            context["is_paginated"] = page.has_other_pages()
            context["current_order"] = self.request.GET.get("order_by", "-created_at")

            if paginator.num_pages <= 9:
                context["page_range"] = range(1, paginator.num_pages + 1)
            else:
                start_index = max(1, page.number - 4)
                end_index = min(paginator.num_pages, page.number + 4)
                context["page_range"] = range(start_index, end_index + 1)

        return context


class PostDetailView(LoginRequiredMixin, DetailView):
    """
    Post의 세부 내용을 확인하는 뷰

    이 뷰는 특정 Post의 세부 정보 표시
    조회수를 증가, 댓글을 달 수 있는 기능을 제공
    북마크, 팔로우, 좋아요 상태를 확인
    """

    model = Post
    template_name = "blogs/post_detail.html"
    context_object_name = "post"

    def get_object(self):
        """
        조회수를 증가시키고 객체를 반환

        사용자가 Post 작성자가 아닐 경우, Post의 조회수를 증가
        """
        post = super().get_object()
        if self.request.user != post.writer:
            Post.objects.filter(pk=post.pk).update(hit=F("hit") + 1)
        return post

    def get_context_data(self, **kwargs):
        """
        추가적인 컨텍스트 데이터를 제공

        Returns:
            dict: 템플릿에서 사용할 컨텍스트 데이터
                (댓글 목록, 북마크 상태, 팔로우 상태, 좋아요 상태)
        """
        context = super().get_context_data(**kwargs)
        post = self.object
        user = self.request.user

        context.update(
            {
                "comments": Comment.objects.filter(post=post, parent=None),
                "is_bookmarked": Bookmark.objects.filter(user=user, post=post).exists(),
                "is_following": Follow.objects.filter(
                    follower=user, following=post.writer
                ).exists(),
                "is_liked": Like.objects.filter(user=user, post=post).exists(),
            }
        )

        return context

    def post(self, request, *args, **kwargs):
        """
        POST 요청을 처리하여 댓글을 등록
        """
        post = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.writer = request.user

            parent_id = request.POST.get("parent")
            if parent_id:
                comment.parent = get_object_or_404(Comment, id=parent_id)

            comment.save()

        return redirect("blogs:post_detail", pk=post.pk)


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    사용자가 새로운 Post를 생성할 수 있는 뷰

    Post를 생성하는 폼을 제공하고, 폼이 유효한 경우 새로운 Post를 저장
    또한, 사용자가 로그인하지 않은 경우 로그인 페이지로 이동
    """

    model = Post
    form_class = PostForm
    template_name = "blogs/post_form.html"
    login_url = "accounts:login"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        """
        카테고리 데이터를 컨텍스트에 추가
        """
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context

    def form_valid(self, form):
        form.instance.writer = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse_lazy("blogs:post_detail", kwargs={"pk": self.object.pk})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    사용자가 기존 Post를 수정할 수 있는 뷰
    """

    model = Post
    form_class = PostForm
    template_name = "blogs/post_form.html"
    redirect_field_name = "next"

    def test_func(self):
        """
        현재 사용자가 게시물의 작성자인지 확인

        Returns:
            bool: 사용자가 게시물 작성자인 경우 True, 그렇지 않은 경우 False
        """
        return self.request.user == self.get_object().writer

    def handle_no_permission(self):
        """
        사용자가 권한이 없을 때 403 Forbidden 오류를 반환
        """
        return PermissionDenied

    def get_context_data(self, **kwargs):
        """
        템플릿에 전달할 추가 컨텍스트 데이터를 설정

        Returns:
            템플릿에서 사용할 컨텍스트 데이터(Post와 모든 카테고리)
        """
        context = super().get_context_data(**kwargs)
        context.update(
            {"post": self.get_object(), "categories": Category.objects.all()}
        )
        return context

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy("blogs:post_detail", kwargs={"pk": self.object.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    사용자가 자신의 Post를 삭제할 수 있는 뷰
    """

    model = Post
    redirect_field_name = "next"
    success_url = reverse_lazy("blogs:post_list")

    def test_func(self):
        return self.request.user == self.get_object().writer

    def handle_no_permission(self):
        return PermissionDenied

    def post(self, request, *args, **kwargs):
        """
        삭제 요청을 처리

        Returns:
            HttpResponseRedirect: 성공적으로 Post가 삭제된 후 리디렉션되는 응답 객체
            HttpResponseForbidden: 사용자가 삭제 권한이 없을 때 반환되는 응답 객체
        """
        if not self.test_func():
            return self.handle_no_permission()
        return super().post(request, *args, **kwargs)


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    사용자가 자신의 댓글을 수정할 수 있는 뷰
    """

    redirect_field_name = "next"

    def test_func(self):
        try:
            comment = Comment.objects.get(pk=self.kwargs["pk"])
        except Comment.DoesNotExist:
            return False
        return self.request.user == comment.writer

    def handle_no_permission(self):
        return JsonResponse({"error": "수정할 권한이 없습니다."}, status=403)

    def post(self, request, *args, **kwargs):
        """
        댓글 수정 요청을 처리
        """
        if not self.test_func():
            return self.handle_no_permission()

        try:
            data = json.loads(request.body)
            content = data.get("content")
            if not content:
                return JsonResponse(
                    {"success": False, "error": "Content cannot be empty"}, status=400
                )

            comment = Comment.objects.get(pk=self.kwargs["pk"])
            comment.content = content
            comment.save()
            return JsonResponse({"success": True, "content": comment.content})
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "JSON 데이터가 없습니다."}, status=400
            )
        except Comment.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "댓글을 찾을 수 없습니다."}, status=404
            )


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    사용자가 자신의 댓글을 삭제할 수 있는 뷰
    """

    model = Comment
    redirect_field_name = "next"

    def test_func(self):
        return self.request.user == self.get_object().writer

    def handle_no_permission(self):
        return redirect("blogs:post_detail", pk=self.get_object().post.pk)

    def post(self, request, *args, **kwargs):
        """
        댓글 삭제 요청을 처리
        """
        return self.delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blogs:post_detail", kwargs={"pk": self.get_object().post.pk})


class ToggleBookmarkView(View):
    """
    사용자가 게시물을 북마크하거나 북마크를 취소할 수 있는 뷰

    """

    def post(self, request, *args, **kwargs):
        """
        POST 요청을 처리하여 사용자가 게시물을 북마크하거나 북마크를 취소하는 동작을 처리

        사용자가 인증되지 않은 경우, 403 Forbidden 응답을 반환
        사용자가 게시물을 북마크하지 않았다면 북마크를 생성하고,
        이미 북마크한 상태라면 해당 북마크를 삭제

        Returns:
            HttpResponseRedirect: 사용자가 북마크 동작 후 이전 페이지로 리디렉션되는 응답 객체
            HttpResponseForbidden: 사용자가 인증되지 않은 경우 반환되는 응답 객체
        """
        if not request.user.is_authenticated:
            return PermissionDenied

        post = get_object_or_404(Post, id=kwargs.get("post_id"))

        bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)

        if not created:
            bookmark.delete()

        return redirect(request.META.get("HTTP_REFERER", "/"))


class ToggleFollowView(View):
    """
    사용자가 다른 사용자를 팔로우하거나 팔로우를 취소할 수 있는 뷰
    """

    def post(self, request, *args, **kwargs):
        """
        POST 요청을 처리하여 사용자가 다른 사용자를 팔로우하거나 팔로우를 취소하는 동작을 처리

        사용자가 인증되지 않은 경우, 이전 페이지로 이동
        사용자가 자신을 팔로우하려고 시도하는 경우, 오류 메시지를 표시하고 이전 페이지로 이동
        사용자가 다른 사용자를 팔로우하지 않았다면 팔로우를 생성하고,
        이미 팔로우한 상태라면 해당 팔로우를 삭제
        """
        if not request.user.is_authenticated:
            messages.error(request, "인증되지 않은 사용자 입니다.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        follow_user = get_object_or_404(CustomUser, id=kwargs.get("user_id"))

        if request.user == follow_user:
            messages.error(request, "본인을 팔로우할 수 없습니다.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        follow, created = Follow.objects.get_or_create(
            follower=request.user, following=follow_user
        )

        if not created:
            follow.delete()

        return redirect(request.META.get("HTTP_REFERER", "/"))


class ToggleLikeView(LoginRequiredMixin, View):
    """
    사용자가 게시물에 좋아요를 누르거나 취소할 수 있는 뷰
    """

    redirect_field_name = "next"

    def post(self, request, *args, **kwargs):
        """
        POST 요청을 처리하여 사용자가 게시물에 좋아요를 누르거나 취소하는 동작을 처리
        """
        post = get_object_or_404(Post, id=kwargs.get("post_id"))

        if post.writer == request.user:
            messages.error(request, "자신의 게시물에는 좋아요를 누를 수 없습니다.")
        else:
            like, created = Like.objects.get_or_create(user=request.user, post=post)

            if created:
                messages.success(request, "게시물에 좋아요를 했습니다.")
            else:
                like.delete()
                messages.info(request, "좋아요가 취소되었습니다.")

        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


class BookmarkedPostsView(LoginRequiredMixin, ListView):
    """
    사용자가 북마크한 게시물 목록을 표시하는 뷰
    """

    model = Bookmark
    template_name = "blogs/bookmarked_posts.html"
    context_object_name = "bookmarks"
    redirect_field_name = "next"

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related(
            "post__writer"
        )
