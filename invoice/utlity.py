import os
from .models import Invoice
from decimal import Decimal, InvalidOperation


GST_TAX = Decimal(os.environ.get('GST_TAX_RATE', 18.00))  # 18% default

def calculate_total_and_tax(price):
    try:
        price = Decimal(price)
        gst = (price * GST_TAX) / Decimal('100')
        total = price + gst
        return gst, total
    except (InvalidOperation, TypeError) as e:
        print(f"Decimal calculation failed: {e}")
        return Decimal('0'), Decimal('0')

def create_invoice(plan, user, billing_name, billing_email, billing_address):
    gst, total = calculate_total_and_tax(plan.price)
    print(gst, total)

    new_invoice = Invoice.objects.create(
        user=user,
        invoice_type="subscription",
        item_description=f"subscription for {plan.name} with 1 qty",
        status="paid",
        discount=0,
        sub_total=plan.price,
        tax=gst,
        total_amount=total,
        payment_method="card",
        payment_reference="testing",
        billing_email=billing_email,
        billing_name=billing_name,
        billing_address=billing_address
    )

    return new_invoice
