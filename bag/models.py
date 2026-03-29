from django.db import models
from django.conf import settings


class Bag(models.Model):
    """
    A shopping bag/basket that can be associated with a user.
    Tracks whether the bag has been checked out and when it was last updated.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='bags'
    )
    STORE_CHOICES = [
        ('orderimo', 'Orderimo'),
        ('petshop-ie', 'PetShop Ireland'),
        ('digitalhub', 'DigitalHub'),
    ]
    store = models.CharField(
        max_length=20,
        choices=STORE_CHOICES,
        default='orderimo'
    )
    updated_at = models.DateTimeField(auto_now=True)
    checkout_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Bag'
        verbose_name_plural = 'Bags'

    def __str__(self):
        return f'Bag {self.id} ({self.get_store_display()})'


class BagItem(models.Model):
    """
    An item within a bag. Supports optional size selection.
    """
    bag = models.ForeignKey(
        Bag,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text='Size code if product has sizes (e.g., S, M, L, XL)'
    )

    class Meta:
        verbose_name = 'Bag Item'
        verbose_name_plural = 'Bag Items'

    def __str__(self):
        if self.size:
            return f'{self.quantity}x {self.product.name} (Size: {self.size})'
        return f'{self.quantity}x {self.product.name}'

    @property
    def total(self):
        """Calculate total price for this line item."""
        return self.product.price * self.quantity

