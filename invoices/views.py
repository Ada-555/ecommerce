from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from checkout.models import Order


def download_invoice(request, order_number):
    """
    Display an invoice as HTML page. Users can use browser's 'Print to PDF'
    to save as PDF file. Provides clean, print-friendly HTML invoice.
    """
    order = get_object_or_404(Order, order_number=order_number)

    # Permission check: user owns order or is staff
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to download invoices.")
    if not request.user.is_staff:
        if order.user_profile is None or order.user_profile.user != request.user:
            return HttpResponseForbidden("You do not have permission to access this invoice.")

    # Get store branding info
    store_branding = getattr(settings, 'STORE_BRANDING', {}).get(
        order.store,
        {
            'name': 'Orderimo',
            'address': 'Ireland',
            'email': 'info@orderimo.com',
            'phone': '+353 1 000 0000'
        }
    )

    context = {
        'order': order,
        'store_name': store_branding.get('name', 'Orderimo'),
        'store_address': store_branding.get('address', ''),
        'store_email': store_branding.get('email', ''),
        'store_phone': store_branding.get('phone', ''),
    }

    return render(request, 'invoices/invoice.html', context)
