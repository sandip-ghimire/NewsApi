from django.test.testcases import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from faker import Faker
import django
django.setup()


class ChannelsTest(TestCase):
    post_response = None

    def setUp(self):
        self.client = APIClient()

    def post_channel(self):
        faker = Faker()
        request_data = {
            'name': faker.name()
        }
        resp = self.client.post(reverse('channels_list'), request_data)
        self.post_response = resp.json()
        self.assertEqual(resp.status_code, 201)  # Success
        # verify that the saved channel name is same one that was provided
        self.assertEqual(request_data['name'], self.post_response['name'])

    def test_get_channels(self):
        resp = self.client.get(reverse('channels_list'))
        self.assertEqual(resp.status_code, 200)  # success

    def test_post_and_delete_channel(self):
        # first post channel with fake channel name
        self.post_channel()
        # delete the recently posted channel
        resp = self.client.delete(reverse('channels_detail', kwargs={'pk': self.post_response['id']}))
        self.assertEqual(resp.status_code, 204)  # Success
