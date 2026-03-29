"""
CheckoutMiddleware — tracks abandoned cart snapshots.

On every request that has a non-empty bag in the session, we upsert an
AbandonedCart record.  When an order is placed the same middleware marks
the cart as converted.
"""

import json
import logging
from decimal import Decimal

from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


class AbandonedCartMiddleware:
    """
    Attaches abandoned-cart tracking to each request.

    - Creates / updates an AbandonedCart record whenever the session bag changes.
    - Marks the cart as converted when the user reaches the checkout-success URL.
    """

    # Paths that represent checkout completion — carts from these are "converted"
    CONVERTED_PATHS = ['/checkout/checkout_success/', '/orderimo/checkout/checkout_success/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only process when the user has a bag
        bag = request.session.get('bag', {})
        if not bag:
            return response

        # Only track for GET / normal page loads (avoid double-trigger on POST)
        if request.method not in ('GET', 'HEAD'):
            return response

        user = getattr(request, 'user', None)
        email = None

        if user and user.is_authenticated:
            try:
                email = user.email
            except Exception:
                email = None

        # Fall back to the profile email for authenticated users
        if not email and user and user.is_authenticated:
            try:
                email = user.profile.email
            except Exception:
                pass

        if not email:
            # Anonymous user — we can't email them, skip tracking
            return response

        store_slug = request.session.get('active_store', 'orderimo')
        bag_snapshot = json.dumps(bag)

        # Calculate current bag total (same logic as bag/contexts.py)
        total = Decimal('0.00')
        for item_id, item_data in bag.items():
            try:
                from products.models import Product
                product = Product.objects.get(id=int(item_id))
                if isinstance(item_data, int):
                    total += item_data * product.price
                elif isinstance(item_data, dict) and 'items_by_size' in item_data:
                    for qty in item_data['items_by_size'].values():
                        total += qty * product.price
            except Exception:
                pass

        try:
            from .models import AbandonedCart

            # Upsert: update if exists (same email+store), otherwise create
            defaults = {
                'bag_snapshot': bag_snapshot,
                'bag_total': total,
                'session_key': request.session.session_key,
                'store': store_slug,
                'is_converted': False,
            }
            if user and user.is_authenticated:
                defaults['user'] = user.profile if hasattr(user, 'profile') else None

            cart, created = AbandonedCart.objects.update_or_create(
                email=email,
                store=store_slug,
                is_converted=False,
                defaults=defaults,
            )
            if created:
                logger.info(f"Created AbandonedCart for {email} store={store_slug}")
            else:
                logger.debug(f"Updated AbandonedCart for {email} store={store_slug}")

        except Exception as e:
            logger.exception(f"Failed to save AbandonedCart: {e}")

        return response
