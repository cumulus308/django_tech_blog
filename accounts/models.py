from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.username
