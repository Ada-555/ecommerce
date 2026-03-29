"""
Management command: send_abandoned_cart_emails

Finds carts that were abandoned (not converted) for more than 24 hours,
then sends a reminder email with an optional recovery coupon.

Usage:
    python manage.py send_abandoned_cart_emails
    python manage.py send_abandoned_cart_emails --hours 48 --dry-run

Recommended cron (hourly):
    0 * * * * cd /path/to && python manage.py send_abandoned_cart_emails >> /var/log/abandoned_cart.log 2>&1
"""

import json
import logging
import random
import string
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone
from django.db.models import Q

from checkout.models import AbandonedCart, Order
from notifications.utils import _send_html_email, get_store_branding
from coupons.models import Coupon
from stores.models import StoreConfig

logger = logging.getLogger(__name__)

# Send window: 9am–8pm local time (Ireland / Europe/Dublin)
SEND_WINDOW_START = 9   # 09:00
SEND_WINDOW_END = 20    # 20:00


def _in_send_window():
    """Return True if current UTC hour is within the allowed send window."""
    now = timezone.now()
    # naive hour in UTC (good enough for Ireland/Dublin ± a few hours)
    hour = now.hour
    return SEND_WINDOW_START <= hour < SEND_WINDOW_END


def _build_cart_items(bag_snapshot):
    """
    Convert a bag snapshot JSON string into a list of item dicts
    suitable for the email template.
    """
    items = []
    try:
        bag = json.loads(bag_snapshot)
    except Exception:
        return []

    for item_id, item_data in bag.items():
        try:
            from products.models import Product
            product = Product.objects.get(id=int(item_id))
            if isinstance(item_data, int):
                qty = item_data
                size = None
            elif isinstance(item_data, dict) and 'items_by_size' in item_data:
                for size, qty in item_data['items_by_size'].items():
                    items.append({
                        'name': product.name,
                        'quantity': qty,
                        'size': size,
                        'total': product.price * qty,
                    })
                continue
            else:
                continue

            items.append({
                'name': product.name,
                'quantity': qty,
                'size': size,
                'total': product.price * qty,
            })
        except Exception:
            pass

    return items


def _generate_recovery_code(length=8):
    """Generate a random uppercase coupon-like code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


class Command(BaseCommand):
    help = 'Send abandoned cart reminder emails to users who left items in their bag.'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Only email carts abandoned for at least this many hours (default: 24)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Ignore the send window (9am-8pm) and send immediately',
        )

    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']
        force_window = options['force']

        if not _in_send_window() and not force_window:
            self.stdout.write(
                self.style.WARNING(
                    f'Outside send window ({SEND_WINDOW_START}:00–{SEND_WINDOW_END}:00 UTC). '
                    'Use --force to send anyway.'
                )
            )
            return

        cutoff = timezone.now() - timedelta(hours=hours)

        abandoned_carts = AbandonedCart.objects.filter(
            is_converted=False,
            reminder_sent=False,
            last_activity__lte=cutoff,
        ).exclude(email='').select_related('user__user')

        count = abandoned_carts.count()
        self.stdout.write(f'Found {count} abandoned cart(s) eligible for reminders.')

        for cart in abandoned_carts:
            # Skip if already converted by a newer order
            recent_order = Order.objects.filter(
                Q(email__iexact=cart.email) | Q(user_profile=cart.user),
                date__gte=cart.last_activity,
            ).exists()
            if recent_order:
                cart.is_converted = True
                cart.save(update_fields=['is_converted'])
                self.stdout.write(f'  Skipping {cart.email} — already has a recent order.')
                continue

            branding = get_store_branding(cart.store)
            cart_items = _build_cart_items(cart.bag_snapshot)

            if not cart_items:
                self.stdout.write(f'  Skipping {cart.email} — empty bag snapshot.')
                continue

            live_link = getattr(settings, 'LIVE_LINK', 'https://orderimo.com')
            cart_url = f'{live_link}bag/'

            # Build recovery coupon
            recovery_code = None
            recovery_url = None
            try:
                recovery_code = _generate_recovery_code()
                store_config = StoreConfig.objects.filter(slug=cart.store).first()
                if store_config:
                    # Create a one-time use coupon for this cart
                    coupon = Coupon.objects.create(
                        store=store_config,
                        code=recovery_code,
                        discount_type='percentage',
                        discount_value=Decimal('10'),  # 10% off
                        min_order_amount=cart.bag_total,
                        max_uses=1,
                        valid_from=timezone.now(),
                        valid_until=timezone.now() + timedelta(hours=48),
                        is_active=True,
                    )
                    recovery_url = f'{cart_url}?coupon={recovery_code}'
                    cart.recovery_coupon_code = recovery_code
                    self.stdout.write(f'  Created recovery coupon {recovery_code} for {cart.email}')
            except Exception as e:
                logger.warning(f'Could not create recovery coupon: {e}')

            subject = f'Your cart at {branding["name"]} is waiting! 🛒'

            context = {
                'cart_items': cart_items,
                'cart_total': cart.bag_total,
                'cart_url': cart_url,
                'recovery_code': recovery_code,
                'recovery_url': recovery_url,
                'live_link': live_link,
            }

            if dry_run:
                self.stdout.write(
                    f'  [DRY-RUN] Would send abandoned cart email to {cart.email} '
                    f'({len(cart_items)} items, total €{cart.bag_total})'
                )
                continue

            success = _send_html_email(
                subject=subject,
                to_email=cart.email,
                html_template='emails/abandoned_cart.html',
                text_template='emails/abandoned_cart.txt',
                context=context,
                branding=branding,
            )

            if success:
                cart.reminder_sent = True
                cart.reminder_sent_at = timezone.now()
                cart.save(update_fields=['reminder_sent', 'reminder_sent_at'])
                self.stdout.write(
                    self.style.SUCCESS(f'  Sent reminder to {cart.email}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'  Failed to send reminder to {cart.email}')
                )

        self.stdout.write(self.style.SUCCESS('Done.'))


# Need Decimal import in this file
from decimal import Decimal
