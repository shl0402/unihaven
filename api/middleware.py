from django.http import HttpResponse
from django.conf import settings

class UniversityAuthenticationMiddleware:
    """
    Middleware to authenticate university systems using API keys.
    
    Required headers:
    - X-University-API-Key: API key for university authentication
    
    Example keys for testing:
    - HKU: hku-secret-key-2025
    - HKUST: hkust-secret-key-2025
    - CUHK: cuhk-secret-key-2025
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip auth for non-API requests and documentation endpoints
        if (not request.path.startswith('/api/') or
            request.path.startswith('/api/docs/') or
            request.path.startswith('/api/redoc/') or
            request.path.startswith('/api/schema/')):
            return self.get_response(request)

        # Check API key
        api_key = request.headers.get('X-University-API-Key')
        if not api_key:
            return HttpResponse('Missing API key', status=401)

        # Validate API key
        valid_keys = settings.UNIVERSITY_API_KEYS.values()
        if api_key not in valid_keys:
            return HttpResponse('Invalid API key', status=401)

        return self.get_response(request)