from random import randint

from datetime import timedelta
from rest_framework.test import APITestCase, APIRequestFactory
from django.db.models.functions.datetime import datetime
import pytz
from faker import Faker

from users.models import User
from pages.models import Page
from posts.models import Post
from posts.permissions import PostOwnerIsNotBlockedOrStaff, PostPageIsNotBlockedOrStaff, \
    IsOwner, PageIsNotPrivate, IsNotPostMethod, IsOwnerOrStaff


class PermissionsTestCase(APITestCase):
    def setUp(self):
        self.fake = Faker()
        admin_name = self.fake.user_name() + str(randint(1, 500))
        self.admin_user = User.objects.create(username=admin_name, email=str(randint(1, 500)) + self.fake.email(),
                                              password=self.fake.password(), role='admin')
        moder_name = self.fake.user_name() + str(randint(1, 500))
        self.moder_user = User.objects.create(username=moder_name, email=str(randint(1, 500)) + self.fake.email(),
                                              password=self.fake.password(), role='moderator')
        blocked_user_name = self.fake.user_name() + str(randint(1, 500))
        self.blocked_user = User.objects.create(username=blocked_user_name, email=str(randint(1, 500)) + self.fake.email(),
                                                password=self.fake.password(), role='user', is_blocked=True)
        page1_name = self.fake.first_name_female() + str(randint(1, 500))
        page1_puid = self.fake.last_name_female() + str(randint(1, 500))
        self.page1 = Page.objects.create(name=page1_name, puid=page1_puid,
                                         owner=self.moder_user)
        page2_name = self.fake.first_name_female() + str(randint(1, 500))
        page2_puid = self.fake.last_name_female() + str(randint(1, 500))
        self.page2 = Page.objects.create(name=page2_name, puid=page2_puid,
                                         owner=self.blocked_user,
                                         unblock_date=datetime.now(pytz.timezone('Europe/Minsk'))+timedelta(days=1))
        self.post1 = Post.objects.create(content=self.fake.name(), page=self.page1)
        self.post2 = Post.objects.create(content=self.fake.name(), page=self.page2)

    def test_post_owner_is_not_blocked(self):
        request = APIRequestFactory().get('/')
        request.user = self.blocked_user
        permission = PostOwnerIsNotBlockedOrStaff().has_object_permission(request=request, obj=self.post1, view=None)
        self.assertTrue(permission)

    def test_post_owner_is_blocked_or_staff(self):
        request = APIRequestFactory().get('/')
        request.user = self.blocked_user
        permission = PostOwnerIsNotBlockedOrStaff().has_object_permission(request=request, obj=self.post2, view=None)
        self.assertFalse(permission)
        request.user = self.moder_user
        permission = PostOwnerIsNotBlockedOrStaff().has_object_permission(request=request, obj=self.post2, view=None)
        self.assertTrue(permission)

    def test_post_page_is_not_blocked(self):
        request = APIRequestFactory().get('/')
        request.user = self.blocked_user
        permission = PostPageIsNotBlockedOrStaff().has_object_permission(request=request, obj=self.post1, view=None)
        self.assertTrue(permission)

    def test_post_page_is_blocked_or_staff(self):
        request = APIRequestFactory().get('/')
        request.user = self.blocked_user
        permission = PostPageIsNotBlockedOrStaff().has_object_permission(request=request, obj=self.post2, view=None)
        self.assertFalse(permission)
        request.user = self.moder_user
        permission = PostPageIsNotBlockedOrStaff().has_object_permission(request=request, obj=self.post2, view=None)
        self.assertTrue(permission)

    def test_is_not_owner(self):
        request = APIRequestFactory().get('/')
        request.user = self.blocked_user
        permission = IsOwner().has_object_permission(request=request, obj=self.post1, view=None)
        self.assertFalse(permission)

    def test_is_owner(self):
        request = APIRequestFactory().get('/')
        request.user = self.moder_user
        permission = IsOwner().has_object_permission(request=request, obj=self.post1, view=None)
        self.assertTrue(permission)

    def test_page_Is_Private(self):
        page3 = Page.objects.create(name=self.fake.first_name_male(), puid=self.fake.last_name_male(),
                                    owner=self.moder_user, is_private=True)
        page3.followers.set([self.admin_user])
        post3 = Post.objects.create(content=self.fake.name(), page=page3)

        request = APIRequestFactory().get('/')
        request.user = self.moder_user
        permission = PageIsNotPrivate().has_object_permission(request=request, obj=post3, view=None)
        self.assertFalse(permission)
        request.user = self.admin_user
        permission = PageIsNotPrivate().has_object_permission(request=request, obj=post3, view=None)
        self.assertTrue(permission)

    def test_page_is_not_private(self):
        request = APIRequestFactory().get('/')
        request.user = self.moder_user
        permission = PageIsNotPrivate().has_object_permission(request=request, obj=self.post1, view=None)
        self.assertTrue(permission)

    def test_is_post_method(self):
        request = APIRequestFactory().post('/')
        request.user = self.admin_user
        permission = IsNotPostMethod().has_permission(request=request, view=None)
        self.assertFalse(permission)

    def test_is_not_post_method(self):
        request = APIRequestFactory().get('/')
        request.user = self.admin_user
        permission = IsNotPostMethod().has_permission(request=request, view=None)
        self.assertTrue(permission)

    def test_is_staff(self):
        request = APIRequestFactory().get('/')
        request.user = self.admin_user
        permission = IsOwnerOrStaff().has_object_permission(request=request, obj=self.post2, view=None)
        self.assertTrue(permission)
        request.user = self.moder_user
        permission = IsOwnerOrStaff().has_object_permission(request=request, obj=self.post1, view=None)
        self.assertTrue(permission)

    def test_is_not_staff(self):
        request = APIRequestFactory().get('/')
        request.user = self.blocked_user
        permission = IsOwnerOrStaff().has_object_permission(request=request, obj=self.post1, view=None)
        self.assertFalse(permission)

    def test_is_owner_or_staff(self):
        request = APIRequestFactory().get('/')
        request.user = self.blocked_user
        permission = IsOwnerOrStaff().has_object_permission(request=request, obj=self.post2, view=None)
        self.assertTrue(permission)
        permission = IsOwnerOrStaff().has_object_permission(request=request, obj=self.post1, view=None)
        self.assertFalse(permission)
        request.user = self.moder_user
        permission = IsOwnerOrStaff().has_object_permission(request=request, obj=self.post2, view=None)
        self.assertTrue(permission)
