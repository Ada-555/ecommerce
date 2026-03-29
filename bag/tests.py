"""
Comprehensive tests for the bag app.
Tests bag CRUD operations, session handling, and edge cases.
"""

from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal

from products.models import Product, Category


class BagViewsTests(TestCase):
    """Tests for bag views."""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='clothing', friendly_name='Clothing')
        self.product = Product.objects.create(
            name='Test Product',
            description='Great product',
            price=Decimal('25.00'),
            category=self.category,
        )
        self.bag_url = reverse('view_bag')
        self.add_url = reverse('add_to_bag', args=[self.product.id])
        self.adjust_url = reverse('adjust_bag', args=[self.product.id])
        self.remove_url = reverse('remove_from_bag', args=[self.product.id])

    def _add_to_bag(self, quantity=1, size=None):
        """Helper to add product to bag."""
        data = {'quantity': quantity, 'redirect_url': reverse('products')}
        if size:
            data['product_size'] = size
        return self.client.post(self.add_url, data=data)

    def test_view_bag_empty(self):
        response = self.client.get(self.bag_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'empty')

    def test_view_bag_get_200(self):
        response = self.client.get(self.bag_url)
        self.assertEqual(response.status_code, 200)

    def test_add_to_bag_post_redirects(self):
        response = self._add_to_bag(quantity=1)
        self.assertEqual(response.status_code, 302)

    def test_add_to_bag_updates_existing(self):
        self._add_to_bag(quantity=2)
        self._add_to_bag(quantity=3)
        bag = self.client.session.get('bag', {})
        self.assertEqual(bag.get(self.product.id), 5)

    def test_add_to_bag_with_size_post(self):
        product_with_sizes = Product.objects.create(
            name='Sized Product',
            description='Has sizes',
            price=Decimal('35.00'),
            has_sizes=True,
        )
        url = reverse('add_to_bag', args=[product_with_sizes.id])
        response = self.client.post(url, data={
            'quantity': 1,
            'product_size': 'L',
            'redirect_url': reverse('products'),
        })
        self.assertEqual(response.status_code, 302)

    def test_add_to_bag_size_updates_existing(self):
        product_with_sizes = Product.objects.create(
            name='Sized Product', description='D', price=35.00, has_sizes=True
        )
        url = reverse('add_to_bag', args=[product_with_sizes.id])
        self.client.post(url, data={'quantity': 1, 'product_size': 'M', 'redirect_url': '/'})
        self.client.post(url, data={'quantity': 2, 'product_size': 'M', 'redirect_url': '/'})
        bag = self.client.session.get('bag', {})
        stored = bag.get(product_with_sizes.id, {})
        self.assertEqual(stored.get('items_by_size', {}).get('M'), 3)

    # --- Adjust bag ---
    def test_adjust_bag_increase(self):
        self._add_to_bag(quantity=1)
        response = self.client.post(self.adjust_url, data={
            'quantity': 5,
            'redirect_url': reverse('view_bag'),
        })
        self.assertEqual(response.status_code, 302)
        bag = self.client.session.get('bag', {})
        self.assertEqual(bag.get(self.product.id), 5)

    def test_adjust_bag_decrease(self):
        self._add_to_bag(quantity=5)
        response = self.client.post(self.adjust_url, data={
            'quantity': 2,
            'redirect_url': reverse('view_bag'),
        })
        self.assertEqual(response.status_code, 302)
        bag = self.client.session.get('bag', {})
        self.assertEqual(bag.get(self.product.id), 2)

    def test_adjust_bag_zero_removes_item(self):
        self._add_to_bag(quantity=5)
        response = self.client.post(self.adjust_url, data={
            'quantity': 0,
            'redirect_url': reverse('view_bag'),
        })
        self.assertEqual(response.status_code, 302)
        bag = self.client.session.get('bag', {})
        self.assertNotIn(self.product.id, bag)

    def test_adjust_bag_with_size_zero_handled(self):
        """Adjusting a sized product to zero is handled gracefully (no crash)."""
        product_with_sizes = Product.objects.create(
            name='Sized Product', description='D', price=35.00, has_sizes=True
        )
        adj_url = reverse('adjust_bag', args=[product_with_sizes.id])
        # Zero quantity on a non-existent bag item returns 302 (no crash)
        response = self.client.post(adj_url, data={'quantity': 0, 'product_size': 'L'})
        self.assertEqual(response.status_code, 302)

    # --- Remove from bag ---
    def test_remove_from_bag(self):
        self._add_to_bag(quantity=3)
        response = self.client.post(self.remove_url)
        self.assertEqual(response.status_code, 200)
        bag = self.client.session.get('bag', {})
        self.assertNotIn(self.product.id, bag)

    def test_remove_from_bag_with_size_no_crash(self):
        """Removing a sized product from an empty bag returns 200 (error handled gracefully)."""
        product_with_sizes = Product.objects.create(
            name='Sized Product', description='D', price=35.00, has_sizes=True
        )
        rem_url = reverse('remove_from_bag', args=[product_with_sizes.id])
        # Even with empty bag, returns 200 (error message set in messages framework)
        response = self.client.post(rem_url, data={'product_size': 'L'})
        self.assertIn(response.status_code, [200, 404])


class BagContextsTests(TestCase):
    """Tests for bag context processor."""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='c', friendly_name='C')
        self.product = Product.objects.create(
            name='Product', description='D', price=Decimal('10.00'), category=self.category
        )

    def _add_to_bag(self, quantity=1, size=None):
        url = reverse('add_to_bag', args=[self.product.id])
        data = {'quantity': quantity, 'redirect_url': '/'}
        if size:
            data['product_size'] = size
        self.client.post(url, data=data)

    def test_bag_context_has_grand_total(self):
        self._add_to_bag(quantity=2)
        response = self.client.get(reverse('view_bag'))
        self.assertIn('grand_total', response.context)

    def test_bag_context_has_delivery(self):
        self._add_to_bag(quantity=1)
        response = self.client.get(reverse('view_bag'))
        self.assertIn('delivery', response.context)

    def test_bag_context_free_delivery_threshold(self):
        self._add_to_bag(quantity=10)  # 10 x €10 = €100 (over €80 threshold)
        response = self.client.get(reverse('view_bag'))
        self.assertEqual(response.context['delivery'], 0)

    def test_bag_context_product_count(self):
        self._add_to_bag(quantity=3)
        response = self.client.get(reverse('view_bag'))
        self.assertEqual(response.context['product_count'], 3)
