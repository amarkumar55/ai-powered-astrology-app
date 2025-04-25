import os
from django.conf import settings


def handle_profile_upload(file, username):
    # Get the original extension
    _, ext = os.path.splitext(file.name)
    filename = f"{username}_profile{ext}"

    upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads", "profiles")
    os.makedirs(upload_dir, exist_ok=True)  # Create the directory if it doesn't exist
    file_path = os.path.join(upload_dir, filename)

    # Write file in chunks
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    # Return relative path for saving in model
    return f"uploads/profiles/{filename}"




def get_cache_key(email, action='otp'):
    return f"{action}_cooldown_{email}"

def get_attempt_key(email):
    return f"otp_attempt_{email}"
