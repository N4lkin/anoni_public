from rest_framework import serializers
from .models import LikedUsers


class LikeOrDislikeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    like = serializers.BooleanField(default=False)
# Dislike не используется, при негативной оценке. отпраляется пустой json


class AddLikeUserSerializer(serializers.Serializer):
    liked = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        return LikedUsers.objects.create(**validated_data)
