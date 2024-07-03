from rest_framework.permissions import BasePermission 


class admin_permissions(BasePermission):
    def has_permission(self, request, view):
        print('----------')
        if request.user.is_authenticated and request.user.role == 1:
            return True
        print(f'Permission denied for user: {request.user}') 
        return False
    
class admin_manager_permissions(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET" and bool (request.user.is_authenticated and request.user.role == 1 or request.user.role == 2):
            return True
        elif request.method == "PUT" and bool (request.user.is_authenticated and request.user.role == 2):
            return True
        elif request.method == "DELETE" and bool (request.user.is_authenticated and request.user.role == 1):
            return True
        else:
            return False
        
class Manager_permissions(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == 2)
    