from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Bookmark, Category, Post, Comment
from django.db.models import Q
from .forms import CommentForm, PostForm
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin


# Create your views here.
class PostListView(ListView):
    model = Post
    template_name = "blogs/post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get("q", "")
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(content__icontains=q)
            ).distinct()

        queryset = queryset.order_by("-created_at")
        return queryset


class PostDetailView(View):
    def get_object(self):
        pk = self.kwargs.get("pk")
        return get_object_or_404(Post, pk=pk)

    def get(self, request, pk):
        post = self.get_object()
        post.hit += 1
        post.save()

        # 북마크 상태를 확인하여 컨텍스트에 추가
        is_bookmarked = False
        if request.user.is_authenticated:
            is_bookmarked = Bookmark.objects.filter(
                user=request.user, post=post
            ).exists()

        context = {
            "post": post,
            "categories": Category.objects.all(),
            "comments": post.comments.all().order_by("created_at"),
            "comment_form": CommentForm(),
            "is_bookmarked": is_bookmarked,  # 북마크 상태를 컨텍스트에 추가
        }
        return render(request, "blogs/post_detail.html", context)

    def post(self, request, *args, **kwargs):
        post = self.get_object()

        if not request.user.is_authenticated:
            messages.error(request, "You need to be logged in to comment.")
            return redirect("accounts:login")

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.writer = request.user
            comment.post = post
            comment.save()
            messages.success(request, "Your comment has been added successfully.")
            return redirect("blogs:post_detail", pk=post.pk)

        context = {
            "post": post,
            "categories": Category.objects.all(),
            "comments": post.comments.all().order_by("created_at"),
            "comment_form": form,
        }
        return render(request, "blogs/post_detail.html", context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blogs/post_form.html"
    login_url = "accounts:login"
    redirect_field_name = "next"

    def form_valid(self, form):
        form.instance.writer = self.request.user
        return super().form_valid(form)

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
        if obj:
            messages.info(self.request, "You are now editing your post.")
        return obj

    def form_valid(self, form):
        messages.success(self.request, "Your post has been updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "There was an error updating your post. Please check the form.",
        )
        return super().form_invalid(form)


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
        comment = Comment.objects.get(pk=self.kwargs["pk"])
        content = request.POST.get("content")
        comment.content = content
        comment.save()
        return JsonResponse({"content": comment.content})

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
        messages.error(
            self.request, "You do not have permission to delete this comment."
        )
        return redirect("blogs:post_detail", pk=self.get_object().post.pk)

    def get_success_url(self):
        return reverse("blogs:post_detail", kwargs={"pk": self.object.post.pk})

    def post(self, request, *args, **kwargs):
        messages.success(self.request, "Your comment has been deleted successfully.")
        return self.delete(request, *args, **kwargs)


class ToggleBookmarkView(View):
    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseForbidden()

        # URL에서 전달된 post_id를 사용하여 Post 객체를 가져옵니다.
        post_id = kwargs.get("post_id")  # 'kwargs'에서 'post_id'를 가져옵니다.
        post = get_object_or_404(Post, id=post_id)  # post_id로 Post 객체를 가져옵니다.

        bookmark, created = Bookmark.objects.get_or_create(user=user, post=post)

        if not created:
            bookmark.delete()

        return redirect(request.META.get("HTTP_REFERER", "/"))
