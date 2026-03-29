from django.shortcuts import render
from products.models import Product, Category


STORE_META = {
    'orderimo': {
        'primary': '#00b4d8',
        'secondary': '#0077b6',
        'accent': '#90e0ef',
        'dark': '#0a0a0f',
        'card': '#12121a',
    },
    'petshop-ie': {
        'primary': '#228B22',
        'secondary': '#2d9a3e',
        'accent': '#90EE90',
        'dark': '#0f1a0f',
        'card': '#1a2a1a',
    },
    'digitalhub': {
        'primary': '#800080',
        'secondary': '#da70d6',
        'accent': '#ff69b4',
        'dark': '#08080f',
        'card': '#10101a',
    },
}


def orderimo_home(request):
    featured = Product.objects.filter(store='orderimo', featured=True).exclude(image='').exclude(image__isnull=True)[:8]
    new_arrivals = Product.objects.filter(store='orderimo').exclude(category__isnull=True).order_by('-id')[:8]
    return render(request, 'stores/orderimo/home.html', {
        'featured': featured,
        'new_arrivals': new_arrivals,
        'store': 'orderimo',
        'store_name': 'Orderimo',
    })


def petshop_home(request):
    featured = Product.objects.filter(store='petshop-ie', featured=True).exclude(image='').exclude(image__isnull=True)[:8]
    new_arrivals = Product.objects.filter(store='petshop-ie').exclude(category__isnull=True).order_by('-id')[:8]
    return render(request, 'stores/petshop/home.html', {
        'featured': featured,
        'new_arrivals': new_arrivals,
        'store': 'petshop-ie',
        'store_name': 'PetShop Ireland',
    })


def digital_home(request):
    featured = Product.objects.filter(store='digitalhub', featured=True).exclude(image='').exclude(image__isnull=True)[:8]
    new_arrivals = Product.objects.filter(store='digitalhub').exclude(category__isnull=True).order_by('-id')[:8]
    return render(request, 'stores/digital/home.html', {
        'featured': featured,
        'new_arrivals': new_arrivals,
        'store': 'digitalhub',
        'store_name': 'DigitalHub',
    })


def store_products(request, store_slug):
    store_map = {'orderimo': 'orderimo', 'petshop': 'petshop-ie', 'digital': 'digitalhub'}
    store_name_map = {'orderimo': 'Orderimo', 'petshop': 'PetShop Ireland', 'digital': 'DigitalHub'}
    db_store = store_map.get(store_slug, 'orderimo')
    meta = STORE_META.get(db_store, STORE_META['orderimo'])
    products = Product.objects.filter(store=db_store).select_related('category')
    return render(request, 'stores/products.html', {
        'products': products,
        'store': db_store,
        'store_name': store_name_map.get(store_slug, store_slug.title()),
        'store_slug': store_slug,
        'store_primary': meta['primary'],
        'store_secondary': meta['secondary'],
        'store_accent': meta['accent'],
        'store_dark': meta['dark'],
        'store_card': meta['card'],
    })
