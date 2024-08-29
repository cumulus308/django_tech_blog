from django.shortcuts import render
from django.db.models import Q
from blogs.models import Category, Post
from django.views.generic import ListView
from accounts.models import CustomUser


def split_string_via_match(text, search_text):
    """
    text에서 search_text와 match가 발생할 시 매치된 텍스트 이전 텍스트, 매치된 텍스트, 매치된 텍스트 이후 텍스트를 반환
    match가 발생하지 않는 경우 None를 반환
    """
    match_pos = text.find(search_text)
    result = None

    if match_pos != -1:
        result = {
            "start": text[:match_pos],
            "match": text[match_pos : match_pos + len(search_text)],
            "end": text[match_pos + len(search_text) :],
        }

    return result


# Create your views here.
def combined_view(request):
    """
    이렇게 함수에 대한 독스트링을 적어주시면 보수하기 편합니다.

    request = {
        q: string, 검색할 문자열
    }

    response = {
        posts : 4개의 포스트
        writers : 4개의 유저
        categories:4개 카테고리

        writer_count: 전체 작성자의 수
        post_count: 전체 포스트의 수
        category_count: 전체 카테고리의 수
    }
    """
    # 초기화
    searching_string = request.GET.get("q", None)
    posts = Post.objects.all().order_by("-created_at")

    # q가 있는 경우(searching_string가 있는 경우)
    if searching_string:
        posts = posts.filter(
            Q(title__icontains=searching_string)
            | Q(content__icontains=searching_string)
        )

    # 추가로 로드할 모델의 pk를 가져옵니다(db hit 없음)
    posts_writer_pk = posts.values_list("writer_id", flat=True).distinct()
    posts_category_pk = posts.values_list("category_id", flat=True).distinct()

    # pk를 바탕으로 데이터를 불러옵니다(db hit 발생)
    writers = CustomUser.objects.filter(pk__in=posts_writer_pk)  # => 쿼리셋
    categories = Category.objects.filter(pk__in=posts_category_pk)

    # 각 데이터를 카운팅
    post_count = posts.count()
    writer_count = writers.count()
    category_count = categories.count()

    # 하이라이트 관련 끝입니다.
    if searching_string:
        highlighted_titles = [
            split_string_via_match(post.title, searching_string) for post in posts[:4]
        ]

    # 반환
    return render(
        request,
        "search/search_result.html",
        {
            "writer_posts": writers[:4],
            "highlighted_posts": posts[:4],
            "highlighted_categories": categories[:4],
            "highlighted_titles": highlighted_titles,
            "writer_count": writer_count,
            "post_count": post_count,
            "category_count": category_count,
            "q": "",
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


# def combined_view(request):
#     """ """
#     q = request.GET.get("q", "")
#     posts = Post.objects.all()
#     posts = posts.order_by("-created_at")
#     # 제목, 내용 필터링
#     if q:
#         posts = posts.filter(Q(title__icontains=q) | Q(content__icontains=q)).distinct()

#     # 글쓴이 필터링
#     if q:
#         writers = writers.filter(writer__username__icontains=q).distinct()

#     # 카테고리 필터링
#     categories = Category.objects.all().order_by("-created_at")
#     if q:
#         categories = categories.filter(category__name__icontains=q).distinct()

#     # 검색된 갯수
#     post_count = posts.count()
#     writer_count = writers.count()
#     category_count = categories.count()

#     # 최근 4개만 출력
#     posts = posts[:4]
#     writers = writers[:4]
#     categories = categories[:4]

#     highlighted_posts = []
#     highlighted_writers = []
#     highlighted_categories = []

#     for post in posts:
#         title = post.title
#         content = post.content

#         q_title_position = title.find(q)
#         if q_title_position != -1:
#             highlighted_title = {
#                 "start": title[:q_title_position],
#                 "match": title[q_title_position : q_title_position + len(q)],
#                 "end": title[q_title_position + len(q) :],
#             }
#         else:
#             highlighted_title = None

#         q_content_position = content.find(q)
#         if q_content_position != -1:
#             highlighted_content = {
#                 "start": content[:q_content_position],
#                 "match": content[q_content_position : q_content_position + len(q)],
#                 "end": content[q_content_position + len(q) :],
#             }
#         else:
#             highlighted_content = None

#         highlighted_posts.append(
#             {
#                 "post": post,
#                 "highlighted_title": highlighted_title,
#                 "highlighted_content": highlighted_content,
#             }
#         )

#     for writer in writers:
#         print(writer)
#         writer = writer.writer.username

#         q_writer_position = writer.find(q)
#         if q_writer_position != -1:
#             highlighted_writer = {
#                 "start": writer[:q_writer_position],
#                 "match": writer[q_writer_position : q_writer_position + len(q)],
#                 "end": writer[q_writer_position + len(q) :],
#             }
#         else:
#             highlighted_writer = None

#         highlighted_writers.append(
#             {
#                 "post": post,
#                 "highlighted_writer": highlighted_writer,
#             }
#         )

#     for category in categories:
#         category_pk = category.pk
#         category = category.name
#         q_category_position = category.find(q)
#         if q_category_position != -1:
#             highlighted_category = {
#                 "start": category[:q_category_position],
#                 "match": category[q_category_position : q_category_position + len(q)],
#                 "end": category[q_category_position + len(q) :],
#             }
#         else:
#             highlighted_category = None

#         highlighted_categories.append(
#             {
#                 "category": category,
#                 "highlighted_category": highlighted_category,
#                 "category_pk": category_pk,
#             }
#         )

#     return render(
#         request,
#         "search/search_result.html",
#         {
#             "writer_posts": highlighted_writers,
#             "highlighted_posts": highlighted_posts,
#             "highlighted_categories": highlighted_categories,
#             "writer_count": writer_count,
#             "post_count": post_count,
#             "category_count": category_count,
#             "q": q,
#         },
#     )
