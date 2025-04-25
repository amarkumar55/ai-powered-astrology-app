from django.contrib import admin
from .models import UserFeatureUsage, UserSubscription, Plan, Feature, UserTransaction

# Register your models here.


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'price', 'duration_days','razorpay_plan_id','is_active','created_at','updated_at',)
    prepopulated_fields = {'slug': ('name',)}
    list_filter=('id','name','price','razorpay_plan_id','created_at','updated_at',)
    search_fields=('id','name','price','razorpay_plan_id','created_at','updated_at',)


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('id','name','qty','is_active')
    prepopulated_fields = {'slug': ('name',)}
    list_filter=('id','name','is_active',)
    search_fields=('id','plan','is_active',)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'plan', 'start_date','end_date','status','invoice_id','payment_paid','razorpay_payment_id',)
    list_filter=('id','user', 'plan', 'start_date','end_date','status','invoice_id','payment_paid','razorpay_payment_id',)
    search_fields=('id','user', 'plan', 'start_date','end_date','status','invoice_id','payment_paid','razorpay_payment_id',)


@admin.register(UserFeatureUsage)
class UserFeatureUsageAdmin(admin.ModelAdmin):
    list_display = ('id','subscription', 'feature', 'remain_quantity',)
    list_filter=('id','subscription', 'feature', 'remain_quantity',)
    search_fields=('id','subscription', 'feature', 'remain_quantity',)


@admin.register(UserTransaction)
class AdminUserTransaction(admin.ModelAdmin):
    list_display = ('id','user', 'invoice', 'payment_method','transaction_id','amount','currency','status','refund_id','refunded_amount','transaction_date','updated_at')
    list_filter=('id','user', 'invoice', 'transaction_id','refund_id','transaction_date','updated_at')
    search_fields=('id','user', 'invoice', 'transaction_id','refund_id','transaction_date','updated_at')