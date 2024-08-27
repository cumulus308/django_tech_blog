from django.shortcuts import render
from django.db.models import Q
from blogs.models import Post


# Create your views here.
def combined_view(request):
    q = request.GET.get("q", "")
    posts = Post.objects.all()
    writers = posts.select_related("writer")

    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(content__icontains=q)).distinct()
        writers = posts.filter(writer__username__icontains=q)

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
            "writers": writers,
            "highlighted_posts": highlighted_posts,
            "q": q,
        },
    )
