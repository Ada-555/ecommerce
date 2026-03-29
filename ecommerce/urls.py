"""ecommerce URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap
from django.views.generic import TemplateView
from .views import handler404
from avatar.views import CustomSignupView
from products.models import Product
from blog.models import BlogPage


# Sitemap info dict
product_info = {
    'queryset': Product.objects.filter(stock_quantity__gt=0),
    'date_field': 'id',
}

blog_info = {
    'queryset': BlogPage.objects.all(),
    'date_field': 'created_at',
}

sitemaps = {
    'products': GenericSitemap(product_info, priority=0.7),
    'blog': GenericSitemap(blog_info, priority=0.5),
}

# Robots.txt
def robots_txt(request):
    return TemplateView.as_view(template_name='robots.txt', content_type='text/plain')(request)


urlpatterns = [
    path(
        'admin/', admin.site.urls),
    path(
        "accounts/signup/", CustomSignupView.as_view(), name="account_signup"),
    path(
        'accounts/', include('allauth.urls')),
    path(
        '', include('home.urls')),
    path(
        'about/', include('about.urls')),
    path(
        'blog/', include('blog.urls')),
    path(
        'products/', include('products.urls')),
    path(
        'bag/', include('bag.urls')),
    path(
        'checkout/', include('checkout.urls')),
    path(
        'profile/', include('profiles.urls')),
    path(
        'avatar/', include('avatar.urls')),
    path(
        'accounts/', include('accounts.urls')),
    path(
        'stores/', include('stores.urls')),
    path(
        'sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path(
        'robots.txt', robots_txt, name='robots'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'ecommerce.views.handler404'
