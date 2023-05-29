from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):

    avatar = models.URLField(blank=True)
    is_player = models.BooleanField(default=False)
    is_spvsr = models.BooleanField(default=False)