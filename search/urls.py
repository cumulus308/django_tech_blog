from django.urls import path
from .views import combined_view

app_name = "search"

urlpatterns = [
    path("", combined_view, name="search_result"),
]
