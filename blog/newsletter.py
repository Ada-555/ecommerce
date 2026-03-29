"""
Blog newsletter utilities using Brevo (Sendinblue) transactional email API.
Sends blog post newsletters to BlogSubscriber recipients when posts are published.
"""

import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone

logger = logging.getLogger(__name__)


def get_brevo_client():
    """Return an authenticated Brevo API client."""
    from brevo import Brevo
    api_key = getattr(settings, 'BREVO_API_KEY', None)
    if not api_key:
        logger.warning("BREVO_API_KEY is not configured.")
        return None
    client = Brevo()
    return client


def get_blog_subscribers(store_slug='orderimo'):
    """Return active BlogSubscriber emails for a given store."""
    from .models import BlogSubscriber
    return list(
        BlogSubscriber.objects.filter(is_active=True, store=store_slug)
        .values_list('email', flat=True)
    )


def send_blog_newsletter(blog_page, subscribers=None):
    """
    Send a blog post newsletter to subscribers via Brevo transactional email.

    Args:
        blog_page: BlogPage instance to newsletter about
        subscribers: Optional list of email addresses. If None, fetched from BlogSubscriber.

    Returns:
        bool: True if sent successfully, False otherwise.
    """
    client = get_brevo_client()
    if not client:
        logger.error("Cannot send blog newsletter: Brevo client not available.")
        return False

    store_slug = blog_page.store or 'orderimo'
    subscriber_emails = subscribers or get_blog_subscribers(store_slug)

    if not subscriber_emails:
        logger.info(f"No active subscribers for store '{store_slug}'. Skipping newsletter for '{blog_page.title}'.")
        return False

    # Build email content
    live_link = getattr(settings, 'LIVE_LINK', 'http://127.0.0.1:8023')
    post_url = f"{live_link}{blog_page.get_absolute_url()}"

    branding = {
        'orderimo': {
            'name': 'Orderimo',
            'primary_color': '#00b4d8',
            'secondary_color': '#0077b6',
            'icon': 'fa-solid fa-store',
        },
        'petshop-ie': {
            'name': 'PetShop Ireland',
            'primary_color': '#228B22',
            'secondary_color': '#2d9a3e',
            'icon': 'fa-solid fa-paw',
        },
        'digitalhub': {
            'name': 'DigitalHub',
            'primary_color': '#800080',
            'secondary_color': '#da70d6',
            'icon': 'fa-solid fa-bolt',
        },
    }.get(store_slug, {'name': 'Orderimo', 'primary_color': '#00b4d8', 'secondary_color': '#0077b6', 'icon': 'fa-solid fa-store'})

    context = {
        'title': blog_page.title,
        'content': blog_page.content,
        'post_url': post_url,
        'store_name': branding['name'],
        'primary_color': branding['primary_color'],
        'secondary_color': branding['secondary_color'],
        'icon': branding['icon'],
        'store_slug': store_slug,
    }

    try:
        html_content = render_to_string('blog/emails/newsletter.html', context)
    except Exception:
        # Fallback if template not found
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: {branding['primary_color']};">{blog_page.title}</h1>
            <p style="color: #555;">A new blog post from {branding['name']}.</p>
            <p><a href="{post_url}" style="background: {branding['primary_color']}; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Read the full post</a></p>
        </body>
        </html>
        """

    text_content = strip_tags(html_content)

    # Build recipient list (max 2000 per Brevo send_transac_email)
    recipients = [{'email': email} for email in subscriber_emails[:2000]]

    try:
        response = client.transactional_emails.send_transac_email(
            subject=f"📬 New post: {blog_page.title}",
            html_content=html_content,
            text_content=text_content,
            sender={'name': branding['name'], 'email': settings.DEFAULT_FROM_EMAIL},
            to=recipients,
            tags=['blog', 'newsletter', store_slug],
        )
        logger.info(
            f"Blog newsletter sent for '{blog_page.title}' "
            f"to {len(recipients)} subscriber(s). Response: {response}"
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send blog newsletter for '{blog_page.title}': {e}")
        return False
