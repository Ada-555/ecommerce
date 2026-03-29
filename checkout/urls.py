from django.urls import path
from . import views
from .webhooks import webhook
from invoices.views import download_invoice

urlpatterns = [
    path(
        '',
        views.checkout,
        name='checkout'),
    # Disabled: apply_coupon view not implemented; coupons handled in checkout view
    # path(
    #     'apply_coupon/',
    #     views.apply_coupon,
    #     name='apply_coupon'),
    path(
        'checkout_success/<order_number>/',
        views.checkout_success,
        name='checkout_success'),
    path(
        'cache_checkout_data/',
        views.cache_checkout_data,
        name='cache_checkout_data'),
    path(
        'wh/',
        webhook,
        name='webhook'),
    path(
        'order/<str:order_number>/',
        views.order_status,
        name='order_status'),
    path(
        'order/<str:order_number>/invoice/',
        download_invoice,
        name='download_invoice'),
    path(
        'coingate/callback/',
        views.coingate_callback,
        name='coingate_callback'),
]
