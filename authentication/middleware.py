from django.urls import  reverse
from django.shortcuts import redirect
import re

class BlockUnverifiedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        path = request.path

        # If user is authenticated but NOT verified
        if user.is_authenticated and not user.is_email_verified:

            # Reverse the named URLs
            resend_verification_url = reverse('resend_verification')
            logout_url = reverse('auth.logout')
            


            # Also allow verification URLs (like /verify/uid/token/)
            is_verification_path = re.match(r'^/authentication/verify/[\w-]+/[\w-]+/?$', path)

            # If NOT in allowed paths AND not admin AND not verification link
            if (not path.startswith(resend_verification_url) and
                not path.startswith(logout_url) and
                not is_verification_path and
                not path.startswith('/admin')):

                return redirect('resend_verification')

        return self.get_response(request)
    

from django.http import HttpResponseBadRequest
import logging

logger = logging.getLogger(__name__)

class DebugHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.META.get('HTTP_HOST', '')
        if ',' in host:
            logger.warning(f"Invalid HTTP_HOST header received: {host}")
            return HttpResponseBadRequest(f"Bad Host header: {host}")
        return self.get_response(request)