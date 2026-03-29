from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order, OrderLineItem


@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """ Update order total on lineitem update/create """
    instance.order.update_total()


@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    """ Update order total on lineitem delete """
    instance.order.update_total()


@receiver(post_save, sender=Order)
def create_affiliate_referral_on_order_paid(sender, instance, created, **kwargs):
    """
    When an order transitions to 'paid' status, check if the buyer
    was referred and create an AffiliateReferral record.
    Uses lazy import to avoid circular imports.
    """
    if created:
        return
    # Track previous payment_status via instance dict to detect transition
    if not hasattr(instance, '_payment_status_was'):
        instance._payment_status_was = 'pending'
    old_status = instance._payment_status_was
    new_status = instance.payment_status
    instance._payment_status_was = new_status
    if old_status != 'paid' and new_status == 'paid':
        from affiliates.signals import create_referral_for_order
        create_referral_for_order(instance)
