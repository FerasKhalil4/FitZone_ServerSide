from rest_framework import permissions

class ClientCheck(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == 5 and request.user.is_deleted == False)