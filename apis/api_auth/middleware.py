from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import PermissionDenied
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import JsonResponse
from django.contrib.auth import get_user_model
import logging
import time

User = get_user_model()
logger = logging.getLogger(__name__)


class APIRateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware for API endpoints
    """
    
    def process_request(self, request):
        # Only apply to API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Rate limiting rules
        rate_limits = {
            'register': {'rate': '5/m', 'window': 60},
            'login': {'rate': '10/m', 'window': 60},
            'password-reset': {'rate': '3/m', 'window': 60},
            'verify-email': {'rate': '10/m', 'window': 60},
        }
        
        # Check rate limits
        for endpoint, limit in rate_limits.items():
            if endpoint in request.path:
                cache_key = f"rate_limit:{client_ip}:{endpoint}"
                requests = cache.get(cache_key, 0)
                
                if requests >= int(limit['rate'].split('/')[0]):
                    return JsonResponse({
                        'error': 'Rate limit exceeded. Please try again later.'
                    }, status=429)
                
                cache.set(cache_key, requests + 1, limit['window'])
                break
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class APIRequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log API requests for monitoring and debugging
    """
    
    def process_request(self, request):
        # Only log API requests
        if request.path.startswith('/api/'):
            request.start_time = time.time()
        
        return None
    
    def process_response(self, request, response):
        # Only log API responses
        if hasattr(request, 'start_time') and request.path.startswith('/api/'):
            duration = time.time() - request.start_time
            
            # Log API request details
            log_data = {
                'path': request.path,
                'method': request.method,
                'status_code': response.status_code,
                'duration': round(duration, 3),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip': self.get_client_ip(request),
            }
            
            if hasattr(request, 'user') and request.user.is_authenticated:
                log_data['user_id'] = request.user.id
                log_data['user_email'] = request.user.email
            
            logger.info(f"API Request: {log_data}")
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class APISecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to API responses
    """
    
    def process_response(self, request, response):
        # Only apply to API responses
        if request.path.startswith('/api/'):
            # Add security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response 
    



class DatabaseSelectionMiddleware:
    """
    Middleware that extracts the DB name from headers and attaches it to request.db
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/'):
            db_name = request.headers.get('X-App-Source', 'default').lower()
            allowed_dbs = ['default', 'astro', 'smartnotes']
            if db_name not in allowed_dbs:
                db_name = 'default'
            request.db = db_name
            setattr(request, 'db', db_name)
        else:
            request.db = 'default'  # ✅ Fallback for non-API routes

        response = self.get_response(request)
        return response 
    

    

class CookieOrHeaderJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)

        raw_token = request.COOKIES.get("access")
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)

        # ✅ Enforce CSRF for cookie-based auth
        try:
            CsrfViewMiddleware().process_view(request, None, (), {})
        except PermissionDenied:
            from rest_framework.exceptions import AuthenticationFailed
            raise AuthenticationFailed("CSRF token missing or incorrect.")

        return (user, validated_token)