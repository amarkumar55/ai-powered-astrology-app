from django.db import models
from invoice.models import Invoice
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from home.models import TimeStampMixin

User = get_user_model()

    

class Feature(TimeStampMixin):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=False)
    qty = models.IntegerField()
    is_active = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Feature, self).save(*args, **kwargs)


    def __str__(self):
        return f"{self.name} - {self.qty}" 
    
    class Mata:
        app_label = "core"
    
 


class Plan(TimeStampMixin):

    name = models.CharField(max_length=100)
    features = models.ManyToManyField(Feature, related_name='features', blank=False)    
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(help_text="Number of days the plan is valid")
    razorpay_plan_id = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Plan, self).save(*args, **kwargs)


    class Mata:
        app_label = "core"
    

    


class UserSubscription(TimeStampMixin):
   
    STATUS_CHOICES = (
        ("active", "Active"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey('core.CustomUser', on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    is_trial = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    invoice_id = models.IntegerField(null=True, blank=True)
    payment_paid = models.BooleanField(default=False)
    razorpay_subscription_id = models.CharField(max_length=200, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.plan.name} ({self.status})"
    

    class Mata:
        app_label = "core"
    


class UserFeatureUsage(TimeStampMixin):
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='feature_usages')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    remain_quantity = models.IntegerField(default=0)

    def remaining(self):
        return max(0, self.feature.qty - self.remain_quantity)
    
   
    class Mata:
        app_label = "core"
    


class UserTransaction(TimeStampMixin):
  
    PAYMENT_METHOD_CHOICES = [
        ("Credit Card", "Credit Card"),
        ("Debit Card", "Debit Card"),
        ("UPI", "UPI"),
        ("PayPal", "PayPal"),
        ("Net Banking", "Net Banking"),
        ("Wallet", "Wallet"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Success", "Success"),
        ("Failed", "Failed"),
        ("Refunded", "Refunded"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey('core.CustomUser', on_delete=models.CASCADE, related_name='users')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='invoices')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=255, unique=True,  blank=False, null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    gateway_response = models.JSONField(blank=True, null=True)
    refund_id = models.CharField(max_length=255, blank=True, null=True)
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-transaction_date']
        app_label = "core"
    def __str__(self):
        return f"{self.transaction_id} - {self.status}"