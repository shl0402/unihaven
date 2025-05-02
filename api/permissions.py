from rest_framework import permissions
from django.conf import settings

class IsUniversitySystemAuthenticated(permissions.BasePermission):
    """
    Custom permission to check if request is from an authenticated university system.
    """
    def has_permission(self, request, view):
        # Check if API key is present and valid
        api_key = request.headers.get('X-University-API-Key')
        if not api_key:
            return False
        # Use settings.UNIVERSITY_API_KEYS directly instead of view method
        return api_key in settings.UNIVERSITY_API_KEYS.values()

class IsFromSameUniversity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'university'):
            return obj.university == request.university
        elif hasattr(obj, 'accommodation'):
            return obj.accommodation.university == request.university
        return False