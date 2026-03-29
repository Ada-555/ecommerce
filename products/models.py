from django.db import models


class Category(models.Model):

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['friendly_name']

    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)
    description = models.TextField(default='', blank=True)
    display_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name or self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products') + f'?category={self.name}'


class Product(models.Model):
    category = models.ForeignKey(
        'Category', null=True, blank=True, on_delete=models.SET_NULL
        )
    sku = models.CharField(max_length=50, unique=True, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    has_sizes = models.BooleanField(default=False, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
        )
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    # New stock fields
    stock_quantity = models.IntegerField(default=0, blank=True)
    low_stock_threshold = models.IntegerField(default=5, blank=True)
    brand = models.CharField(max_length=100, blank=True, default='')
    featured = models.BooleanField(default=False)
    new_arrival = models.BooleanField(default=False)
    best_seller = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    # Digital product fields
    is_digital = models.BooleanField(default=False)
    download_file = models.FileField(upload_to='downloads/', blank=True, null=True)
    # Subscription fields
    is_subscription = models.BooleanField(
        default=False,
        help_text='Enable this product as a recurring subscription'
    )
    subscription_interval = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ],
        blank=True,
        default='',
        help_text='Billing interval for subscription'
    )
    stripe_price_id = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='Stripe Price ID for subscription billing'
    )
    # Store filtering
    store = models.CharField(max_length=50, blank=True, default='orderimo',
        help_text="Store slug this product belongs to: orderimo, petshop-ie, digitalhub")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('product_detail', args=[self.id])

    @property
    def stock_status(self):
        if self.stock_quantity <= 0:
            return 'Out of Stock'
        elif self.stock_quantity <= self.low_stock_threshold:
            return 'Low Stock'
        return 'In Stock'

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        return 0 < self.stock_quantity <= self.low_stock_threshold

    @property
    def has_variants(self):
        return self.variants.exists()

    @property
    def average_rating(self):
        approved = self.reviews.filter(approved=True)
        if not approved.exists():
            return None
        return round(sum(r.rating for r in approved) / approved.count(), 1)

    @property
    def review_count(self):
        return self.reviews.filter(approved=True).count()


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    size = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True)
    price_override = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    stock_quantity = models.IntegerField(default=0)
    weight_kg = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        parts = [self.product.name]
        if self.size:
            parts.append(self.size)
        if self.color:
            parts.append(self.color)
        return ' / '.join(parts)

    @property
    def effective_price(self):
        return self.price_override if self.price_override else self.product.price

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0


class Review(models.Model):
    user = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='reviews'
    )
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE, related_name='reviews'
    )
    rating = models.IntegerField(
        choices=[(i, f'{i} star{"s" if i > 1 else ""}') for i in range(1, 6)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.user.username} - {self.product.name} ({self.rating}★)'
