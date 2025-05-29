from django.contrib import admin
from .models import Horoscope

@admin.register(Horoscope)
class HoroscopeAdmin(admin.ModelAdmin):
    list_display = ('sign', 'date', 'type', 'created_at')
    list_filter = ('sign', 'type', 'date')
    search_fields = ('sign', 'prediction')
    readonly_fields = ('created_at',)
    ordering = ('-date', 'sign')
    fieldsets = (
        ('Basic Information', {
            'fields': ('sign', 'date', 'type')
        }),
        ('Prediction', {
            'fields': ('prediction',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )


