from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it,
    or admins can edit any object.
    """

    def has_object_permission(self, request, view, obj):
        # Admin always has permission
        if request.user and request.user.is_staff:
            return True

        # Allow GET, HEAD or OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        return obj.talaba == request.user if hasattr(obj, 'talaba') else obj == request.user
