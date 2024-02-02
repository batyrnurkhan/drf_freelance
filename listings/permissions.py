# listings/permissions.py
from rest_framework import permissions

class IsClientUser(permissions.BasePermission):
    """
    Custom permission to only allow clients to create a listing.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'client'

