from rest_framework.test import APITestCase, APIRequestFactory
from faker import Faker

from users.models import User
from pages.models import Page
from pages.permissions import IsStaff, AllowedMethod, ObjUserNotBlocked, IsPageNotBlocked, \
    IsOwner, IsFollowerAndNotOwner, IsNotFollowerAndNotOwner, NotInFollowRequests, InFollowRequests,\
    IsPrivatePage, RequestIdInFollowRequests, IsValidTag


class PermissionsTestCase(APITestCase):
    fixtures = ['permissions.yaml']

    def setUp(self):
        self.fake = Faker()
        self.admin_user = User.objects.get(pk=1)
        self.moder_user = User.objects.get(pk=2)
        self.blocked_user = User.objects.get(pk=3)
        self.page1 = Page.objects.get(pk=1)
        self.page2 = Page.objects.get(pk=2)
        self.page3 = Page.objects.get(pk=3)

    def test_is_staff(self):
        request = APIRequestFactory().get('/')
        request.user = self.admin_user
        permission = IsStaff().has_object_permission(request=request, obj=self.page1, view=None)
        self.assertTrue(permission)
        request.user = self.moder_user
        permission = IsStaff().has_object_permission(request=request, obj=self.page1, view=None)
        self.assertTrue(permission)

    def test_is_not_staff(self):
        request = APIRequestFactory().get('/')
        request.user = self.blocked_user
        permission = IsStaff().has_object_permission(request=request, obj=self.page1, view=None)
        self.assertFalse(permission)

    def test_not_allowed_method(self):
        request = APIRequestFactory().post('/')
        request.user = self.admin_user
        permission = AllowedMethod().has_permission(request=request, view=None)
        self.assertFalse(permission)
        request = APIRequestFactory().delete('/')
        request.user = self.admin_user
        permission = AllowedMethod().has_permission(request=request, view=None)
        self.assertFalse(permission)

    def test_allowed_method(self):
        request = APIRequestFactory().get('/')
        request.user = self.admin_user
        permission = AllowedMethod().has_permission(request=request, view=None)
        self.assertTrue(permission)

    def test_obj_user_blocked(self):
        request = APIRequestFactory().get('/')
        request.user = self.admin_user
        permission = ObjUserNotBlocked().has_object_permission(request=request, obj=self.page2, view=None)
        self.assertFalse(permission)

    def test_obj_user_not_blocked(self):
        request = APIRequestFactory().get('/')
        request.user = self.admin_user
        permission = ObjUserNotBlocked().has_object_permission(request=request, obj=self.page1, view=None)
        self.assertTrue(permission)

    def test_is_page_blocked(self):
        request = APIRequestFactory().get('/')
        request.user = self.admin_user
        permission = IsPageNotBlocked().has_object_permission(request=request, obj=self.page2, view=None)
        self.assertFalse(permission)

    def test_is_page_not_blocked(self):
        request = APIRequestFactory().get('/')
        request.user = self.admin_user
        permission = IsPageNotBlocked().has_object_permission(request=request, obj=self.page1, view=None)
        self.assertTrue(permission)

    def test_is_owner(self):
        request = APIRequestFactory().get('/')
        request.user = self.moder_user
        permission = IsOwner().has_object_permission(request=request, obj=self.page1, view=None)
        self.assertTrue(permission)
        permission = IsOwner().has_object_permission(request=request, obj=self.page2, view=None)
        self.assertFalse(permission)

    def test_is_follower_and_not_owner(self):
        request = APIRequestFactory().get('/')
        request.user = self.moder_user
        permission = IsFollowerAndNotOwner().has_object_permission(request=request, obj=self.page1, view=None)
        self.assertFalse(permission)
        permission = IsFollowerAndNotOwner().has_object_permission(request=request, obj=self.page2, view=None)
        self.assertFalse(permission)
        request.user = self.blocked_user
        permission = IsFollowerAndNotOwner().has_object_permission(request=request, obj=self.page1, view=None)
        self.assertTrue(permission)

    def test_is_not_follower_and_not_owner(self):
        request = APIRequestFactory().get('/')
        request.user = self.moder_user
        permission = IsNotFollowerAndNotOwner().has_object_permission(request=request, obj=self.page1, view=None)
        self.assertFalse(permission)
        permission = IsNotFollowerAndNotOwner().has_object_permission(request=request, obj=self.page2, view=None)
        self.assertTrue(permission)
        request.user = self.blocked_user
        permission = IsNotFollowerAndNotOwner().has_object_permission(request=request, obj=self.page1, view=None)
        self.assertFalse(permission)

    def test_not_in_follow_requests(self):
        request = APIRequestFactory().get('/')
        request.user = self.blocked_user
        permission = NotInFollowRequests().has_object_permission(request=request, obj=self.page1, view=None)
        self.assertTrue(permission)
        permission = NotInFollowRequests().has_object_permission(request=request, obj=self.page3, view=None)
        self.assertFalse(permission)

    def test_in_follow_requests(self):
        request = APIRequestFactory().get('/')
        request.user = self.blocked_user
        permission = InFollowRequests().has_object_permission(request=request, obj=self.page1, view=None)
        self.assertTrue(permission)
        permission = InFollowRequests().has_object_permission(request=request, obj=self.page3, view=None)
        self.assertTrue(permission)

    def test_is_private_page(self):
        request = APIRequestFactory().get('/')
        request.user = self.blocked_user
        permission = IsPrivatePage().has_object_permission(request=request, obj=self.page3, view=None)
        self.assertTrue(permission)
        permission = IsPrivatePage().has_object_permission(request=request, obj=self.page1, view=None)
        self.assertFalse(permission)

    def test_request_id_in_follow_requests(self):
        class View:
            def __init__(self, request_pk):
                self.kwargs = {'request_pk': request_pk}

        request = APIRequestFactory().get('/')
        request.user = self.admin_user
        permission = RequestIdInFollowRequests().has_object_permission(request=request, obj=self.page3, view=View(-1))
        self.assertFalse(permission)
        permission = RequestIdInFollowRequests().has_object_permission(request=request, obj=self.page3,
                                                                       view=View(self.admin_user.pk))
        self.assertFalse(permission)
        permission = RequestIdInFollowRequests().has_object_permission(request=request, obj=self.page3,
                                                                       view=View(self.blocked_user.pk))
        self.assertTrue(permission)

    def test_is_valid_tag(self):
        class Request:
            def __init__(self, tag):
                self.data = {'name': tag}
        permission = IsValidTag().has_object_permission(request=Request('tag'), obj=None, view=None)
        self.assertTrue(permission)
        permission = IsValidTag().has_object_permission(request=Request('1' * 40), obj=None, view=None)
        self.assertFalse(permission)
