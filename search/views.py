from django.shortcuts import render
from django.db.models import Q
from blogs.models import Category, Post
from django.views.generic import ListView
from accounts.models import CustomUser
from utils import split_string_via_match


def combined_view(request):
    """
    이 함수는 요청을 받아 검색어에 해당하는 포스트, 글쓴이, 카테고리 정보를 반환합니다.

    request = {
        q: string, 검색할 문자열
    }

    response = {
        posts : 최근 4개의 포스트
        writers : 최근 글쓴 4명의 유저
        categories: 최근 글이 작성된 4개 카테고리

        writer_count: 전체 작성자의 수
        post_count: 전체 포스트의 수
        category_count: 전체 카테고리의 수
    }
    """
    # 초기화
    searching_string = request.GET.get("q", "")
    posts = Post.objects.all().order_by("-created_at")

    # 추가로 로드할 모델의 pk를 가져옵니다(db hit 없음)
    posts_writer_pk = posts.values_list("writer_id", flat=True).distinct()
    posts_category_pk = posts.values_list("category_id", flat=True).distinct()

    # pk를 바탕으로 데이터를 불러옵니다(db hit 발생)
    writers = CustomUser.objects.filter(pk__in=posts_writer_pk)
    categories = Category.objects.filter(pk__in=posts_category_pk)

    # 반환할 빈 리스트 생성
    highlighted_posts = []
    highlighted_writers = []
    highlighted_categories = []

    if searching_string:
        posts = posts.filter(
            Q(title__icontains=searching_string)
            | Q(content__icontains=searching_string)
        ).distinct()
        writers = writers.filter(username__icontains=searching_string).distinct()
        categories = categories.filter(name__icontains=searching_string).distinct()

    for post in posts[:4]:
        highlighted_title = (
            split_string_via_match(post.title, searching_string)
            if searching_string
            else None
        )
        highlighted_content = (
            split_string_via_match(post.content, searching_string)
            if searching_string
            else None
        )
        highlighted_posts.append(
            {
                "post": post,
                "highlighted_title": highlighted_title,
                "highlighted_content": highlighted_content,
            }
        )
        # [i if i==12 else "No" for i in v ]
        [
            split_string_via_match(writer.username, searching_string)
            if searching_string
            else None
            for writer in writers[:4]
        ]

    for writer in writers[:4]:
        highlighted_writer = (
            split_string_via_match(writer.username, searching_string)
            # if searching_string
            # else None
        )
        highlighted_writers.append(
            {
                "writer": writer,
                "highlighted_writer": highlighted_writer,
            }
        )

    for category in categories[:4]:
        highlighted_category = (
            split_string_via_match(category.name, searching_string)
            if searching_string
            else None
        )
        highlighted_categories.append(
            {
                "category": category,
                "highlighted_category": highlighted_category,
            }
        )

    # 각 데이터를 카운팅
    post_count = posts.count()
    writer_count = writers.count()
    category_count = categories.count()

    # 반환
    return render(
        request,
        "search/search_result.html",
        {
            "highlighted_posts": highlighted_posts,
            "highlighted_writers": highlighted_writers,
            "highlighted_categories": highlighted_categories,
            "writer_count": writer_count,
            "post_count": post_count,
            "category_count": category_count,
            "q": searching_string,
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

        return queryset.values("pk", "title", "content")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "")
        posts = context["posts"]

        highlighted_posts = []
        for post in posts:
            highlighted_title = split_string_via_match(post["title"], q)
            highlighted_content = split_string_via_match(post["content"], q)

            highlighted_posts.append(
                {
                    "post_pk": post["pk"],
                    "post_title": post["title"],
                    "post_content": post["content"],
                    "highlighted_title": highlighted_title,
                    "highlighted_content": highlighted_content,
                }
            )

        context["highlighted_posts"] = highlighted_posts
        context["q"] = q
        context["post_count"] = len(posts)
        return context


class WriterSearchListView(ListView):
    """
    작성자 이름에 검색어가 포함된 게시물을 출력하는 뷰
    """

    model = CustomUser
    template_name = "search/search_writer_result.html"
    context_object_name = "writers"

    def get_queryset(self):
        q = self.request.GET.get("q", "")
        queryset = super().get_queryset().order_by("-date_joined")

        if q:
            queryset = queryset.filter(username__icontains=q).distinct()

        return queryset.values("pk", "username")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "")
        writers = context["writers"]

        highlighted_writers = []
        for writer in writers:
            highlighted_writer = split_string_via_match(writer["username"], q)

            highlighted_writers.append(
                {
                    "writer_pk": writer["pk"],
                    "writer_username": writer["username"],
                    "highlighted_writer": highlighted_writer,
                }
            )

        context["highlighted_writers"] = highlighted_writers
        context["q"] = q
        context["writer_count"] = len(writers)
        return context


class CategorySearchListView(ListView):
    model = Category
    template_name = "search/search_category_result.html"
    context_object_name = "categories"

    def get_queryset(self):
        q = self.request.GET.get("q", "")
        queryset = super().get_queryset().order_by("-created_at")

        if q:
            queryset = queryset.filter(name__icontains=q).distinct()

        return queryset.values("pk", "name")  # 필요한 필드만 선택

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "")
        categories = context["categories"]

        highlighted_categories = []
        for category in categories:
            highlighted_category = split_string_via_match(category["name"], q)

            highlighted_categories.append(
                {
                    "category_pk": category["pk"],
                    "category_name": category["name"],
                    "highlighted_category": highlighted_category,
                }
            )

        context["highlighted_categories"] = highlighted_categories
        context["q"] = q
        context["category_count"] = len(categories)
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


class WriterSearchDetailListView(ListView):
    model = Post
    template_name = "search/search_writer_detail_result.html"
    context_object_name = "posts"

    def get_queryset(self):
        writer_pk = self.kwargs.get("writer_pk")
        queryset = super().get_queryset().filter(writer_id=writer_pk)

        print(queryset)
        return queryset
