from rest_framework import permissions

from users.enums import Roles


class IsNotBlocked(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_blocked:
            self.message = 'You are blocked'
            return False
        return True


class AllowedMethod(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method not in ('POST', 'DELETE')


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == Roles.Admin


class ObjNotBlockedOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.is_blocked and request.user.role != Roles.Admin:
            self.message = 'User is blocked'
            return False
        return True


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj == request.user or request.user.role == Roles.Admin:
            return True
        else:
            return request.method in permissions.SAFE_METHODS


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsImage(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.FILES.get('file', False) \
                and request.FILES.get('file').name.split('.')[-1] in ('jpg', 'png', 'jpeg'):
            return True
        self.message = 'Should choose an image'
        return False
