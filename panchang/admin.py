from django.contrib import admin
from .models import UserPanchang, Panchang

@admin.register(UserPanchang)
class UserPanchangAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'user', 'date_of_birth', 'time_of_birth', 'place', 'created_at')
    list_filter = ('date_of_birth', 'created_at')
    search_fields = ('first_name', 'last_name', 'user__email', 'user__username', 'place')
    readonly_fields = ('created_at',)
    ordering = ('-date_of_birth', '-time_of_birth')
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'first_name', 'last_name')
        }),
        ('Birth Details', {
            'fields': ('date_of_birth', 'time_of_birth', 'place', 'latitude', 'longitude')
        }),
        ('Astrological Details', {
            'fields': ('tithi', 'nakshatra', 'yoga', 'karana', 'vara')
        }),
        ('Timings', {
            'fields': ('sunrise', 'sunset', 'rahu_kaal', 'gulika_kaal', 'yamaganda', 'abhijit_muhurat')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )

@admin.register(Panchang)
class PanchangAdmin(admin.ModelAdmin):
    list_display = ('date', 'tithi', 'vara', 'nakshatra', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('tithi', 'vara', 'nakshatra', 'yoga', 'karana')
    readonly_fields = ('created_at',)
    ordering = ('-date',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('date', 'tithi', 'vara', 'nakshatra', 'yoga', 'karana')
        }),
        ('Timings', {
            'fields': ('sunrise', 'sunset', 'rahu_kaal', 'gulika_kaal', 'yamaganda', 'abhijit_muhurat')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )


    