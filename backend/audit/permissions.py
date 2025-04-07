from rest_framework.permissions import BasePermission
from .models import Access


class AuditPermission(BasePermission):
    """
    In the future, multiple Access objects here would mean that the user has
    multiple roles, and we will at some point probably have to enforce
    different permissions for different roles, so it's not clear how we'd
    handle that yet.
    For the moment, we just assume that if there are more than zero results
    for this query, we know the user has access to the SAC and return True.
    """

    def has_object_permission(self, request, view, obj):
        accesses = Access.objects.filter(audit=obj, user=request.user)
        if accesses:
            return True
        return False
