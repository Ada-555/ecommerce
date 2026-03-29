from django.urls import path
from . import views

# Use path('') so this can be included at a store prefix like orderimo/compare/
# giving URLs: /orderimo/compare/, /orderimo/compare/add/<id>/, etc.
urlpatterns = [
    path('', views.compare_view, name='product_compare'),
    path('add/<int:product_id>/', views.add_to_compare, name='add_to_compare'),
    path('remove/<int:product_id>/', views.remove_from_compare, name='remove_from_compare'),
    path('clear/', views.clear_compare, name='clear_compare'),
]
