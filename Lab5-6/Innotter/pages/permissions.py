from django.db.models.functions.datetime import datetime
from rest_framework import permissions

from users.enums import Roles
from users.models import User
from pages.models import Tag
from pages.serializers import TagSerializer


class IsStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role in (Roles.Moder, Roles.Admin)


class AllowedMethod(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method not in ('DELETE', 'POST')


class ObjUserNotBlocked(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.owner.is_blocked:
            self.message = 'User was blocked'
            return False
        return True


class IsPageNotBlocked(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.unblock_date is not None:
            self.message = 'Page was blocked'
            return obj.unblock_date <= datetime.now(obj.unblock_date.tzinfo)
        return True


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner


class IsNotFollowerAndNotOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.owner or request.user in tuple(obj.followers.all()):
            self.message = 'Owner or already follower'
            return False
        return True


class NotInFollowRequests(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.is_private and request.user in tuple(obj.follow_requests.all()):
            self.message = 'Request has already been sent'
            return False
        return True


class IsFollowerAndNotOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.owner or request.user not in tuple(obj.followers.all()):
            self.message = 'Not followed'
            return False
        return True


class InFollowRequests(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.is_private and request.user not in tuple(obj.follow_requests.all()):
            self.message = 'Request was not sent'
            return False
        return True


class IsPrivatePage(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not obj.is_private:
            self.message = 'Page is not private'
            return False
        return True


class RequestIdInFollowRequests(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        request_user = User.objects.filter(pk=view.kwargs['request_pk']).first()
        if not request_user or request_user not in tuple(obj.follow_requests.all()):
            self.message = 'Not a follow request'
            return False
        return True


class IsValidTag(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        tag_name = request.data.get('name')
        tag = Tag.objects.filter(name=tag_name).exists()
        serializer = TagSerializer(data={'name': tag_name})
        if tag or serializer.is_valid(raise_exception=False):
            return True
        self.message = 'Invalid tag'
        return False
