from . import views
from django.urls import path
from django_ratelimit.decorators import ratelimit
from django.contrib.auth import views as auth_views


urlpatterns = [
   path("login", views.CustomLoginView.as_view(), name="auth.login"),
   path("register", views.RegisterView.as_view(), name="auth.register"),
   path("verify/login/otp", views.VerifyLoginOTPView.as_view(), name="verify_login_otp"),
   path("logout", views.CustomLogoutView.as_view(), name="auth.logout"),
   path('verify/<uidb64>/<token>/', views.ProcessAccountVerificationView.as_view(), name='accont_verification'),
   path('resend/verification/email', views.ResendVerificationView.as_view(), name='resend_verification'),
   path('password/reset/', ratelimit(key='user_or_ip', rate='5/m', block=True)(auth_views.PasswordResetView.as_view(template_name='authentication/password_reset.html')), name='password_reset'),
   path('password/reset/done/',ratelimit(key='user_or_ip', rate='5/m', block=True) (auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html')), name='password_reset_done'),
   path('reset/<uidb64>/<token>/',ratelimit(key='user_or_ip', rate='5/m', block=True) (views.CustomPasswordResetConfirmView.as_view()), name='password_reset_confirm'),
   path('reset/done/', ratelimit(key='user_or_ip', rate='5/m', block=True)(auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html')), name='password_reset_complete'),
]
