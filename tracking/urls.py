from django.urls import path
from . import views

urlpatterns = [
    path(
        'order/<str:order_number>/track/',
        views.track_order,
        name='track_order'),
    path(
        'order/<str:order_number>/verify/',
        views.verify_order_email,
        name='verify_order_email'),
]
