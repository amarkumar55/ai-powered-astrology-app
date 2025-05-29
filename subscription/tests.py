from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Feature, Plan, UserSubscription, UserFeatureUsage, UserTransaction

User = get_user_model()

# Model Tests
class FeatureModelTest(TestCase):
    def setUp(self):
        self.feature = Feature.objects.create(name='Test Feature', qty=10, is_active=True)

    def test_feature_creation(self):
        self.assertEqual(self.feature.name, 'Test Feature')
        self.assertEqual(self.feature.qty, 10)
        self.assertTrue(self.feature.is_active)

    def test_feature_string_representation(self):
        self.assertEqual(str(self.feature), 'Test Feature - 10')

class PlanModelTest(TestCase):
    def setUp(self):
        self.plan = Plan.objects.create(name='Test Plan', description='Test Description', price=100.00, duration_days=30)

    def test_plan_creation(self):
        self.assertEqual(self.plan.name, 'Test Plan')
        self.assertEqual(self.plan.description, 'Test Description')
        self.assertEqual(self.plan.price, 100.00)
        self.assertEqual(self.plan.duration_days, 30)

class UserSubscriptionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)
        self.plan = Plan.objects.create(name='Test Plan', description='Test Description', price=100.00, duration_days=30)
        self.subscription = UserSubscription.objects.create(user=self.user, plan=self.plan, end_date=timezone.now() + timezone.timedelta(days=30), status='active')

    def test_subscription_creation(self):
        self.assertEqual(self.subscription.user, self.user)
        self.assertEqual(self.subscription.plan, self.plan)
        self.assertEqual(self.subscription.status, 'active')

    def test_subscription_string_representation(self):
        self.assertEqual(str(self.subscription), f"{self.user} - {self.plan.name} (active)")

class UserFeatureUsageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)
        self.plan = Plan.objects.create(name='Test Plan', description='Test Description', price=100.00, duration_days=30)
        self.subscription = UserSubscription.objects.create(user=self.user, plan=self.plan, end_date=timezone.now() + timezone.timedelta(days=30), status='active')
        self.feature = Feature.objects.create(name='Test Feature', qty=10, is_active=True)
        self.feature_usage = UserFeatureUsage.objects.create(subscription=self.subscription, feature=self.feature, remain_quantity=5)

    def test_feature_usage_creation(self):
        self.assertEqual(self.feature_usage.subscription, self.subscription)
        self.assertEqual(self.feature_usage.feature, self.feature)
        self.assertEqual(self.feature_usage.remain_quantity, 5)

class UserTransactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)
        self.transaction = UserTransaction.objects.create(user=self.user, payment_method='Credit Card', transaction_id='test_transaction_id', amount=100.00, status='Success')

    def test_transaction_creation(self):
        self.assertEqual(self.transaction.user, self.user)
        self.assertEqual(self.transaction.payment_method, 'Credit Card')
        self.assertEqual(self.transaction.transaction_id, 'test_transaction_id')
        self.assertEqual(self.transaction.amount, 100.00)
        self.assertEqual(self.transaction.status, 'Success')

    def test_transaction_string_representation(self):
        self.assertEqual(str(self.transaction), 'test_transaction_id - Success')
