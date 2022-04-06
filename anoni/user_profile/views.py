from django.core.cache import cache
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from email_backend.tasks import send_mail_for_registration_user, send_mail_for_restore_user_password
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import *


class RegisterUser(APIView):
    @staticmethod
    def post(request):
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        settings_serializer = CreateSearchSettingsProfileSerializer(data=request.data)
        settings_serializer.is_valid(raise_exception=True)
        serializer.save()
        settings_serializer.save(
            user=User.objects.get(username=serializer.data['username']),
        )
        send_mail_for_registration_user.delay(
            user_email=serializer.data['email'],
            uuid_link=serializer.data['confirm_registration_uuid'])
        return Response({'message': 'Please check your email to confirm registration'}, status=status.HTTP_200_OK)


class ConfirmRegistrations(APIView):
    @staticmethod
    def get(request, uuid_link):
        try:
            user = User.objects.get(confirm_registration_uuid=uuid_link)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ConfirmRegistrationsSerializer(data=request.data, instance=user)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            confirm_registration_uuid=None,
            is_active=True
        )
        return Response({'message': 'Registration confirm'}, status=status.HTTP_200_OK)


class UserSettingsProfile(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @staticmethod
    def patch(request):
        user = User.objects.get(username=request.user)
        serializer = UserSettingsProfileSerializer(data=request.data, instance=user, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Data changed successfully'}, status=status.HTTP_200_OK)


class UserFilterSettingsProfile(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def patch(request):
        cache.delete(request.user.username)
        user = SearchSettings.objects.get(user=User.objects.get(username=request.user))
        serializer = UserSearchSettingsProfileSerializer(data=request.data, instance=user, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache.set(request.user.username, serializer.data, None)
        return Response({'message': 'Data changed successfully'}, status=status.HTTP_200_OK)


class UserRestorePassword(APIView):
    @staticmethod
    def put(request):
        email_serializer = UserRestorePasswordCheckEmailSerializer(data=request.data)
        email_serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=email_serializer.validated_data['email'])
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        main_serializer = UserRestorePasswordSerializer(
            instance=user,
            data={
                'email': email_serializer.validated_data['email']
            })
        main_serializer.is_valid(raise_exception=True)
        send_mail_for_restore_user_password.delay(
            user_email=main_serializer.validated_data['email'],
            restore_password_uuid=main_serializer.validated_data['restore_password_uuid']
        )
        main_serializer.save()
        return Response({'message': 'Please check your email'}, status=status.HTTP_200_OK)


class UserRestorePasswordConfirm(APIView):
    @staticmethod
    def post(request, uuid_link):
        try:
            user = User.objects.get(restore_password_uuid=uuid_link)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserRestorePasswordConfirmSerializer(data=request.data, instance=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'password changed successfully'}, status=status.HTTP_200_OK)
