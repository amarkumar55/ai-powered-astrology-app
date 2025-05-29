from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from .forms import ProfileForm, AccountDeleteForm, DisableTwoFactorForm, Enable2FAForm, VerifyOTPForm, VerifyEmailChangeForm, VerifyEmailChangeOTP
from .views import ProfileUpdateView, AccountDeleteView, DisableTwoFactorView, EnableTwoFactorView, VerifyTwoFactorOTPView, change_email_view, SendOTPForEmailChangeView, VerifyOTPForEmailChangeView

User = get_user_model()

# View Tests
class ProfileUpdateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        response = self.client.get(reverse('dashboard.get_profile'))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        form_data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'username': 'updateduser',
            'gender': 'Male',
            'day': 1,
            'month': 1,
            'year': 2000,
            'hours': 12,
            'minutes': 0,
            'seconds': 0,
            'time_format': 'AM',
            'place': 'Updated Place',
            'timezone': 'UTC',
            'notification_preference': True,
            'password': 'TestPass123!'
        }
        response = self.client.post(reverse('dashboard.get_profile'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update

class AccountDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        response = self.client.get(reverse('dashboard.delete_account'))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        form_data = {
            'password': 'TestPass123!',
            'delete_type': 'temp'
        }
        response = self.client.post(reverse('dashboard.delete_account'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion

class DisableTwoFactorViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        response = self.client.get(reverse('dashboard.disable_2fa'))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        form_data = {
            'password': 'TestPass123!'
        }
        response = self.client.post(reverse('dashboard.disable_2fa'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful disable

class EnableTwoFactorViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        response = self.client.get(reverse('dashboard.enable_2fa'))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        form_data = {
            'email': 'test@example.com'
        }
        response = self.client.post(reverse('dashboard.enable_2fa'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful enable

class VerifyTwoFactorOTPViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_post(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        form_data = {
            'email_otp': '123456'
        }
        response = self.client.post(reverse('dashboard.verify_2fa_otp'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful verification

class ChangeEmailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        response = self.client.get(reverse('dashboard.change_email'))
        self.assertEqual(response.status_code, 200)

class SendOTPForEmailChangeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_post(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        form_data = {
            'old_email': 'test@example.com',
            'new_email': 'new@example.com',
            'password': 'TestPass123!'
        }
        response = self.client.post(reverse('dashboard.send_otp_for_email_change'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful OTP send

class VerifyOTPForEmailChangeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_post(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        form_data = {
            'old_email': 'test@example.com',
            'new_email': 'new@example.com',
            'old_email_otp': '123456',
            'new_email_otp': '123456'
        }
        response = self.client.post(reverse('dashboard.verify_otp_for_email_change'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful verification

# Form Tests
class ProfileFormTest(TestCase):
    def test_clean_profile(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'gender': 'Male',
            'day': 1,
            'month': 1,
            'year': 2000,
            'hours': 12,
            'minutes': 0,
            'seconds': 0,
            'time_format': 'AM',
            'place': 'Test Place',
            'timezone': 'UTC',
            'notification_preference': True,
            'password': 'TestPass123!'
        }
        form = ProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

class AccountDeleteFormTest(TestCase):
    def test_clean_password(self):
        form_data = {
            'password': 'TestPass123!',
            'delete_type': 'temp'
        }
        form = AccountDeleteForm(data=form_data)
        self.assertTrue(form.is_valid())

class DisableTwoFactorFormTest(TestCase):
    def test_clean_password(self):
        form_data = {
            'password': 'TestPass123!'
        }
        form = DisableTwoFactorForm(data=form_data)
        self.assertTrue(form.is_valid())

class Enable2FAFormTest(TestCase):
    def test_clean_email(self):
        form_data = {
            'email': 'test@example.com'
        }
        form = Enable2FAForm(data=form_data)
        self.assertTrue(form.is_valid())

class VerifyOTPFormTest(TestCase):
    def test_clean_email_otp(self):
        form_data = {
            'email_otp': '123456'
        }
        form = VerifyOTPForm(data=form_data)
        self.assertTrue(form.is_valid())

class VerifyEmailChangeFormTest(TestCase):
    def test_clean_old_email(self):
        form_data = {
            'old_email': 'test@example.com',
            'new_email': 'new@example.com',
            'password': 'TestPass123!'
        }
        form = VerifyEmailChangeForm(data=form_data)
        self.assertTrue(form.is_valid())

class VerifyEmailChangeOTPTest(TestCase):
    def test_clean_old_email_otp(self):
        form_data = {
            'old_email': 'test@example.com',
            'new_email': 'new@example.com',
            'old_email_otp': '123456',
            'new_email_otp': '123456'
        }
        form = VerifyEmailChangeOTP(data=form_data)
        self.assertTrue(form.is_valid())
