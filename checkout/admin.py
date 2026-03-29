from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderLineItem, AbandonedCart


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)


class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)

    readonly_fields = ('order_number', 'date',
                       'delivery_cost', 'order_total',
                       'grand_total', 'original_bag', 'stripe_pid',)

    fields = ('order_number', 'user_profile', 'date', 'full_name',
              'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'status',
              'delivery_cost', 'order_total', 'grand_total',
              'original_bag', 'stripe_pid',
              'payment_method', 'payment_status',
              'crypto_txid', 'crypto_amount', 'crypto_address',)

    list_display = ('order_number', 'date', 'full_name',
                    'order_total', 'delivery_cost',
                    'grand_total', 'status', 'payment_status_badge', 'store_badge')

    list_filter = ('status', 'date', 'payment_method', 'payment_status')

    ordering = ('-date',)

    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        store_scope = request.GET.get('store') or request.COOKIES.get('admin_store_scope', '')
        if store_scope:
            qs = qs.filter(lineitems__product__store=store_scope).distinct()
        return qs

    def store_badge(self, obj):
        # Derive store from the first line item's product
        first_item = obj.lineitems.select_related('product').first()
        if not first_item:
            return format_html('<span style="color:#ccc;">—</span>')
        store = first_item.product.store
        colors = {
            'orderimo': '#00FFFF',
            'petshop-ie': '#90EE90',
            'digitalhub': '#DDA0DD',
        }
        names = {
            'orderimo': 'Orderimo',
            'petshop-ie': 'PetShop Ireland',
            'digitalhub': 'DigitalHub',
        }
        color = colors.get(store, '#cccccc')
        name = names.get(store, store)
        return format_html(
            '<span style="background:{0}22; color:{0}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:bold;">{1}</span>',
            color, name
        )
    store_badge.short_description = 'Store'

    def payment_status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'paid': '#00FF00',
            'failed': '#FF4444',
            'refunded': '#AAAAAA',
        }
        color = colors.get(obj.payment_status, '#cccccc')
        label = obj.get_payment_status_display()
        return format_html(
            '<span style="background:{0}22; color:{0}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:bold;">{1}</span>',
            color, label
        )
    payment_status_badge.short_description = 'Payment'

    @admin.action(description='Mark selected orders as Processing')
    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')

    @admin.action(description='Mark selected orders as Shipped')
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')

    @admin.action(description='Mark selected orders as Delivered')
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')


admin.site.register(Order, OrderAdmin)


@admin.register(AbandonedCart)
class AbandonedCartAdmin(admin.ModelAdmin):
    list_display = ('email', 'store', 'bag_total', 'last_activity',
                    'is_converted', 'reminder_sent', 'reminder_sent_at')
    list_filter = ('store', 'is_converted', 'reminder_sent')
    search_fields = ('email',)
    readonly_fields = ('bag_snapshot', 'last_activity', 'reminder_sent_at',
                       'converted_at')
    ordering = ('-last_activity',)
    actions = ['resend_reminder']

    @admin.action(description='Re-send reminder email to selected carts')
    def resend_reminder(self, request, queryset):
        from .management.commands.send_abandoned_cart_emails import _build_cart_items
        from notifications.utils import _send_html_email, get_store_branding
        from django.utils import timezone
        from django.conf import settings

        for cart in queryset.filter(is_converted=False).exclude(email=''):
            branding = get_store_branding(cart.store)
            cart_items = _build_cart_items(cart.bag_snapshot)
            if not cart_items:
                continue
            live_link = getattr(settings, 'LIVE_LINK', 'https://orderimo.com')
            success = _send_html_email(
                subject=f'Your cart at {branding["name"]} is waiting! 🛒',
                to_email=cart.email,
                html_template='emails/abandoned_cart.html',
                text_template='emails/abandoned_cart.txt',
                context={
                    'cart_items': cart_items,
                    'cart_total': cart.bag_total,
                    'cart_url': f'{live_link}bag/',
                    'recovery_code': cart.recovery_coupon_code,
                    'recovery_url': f'{live_link}bag/?coupon={cart.recovery_coupon_code}' if cart.recovery_coupon_code else None,
                    'live_link': live_link,
                },
                branding=branding,
            )
            if success:
                cart.reminder_sent = True
                cart.reminder_sent_at = timezone.now()
                cart.save(update_fields=['reminder_sent', 'reminder_sent_at'])
        self.message_user(request, 'Reminder emails queued.')

