from random import randint

from faker import Faker
from rest_framework.test import APITestCase, APIRequestFactory

from users.models import User
from users.permissions import IsAdmin, IsNotBlocked, IsOwnerOrAdminOrReadOnly, ObjNotBlockedOrAdmin,\
    AllowedMethod, IsOwner


class PermissionsTestCase(APITestCase):
    def setUp(self):
        fake = Faker()
        admin_name = fake.user_name() + str(randint(1, 500))
        self.admin_user = User.objects.create(username=admin_name, email=str(randint(1, 500)) + fake.email(),
                                              password=fake.password(), role='admin')
        user_name = fake.user_name() + str(randint(1, 500))
        self.user = User.objects.create(username=user_name, email=str(randint(1, 500)) + fake.email(),
                                        password=fake.password(), role='user')
        blocked_user_name = fake.user_name() + str(randint(1, 500))
        self.blocked_user = User.objects.create(username=blocked_user_name, email=str(randint(1, 500)) + fake.email(),
                                                password=fake.password(), role='user', is_blocked=True)

    def test_is_not_blocked(self):
        request = APIRequestFactory().get('/')
        request.user = self.admin_user
        permission = IsNotBlocked().has_permission(request=request, view=None)
        self.assertTrue(permission)

    def test_is_blocked(self):
        request = APIRequestFactory().get('/')
        request.user = self.blocked_user
        permission = IsNotBlocked().has_permission(request=request, view=None)
        self.assertFalse(permission)

    def test_not_allowed_method(self):
        request = APIRequestFactory().post('/')
        permission = AllowedMethod().has_permission(request=request, view=None)
        self.assertFalse(permission)
        request = APIRequestFactory().delete('/')
        permission = AllowedMethod().has_permission(request=request, view=None)
        self.assertFalse(permission)

    def test_allowed_method(self):
        request = APIRequestFactory().get('/')
        permission = AllowedMethod().has_permission(request=request, view=None)
        self.assertTrue(permission)

    def test_is_owner_or_admin_or_read_only(self):
        post_request = APIRequestFactory().post('/')
        get_request = APIRequestFactory().get('/')
        post_request.user = self.user
        get_request.user = self.user
        false_permission = IsOwnerOrAdminOrReadOnly().has_object_permission(request=post_request,
                                                                            obj=self.blocked_user, view=None)
        true_permission = IsOwnerOrAdminOrReadOnly().has_object_permission(request=get_request,
                                                                           obj=self.blocked_user, view=None)
        self.assertFalse(false_permission)
        self.assertTrue(true_permission)
        permission = IsOwnerOrAdminOrReadOnly().has_object_permission(request=post_request, obj=self.user, view=None)
        self.assertTrue(permission)
        post_request.user = self.admin_user
        permission = IsOwnerOrAdminOrReadOnly().has_object_permission(request=post_request,
                                                                      obj=self.blocked_user, view=None)
        self.assertTrue(permission)

    def test_obj_blocked_or_admin(self):
        request = APIRequestFactory().get('/')
        request.user = self.user
        permission = ObjNotBlockedOrAdmin().has_object_permission(request=request, obj=self.blocked_user, view=None)
        self.assertFalse(permission)

    def test_obj_not_blocked_or_admin(self):
        request = APIRequestFactory().get('/')
        request.user = self.user
        permission = ObjNotBlockedOrAdmin().has_object_permission(request=request, obj=self.user, view=None)
        self.assertTrue(permission)

    def test_is_admin(self):
        request = APIRequestFactory().get('/')
        request.user = self.admin_user
        permission = IsAdmin().has_permission(request=request, view=None)
        self.assertTrue(permission)
        request.user = self.user
        permission = IsAdmin().has_permission(request=request, view=None)
        self.assertFalse(permission)

    def test_is_owner(self):
        request = APIRequestFactory().get('/')
        request.user = self.admin_user
        permission = IsOwner().has_object_permission(request=request, obj=self.admin_user, view=None)
        self.assertTrue(permission)
        permission = IsOwner().has_object_permission(request=request, obj=self.user, view=None)
        self.assertFalse(permission)
