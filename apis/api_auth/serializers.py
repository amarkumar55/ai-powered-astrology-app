from rest_framework import serializers
from django.contrib.auth import get_user_model
from authentication.utlity import generate_username, send_verification_email_api
from django.contrib.auth import authenticate
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from datetime import date
from django.utils import timezone
import re
from utlity.helper import store_activity
from django.core.mail import send_mail
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
  
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    is_accepted_terms = serializers.BooleanField(required=True)
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'birth_date', 'gender', 
            'email', 'password', 'confirm_password', 'is_accepted_terms'
        ]
        extra_kwargs = {
            'first_name': {'min_length': 2, 'max_length': 30},
            'last_name': {'min_length': 2, 'max_length': 30},
            'birth_date': {'required': True},
            'gender': {'required': True},
            'email': {'required': True},
        }

    def validate_email(self, value):
        db = self.context.get('request').db
        # Email format validation
        email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not email_regex.fullmatch(value):
            raise serializers.ValidationError("Please enter a valid email address.")
        
        # Check if email already exists
        if User.objects.using(db).filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        
        return value

    def validate_birth_date(self, value):
        # Ensure user is at least 13 years old
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 13:
            raise serializers.ValidationError("You must be at least 13 years old to register.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        
        if not attrs.get('is_accepted_terms'):
            raise serializers.ValidationError("You must accept the terms and conditions.")
        
        # Password strength validation
        password = attrs['password']
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', password):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise serializers.ValidationError("Password must contain at least one special character.")
        
        return attrs

    def create(self, validated_data):
       
        db = self.context.get('request').db
        
        validated_data.pop('confirm_password')
        validated_data.pop('is_accepted_terms')
        
        username = generate_username(validated_data.get('first_name'))
        
        user = User(
            email=validated_data.get('email'),
            username=username,
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            birth_date=validated_data.get('birth_date'),
            gender=validated_data.get('gender'),
            is_accepted_terms=True,
            is_active=False,
            is_email_verified=False,
            date_joined=timezone.now(),
            last_login=timezone.now(),
        )
        user.set_password(validated_data.get('password'))
        user.save(using=db)

      
        # Send verification email
        try:
            send_verification_email_api(self.context['request'], user)
        except Exception as e:
            pass
        
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    remember_me = serializers.BooleanField(default=False, required=False)

    def validate(self, attrs):
        
        db = self.context.get('request').db
        
        email = attrs.get('email')
        password = attrs.get('password')
        
        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")
        
        try:
            user = User.objects.using(db).get(email=email)
           
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        if not user.is_active:
            attrs['account_status'] = "inactive"
            attrs['user'] = user
            return attrs

        if user.is_temporarily_disabled:
            attrs['account_status'] = "temporary_disabled"
            attrs['user'] = user
            return attrs

        if user.is_permanent_disabled:
            attrs['account_status'] = "permanent_disabled"
            attrs['user'] = user
            return attrs

        # Authenticate user
        user = authenticate(self.context.get('request'), username=user.username, password=password)
        
        if not user:
            raise serializers.ValidationError({"detail": "Invalid credentials."})

        if not user.is_email_verified:
            attrs['account_status'] = "email_unverified"
            attrs['user'] = user
            return attrs

        attrs['account_status'] = "active"
        attrs['user'] = user
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
  
    def validate(self, attrs):
        db = self.context.get('request').db
        uidb64 =self.context.get('uuid')
        token = self.context.get('token')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.using(db).get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid verification link.")

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError("Invalid or expired verification link.")

        if user.is_email_verified:
            raise serializers.ValidationError("Email is already verified.")

        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.is_email_verified = True
        user.is_active = True
        user.save()
        return user


class ResendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        db = self.context.get('request').db
        try:
            user = User.objects.using(db).get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account associated with this email.")
        
        if user.is_email_verified:
            raise serializers.ValidationError("This account is already verified.")
        
        self.context['user'] = user
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        db = self.context.get('request').db
        try:
            user = User.objects.using(db).get(email=value)
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            return value
        
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        
        self.context['user'] = user
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):

    new_password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        db = self.context.get('request').db
        uidb64 = self.context.get('uid')
        token = self.context.get('token')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        # Validate token
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.using(db).get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid reset link.")

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError("Invalid or expired reset link.")

        # Validate password
        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        # Password strength validation
        if not re.search(r'[A-Z]', new_password):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', new_password):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', new_password):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            raise serializers.ValidationError("Password must contain at least one special character.")

        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def validate_old_password(self, value):
        if not self.user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New passwords do not match.")

        # Password strength validation
        new_password = attrs['new_password']
        if not re.search(r'[A-Z]', new_password):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', new_password):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', new_password):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            raise serializers.ValidationError("Password must contain at least one special character.")

        return attrs


class PasswordVerificationSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def validate(self, data):
        password = data.get('password')

        if not self.user:
            raise serializers.ValidationError("User context is required.")

        if not self.user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 
            'birth_date', 'gender', 'is_email_verified', 'date_joined',
            'profile_picture', 'bio', 'country_code', 'cell',
            'birth_place', 'latitude', 'longitude', 'timezone',
            'language_preference', 'notification_preference', 'time_format',
            'zodiac_sign', 'two_factor_enabled','is_active'
        ]
        read_only_fields = ['id', 'email', 'username', 'is_email_verified', 'date_joined','is_active']


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'profile_picture', 'bio', 'gender', 'username',
            'country_code', 'cell', 'birth_place', 'latitude', 'birth_date',
            'longitude', 'timezone', 'language_preference', 
            'notification_preference', 'time_format'
        ]

    def validate_first_name(self, value):
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters long.")
        return value.strip()

    def validate_last_name(self, value):
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters long.")
        return value.strip()


class TwoFactorSetupSerializer(serializers.Serializer):
    enable_2fa = serializers.BooleanField(required=True)

class LogoutSerializer(serializers.Serializer):
    pass  # No fields required for logout



class EmailOtpRequestSerializer(serializers.Serializer):
    old_email = serializers.EmailField(required=True)
    new_email = serializers.EmailField(required=True)


class EmailOtpVerifySerializer(serializers.Serializer):
    old_email = serializers.EmailField(required=True)
    new_email = serializers.EmailField(required=True)
    old_email_otp = serializers.CharField(required=True, min_length=6, max_length=6)
    new_email_otp = serializers.CharField(required=True, min_length=6, max_length=6)
 


class AccountDeactivateSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        request = self.context['request']
        db = request.db
        user = request.user

        if not user.check_password(attrs.get('password')):
            raise serializers.ValidationError({"password": "Incorrect password."})

        attrs['user'] = user
        attrs['db'] = db
        return attrs

    def save(self, **kwargs):
        db = self.validated_data['db']
        user = self.validated_data['user']

        user.is_active = False
        user.is_permanent_disabled = True
        user.updated_at = timezone.now()

        user.save(using=db, update_fields=["is_active", "is_permanent_disabled", "updated_at"])
    
        send_mail(
            'Account Deactivated – Scheduled for Deletion',
            f"""Hello {user.first_name},

        We noticed you have requested to delete your account, or your account has been inactive for 30 days.

        Your account is now deactivated and scheduled for permanent deletion in 30 days.
        During this time:
        - You may log in to reactivate your account and cancel deletion.
        - If you take no action, your account and all associated data will be permanently removed after the 30-day period.

        If you did not request this action, please log in immediately or contact our support team at support@yourdomain.com.

        Once deletion is complete, it cannot be reversed.

        Thank you,
        Your Company Name
        """,
            'noreply@yourdomain.com',
            [user.email],
            fail_silently=False,
        )

        store_activity(self.context['request'], {}, "Account deactivated", user)
        return user


class AccountRestoreSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        request = self.context.get('request')
        db = request.db  # ensure db routing
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.using(db).get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found."})

        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Incorrect password."})

        if user.is_active:
            raise serializers.ValidationError({"email": "Account is already active."})

        attrs['user'] = user
        attrs['db'] = db  # store db in attrs for save()
        return attrs

    def save(self, **kwargs):
        db = self.validated_data['db']
        user = self.validated_data['user']
        user.is_active = True
        user.is_permanent_disabled = False
        user.updated_at = timezone.now()
        user.save(using=db, update_fields=["is_active", "is_permanent_disabled", "updated_at"])
        send_mail(
            'Account Successfully Restored',
            f"""Hello {user.first_name},

        Good news! Your account has been successfully restored and is now active again.  
        All your data and settings have been retained.

    
        If you did not request this restoration, please contact our support team immediately at support@yourdomain.com.

        Thank you,
        Your Company Name
        """,
            'noreply@yourdomain.com',
            [user.email],
            fail_silently=False,
        )
        store_activity(self.context.get('request'), {}, "Account restored", user)
        return user
    


from authentication.models import Follow

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]

class FollowSerializer(serializers.ModelSerializer):
    follower = UserPublicSerializer(read_only=True)
    following = UserPublicSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ["id", "follower", "following", "created_at"]