from django.test import TestCase
from django.utils import timezone
from dasha.models import BirthDetails
from .models import KundliMatching

# Model Tests
class KundliMatchingModelTest(TestCase):
    def setUp(self):
        self.boy_birth = BirthDetails.objects.create(
            birth_date=timezone.now().date(),
            birth_time=timezone.now().time(),
            latitude=28.6139,
            longitude=77.2090
        )
        self.girl_birth = BirthDetails.objects.create(
            birth_date=timezone.now().date(),
            birth_time=timezone.now().time(),
            latitude=28.6139,
            longitude=77.2090
        )
        self.kundli_matching = KundliMatching.objects.create(
            boy_birth=self.boy_birth,
            girl_birth=self.girl_birth,
            varna_score=75,
            vasha_score=80,
            tara_score=70,
            yoni_score=85,
            graha_maitry_score=90,
            gana_score=65,
            bhakoot_score=75,
            nadi_score=80
        )

    def test_kundli_matching_creation(self):
        self.assertEqual(self.kundli_matching.varna_score, 75)
        self.assertEqual(self.kundli_matching.vasha_score, 80)
        self.assertEqual(self.kundli_matching.tara_score, 70)
        self.assertEqual(self.kundli_matching.yoni_score, 85)
        self.assertEqual(self.kundli_matching.graha_maitry_score, 90)
        self.assertEqual(self.kundli_matching.gana_score, 65)
        self.assertEqual(self.kundli_matching.bhakoot_score, 75)
        self.assertEqual(self.kundli_matching.nadi_score, 80)
