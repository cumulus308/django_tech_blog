from django.db import models
from accounts.models import CustomUser


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=10, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=100)
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    thumbnail = models.ImageField(upload_to="blog/files/%Y/%m/%d/", blank=True)
    hit = models.IntegerField(default=0)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    like_count = models.PositiveIntegerField(default=0)

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
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.writer} comment {self.content}"

    @property
    def children(self):
        return Comment.objects.filter(parent=self).reverse()

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False


class Bookmark(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bookmarked {self.post.title}"

    class Meta:
        unique_together = ("user", "post")


class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"
