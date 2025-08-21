from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import date, timedelta
from authentication.models import EmailOTP

User = get_user_model()


class APIAuthenticationTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('api_register')
        self.login_url = reverse('api_login')
        self.logout_url = reverse('api_logout')
        
        # Test user data
        self.user_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'birth_date': '1990-01-01',
            'gender': 'Male',
            'is_accepted_terms': True
        }
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='TestPass123!',
            first_name='Existing',
            last_name='User',
            birth_date=date(1990, 1, 1),
            gender='Male',
            is_accepted_terms=True
        )

    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], self.user_data['email'])
        
        # Check if user was created in database
        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])
        

    def test_user_registration_duplicate_email(self):
        """Test registration with existing email"""
        # Create user first
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='TestPass123!',
            first_name='Existing',
            last_name='User',
            birth_date=date(1990, 1, 1),
            gender='Male',
            is_accepted_terms=True
        )
        
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_invalid_data(self):
        """Test registration with invalid data"""
        invalid_data = self.user_data.copy()
        invalid_data['password'] = 'weak'  # Weak password
        
        response = self.client.post(self.register_url, invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_login_success(self):
        """Test successful user login"""
        login_data = {
            'email': 'existing@example.com',
            'password': 'TestPass123!'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            'email': 'existing@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_user_logout(self):
        """Test user logout"""
        # First login to get token
        login_data = {
            'email': 'existing@example.com',
            'password': 'TestPass123!'
        }
        login_response = self.client.post(self.login_url, login_data)
        token = login_response.data['token']
        
        # Set token in header
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        # Logout
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)


class APIEmailVerificationTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.verify_url = reverse('api_verify_email')
        self.resend_url = reverse('api_resend_verification')
        
        # Create unverified user
        self.user = User.objects.create_user(
            username='unverified',
            email='unverified@example.com',
            password='TestPass123!',
            first_name='Unverified',
            last_name='User',
            birth_date=date(1990, 1, 1),
            gender='Male',
            is_accepted_terms=True,
            is_email_verified=False
        )

    def test_email_verification_success(self):
        """Test successful email verification"""
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        from django.contrib.auth.tokens import default_token_generator
        
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        
        verification_data = {
            'uid': uid,
            'token': token
        }
        
        response = self.client.post(self.verify_url, verification_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Check if user is now verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_email_verification_invalid_token(self):
        """Test email verification with invalid token"""
        verification_data = {
            'uid': 'invalid_uid',
            'token': 'invalid_token'
        }
        
        response = self.client.post(self.verify_url, verification_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_resend_verification_email(self):
        """Test resending verification email"""
        resend_data = {
            'email': 'unverified@example.com'
        }
        
        response = self.client.post(self.resend_url, resend_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)


class APIPasswordResetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.reset_request_url = reverse('api_password_reset_request')
        self.reset_confirm_url = reverse('api_password_reset_confirm')
        
        # Create verified user
        self.user = User.objects.create_user(
            username='resetuser',
            email='reset@example.com',
            password='TestPass123!',
            first_name='Reset',
            last_name='User',
            birth_date=date(1990, 1, 1),
            gender='Male',
            is_accepted_terms=True,
            is_email_verified=True
        )

    def test_password_reset_request(self):
        """Test password reset request"""
        reset_data = {
            'email': 'reset@example.com'
        }
        
        response = self.client.post(self.reset_request_url, reset_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_password_reset_confirm(self):
        """Test password reset confirmation"""
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        from django.contrib.auth.tokens import default_token_generator
        
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        
        confirm_data = {
            'uid': uid,
            'token': token,
            'new_password': 'NewPass123!',
            'confirm_password': 'NewPass123!'
        }
        
        response = self.client.post(self.reset_confirm_url, confirm_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Check if password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass123!'))


class APIUserProfileTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.profile_url = reverse('api_profile')
        
        # Create user and token
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='TestPass123!',
            first_name='Profile',
            last_name='User',
            birth_date=date(1990, 1, 1),
            gender='Male',
            is_accepted_terms=True,
            is_email_verified=True
        )
        self.token = Token.objects.create(user=self.user)

    def test_get_user_profile(self):
        """Test getting user profile"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['first_name'], self.user.first_name)

    def test_update_user_profile(self):
        """Test updating user profile"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Updated bio'
        }
        
        response = self.client.put(self.profile_url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Check if profile was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.bio, 'Updated bio')

    def test_get_profile_unauthorized(self):
        """Test getting profile without authentication"""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class APIChangePasswordTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.change_password_url = reverse('api_change_password')
        
        # Create user and token
        self.user = User.objects.create_user(
            username='passworduser',
            email='password@example.com',
            password='TestPass123!',
            first_name='Password',
            last_name='User',
            birth_date=date(1990, 1, 1),
            gender='Male',
            is_accepted_terms=True,
            is_email_verified=True
        )
        self.token = Token.objects.create(user=self.user)

    def test_change_password_success(self):
        """Test successful password change"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        change_data = {
            'old_password': 'TestPass123!',
            'new_password': 'NewPass123!',
            'confirm_password': 'NewPass123!'
        }
        
        response = self.client.post(self.change_password_url, change_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Check if password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass123!'))

    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        change_data = {
            'old_password': 'WrongPass123!',
            'new_password': 'NewPass123!',
            'confirm_password': 'NewPass123!'
        }
        
        response = self.client.post(self.change_password_url, change_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)

    def test_change_password_mismatch(self):
        """Test password change with mismatched new passwords"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        change_data = {
            'old_password': 'TestPass123!',
            'new_password': 'NewPass123!',
            'confirm_password': 'DifferentPass123!'
        }
        
        response = self.client.post(self.change_password_url, change_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)


class APITwoFactorTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.twofa_setup_url = reverse('api_2fa_setup')
        self.twofa_login_url = reverse('api_2fa_login')
        
        # Create user with 2FA enabled
        self.user = User.objects.create_user(
            username='2fauser',
            email='2fa@example.com',
            password='TestPass123!',
            first_name='TwoFactor',
            last_name='User',
            birth_date=date(1990, 1, 1),
            gender='Male',
            is_accepted_terms=True,
            is_email_verified=True,
            two_factor_enabled=True
        )

    def test_enable_2fa(self):
        """Test enabling two-factor authentication"""
        self.user.two_factor_enabled = False
        self.user.save()
        
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        setup_data = {
            'enable_2fa': True
        }
        
        response = self.client.post(self.twofa_setup_url, setup_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Check if 2FA was enabled
        self.user.refresh_from_db()
        self.assertTrue(self.user.two_factor_enabled)

    def test_disable_2fa(self):
        """Test disabling two-factor authentication"""
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        setup_data = {
            'enable_2fa': False
        }
        
        response = self.client.post(self.twofa_setup_url, setup_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Check if 2FA was disabled
        self.user.refresh_from_db()
        self.assertFalse(self.user.two_factor_enabled)

    def test_2fa_login_flow(self):
        """Test 2FA login flow"""
        login_data = {
            'email': '2fa@example.com',
            'password': 'TestPass123!'
        }
        
        response = self.client.post(reverse('api_login'), login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('requires_2fa', response.data)
        self.assertTrue(response.data['requires_2fa'])


class APIAuthenticationCheckTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.check_auth_url = reverse('api_check_auth')
        
        # Create user and token
        self.user = User.objects.create_user(
            username='checkuser',
            email='check@example.com',
            password='TestPass123!',
            first_name='Check',
            last_name='User',
            birth_date=date(1990, 1, 1),
            gender='Male',
            is_accepted_terms=True,
            is_email_verified=True
        )
        self.token = Token.objects.create(user=self.user)

    def test_check_auth_authenticated(self):
        """Test authentication check for authenticated user"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        response = self.client.get(self.check_auth_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['authenticated'])
        self.assertIn('user', response.data)

    def test_check_auth_unauthenticated(self):
        """Test authentication check for unauthenticated user"""
        response = self.client.get(self.check_auth_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
