from django.urls import path
from . import views

urlpatterns = [
    # Toggle must come before empty string to avoid matching '' first
    path('toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('', views.view_wishlist, name='wishlist'),
]
