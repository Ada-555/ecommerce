from django.db import models
from django.contrib.auth.models import User


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('past_due', 'Past Due'),
        ('unpaid', 'Unpaid'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions'
    )
    stripe_subscription_id = models.CharField(max_length=200, blank=True, default='')
    stripe_customer_id = models.CharField(max_length=200, blank=True, default='')
    product_name = models.CharField(max_length=254)
    product_id = models.PositiveIntegerField()
    interval = models.CharField(max_length=20, choices=[
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product_name} ({self.status})"
