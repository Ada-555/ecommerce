"""
Django signals for the affiliate program.

Handles:
- Linking new users to affiliates when they register with a referral code
- Creating AffiliateReferral records when orders are placed by referred users
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings

from .models import Affiliate, AffiliateReferral


def handle_referral_on_registration(user, referral_code):
    """
    Called by the registration flow when a referral code is provided.
    Links the user to the affiliate and stores the referral in their profile.
    """
    try:
        affiliate = Affiliate.objects.get(referral_code=referral_code.upper(), is_active=True)
        # Set referred_by on the user's profile if it exists
        if hasattr(user, 'userprofile'):
            user.userprofile.referred_by = affiliate
            user.userprofile.save()
        return affiliate
    except Affiliate.DoesNotExist:
        return None


def create_referral_for_order(order):
    """
    Called when an order is completed. If the order's user was referred,
    create an AffiliateReferral record and calculate commission.
    """
    from decimal import Decimal

    if not order.user_profile:
        return None

    referred_by = getattr(order.user_profile, 'referred_by', None)
    if not referred_by:
        return None

    try:
        affiliate = referred_by
    except Affiliate.DoesNotExist:
        return None

    # Calculate commission based on order total
    commission_amount = Decimal(str(order.grand_total)) * affiliate.commission_rate

    referral, created = AffiliateReferral.objects.get_or_create(
        affiliate=affiliate,
        order=order,
        defaults={
            'commission_amount': commission_amount,
            'status': 'pending',
        }
    )
    return referral


# Allauth signal: fire after a user completes registration
@receiver(post_save, sender=User)
def link_referral_on_user_created(sender, instance, created, **kwargs):
    """
    After a new User is created, check the session for an affiliate referral
    code and link the user's profile to the affiliate.
    """
    if not created:
        return

    # Import here to avoid circular dependency
    from django.contrib.sessions.backends.db import SessionStore
    from django.conf import settings as django_settings

    # We can't access request directly from signal, so we check the
    # affiliate registration code stored via the landing page.
    # The accounts adapter or view should call handle_referral_on_registration.
    # This signal primarily serves as a hook point — the real linking is
    # done via the allauth adapter in accounts.
    pass
