from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Post, Comment
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.get_object().comments.all().order_by("created_at")
        context["comment_form"] = CommentForm()
        return context

    def get(self, request, pk):
        post = self.get_object()
        return render(
            request,
            "blogs/post_detail.html",
            {
                "post": post,
            },
        )

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

        context = self.get_context_data(object=post)
        context["comment_form"] = form
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
        context["post"] = self.get_object()  # 명시적으로 post 객체를 컨텍스트에 추가
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
