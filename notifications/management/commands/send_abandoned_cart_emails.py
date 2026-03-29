from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from bag.models import Bag
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from notifications.utils import get_store_branding


class Command(BaseCommand):
    help = "Send abandoned cart email reminders"

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(hours=24)
        # Find bags that haven't been checked out and haven't been updated for 24 hours
        abandoned = Bag.objects.filter(updated_at__lt=cutoff, checkout_completed=False)
        count = 0

        for bag in abandoned:
            user = bag.user
            # Only send if user is logged in and has an email address
            if user and user.email:
                store_slug = bag.store
                branding = get_store_branding(store_slug)
                subject = f"Come back to {branding['name']} — you left items in your bag!"

                # Build cart items list and total
                items = []
                total = 0
                # Use select_related for product to avoid N+1 queries
                bag_items = bag.items.select_related('product').all()
                for item in bag_items:
                    item_total = item.total
                    items.append({
                        'name': item.product.name,
                        'quantity': item.quantity,
                        'size': item.size,
                        'total': item_total,
                    })
                    total += item_total

                # Skip empty bags
                if not items:
                    continue

                # Build cart URL (absolute)
                live_link = getattr(settings, 'LIVE_LINK', 'https://orderimo.com')
                # Ensure live_link ends without trailing slash
                live_link = live_link.rstrip('/')
                cart_url = f'{live_link}/{store_slug}/bag/'

                context = {
                    'branding': branding,
                    'cart_items': items,
                    'cart_total': total,
                    'cart_url': cart_url,
                }

                html = render_to_string('emails/abandoned_cart.html', context)
                # Send email with HTML content; plain-text body is empty (simplified)
                send_mail(
                    subject,
                    '',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html
                )
                count += 1

        self.stdout.write(f"Sent {count} abandoned cart emails")
