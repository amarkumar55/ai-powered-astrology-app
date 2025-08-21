from rest_framework import serializers
from horoscope.models import Horoscope

class HoroscopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horoscope
        fields = [
            'id', 'sign', 'date', 'type', 'general', 'love', 'career', 'health', 'finance', 'created_at', 'updated_at'
        ] 