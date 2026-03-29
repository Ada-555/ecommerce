from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscribe/', views.subscribe, name='newsletter_subscribe'),  # alias for compatibility
]
