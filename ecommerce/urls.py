"""ecommerce URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from .views import handler404
from .sitemaps import ProductSitemap, CategorySitemap, BlogSitemap
from avatar.views import CustomSignupView
from stores import store_views


sitemaps = {
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'blog': BlogSitemap,
}


def robots_txt(request):
    return TemplateView.as_view(template_name='robots.txt', content_type='text/plain')(request)


urlpatterns = [
    # Store routes FIRST (more specific)
    path('orderimo/', store_views.orderimo_home, name='orderimo_home'),
    path('orderimo/products/', store_views.store_products, {'store_slug': 'orderimo'}, name='orderimo_products'),

    path('petshop/', store_views.petshop_home, name='petshop_home'),
    path('petshop/products/', store_views.store_products, {'store_slug': 'petshop'}, name='petshop_products'),

    path('digital/', store_views.digital_home, name='digital_home'),
    path('digital/products/', store_views.store_products, {'store_slug': 'digital'}, name='digital_products'),

    # Existing global routes
    path('admin/', admin.site.urls),
    path("accounts/signup/", CustomSignupView.as_view(), name="account_signup"),
    path('accounts/', include('allauth.urls')),
    path('', include('home.urls')),
    path('about/', include('about.urls')),
    path('blog/', include('blog.urls')),
    path('products/', include('products.urls')),
    path('bag/', include('bag.urls')),
    path('checkout/', include('checkout.urls')),
    path('profile/', include('profiles.urls')),
    path('avatar/', include('avatar.urls')),
    path('accounts/', include('accounts.urls')),
    path('stores/', include('stores.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', robots_txt, name='robots'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'ecommerce.views.handler404'
