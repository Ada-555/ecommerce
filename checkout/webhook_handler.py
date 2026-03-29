from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile
from subscriptions.models import Subscription

import stripe
import json
import time


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        # Get the Charge object
        stripe_charge = stripe.Charge.retrieve(
            intent.latest_charge
        )

        billing_details = stripe_charge.billing_details  # updated
        shipping_details = intent.shipping
        grand_total = round(stripe_charge.amount / 100, 2)  # updated

        # Clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # Update profile information if save_info was checked
        profile = None
        username = intent.metadata.username
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)
            if save_info:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = shipping_details.address.line1
                profile.default_street_address2 = shipping_details.address.line2
                profile.default_county = shipping_details.address.state
                profile.save()

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    user_profile=profile,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'''Webhook received: {event["type"]}
                 | SUCCESS: Verified order already in database''',
                status=200)
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'''Webhook received: {event["type"]}
             | SUCCESS: Created order in webhook''',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)

    def handle_invoice_payment_succeeded(self, event):
        """
        Handle the invoice.payment_succeeded webhook from Stripe
        This indicates a successful recurring subscription payment.
        """
        invoice = event.data.object
        stripe_subscription_id = invoice.subscription

        # Find the local subscription record
        try:
            subscription = Subscription.objects.get(stripe_subscription_id=stripe_subscription_id)
            subscription.status = 'active'
            # Update the current_period_end from invoice's period_end
            import datetime
            period_end = datetime.datetime.fromtimestamp(invoice.lines.data[0].period.end, tz=datetime.timezone.utc)
            subscription.current_period_end = period_end
            subscription.save()
        except Subscription.DoesNotExist:
            # If no local record, you might want to create one based on customer and product info
            # For now, just log
            pass

        return HttpResponse(
            content=f'Webhook received: {event["type"]} | Subscription payment succeeded',
            status=200)

    def handle_customer_subscription_deleted(self, event):
        """
        Handle the customer.subscription.deleted webhook from Stripe
        This indicates a subscription was cancelled.
        """
        stripe_subscription = event.data.object
        stripe_subscription_id = stripe_subscription.id

        try:
            subscription = Subscription.objects.get(stripe_subscription_id=stripe_subscription_id)
            subscription.status = 'cancelled'
            from django.utils import timezone
            subscription.cancelled_at = timezone.now()
            subscription.save()
        except Subscription.DoesNotExist:
            pass

        return HttpResponse(
            content=f'Webhook received: {event["type"]} | Subscription cancelled',
            status=200)

    def handle_invoice_payment_failed(self, event):
        """
        Handle the invoice.payment_failed webhook from Stripe
        This indicates a failed subscription payment.
        """
        invoice = event.data.object
        stripe_subscription_id = invoice.subscription

        try:
            subscription = Subscription.objects.get(stripe_subscription_id=stripe_subscription_id)
            subscription.status = 'past_due'  # or 'unpaid' depending on your logic
            subscription.save()
        except Subscription.DoesNotExist:
            pass

        return HttpResponse(
            content=f'Webhook received: {event["type"]} | Subscription payment failed',
            status=200)
