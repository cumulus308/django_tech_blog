from django.urls import path
from .views import combined_view, TitleContentSearchListView, WriterPostSearchListView

app_name = "search"

urlpatterns = [
    path("", combined_view, name="search_result"),
    path(
        "titlecontent",
        TitleContentSearchListView.as_view(),
        name="title_content_result",
    ),
    path("writer", WriterPostSearchListView.as_view(), name="writer_result"),
]
