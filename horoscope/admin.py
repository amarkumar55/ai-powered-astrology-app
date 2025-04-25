from .models import Horoscope
from django.contrib import admin

@admin.register(Horoscope)
class HoroscopeAdmin(admin.ModelAdmin):
    list_display = ('sign', 'date', 'type','prediction',)
    search_fields = ('date','sign')
    list_filter = ('date','sign')


