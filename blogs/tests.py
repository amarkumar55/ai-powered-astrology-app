from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Blog

User = get_user_model()

# Model Tests
class BlogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='TestPass123!', first_name='Test', last_name='User', birth_date=timezone.now().date(), gender='Male', username='testuser', is_accepted_terms=True)
        self.blog = Blog.objects.create(
            publish_by=self.user,
            title='Test Blog',
            description='This is a test blog description.',
            is_published=True,
            published_at=timezone.now()
        )

    def test_blog_creation(self):
        self.assertEqual(self.blog.title, 'Test Blog')
        self.assertEqual(self.blog.description, 'This is a test blog description.')
        self.assertTrue(self.blog.is_published)
        self.assertIsNotNone(self.blog.published_at)

    def test_blog_string_representation(self):
        self.assertEqual(str(self.blog), 'Test Blog')
