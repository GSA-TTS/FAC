from rest_framework.permissions import BasePermission

class SingleAuditChecklistPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        print('im here!')
        return False
