from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user_profile.models import User


class GetRandomUserScrollNotFilterAPITestCase(APITestCase):
    def setUp(self):
        url = reverse('register')
        data = {
            'password': 'qwerty123',
            'password2': 'qwerty123',
            'username': 'ADMINNotFilterUserTest',
            'first_name': 'Biba',
            'last_name': 'Boba',
            'email': 'test.email@email.com',
            'birthday': '2000-01-01',
            'country': 'rus',
            'gender': 'man',
            'is_active': True
        }
        self.client.post(url, data, format='json')
        user = User.objects.get(username='ADMINNotFilterUserTest')
        self.client.force_authenticate(user)

        User.objects.create(password='qwerty123',
                            first_name='SomeFirstName',
                            last_name='SomeLastName',
                            username='UserTest',
                            gender='man',
                            country='rus',
                            age=22,
                            is_active=True)

    def test_make_cache(self):
        url = reverse('filter_settings_data')
        data = {
            'use_settings': False,
            'gender': 'man',
            'country': 'rus',
            'age': 22
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_not_filter(self):
        url = reverse('get_random_user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'id': 2,
                                         'first_name': 'SomeFirstName',
                                         'last_name': 'SomeLastName',
                                         'age': 22})

    # def test_post_not_filter(self):
    #     url = reverse('get_random_user')
    #     data = {
    #         "like": "True",
    #         "id": 2
    #     }
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(LikedUsers.objects.count(), 1)
    #     self.assertEqual(LikedUsers.objects.get().username, 'UserTest')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        # ЭТОТ ТЕСТ ПРОВОДИТЬ ОТДЕЛЬНО ОТ ДРУГИХ. В ОБЩЕМ НАБОРЕ ОН ФЕЙЛИТСЯ


class GetRandomUserScrollUseFilterAPITestCase(APITestCase):
    def setUp(self):
        url = reverse('register')
        data = {
            'password': 'qwerty123',
            'password2': 'qwerty123',
            'username': 'ADMINFilterUserTest',
            'first_name': 'Biba',
            'last_name': 'Boba',
            'email': 'test.email@email.com',
            'birthday': '2000-01-01',
            'country': 'rus',
            'gender': 'man',
            'is_active': True
        }

        data_test_user = {
            'password': 'qwerty123',
            'password2': 'qwerty123',
            'username': 'UserTest',
            'first_name': 'Olga',
            'last_name': 'Sveta',
            'email': 'test.email@email.com',
            'birthday': '2000-01-01',
            'country': 'rus',
            'gender': 'man',
            'is_active': True
        }
        self.client.post(url, data_test_user, format='json')
        self.client.post(url, data, format='json')
        user = User.objects.get(username='ADMINFilterUserTest')
        self.client.force_authenticate(user)

    def test_make_cache(self):
        url = reverse('filter_settings_data')
        data = {
            'use_settings': True,
            'gender': 'man',
            'country': 'rus',
            'age': 22
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_use_filter(self):
        url = reverse('get_random_user')
        response = self.client.get(url)
        self.assertEqual(response.data, {
            'id': 5,
            'first_name': 'Olga',
            'last_name': 'Sveta',
            'age': 22
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_post_use_filter(self):
    #     url = reverse('get_random_user')
    #     data = {
    #         "like": "True",
    #         "id": 7
    #     }
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(LikedUsers.objects.count(), 1)
    #     self.assertEqual(LikedUsers.objects.get().username, 'UserTest')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

# тут херня какая-то с тестом с фильтром. работает через раз.
# UPD: она резко исчезла, но имей ввиду
