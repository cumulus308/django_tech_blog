from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from django.http import HttpResponseNotFound
from django.shortcuts import render

from accounts.views import index


urlpatterns = [
    path("admin/", admin.site.urls, name="index"),
    path("accounts/", include("accounts.urls")),
    path("blogs/", include("blogs.urls")),
    path("search/", include("search.urls")),
    path("", index, name="index"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
