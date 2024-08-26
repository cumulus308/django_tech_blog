from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from .models import Post
from django.db.models import Q
from .forms import PostForm
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

# Create your views here.
class PostListView(ListView):
    model = Post
    template_name = 'blogs/post_list.html'
    context_object_name = "posts"
    
    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get("q", "")
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(content__icontains=q)
            ).distinct()

        return queryset
    

class PostDetailView(View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        return render(
            request,
            "blogs/post_detail.html",
            {
                "post": post,
            },
        )
    

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blogs/post_form.html"
    login_url = 'accounts:login'
    redirect_field_name = 'next'
    
    def form_valid(self, form):
        form.instance.writer = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("blogs:post_detail", kwargs={"pk": self.object.pk})


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blogs/post_form.html"

    def get_success_url(self):
        return reverse_lazy("blogs:post_detail", kwargs={"pk": self.object.pk})
    

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("blogs:post_list")

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        return HttpResponseForbidden("You do not have permission to delete this post.")

    def post(self, request, *args, **kwargs):
        if self.test_func():
            self.object = self.get_object()
            self.object.delete()
            return redirect(self.success_url)
        else:
            return self.handle_no_permission()
