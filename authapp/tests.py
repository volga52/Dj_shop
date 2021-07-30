from django.conf import settings
from django.test import TestCase
from django.test.client import Client

from authapp.models import ShopUser


class UserManagementTestCase(TestCase):
    username = 'django'
    email = 'django@gb.local'
    password = 'geekbrains'
    status_code_success = 200
    status_code_redirect = 302

    new_user_data = {
        'username': 'user01',
        'first_name': 'user',
        'last_name': 'Uuser',
        'password1': 'geekbrains',
        'password2': 'geekbrains',
        'age': 33,
        'email': 'user1@gb.local'
    }

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

    def test_user_register(self):
        response = self.client.post('/auth/register/', data=self.new_user_data)
        self.assertEqual(response.status_code, self.status_code_redirect)

        new_user = ShopUser.objects.get(username=self.new_user_data['username'])

        activation_url = f'{settings.DOMAIN_NAME}/auth/verify/{new_user.email}/{new_user.activation_key}/'

        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, self.status_code_success)

        new_user.refresh_from_db()
        self.assertTrue(new_user.is_active)

    def test_basket_login_redirect(self):
        # без логина должен переадресовать
        response = self.client.get('/basket/')
        self.assertEqual(response.url, '/auth/login/?next=/basket/')
        self.assertEqual(response.status_code, self.status_code_redirect)

        # с логином все должно быть хорошо
        self.client.login(username=self.username, password=self.password)

        response = self.client.get('/basket/')
        self.assertEqual(response.status_code, self.status_code_success)
        self.assertEqual(list(response.context['basket']), [])
        self.assertEqual(response.request['PATH_INFO'], '/basket/')
        self.assertIn('Ваша корзина, Пользователь', response.content.decode())
