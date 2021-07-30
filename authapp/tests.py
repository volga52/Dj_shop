from django.test import TestCase
from django.test.client import Client

from authapp.models import ShopUser


class UserManagementTestCase(TestCase):
    username = 'django'
    email = 'django@gb.local'
    password = 'geekbrains'
    status_code_success = 200
    status_code_redirect = 302

    def setUp(self):
        self.user = ShopUser.objects.create_superuser('django', email=self.email, password=self.password)
        self.client = Client()

    def test_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, self.status_code_success)
        self.assertTrue(response.context['user'].is_anonymous)

        self.client.login(username=self.username, password=self.password)
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, self.status_code_redirect)
        # self.assertFalse(response.context['user'].is_anonymous)

    def test_user_logout(self):
        # данные пользователя
        self.client.login(username=self.username, password=self.password)

        # логинимся
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, self.status_code_redirect)
        # self.assertFalse(response.context['user'].is_anonymous)

        # выходим из системы
        response = self.client.get('/auth/logout/')
        self.assertEqual(response.status_code, self.status_code_redirect)

        # главная после выхода
        response = self.client.get('/')
        self.assertEqual(response.status_code, self.status_code_success)
        self.assertTrue(response.context['user'].is_anonymous)
