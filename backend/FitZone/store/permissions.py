from rest_framework.permissions import BasePermission
from gym.models import Branch
class Has_store_permissions(BasePermission):
    def has_permission(self, request, view):
        branch_id= request.data.get('branch_id')
        branch = Branch.objects.get(id=branch_id)
        return branch.has_store
            