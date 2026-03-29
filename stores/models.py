from django.db import models
from django.contrib.sites.models import Site


class StoreConfig(models.Model):
    THEME_CHOICES = [
        ('cyan', 'Cyan/Neon (Orderimo)'),
        ('green', 'Green/Earthy (PetShop Ireland)'),
        ('purple', 'Purple/Modern (DigitalHub)'),
    ]

    site = models.OneToOneField(Site, on_delete=models.CASCADE, related_name='store_config')
    store_name = models.CharField(max_length=100)
    tagline = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    theme = models.CharField(max_length=50, default='cyan', choices=THEME_CHOICES)
    description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    footer_text = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.store_name
