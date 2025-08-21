from django.contrib import admin
from .models import Horoscope

@admin.register(Horoscope)
class HoroscopeAdmin(admin.ModelAdmin):
    list_display = ('sign', 'date', 'type',)
    list_filter = ('sign', 'type', 'date')
    search_fields = ('sign', 'prediction')
  
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


