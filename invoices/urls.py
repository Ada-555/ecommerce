from django.urls import path
from . import views

urlpatterns = [
    path('<str:order_number>/', views.download_invoice, name='download_invoice'),
]
