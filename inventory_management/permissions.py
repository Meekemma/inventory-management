from rest_framework import permissions

class IsUser(permissions.BasePermission):
    """
    Custom permission to grant access to regular users only.
    """

    message = "You don't have permission to access this endpoint."

    def has_permission(self, request, view):
        # Allow access only to users in the 'User' group
        return request.user.groups.filter(name='User').exists()

    def has_object_permission(self, request, view, obj):
        # Allow read-only access for users in 'User' group
        return request.method in permissions.SAFE_METHODS