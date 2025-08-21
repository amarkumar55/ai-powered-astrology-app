from django.db import models
from django.contrib.auth import get_user_model
from home.models import TimeStampMixin
User = get_user_model()

class Invoice(TimeStampMixin):
    INVOICE_TYPE_CHOICES = (
        ('subscription', 'Subscription'),
        ('onetime', 'One-Time Service'),
    )

    STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey('core.CustomUser', on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=100, unique=True, blank=True)
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES)
    subscription = models.OneToOneField('subscription.UserSubscription', on_delete=models.SET_NULL, null=True, blank=True)
    item_description = models.TextField(blank=True, null=True)
    qty = models.IntegerField(blank=False, null=False, default=1) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sub_total = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0.0) 
    tax = models.DecimalField(max_digits=8, decimal_places=2, default=0.0) 
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.0) 
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_reference = models.CharField(max_length=200, blank=True, null=True)
    billing_email = models.EmailField(blank=True, null=True)
    billing_name = models.CharField(max_length=100, blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)
   
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from uuid import uuid4
            self.invoice_number = f"INV-{uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.invoice_type} - {self.status}"
    
    class Mata:
        app_label = "common"