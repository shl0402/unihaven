from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings
from .models import Campus
from drf_spectacular.extensions import OpenApiAuthenticationExtension

class UniversityAPIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-University-API-Key')
        if not api_key:
            return None

        # Find university matching API key
        for uni, key in settings.UNIVERSITY_API_KEYS.items():
            if api_key == key:
                # Still set a single university for the request context
                # This represents the university making the request
                request.university = uni
                return (uni, None)  # Auth successful
        
        raise exceptions.AuthenticationFailed('Invalid API key')

class UniversityApiKeyAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'api.authentication.UniversityAPIKeyAuthentication'
    name = 'University-API-Key'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-University-API-Key',
            'description': 'University API key for authentication'
        }