from django.urls import path

from .views import (
    CategorySearchDetailListView,
    CategorySearchListView,
    TitleContentSearchListView,
    WriterSearchDetailListView,
    WriterSearchListView,
    combined_view,
)

app_name = "search"

urlpatterns = [
    path("", combined_view, name="search_result"),
    path(
        "titlecontent/",
        TitleContentSearchListView.as_view(),
        name="title_content_result",
    ),
    path("writer/", WriterSearchListView.as_view(), name="writer_result"),
    path(
        "writer/<int:writer_pk>/",
        WriterSearchDetailListView.as_view(),
        name="writer_detail_result",
    ),
    path("category/", CategorySearchListView.as_view(), name="category_result"),
    path(
        "category/<int:category_pk>/",
        CategorySearchDetailListView.as_view(),
        name="category_detail_result",
    ),
]
