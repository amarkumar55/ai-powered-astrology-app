import os
import random
import string
import traceback
from .models import EmailOTP
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.core.mail import send_mail
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

User = get_user_model()

# admin eror to deliver error reporting
admin_error_report_manager = os.environ.get('admin_error_report_manager')

def generate_username(first_name, rondom_digit=6):
    random_digits = ''.join(random.choices(string.digits, k=rondom_digit))
    username = f"{first_name.lower()}{random_digits}"
   
    while User.objects.filter(username=username).exists():
        random_digits = ''.join(random.choices(string.digits, k=rondom_digit))
        username = f"{first_name.lower()}{random_digits}"
   
    return username


def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))


def send_otp_message(email, message):
       
    try:
        validate_email(email)  # Check if the email is valid
    except ValidationError:
        raise ValueError("Invalid email address provided.")  # Raise 
    
    otp = generate_otp()
    EmailOTP.objects.update_or_create(
        email=email,
        defaults={'otp': otp, 'otp_created_at': timezone.now()}
    )
  
    send_mail(
        message,
        f'Your OTP is: {otp}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

def send_otp_message_api(email, message, request):
       
    try:
        validate_email(email)  # Check if the email is valid
    except ValidationError:
        raise ValueError("Invalid email address provided.")  # Raise 
    
    otp = generate_otp()
    EmailOTP.objects.using(request.db).update_or_create(
        email=email,
        defaults={'otp': otp, 'otp_created_at': timezone.now()}
    )
  
    send_mail(
        message,
        f'Your OTP is: {otp}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )



def send_verification_email(request, user):

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    accont_verification = request.build_absolute_uri(reverse('accont_verification', kwargs={'uidb64': uid, 'token': token}))

    html_message = render_to_string('emails/verify_email_confirm_mail.html', {
        'accont_verification': accont_verification,
        'user': user,
    })

  
    app_name = 'AstroLive'

    send_mail(
        subject= f'Verify Your Email –  {app_name}',
        message=f'Click here to verify: {accont_verification}',  # fallback for non-HTML readers
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message
    )

def send_verification_email_api(request, user):

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    accont_verification = request.build_absolute_uri(reverse('api_verify_email', kwargs={'uidb64': uid, 'token': token}))

    html_message = render_to_string('emails/verify_email_confirm_mail.html', {
        'accont_verification': accont_verification,
        'user': user,
    })

    if request.db == 'smartnotes':
        app_name = 'SmartNote'
    else:
        app_name = 'AstroLive'

    send_mail(
        subject=f'Verify Your Email – {app_name}',
        message=f'Click here to verify: {accont_verification}',  # fallback for non-HTML readers
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message
    )


def send_password_change_email(user):
     send_mail(
        subject="Your password has been changed",
        message="Hi {}, your password was successfully changed. If this wasn't you, please contact support.".format(user.username),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


def send_error_log(error):
    send_mail(
        subject='AstroLive: Error Report',
        message=f"{str(error)}\n{traceback.format_exc()}",  # fallback for non-HTML readers
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[admin_error_report_manager],
        html_message="",
    )

    
def get_cache_key(request):
    return get_client_ip(request)

def increment_failed_attempts(request):
    key = get_cache_key(request)
    attempts = cache.get(key, 0) + 1
    cache.set(key, attempts, timeout=300)
    return attempts

def reset_failed_attempts(request):
    cache.delete(get_cache_key(request))

def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def handle_captcha_logic(request, context: dict, threshold: int = 2):
    """
    Check if captcha should be shown based on failed attempts.
    Update context with captcha data if needed.
    Returns (show_captcha: bool, updated_context: dict)
    """
    cache_key = get_cache_key(request)
    failed_attempts = cache.get(cache_key, 0)
    show_captcha = failed_attempts >= threshold

    new_key = CaptchaStore.generate_key()
    image_url = captcha_image_url(new_key)
    context.update({
        'captcha_key': new_key,
        'captcha_image_url': image_url,
        'show_captcha': show_captcha,
    })

    return show_captcha, context