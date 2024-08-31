from django.urls import path

from .views import (
    BookmarkedPostsView,
    PostListView,
    PostDetailView,
    PostUpdateView,
    PostCreateView,
    PostDeleteView,
    CommentUpdateView,
    CommentDeleteView,
    ToggleBookmarkView,
    ToggleFollowView,
    ToggleLikeView,
)


app_name = "blogs"

urlpatterns = [
    path("", PostListView.as_view(), name="post_list"),
    path("<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("edit/<int:pk>/", PostUpdateView.as_view(), name="post_update"),
    path("delete/<int:pk>/", PostDeleteView.as_view(), name="post_delete"),
    path("write/", PostCreateView.as_view(), name="post_create"),
    path(
        "comment/<int:pk>/update/", CommentUpdateView.as_view(), name="comment_update"
    ),
    path(
        "comment/<int:pk>/delete/", CommentDeleteView.as_view(), name="comment_delete"
    ),
    path(
        "post/<int:post_id>/toggle-bookmark/",
        ToggleBookmarkView.as_view(),
        name="toggle_bookmark",
    ),
    path(
        "post/<int:post_id>/toggle-like/",
        ToggleLikeView.as_view(),
        name="toggle_like",
    ),
    path(
        "user/<int:user_id>/toggle-follow/",
        ToggleFollowView.as_view(),
        name="toggle_follow",
    ),
    path("bookmarks/", BookmarkedPostsView.as_view(), name="bookmarked_posts"),
]
