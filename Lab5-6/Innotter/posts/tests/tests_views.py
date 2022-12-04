from random import randint

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.db.models.functions.datetime import datetime
from datetime import timedelta
import pytz
from faker import Faker

from posts.serializers import PostSerializer, PostRetrieveSerializer, PostUserSerializer
from users.models import User
from pages.models import Page
from posts.models import Post


class PostViewSetTestCase(APITestCase):
    def setUp(self):
        self.fake = Faker()
        self.user1 = User.objects.create(username=self.fake.user_name() + str(randint(1, 500)),
                                         email=str(randint(1, 500)) + self.fake.email(),
                                         password=self.fake.password(), role='user')
        self.user2 = User.objects.create(username=self.fake.user_name() + str(randint(1, 500)),
                                         email=str(randint(1, 500)) + self.fake.email(),
                                         password=self.fake.password(), role='user')
        self.page1 = Page.objects.create(name=self.fake.first_name_male() + str(randint(1, 500)),
                                         puid=str(randint(1, 500)) + self.fake.last_name_male(),
                                         owner=self.user1)
        self.page2 = Page.objects.create(name=self.fake.first_name_male() + str(randint(1, 500)),
                                         puid=str(randint(1, 500)) + self.fake.last_name_male(),
                                         owner=self.user2,
                                         unblock_date=datetime.now(pytz.timezone('Europe/Minsk'))+timedelta(days=1))
        self.post1 = Post.objects.create(content=self.fake.name(), page=self.page1)
        self.post2 = Post.objects.create(content=self.fake.name(), page=self.page2)
        self.client = APIClient()
        self.client.force_authenticate(self.user1)

    def test_list(self):
        response = self.client.get(reverse('posts-list'))
        expected_data = PostSerializer([self.post1, self.post2], many=True).data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_data)

    def test_retrieve(self):
        response = self.client.get(reverse('posts-detail', args=[self.post1.pk]))
        expected_data = PostRetrieveSerializer(self.post1).data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_data)

    def test_partial_update(self):
        new_content = self.fake.name()
        self.client.patch(reverse('posts-detail', args=[self.post1.pk]), data={'content': new_content})
        result = Post.objects.get(pk=self.post1.pk)
        self.assertEqual(new_content, result.content)

    def test_destroy(self):
        self.assertTrue(Post.objects.filter(pk=self.post1.pk).exists())
        self.client.delete(reverse('posts-detail', args=[self.post1.pk]))
        self.assertFalse(Post.objects.filter(pk=self.post1.pk).exists())

    def test_likes(self):
        self.post1.likes.set([self.user1, self.user2])
        response = self.client.get(reverse('posts-likes', args=[self.post1.pk]))
        self.assertEqual(PostUserSerializer([self.user1, self.user2], many=True).data, response.data)

    def test_like(self):
        self.client.patch(reverse('posts-like', args=[self.post1.pk]))
        self.assertTrue(Post.objects.get(pk=self.post1.pk).likes.filter(pk=self.user1.pk).exists())

    def test_unlike(self):
        self.post1.likes.set([self.user1])
        self.assertTrue(Post.objects.get(pk=self.post1.pk).likes.filter(pk=self.user1.pk).exists())
        self.client.patch(reverse('posts-unlike', args=[self.post1.pk]))
        self.assertFalse(Post.objects.get(pk=self.post1.pk).likes.filter(pk=self.user1.pk).exists())
