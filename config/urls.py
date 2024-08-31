from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include
from accounts.views import index


from django.http import HttpResponseNotFound
from django.shortcuts import render


def test_404_viw(request):
    return HttpResponseNotFound(render(request, "404.html"))


urlpatterns = [
    path("admin/", admin.site.urls, name="index"),
    path("accounts/", include("accounts.urls")),
    path("blogs/", include("blogs.urls")),
    path("search/", include("search.urls")),
    path("", index, name="index"),
    path("test-404/", test_404_viw, name="error404"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
