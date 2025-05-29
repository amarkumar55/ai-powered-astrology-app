from django.contrib import admin
from .models import UserFeatureUsage, UserSubscription, Plan, Feature, UserTransaction

# Register your models here.


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'duration_days', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('features',)
    ordering = ('-created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'price', 'duration_days')
        }),
        ('Features', {
            'fields': ('features',)
        }),
        ('Payment Integration', {
            'fields': ('razorpay_plan_id',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'qty', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


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
class UserTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'invoice', 'payment_method', 'amount', 'status', 'transaction_date')
    list_filter = ('payment_method', 'status', 'transaction_date')
    search_fields = ('user__email', 'user__username', 'transaction_id', 'invoice__invoice_number')
    readonly_fields = ('transaction_date', 'updated_at')
    ordering = ('-transaction_date',)
    fieldsets = (
        ('Transaction Details', {
            'fields': ('user', 'invoice', 'payment_method', 'transaction_id', 'amount', 'currency', 'status')
        }),
        ('Gateway Information', {
            'fields': ('gateway_response',)
        }),
        ('Refund Information', {
            'fields': ('refund_id', 'refunded_amount')
        }),
        ('Metadata', {
            'fields': ('transaction_date', 'updated_at')
        }),
    )