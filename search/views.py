from django.shortcuts import render
from django.db.models import Q
from blogs.models import Category, Post
from django.views.generic import ListView


# Create your views here.
def combined_view(request):
    """ """
    q = request.GET.get("q", "")
    posts = Post.objects.all()
    posts = posts.order_by("-created_at")
    # 제목, 내용 필터링
    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(content__icontains=q)).distinct()
    # 글쓴이 필터링
    writer_posts = Post.objects.all().select_related("writer").order_by("-created_at")
    if q:
        writer_posts = writer_posts.filter(writer__username__icontains=q).distinct()
    # 카테고리 필터링
    category_posts = (
        Post.objects.all().select_related("category").order_by("-created_at")
    )
    if q:
        category_posts = category_posts.filter(category__name__icontains=q).distinct()

    # 검색된 갯수
    post_count = posts.count()
    writer_count = writer_posts.count()
    category_count = category_posts.count()

    # 최근 4개만 출력
    posts = posts[:4]
    writer_posts = writer_posts[:4]
    category_posts = category_posts[:4]

    highlighted_posts = []
    highlighted_writers = []
    highlighted_categories = []

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

    for post in writer_posts:
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

        highlighted_writers.append(
            {
                "post": post,
                "highlighted_writer": highlighted_writer,
            }
        )

    for post in category_posts:
        category = post.category.name
        category_pk = post.category.pk
        q_category_position = category.find(q)
        if q_category_position != -1:
            highlighted_category = {
                "start": category[:q_category_position],
                "match": category[q_category_position : q_category_position + len(q)],
                "end": category[q_category_position + len(q) :],
            }
        else:
            highlighted_category = None

        highlighted_categories.append(
            {
                "post": post,
                "highlighted_category": highlighted_category,
                "category_pk": category_pk,
            }
        )

    return render(
        request,
        "search/search_result.html",
        {
            "writer_posts": highlighted_writers,
            "highlighted_posts": highlighted_posts,
            "highlighted_categories": highlighted_categories,
            "writer_count": writer_count,
            "post_count": post_count,
            "category_count": category_count,
            "q": q,
        },
    )


class TitleContentSearchListView(ListView):
    """
    제목과 내용 중 검색어를 포함한 post를 출력하는 뷰
    """

    model = Post
    template_name = "search/search_title_content_result.html"
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
    template_name = "search/search_writer_result.html"
    context_object_name = "posts"

    def get_queryset(self):
        q = self.request.GET.get("q", "")
        queryset = (
            super().get_queryset().select_related("writer").order_by("-created_at")
        )

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


class CategorySearchListView(ListView):
    model = Category
    template_name = "search/search_category_result.html"
    context_object_name = "categories"

    def get_queryset(self):
        q = self.request.GET.get("q", "")
        queryset = super().get_queryset().all().order_by("-created_at")

        if q:
            queryset = queryset.filter(name__icontains=q).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "")
        categories = context["categories"]
        category_count = categories.count()
        highlighted_categories = []

        for category in categories:
            category_name = category.name  # 카테고리 이름을 별도의 변수로 처리
            category_pk = category.pk  # 카테고리 객체의 pk를 가져옴

            q_category_position = category_name.find(q)
            if q_category_position != -1:
                highlighted_category = {
                    "start": category_name[:q_category_position],
                    "match": category_name[
                        q_category_position : q_category_position + len(q)
                    ],
                    "end": category_name[q_category_position + len(q) :],
                }
            else:
                highlighted_category = None

            highlighted_categories.append(
                {
                    "category": category,  # 실제 카테고리 객체를 그대로 유지
                    "highlighted_category": highlighted_category,
                    "category_pk": category_pk,  # 실제 pk 값을 추가
                }
            )

        context["highlighted_categories"] = highlighted_categories
        context["q"] = q
        context["category_count"] = category_count
        return context


class CategorySearchDetailListView(ListView):
    model = Post
    template_name = "search/search_category_detail_result.html"
    context_object_name = "posts"

    def get_queryset(self):
        category_pk = self.kwargs.get("category_pk")
        queryset = super().get_queryset().filter(category_id=category_pk)

        print(queryset)
        return queryset
