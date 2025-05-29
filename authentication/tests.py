from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import CustomUser, UserActivity, UserOtp, TwoFactorPhoneDevice, EmailOTP
from .forms import RegisterForm, VerifyLoginOtp, VerifyOtpForm, CustomLoginForm, ResendVerificationForm, CustomSetPasswordForm
from .views import CustomPasswordResetConfirmView, RegisterView, CustomLoginView, VerifyLoginOTPView, CustomLogoutView, ProcessAccountVerificationView, ResendVerificationView

User = get_user_model()

# Model Tests
class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'birth_date': timezone.now().date(),
            'gender': 'Male',
            'username': 'testuser',
            'is_accepted_terms': True
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.gender, 'Male')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.is_accepted_terms)

    def test_user_str(self):
        self.assertEqual(str(self.user), 'test@example.com')

class UserActivityModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)
        self.activity = UserActivity.objects.create(user=self.user, activity_type='login', ip_address='127.0.0.1')

    def test_activity_creation(self):
        self.assertEqual(self.activity.user, self.user)
        self.assertEqual(self.activity.activity_type, 'login')
        self.assertEqual(self.activity.ip_address, '127.0.0.1')

class UserOtpModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)
        self.otp = UserOtp.objects.create(user=self.user, email_otp='12345678')

    def test_otp_creation(self):
        self.assertEqual(self.otp.user, self.user)
        self.assertEqual(self.otp.email_otp, '12345678')

    def test_otp_str(self):
        self.assertEqual(str(self.otp), 'OTP for test@example.com')

class TwoFactorPhoneDeviceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)
        self.device = TwoFactorPhoneDevice.objects.create(user=self.user, phone_number='1234567890')

    def test_device_creation(self):
        self.assertEqual(self.device.user, self.user)
        self.assertEqual(self.device.phone_number, '1234567890')
        self.assertFalse(self.device.is_verified)

    def test_generate_otp(self):
        otp = self.device.generate_otp()
        self.assertEqual(len(otp), 6)
        self.assertIsNotNone(self.device.otp_generated_at)

    def test_verify_otp(self):
        self.device.otp = '123456'
        self.assertTrue(self.device.verify_otp('123456'))
        self.assertTrue(self.device.is_verified)

    def test_device_str(self):
        self.assertEqual(str(self.device), 'testuser - 1234567890')

class EmailOTPModelTest(TestCase):
    def setUp(self):
        self.email_otp = EmailOTP.objects.create(email='test@example.com', otp='123456', otp_created_at=timezone.now())

    def test_email_otp_creation(self):
        self.assertEqual(self.email_otp.email, 'test@example.com')
        self.assertEqual(self.email_otp.otp, '123456')
        self.assertEqual(self.email_otp.attempts, 0)

    def test_is_expired(self):
        self.assertFalse(self.email_otp.is_expired())

    def test_verify_otp(self):
        self.assertTrue(self.email_otp.verify_otp('123456'))

# Form Tests
class RegisterFormTest(TestCase):
    def test_clean_email(self):
        form_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'birth_date': timezone.now().date(),
            'first_name': 'Test',
            'last_name': 'User',
            'gender': 'Male',
            'is_accepted_terms': True
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean_password(self):
        form_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'birth_date': timezone.now().date(),
            'first_name': 'Test',
            'last_name': 'User',
            'gender': 'Male',
            'is_accepted_terms': True
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean_confirm_password(self):
        form_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'birth_date': timezone.now().date(),
            'first_name': 'Test',
            'last_name': 'User',
            'gender': 'Male',
            'is_accepted_terms': True
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean(self):
        form_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'birth_date': timezone.now().date(),
            'first_name': 'Test',
            'last_name': 'User',
            'gender': 'Male',
            'is_accepted_terms': True
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

class VerifyLoginOtpTest(TestCase):
    def test_clean(self):
        form_data = {'otp': '123456'}
        form = VerifyLoginOtp(data=form_data)
        self.assertTrue(form.is_valid())

class VerifyOtpFormTest(TestCase):
    def test_clean_email(self):
        form_data = {'email': 'test@example.com', 'otp': '123456'}
        form = VerifyOtpForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean(self):
        form_data = {'email': 'test@example.com', 'otp': '123456'}
        form = VerifyOtpForm(data=form_data)
        self.assertTrue(form.is_valid())

class CustomLoginFormTest(TestCase):
    def test_form_validation(self):
        form_data = {'username': 'test@example.com', 'password': 'TestPass123!'}
        form = CustomLoginForm(data=form_data)
        self.assertTrue(form.is_valid())

class ResendVerificationFormTest(TestCase):
    def test_form_validation(self):
        form_data = {'email': 'test@example.com'}
        form = ResendVerificationForm(data=form_data)
        self.assertTrue(form.is_valid())

class CustomSetPasswordFormTest(TestCase):
    def test_form_validation(self):
        user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)
        form_data = {'new_password1': 'NewPass123!', 'new_password2': 'NewPass123!'}
        form = CustomSetPasswordForm(user=user, data=form_data)
        self.assertTrue(form.is_valid())

# View Tests
class CustomPasswordResetConfirmViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        response = self.client.get(reverse('password_reset_confirm', kwargs={'uidb64': 'test', 'token': 'test'}))
        self.assertEqual(response.status_code, 200)

class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get(reverse('auth.register'))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        form_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'birth_date': timezone.now().date(),
            'first_name': 'Test',
            'last_name': 'User',
            'gender': 'Male',
            'is_accepted_terms': True
        }
        response = self.client.post(reverse('auth.register'), form_data)
        self.assertEqual(response.status_code, 302)

class CustomLoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        response = self.client.get(reverse('auth.login'))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        form_data = {'username': 'test@example.com', 'password': 'TestPass123!'}
        response = self.client.post(reverse('auth.login'), form_data)
        self.assertEqual(response.status_code, 302)

class VerifyLoginOTPViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        response = self.client.get(reverse('verify_login_otp'))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        form_data = {'otp': '123456'}
        response = self.client.post(reverse('verify_login_otp'), form_data)
        self.assertEqual(response.status_code, 200)

class CustomLogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        response = self.client.get(reverse('auth.logout'))
        self.assertEqual(response.status_code, 302)

class ProcessAccountVerificationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        response = self.client.get(reverse('process_account_verification', kwargs={'uidb64': 'test', 'token': 'test'}))
        self.assertEqual(response.status_code, 200)

class ResendVerificationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        response = self.client.get(reverse('resend_verification'))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        form_data = {'email': 'test@example.com'}
        response = self.client.post(reverse('resend_verification'), form_data)
        self.assertEqual(response.status_code, 200)
