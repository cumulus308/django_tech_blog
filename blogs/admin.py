from django.contrib import admin
from .models import Category, Post, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "writer",
        "category",
        "created_at",
        "updated_at",
        "hit",
        "like_count",
    )
    list_filter = ("created_at", "category", "writer")
    search_fields = ("title", "content", "writer__username")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    inlines = [CommentInline]
    readonly_fields = ("created_at", "updated_at", "hit", "like_count")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "content",
                    "writer",
                    "thumbnail",
                    "category",
                    "hit",
                    "like_count",
                )
            },
        ),
        (
            "Date Information",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("created_at", "updated_at")
    ordering = ("name",)
