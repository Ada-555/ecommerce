from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.views.decorators.cache import never_cache

from checkout.models import Order


@never_cache
def track_order(request, order_number):
    """
    Public order tracking page.
    Customers enter their order number and email to view order status.
    """
    order = get_object_or_404(Order, order_number=order_number)

    # Email verification for public tracking
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        if email != order.email.lower():
            messages.error(request, 'The email address does not match this order.')
            return render(request, 'tracking/track_order.html', {
                'order_number': order_number,
                'order': None,
            })
        # Email verified — fall through to show order
    else:
        # GET request: check if email was already submitted via session
        verified_email = request.session.get('verified_order_email', '').lower()
        if verified_email != order.email.lower():
            # Show email verification form
            return render(request, 'tracking/track_order.html', {
                'order_number': order_number,
                'order': None,
                'show_verify': True,
            })

    # Store verified email in session
    request.session['verified_order_email'] = order.email.lower()

    # Build tracking timeline
    timeline = []
    status_order = ['pending', 'confirmed', 'shipped', 'out_for_delivery', 'delivered', 'cancelled']
    current_idx = status_order.index(order.status) if order.status in status_order else 0

    for idx, status in enumerate(status_order):
        status_labels = {
            'pending': ('Order Placed', 'fa-clock'),
            'confirmed': ('Order Confirmed', 'fa-check-circle'),
            'shipped': ('Shipped', 'fa-truck'),
            'out_for_delivery': ('Out for Delivery', 'fa-truck-fast'),
            'delivered': ('Delivered', 'fa-box-open'),
            'cancelled': ('Cancelled', 'fa-xmark-circle'),
        }
        label, icon = status_labels.get(status, (status.title(), 'fa-circle'))
        timeline.append({
            'status': status,
            'label': label,
            'icon': icon,
            'done': idx <= current_idx,
            'active': idx == current_idx and order.status != 'cancelled',
        })

    context = {
        'order': order,
        'timeline': timeline,
        'order_number': order_number,
    }
    return render(request, 'tracking/track_order.html', context)


def verify_order_email(request, order_number):
    """
    Handle email verification form submission.
    """
    email = request.POST.get('email', '').strip().lower()
    order = get_object_or_404(Order, order_number=order_number)

    if email != order.email.lower():
        messages.error(request, 'The email address does not match this order.')
        return render(request, 'tracking/track_order.html', {
            'order_number': order_number,
            'order': None,
            'show_verify': True,
        })

    request.session['verified_order_email'] = order.email.lower()
    return track_order(request, order_number)
