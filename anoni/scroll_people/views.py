import random
import logging

from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Max
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from user_profile.models import User
from .serializers import *

logger = logging.getLogger('main')

class GetRandomUserScroll(APIView):
    permission_classes = [IsAuthenticated]

    def get_random_user(self, request):
        # CODE RAISE EXCEPTION IF FIRST NOTE DON'T EXIST.
        max_id = User.objects.all().aggregate(max_id=Max("id"))['max_id']
        while True:
            pk = random.randint(1, max_id)
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                continue
                # возможно, нужно будет переписать

            try:
                LikedUsers.objects.get(user_id=request.user.id, liked=pk)
            except LikedUsers.DoesNotExist:
                if user != request.user:
                    JSONUser = {
                        'id': user.id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'age': user.age,
                        'image': str(user.profile_photo)
                    }
                    return JSONUser

    def filter_get_random_user(self, request, age=None, country=None, gender=None):
        """
            В случае успеха проекта и большой нагрузки, будет нужен алгоритм для выборки юзеров,
            да бы они попадались +-одинаково часто. простая выборка по рандому не подходит
        """
        users_filter_list = User.objects.filter(age=age, country=country, gender=gender)
        count_users = users_filter_list.count()
        while True:
            # ПОКА НЕ ЗНАЮ КАК, НО ПРОПИШИ ВЫБОРКУ ПО НЕ ПУСТОМУ ПОЛЮ, ЕСЛИ В АРГУМЕНТАХ ФУНКЦИИ НИЧЕГО НЕ ПЕРЕДАЕТСЯ
            user = users_filter_list[random.randint(0, count_users-1)]
            try:
                LikedUsers.objects.get(liked=user.id, user=request.user)
            except LikedUsers.DoesNotExist:
                if user != request.user:
                    JSONUser = {
                        'id': user.id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'age': user.age,
                    }
                    return JSONUser

    def get(self, request):
        cache_info = cache.get(request.user.username)
        try:
            if cache_info['use_settings']:
                age = cache_info['age']
                country = cache_info['country']
                gender = cache_info['gender']
                user = self.filter_get_random_user(request=request, age=age, country=country, gender=gender)
            else:
                user = self.get_random_user(request=request)
        except TypeError:
            user = self.get_random_user(request=request)
        return Response(user)

    def post(self, request):
        try:
            user_id = request.data['id']
        except KeyError:
            return Response({'error': 'id not passed'}, status=status.HTTP_404_NOT_FOUND)
        try:
            LikedUsers.objects.get(user=request.user, liked=user_id)
            return Response({'message': 'User already liked'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'error': 'Not excepted value'}, status=status.HTTP_404_NOT_FOUND)
        except LikedUsers.DoesNotExist:
            serializer = LikeOrDislikeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
    # Подумай над изменением системы сохранения информации о лайках через кэш
            if serializer.data['like']:
                serializer_like_user = AddLikeUserSerializer(data=request.data)
                serializer_like_user.is_valid(raise_exception=True)
                try:
                    serializer_like_user.save(
                        user=User.objects.get(username=request.user),
                        liked=User.objects.get(pk=user_id).id)
                except User.DoesNotExist:
                    return Response({'error': 'User not exist'}, status=status.HTTP_404_NOT_FOUND)
            return self.get(request)
