from datetime import datetime
import random

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .models import User, SearchSettings
import uuid


class RegisterUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    is_active = serializers.BooleanField(write_only=False)
    password = serializers.CharField(max_length=255, write_only=True)
    password2 = serializers.CharField(max_length=255, write_only=True)
    confirm_registration_uuid = serializers.CharField(max_length=50, default=uuid.uuid4)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'birthday', 'country', 'gender',
                  'email', 'password', 'password2', 'is_active', 'confirm_registration_uuid', 'age',)

    def validate(self, attrs):
        for attr, value in attrs.items():
            if value == '':
                raise ValidationError({'validation_error': f'Поле {attr} не может быть пустым'})
        now = timezone.now()
        if attrs['password'] != attrs['password2']:
            raise ValidationError({'validation_error': 'Пароли не совпадают'})
        if (now.year - attrs['birthday'].year) < 16:
            raise ValidationError({'validation_error': 'Маленький возраст для регистрации'})
        if (now.year - attrs['birthday'].year) > 120:
            raise ValidationError({'validation_error': 'Введите настоящий возраст'})
        return attrs

    def create(self, validated_data):
        default_avatar_id = random.randint(1, 5)
        avatar = f'default_profile_photos/default_profile_photo_{default_avatar_id}.png'
        password = make_password(validated_data['password'])
        validated_data.pop('password2')
        validated_data.pop('password')
        validated_data.pop('is_active')
        return User.objects.create(
            age=timezone.now().year - validated_data['birthday'].year,
            is_active=False,
            password=password,
            profile_photo=avatar,
            **validated_data
        )


class CreateSearchSettingsProfileSerializer(serializers.Serializer):
    age = serializers.IntegerField(read_only=True, write_only=False)
    country = serializers.CharField(default=None, read_only=True, write_only=False)
    gender = serializers.CharField(default=None, read_only=True, write_only=False)
    use_settings = serializers.BooleanField(default=False, read_only=True, write_only=False)

    def create(self, validated_data):
        return SearchSettings.objects.create(**validated_data)


class ConfirmRegistrationsSerializer(serializers.ModelSerializer):
    confirm_registration_uuid = serializers.CharField(default=None, write_only=True)
    is_active = serializers.BooleanField(default=True, write_only=True)

    class Meta:
        model = User
        fields = ('confirm_registration_uuid', 'is_active',)


class UserSettingsProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'birthday', 'password', 'email', 'profile_photo')

    # If be changed username or password - user will be logged out

    def validate(self, attrs):
        for attr, value in attrs.items():
            if value == '':
                raise ValidationError({'validation_error': f'Поле {attr} не может быть пустым'})
        now = timezone.now()
        try:
            if (now.year - attrs['birthday'].year) < 16:
                raise ValidationError({'validation_error': 'Маленький возраст для регистрации'})
            if (now.year - attrs['birthday'].year) > 120:
                raise ValidationError({'validation_error': 'Введите настоящий возраст'})
        except KeyError:
            pass
        return attrs

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.password = make_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance

    #СДЕЛАЙ МАРКИРОВКУ ФОТО ОТ ЮЗЕРА ПО ЕГО ID В НАЧАЛЕ
    #СДЕЛАЙ ПРОВЕРКУ РАЗМЕРА И РАЗРЕШЕНИЯ ЗАГРУЖАЕМОГО ФОТО
    #СДЕЛАЙ УДАЛЕНИЕ СТАРОЙ ФОТО ПРИ ЗАГРУЗКЕ НОВОЙ


class UserRestorePasswordCheckEmailSerializer(serializers.Serializer):
    email = serializers.CharField()


class UserRestorePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    restore_password_uuid = serializers.CharField(default=uuid.uuid4)

    def update(self, instance, validated_data):
        instance.restore_password_uuid = validated_data['restore_password_uuid']
        instance.save()
        return instance


class UserRestorePasswordConfirmSerializer(serializers.Serializer):
    restore_password_uuid = serializers.CharField(default=None, write_only=True)
    password = serializers.CharField(max_length=255, write_only=True)
    password2 = serializers.CharField(max_length=255, write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise ValidationError('Пароли не совпадают')
        return attrs

    def update(self, instance, validated_data):
        instance.password = make_password(validated_data['password'])
        instance.restore_password_uuid = validated_data['restore_password_uuid']
        validated_data.pop('password2')
        validated_data.pop('password')
        instance.save()
        return instance


class UserSearchSettingsProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchSettings
        fields = '__all__'

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
