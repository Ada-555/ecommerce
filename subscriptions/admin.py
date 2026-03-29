from django.contrib import admin
from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'product_name', 'interval', 'status',
        'current_period_end', 'created_at'
    ]
    list_filter = ['status', 'interval', 'created_at']
    search_fields = ['user__username', 'product_name', 'stripe_subscription_id']
    readonly_fields = ['created_at', 'stripe_subscription_id']
    ordering = ['-created_at']

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Subscription Details', {
            'fields': ('product_name', 'product_id', 'interval', 'status')
        }),
        ('Stripe Info', {
            'fields': ('stripe_subscription_id', 'stripe_customer_id')
        }),
        ('Timing', {
            'fields': ('current_period_end', 'created_at', 'cancelled_at')
        }),
    )
