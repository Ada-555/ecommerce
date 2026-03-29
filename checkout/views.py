import json
import stripe
import hashlib
import hmac
import urllib.parse

from django.shortcuts import (
    render, redirect, reverse, get_object_or_404, HttpResponse
)
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.views.decorators.cache import never_cache
from django_ratelimit.decorators import ratelimit

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from bag.contexts import bag_contents
from notifications.utils import send_order_confirmation


def _create_stripe_checkout_session(request, order, current_bag):
    """Create a Stripe Checkout Session (card + crypto via Stripe)."""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    total = current_bag['grand_total']

    # Build line items description
    line_items = []
    bag = request.session.get('bag', {})
    for item_id, item_data in bag.items():
        try:
            product = Product.objects.get(id=item_id)
            if isinstance(item_data, int):
                qty = item_data
                size = None
            else:
                qty = sum(item_data['items_by_size'].values())
                size = None
            line_items.append({
                'price_data': {
                    'currency': settings.STRIPE_CURRENCY.lower(),
                    'product_data': {'name': product.name},
                    'unit_amount': int(product.price * 100),
                },
                'quantity': qty,
            })
        except Product.DoesNotExist:
            pass

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card', 'crypto'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri(
            reverse('checkout_success', args=[order.order_number])
        ) + '?payment=stripe_crypto',
        cancel_url=request.build_absolute_uri(reverse('checkout')),
        customer_email=order.email,
        metadata={
            'order_number': order.order_number,
            'payment_method': 'stripe_crypto',
            'bag': json.dumps(bag),
        },
        shipping_options=[
            {
                'shipping_rate_data': {
                    'type': 'fixed_amount',
                    'fixed_amount': {
                        'amount': int(current_bag['delivery_cost'] * 100),
                        'currency': settings.STRIPE_CURRENCY.lower(),
                    },
                    'display_name': 'Standard Delivery',
                },
            },
        ] if current_bag['delivery_cost'] > 0 else [],
    )
    return checkout_session


def _create_coingate_order(request, order, current_bag):
    """
    Create a CoinGate payment order for XMR.
    CoinGate uses a redirect-based flow: user is redirected to CoinGate
    to pay, then CoinGate calls our callback URL to confirm payment.
    """
    import requests

    coingate_api_key = getattr(settings, 'COINGATE_API_KEY', None)
    if not coingate_api_key:
        return None

    total = current_bag['grand_total']
    callback_url = request.build_absolute_uri(reverse('coingate_callback'))
    redirect_url = request.build_absolute_uri(
        reverse('checkout_success', args=[order.order_number])
    ) + '?payment=coingate_xmr'

    payload = {
        'order_id': order.order_number,
        'price_amount': str(total),
        'price_currency': 'EUR',
        'receive_currency': 'XMR',
        'callback_url': callback_url,
        'cancel_url': redirect_url,
        'success_url': redirect_url,
        'title': f'Order {order.order_number}',
        'description': f'Order {order.order_number} - {order.full_name}',
    }

    try:
        response = requests.post(
            'https://api.coingate.com/v2/orders',
            auth=(coingate_api_key, ''),
            data=payload,
            timeout=10,
        )
        if response.status_code in (200, 201):
            data = response.json()
            # CoinGate returns a payment_url to redirect the user
            return data.get('payment_url')
    except Exception:
        pass

    return None


@require_POST
@ratelimit(key='post:client_secret', rate='10/m', method='POST', block=True)
def cache_checkout_data(request):
    """ Cache checkout """
    try:
        # pid is the payment ID
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


@never_cache
@ratelimit(key='post:full_name', rate='5/m', method='POST', block=True)
@ratelimit(key='ip', rate='30/m', method='POST', block=True)
def _get_store_from_request(request):
    """Infer the store slug from the request path."""
    path = request.path_info
    if '/petshop/' in path:
        return 'petshop-ie'
    elif '/digital/' in path:
        return 'digitalhub'
    else:
        return 'orderimo'


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    payment_method = request.POST.get('payment_method', 'card')

    if request.method == 'POST':
        bag = request.session.get('bag', {})

        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.payment_method = payment_method
            order.original_bag = json.dumps(bag)
            # Set store based on URL path
            order.store = _get_store_from_request(request)

            current_bag = bag_contents(request)

            if payment_method == 'card':
                # Standard card payment via Stripe PaymentIntent
                pid = request.POST.get('client_secret', '').split('_secret')[0]
                order.stripe_pid = pid
                order.payment_status = 'paid'
                order.save()
                _create_or_update_line_items(request, order, bag)

            elif payment_method == 'stripe_crypto':
                # Stripe Checkout Session for BTC/USDC
                order.save()  # Save first to get order_number
                _create_or_update_line_items(request, order, bag)
                session = _create_stripe_checkout_session(request, order, current_bag)
                return redirect(session.url)

            elif payment_method == 'coingate_xmr':
                # CoinGate XMR redirect flow
                order.payment_status = 'pending'
                order.save()
                _create_or_update_line_items(request, order, bag)
                coingate_url = _create_coingate_order(request, order, current_bag)
                if coingate_url:
                    return redirect(coingate_url)
                else:
                    messages.error(request, (
                        'Crypto payment service is temporarily unavailable. '
                        'Please choose card payment instead.'))
                    return redirect(reverse('checkout'))

            request.session['save_info'] = 'save-info' in request.POST
            return redirect(
                reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')
    else:
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(
                request, "There's nothing in your bag at the moment")
            return redirect(reverse('products'))

        current_bag = bag_contents(request)
        total = current_bag['grand_total']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        # Attempt to prefill the form with any info from the user's profile
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                    'town_or_city': profile.default_town_or_city,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'county': profile.default_county,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


def _create_or_update_line_items(request, order, bag):
    """Helper: create OrderLineItems from bag data."""
    for item_id, item_data in bag.items():
        try:
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
        except Product.DoesNotExist:
            messages.error(request, (
                "One of the products in your bag wasn't found in "
                "our database. Please call us for assistance!"))
            order.delete()
            return


def checkout_success(request, order_number):
    """
    Handle successful checkouts.
    Sends order confirmation email via notifications utils.
    """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)

    # Truncate the order number to 16 characters
    truncated_order_number = order_number[:16]

    # Read crypto payment indicator from query string
    payment_type = request.GET.get('payment', order.payment_method)

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        # Attach the user's profile to the order
        order.user_profile = profile
        order.save()

        # Save the user's info
        if save_info:
            profile_data = {
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    if payment_type == 'coingate_xmr':
        messages.success(request, f'Order {truncated_order_number}... — '
            'Your XMR payment is being processed. '
            'You will receive a confirmation once CoinGate confirms the transaction.')
    else:
        messages.success(request, f'Order successfully processed! \
            Your order number is {truncated_order_number}... A confirmation \
            email will be sent to {order.email}.')

    if 'bag' in request.session:
        del request.session['bag']

    # Send order confirmation email (via notifications app)
    send_order_confirmation(order)

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'payment_type': payment_type,
    }

    return render(request, template, context)


@require_POST
def coingate_callback(request):
    """
    CoinGate IPN callback — called by CoinGate when XMR payment is received.
    Updates the order's payment_status to 'paid' and stores the txid.
    """
    import requests

    coingate_api_key = getattr(settings, 'COINGATE_API_KEY', None)
    if not coingate_api_key:
        return HttpResponse('CoinGate not configured', status=400)

    # Verify CoinGate signature (idempotency key in X-GOIPN-IDEMPOTENCY)
    # CoinGate sends POST with order_id, status, etc.
    order_id = request.POST.get('order_id')
    status = request.POST.get('status')
    tx_id = request.POST.get('tx_id', '')
    amount = request.POST.get('receive_amount', '')

    try:
        order = Order.objects.get(order_number=order_id)
    except Order.DoesNotExist:
        return HttpResponse('Order not found', status=404)

    # CoinGate statuses: 'created', 'pending', 'paid', 'failed', 'refunded'
    if status == 'paid':
        order.payment_status = 'paid'
        order.crypto_txid = tx_id
        if amount:
            order.crypto_amount = amount
        order.save()
        # Send confirmation email
        handler = StripeWH_Handler(request)
        handler._send_confirmation_email(order)

    return HttpResponse('OK', status=200)


def order_status(request, order_number):
    """Order status page for tracking orders."""
    order = get_object_or_404(Order, order_number=order_number)
    context = {'order': order}
    return render(request, 'checkout/order_status.html', context)
