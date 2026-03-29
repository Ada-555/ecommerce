from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import RedirectView

from stores import store_views
from stores.store_views import store_search
from home import views as home_views
from about import views as about_views
from products import views as product_views
from tracking import views as tracking_views
# from affiliates import views as affiliate_views  # Not ready yet
from . import views as ecommerce_views
from .sitemaps import ProductSitemap, CategorySitemap, BlogSitemap
# from analytics import views as analytics_views  # Not ready yet

urlpatterns = [
    # Root serves the home page
    path('', home_views.index, name='home'),
    # Currency setter
    path('set-currency/<str:currency>/', ecommerce_views.set_currency, name='set_currency'),

    # ========================
    # ORDERIMO STORE
    # ========================
    path('orderimo/', store_views.orderimo_home, name='orderimo_home'),
    path('orderimo/products/', store_views.store_products, {'store_slug': 'orderimo'}, name='orderimo_products'),
    path('orderimo/search/', store_search, {'store_slug': 'orderimo'}, name='orderimo_search'),
    path('orderimo/products/<int:product_id>/', product_views.product_detail, name='orderimo_product_detail'),
    path('orderimo/bag/', include('bag.urls')),
    path('orderimo/checkout/', include('checkout.urls')),
    path('orderimo/wishlist/', include('wishlist.urls')),
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
    path('petshop/search/', store_search, {'store_slug': 'petshop'}, name='petshop_search'),
    path('petshop/products/<int:product_id>/', product_views.product_detail, name='petshop_product_detail'),
    path('petshop/bag/', include('bag.urls')),
    path('petshop/checkout/', include('checkout.urls')),
    path('petshop/wishlist/', include('wishlist.urls')),
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
    path('digital/search/', store_search, {'store_slug': 'digital'}, name='digital_search'),
    path('digital/products/<int:product_id>/', product_views.product_detail, name='digital_product_detail'),
    path('digital/bag/', include('bag.urls')),
    path('digital/checkout/', include('checkout.urls')),
    path('digital/wishlist/', include('wishlist.urls')),
    path('digital/about/', about_views.about, name='digital_about'),
    path('digital/blog/', include('blog.urls')),
    path('digital/contact/', about_views.contact, name='digital_contact'),
    path('digital/faq/', about_views.faq, name='digital_faq'),
    path('digital/privacy/', about_views.privacy_policy, name='digital_privacy'),
    path('digital/terms/', about_views.terms, name='digital_terms'),
    path('digital/cookies/', about_views.cookies, name='digital_cookies'),
    path('digital/accept-cookies/', about_views.accept_cookies, name='digital_accept_cookies'),

    # ========================
    # GLOBAL / LEGACY (redirect to orderimo store)
    # ========================
    path('order/<str:order_number>/track/', tracking_views.track_order, name='track_order'),
    path('products/', include('products.urls')),
    path('bag/', include('bag.urls')),
    path('wishlist/', include('wishlist.urls')),
    path('checkout/', include('checkout.urls')),
    path('blog/', include('blog.urls')),
    path('about/', include('about.urls')),
    path('stores/', include('stores.urls')),
    path('accounts/', include('allauth.urls')),
    path('profiles/', include('profiles.urls')),
    path('avatar/', include('avatar.urls')),
    # path('newsletter/', include('newsletter.urls')),
    # path('', include('comparison.urls')),
    # path('', include('subscriptions.urls')),
    # Affiliate URLs disabled until app is implemented
    # path('accounts/affiliate/', affiliate_views.affiliate_dashboard, name='affiliate_dashboard'),
    # path('accounts/affiliate/create/', affiliate_views.become_affiliate, name='become_affiliate'),
    # path('affiliate/<str:code>/', affiliate_views.affiliate_landing, name='affiliate_landing'),
    path("admin/analytics/", analytics_views.analytics_dashboard, name="analytics_dashboard"),
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': {
        'products': ProductSitemap,
        'categories': CategorySitemap,
        'blog': BlogSitemap,
    }}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
