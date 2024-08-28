from django.db import models
from accounts.models import CustomUser


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=100)
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    thumbnail = models.ImageField(upload_to="blog/files/%Y/%m/%d/", blank=True)
    img_upload = models.ImageField(upload_to="blog/files/%Y/%m/%d/", blank=True)
    hit = models.IntegerField(default=0)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
