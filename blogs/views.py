from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from .models import Post
from django.db.models import Q
from .forms import PostForm

# Create your views here.
class PostListView(ListView):
    model = Post
    template_name = 'blogs/Blog_list.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get("q", "")
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(content__icontains=q)
            ).distinct()

        return queryset
    

class PostDetailView(DetailView):
    model = Post
    template_name = 'blogs/Blog_list.html'
    

class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"

    def get_success_url(self):
        return reverse_lazy("posts:post_detail", kwargs={"pk": self.object.pk})


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"

    def get_success_url(self):
        return reverse_lazy("posts:post_detail", kwargs={"pk": self.object.pk})
    

class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy("posts:post_list")