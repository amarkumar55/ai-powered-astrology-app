import bleach
import random
from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    
    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError('The Email field must be set')
        
        if not password:
            raise ValueError('The Password field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', False)
        extra_fields.setdefault('is_staff', False)
        return self.create_user(email, password, **extra_fields)
    
    def create_admin(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', False)
        return self.create_user(email, password, **extra_fields)
    
    def create_staff(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_admin', False)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(email, password, **extra_fields)
    
    
class CustomUser(AbstractBaseUser, PermissionsMixin):
  
    alphabetic = RegexValidator(
        regex=r'^[a-zA-Z]*$',
        message='Field must contain only alphabetic characters.'
    )

    # required fields      
    first_name = models.CharField(max_length=30, blank=False, null=False, validators=[alphabetic])
    last_name = models.CharField(max_length=30,  blank=False, null=False, validators=[alphabetic])
    email = models.EmailField(unique=True, blank=False, null=False, error_messages={
        'unquie':'A user with this email already exists.'
    })
    is_email_verified=models.BooleanField(default=False)
    username = models.CharField(max_length=30, unique=True, blank=False, null=False)
    birth_date = models.DateField(null=False, blank=False)
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")], blank=False, null=False)
    date_joined = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_user = models.BooleanField(default=True)
    is_accepted_terms = models.BooleanField(default=False, blank=False, null=False)

    #optional fields
    country_code = models.CharField(max_length=3, null=True, blank=True)
    cell = models.CharField(max_length=12, null=True, blank=True)
    is_cell_verified=models.BooleanField(default=False)
    social_id = models.CharField(max_length=255, blank=True, null=True)
    provider = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='uploads/profiles/', blank=True, null=True)
    birth_time = models.TimeField(blank=True, null=True)
    birth_place = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True)    
    language_preference = models.CharField(max_length=10, default="English")
    notification_preference = models.BooleanField(default=True)
    bio = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=20, null=True, blank=True)
    is_temporarily_disabled = models.BooleanField(default=False, blank=True, null=True)
    is_parament_disabled = models.BooleanField(default=False,blank=True, null=True )
    is_remember_me = models.BooleanField(default=False, blank=True, null=True)
    password_reset_token = models.TextField(null=True, blank=True)
    is_profile_block = models.BooleanField(default=False)
    zodiac_sign = models.CharField(max_length=50,blank=True, null=True)
    two_factor_enabled= models.BooleanField(default=False)
    time_format =  models.CharField(max_length=10, choices=[("AM", "AM"), ("PM", "PM")], blank=False, null=False)
    is_active=models.BooleanField(default=True)
    objects = CustomUserManager()
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'birth_date', 'last_login', 'date_joined', 'gender', 'username']


    def save(self, *args, **kwargs):
        self.first_name = bleach.clean(self.first_name, tags=[], strip=True)
        self.last_name = bleach.clean(self.last_name, tags=[], strip=True)
        self.email = bleach.clean(self.email, tags=[], strip=True)
        self.gender = bleach.clean(self.gender, tags=[], strip=True)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.email


User = get_user_model()

class UserActivity(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    activity_type = models.CharField(blank=False, null=False, max_length=100)
    data = models.JSONField(default=dict, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=False, null=False)
    action_date_time = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    browser = models.CharField(max_length=100, null=True, blank=True)
    browser_version = models.CharField(max_length=100, blank=True, null=True)
    os = models.CharField(max_length=100, blank=True, null=True)
    os_version = models.CharField(max_length=100, blank=True, null=True)
    device_brand = models.CharField(max_length=100, blank=True, null=True)
    device_model = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.CharField(max_length=100, blank=True, null=True)



class UserOtp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    otp_validator = RegexValidator(r'^\d{8}$', 'OTP must be exactly 8 digits.')

    email_otp = models.CharField(
        max_length=8,
        validators=[otp_validator],
        null=True,
        blank=True
    )
    
    mobile_otp = models.CharField(
        max_length=8,
        validators=[otp_validator],
        null=True,
        blank=True
    )

    def __str__(self):
        return f"OTP for {self.user}"
    


class TwoFactorPhoneDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phone_devices')
    phone_number = models.CharField(max_length=15)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    otp_generated_at = models.DateTimeField(blank=True, null=True)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.otp_generated_at = timezone.now()
        self.save()
        return self.otp

    def verify_otp(self, input_otp):
        # Optionally check expiry (e.g., 5 mins)
        if self.otp == input_otp:
            self.is_verified = True
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"
    


class EmailOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    otp_created_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)

    def is_expired(self):
        return timezone.now() > self.otp_created_at + timedelta(minutes=5)

    def verify_otp(self, otp_input):
        return self.otp == str(otp_input)