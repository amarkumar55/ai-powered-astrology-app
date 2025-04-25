from .models import Invoice
from django.contrib import admin
# Register your models here.


@admin.register(Invoice)
class AdminInvoice(admin.ModelAdmin):
    list_display =('id','invoice_number','user','item_description','status','total_amount','payment_method','payment_reference','billing_email','billing_name','billing_address','created_at',)
    list_filter = ('invoice_number','user','created_at',)
    search_fields = ('invoice_number','user','created_at',)