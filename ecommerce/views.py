from django.shortcuts import render, redirect
from django.conf import settings


def handler404(request, exception):
    """ Error Handler 404 - Page Not Found """
    return render(request, "errors/404.html", status=404)


def set_currency(request, currency):
    """Set the active currency in session and redirect back."""
    if currency in settings.CURRENCIES:
        request.session['currency'] = currency
    return redirect(request.META.get('HTTP_REFERER', '/'))

