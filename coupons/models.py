from django.db import models
from django.utils import timezone
from decimal import Decimal


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', '% Off'),
        ('fixed', 'Fixed Amount'),
        ('free_shipping', 'Free Shipping'),
    ]

    store = models.ForeignKey(
        'stores.StoreConfig', on_delete=models.CASCADE, related_name='coupons'
    )
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percentage'
    )
    discount_value = models.DecimalField(decimal_places=2, max_digits=10)
    min_order_amount = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        default=Decimal('0.00')
    )
    max_uses = models.PositiveIntegerField(default=1)
    current_uses = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()})"

    @property
    def is_expired(self):
        return timezone.now() > self.valid_until

    @property
    def is_maxed_out(self):
        return self.current_uses >= self.max_uses

    def calculate_discount(self, order_total):
        """Calculate the discount amount for a given order total."""
        if self.discount_type == 'percentage':
            return (order_total * self.discount_value) / Decimal('100')
        elif self.discount_type == 'fixed':
            return min(self.discount_value, order_total)
        elif self.discount_type == 'free_shipping':
            return Decimal('0.00')  # Handled separately in delivery calc
        return Decimal('0.00')
