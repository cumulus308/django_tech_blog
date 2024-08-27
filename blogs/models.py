from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    thumbnail = models.ImageField(upload_to="blog/files/%Y/%m/%d/", blank=True)
    img_upload = models.FileField(upload_to="blog/files/%Y/%m/%d/", blank=True)
    hit = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
