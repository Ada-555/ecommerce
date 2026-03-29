import uuid
from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.conf import settings

from django_countries.fields import CountryField

from products.models import Product
from profiles.models import UserProfile


class Order(models.Model):
    order_number = models.CharField(
        max_length=32, null=False, editable=False)
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='orders')
    full_name = models.CharField(
        max_length=50, null=False, blank=False)
    email = models.EmailField(
        max_length=254, null=False, blank=False)
    phone_number = models.CharField(
        max_length=20, null=False, blank=False)
    country = CountryField(
        blank_label='Country *', null=False, blank=False)
    postcode = models.CharField(
        max_length=20, null=True, blank=True)
    town_or_city = models.CharField(
        max_length=40, null=False, blank=False)
    street_address1 = models.CharField(
        max_length=80, null=False, blank=False)
    street_address2 = models.CharField(
        max_length=80, null=True, blank=True)
    county = models.CharField(
        max_length=80, null=True, blank=True)
    date = models.DateTimeField(
        auto_now_add=True)
    delivery_cost = models.DecimalField(
        max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0)
    original_bag = models.TextField(
        null=False, blank=False, default='')
    stripe_pid = models.CharField(
        max_length=254, null=False, blank=False, default='')
    store = models.CharField(
        max_length=20, choices=[
            ('orderimo', 'Orderimo'),
            ('petshop-ie', 'PetShop Ireland'),
            ('digitalhub', 'DigitalHub'),
        ], default='orderimo')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    tracking_number = models.CharField(
        max_length=100, null=True, blank=True,
        help_text='Carrier tracking number')
    carrier = models.CharField(
        max_length=100, null=True, blank=True,
        help_text='Shipping carrier name (e.g. An Post, DPD)')
    estimated_delivery = models.DateField(null=True, blank=True)

    # Crypto payment fields
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Card'),
        ('stripe_crypto', 'Stripe Crypto (BTC/USDC)'),
        ('coingate_xmr', 'CoinGate (XMR)'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES,
        default='card', null=False, blank=False)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES,
        default='pending', null=False, blank=False)
    crypto_txid = models.CharField(
        max_length=255, null=True, blank=True,
        help_text='Cryptocurrency transaction ID')
    crypto_amount = models.DecimalField(
        max_digits=20, decimal_places=12, null=True, blank=True,
        help_text='Crypto amount sent (for XMR via CoinGate)')
    crypto_address = models.CharField(
        max_length=255, null=True, blank=True,
        help_text='Destination crypto wallet address')
    coupon_codes = models.CharField(
        max_length=200, blank=True, default='',
        help_text='Comma-separated list of applied coupon codes')
    coupon_discount = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=True, default=0,
        help_text='Total discount from applied coupons')

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs and coupon discounts.
        """
        self.order_total = self.lineitems.aggregate(
            Sum('lineitem_total'))['lineitem_total__sum'] or 0
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        else:
            self.delivery_cost = 0
        # Apply coupon discount (subtract from grand_total)
        discount = getattr(self, 'coupon_discount', Decimal('0.00')) if self.coupon_discount else Decimal('0.00')
        self.grand_total = self.order_total + self.delivery_cost - discount
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order, null=False, blank=False,
        on_delete=models.CASCADE, related_name='lineitems')
    product = models.ForeignKey(
        Product, null=False, blank=False, on_delete=models.CASCADE)
    product_size = models.CharField(
        max_length=2, null=True, blank=True)  # XS, S, M, L, XL
    quantity = models.IntegerField(
        null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(
        max_digits=6, decimal_places=2,
        null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'SKU {self.product.sku} on order {self.order.order_number}'


class AbandonedCart(models.Model):
    """
    Records abandoned shopping cart snapshots so we can send
    follow-up reminder emails.

    Updated by CheckoutMiddleware whenever the session bag changes.
    Marked as converted when the user completes an order.
    """
    user = models.ForeignKey(
        UserProfile, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='abandoned_carts')
    session_key = models.CharField(
        max_length=40, null=True, blank=True,
        help_text='Django session key for anonymous carts')
    email = models.EmailField(
        max_length=254, null=False, blank=False,
        help_text='Email address to send the reminder to')
    store = models.CharField(
        max_length=20, choices=[
            ('orderimo', 'Orderimo'),
            ('petshop-ie', 'PetShop Ireland'),
            ('digitalhub', 'DigitalHub'),
        ], default='orderimo')
    # Serialised bag snapshot: same format as request.session['bag']
    bag_snapshot = models.TextField(default='{}')
    bag_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0)
    last_activity = models.DateTimeField(auto_now=True)
    # Conversion tracking
    is_converted = models.BooleanField(default=False)
    converted_at = models.DateTimeField(null=True, blank=True)
    # Email send tracking
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    # Recovery coupon (links to a Coupon if one was issued)
    recovery_coupon_code = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = 'Abandoned Cart'
        verbose_name_plural = 'Abandoned Carts'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['email', 'store', 'is_converted']),
            models.Index(fields=['last_activity']),
        ]

    def __str__(self):
        return f'AbandonedCart({self.email}, {self.store}, converted={self.is_converted})'

