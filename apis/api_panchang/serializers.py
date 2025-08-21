from rest_framework import serializers
from panchang.models import Panchang, UserPanchang

class PanchangSerializer(serializers.ModelSerializer):
    class Meta:
        model = Panchang
        fields = '__all__'

class UserPanchangSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPanchang
        fields = '__all__' 