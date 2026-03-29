from django.contrib import admin
from .models import Product, Category, ProductVariant, Review
from django.utils.html import format_html
from django.db.models import F
from django.core.mail import send_mail
from django.conf import settings


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('size', 'color', 'sku', 'price_override', 'stock_quantity', 'weight_kg')


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariantInline]
    list_display = (
        'name', 'sku', 'store_badge', 'category', 'price', 'stock_quantity',
        'stock_status', 'is_featured',
    )
    list_editable = ('price', 'stock_quantity')
    search_fields = ('name', 'sku')
    list_filter = ('store', 'category', 'featured', 'new_arrival', 'best_seller')
    ordering = ('sku',)
    list_per_page = 50

    actions = [
        'mark_out_of_stock',
        'mark_in_stock',
        'alert_low_stock',
        'products_have_sizes',
        'products_dont_have_sizes',
        'mark_as_featured',
        'mark_as_out_of_stock',
    ]

    fieldsets = (
        (None, {
            'fields': ('name', 'sku', 'store', 'brand', 'category')
        }),
        ('Pricing & Media', {
            'fields': ('price', 'rating', 'image', 'image_url')
        }),
        ('Stock & Inventory', {
            'fields': ('stock_quantity', 'low_stock_threshold', 'featured', 'new_arrival', 'best_seller')
        }),
        ('Details', {
            'fields': ('description', 'has_sizes', 'weight_kg', 'views_count')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        store_scope = request.GET.get('store') or request.COOKIES.get('admin_store_scope', '')
        if store_scope:
            qs = qs.filter(store=store_scope)
        return qs

    def store_badge(self, obj):
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
        color = colors.get(obj.store, '#cccccc')
        name = names.get(obj.store, obj.store)
        return format_html(
            '<span style="background:{0}22; color:{0}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:bold;">{1}</span>',
            color, name
        )
    store_badge.short_description = 'Store'

    def stock_status(self, obj):
        if obj.stock_quantity == 0:
            return format_html('<span style="color:red;">Out of Stock</span>')
        elif obj.stock_quantity < obj.low_stock_threshold:
            return format_html('<span style="color:orange;">Low Stock</span>')
        return format_html('<span style="color:green;">In Stock</span>')
    stock_status.short_description = 'Stock'

    def is_featured(self, obj):
        return obj.featured
    is_featured.boolean = True
    is_featured.short_description = 'Featured'

    @admin.action(description='Mark selected as out of stock')
    def mark_out_of_stock(self, request, queryset):
        queryset.update(stock_quantity=0)
        self.message_user(request, f'{queryset.count()} products marked as out of stock.')

    @admin.action(description='Mark selected as in stock')
    def mark_in_stock(self, request, queryset):
        for obj in queryset:
            obj.stock_quantity = max(obj.stock_quantity, 10)
            obj.save()
        self.message_user(request, f'{queryset.count()} products marked as in stock.')

    @admin.action(description='Alert low stock (send email)')
    def alert_low_stock(self, request, queryset):
        low_stock = queryset.filter(stock_quantity__lt=F('low_stock_threshold'))
        if not low_stock.exists():
            self.message_user(request, 'No low stock products in selection.')
            return
        subject = 'Low Stock Alert — Orderimo'
        message = 'The following products are running low:\n'
        for p in low_stock:
            message += f'- {p.name}: {p.stock_quantity} left\n'
        send_mail(
            subject, message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=True
        )
        self.message_user(request, f'Alert sent for {low_stock.count()} products.')

    def products_have_sizes(self, request, queryset):
        queryset.update(has_sizes=True)
        self.message_user(request, "Sizes have been added to the selected products.")

    def products_dont_have_sizes(self, request, queryset):
        queryset.update(has_sizes=False)
        self.message_user(request, "Sizes have been removed from the selected products.")

    def mark_as_featured(self, request, queryset):
        queryset.update(featured=True)
        self.message_user(request, "Selected products marked as featured.")

    def mark_as_out_of_stock(self, request, queryset):
        queryset.update(stock_quantity=0)
        self.message_user(request, "Selected products marked as out of stock.")

    def stock_status_display(self, obj):
        status = obj.stock_status
        if status == 'In Stock':
            color = 'green'
        elif status == 'Low Stock':
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color, status
        )
    stock_status_display.short_description = 'Stock'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 60px; object-fit: cover;">',
                obj.image.url)
        return format_html('<span class="text-muted">—</span>')
    image_preview.short_description = 'Image'


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'friendly_name',
        'name',
        'display_order',
    )
    ordering = ('display_order', 'friendly_name')


class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'product',
        'size',
        'color',
        'sku',
        'price_override',
        'stock_quantity',
    )
    search_fields = ['sku', 'product__name']
    list_filter = ('size', 'color')


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'store_badge', 'approved', 'created_at')
    list_filter = ('approved', 'rating')
    list_editable = ('approved',)
    search_fields = ('user__username', 'product__name')
    actions = ['approve_selected']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        store_scope = request.GET.get('store') or request.COOKIES.get('admin_store_scope', '')
        if store_scope:
            qs = qs.filter(product__store=store_scope)
        return qs

    def store_badge(self, obj):
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
        color = colors.get(obj.product.store, '#cccccc')
        name = names.get(obj.product.store, obj.product.store)
        return format_html(
            '<span style="background:{0}22; color:{0}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:bold;">{1}</span>',
            color, name
        )
    store_badge.short_description = 'Store'

    @admin.action(description='Approve selected reviews')
    def approve_selected(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, f'{queryset.count()} reviews approved.')


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(Review, ReviewAdmin)
