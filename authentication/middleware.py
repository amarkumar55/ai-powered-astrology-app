import re
from django.urls import reverse
from django.shortcuts import redirect


class BlockUnverifiedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        path = request.path

        if user.is_authenticated and not user.is_email_verified:
            # List of explicitly allowed paths for unverified users
            allowed_paths = [
                reverse('resend_verification'),
                reverse('auth.logout'),
                # Add other essentials here
            ]

            # Allow verification link paths like /verify/uid/token/
            is_verification_path = re.match(r'^/verify/[\w-]+/[\w-]+/?$', path)

            # Default: BLOCK everything unless explicitly allowed
            if path not in allowed_paths and not is_verification_path and not path.startswith('/admin'):
                return redirect('resend_verification')

        return self.get_response(request)