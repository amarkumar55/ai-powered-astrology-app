from . import views
from django.urls import path
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("index", views.index, name="dashboard.index"),
    path("invoices/index", views.invoices, name="dashboard.invoices"),
    path("kundli/index", views.kundlies, name="dashboard.kundlies"),
    path("activity/index", views.get_your_activity, name="dashboard.activity"),
    path("profile/index", views.ProfileUpdateView.as_view(), name="dashboard.get_profile"),
    path("payment-history/index", views.get_payment_history, name="dashboard.get_payment_history"),
    path("payment-refund-history/index", views.get_refund_history, name="dashboard.get_refund_history"),
    path("manage-account/index", views.AccountDeleteView.as_view(), name="dashboard.get_account_view"),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='authentication/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='authentication/password_change_done.html'), name='password_change_done'),    
    path("secure-your-account/index", views.get_setting, name='dashboard.get_setting'),
    path('secure-your-account/disable/2fa', views.DisableTwoFactorView.as_view(), name="dashboard.disable.2fa"),
    path('secure-your-account/enable/2fa', views.EnableTwoFactorView.as_view(), name="dashboard.enable.2fa"),
    path('secure-your-account/verify-otp/', views.VerifyTwoFactorOTPView.as_view(), name='dashboard.verify_otp'),
    path('change-email/', views.change_email_view, name='dashboard.change_email'),
    path('change-email/generate-otp/', views.SendOTPForEmailChangeView.as_view(), name='emai_generate_otp'),
    path('change-email/verify-otp/', views.VerifyOTPForEmailChangeView.as_view(), name='email_verify_otp'),
]