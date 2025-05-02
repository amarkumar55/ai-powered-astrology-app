from django.contrib import admin
from .models import Location, KundliReport


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('place', 'latitude', 'longitude',)
    search_fields = ('place',)
    list_filter = ('place',)



@admin.register(KundliReport)
class KundiReport(admin.ModelAdmin):
    list_display = ('id','birth_details', 'ascendant', 'asc_deg','asc_sign','birth_sign','created_at')
    search_fields = ('birth_details','created_at',)
    list_filter = ('id','birth_details','created_at',)
