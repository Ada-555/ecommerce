from django.contrib import admin
from .models import Product, Category, ProductVariant
from django.utils.html import format_html


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('size', 'color', 'sku', 'price_override', 'stock_quantity', 'weight_kg')


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariantInline]
    list_display = (
        'pk',
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'has_sizes',
        'stock_quantity',
        'featured',
        'image_preview',
        'stock_status_display',
    )

    search_fields = ['sku', 'name', 'brand']
    list_filter = ('category', 'has_sizes', 'featured', 'new_arrival', 'best_seller')
    ordering = ('sku',)
    list_per_page = 50

    actions = [
        'products_have_sizes',
        'products_dont_have_sizes',
        'mark_as_featured',
        'mark_as_out_of_stock',
    ]

    fieldsets = (
        (None, {
            'fields': ('name', 'sku', 'brand', 'category')
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


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
