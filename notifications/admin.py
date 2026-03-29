"""
Admin integration for manually triggering email notifications.
"""

from django.contrib import admin
from django.utils.html import format_html
from checkout.models import Order


@admin.action(description='📧 Send Shipping Notification')
def send_shipping_email(modeladmin, request, queryset):
    from notifications.utils import send_shipping_notification
    for order in queryset.filter(status='shipped'):
        send_shipping_notification(order)
    modeladmin.message_user(request, f"Shipping email sent for {queryset.count()} order(s).")


@admin.action(description='📧 Send Delivery Notification')
def send_delivery_email(modeladmin, request, queryset):
    from notifications.utils import send_delivery_notification
    for order in queryset.filter(status='delivered'):
        send_delivery_notification(order)
    modeladmin.message_user(request, f"Delivery email sent for {queryset.count()} order(s).")


# Register actions on OrderAdmin if imported there, otherwise they can be
# used via checkout/admin.py integration
