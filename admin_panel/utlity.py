import os
from django.conf import settings
from PIL import Image

APP_BASE_URL = os.environ.get('APP_BASE_URL')


def handle_file_upload(file, post):
    image = Image.open(file)
    ext = image.format.lower()  # Get actual image format like 'jpeg', 'png'
    filename = f"{post.id}_image.{ext}"
    upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads", "posts")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    # Save image properly using Pillow
    image.save(file_path, format=image.format)

    return f"{APP_BASE_URL}/media/uploads/posts/{filename}"
