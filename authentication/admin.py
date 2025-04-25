from django.contrib import admin
from .models import CustomUser, UserActivity, UserOtp
# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'email', 'is_email_verified', 
                    'cell', 'is_cell_verified','birth_date','gender','date_joined', 'is_superuser','is_admin','is_staff','is_user','is_accepted_terms')
    search_fields = ('email', 'username','cell')
    list_filter = ('username', 'email')


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'data','ip_address', 'action_date_time','browser','browser_version','os',
    'os_version','device_brand','device_model')
    search_fields = ('user', 'activity_type','ip_address','action_date_time')
    list_filter = ('action_date_time', 'activity_type')



@admin.register(UserOtp)
class AdminUserOtp(admin.ModelAdmin):
    list_display = ('user','email_otp','mobile_otp',)
    search_fields = ('user',)
    list_filter = ('user',)
