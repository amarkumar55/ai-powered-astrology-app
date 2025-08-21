from rest_framework import serializers
from home.models import ContactQuery
from authentication.models import Wallet, UserActivity, WalletTransaction


class ContactQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactQuery
        fields = ['id', 'full_name', 'email', 'message', 'created_at', 'updated_at']

    def create(self, validated_data):
        using = self.context.get('using') or 'default'
        return ContactQuery.objects.using(using).create(**validated_data)
    
class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'  # Or specify only the fields you want to expose


class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = '__all__'  # Or specify only the fields you want to expose


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = '__all__'  # Or specify only the fields you want to expose

