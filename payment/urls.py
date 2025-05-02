from . import views
from django.urls import path

urlpatterns = [
   path("payment/kundli-payment-checkout", views.kundli_payment_checkout, name="payment.kundli_payment_checkout"),
   path("premium/payment/handler", views.KundliPaymentHandler, name="kundli.payment_handle"),
   path("payment/subscription-payment-checkout", views.subscription_payment_checkout, name="payment.subscription_payment_checkout"),
   path("subscription/payment/handler", views.SubscriptionPaymentHandler, name="subscription.payment_handle"),
   path("test_payment", views.test_payment, name="subscription.test"),
]
