"""
Django signals for the blog app.
Triggers blog newsletter emails via Brevo when a BlogPage is published.
"""

import logging
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import BlogPage
from .newsletter import send_blog_newsletter

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=BlogPage)
def blogpage_pre_save(sender, instance, **kwargs):
    """
    Capture the previous is_published state before save so we can detect
    transitions from unpublished → published.
    """
    if instance.pk:
        try:
            old = BlogPage.objects.get(pk=instance.pk)
            instance._was_published = old.is_published
        except BlogPage.DoesNotExist:
            instance._was_published = False
    else:
        instance._was_published = False


@receiver(post_save, sender=BlogPage)
def blogpage_published_newsletter(sender, instance, created, **kwargs):
    """
    Send a blog newsletter email when a BlogPage is published or when
    is_published transitions from False → True.

    Does NOT re-send if is_published is already True and the post is updated.
    Does NOT send on first creation unless is_published=True was set at creation time.
    """
    was_published = getattr(instance, '_was_published', False)
    is_published = instance.is_published

    # Only fire when transitioning: unpublished → published
    if was_published or not is_published:
        return

    logger.info(f"BlogPage '{instance.title}' published — triggering newsletter.")

    success = send_blog_newsletter(instance)

    if success:
        instance.newsletter_sent_at = timezone.now()
        # Use update to avoid triggering the signal again
        BlogPage.objects.filter(pk=instance.pk).update(newsletter_sent_at=timezone.now())
        logger.info(f"newsletter_sent_at updated for BlogPage '{instance.title}'.")
    else:
        logger.warning(f"Newsletter failed for BlogPage '{instance.title}' — newsletter_sent_at not updated.")
