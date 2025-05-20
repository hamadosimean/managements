from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """permission for company owner"""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user == obj.user:
            return True
        return False


class IsUser(permissions.BasePermission):
    """permission for company owner"""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user == obj:
            return True
        return False
