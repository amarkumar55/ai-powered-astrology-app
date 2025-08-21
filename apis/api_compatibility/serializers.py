from rest_framework import serializers
from compatibility.models import KundliMatching
from dasha.models import BirthDetails

class BirthDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BirthDetails
        fields = ['id', 'birth_date', 'birth_time', 'latitude', 'longitude']

class KundliMatchingSerializer(serializers.ModelSerializer):
    boy_birth = BirthDetailsSerializer(read_only=True)
    girl_birth = BirthDetailsSerializer(read_only=True)
    class Meta:
        model = KundliMatching
        fields = [
            'id', 'boy_birth', 'girl_birth', 'varna_score', 'vasha_score', 'tara_score', 'yoni_score',
            'graha_maitry_score', 'gana_score', 'bhakoot_score', 'nadi_score', 'created_at', 'updated_at'
        ] 