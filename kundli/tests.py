from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Location, KundliReport
from .forms import KundliForm
from .views import KundliPreditionView, KundliPremiumView, KundliPaymentProcessView, KundliPremiumDownloadView, KundliDownloadView, SearchLocationView

User = get_user_model()

# Model Tests
class LocationModelTest(TestCase):
    def setUp(self):
        self.location = Location.objects.create(place='Test Place', latitude=10.0, longitude=20.0)

    def test_location_creation(self):
        self.assertEqual(self.location.place, 'Test Place')
        self.assertEqual(self.location.latitude, 10.0)
        self.assertEqual(self.location.longitude, 20.0)

class KundliReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)
        self.kundli_report = KundliReport.objects.create(
            user=self.user,
            name='Test Kundli',
            place='Test Place',
            birth_details=None,  # Assuming BirthDetails is a related model
            ascendant='Test Ascendant',
            asc_deg=10.0,
            asc_sign='Test Sign',
            birth_sign='Test Birth Sign',
            lagna_chart={},
            chart_url='http://example.com',
            nakshatra='Test Nakshatra',
            ganra='Test Ganra',
            nadi='Test Nadi',
            yoni='Test Yoni',
            varna='Test Varna',
            houses={},
            planet_positions={},
            planets_longitudes={},
            planet_house_map={},
            sade_sati_result={},
            sade_sati_phases={},
            kundli_data={},
            manglik_dosha=False,
            kaal_sarp_dosha=False,
            mahapurush_yogas={},
            gaja_kesari_yoga=False,
            budha_aditya_yoga=False,
            pitra_dosha={}
        )

    def test_kundli_report_creation(self):
        self.assertEqual(self.kundli_report.user, self.user)
        self.assertEqual(self.kundli_report.name, 'Test Kundli')
        self.assertEqual(self.kundli_report.place, 'Test Place')
        self.assertEqual(self.kundli_report.ascendant, 'Test Ascendant')
        self.assertEqual(self.kundli_report.asc_deg, 10.0)
        self.assertEqual(self.kundli_report.asc_sign, 'Test Sign')
        self.assertEqual(self.kundli_report.birth_sign, 'Test Birth Sign')
        self.assertEqual(self.kundli_report.chart_url, 'http://example.com')
        self.assertEqual(self.kundli_report.nakshatra, 'Test Nakshatra')
        self.assertEqual(self.kundli_report.ganra, 'Test Ganra')
        self.assertEqual(self.kundli_report.nadi, 'Test Nadi')
        self.assertEqual(self.kundli_report.yoni, 'Test Yoni')
        self.assertEqual(self.kundli_report.varna, 'Test Varna')
        self.assertFalse(self.kundli_report.manglik_dosha)
        self.assertFalse(self.kundli_report.kaal_sarp_dosha)
        self.assertFalse(self.kundli_report.gaja_kesari_yoga)
        self.assertFalse(self.kundli_report.budha_aditya_yoga)

# Form Tests
class KundliFormTest(TestCase):
    def test_clean_first_name(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'days': 1,
            'months': 1,
            'years': 2000,
            'hours': 12,
            'minutes': 0,
            'seconds': 0,
            'time_format': 'AM',
            'is_accepted_terms': True,
            'place': 'Test Place'
        }
        form = KundliForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean_last_name(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'days': 1,
            'months': 1,
            'years': 2000,
            'hours': 12,
            'minutes': 0,
            'seconds': 0,
            'time_format': 'AM',
            'is_accepted_terms': True,
            'place': 'Test Place'
        }
        form = KundliForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean_place(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'days': 1,
            'months': 1,
            'years': 2000,
            'hours': 12,
            'minutes': 0,
            'seconds': 0,
            'time_format': 'AM',
            'is_accepted_terms': True,
            'place': 'Test Place'
        }
        form = KundliForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean_latitude(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'days': 1,
            'months': 1,
            'years': 2000,
            'hours': 12,
            'minutes': 0,
            'seconds': 0,
            'time_format': 'AM',
            'is_accepted_terms': True,
            'place': 'Test Place',
            'latitude': 10.0
        }
        form = KundliForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean_longitude(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'days': 1,
            'months': 1,
            'years': 2000,
            'hours': 12,
            'minutes': 0,
            'seconds': 0,
            'time_format': 'AM',
            'is_accepted_terms': True,
            'place': 'Test Place',
            'longitude': 20.0
        }
        form = KundliForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'days': 1,
            'months': 1,
            'years': 2000,
            'hours': 12,
            'minutes': 0,
            'seconds': 0,
            'time_format': 'AM',
            'is_accepted_terms': True,
            'place': 'Test Place'
        }
        form = KundliForm(data=form_data)
        self.assertTrue(form.is_valid())

# View Tests
class KundliPreditionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        response = self.client.get(reverse('kundli.prediction'))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'days': 1,
            'months': 1,
            'years': 2000,
            'hours': 12,
            'minutes': 0,
            'seconds': 0,
            'time_format': 'AM',
            'is_accepted_terms': True,
            'place': 'Test Place'
        }
        response = self.client.post(reverse('kundli.prediction'), form_data)
        self.assertEqual(response.status_code, 200)

class KundliPremiumViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        response = self.client.get(reverse('kundli.premium_analysis'))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'days': 1,
            'months': 1,
            'years': 2000,
            'hours': 12,
            'minutes': 0,
            'seconds': 0,
            'time_format': 'AM',
            'is_accepted_terms': True,
            'place': 'Test Place'
        }
        response = self.client.post(reverse('kundli.premium_analysis'), form_data)
        self.assertEqual(response.status_code, 200)

class KundliPaymentProcessViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        response = self.client.get(reverse('kundli.premium_payment'))
        self.assertEqual(response.status_code, 200)

class KundliPremiumDownloadViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        response = self.client.get(reverse('kundli.premium_download'))
        self.assertEqual(response.status_code, 200)

class KundliDownloadViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        response = self.client.get(reverse('kundli.download', kwargs={'kundli_id': 1}))
        self.assertEqual(response.status_code, 200)

class SearchLocationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)

    def test_get(self):
        self.client.login(username='test@example.com', password='TestPass123!')
        response = self.client.get(reverse('kundli.search_location'))
        self.assertEqual(response.status_code, 200)
