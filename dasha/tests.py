from django.test import TestCase
from django.utils import timezone
from .models import BirthDetails, AntarDasha, PlanetaryPosition, MoonPosition, DashaEffect

# Model Tests
class BirthDetailsModelTest(TestCase):
    def setUp(self):
        self.birth_details = BirthDetails.objects.create(
            birth_date=timezone.now().date(),
            birth_time=timezone.now().time(),
            latitude=28.6139,
            longitude=77.2090
        )

    def test_birth_details_creation(self):
        self.assertEqual(self.birth_details.birth_date, timezone.now().date())
        self.assertEqual(self.birth_details.birth_time, timezone.now().time())
        self.assertEqual(self.birth_details.latitude, 28.6139)
        self.assertEqual(self.birth_details.longitude, 77.2090)

    def test_birth_details_string_representation(self):
        self.assertEqual(str(self.birth_details), f"Birth: {self.birth_details.birth_date} {self.birth_details.birth_time} (Lat: {self.birth_details.latitude}, Lon: {self.birth_details.longitude})")

class AntarDashaModelTest(TestCase):
    def setUp(self):
        self.birth_details = BirthDetails.objects.create(
            birth_date=timezone.now().date(),
            birth_time=timezone.now().time(),
            latitude=28.6139,
            longitude=77.2090
        )
        self.antar_dasha = AntarDasha.objects.create(
            birth_details=self.birth_details,
            nakshatra='Rohini',
            major_dasha='Jupiter',
            remaining_years=5.0,
            antar_dasha_planet='Saturn',
            start_date=timezone.now().date(),
            end_date=timezone.now().date()
        )

    def test_antar_dasha_creation(self):
        self.assertEqual(self.antar_dasha.nakshatra, 'Rohini')
        self.assertEqual(self.antar_dasha.major_dasha, 'Jupiter')
        self.assertEqual(self.antar_dasha.remaining_years, 5.0)
        self.assertEqual(self.antar_dasha.antar_dasha_planet, 'Saturn')

    def test_antar_dasha_string_representation(self):
        self.assertEqual(str(self.antar_dasha), f"{self.antar_dasha.major_dasha} - {self.antar_dasha.antar_dasha_planet} ({self.antar_dasha.start_date} to {self.antar_dasha.end_date})")

class PlanetaryPositionModelTest(TestCase):
    def setUp(self):
        self.birth_details = BirthDetails.objects.create(
            birth_date=timezone.now().date(),
            birth_time=timezone.now().time(),
            latitude=28.6139,
            longitude=77.2090
        )
        self.planetary_position = PlanetaryPosition.objects.create(
            birth_details=self.birth_details,
            planet='Mars',
            speed=0.5,
            nakshatra='Mrigashira',
            rashi='Gemini'
        )

    def test_planetary_position_creation(self):
        self.assertEqual(self.planetary_position.planet, 'Mars')
        self.assertEqual(self.planetary_position.speed, 0.5)
        self.assertEqual(self.planetary_position.nakshatra, 'Mrigashira')
        self.assertEqual(self.planetary_position.rashi, 'Gemini')

    def test_planetary_position_string_representation(self):
        self.assertEqual(str(self.planetary_position), f"{self.planetary_position.planet} - {self.planetary_position.rashi} ({self.planetary_position.birth_details})")

class MoonPositionModelTest(TestCase):
    def setUp(self):
        self.birth_details = BirthDetails.objects.create(
            birth_date=timezone.now().date(),
            birth_time=timezone.now().time(),
            latitude=28.6139,
            longitude=77.2090
        )
        self.moon_position = MoonPosition.objects.create(
            birth_details=self.birth_details,
            moon_longitude=45.0,
            nakshatra='Rohini'
        )

    def test_moon_position_creation(self):
        self.assertEqual(self.moon_position.moon_longitude, 45.0)
        self.assertEqual(self.moon_position.nakshatra, 'Rohini')

    def test_moon_position_string_representation(self):
        self.assertEqual(str(self.moon_position), f"Moon: {self.moon_position.nakshatra} ({self.moon_position.birth_details})")

class DashaEffectModelTest(TestCase):
    def setUp(self):
        self.dasha_effect = DashaEffect.objects.create(
            mahadasha_planet='Jupiter',
            antar_dasha_planet='Saturn',
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            mahadasha_effect='Positive influence on career.',
            antardasha_effect='Challenges in personal life.',
            combined_effect='Overall balanced period.'
        )

    def test_dasha_effect_creation(self):
        self.assertEqual(self.dasha_effect.mahadasha_planet, 'Jupiter')
        self.assertEqual(self.dasha_effect.antar_dasha_planet, 'Saturn')
        self.assertEqual(self.dasha_effect.mahadasha_effect, 'Positive influence on career.')
        self.assertEqual(self.dasha_effect.antardasha_effect, 'Challenges in personal life.')
        self.assertEqual(self.dasha_effect.combined_effect, 'Overall balanced period.')