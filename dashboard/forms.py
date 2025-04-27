import re
import os
import uuid
import bleach
from PIL import Image
from django import forms
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.text import get_valid_filename
from pytz import all_timezones

get_all_timezone = all_timezones

RESERVED_USERNAMES = {"admin", "root", "support", "staff", "moderator"}

class ProfileForm(forms.Form):

    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    )

    TIME_PERIOD_CHOICES = [
        ('AM', 'AM'),
        ('PM', 'PM'),
    ]

    first_name = forms.CharField(min_length=2, strip=True, max_length=30, required=True)
    last_name = forms.CharField(min_length=2, strip=True, max_length=30, required=True)
    username = forms.CharField(min_length=2, strip=True, max_length=30, required=True)

    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    day = forms.IntegerField(min_value=1, max_value=31, required=True)
    month = forms.IntegerField(min_value=1, max_value=12, required=True)
    year = forms.IntegerField(min_value=1954, max_value=timezone.now().year, required=True)

    hours = forms.IntegerField(min_value=1, max_value=12, required=True)
    minutes = forms.IntegerField(min_value=0, max_value=59, required=True)
    seconds = forms.IntegerField(min_value=0, max_value=59, required=True)

    time_format = forms.ChoiceField(choices=TIME_PERIOD_CHOICES, required=True)
    profile = forms.FileField(required=False)
    place = forms.CharField(max_length=255, required=False)
    timezone = forms.CharField(max_length=255, required=False)
    notification_preference = forms.BooleanField(required=False)

    password = forms.CharField(
        min_length=8,
        error_messages={
            "min_length": "Please enter a valid account password.",
        }
    )

    def clean_profile(self):
        file = self.cleaned_data.get('profile')
        if not file:
            return None

        max_size = 1 * 1024 * 1024  # 1MB
        if file.size > max_size:
            raise ValidationError("Image file too large ( > 1MB ).")

        try:
            img = Image.open(file)
            img.verify()
        except Exception:
            raise ValidationError("Invalid image or corrupted file.")

        file_type = file.content_type
        if file_type not in ['image/jpeg', 'image/png']:
            raise ValidationError("Only JPEG and PNG images are allowed.")

        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png']:
            raise ValidationError("Invalid image file extension.")

        file.name = get_valid_filename(f"{uuid.uuid4()}{ext}")
        return file

    def clean(self):
        cleaned_data = super().clean()

        # Clean all string inputs: trim + bleach
        for field, value in cleaned_data.items():
            if isinstance(value, str):
                value = value.strip()
                cleaned_data[field] = bleach.clean(value, tags=[], strip=True)

        # Extract fields
        day = cleaned_data.get("day")
        month = cleaned_data.get("month")
        year = cleaned_data.get("year")

        hours = cleaned_data.get("hours")
        minutes = cleaned_data.get("minutes")
        seconds = cleaned_data.get("seconds")
        time_format = cleaned_data.get("time_format")
        timezone_val = cleaned_data.get("timezone")
        username = cleaned_data.get("username")
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        place = cleaned_data.get("place")
        password = cleaned_data.get("password")

        # Validate names
        if first_name and not re.fullmatch(r"^[A-Za-z]+$", first_name):
            self.add_error("first_name", "First name must contain only letters.")
        if last_name and not re.fullmatch(r"^[A-Za-z]+$", last_name):
            self.add_error("last_name", "Last name must contain only letters.")

        # Validate username
        if username:
            if username.lower() in RESERVED_USERNAMES:
                self.add_error("username", "This username is reserved.")
            elif not re.fullmatch(r"^[A-Za-z0-9]+$", username):
                self.add_error("username", "Username must contain only alphabets and numbers.")

        # Validate place
        if place and not re.fullmatch(r"^[a-zA-Z0-9\s,]+$", place):
            self.add_error("place", "Place can contain only alphabets, numbers, comma and spaces.")

        # Validate timezone
        if timezone_val and timezone_val not in get_all_timezone:
            self.add_error("timezone", "Please select a valid timezone.")

        # Validate password complexity
        if password and not re.fullmatch(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$', password):
            self.add_error("password", "Password must include uppercase, lowercase, number, and special character.")

        # Validate full datetime with AM/PM
        if all([day, month, year, hours, minutes is not None, seconds is not None, time_format]):
            try:
                if time_format == 'PM' and hours != 12:
                    hours += 12
                elif time_format == 'AM' and hours == 12:
                    hours = 0
                datetime(year, month, day, hours, minutes, seconds)
            except ValueError as e:
                self.add_error("day", f"Invalid date or time: {e}")

        return cleaned_data


class AccountDeleteForm(forms.Form):
    password = forms.CharField(
        min_length=8,
        strip=True,
        widget=forms.PasswordInput,
        error_messages={
            "min_length": "Please enter a valid account password.",
            "required": "Password is required.",
        }
    )

    DELETE_CHOICES = [
        ("temp", "Temporarily Deactivate"),
        ("permanent", "Permanently Delete"),
    ]

    delete_type = forms.ChoiceField(
        choices=DELETE_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        error_messages={
            "required": "Please select an option.",
        }
    )

    def clean_password(self):
        password = self.cleaned_data.get("password")

        if not password:
            raise forms.ValidationError("Password is required.")

        # Password strength validation
        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", password):
            raise forms.ValidationError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise forms.ValidationError("Password must contain at least one special character.")

        return password

    def clean(self):
        cleaned_data = super().clean()

        # Sanitize all string inputs
        for field, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field] = bleach.clean(value.strip(), tags=[], strip=True)

        delete_type = cleaned_data.get("delete_type")
        valid_delete_types = dict(self.DELETE_CHOICES).keys()

        if delete_type not in valid_delete_types:
            self.add_error("delete_type", "Please select a valid option.")

        return cleaned_data
    

class DisableTwoFactorForm(forms.Form):
   
    password = forms.CharField(
        min_length=8,
        strip=True,
        widget=forms.PasswordInput,
        error_messages={
            "min_length": "Please enter a valid account password.",
            "required": "Password is required.",
        }
    )


    def clean_password(self):
       
        password = self.cleaned_data.get("password")

        # Password strength validation
        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", password):
            raise forms.ValidationError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise forms.ValidationError("Password must contain at least one special character.")

        return password
    

    def clean(self):
        cleaned_data = super().clean()

        # Clean all string fields
        for field, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field] = bleach.clean(value, tags=[], strip=True)

        return cleaned_data
    

class Enable2FAForm(forms.Form):
    email = forms.EmailField(min_length=5, max_length=100, required=True)

    def clean_email(self):
        email = self.cleaned_data.get("email").strip()  # Remove any extra spaces
        
        # Regex to validate email address format
        email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not email_regex.fullmatch(email):
            raise forms.ValidationError("Please enter a valid email address.")

        # Optional: prevent disposable email services
        disposable_domains = ["mailinator.com", "10minutemail.com", "tempmail.com"]
        domain = email.split('@')[-1]
        if domain.lower() in disposable_domains:
            raise forms.ValidationError("Please use a real, non-disposable email address.")

        return email

    def clean(self):
        cleaned_data = super().clean()

        # Clean all string fields except email
        for field, value in cleaned_data.items():
            if isinstance(value, str) and field != 'email':
                cleaned_data[field] = bleach.clean(value, tags=[], strip=True)

        return cleaned_data

class VerifyOTPForm(forms.Form):
    email_otp = forms.CharField(min_length=6, max_length=6, required=True)

    def clean_email_otp(self):
        email_otp = self.cleaned_data.get("email_otp")

        # Ensure OTP is only digits
        if not re.fullmatch(r"^\d{6}$", email_otp):
            raise forms.ValidationError("OTP must contain exactly 6 digits.")

        return email_otp
    
    def clean(self):
        cleaned_data = super().clean()

        # Clean all string fields
        for field, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field] = bleach.clean(value, tags=[], strip=True)

        return cleaned_data



class VerifyEmailChangeForm(forms.Form):
    old_email = forms.EmailField(min_length=7, max_length=100, required=True)
    new_email = forms.EmailField(min_length=7, max_length=100, required=True)
    password = forms.CharField(
        min_length=8,
        strip=True,
        widget=forms.PasswordInput,
        error_messages={
            "min_length": "Please enter a valid account password.",
            "required": "Password is required.",
        }
    )


    def clean_old_email(self):
        old_email = self.cleaned_data.get("old_email")

        email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not email_regex.fullmatch(old_email):
            raise forms.ValidationError("Please enter a valid email address.")

        # Optional: prevent disposable email services
        disposable_domains = ["mailinator.com", "10minutemail.com", "tempmail.com"]
        domain = old_email.split('@')[-1]
        if domain.lower() in disposable_domains:
            raise forms.ValidationError("Please use a real, non-disposable email address.")

        return old_email
    
    def clean_new_email(self):
        new_email = self.cleaned_data.get("new_email")

        email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not email_regex.fullmatch(new_email):
            raise forms.ValidationError("Please enter a valid email address.")

        # Optional: prevent disposable email services
        disposable_domains = ["mailinator.com", "10minutemail.com", "tempmail.com"]
        domain = new_email.split('@')[-1]
        if domain.lower() in disposable_domains:
            raise forms.ValidationError("Please use a real, non-disposable email address.")

        return new_email
    

    def clean_password(self):
        password = self.cleaned_data.get("password")

        # Password strength validation
        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", password):
            raise forms.ValidationError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise forms.ValidationError("Password must contain at least one special character.")

        return password

    def clean(self):
        cleaned_data = super().clean()

        # Clean all string fields
        for field, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field] = bleach.clean(value, tags=[], strip=True)

        return cleaned_data            


class VerifyEmailChangeOTP(forms.Form):
    old_email = forms.EmailField(min_length=7, max_length=100, required=True)
    new_email = forms.EmailField(min_length=7, max_length=100, required=True)
    old_email_otp = forms.CharField(required=True)
    new_email_otp = forms.CharField(required=True)

    def clean_old_email(self):
        old_email = self.cleaned_data.get("old_email")

        email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not email_regex.fullmatch(old_email):
            raise forms.ValidationError("Please enter a valid email address.")

        # Optional: prevent disposable email services
        disposable_domains = ["mailinator.com", "10minutemail.com", "tempmail.com"]
        domain = old_email.split('@')[-1]
        if domain.lower() in disposable_domains:
            raise forms.ValidationError("Please use a real, non-disposable email address.")

        return old_email
    
    def clean_new_email(self):
        new_email = self.cleaned_data.get("new_email")

        email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not email_regex.fullmatch(new_email):
            raise forms.ValidationError("Please enter a valid email address.")

        # Optional: prevent disposable email services
        disposable_domains = ["mailinator.com", "10minutemail.com", "tempmail.com"]
        domain = new_email.split('@')[-1]
        if domain.lower() in disposable_domains:
            raise forms.ValidationError("Please use a real, non-disposable email address.")

        return new_email
    
    def clean_old_email_otp(self):
        old_email_otp = self.cleaned_data.get("old_email_otp")

        # Ensure OTP is only digits
        if not re.fullmatch(r"^\d{6}$", old_email_otp):
            raise forms.ValidationError("OTP must contain exactly 6 digits.")

        return old_email_otp
    
    def clean_new_email_otp(self):
        new_email_otp = self.cleaned_data.get("new_email_otp")

        # Ensure OTP is only digits
        if not re.fullmatch(r"^\d{6}$", new_email_otp):
            raise forms.ValidationError("OTP must contain exactly 6 digits.")

        return new_email_otp

    def clean(self):
        cleaned_data = super().clean()

        # Clean all string fields
        for field, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field] = bleach.clean(value, tags=[], strip=True)

        return cleaned_data