from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderLineItem


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
              'original_bag', 'stripe_pid',)

    list_display = ('order_number', 'date', 'full_name',
                    'order_total', 'delivery_cost',
                    'grand_total', 'status', 'store_badge')

    list_filter = ('status', 'date')

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
