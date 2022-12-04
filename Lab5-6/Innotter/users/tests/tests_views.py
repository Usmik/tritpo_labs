from random import randint

from django.urls import reverse
from faker import Faker
import rest_framework.status
from rest_framework.test import APITestCase, APIClient

from users.serializers import UserSerializer, PagesSerializer, UserPostSerializer
from users.models import User
from pages.models import Page
from posts.models import Post


class UserViewSetTestCase(APITestCase):
    def setUp(self):
        self.fake = Faker()
        user1_name = self.fake.user_name() + str(randint(1, 500))
        self.user1 = User.objects.create(username=user1_name, email=str(randint(1, 500)) + self.fake.email(),
                                         password=self.fake.password(), role='admin')
        user2_name = self.fake.user_name() + str(randint(1, 500))
        self.user2 = User.objects.create(username=user2_name, email=str(randint(1, 500)) + self.fake.email(),
                                         password=self.fake.password(), role='user')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_list(self):
        response = self.client.get(reverse('users-list'))
        expected_data = UserSerializer([self.user1, self.user2], many=True).data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_data)

    def test_retrieve(self):
        response = self.client.get(reverse('users-detail', args=[self.user2.pk]))
        expected_data = UserSerializer(self.user2).data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_data)

    def test_partial_update(self):
        new_title = self.fake.name()
        self.assertEqual(self.user1.title, "")
        self.client.patch(reverse('users-detail', args=[self.user1.pk]), data={'title': new_title})
        result = User.objects.get(pk=self.user1.pk)
        self.assertEqual(new_title, result.title)

    def test_register(self):
        data = {'user': {'username': self.fake.last_name_male(),
                         'email': self.fake.email(),
                         'password': self.fake.password()}}
        response = APIClient().post(reverse('users-register'), data=data, format='json')
        self.assertEqual(response.status_code, rest_framework.status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username=data['user']['username']).exists())

    def test_wrong_register(self):
        response = APIClient().post(reverse('users-register'), data={"user": "username"}, format='json')
        self.assertEqual(response.status_code, rest_framework.status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        self.username = self.fake.last_name_female()
        self.password = self.fake.password()
        self.email = self.fake.email()
        self.user = User.objects.create_user(username=self.username, password=self.password,
                                             email=self.email)
        response = APIClient().post(reverse('users-login'), data={'user': {'username': self.username,
                                                                  'password': self.password}}, format='json')
        self.assertEqual(response.status_code, rest_framework.status.HTTP_200_OK)
        self.assertEqual(response.data.get('username'), self.username)
        self.assertFalse(response.data.get('token') is None)

    def test_wrong_login(self):
        self.username = self.fake.last_name_female()
        self.password = self.fake.password()
        self.email = self.fake.email()
        self.user = User.objects.create_user(username=self.username, password=self.password,
                                             email=self.email)
        response = APIClient().post(reverse('users-login'), data={"user": {"username": self.username,
                                                                           "password": ""}}, format='json')
        self.assertEqual(response.status_code, rest_framework.status.HTTP_400_BAD_REQUEST)

    def test_retrieve_profile(self):
        response = self.client.get(reverse('users-profile'))
        self.assertEqual(response.status_code, rest_framework.status.HTTP_200_OK)
        self.assertEqual(response.data.get('username'), self.user1.username)
        self.assertEqual(response.data.get('email'), self.user1.email)

    def test_update_profile(self):
        new_username = self.fake.first_name_male()
        data = {'user': {'username': new_username}}
        response = self.client.put(reverse('users-profile'), data=data, format='json')
        self.assertEqual(response.status_code, rest_framework.status.HTTP_200_OK)
        self.assertEqual(response.data.get('username'), new_username)
        self.assertEqual(response.data.get('email'), self.user1.email)

    def test_block(self):
        self.assertFalse(User.objects.get(pk=self.user2.pk).is_blocked)
        self.client.patch(reverse('users-block', args=[self.user2.pk]))
        self.assertEqual(User.objects.get(pk=self.user2.pk).is_blocked, True)

    def test_unblock(self):
        self.user2.is_blocked = True
        self.user2.save()
        self.assertTrue(User.objects.get(pk=self.user2.pk).is_blocked)
        self.client.patch(reverse('users-unblock', args=[self.user2.pk]))
        self.assertFalse(User.objects.get(pk=self.user2.pk).is_blocked)

    def test_pages(self):
        page1_name = self.fake.first_name_male() + str(randint(1, 500))
        page1_puid = self.fake.last_name_male() + str(randint(1, 500))
        self.page1 = Page.objects.create(name=page1_name, puid=page1_puid, owner=self.user1)
        page2_name = self.fake.first_name_male() + str(randint(1, 500))
        page2_puid = self.fake.last_name_male() + str(randint(1, 500))
        self.page2 = Page.objects.create(name=page2_name, puid=page2_puid, owner=self.user1)

        response = self.client.get(reverse('users-pages', args=[self.user1.pk]))
        expected_data = PagesSerializer([self.page1, self.page2], many=True).data
        self.assertEqual(response.data, expected_data)

    def test_liked(self):
        page1_name = self.fake.first_name_male() + str(randint(1, 500))
        page1_puid = self.fake.last_name_male() + str(randint(1, 500))
        self.page1 = Page.objects.create(name=page1_name, puid=page1_puid, owner=self.user1)
        self.post1 = Post.objects.create(content=self.fake.name(), page=self.page1)
        self.post1.likes.set([self.user1])
        self.post2 = Post.objects.create(content=self.fake.name(), page=self.page1)
        self.post2.likes.set([self.user1])
        response = self.client.get(reverse('users-liked', args=[self.user1.pk]))
        expected_data = UserPostSerializer([self.post1, self.post2], many=True).data
        self.assertEqual(response.data, expected_data)

    def test_new_page(self):
        page_name = self.fake.last_name_male() + str(randint(1, 500))
        page_puid = self.fake.first_name_male() + str(randint(1, 500))
        self.assertFalse(Page.objects.filter(name=page_name).exists())
        response = self.client.post(reverse('users-new-page', args=[self.user1.pk]),
                                    data={'name': page_name, 'puid': page_puid}, format='json')
        self.assertTrue(response)
        self.assertNotEqual(Page.objects.filter(name=page_name).first(), None)
