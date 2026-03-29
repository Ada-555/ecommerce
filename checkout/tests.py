"""
Comprehensive tests for the checkout app.
Tests forms, models, and views.
"""

from unittest.mock import patch, MagicMock

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from decimal import Decimal

from products.models import Product, Category
from profiles.models import UserProfile
from .models import Order, OrderLineItem
from .forms import OrderForm


class OrderModelTests(TestCase):
    """Tests for Order and OrderLineItem models."""

    def setUp(self):
        self.category = Category.objects.create(name='c', friendly_name='C')
        self.product = Product.objects.create(
            name='Test Product',
            description='Desc',
            price=Decimal('25.00'),
            category=self.category,
        )

    def test_order_number_auto_generated(self):
        order = Order.objects.create(
            full_name='Kay',
            email='kay@test.com',
            phone_number='+123456',
            street_address1='123 Main St',
            town_or_city='Dublin',
            country='IE',
            original_bag='{}',
            stripe_pid='test_pid',
        )
        self.assertIsNotNone(order.order_number)
        self.assertEqual(len(order.order_number), 32)  # UUID4 hex upper

    def test_order_str_is_order_number(self):
        order = Order.objects.create(
            full_name='Kay',
            email='kay@test.com',
            phone_number='+123456',
            street_address1='123 Main St',
            town_or_city='Dublin',
            country='IE',
            original_bag='{}',
            stripe_pid='test_pid',
        )
        self.assertEqual(str(order), order.order_number)

    def test_order_update_total_no_delivery(self):
        """Order over free delivery threshold has no delivery cost."""
        order = Order.objects.create(
            full_name='Kay',
            email='kay@test.com',
            phone_number='+123456',
            street_address1='123 Main St',
            town_or_city='Dublin',
            country='IE',
            original_bag='{}',
            stripe_pid='test_pid',
            order_total=Decimal('100.00'),
        )
        OrderLineItem.objects.create(order=order, product=self.product, quantity=4)
        order.update_total()
        self.assertEqual(order.delivery_cost, Decimal('0.00'))
        self.assertEqual(order.grand_total, Decimal('100.00'))

    def test_order_update_total_with_delivery(self):
        """Order under threshold gets 20% delivery charge."""
        order = Order.objects.create(
            full_name='Kay',
            email='kay@test.com',
            phone_number='+123456',
            street_address1='123 Main St',
            town_or_city='Dublin',
            country='IE',
            original_bag='{}',
            stripe_pid='test_pid',
            order_total=Decimal('50.00'),
        )
        OrderLineItem.objects.create(order=order, product=self.product, quantity=2)
        order.update_total()
        self.assertEqual(order.delivery_cost, Decimal('10.00'))  # 20% of 50
        self.assertEqual(order.grand_total, Decimal('60.00'))

    def test_order_lineitem_total_auto_calculated(self):
        order = Order.objects.create(
            full_name='Kay',
            email='kay@test.com',
            phone_number='+123456',
            street_address1='123 Main St',
            town_or_city='Dublin',
            country='IE',
            original_bag='{}',
            stripe_pid='test_pid',
        )
        item = OrderLineItem.objects.create(
            order=order,
            product=self.product,
            quantity=3,
        )
        self.assertEqual(item.lineitem_total, Decimal('75.00'))  # 3 x 25


class OrderFormTests(TestCase):
    """Tests for OrderForm."""

    def test_order_form_valid(self):
        form = OrderForm(data={
            'full_name': 'Kay Smith',
            'email': 'kay@example.com',
            'phone_number': '+3531234567',
            'street_address1': '123 Test St',
            'town_or_city': 'Dublin',
            'country': 'IE',
            'postcode': 'D01 AB12',
        })
        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_order_form_missing_required_fields(self):
        form = OrderForm(data={})
        self.assertFalse(form.is_valid())
        required_fields = ['full_name', 'email', 'phone_number',
                          'street_address1', 'town_or_city', 'country']
        for field in required_fields:
            self.assertIn(field, form.errors)

    def test_order_form_invalid_email(self):
        form = OrderForm(data={
            'full_name': 'Kay',
            'email': 'not-an-email',
            'phone_number': '123',
            'street_address1': '123 St',
            'town_or_city': 'Dublin',
            'country': 'IE',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class CheckoutViewTests(TestCase):
    """Tests for checkout view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('shopper', 'shop@test.com', 'pass123')
        self.category = Category.objects.create(name='c', friendly_name='C')
        self.product = Product.objects.create(
            name='Product',
            description='Desc',
            price=Decimal('25.00'),
            category=self.category,
        )
        self.checkout_url = reverse('checkout')

    def test_checkout_view_empty_bag_redirects(self):
        response = self.client.get(self.checkout_url)
        self.assertEqual(response.status_code, 302)
        # Empty bag redirects to products page
        self.assertRedirects(response, reverse('products'))

    @patch('checkout.views.stripe.PaymentIntent.create')
    def test_checkout_view_with_bag(self, mock_stripe):
        mock_stripe.return_value = MagicMock(client_secret='test_secret_test')
        # Add to bag
        self.client.post(
            reverse('add_to_bag', args=[self.product.id]),
            data={'quantity': 1, 'redirect_url': '/'},
        )
        response = self.client.get(self.checkout_url)
        self.assertEqual(response.status_code, 200)

    @patch('checkout.views.stripe.PaymentIntent.create')
    def test_checkout_view_has_order_form(self, mock_stripe):
        mock_stripe.return_value = MagicMock(client_secret='test_secret_test')
        self.client.post(
            reverse('add_to_bag', args=[self.product.id]),
            data={'quantity': 1, 'redirect_url': '/'},
        )
        response = self.client.get(self.checkout_url)
        self.assertIn('order_form', response.context)

    @patch('checkout.views.stripe.PaymentIntent.create')
    def test_checkout_view_stripe_public_key_missing_warning(self, mock_stripe):
        mock_stripe.return_value = MagicMock(client_secret='test_secret_test')
        self.client.post(
            reverse('add_to_bag', args=[self.product.id]),
            data={'quantity': 1, 'redirect_url': '/'},
        )
        # Stripe key not set in test env
        response = self.client.get(self.checkout_url)
        self.assertIn('messages', response.context)


class CheckoutSuccessTests(TestCase):
    """Tests for checkout success view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('shopper', 'shop@test.com', 'pass123')
        self.order = Order.objects.create(
            full_name='Kay',
            email='kay@test.com',
            phone_number='+123456',
            street_address1='123 Main St',
            town_or_city='Dublin',
            country='IE',
            original_bag='{}',
            stripe_pid='test_pid_abc123',
            grand_total=Decimal('25.00'),
        )
        self.success_url = reverse('checkout_success', args=[self.order.order_number])

    def test_checkout_success_get(self):
        response = self.client.get(self.success_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.order_number)

    def test_checkout_success_404_for_unknown_order(self):
        response = self.client.get(reverse('checkout_success', args=['nonexistent']))
        self.assertEqual(response.status_code, 404)
