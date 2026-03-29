from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Wishlist(models.Model):
    """User wishlist containing products saved for later."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name='in_wishlists'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'wishlist'
        verbose_name_plural = 'Wishlists'

    def __str__(self):
        return f"{self.user.username}'s Wishlist"

    def get_store_products(self, store_slug):
        """Return wishlist products filtered by store slug."""
        store_map = {
            'orderimo': 'orderimo',
            'petshop': 'petshop-ie',
            'digital': 'digitalhub',
        }
        db_store = store_map.get(store_slug, 'orderimo')
        return self.products.filter(store=db_store)

    @property
    def count(self):
        return self.products.count()
