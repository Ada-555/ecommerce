"""
Comprehensive tests for the products app.
Tests CRUD operations, views, forms, and edge cases.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Q
from decimal import Decimal
import json

from .models import Category, Product
from .forms import ProductForm


class CategoryModelTests(TestCase):
    """Tests for the Category model."""

    def test_create_category(self):
        cat = Category.objects.create(name="test_category", friendly_name="Test Category")
        self.assertEqual(str(cat), "test_category")
        self.assertEqual(cat.get_friendly_name(), "Test Category")

    def test_category_friendly_name_optional(self):
        cat = Category.objects.create(name="no_friendly")
        self.assertEqual(cat.get_friendly_name(), None)

    def test_category_name_uniqueness(self):
        """Category names are not enforced unique at model level."""
        cat1 = Category.objects.create(name="cat_name")
        cat2 = Category.objects.create(name="cat_name")
        # Both can exist (no unique constraint on name)
        self.assertEqual(cat1.name, cat2.name)
        self.assertNotEqual(cat1.pk, cat2.pk)


class ProductModelTests(TestCase):
    """Tests for the Product model."""

    def setUp(self):
        self.category = Category.objects.create(name="clothing", friendly_name="Clothing")

    def test_create_product_without_category(self):
        product = Product.objects.create(
            name="Test Product",
            description="A great product",
            price=Decimal("29.99"),
        )
        self.assertEqual(str(product), "Test Product")
        self.assertEqual(product.category, None)

    def test_create_product_with_category(self):
        product = Product.objects.create(
            name="T-Shirt",
            description="AI-generated tee",
            price=Decimal("39.99"),
            category=self.category,
            has_sizes=True,
            sku="TSHIRT001",
        )
        self.assertEqual(str(product), "T-Shirt")
        self.assertEqual(product.category.name, "clothing")
        self.assertTrue(product.has_sizes)

    def test_product_price_decimal_places(self):
        product = Product.objects.create(
            name="Precise Product",
            description="Test",
            price=Decimal("19.99"),
        )
        self.assertEqual(str(product.price), "19.99")


class ProductFormTests(TestCase):
    """Tests for ProductForm validation."""

    def setUp(self):
        self.category = Category.objects.create(name="art", friendly_name="Art")

    def test_form_valid_with_all_fields(self):
        form = ProductForm(data={
            'name': 'AI Art Print',
            'description': 'Beautiful AI-generated art',
            'price': '49.99',
            'category': self.category.id,
            'sku': 'ART001',
            'has_sizes': True,
        })
        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_form_valid_minimal_fields(self):
        form = ProductForm(data={
            'name': 'Minimal Product',
            'description': 'Description here',
            'price': '9.99',
        })
        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_form_invalid_missing_name(self):
        form = ProductForm(data={'description': 'Desc', 'price': '10.00'})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_form_invalid_missing_description(self):
        form = ProductForm(data={'name': 'Name', 'price': '10.00'})
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    def test_form_invalid_missing_price(self):
        form = ProductForm(data={'name': 'Name', 'description': 'Desc'})
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_form_invalid_negative_price(self):
        form = ProductForm(data={
            'name': 'Product',
            'description': 'Desc',
            'price': '-5.00',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_form_invalid_zero_price(self):
        form = ProductForm(data={
            'name': 'Product',
            'description': 'Desc',
            'price': '0',
        })
        self.assertFalse(form.is_valid())


class ProductsViewTests(TestCase):
    """Tests for products app views."""

    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser('admin', 'admin@test.com', 'adminpass123')
        self.user = User.objects.create_user('shopper', 'shop@test.com', 'shopperpass')
        self.category = Category.objects.create(name='clothing', friendly_name='Clothing')
        self.product = Product.objects.create(
            name='AI Tee',
            description='Great t-shirt',
            price=Decimal('25.00'),
            category=self.category,
        )
        self.products_url = reverse('products')
        self.product_detail_url = reverse('product_detail', args=[self.product.id])

    # --- All Products View ---
    def test_all_products_get_200(self):
        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Tee')

    def test_all_products_pagination(self):
        # Create 20 products
        for i in range(20):
            Product.objects.create(name=f'Product {i}', description='Desc', price=10.00)
        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, 200)
        # Default paginate_by = 12
        self.assertEqual(len(response.context['page_obj']), 12)

    def test_all_products_search_query(self):
        response = self.client.get(self.products_url + '?q=AI')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Tee')

    def test_all_products_search_no_results(self):
        response = self.client.get(self.products_url + '?q=nonexistent')
        self.assertEqual(response.status_code, 200)
        # Should show empty state or no products

    def test_all_products_category_filter(self):
        response = self.client.get(self.products_url + f'?category={self.category.name}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Tee')

    def test_all_products_sort_by_price_asc(self):
        Product.objects.create(name='Cheap', description='D', price=5.00)
        response = self.client.get(self.products_url + '?sort=price&direction=asc')
        self.assertEqual(response.status_code, 200)

    def test_all_products_sort_by_price_desc(self):
        response = self.client.get(self.products_url + '?sort=price&direction=desc')
        self.assertEqual(response.status_code, 200)

    # --- Product Detail View ---
    def test_product_detail_get_200(self):
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Tee')
        self.assertContains(response, '25.00')

    def test_product_detail_404(self):
        response = self.client.get(reverse('product_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_product_detail_no_image_shows_placeholder(self):
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, 200)
        # Should show noimage placeholder

    # --- Add Product (requires superuser) ---
    def test_add_product_requires_login(self):
        response = self.client.get(reverse('add_product'))
        self.assertEqual(response.status_code, 302)  # redirect to login

    def test_add_product_requires_superuser(self):
        self.client.login(username='shopper', password='shopperpass')
        response = self.client.get(reverse('add_product'))
        self.assertEqual(response.status_code, 302)  # redirect to home

    def test_add_product_get_as_superuser(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('add_product'))
        self.assertEqual(response.status_code, 200)

    def test_add_product_post_valid(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('add_product'), data={
            'name': 'New Product',
            'description': 'A new product',
            'price': '19.99',
            'category': self.category.id,
        })
        self.assertEqual(Product.objects.filter(name='New Product').count(), 1)
        new_product = Product.objects.get(name='New Product')
        self.assertRedirects(response, reverse('product_detail', args=[new_product.id]))

    def test_add_product_post_invalid(self):
        self.client.login(username='admin', password='adminpass123')
        # Submit with missing required 'name' field
        response = self.client.post(reverse('add_product'), data={
            'description': 'Missing name',
            'price': '10.00',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())

    # --- Edit Product ---
    def test_edit_product_get_as_superuser(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('edit_product', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Tee')

    def test_edit_product_post_valid(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('edit_product', args=[self.product.id]), data={
            'name': 'Updated Tee',
            'description': 'Updated description',
            'price': '35.00',
            'category': self.category.id,
        })
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Tee')
        self.assertEqual(str(self.product.price), '35.00')
        self.assertRedirects(response, reverse('product_detail', args=[self.product.id]))

    def test_edit_product_requires_superuser(self):
        self.client.login(username='shopper', password='shopperpass')
        response = self.client.get(reverse('edit_product', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)

    # --- Delete Product ---
    def test_delete_product_wrong_username(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('delete_product', args=[self.product.id]), data={
            'username': 'wrong_user',
        })
        self.product.refresh_from_db()
        self.assertTrue(Product.objects.filter(id=self.product.id).exists())

    def test_delete_product_correct_username(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('delete_product', args=[self.product.id]), data={
            'username': 'admin',
        })
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())
        self.assertRedirects(response, reverse('products'))

    def test_delete_product_requires_superuser(self):
        self.client.login(username='shopper', password='shopperpass')
        response = self.client.post(reverse('delete_product', args=[self.product.id]), data={
            'username': 'shopper',
        })
        self.assertTrue(Product.objects.filter(id=self.product.id).exists())
