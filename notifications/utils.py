"""
Email notification utilities for Orderimo.
Sends transactional emails for order and account events.
"""

import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


# Store branding map used in email templates
STORE_BRANDING = {
    'orderimo': {
        'name': 'Orderimo',
        'primary_color': '#00b4d8',
        'secondary_color': '#0077b6',
        'accent_color': '#90e0ef',
        'dark': '#0a0a0f',
        'icon': 'fa-solid fa-store',
        'tagline': 'One platform. Multiple curated stores.',
        'copyright': '© 2026 Orderimo',
    },
    'petshop-ie': {
        'name': 'PetShop Ireland',
        'primary_color': '#228B22',
        'secondary_color': '#2d9a3e',
        'accent_color': '#90EE90',
        'dark': '#0a150a',
        'icon': 'fa-solid fa-paw',
        'tagline': "Ireland's best pet supplies.",
        'copyright': '© 2026 PetShop Ireland — Delivering to Ireland 🇮🇪',
    },
    'digitalhub': {
        'name': 'DigitalHub',
        'primary_color': '#800080',
        'secondary_color': '#da70d6',
        'accent_color': '#ff69b4',
        'dark': '#06060f',
        'icon': 'fa-solid fa-bolt',
        'tagline': 'Instant delivery. Lifetime access.',
        'copyright': '© 2026 DigitalHub — Instant Digital Delivery',
    },
}

DEFAULT_BRANDING = {
    'name': 'Orderimo',
    'primary_color': '#00b4d8',
    'secondary_color': '#0077b6',
    'accent_color': '#90e0ef',
    'dark': '#0a0a0f',
    'icon': 'fa-solid fa-store',
    'tagline': 'Orderimo — One platform. Multiple curated stores.',
    'copyright': '© 2026 Orderimo',
}


def get_store_branding(store_slug):
    """Return branding dict for a store slug, falling back to defaults."""
    return STORE_BRANDING.get(store_slug, DEFAULT_BRANDING)


def _send_html_email(subject, to_email, html_template, text_template, context, branding=None):
    """
    Core email sender. Renders both HTML and plain-text versions.
    """
    if branding is None:
        branding = DEFAULT_BRANDING

    ctx = {**context, 'branding': branding}
    try:
        html_content = render_to_string(html_template, ctx)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=True)
        logger.info(f"Email sent: {subject} -> {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email '{subject}' to {to_email}: {e}")
        return False


# ---------------------------------------------------------------------------
# Order Emails
# ---------------------------------------------------------------------------

def send_order_confirmation(order):
    """
    Send order confirmation email after successful checkout.
    Called from checkout/views.checkout_success().
    """
    branding = get_store_branding(getattr(order, 'store', 'orderimo'))

    subject = f'Order #{order.order_number} Confirmed — {branding["name"]}'

    # Build line items context
    line_items = []
    for item in order.lineitems.select_related('product').all():
        line_items.append({
            'name': item.product.name,
            'sku': item.product.sku,
            'quantity': item.quantity,
            'size': item.product_size,
            'price': item.product.price,
            'total': item.lineitem_total,
        })

    context = {
        'order': order,
        'line_items': line_items,
        'order_total': order.order_total,
        'delivery_cost': order.delivery_cost,
        'grand_total': order.grand_total,
        'live_link': getattr(settings, 'LIVE_LINK', 'https://orderimo.com'),
        'store_slug': order.store,
    }

    _send_html_email(
        subject=subject,
        to_email=order.email,
        html_template='emails/order_confirmation.html',
        text_template='emails/order_confirmation.txt',
        context=context,
        branding=branding,
    )


def send_shipping_notification(order, tracking_number=None, carrier=None, expected_delivery=None):
    """
    Send shipping notification when order status changes to 'shipped'.
    Called from signals when order.status transitions to 'shipped'.
    """
    branding = get_store_branding(getattr(order, 'store', 'orderimo'))

    subject = f'Your Order #{order.order_number} Has Shipped! 🚚'

    context = {
        'order': order,
        'tracking_number': tracking_number,
        'carrier': carrier or 'Our courier partner',
        'expected_delivery': expected_delivery,
        'store_slug': order.store,
    }

    _send_html_email(
        subject=subject,
        to_email=order.email,
        html_template='emails/order_shipped.html',
        text_template='emails/order_shipped.txt',
        context=context,
        branding=branding,
    )


def send_delivery_notification(order):
    """
    Send delivery confirmation when order status changes to 'delivered'.
    Called from signals when order.status transitions to 'delivered'.
    """
    branding = get_store_branding(getattr(order, 'store', 'orderimo'))

    subject = f'Your Order #{order.order_number} Has Been Delivered! 🎉'

    context = {
        'order': order,
        'store_slug': order.store,
    }

    _send_html_email(
        subject=subject,
        to_email=order.email,
        html_template='emails/order_delivered.html',
        text_template='emails/order_delivered.txt',
        context=context,
        branding=branding,
    )


# ---------------------------------------------------------------------------
# Account Emails
# ---------------------------------------------------------------------------

def send_welcome_email(user, store_slug='orderimo'):
    """
    Send welcome email when a new user signs up.
    Called from signals when a new user account is created via allauth.
    """
    branding = get_store_branding(store_slug)

    subject = f'Welcome to {branding["name"]}! 🎉'

    context = {
        'user': user,
        'first_name': user.first_name or user.username,
        'store_slug': store_slug,
    }

    _send_html_email(
        subject=subject,
        to_email=user.email,
        html_template='emails/welcome.html',
        text_template='emails/welcome.txt',
        context=context,
        branding=branding,
    )
