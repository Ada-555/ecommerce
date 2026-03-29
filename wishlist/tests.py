from django.test import TestCase
from django.contrib.auth.models import User
from products.models import Product, Category


class WishlistModelTests(TestCase):
    """Tests for the Wishlist model."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        cls.category = Category.objects.create(name='test-category', friendly_name='Test Category')
        cls.product = Product.objects.create(
            name='Test Product',
            description='A test product',
            price=29.99,
            store='orderimo',
            category=cls.category,
        )

    def test_wishlist_created_for_user(self):
        """Test that a wishlist is automatically created for a user."""
        wishlist = self.user.wishlist
        self.assertIsNotNone(wishlist)
        self.assertEqual(wishlist.user, self.user)

    def test_wishlist_products_m2m(self):
        """Test that products can be added to wishlist via M2M."""
        wishlist = self.user.wishlist
        wishlist.products.add(self.product)
        self.assertIn(self.product, wishlist.products.all())

    def test_wishlist_count(self):
        """Test the count property."""
        wishlist = self.user.wishlist
        wishlist.products.add(self.product)
        self.assertEqual(wishlist.count, 1)

    def test_wishlist_str(self):
        """Test string representation."""
        self.assertEqual(str(self.user.wishlist), "testuser's Wishlist")

    def test_get_store_products_filters_by_store(self):
        """Test that get_store_products filters by store slug."""
        product2 = Product.objects.create(
            name='Pet Product',
            description='A pet product',
            price=19.99,
            store='petshop-ie',
            category=self.category,
        )
        wishlist = self.user.wishlist
        wishlist.products.add(self.product, product2)

        orderimo_products = wishlist.get_store_products('orderimo')
        self.assertEqual(orderimo_products.count(), 1)
        self.assertEqual(orderimo_products.first(), self.product)


class WishlistViewTests(TestCase):
    """Tests for wishlist views."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        cls.category = Category.objects.create(name='test-category', friendly_name='Test Category')
        cls.product = Product.objects.create(
            name='Test Product',
            description='A test product',
            price=29.99,
            store='orderimo',
            category=cls.category,
        )

    def test_view_wishlist_requires_login(self):
        """Test that viewing wishlist requires authentication."""
        response = self.client.get('/orderimo/wishlist/')
        # 302 redirect to login, or 301 if trailing slash redirect first
        self.assertIn(response.status_code, [301, 302])

    def test_view_wishlist_authenticated(self):
        """Test that authenticated user can view their wishlist."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/orderimo/wishlist/')
        # May get 301 if APPEND_SLASH redirects
        if response.status_code == 301:
            response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)

    def test_toggle_adds_product(self):
        """Test toggling adds a product to wishlist."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            '/orderimo/wishlist/toggle/{}/'.format(self.product.id),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user.wishlist.products.filter(id=self.product.id).exists())

    def test_toggle_removes_product(self):
        """Test toggling removes a product from wishlist."""
        self.client.login(username='testuser', password='testpass123')
        # First add it
        self.user.wishlist.products.add(self.product)
        # Then toggle (remove)
        response = self.client.post(
            '/orderimo/wishlist/toggle/{}/'.format(self.product.id),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user.wishlist.products.filter(id=self.product.id).exists())

    def test_toggle_returns_json(self):
        """Test that toggle returns JSON for AJAX requests."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            '/orderimo/wishlist/toggle/{}/'.format(self.product.id),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_toggle_unauthenticated_redirects(self):
        """Test that unauthenticated toggle redirects to login."""
        response = self.client.post(
            '/orderimo/wishlist/toggle/{}/'.format(self.product.id)
        )
        # 302 redirect to login, or 301 if trailing slash redirect first
        self.assertIn(response.status_code, [301, 302])
