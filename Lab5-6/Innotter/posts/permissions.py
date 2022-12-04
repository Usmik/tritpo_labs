from rest_framework import permissions
from django.db.models.functions.datetime import datetime

from users.enums import Roles


class PostOwnerIsNotBlockedOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role not in (Roles.Moder, Roles.Admin) and obj.page.owner.is_blocked:
            self.message = 'Author of post are blocked'
            return False
        return True


class PostPageIsNotBlockedOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role not in (Roles.Moder, Roles.Admin) and obj.page.unblock_date is not None:
            self.message = 'Page was blocked'
            return obj.page.unblock_date <= datetime.now(obj.page.unblock_date.tzinfo)
        return True


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.page.owner


class PageIsNotPrivate(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.page.is_private \
                and request.user not in tuple(obj.page.followers.all()):
            self.message = 'Page is private'
            return False
        return True


class IsOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.page.owner \
               or request.user.role in (Roles.Moder, Roles.Admin)


class IsNotPostMethod(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.method == 'POST'
