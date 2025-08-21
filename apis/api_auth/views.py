from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django_ratelimit.decorators import ratelimit
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta
from utlity.helper import store_activity
import logging
from authentication.utlity import  send_verification_email_api, send_otp_message_api
from .utility import create_refresh_token
from .serializers import (
    RegisterSerializer, LoginSerializer, EmailVerificationSerializer,
    ResendEmailVerificationSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, ChangePasswordSerializer,
    PasswordVerificationSerializer, UserProfileSerializer,
    UpdateProfileSerializer, TwoFactorSetupSerializer,
    EmailOtpRequestSerializer, EmailOtpVerifySerializer,
    AccountDeactivateSerializer,AccountRestoreSerializer,
    FollowSerializer, UserPublicSerializer
)
from dashboard.utlity import get_cache_key,get_attempt_key
from authentication.utlity import send_otp_message
from django.core.cache import cache
from authentication.models import EmailOTP, Follow


User = get_user_model()
logger = logging.getLogger(__name__)

    
# total seconds 
EXPIRE_IN = 3600
OTP_EXPIRY_MINUTES = 5
OTP_COOLDOWN_SECONDS = 60
MAX_ATTEMPTS = 5

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='5/m', block=True))
    def post(self, request):
        """Register a new user with JWT auth"""

        serializer = RegisterSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            try:
                user = serializer.save()

            
                refresh = RefreshToken.for_user(user)
                access = refresh.access_token

                # Store activity log
                store_activity(
                    request,
                    {},
                    "Account Created",
                    user
                )

                return Response({
                    "message": "Registration successful. Please check your email for verification.",
                    "access": str(access),
                    "refresh": str(refresh),
                    "expiresIn": access.lifetime.total_seconds(),
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "is_email_verified": user.is_email_verified,
                        "is_active": user.is_active,
                    }
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                return Response({
                    "error": "Registration failed. Please try again."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='10/m', block=True))
    def post(self, request):
        """Login user"""
        serializer = LoginSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        remember_me = serializer.validated_data.get('remember_me', False)
        account_status = serializer.validated_data.get('account_status', 'active')

        # 🚫 Special account states — don't log in, just return status
        if account_status in ["inactive", "temporary_disabled", "permanent_disabled", "email_unverified"]:
            return Response({
                "message": "Account not active.",
                "status": account_status,
                "email": user.email
            }, status=status.HTTP_200_OK)

        # ✅ Handle 2FA if enabled
        if user.two_factor_enabled:
            try:
                send_otp_message_api(user.email, "LOGIN OTP", request)
                return Response({
                    "message": "Two-factor authentication required.",
                    "requires_2fa": True,
                    "email": user.email
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"2FA OTP send error: {str(e)}")
                return Response({
                    "error": "Failed to send verification code."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # ✅ Regular login
        login(request, user)
        token, _ = Token.objects.using(request.db).get_or_create(user=user)
        refresh_token = create_refresh_token(user)

        store_activity(request, {}, "Logged Into Acount", user)

        # Session expiry
        if remember_me:
            request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
        else:
            request.session.set_expiry(0)  # Browser close

        return Response({
            "message": "Login successful.",
            "status": "active",
            "token": token.key,
            "refreshToken": refresh_token.token,
            "expiresIn": EXPIRE_IN,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_email_verified": user.is_email_verified,
                'is_active':user.is_active,
            }
        }, status=status.HTTP_200_OK)
    

class TwoFactorLoginView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='10/m', block=True))
    def post(self, request):
        """Complete login with 2FA OTP"""
        email = request.data.get('email')
        otp = request.data.get('otp')
        db = request.db
     
        
        if not email or not otp:
            return Response({
                'error': 'Email and OTP are required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.using(db).get(email=email)
            
            # Verify OTP (you'll need to implement OTP verification logic)
            # This is a placeholder - implement based on your OTP system
            from authentication.models import EmailOTP
            
            try:
                email_otp = EmailOTP.objects.using(db).get(email=email, otp=otp)
                # Check if OTP is not expired (e.g., 10 minutes)
                if timezone.now() - email_otp.otp_created_at > timedelta(minutes=10):
                    return Response({
                        'error': 'OTP has expired.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Clear used OTP
                email_otp.delete()
                
            except EmailOTP.DoesNotExist:
                return Response({
                    'error': 'Invalid OTP.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Complete login
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            token, _ = Token.objects.using(db).get_or_create(user=user)
            refresh_token = create_refresh_token(user)
            store_activity(request, {}, "Logged Into Acount", user)
            return Response({
                'message': 'Login successful.',
                'token': token.key,
                'refreshToken': refresh_token.token,
                'expiresIn': EXPIRE_IN,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_email_verified': user.is_email_verified,
                    'is_active':user.is_active,
                }
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'User not found.'
            }, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorLoginOtpSend(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='10/m', block=True))
    def post(self, request):
        """Complete login with 2FA OTP"""
        email = request.data.get('email')
     
        try:
            send_otp_message_api(email, "LOGIN OTP",request)
            return Response({
                'message': 'OTP sent, Please check your mail.',
                'email': email
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"2FA OTP send error: {str(e)}")
            return Response({
                'error': 'Failed to send verification code.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class RefreshTokenView(APIView):
    def post(self, request):

        refresh_token_value = request.data.get("refresh_token")

        if not refresh_token_value:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh_token = RefreshToken.objects.get(token=refresh_token_value)
            
        except RefreshToken.DoesNotExist:
            return Response({"error": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)

        if not refresh_token.is_valid():
            return Response({"error": "Refresh token expired or inactive."}, status=status.HTTP_401_UNAUTHORIZED)

        user = refresh_token.user

        # Optional: Invalidate old access token
        Token.objects.filter(user=user).delete()

        # Generate new access token
        access_token = Token.objects.create(user=user)

        return Response({
            "token": access_token.key,
            "user_id": user.id,
            "email": user.email
        }, status=status.HTTP_200_OK)
             

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Logout user"""
        db_source = request.db

        try:
            # Delete token
            Token.objects.using(db_source).filter(user=request.user).delete()
            store_activity(request, {}, "Logout from acount", request.user)
            # Logout from session
            logout(request)
            
            return Response({
                'message': 'Logged out successfully.'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({
                'error': 'Logout failed.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailVerificationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Verify email with token"""
        uuid = self.kwargs.get('uidb64')
        token = self.kwargs.get('token')

        serializer = EmailVerificationSerializer(data=request.data,context={'request': request,'uuid':uuid, 'token':token})
        
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Email verified successfully.'
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Email verification error: {str(e)}")
                return Response({
                    'error': 'Email verification failed.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendEmailVerificationView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='3/m', block=True))
    def post(self, request):
        """Resend email verification"""

        serializer = ResendEmailVerificationSerializer(data=request.data,context={'request': request})
        
        if serializer.is_valid():
            user = serializer.context['user']
            
            try:
                send_verification_email_api(request, user)
                return Response({
                    'message': 'Verification email sent successfully.'
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Resend verification error: {str(e)}")
                return Response({
                    'error': 'Failed to send verification email.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='3/m', block=True))
    def post(self, request):
        """Request password reset"""
   
        serializer = PasswordResetRequestSerializer(data=request.data,context={'request': request})
        
        if serializer.is_valid():
            user = serializer.context.get('user')
            
            if user:
                try:
                    # Generate reset token
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    
                    # Store reset token (optional - for additional security)
                    user.password_reset_token = token
                    user.save()
                    
                    # Send reset email
                    reset_url = request.build_absolute_uri(
                        f'/api/1.0/auth/password-reset-confirm/{uid}/{token}/'
                    )
                    
                    # You can implement a proper email template here
                
                    send_mail(
                        'Password Reset Request',
                        f'Click here to reset your password: {reset_url}',
                        'noreply@yourdomain.com',
                        [user.email],
                        fail_silently=False,
                    )
                    
                    return Response({
                        'message': 'Password reset email sent successfully.'
                    }, status=status.HTTP_200_OK)
                except Exception as e:
                    logger.error(f"Password reset request error: {str(e)}")
                    return Response({
                        'error': 'Failed to send reset email.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                # Don't reveal if email exists or not
                return Response({
                    'message': 'If an account with this email exists, a reset link has been sent.'
                }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@method_decorator(ratelimit(key='ip', rate='5/m', block=True), name='dispatch')
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
 

    def post(self, request, *args, **kwargs):
        """Confirm password reset with token"""
        uuid = self.kwargs.get('uidb64')
        token = self.kwargs.get('token')

        serializer = PasswordResetConfirmSerializer(data=request.data, context={'request': request, 'uid':uuid, 'token':token})
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            new_password = serializer.validated_data['new_password']
            
            try:
                # Set new password
                user.set_password(new_password)
                user.password_reset_token = None  # Clear reset token
                user.save()
                
                store_activity(request, {}, "Password Changed", user)
                
                send_mail(
                    'Password Changed',
                    f'Your Password has been changed successfully.',
                    'noreply@yourdomain.com',
                    [user.email],
                    fail_silently=False,
                )

                # Delete all existing tokens for this user
                Token.objects.using(request.db).filter(user=user).delete()
    
                return Response({
                    'message': 'Password reset successfully.'
                }, status=status.HTTP_200_OK)
            
            except Exception as e:
                logger.error(f"Password reset confirm error: {str(e)}")
                return Response({
                    'error': 'Password reset failed.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    @method_decorator(ratelimit(key='user', rate='5/m', block=True))
    def post(self, request):
        """Change password for authenticated user"""
        
        serializer = ChangePasswordSerializer(data=request.data,user=request.user, context={'request': request})
        
        if serializer.is_valid():
            try:
                new_password = serializer.validated_data['new_password']
                request.user.set_password(new_password)
                request.user.save()
                store_activity(request, {}, "Password Changed", request.user)
                # Delete all existing tokens for this user

                send_mail(
                    'Password Changed',
                    f'Your Password has been changed successfully.',
                    'noreply@yourdomain.com',
                    [request.user.email],
                    fail_silently=False,
                )

                Token.objects.using(request.db).filter(user=request.user).delete()
                
                return Response({
                    'message': 'Password changed successfully.'
                }, status=status.HTTP_200_OK)
            
            except Exception as e:

                logger.error(f"Change password error: {str(e)}")
                return Response({
                    'error': 'Password change failed.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordVerificationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Verify current password"""
        
        serializer = PasswordVerificationSerializer(data=request.data, user=request.user, context={'request': request})
        
        if serializer.is_valid():
            return Response({
                'message': 'Password verified successfully.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # ✅ ADD THIS LINE
    
    def get(self, request):
        """Get user profile"""
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        """Update user profile"""
    
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        store_activity(request, {}, "Profile updated", request.user)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully.',
                'user': UserProfileSerializer(request.user).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TwoFactorSetupView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Enable/disable two-factor authentication"""

        serializer = TwoFactorSetupSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            enable_2fa = serializer.validated_data['enable_2fa']
            
            try:
                request.user.two_factor_enabled = enable_2fa
                request.user.save()
                store_activity(request, {}, "Updated 2FA Setting", request.user)
                return Response({
                    'message': f'Two-factor authentication {"enabled" if enable_2fa else "disabled"} successfully.',
                    'two_factor_enabled': enable_2fa
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"2FA setup error: {str(e)}")
                return Response({
                    'error': 'Failed to update two-factor authentication settings.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckAuthView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Check if user is authenticated and return user info"""
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response({
            'authenticated': True,
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
class ChangeEmailRequestOTPView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EmailOtpRequestSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            old_email = serializer.validated_data['old_email']
            new_email = serializer.validated_data['new_email']

            if User.objects.filter(email=new_email).exists():
                return Response(
                    {'error': 'Email is already linked with another account.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cooldown_key = get_cache_key(old_email)
           
            if cache.get(cooldown_key):
                return Response(
                    {'error': 'Please wait before requesting OTP again.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            send_otp_message(old_email, "Your OTP for Email Verification")
            send_otp_message(new_email, "Your OTP for Email Verification")

            # Set cooldown (e.g., 1 minute)
            cache.set(cooldown_key, True, timeout=60)

            return Response(
                {'message': 'OTPs sent to both old and new email addresses.'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error sending OTPs for email change: {str(e)}")
            return Response(
                {'error': 'Failed to send OTPs for email change.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChangeEmailVerifyOTPView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        db = request.db
        serializer = EmailOtpVerifySerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            old_email = serializer.validated_data['old_email']
            new_email = serializer.validated_data['new_email']
            old_email_otp = serializer.validated_data['old_email_otp']
            new_email_otp = serializer.validated_data['new_email_otp']

            try:
                old_otp = EmailOTP.objects.using(db).get(email=old_email)
                new_otp = EmailOTP.objects.using(db).get(email=new_email)
            except EmailOTP.DoesNotExist:
                return Response(
                    {'error': 'OTP not found for one or both emails.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if old_otp.is_expired() or new_otp.is_expired():
                return Response(
                    {'error': 'One or both OTPs have expired.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            attempt_key = get_attempt_key(old_email)
            attempts = cache.get(attempt_key, 0)
            if attempts >= MAX_ATTEMPTS:
                return Response(
                    {'error': 'Too many invalid attempts. Try again later.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            if old_otp.verify_otp(old_email_otp) and new_otp.verify_otp(new_email_otp):
                cache.delete(attempt_key)
                request.user.email = new_email
                request.user.save()

                store_activity(
                    request,
                    {"new_email": new_email, "old_email": old_email},
                    "Changed email for account",
                    request.user
                )

                return Response(
                    {'message': 'Email updated successfully.'},
                    status=status.HTTP_200_OK
                )
            else:
                cache.set(attempt_key, attempts + 1, 600)  # 10-minute expiry
                return Response(
                    {'error': 'Invalid OTP(s).'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.error(f"Error verifying OTPs for email change: {str(e)}")
            return Response(
                {'error': 'Failed to verify OTPs for email change.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class AccountDeactivateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def post(self, request):
        serializer = AccountDeactivateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": "Account deactivated. It will be permanently deleted after 30 days if you don't log in again."
            },
            status=status.HTTP_200_OK
        )
    

class AccountRestoreView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = AccountRestoreSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": "Account restored. You can now login into your account."
            },
            status=status.HTTP_200_OK
        )
    

class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if target_user == request.user:
            return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
        if not created:
            return Response({"message": "Already following."}, status=status.HTTP_200_OK)

        return Response(FollowSerializer(follow).data, status=status.HTTP_201_CREATED)


class UnfollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        try:
            follow = Follow.objects.get(follower=request.user, following_id=user_id)
        except Follow.DoesNotExist:
            return Response({"error": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)

        follow.delete()
        return Response({"message": "Unfollowed successfully."}, status=status.HTTP_200_OK)


class FollowersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        followers = Follow.objects.filter(following_id=user_id)
        data = [UserPublicSerializer(f.follower).data for f in followers]
        return Response(data, status=status.HTTP_200_OK)


class FollowingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        following = Follow.objects.filter(follower_id=user_id)
        data = [UserPublicSerializer(f.following).data for f in following]
        return Response(data, status=status.HTTP_200_OK)