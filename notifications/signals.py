"""
Signals for triggering transactional email notifications.
- Order status changes (confirmed → shipped → out_for_delivery → delivered)
- New user registration (allauth)
"""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from checkout.models import Order
from .utils import send_shipping_notification, send_delivery_notification, send_welcome_email


@receiver(pre_save, sender=Order)
def order_pre_save(sender, instance, **kwargs):
    """
    Capture the previous status before save so we can detect transitions.
    """
    if instance.pk:
        try:
            old = Order.objects.get(pk=instance.pk)
            instance._previous_status = old.status
            instance._previous_tracking = old.tracking_number
        except Order.DoesNotExist:
            instance._previous_status = None
            instance._previous_tracking = None
    else:
        instance._previous_status = None
        instance._previous_tracking = None


@receiver(post_save, sender=Order)
def order_status_change_email(sender, instance, created, **kwargs):
    """
    Detect status transitions and send the appropriate email.
    - New orders: confirmation is sent directly from checkout_success()
    - Status → 'shipped': send shipping notification
    - Status → 'delivered': send delivery notification
    """
    if created:
        return  # Confirmation handled in checkout_success()

    prev_status = getattr(instance, '_previous_status', None)
    curr_status = instance.status

    if prev_status == curr_status:
        return  # No status change

    # → Shipped
    if curr_status == 'shipped' and prev_status != 'shipped':
        send_shipping_notification(
            instance,
            tracking_number=instance.tracking_number,
            carrier=instance.carrier,
            expected_delivery=instance.estimated_delivery,
        )

    # → Delivered
    if curr_status == 'delivered' and prev_status != 'delivered':
        send_delivery_notification(instance)


# ---------------------------------------------------------------------------
# User registration signal (allauth)
# ---------------------------------------------------------------------------

@receiver(post_save, sender='auth.User')
def user_created_welcome_email(sender, instance, created, **kwargs):
    """
    Send welcome email when a new user account is created via allauth.
    Sends for all new Users with an email address.
    """
    if not created:
        return
    if not instance.email:
        return
    # allauth may create inactive users pending email verification;
    # still send welcome — verification is a separate flow.
    send_welcome_email(instance, store_slug='orderimo')
