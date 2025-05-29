from django.test import TestCase
from .models import ContactQuery

# Model Tests
class ContactQueryModelTest(TestCase):
    def setUp(self):
        self.contact_query = ContactQuery.objects.create(
            full_name='John Doe',
            email='john.doe@example.com',
            message='This is a test message.'
        )

    def test_contact_query_creation(self):
        self.assertEqual(self.contact_query.full_name, 'John Doe')
        self.assertEqual(self.contact_query.email, 'john.doe@example.com')
        self.assertEqual(self.contact_query.message, 'This is a test message.')

    def test_contact_query_string_representation(self):
        self.assertEqual(str(self.contact_query), f"{self.contact_query.full_name} - {self.contact_query.email}")
