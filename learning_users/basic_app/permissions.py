from rest_framework import permissions


class IsOwnerUserOrIsAdminUser(permissions.BasePermission):
    """
    Permission class to check that a user can update his own resource only
    """

    def has_permissions(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or obj.user == request.user:
            return True
        return False
