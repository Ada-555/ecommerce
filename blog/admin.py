from django.contrib import admin
from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import BlogPage, BlogSubscriber
from django.utils.html import format_html
from django.template.defaultfilters import truncatechars
from datetime import datetime


class BlogPageAdminForm(forms.ModelForm):
    """ Add CKEditor to admin for blog page """
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = BlogPage
        fields = '__all__'


class BlogPageAdmin(admin.ModelAdmin):
    """ Admin for blog page """
    form = BlogPageAdminForm
    list_display = [
        'pk', 'title', 'store_badge', 'is_published', 'newsletter_sent_at_display', 'created_at_days_ago', 'short_content', 'preview_image']
    list_display_links = ['pk', 'title']
    readonly_fields = ['preview_image']
    search_fields = ['title', 'content']
    list_filter = ['store', 'is_published', 'created_at']
    list_editable = ['is_published']

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

    def created_at_days_ago(self, obj):
        days_ago = (datetime.now().date() - obj.created_at.date()).days
        return f"{days_ago} days ago"
    created_at_days_ago.short_description = 'Created At'

    def short_content(self, obj):
        return format_html(truncatechars(obj.content, 100))
    short_content.short_description = 'Content'

    def preview_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;">',
                obj.image.url)
        return "No Image"
    preview_image.short_description = 'Preview Image'

    def is_published_badge(self, obj):
        color = '#00b4d8' if obj.is_published else '#555'
        label = 'Published' if obj.is_published else 'Draft'
        return format_html(
            '<span style="background:{}22; color:{}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:bold;">{}</span>',
            color, color, label
        )
    is_published_badge.short_description = 'Status'

    def newsletter_sent_at_display(self, obj):
        if obj.newsletter_sent_at:
            return obj.newsletter_sent_at.strftime('%Y-%m-%d %H:%M')
        return '—'
    newsletter_sent_at_display.short_description = 'Newsletter Sent'

    ordering = ('-created_at', )


admin.site.register(BlogPage, BlogPageAdmin)


class BlogSubscriberAdmin(admin.ModelAdmin):
    """ Admin for blog newsletter subscribers """
    list_display = ['email', 'name', 'store_badge', 'is_active', 'subscribed_at']
    list_filter = ['store', 'is_active', 'subscribed_at']
    search_fields = ['email', 'name']
    list_editable = ['is_active']

    def store_badge(self, obj):
        colors = {
            'orderimo': '#00FFFF',
            'petshop-ie': '#90EE90',
            'digitalhub': '#DDA0DD',
        }
        color = colors.get(obj.store, '#cccccc')
        return format_html(
            '<span style="background:{}22; color:{}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:bold;">{}</span>',
            color, color, obj.store or 'orderimo'
        )
    store_badge.short_description = 'Store'


admin.site.register(BlogSubscriber, BlogSubscriberAdmin)
