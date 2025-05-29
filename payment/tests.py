from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from .views import kundli_payment_checkout, KundliPaymentHandler, subscription_payment_checkout, SubscriptionPaymentHandler

User = get_user_model()

# View Tests
class KundliPaymentCheckoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_post(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        form_data = {
            'country': 'India',
            'state': 'Maharashtra',
            'city': 'Mumbai',
            'pincode': '400001'
        }
        response = self.client.post(reverse('payment.kundli_payment_checkout'), form_data)
        self.assertEqual(response.status_code, 200)

class KundliPaymentHandlerTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_post(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        form_data = {
            'razorpay_payment_id': 'test_payment_id',
            'razorpay_order_id': 'test_order_id',
            'razorpay_signature': 'test_signature'
        }
        response = self.client.post(reverse('payment.kundli_payment_handler'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after payment handling

class SubscriptionPaymentCheckoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_post(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        form_data = {
            'country': 'India',
            'state': 'Maharashtra',
            'city': 'Mumbai',
            'pincode': '400001'
        }
        response = self.client.post(reverse('payment.subscription_payment_checkout'), form_data)
        self.assertEqual(response.status_code, 200)

class SubscriptionPaymentHandlerTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_post(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        form_data = {
            'razorpay_payment_id': 'test_payment_id',
            'razorpay_order_id': 'test_order_id',
            'razorpay_signature': 'test_signature'
        }
        response = self.client.post(reverse('payment.subscription_payment_handler'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after payment handling
