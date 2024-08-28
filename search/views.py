from django.shortcuts import render
from django.db.models import Q
from blogs.models import Post
from django.views.generic import ListView


# Create your views here.
def combined_view(request):
    q = request.GET.get("q", "")
    posts = Post.objects.all()
    posts = posts.order_by("-created_at")

    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(content__icontains=q)).distinct()

    writer_posts = Post.objects.all().select_related("writer").order_by("-created_at")
    if q:
        writer_posts = writer_posts.filter(writer__username__icontains=q).distinct()

    post_count = posts.count()
    writer_count = writer_posts.count()

    posts = posts[:4]
    writer_posts = writer_posts[:4]

    highlighted_posts = []

    for post in posts:
        title = post.title
        content = post.content

        q_title_position = title.find(q)
        if q_title_position != -1:
            highlighted_title = {
                "start": title[:q_title_position],
                "match": title[q_title_position : q_title_position + len(q)],
                "end": title[q_title_position + len(q) :],
            }
        else:
            highlighted_title = None

        q_content_position = content.find(q)
        if q_content_position != -1:
            highlighted_content = {
                "start": content[:q_content_position],
                "match": content[q_content_position : q_content_position + len(q)],
                "end": content[q_content_position + len(q) :],
            }
        else:
            highlighted_content = None

        highlighted_posts.append(
            {
                "post": post,
                "highlighted_title": highlighted_title,
                "highlighted_content": highlighted_content,
            }
        )

    return render(
        request,
        "search/search_result.html",
        {
            "writer_posts": writer_posts,
            "highlighted_posts": highlighted_posts,
            "writer_count": writer_count,
            "post_count": post_count,
            "q": q,
        },
    )


class TitleContentSearchListView(ListView):
    """
    제목과 내용 중 검색어를 포함한 post를 출력하는 뷰
    """

    model = Post
    template_name = "blogs/search_title_content_result.html"
    context_object_name = "posts"

    def get_queryset(self):
        q = self.request.GET.get("q", "")
        queryset = super().get_queryset().order_by("-created_at")
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(content__icontains=q)
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "")
        posts = context["posts"]
        post_count = posts.count()
        highlighted_posts = []

        for post in posts:
            title = post.title
            content = post.content

            q_title_position = title.find(q)
            if q_title_position != -1:
                highlighted_title = {
                    "start": title[:q_title_position],
                    "match": title[q_title_position : q_title_position + len(q)],
                    "end": title[q_title_position + len(q) :],
                }
            else:
                highlighted_title = None

            q_content_position = content.find(q)
            if q_content_position != -1:
                highlighted_content = {
                    "start": content[:q_content_position],
                    "match": content[q_content_position : q_content_position + len(q)],
                    "end": content[q_content_position + len(q) :],
                }
            else:
                highlighted_content = None

            highlighted_posts.append(
                {
                    "post": post,
                    "highlighted_title": highlighted_title,
                    "highlighted_content": highlighted_content,
                }
            )

        context["highlighted_posts"] = highlighted_posts
        context["q"] = q
        context["post_count"] = post_count

        return context


class WriterPostSearchListView(ListView):
    """
    작성자 이름에 검색어가 포함된 게시물을 출력하는 뷰
    """

    model = Post
    template_name = "blogs/search_writer_result.html"
    context_object_name = "posts"

    def get_queryset(self):
        q = self.request.GET.get("q", "")
        queryset = super().get_queryset().order_by("-created_at")

        if q:
            queryset = queryset.filter(writer__username__icontains=q).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "")
        posts = context["posts"]
        post_count = posts.count()
        highlighted_posts = []

        for post in posts:
            writer = post.writer.username

            q_writer_position = writer.find(q)
            if q_writer_position != -1:
                highlighted_writer = {
                    "start": writer[:q_writer_position],
                    "match": writer[q_writer_position : q_writer_position + len(q)],
                    "end": writer[q_writer_position + len(q) :],
                }
            else:
                highlighted_writer = None

            highlighted_posts.append(
                {
                    "post": post,
                    "highlighted_writer": highlighted_writer,
                }
            )

        context["highlighted_posts"] = highlighted_posts
        context["q"] = q
        context["post_count"] = post_count

        return context
