from django.shortcuts import redirect


VALID_STORES = ['orderimo', 'petshop-ie', 'digitalhub']


def set_active_store(request, store_slug):
    """Set the active store in session and redirect to home."""
    if store_slug in VALID_STORES:
        request.session['active_store'] = store_slug
    else:
        # Default to orderimo for unknown slugs
        request.session['active_store'] = 'orderimo'
    return redirect('home')


def get_store_context(request):
    """Return context dict with active store info."""
    store_slug = request.session.get('active_store', 'orderimo')
    return {
        'active_store': store_slug,
        'active_store_name': {
            'orderimo': 'Orderimo',
            'petshop-ie': 'PetShop Ireland',
            'digitalhub': 'DigitalHub',
        }.get(store_slug, 'Orderimo'),
        'active_store_color': {
            'orderimo': '#00FFFF',
            'petshop-ie': '#228B22',
            'digitalhub': '#800080',
        }.get(store_slug, '#00FFFF'),
    }
