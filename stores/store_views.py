from django.shortcuts import render
from products.models import Product

def orderimo_home(request):
    products = Product.objects.filter(store='orderimo').select_related('category').order_by('-created_at')
    featured = list(products.filter(featured=True)[:4])
    new_arrivals = list(products[:8])
    if not featured:
        featured = list(products.order_by('-created_at')[:4])
    return render(request, 'stores/orderimo/home.html', {
        'featured': featured,
        'new_arrivals': new_arrivals,
        'store': 'orderimo',
    })

def petshop_home(request):
    products = Product.objects.filter(store='petshop-ie').select_related('category').order_by('-created_at')
    featured = list(products.filter(featured=True)[:4])
    new_arrivals = list(products[:8])
    return render(request, 'stores/petshop/home.html', {
        'featured': featured,
        'new_arrivals': new_arrivals,
        'store': 'petshop-ie',
    })

def digital_home(request):
    products = Product.objects.filter(store='digitalhub').select_related('category').order_by('-created_at')
    featured = list(products.filter(featured=True)[:4])
    new_arrivals = list(products[:8])
    return render(request, 'stores/digital/home.html', {
        'featured': featured,
        'new_arrivals': new_arrivals,
        'store': 'digitalhub',
    })

def store_products(request, store_slug):
    store_map = {'orderimo': 'orderimo', 'petshop': 'petshop-ie', 'digital': 'digitalhub'}
    db_store = store_map.get(store_slug, 'orderimo')
    products = Product.objects.filter(store=db_store).select_related('category').order_by('-created_at')
    store_names = {'orderimo': 'Orderimo', 'petshop': 'PetShop Ireland', 'digital': 'DigitalHub'}
    return render(request, 'stores/products.html', {
        'products': products,
        'store': db_store,
        'store_name': store_names.get(store_slug, store_slug.title()),
    })
