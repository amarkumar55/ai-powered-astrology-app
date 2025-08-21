import secrets
from datetime import timedelta
from django.utils import timezone
from authentication.models import RefreshToken  # update with your model path


def get_db_from_request(request):
    app_source = request.headers.get("X-App-Source", "").lower()
    if app_source == "astrology":
        return "astro"
    elif app_source == "smartnotes":
        return "smartnotes"
    else:
        return "default"
    

def create_refresh_token(user):
    token = secrets.token_urlsafe(64)
    expires_at = timezone.now() + timedelta(days=30)  # valid for 30 days
    refresh_token = RefreshToken.objects.create(
        user=user,
        token=token,
        expires_at=expires_at
    )
    return refresh_token