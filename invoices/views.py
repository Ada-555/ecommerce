from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.conf import settings
import os
from checkout.models import Order
from .utils import generate_invoice_pdf


def download_invoice(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    # Permission check: user owns order or is staff
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to download invoices.")
    if not request.user.is_staff:
        if order.user_profile is None or order.user_profile.user != request.user:
            return HttpResponseForbidden("You do not have permission to access this invoice.")
    pdf_path = os.path.join(settings.MEDIA_ROOT, f'invoices/inv-{order_number}.pdf')
    if not os.path.exists(pdf_path):
        generate_invoice_pdf(order)
    with open(pdf_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="inv-{order_number}.pdf"'
        return response
