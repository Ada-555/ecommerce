from django.urls import path
from . import views

urlpatterns = [
    path('', views.affiliate_dashboard, name='affiliate_dashboard'),
    path('register/', views.affiliate_register, name='affiliate_register'),
    path('<str:referral_code>/', views.affiliate_landing, name='affiliate_landing'),
]
