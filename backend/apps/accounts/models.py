from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return self.email