from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserActivity, UserOtp, Wallet
# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'is_admin', 'is_user', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'birth_date', 'gender', 'profile_picture')}),
        ('Contact info', {'fields': ('country_code', 'cell', 'birth_place', 'latitude', 'longitude', 'timezone')}),
        ('Preferences', {'fields': ('language_preference', 'notification_preference', 'time_format')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin', 'is_user', 'groups', 'user_permissions')}),
        ('Security', {'fields': ('is_email_verified', 'is_cell_verified', 'two_factor_enabled', 'is_profile_block')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name', 'birth_date', 'gender'),
        }),
    )


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'ip_address', 'action_date_time', 'device_type')
    list_filter = ('activity_type', 'action_date_time', 'device_type')
    search_fields = ('user__email', 'user__username', 'activity_type', 'ip_address')
    readonly_fields = ('action_date_time',)
    ordering = ('-action_date_time',)


@admin.register(UserOtp)
class AdminUserOtp(admin.ModelAdmin):
    list_display = ('user','email_otp','mobile_otp',)
    search_fields = ('user',)
    list_filter = ('user',)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
