from django.contrib import admin
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'store', 'discount_type', 'discount_value',
        'min_order_amount', 'current_uses', 'max_uses',
        'valid_from', 'valid_until', 'is_active'
    ]
    list_filter = ['discount_type', 'is_active', 'store']
    search_fields = ['code', 'store__store_name']
    readonly_fields = ['created_at', 'current_uses']
    ordering = ['-created_at']

    fieldsets = (
        (None, {
            'fields': ('store', 'code', 'is_active')
        }),
        ('Discount', {
            'fields': ('discount_type', 'discount_value', 'min_order_amount')
        }),
        ('Usage Limits', {
            'fields': ('max_uses', 'current_uses')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
