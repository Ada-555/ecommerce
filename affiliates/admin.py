from django.contrib import admin
from .models import Affiliate, AffiliateReferral


@admin.register(Affiliate)
class AffiliateAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'referral_code', 'commission_rate',
        'is_active', 'created_at',
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'referral_code']
    readonly_fields = ['referral_code', 'created_at']
    ordering = ['-created_at']


@admin.register(AffiliateReferral)
class AffiliateReferralAdmin(admin.ModelAdmin):
    list_display = [
        'affiliate', 'order', 'commission_amount', 'status', 'created_at',
    ]
    list_filter = ['status', 'created_at']
    search_fields = [
        'affiliate__user__username', 'affiliate__referral_code',
        'order__order_number',
    ]
    readonly_fields = ['created_at']
    ordering = ['-created_at']
