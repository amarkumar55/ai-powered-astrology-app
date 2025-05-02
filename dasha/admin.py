from django.contrib import admin
from .models import BirthDetails, PlanetaryPosition, MoonPosition, AntarDasha, DashaEffect

# Register your models here.
@admin.register(BirthDetails)
class BirthDetailsAdmin(admin.ModelAdmin):
    list_display = ('id','birth_date', 'birth_time', 'latitude','longitude','created_at')
    search_fields = ('birth_date','created_at')
    list_filter = ('birth_date','created_at')


@admin.register(PlanetaryPosition)
class PlanetaryPositionAdmin(admin.ModelAdmin):
    list_display=('birth_details','planet','speed','nakshatra','rashi','created_at','updated_at')
    search_fields=('birth_details','created_at')
    list_filter=('birth_details','created_at')


@admin.register(MoonPosition)
class MoonPositionAdmin(admin.ModelAdmin):
    list_display=('birth_details','moon_longitude','nakshatra','created_at')
    search_fields=('birth_details','created_at')
    list_filter=('birth_details','created_at')


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
