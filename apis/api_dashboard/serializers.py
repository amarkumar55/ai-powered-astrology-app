from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'birth_date', 'gender', 'profile_picture',
            'birth_time', 'birth_place', 'latitude', 'longitude', 'timezone', 'language_preference',
            'notification_preference', 'bio', 'zodiac_sign', 'two_factor_enabled', 'is_email_verified',
            'date_joined', 'last_login', 'time_format', 'is_active'
        ] 