from datetime import timezone
from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from faker import Faker

from pages.serializers import PageSerializer, PageRetrieveSerializer, PageUserSerializer, PostsSerializer
from posts.models import Post
from users.models import User
from pages.models import Page, Tag


class PageViewSetTestCase(APITestCase):
    fixtures = ['views.yaml']

    def setUp(self):
        self.fake = Faker()
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.page1 = Page.objects.get(pk=1)
        self.page2 = Page.objects.get(pk=2)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_list(self):
        response = self.client.get(reverse('pages-list'))
        expected_data = PageSerializer([self.page1, self.page2], many=True).data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_data)

    def test_retrieve(self):
        response = self.client.get(reverse('pages-detail', args=[self.page2.pk]))
        expected_data = PageRetrieveSerializer(self.page2).data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_data)

    def test_partial_update(self):
        new_puid = self.fake.name()
        self.client.patch(reverse('pages-detail', args=[self.page1.pk]), data={'puid': new_puid})
        result = Page.objects.get(pk=self.page1.pk)
        self.assertEqual(new_puid, result.puid)

    def test_follow(self):
        self.assertEqual(None, Page.objects.get(pk=self.page2.pk).followers.filter(pk=self.user1.pk).first())
        self.client.patch(reverse('pages-follow', args=[self.page2.pk]))
        result = Page.objects.get(pk=self.page2.pk).followers.filter(pk=self.user1.pk).first()
        self.assertEqual(result, self.user1)

    def test_unfollow(self):
        self.page2.followers.set([self.user1])
        self.assertEqual(self.user1, Page.objects.get(pk=self.page2.pk).followers.filter(pk=self.user1.pk).first())
        self.client.patch(reverse('pages-unfollow', args=[self.page2.pk]))
        result = Page.objects.get(pk=self.page2.pk).followers.filter(pk=self.user1.pk).first()
        self.assertEqual(None, result)

    def test_followers(self):
        response = self.client.get(reverse('pages-followers', args=[self.page2.pk]))
        self.assertEqual(response.data, [])
        self.page2.followers.set([self.user1, self.user2])
        response = self.client.get(reverse('pages-followers', args=[self.page2.pk]))
        self.assertEqual(response.data, PageUserSerializer([self.user1, self.user2], many=True).data)

    def test_posts(self):
        response = self.client.get(reverse('pages-posts', args=[self.page2.pk]))
        self.assertEqual(response.data, [])

        post1 = Post.objects.create(content=self.fake.name(), page=self.page2)
        post2 = Post.objects.create(content=self.fake.name(), page=self.page2)

        response = self.client.get(reverse('pages-posts', args=[self.page2.pk]))
        self.assertEqual(response.data, PostsSerializer([post1, post2], many=True).data)

    @patch('Innotter.aws.ses')
    def test_new_post(self, mocked_ses):
        content = self.fake.name()
        response = self.client.post(reverse('pages-new-post', args=[self.page1.pk]),
                                    data={'content': content}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get('content'), content)
        response = self.client.post(reverse('pages-new-post', args=[self.page1.pk]),
                                    data={'content': content, 'reply_to': -1}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_set_unblock_date(self):
        date = self.fake.iso8601(tzinfo=timezone.utc)
        self.assertEqual(None, Page.objects.get(pk=self.page2.pk).unblock_date)
        self.user1.role = 'admin'
        self.user1.save()
        response = self.client.patch(reverse('pages-set-unblock-date', args=[self.page2.pk]),
                                     data={'unblock_date': date}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(None, Page.objects.get(pk=self.page2.pk).unblock_date)

    def test_private(self):
        self.assertEqual(Page.objects.get(pk=self.page1.pk).is_private, False)
        self.client.patch(reverse('pages-private', args=[self.page1.pk]))
        self.assertEqual(Page.objects.get(pk=self.page1.pk).is_private, True)

    def test_public(self):
        self.page1.is_private = True
        self.page1.save()
        self.page1.follow_requests.add(self.user2)
        self.client.patch(reverse('pages-public', args=[self.page1.pk]))
        self.assertEqual(Page.objects.get(pk=self.page1.pk).is_private, False)
        self.assertEqual(Page.objects.get(pk=self.page1.pk).follow_requests.first(), None)

    def test_follow_requests(self):
        response = self.client.get(reverse('pages-follow-requests', args=[self.page1.pk]))
        self.assertEqual(response.data, [])
        self.page1.follow_requests.set([self.user1, self.user2])
        response = self.client.get(reverse('pages-follow-requests', args=[self.page1.pk]))
        self.assertEqual(response.data, PageUserSerializer([self.user1, self.user2], many=True).data)

    def test_accept_all_requests(self):
        self.page1.follow_requests.set([self.user1, self.user2])
        self.page1.is_private = True
        self.page1.save()
        response = self.client.patch(reverse('pages-accept-all-requests', args=[self.page1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Page.objects.get(pk=self.page1.pk).follow_requests.first(), None)
        self.assertEqual(Page.objects.get(pk=self.page1.pk).followers.count(), 2)

    def test_decline_all_requests(self):
        self.page1.follow_requests.set([self.user1, self.user2])
        self.page1.is_private = True
        self.page1.save()
        response = self.client.patch(reverse('pages-decline-all-requests', args=[self.page1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Page.objects.get(pk=self.page1.pk).follow_requests.first(), None)
        self.assertEqual(Page.objects.get(pk=self.page1.pk).followers.first(), None)

    def test_decline_request(self):
        self.page1.follow_requests.set([self.user1, self.user2])
        self.page1.is_private = True
        self.page1.save()
        response = self.client.patch(reverse('pages-decline-request', kwargs={'pk': self.page1.pk,
                                                                              'request_pk': self.user1.pk}))
        self.assertEqual(response.status_code, 202)
        self.assertTrue(Page.objects.get(pk=self.page1.pk).follow_requests.exists())
        self.assertFalse(Page.objects.get(pk=self.page1.pk).follow_requests.filter(pk=self.user1.pk).exists())
        self.assertFalse(Page.objects.get(pk=self.page1.pk).followers.exists())

    def test_accept_request(self):
        self.page1.follow_requests.set([self.user1, self.user2])
        self.page1.is_private = True
        self.page1.save()
        response = self.client.patch(reverse('pages-accept-request', kwargs={'pk': self.page1.pk,
                                                                             'request_pk': self.user1.pk}))
        self.assertEqual(response.status_code, 202)
        self.assertTrue(Page.objects.get(pk=self.page1.pk).follow_requests.exists())
        self.assertFalse(Page.objects.get(pk=self.page1.pk).follow_requests.filter(pk=self.user1.pk).exists())
        self.assertEqual(Page.objects.get(pk=self.page1.pk).followers.first(), self.user1)

    def test_add_tag(self):
        tag_name = self.fake.name()
        self.client.post(reverse('pages-tag', args=[self.page1.pk]),
                         data={'name': tag_name}, format='json')
        self.assertTrue(Page.objects.get(pk=self.page1.pk).tags.filter(name=tag_name).exists())

    def test_delete_tag(self):
        tag_name = self.fake.name()
        tag = Tag.objects.create(name=tag_name)
        self.page1.tags.add(tag)
        self.client.delete(reverse('pages-tag', args=[self.page1.pk]), data={'name': tag_name}, format='json')
        self.assertFalse(Page.objects.get(pk=self.page1.pk).tags.exists())
