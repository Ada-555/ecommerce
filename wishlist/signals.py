from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Wishlist


@receiver(post_save, sender=User)
def create_wishlist_for_user(sender, instance, created, **kwargs):
    """Auto-create a wishlist when a new user is created."""
    if created:
        Wishlist.objects.get_or_create(user=instance)
