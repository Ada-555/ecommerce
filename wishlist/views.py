from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from products.models import Product
from .models import Wishlist


STORE_MAP = {'orderimo': 'orderimo', 'petshop': 'petshop-ie', 'digital': 'digitalhub'}
STORE_NAME_MAP = {'orderimo': 'Orderimo', 'petshop': 'PetShop Ireland', 'digital': 'DigitalHub'}


def _get_store_from_path(path):
    """Detect store slug from URL path."""
    if '/petshop/' in path:
        return 'petshop'
    elif '/digital/' in path:
        return 'digital'
    return 'orderimo'


def _build_context(store_slug):
    """Build standard context for wishlist views."""
    db_store = STORE_MAP.get(store_slug, 'orderimo')
    store_name = STORE_NAME_MAP.get(store_slug, 'Orderimo')
    from stores.store_views import STORE_META
    meta = STORE_META.get(db_store, STORE_META['orderimo'])
    return {
        'store_slug': store_slug,
        'store': db_store,
        'store_name': store_name,
        'store_primary': meta['primary'],
        'store_secondary': meta['secondary'],
        'store_accent': meta['accent'],
        'store_dark': meta['dark'],
        'store_card': meta['card'],
        'store_text': meta['text'],
        'store_muted': meta['muted'],
        'store_border': meta['border'],
        'store_css_class': f'store-{db_store}',
    }


def _get_or_create_wishlist(user):
    """Get or create a wishlist for the user."""
    wishlist, _ = Wishlist.objects.get_or_create(user=user)
    return wishlist


@require_POST
def toggle_wishlist(request, product_id):
    """Toggle a product in/out of the user's wishlist. Returns JSON for HTMX."""
    if not request.user.is_authenticated:
        if request.headers.get('HX-Request'):
            return JsonResponse({'error': 'login_required'}, status=401)
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())

    product = get_object_or_404(Product, pk=product_id)
    wishlist = _get_or_create_wishlist(request.user)

    added = product not in wishlist.products.all()
    if added:
        wishlist.products.add(product)
        messages.success(request, f'{product.name} added to your wishlist')
    else:
        wishlist.products.remove(product)
        messages.success(request, f'{product.name} removed from your wishlist')

    if request.headers.get('HX-Request'):
        return JsonResponse({
            'added': added,
            'count': wishlist.count,
        })

    return redirect(request.META.get('HTTP_REFERER', '/'))


def view_wishlist(request):
    """Display the user's wishlist."""
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())

    store_slug = _get_store_from_path(request.path)
    wishlist = _get_or_create_wishlist(request.user)
    products = wishlist.get_store_products(store_slug)

    ctx = _build_context(store_slug)
    ctx['wishlist_products'] = products
    ctx['wishlist_count'] = products.count()
    return render(request, 'wishlist/wishlist.html', ctx)
