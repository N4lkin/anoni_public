from django.db import models
from django.db.models import CASCADE

from user_profile.models import User


class LikedUsers(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    liked = models.IntegerField()
