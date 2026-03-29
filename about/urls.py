from django.urls import path
from . import views

urlpatterns = [
    path('', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms, name='terms'),
    path('cookies/', views.cookies, name='cookies'),
    path('accept-cookies/', views.accept_cookies, name='accept_cookies'),
    path('create/', views.create_about_page, name='create_about_page'),
    # Store-specific about pages
    path('petshop-ie/', views.petshop_about, name='petshop_about'),
    path('digitalhub/', views.digitalhub_about, name='digitalhub_about'),
    path('<int:pk>/', views.about_page_detail, name='about_page_detail'),
    path('<int:pk>/delete/', views.delete_about_page, name='delete_about_page'),
    path('<int:pk>/edit/', views.edit_about_page, name='edit_about_page'),
]
