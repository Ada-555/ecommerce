from django.contrib import admin
from .models import StoreConfig


@admin.register(StoreConfig)
class StoreConfigAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'slug', 'theme', 'is_active']
    list_editable = ['is_active', 'theme']
    prepopulated_fields = {'slug': ('store_name',)}
