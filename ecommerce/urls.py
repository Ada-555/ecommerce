from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from stores import store_views
from home import views as home_views
from about import views as about_views
from .sitemaps import ProductSitemap, CategorySitemap, BlogSitemap

urlpatterns = [
    # ========================
    # ORDERIMO STORE
    # ========================
    path('orderimo/', store_views.orderimo_home, name='orderimo_home'),
    path('orderimo/products/', store_views.store_products, {'store_slug': 'orderimo'}, name='orderimo_products'),
    path('orderimo/bag/', include('bag.urls')),
    path('orderimo/checkout/', include('checkout.urls')),
    path('orderimo/about/', about_views.about, name='orderimo_about'),
    path('orderimo/blog/', include('blog.urls')),
    path('orderimo/contact/', about_views.contact, name='orderimo_contact'),
    path('orderimo/faq/', about_views.faq, name='orderimo_faq'),
    path('orderimo/privacy/', about_views.privacy_policy, name='orderimo_privacy'),
    path('orderimo/terms/', about_views.terms, name='orderimo_terms'),
    path('orderimo/cookies/', about_views.cookies, name='orderimo_cookies'),
    path('orderimo/accept-cookies/', about_views.accept_cookies, name='orderimo_accept_cookies'),

    # ========================
    # PETSHOP IRELAND STORE
    # ========================
    path('petshop/', store_views.petshop_home, name='petshop_home'),
    path('petshop/products/', store_views.store_products, {'store_slug': 'petshop'}, name='petshop_products'),
    path('petshop/bag/', include('bag.urls')),
    path('petshop/checkout/', include('checkout.urls')),
    path('petshop/about/', about_views.about, name='petshop_about'),
    path('petshop/blog/', include('blog.urls')),
    path('petshop/contact/', about_views.contact, name='petshop_contact'),
    path('petshop/faq/', about_views.faq, name='petshop_faq'),
    path('petshop/privacy/', about_views.privacy_policy, name='petshop_privacy'),
    path('petshop/terms/', about_views.terms, name='petshop_terms'),
    path('petshop/cookies/', about_views.cookies, name='petshop_cookies'),
    path('petshop/accept-cookies/', about_views.accept_cookies, name='petshop_accept_cookies'),

    # ========================
    # DIGITALHUB STORE
    # ========================
    path('digital/', store_views.digital_home, name='digital_home'),
    path('digital/products/', store_views.store_products, {'store_slug': 'digital'}, name='digital_products'),
    path('digital/bag/', include('bag.urls')),
    path('digital/checkout/', include('checkout.urls')),
    path('digital/about/', about_views.about, name='digital_about'),
    path('digital/blog/', include('blog.urls')),
    path('digital/contact/', about_views.contact, name='digital_contact'),
    path('digital/faq/', about_views.faq, name='digital_faq'),
    path('digital/privacy/', about_views.privacy_policy, name='digital_privacy'),
    path('digital/terms/', about_views.terms, name='digital_terms'),
    path('digital/cookies/', about_views.cookies, name='digital_cookies'),
    path('digital/accept-cookies/', about_views.accept_cookies, name='digital_accept_cookies'),

    # ========================
    # GLOBAL / LEGACY ROUTES
    # ========================
    path('', home_views.index, name='home'),
    path('products/', include('products.urls')),
    path('bag/', include('bag.urls')),
    path('checkout/', include('checkout.urls')),
    path('blog/', include('blog.urls')),
    path('about/', include('about.urls')),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('sitemap.xml', include('ecommerce.sitemaps')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
