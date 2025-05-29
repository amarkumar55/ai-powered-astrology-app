from django.contrib import admin
from .models import BirthDetails, PlanetaryPosition, MoonPosition, AntarDasha, DashaEffect

# Register your models here.
@admin.register(BirthDetails)
class BirthDetailsAdmin(admin.ModelAdmin):
    list_display = ('birth_date', 'birth_time', 'latitude', 'longitude', 'created_at')
    list_filter = ('birth_date', 'created_at')
    search_fields = ('birth_date', 'birth_time')
    readonly_fields = ('created_at',)
    ordering = ('-birth_date', '-birth_time')

@admin.register(PlanetaryPosition)
class PlanetaryPositionAdmin(admin.ModelAdmin):
    list_display = ('birth_details', 'planet', 'speed', 'nakshatra', 'rashi', 'created_at')
    list_filter = ('planet', 'nakshatra', 'rashi', 'created_at')
    search_fields = ('planet', 'nakshatra', 'rashi', 'birth_details__birth_date')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('birth_details', 'planet')

@admin.register(MoonPosition)
class MoonPositionAdmin(admin.ModelAdmin):
    list_display = ('birth_details', 'moon_longitude', 'nakshatra', 'created_at')
    list_filter = ('nakshatra', 'created_at')
    search_fields = ('nakshatra', 'birth_details__birth_date')
    readonly_fields = ('created_at',)
    ordering = ('birth_details', 'created_at')

@admin.register(AntarDasha)
class AdminAntarDasha(admin.ModelAdmin):
    list_display=('birth_details','nakshatra','major_dasha','antar_dasha_planet','start_date','end_date','created_at')
    search_fields=('birth_details','created_at')
    list_filter=('birth_details','created_at')

@admin.register(DashaEffect)
class DashaEffectModel(admin.ModelAdmin):
    list_display=('mahadasha_planet','antar_dasha_planet','start_date','end_date','mahadasha_effect','antardasha_effect','combined_effect','created_at')
    search_fields=('start_date','end_date','created_at','mahadasha_planet','antar_dasha_planet')
    list_filter=('start_date','end_date','created_at','mahadasha_planet','antar_dasha_planet')
