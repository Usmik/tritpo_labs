import time

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from faker import Faker
import requests

from users.models import User
from pages.models import Page


class SendingMailTestCase(APITestCase):
    fixtures = ['views.yaml']

    def setUp(self):
        self.fake = Faker()
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.page1 = Page.objects.get(pk=1)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_send_mail(self):
        content = self.fake.name()
        self.page1.followers.set([self.user2])
        response = self.client.post(reverse('pages-new-post', args=[self.page1.pk]),
                                    data={'content': content}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get('content'), content)
        time.sleep(3)
        response = requests.get('http://localstack:4566/_localstack/ses')
        self.assertEqual(response.status_code, 200)
        self.assertIn(content, response.content.decode('utf-8'))
