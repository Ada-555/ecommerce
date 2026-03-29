from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid


class Affiliate(models.Model):
    """
    Represents an affiliate partner who can earn commissions
    by referring new users to the platform.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='affiliate')
    referral_code = models.CharField(
        max_length=32, unique=True, blank=False, editable=False)
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=0.10,
        help_text='Commission as a decimal (e.g. 0.10 = 10%)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Affiliate({self.user.username}, {self.referral_code})"

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    def total_earnings(self):
        """Sum of all paid commissions."""
        return self.referrals.filter(status='paid').aggregate(
            total=models.Sum('commission_amount'))['total'] or 0

    def pending_earnings(self):
        """Sum of all pending commissions."""
        return self.referrals.filter(status='pending').aggregate(
            total=models.Sum('commission_amount'))['total'] or 0

    def total_referrals(self):
        """Total number of successful referrals (paid orders)."""
        return self.referrals.filter(status='paid').count()


class AffiliateReferral(models.Model):
    """
    Tracks a referral event: when a referred user places an order,
    a commission is generated.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    affiliate = models.ForeignKey(
        Affiliate, on_delete=models.CASCADE,
        related_name='referrals')
    order = models.ForeignKey(
        'checkout.Order', on_delete=models.CASCADE,
        related_name='affiliate_referrals')
    commission_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['affiliate', 'order']

    def __str__(self):
        return (
            f"Referral({self.affiliate.referral_code} -> "
            f"{self.order.order_number}, €{self.commission_amount}, "
            f"{self.status})"
        )
