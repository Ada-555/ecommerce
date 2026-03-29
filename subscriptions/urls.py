from django.urls import path
from . import views

urlpatterns = [
    path('my-subscriptions/', views.my_subscriptions, name='my_subscriptions'),
    path('cancel/<int:subscription_id>/', views.cancel_subscription, name='cancel_subscription'),
    path('success/<int:product_id>/', views.subscription_success, name='subscription_success'),
    path('subscribe/<int:product_id>/', views.subscribe, name='subscribe'),
]
