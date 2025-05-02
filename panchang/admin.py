from .models import Panchang
from django.contrib import admin

# Register your models here.

@admin.register(Panchang)
class PanchangAdmin(admin.ModelAdmin):
    list_display = ('date', 'tithi', 'nakshatra','yoga', 'karana','vara','sunrise','sunset',
    'rahu_kaal','gulika_kaal','yamaganda','abhijit_muhurat',)
    search_fields = ('date',)
    list_filter = ('date',)


    