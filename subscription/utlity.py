from uuid import uuid4
from datetime import timedelta
from django.utils import timezone
from invoice.utlity import calculate_total_and_tax
from utlity.location_loader import get_all_countries
from .models import UserSubscription, UserFeatureUsage, Plan

def create_subscription(plan, user, invoice):
    # Cancel previous subscription if any
    UserSubscription.objects.filter(user=user).update(status="expired")

    start_date = timezone.now()
    end_date = start_date + timedelta(days=plan.duration_days)

    subscription = UserSubscription.objects.create(
        user=user,
        plan=plan,
        start_date=start_date,
        end_date=end_date,
        status="active",
        payment_paid=True,
        invoice_id=invoice.id,
        razorpay_subscription_id=f"INV-{uuid4().hex[:8].upper()}",
        razorpay_payment_id=f"INV-{uuid4().hex[:8].upper()}",
    )

    assignFeatures(plan.features.all(), subscription)

    return subscription

def assignFeatures(features, subscription):
    for feature in features:
        if feature.is_active:
            UserFeatureUsage.objects.create(
                subscription=subscription,
                feature=feature,
                remain_quantity=feature.qty
            )

def create_data(plan_slug):
    plan = Plan.objects.prefetch_related('features').filter(slug=plan_slug).first()

    if not plan:
        return {"error": "Plan not found"}
    
    gst, total = calculate_total_and_tax(plan.price)
    plan.gst = gst
    plan.total = total
    countries = get_all_countries()
 
    return {plan, countries}
