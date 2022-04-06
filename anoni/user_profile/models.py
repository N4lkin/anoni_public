from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CASCADE

from .utils import *


class User(AbstractUser):
    birthday = models.DateField(verbose_name='Дата рождения', blank=True)
    age = models.PositiveIntegerField(null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/',
                                      default='default_profile_photos/default_profile_photo_1.png')
    confirm_registration_uuid = models.CharField(max_length=50, null=True)
    restore_password_uuid = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=255, choices=countries, default=None)
    gender = models.CharField(max_length=30, choices=gender, default=None)

    def __str__(self):
        return self.username


class SearchSettings(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE)
    age = models.PositiveIntegerField()
    country = models.CharField(max_length=255, choices=countries)
    gender = models.CharField(max_length=30, choices=gender)
    use_settings = models.BooleanField(default=False)
