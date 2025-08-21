from rest_framework import serializers
from kundli.models import KundliReport

class KundliReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = KundliReport
        fields = '__all__'
        depth = 1 