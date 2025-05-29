from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import UserPanchang, Panchang

User = get_user_model()

# Model Tests
class UserPanchangModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user_panchang = UserPanchang.objects.create(
            first_name='John',
            last_name='Doe',
            user=self.user,
            date_of_birth=timezone.now().date(),
            time_of_birth=timezone.now().time(),
            place='New York',
            latitude=40.7128,
            longitude=-74.0060,
            tithi='Shukla Paksha',
            nakshatra='Rohini',
            yoga='Shiva',
            karana='Bava',
            vara='Monday',
            sunrise=timezone.now().time(),
            sunset=timezone.now().time(),
            rahu_kaal='10:00 AM - 11:30 AM',
            gulika_kaal='12:00 PM - 1:30 PM',
            yamaganda='3:00 PM - 4:30 PM',
            abhijit_muhurat='11:30 AM - 12:00 PM'
        )

    def test_user_panchang_creation(self):
        self.assertEqual(self.user_panchang.first_name, 'John')
        self.assertEqual(self.user_panchang.last_name, 'Doe')
        self.assertEqual(self.user_panchang.place, 'New York')
        self.assertEqual(self.user_panchang.tithi, 'Shukla Paksha')
        self.assertEqual(self.user_panchang.nakshatra, 'Rohini')
        self.assertEqual(self.user_panchang.yoga, 'Shiva')
        self.assertEqual(self.user_panchang.karana, 'Bava')
        self.assertEqual(self.user_panchang.vara, 'Monday')

    def test_user_panchang_string_representation(self):
        self.assertEqual(str(self.user_panchang), f"Panchang for {self.user_panchang.first_name} {self.user_panchang.last_name} on {self.user_panchang.date_of_birth}")

class PanchangModelTest(TestCase):
    def setUp(self):
        self.panchang = Panchang.objects.create(
            date=timezone.now().date(),
            tithi='Shukla Paksha',
            vara='Monday',
            nakshatra='Rohini',
            yoga='Shiva',
            karana='Bava',
            sunrise=timezone.now().time(),
            sunset=timezone.now().time(),
            rahu_kaal='10:00 AM - 11:30 AM',
            gulika_kaal='12:00 PM - 1:30 PM',
            yamaganda='3:00 PM - 4:30 PM',
            abhijit_muhurat='11:30 AM - 12:00 PM'
        )

    def test_panchang_creation(self):
        self.assertEqual(self.panchang.tithi, 'Shukla Paksha')
        self.assertEqual(self.panchang.vara, 'Monday')
        self.assertEqual(self.panchang.nakshatra, 'Rohini')
        self.assertEqual(self.panchang.yoga, 'Shiva')
        self.assertEqual(self.panchang.karana, 'Bava')

    def test_panchang_string_representation(self):
        self.assertEqual(str(self.panchang), f"Panchang for {self.panchang.date}")
