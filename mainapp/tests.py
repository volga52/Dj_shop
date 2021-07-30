from django.test import TestCase
from django.test.client import Client

from mainapp.models import Product, ProductCategory


class TestMainSmokeTest(TestCase):
    status_cod_success = 200

    def setUp(self):
        cat_1 = ProductCategory.object.create(name='cat_1')
        Product.object.create(
            category=cat_1,
            name='prod 1',
        )
        self.client = Client()

    def test_mainapp_urls(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, self.status_cod_success)

