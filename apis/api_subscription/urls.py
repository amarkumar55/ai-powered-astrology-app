from django.urls import path
from .views import PlanListView, PlanDetailView, SubscribeAstroPlanView, UserAstrologySubscriptionsView, RazorpayCheckoutView, AssignPlanView

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='plan-list'),
    path('plans/<slug:slug>/', PlanDetailView.as_view(), name='plan-detail'),
    path('checkout/', RazorpayCheckoutView.as_view(), name='razorpay-checkout'),
    path('assign/', AssignPlanView.as_view(), name='assign-plan'),

    # Astrology Subscription
    path('subscribe/', SubscribeAstroPlanView.as_view(), name='subscribe'),
    path('user-subscriptions/', UserAstrologySubscriptionsView.as_view(), name='user-subscriptions'),
] 