from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, TwoFactorLoginView,
    EmailVerificationView, ResendEmailVerificationView,
    PasswordResetRequestView, PasswordResetConfirmView,
    ChangePasswordView, PasswordVerificationView,AccountDeactivateView,AccountRestoreView,
    UserProfileView, TwoFactorSetupView, CheckAuthView,TwoFactorLoginOtpSend, RefreshTokenView, ChangeEmailRequestOTPView, ChangeEmailVerifyOTPView
    ,FollowUserView, UnfollowUserView, FollowersListView, FollowingListView
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # Registration and Login
    path("register/", RegisterView.as_view(), name="api_register"),
    path("login/", LoginView.as_view(), name="api_login"),
    path("login/2fa/", TwoFactorLoginView.as_view(), name="api_2fa_login"),
    path("resend/otp/", TwoFactorLoginOtpSend.as_view(), name="api_2fa_login_otp_send"),
    path("refresh-token/", RefreshTokenView.as_view(), name="api_refresh_token"),
    path("logout/", LogoutView.as_view(), name="api_logout"),
    
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    
    # Email Verification
    path("verify-email/<uidb64>/<token>/", EmailVerificationView.as_view(), name="api_verify_email"),
    path("resend-verification/", ResendEmailVerificationView.as_view(), name="api_resend_verification"),
    
    # Password Management
    path("password-reset-request/", PasswordResetRequestView.as_view(), name="api_password_reset_request"),
    path("password-reset-confirm/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="api_password_reset_confirm"),
  
    path("change-password/", ChangePasswordView.as_view(), name="api_change_password"),
    path("verify-password/", PasswordVerificationView.as_view(), name="api_verify_password"),

    # User Profile
    path("profile/", UserProfileView.as_view(), name="api_profile"),
    path("2fa-setup/", TwoFactorSetupView.as_view(), name="api_2fa_setup"),
    
    # Authentication Check
    path("check-auth/", CheckAuthView.as_view(), name="api_check_auth"),

    path("change-email/request-otp/", ChangeEmailRequestOTPView.as_view(), name="api_change_email_otp_request"),
    path("change-email/verify/", ChangeEmailVerifyOTPView.as_view(), name="api_change_email_otp_verify"),
    path('account/deactivate/', AccountDeactivateView.as_view(), name='account-deactivate'),
    path('account/restore/', AccountRestoreView.as_view(), name='account-restore'),


    path('follow/<int:user_id>/', FollowUserView.as_view(), name='follow-user'),
    path('unfollow/<int:user_id>/', UnfollowUserView.as_view(), name='unfollow-user'),
    path('followers/<int:user_id>/', FollowersListView.as_view(), name='followers-list'),
    path('following/<int:user_id>/', FollowingListView.as_view(), name='following-list'),
]