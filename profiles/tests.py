"""
Comprehensive tests for the profiles app.
Tests UserProfile model, form, and views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from .models import UserProfile
from .forms import UserProfileForm


class UserProfileModelTests(TestCase):
    """Tests for UserProfile model."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')

    def test_user_profile_created_on_user_creation(self):
        """Signal should auto-create profile when user is created."""
        self.assertTrue(hasattr(self.user, 'userprofile'))
        self.assertEqual(str(self.user.userprofile), 'testuser')

    def test_user_profile_str(self):
        self.assertEqual(str(self.user.userprofile), self.user.username)

    def test_user_profile_optional_fields(self):
        # The signal already created a profile for this user
        profile = self.user.userprofile
        # All fields should be nullable/blank=True — no errors
        self.assertIsNone(profile.default_phone_number)
        # CountryField returns Country(code=None) when empty, not Python None
        self.assertEqual(str(profile.default_country), '')


class UserProfileFormTests(TestCase):
    """Tests for UserProfileForm."""

    def setUp(self):
        self.user = User.objects.create_user('formuser', 'form@test.com', 'pass123')

    def test_form_valid_partial_data(self):
        form = UserProfileForm(data={
            'default_phone_number': '+123456',
            'default_town_or_city': 'Dublin',
        })
        self.assertTrue(form.is_valid())

    def test_form_all_fields(self):
        form = UserProfileForm(data={
            'default_phone_number': '+123456',
            'default_street_address1': '123 Main St',
            'default_street_address2': 'Apt 2',
            'default_town_or_city': 'Dublin',
            'default_county': 'Co. Dublin',
            'default_country': 'IE',
            'default_postcode': 'D01 AB12',
        })
        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_form_excludes_user_field(self):
        form = UserProfileForm()
        # 'user' field should not be in the form fields
        self.assertNotIn('user', form.fields)


class ProfileViewTests(TestCase):
    """Tests for profile views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('shopper', 'shop@test.com', 'shoppass123')
        self.superuser = User.objects.create_superuser('admin', 'admin@test.com', 'adminpass')
        self.profile_url = reverse('profile')

    def test_profile_requires_login(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)

    def test_profile_view_logged_in(self):
        self.client.login(username='shopper', password='shoppass123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)

    def test_profile_view_has_form(self):
        self.client.login(username='shopper', password='shoppass123')
        response = self.client.get(self.profile_url)
        self.assertIn('form', response.context)

    def test_profile_update_post(self):
        self.client.login(username='shopper', password='shoppass123')
        response = self.client.post(self.profile_url, data={
            'default_phone_number': '+35387123456',
            'default_street_address1': '123 Test Street',
            'default_town_or_city': 'Dublin',
            'default_postcode': 'D01',
        })
        self.assertEqual(response.status_code, 200)
        self.user.userprofile.refresh_from_db()
        self.assertEqual(self.user.userprofile.default_phone_number, '+35387123456')
        self.assertEqual(self.user.userprofile.default_town_or_city, 'Dublin')

    def test_profile_shows_order_history_for_user(self):
        # Profile should show order history (tested by checking context)
        self.client.login(username='shopper', password='shoppass123')
        response = self.client.get(self.profile_url)
        self.assertIn('orders', response.context)
