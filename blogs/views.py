import json
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib import messages
from accounts.models import CustomUser, Follow
from .models import Bookmark, Category, Like, Post, Comment
from django.db.models import Q
from django.db.models import F
from .forms import CommentForm, PostForm
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin


class PostListView(ListView):
    model = Post
    template_name = "blogs/post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get("q", "")
        order_by = self.request.GET.get("order_by", "-created_at")
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(content__icontains=q)
            ).distinct()

        valid_order_fields = ["-created_at", "-hit", "-like_count"]
        if order_by in valid_order_fields:
            queryset = queryset.order_by(order_by)
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get("per_page", 12)
        return per_page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context["paginator"]
        page = context["page_obj"]
        context["is_paginated"] = page.has_other_pages()
        context["current_order"] = self.request.GET.get("order_by", "-created_at")

        # 페이지 범위 계산
        if paginator.num_pages <= 9:
            context["page_range"] = range(1, paginator.num_pages + 1)
        else:
            start_index = max(1, page.number - 4)
            end_index = min(paginator.num_pages, page.number + 4)
            context["page_range"] = range(start_index, end_index + 1)

        return context


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "blogs/post_detail.html"
    context_object_name = "post"

    def get_object(self):
        obj = super().get_object()
        if self.request.user != obj.writer:
            Post.objects.filter(pk=obj.pk).update(hit=F("hit") + 1)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        user = self.request.user

        # 댓글과 대댓글
        comments = Comment.objects.filter(post=post, parent=None)
        context["comments"] = comments

        # 북마크 상태
        context["is_bookmarked"] = Bookmark.objects.filter(
            user=user, post=post
        ).exists()

        # 팔로우 상태
        context["is_following"] = Follow.objects.filter(
            follower=user, following=post.writer
        ).exists()

        # 좋아요 상태
        context["is_liked"] = Like.objects.filter(user=user, post=post).exists()

        return context

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.writer = request.user

            # parent_id가 제공된 경우 (대댓글인 경우)
            parent_id = request.POST.get("parent")
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)
                comment.parent = parent_comment

            comment.save()
        return redirect("blogs:post_detail", pk=post.pk)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blogs/post_form.html"
    login_url = "accounts:login"
    redirect_field_name = "next"

    def form_valid(self, form):
        form.instance.writer = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context["errors"] = form.errors
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse_lazy("blogs:post_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blogs/post_form.html"

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.writer

    def handle_no_permission(self):
        return HttpResponseForbidden("You do not have permission to edit this post.")

    def get_success_url(self):
        return reverse_lazy("blogs:post_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = self.get_object()
        context["categories"] = Category.objects.all()
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        return obj

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context["errors"] = form.errors
        return self.render_to_response(context)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("blogs:post_list")

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.writer

    def handle_no_permission(self):
        return HttpResponseForbidden("You do not have permission to delete this post.")

    def post(self, request, *args, **kwargs):
        if self.test_func():
            self.object = self.get_object()
            self.object.delete()
            return redirect(self.success_url)
        else:
            return self.handle_no_permission()


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        comment = Comment.objects.get(pk=self.kwargs["pk"])
        return self.request.user == comment.writer

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            content = data.get("content")
            comment = Comment.objects.get(pk=self.kwargs["pk"])
            comment.content = content
            comment.save()
            return JsonResponse({"success": True, "content": comment.content})
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "Invalid JSON data"}, status=400
            )

    def handle_no_permission(self):
        return JsonResponse(
            {"error": "You do not have permission to edit this comment."}, status=403
        )


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.writer

    def handle_no_permission(self):
        return redirect("blogs:post_detail", pk=self.get_object().post.pk)

    def get_success_url(self):
        return reverse("blogs:post_detail", kwargs={"pk": self.object.post.pk})

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class ToggleBookmarkView(View):
    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseForbidden()

        post_id = kwargs.get("post_id")
        post = get_object_or_404(Post, id=post_id)

        bookmark, created = Bookmark.objects.get_or_create(user=user, post=post)

        if not created:
            bookmark.delete()

        return redirect(request.META.get("HTTP_REFERER", "/"))


class ToggleFollowView(View):
    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect(request.META.get("HTTP_REFERER", "/"))

        follow_user_id = kwargs.get("user_id")
        follow_user = get_object_or_404(CustomUser, id=follow_user_id)

        if user == follow_user:
            messages.error(request, "본인을 팔로우할 수 없습니다.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        follow, created = Follow.objects.get_or_create(
            follower=user, following=follow_user
        )

        if not created:
            follow.delete()

        return redirect(request.META.get("HTTP_REFERER", "/"))


class ToggleLikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseForbidden()

        post_id = kwargs.get("post_id")
        post = get_object_or_404(Post, id=post_id)

        if post.writer == request.user:
            messages.error(request, "자신의 게시물에는 좋아요를 누를 수 없습니다.")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()
            messages.info(request, "좋아요가 취소되었습니다.")
        else:
            messages.success(request, "게시물을 좋아요했습니다.")

        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


class BookmarkedPostsView(LoginRequiredMixin, ListView):
    model = Bookmark
    template_name = "blogs/bookmarked_posts.html"
    context_object_name = "bookmarks"

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related("post")
