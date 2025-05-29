from django.contrib import admin
from .models import KundliMatching

@admin.register(KundliMatching)
class KundliMatchingAdmin(admin.ModelAdmin):
    list_display = ('boy_birth', 'girl_birth', 'varna_score', 'vasha_score', 'tara_score', 'yoni_score', 'graha_maitry_score', 'gana_score', 'bhakoot_score', 'nadi_score')
    list_filter = ('varna_score', 'vasha_score', 'tara_score', 'yoni_score', 'graha_maitry_score', 'gana_score', 'bhakoot_score', 'nadi_score')
    search_fields = ('boy_birth__birth_date', 'girl_birth__birth_date')
    readonly_fields = ('boy_birth', 'girl_birth')
    fieldsets = (
        ('Birth Details', {
            'fields': ('boy_birth', 'girl_birth')
        }),
        ('Matching Scores', {
            'fields': ('varna_score', 'vasha_score', 'tara_score', 'yoni_score', 'graha_maitry_score', 'gana_score', 'bhakoot_score', 'nadi_score')
        }),
    )
