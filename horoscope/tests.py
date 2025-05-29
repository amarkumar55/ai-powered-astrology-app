from django.test import TestCase
from django.utils import timezone
from .models import Horoscope

# Model Tests
class HoroscopeModelTest(TestCase):
    def setUp(self):
        self.horoscope = Horoscope.objects.create(
            sign='Aries',
            date=timezone.now().date(),
            type='daily',
            prediction='This is a test prediction for Aries.'
        )

    def test_horoscope_creation(self):
        self.assertEqual(self.horoscope.sign, 'Aries')
        self.assertEqual(self.horoscope.type, 'daily')
        self.assertEqual(self.horoscope.prediction, 'This is a test prediction for Aries.')

    def test_horoscope_string_representation(self):
        self.assertEqual(str(self.horoscope), f"Aries - Daily Horoscope ({self.horoscope.date})")
