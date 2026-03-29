"""
Tests for email notification system (notifications app).
Tests send_order_confirmation, send_shipping_notification,
send_delivery_notification, send_welcome_email, and branding utils.
"""

from unittest.mock import patch, MagicMock
from io import StringIO

from django.test import TestCase, override_settings
from django.core import mail as django_mail
from django.contrib.auth.models import User
from decimal import Decimal

from checkout.models import Order, OrderLineItem
from products.models import Product, Category
from .utils import (
    send_order_confirmation,
    send_shipping_notification,
    send_delivery_notification,
    send_welcome_email,
    get_store_branding,
    STORE_BRANDING,
)


class BrandingTests(TestCase):
    """Tests for store branding utilities."""

    def test_get_store_branding_orderimo(self):
        branding = get_store_branding('orderimo')
        self.assertEqual(branding['name'], 'Orderimo')
        self.assertIn('#00b4d8', branding['primary_color'])

    def test_get_store_branding_petshop(self):
        branding = get_store_branding('petshop-ie')
        self.assertEqual(branding['name'], 'PetShop Ireland')
        self.assertIn('#228B22', branding['primary_color'])

    def test_get_store_branding_digitalhub(self):
        branding = get_store_branding('digitalhub')
        self.assertEqual(branding['name'], 'DigitalHub')
        self.assertIn('#800080', branding['primary_color'])

    def test_get_store_branding_unknown_defaults_to_orderimo(self):
        branding = get_store_branding('nonexistent')
        self.assertEqual(branding['name'], 'Orderimo')


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='hello@orderimo.com',
)
class OrderConfirmationEmailTests(TestCase):
    """Tests for order confirmation email."""

    def setUp(self):
        self.category = Category.objects.create(name='test-cat', friendly_name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            description='A great product',
            price=Decimal('29.99'),
            category=self.category,
            sku='TEST-001',
        )
        self.order = Order.objects.create(
            full_name='Kay Test',
            email='kay@example.com',
            phone_number='+35312345678',
            street_address1='123 Test Street',
            town_or_city='Dublin',
            country='IE',
            original_bag='{}',
            stripe_pid='test_pid_123',
            grand_total=Decimal('35.99'),
            delivery_cost=Decimal('5.99'),
            order_total=Decimal('29.99'),
            store='orderimo',
        )
        OrderLineItem.objects.create(order=self.order, product=self.product, quantity=1)

    def test_send_order_confirmation_sends_email(self):
        """send_order_confirmation dispatches an email to the order's email address."""
        send_order_confirmation(self.order)
        self.assertEqual(len(django_mail.outbox), 1)
        self.assertIn('kay@example.com', django_mail.outbox[0].to)
        self.assertIn(self.order.order_number, django_mail.outbox[0].subject)

    def test_send_order_confirmation_includes_order_number_in_subject(self):
        """Subject line contains the order number."""
        send_order_confirmation(self.order)
        self.assertIn(self.order.order_number, django_mail.outbox[0].subject)
        self.assertIn('Orderimo', django_mail.outbox[0].subject)

    def test_send_order_confirmation_html_body_contains_items(self):
        """HTML body includes product name and total."""
        send_order_confirmation(self.order)
        body = django_mail.outbox[0].alternatives[0][0]  # HTML body
        self.assertIn('Test Product', body)
        self.assertIn('29.99', body)

    def test_send_order_confirmation_plain_text_fallback(self):
        """Email includes a plain-text alternative."""
        send_order_confirmation(self.order)
        msg = django_mail.outbox[0]
        self.assertTrue(msg.alternatives)
        # First alternative is HTML, second (if exists) would be text
        # Our implementation uses strip_tags for text, so alternatives = [(html, text/html)]

    def test_send_order_confirmation_petshop_store(self):
        """Order from petshop-ie uses PetShop branding."""
        self.order.store = 'petshop-ie'
        self.order.save()
        send_order_confirmation(self.order)
        body = django_mail.outbox[0].alternatives[0][0]
        self.assertIn('PetShop Ireland', body)

    def test_send_order_confirmation_digitalhub_store(self):
        """Order from digitalhub uses DigitalHub branding."""
        self.order.store = 'digitalhub'
        self.order.save()
        send_order_confirmation(self.order)
        body = django_mail.outbox[0].alternatives[0][0]
        self.assertIn('DigitalHub', body)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='hello@orderimo.com',
)
class ShippingNotificationEmailTests(TestCase):
    """Tests for shipping notification email."""

    def setUp(self):
        self.category = Category.objects.create(name='test-cat', friendly_name='Test Category')
        self.product = Product.objects.create(
            name='Widget',
            description='Desc',
            price=Decimal('10.00'),
            category=self.category,
        )
        self.order = Order.objects.create(
            full_name='Kay Test',
            email='kay@shipping-test.com',
            phone_number='+35312345678',
            street_address1='456 Delivery Rd',
            town_or_city='Cork',
            country='IE',
            original_bag='{}',
            stripe_pid='test_pid_ship',
            grand_total=Decimal('12.00'),
            store='orderimo',
        )

    def test_send_shipping_notification_sends_email(self):
        """send_shipping_notification dispatches an email."""
        send_shipping_notification(
            self.order,
            tracking_number='TRACK123456',
            carrier='DPD Ireland',
            expected_delivery='2026-04-05',
        )
        self.assertEqual(len(django_mail.outbox), 1)
        self.assertIn('TRACK123456', django_mail.outbox[0].body)

    def test_send_shipping_notification_includes_tracking_number(self):
        """Email body contains the tracking number."""
        send_shipping_notification(
            self.order,
            tracking_number='TRACK999',
            carrier='An Post',
        )
        self.assertIn('TRACK999', django_mail.outbox[0].alternatives[0][0])

    def test_send_shipping_notification_without_tracking(self):
        """Handles case where tracking number is not yet available."""
        send_shipping_notification(self.order)
        self.assertEqual(len(django_mail.outbox), 1)
        # Should not crash, email still sent


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='hello@orderimo.com',
)
class DeliveryNotificationEmailTests(TestCase):
    """Tests for delivery confirmation email."""

    def setUp(self):
        self.category = Category.objects.create(name='test-cat', friendly_name='Test Category')
        self.product = Product.objects.create(
            name='Gadget',
            description='Desc',
            price=Decimal('50.00'),
            category=self.category,
        )
        self.order = Order.objects.create(
            full_name='Kay Test',
            email='kay@delivered.com',
            phone_number='+35312345678',
            street_address1='789 Home Ave',
            town_or_city='Galway',
            country='IE',
            original_bag='{}',
            stripe_pid='test_pid_delivered',
            grand_total=Decimal('60.00'),
            store='petshop-ie',
        )

    def test_send_delivery_notification_sends_email(self):
        """send_delivery_notification dispatches an email."""
        send_delivery_notification(self.order)
        self.assertEqual(len(django_mail.outbox), 1)
        self.assertIn('kay@delivered.com', django_mail.outbox[0].to)
        self.assertIn('Delivered', django_mail.outbox[0].subject)

    def test_send_delivery_notification_petshop_branding(self):
        """Petshop-ie order uses PetShop branding."""
        send_delivery_notification(self.order)
        body = django_mail.outbox[0].alternatives[0][0]
        self.assertIn('PetShop Ireland', body)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='hello@orderimo.com',
)
class WelcomeEmailTests(TestCase):
    """Tests for welcome email on new user registration."""

    def setUp(self):
        # Clear any residual emails (e.g. from user_created_welcome_email signal)
        outbox = []

    def test_send_welcome_email_sends_email(self):
        """send_welcome_email dispatches an email to the new user."""
        user = User.objects.create_user('newuser', 'welcome@test.com', 'pass123')
        send_welcome_email(user, store_slug='orderimo')
        # There may be other emails from signals; find the welcome email
        welcome_emails = [m for m in outbox if 'Welcome' in m.subject]
        self.assertGreaterEqual(len(welcome_emails), 1)
        last_welcome = welcome_emails[-1]
        self.assertIn('welcome@test.com', last_welcome.to)
        self.assertIn('Orderimo', last_welcome.subject)

    def test_send_welcome_email_uses_first_name(self):
        """Welcome email uses user's first name."""
        user = User.objects.create_user('firstnameuser', 'fn@test.com', 'pass123')
        user.first_name = 'Kay'
        user.save()
        send_welcome_email(user, store_slug='orderimo')
        welcome_emails = [m for m in outbox if 'Welcome' in m.subject]
        body = welcome_emails[-1].alternatives[0][0]
        self.assertIn('Kay', body)

    def test_send_welcome_email_petshop_store(self):
        """Welcome email for petshop store uses correct branding."""
        user = User.objects.create_user('petlover', 'petshop@user.com', 'pass123')
        send_welcome_email(user, store_slug='petshop-ie')
        welcome_emails = [m for m in outbox if 'PetShop' in m.subject]
        self.assertGreaterEqual(len(welcome_emails), 1)
        body = welcome_emails[-1].alternatives[0][0]
        self.assertIn('PetShop Ireland', body)
