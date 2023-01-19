from django.test.testcases import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from faker import Faker
import django
django.setup()


class NewsTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_get_news(self):
        resp = self.client.get(reverse('news_list'))
        self.assertEqual(resp.status_code, 200)  # success

    def test_post_news(self):
        faker = Faker()
        request_data = {
            'url': faker.url()
        }
        resp = self.client.post(reverse('news_list'), request_data)
        self.assertEqual(resp.status_code, 201)  # Success
        # verify that the saved url is same one that was provided
        self.assertEqual(request_data['url'], resp.json()[0]['url'])
