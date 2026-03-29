import stripe
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Subscription
from products.models import Product


@login_required
def my_subscriptions(request):
    """List all active subscriptions for the current user."""
    subscriptions = Subscription.objects.filter(user=request.user)
    context = {
        'subscriptions': subscriptions,
    }
    return render(request, 'subscriptions/my_subscriptions.html', context)


@login_required
def cancel_subscription(request, subscription_id):
    """Cancel a subscription via Stripe API."""
    subscription = get_object_or_404(
        Subscription, id=subscription_id, user=request.user
    )

    stripe.api_key = settings.STRIPE_SECRET_KEY

    if subscription.stripe_subscription_id:
        try:
            stripe.Subscription.delete(subscription.stripe_subscription_id)
            subscription.status = 'cancelled'
            subscription.cancelled_at = timezone.now()
            subscription.save()
            messages.success(request, 'Your subscription has been cancelled.')
        except stripe.error.StripeError as e:
            messages.error(request, f'Failed to cancel subscription: {e.user_message or str(e)}')
    else:
        # No Stripe subscription ID — just mark as cancelled locally
        subscription.status = 'cancelled'
        subscription.cancelled_at = timezone.now()
        subscription.save()
        messages.success(request, 'Your subscription has been cancelled.')

    return redirect(reverse('my_subscriptions'))


def _create_subscription_checkout_session(request, product):
    """Create a Stripe Subscription Checkout Session for a subscription product."""
    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout_session = stripe.checkout.Session.create(
        mode='subscription',
        line_items=[{
            'price': product.stripe_price_id,
            'quantity': 1,
        }],
        success_url=request.build_absolute_uri(
            reverse('subscription_success', args=[product.id])
        ) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('my_subscriptions')),
        customer_email=request.user.email if request.user.is_authenticated else None,
        metadata={
            'product_id': product.id,
            'user_id': request.user.id if request.user.is_authenticated else '',
            'interval': product.subscription_interval,
        },
    )
    return checkout_session


@login_required
def subscribe(request, product_id):
    """Redirect to Stripe Subscription Checkout for a subscription product."""
    product = get_object_or_404(Product, id=product_id)
    if not product.is_subscription or not product.stripe_price_id:
        messages.error(request, "This product is not available as a subscription.")
        return redirect(reverse('product_detail', args=[product_id]))

    checkout_session = _create_subscription_checkout_session(request, product)
    return redirect(checkout_session.url)


@login_required
def subscription_success(request, product_id):
    """Handle successful subscription checkout."""
    session_id = request.GET.get('session_id')
    product = get_object_or_404(Product, id=product_id)

    if session_id:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            customer_id = session.customer
            subscription_id = session.subscription

            # Create local subscription record
            Subscription.objects.update_or_create(
                user=request.user,
                stripe_subscription_id=subscription_id,
                defaults={
                    'stripe_customer_id': customer_id,
                    'product_name': product.name,
                    'product_id': product.id,
                    'interval': product.subscription_interval,
                    'status': 'active',
                }
            )
        except stripe.error.StripeError:
            pass

    messages.success(
        request,
        f'You have successfully subscribed to {product.name}! '
        'Your subscription is now active.'
    )
    return redirect(reverse('my_subscriptions'))
