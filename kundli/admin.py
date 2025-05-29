from django.contrib import admin
from .models import Location, KundliReport


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('place', 'latitude', 'longitude')
    search_fields = ('place',)
    list_filter = ('place',)


@admin.register(KundliReport)
class KundliReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'place', 'birth_details', 'ascendant', 'birth_sign', 'created_at')
    list_filter = ('birth_sign', 'created_at')
    search_fields = ('user__email', 'user__username', 'name', 'place', 'ascendant', 'birth_sign')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'place', 'birth_details')
        }),
        ('Astrological Details', {
            'fields': ('ascendant', 'asc_deg', 'asc_sign', 'birth_sign', 'nakshatra', 'ganra', 'nadi', 'yoni', 'varna')
        }),
        ('Charts and Positions', {
            'fields': ('lagna_chart', 'chart_url', 'houses', 'planet_positions', 'planets_longitudes', 'planet_house_map')
        }),
        ('Yogas and Doshas', {
            'fields': ('sade_sati_result', 'sade_sati_phases', 'kundli_data', 'manglik_dosha', 'kaal_sarp_dosha', 
                      'mahapurush_yogas', 'gaja_kesari_yoga', 'budha_aditya_yoga', 'pitra_dosha')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
