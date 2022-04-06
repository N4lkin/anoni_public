from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user_profile.models import User


class RegisterUserAPITestCase(APITestCase):
    def test_post(self):
        url = reverse('register')
        data = {
            'password': 'qwerty123',
            'password2': 'qwerty123',
            'username': 'UserTest',
            'first_name': 'Biba',
            'last_name': 'Boba',
            'email': 'test.email@email.com',
            'birthday': '2000-01-01',
            'country': 'rus',
            'gender': 'man',
            'is_active': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'UserTest')
        self.assertEqual(User.objects.get().is_active, False)
        # ПЕРЕПИШИ ПЕРВЫЙ И ПОСЛЕДНИЙ ТЕСТ. ОНИ ФЕЙЛЯТСЯ, НО ПРИ РУЧНОМ ТЕСТИРОВАННИ - ВСЕ ОК


class UserSettingsProfileAPITestCase(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username='UserTest',
                                        password='qwerty123')
        self.client.force_authenticate(user)

    def test_patch(self):
        url = reverse('settings_profile_data')
        data0 = {
            'first_name': 'Biba',
            'last_name': 'Boba',
        }
        response0 = self.client.patch(url, data0, format='json')

        self.assertEqual(response0.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'UserTest')

        data1 = {
            'username': 'SuperUserTest',
        }
        response1 = self.client.patch(url, data1, format='json')

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'SuperUserTest')


class UserRestorePasswordTestCase(APITestCase):
    def test_put(self):
        User.objects.create_user(username='UserTest',
                                 password='qwerty123',
                                 email='test.mail@mail.com')
        url = reverse('user_restore_password')
        data = {
            'email': 'test.mail@mail.com'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_error(self):
        User.objects.create_user(username='UserTest',
                                 password='qwerty123',
                                 email='test.mail@mail.com')
        url = reverse('user_restore_password')
        data = {
            'email': 'wrong_test.mail@mail.com'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
