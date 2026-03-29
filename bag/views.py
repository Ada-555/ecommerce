from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product
from stores.store_views import STORE_META, _build_context

STORE_MAP = {'orderimo': 'orderimo', 'petshop': 'petshop-ie', 'digital': 'digitalhub'}
STORE_NAME_MAP = {'orderimo': 'Orderimo', 'petshop': 'PetShop Ireland', 'digital': 'DigitalHub'}


def _get_store_from_path(path):
    """Detect store slug from URL path like /petshop/bag/"""
    if '/petshop/' in path:
        return 'petshop'
    elif '/digital/' in path:
        return 'digital'
    return 'orderimo'


def view_bag(request):
    """Render the bag contents page with store context."""
    store_slug = _get_store_from_path(request.path)
    db_store = STORE_MAP.get(store_slug, 'orderimo')
    store_name = STORE_NAME_MAP.get(store_slug, 'Orderimo')
    ctx = _build_context(store_slug, db_store, store_name)
    return render(request, 'bag/bag.html', ctx)


def add_to_bag(request, item_id):
    item_id = str(item_id)
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity') or request.GET.get('quantity', 1))
    redirect_url = request.POST.get('redirect_url') or request.GET.get('redirect_url', '/bag/')
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    bag = request.session.get('bag', {})

    if size:
        if item_id in list(bag.keys()):
            if size in bag[item_id]['items_by_size'].keys():
                bag[item_id]['items_by_size'][size] += quantity
                messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')
            else:
                bag[item_id]['items_by_size'][size] = quantity
                messages.success(request, f'Added size {size.upper()} {product.name} to your bag')
        else:
            bag[item_id] = {'items_by_size': {size: quantity}}
            messages.success(request, f'Added size {size.upper()} {product.name} to your bag')
    else:
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
            messages.success(request, f'Updated {product.name} quantity to {bag[item_id]}')
        else:
            bag[item_id] = quantity
            messages.success(request, f'Added {product.name} to your bag')

    request.session['bag'] = bag
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """Adjust the quantity of a bag item."""
    item_id_str = str(item_id)
    quantity = int(request.POST.get('quantity', 0))
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    bag = request.session.get('bag', {})

    if item_id_str in list(bag.keys()):
        if size and isinstance(bag[item_id_str], dict) and size in bag[item_id_str].get('items_by_size', {}):
            if quantity > 0:
                bag[item_id_str]['items_by_size'][size] = quantity
                messages.success(request, f'Updated quantity to {quantity}')
            else:
                del bag[item_id_str]['items_by_size'][size]
                if not bag[item_id_str]['items_by_size']:
                    del bag[item_id_str]
                messages.success(request, 'Item removed from bag')
        elif not size and isinstance(bag[item_id_str], int):
            if quantity > 0:
                bag[item_id_str] = quantity
                messages.success(request, f'Updated quantity to {quantity}')
            else:
                del bag[item_id_str]
                messages.success(request, 'Item removed from bag')
    request.session['bag'] = bag
    # Redirect back to the store's bag page
    store_slug = _get_store_from_path(request.path)
    return redirect(f'/{store_slug}/bag/' if store_slug != 'orderimo' else '/bag/')


def remove_from_bag(request, item_id):
    """Remove an item from the bag."""
    item_id_str = str(item_id)
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    bag = request.session.get('bag', {})

    if item_id_str in list(bag.keys()):
        if size and isinstance(bag[item_id_str], dict) and size in bag[item_id_str].get('items_by_size', {}):
            del bag[item_id_str]['items_by_size'][size]
            if not bag[item_id_str]['items_by_size']:
                del bag[item_id_str]
        else:
            del bag[item_id_str]
        messages.success(request, 'Item removed from bag')

    request.session['bag'] = bag
    store_slug = _get_store_from_path(request.path)
    return redirect(f'/{store_slug}/bag/' if store_slug != 'orderimo' else '/bag/')
