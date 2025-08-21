from rest_framework import serializers
from dasha.models import AntarDasha, DashaEffect, BirthDetails

class BirthDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BirthDetails
        fields = ['id', 'birth_date', 'birth_time', 'latitude', 'longitude']

class AntarDashaSerializer(serializers.ModelSerializer):
    birth_details = BirthDetailsSerializer(read_only=True)
    class Meta:
        model = AntarDasha
        fields = [
            'id', 'birth_details', 'nakshatra', 'major_dasha', 'remaining_years',
            'antar_dasha_planet', 'start_date', 'end_date', 'created_at', 'updated_at'
        ]

class DashaEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashaEffect
        fields = [
            'id', 'mahadasha_planet', 'antar_dasha_planet', 'start_date', 'end_date',
            'mahadasha_effect', 'antardasha_effect', 'combined_effect', 'created_at', 'updated_at'
        ] 