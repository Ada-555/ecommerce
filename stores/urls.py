from django.urls import path
from . import views

urlpatterns = [
    path('set-store/<str:store_slug>/', views.set_active_store, name='set_active_store'),
]
