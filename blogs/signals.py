from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Like


@receiver(post_save, sender=Like)
def update_like_count_on_save(sender, instance, **kwargs):
    post = instance.post
    post.like_count = post.post_likes.count()
    post.save()


@receiver(post_delete, sender=Like)
def update_like_count_on_delete(sender, instance, **kwargs):
    post = instance.post
    post.like_count = post.post_likes.count()
    post.save()
