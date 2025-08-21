from rest_framework import serializers
from subscription.models import Plan, Feature, UserSubscription, UserFeatureUsage, UserTransaction

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'name', 'slug', 'qty', 'is_active']

class PlanSerializer(serializers.ModelSerializer):
    features = FeatureSerializer(many=True, read_only=True)
    class Meta:
        model = Plan
        fields = ['id', 'name', 'features', 'description', 'slug', 'price', 'duration_days', 'razorpay_plan_id', 'is_active']

class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    class Meta:
        model = UserSubscription
        fields = ['id', 'user', 'plan', 'is_trial', 'start_date', 'end_date', 'status', 'invoice_id', 'payment_paid', 'razorpay_subscription_id', 'razorpay_payment_id']

class UserFeatureUsageSerializer(serializers.ModelSerializer):
    feature = FeatureSerializer(read_only=True)
    class Meta:
        model = UserFeatureUsage
        fields = ['id', 'subscription', 'feature', 'remain_quantity']

class UserTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTransaction
        fields = ['id', 'user', 'invoice', 'payment_method', 'transaction_id', 'amount', 'currency', 'status', 'gateway_response', 'refund_id', 'refunded_amount', 'transaction_date'] 