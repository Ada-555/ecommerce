from django.shortcuts import render, redirect
from products.models import Product


def _get_store_from_request(request):
    """Extract store slug from request path."""
    path = request.path
    if '/petshop/' in path:
        return 'petshop-ie'
    elif '/digital/' in path:
        return 'digitalhub'
    return 'orderimo'


def compare_view(request):
    """Display side-by-side comparison of selected products."""
    compare_ids = request.session.get('compare_ids', [])
    store = _get_store_from_request(request)
    products = Product.objects.filter(id__in=compare_ids, store=store)
    return render(request, 'comparison/compare.html', {
        'products': products,
        'compare_ids': compare_ids,
    })


def _get_compare_redirect_url(request):
    """Return the correct store-prefixed compare URL for the request."""
    path = request.path
    if '/petshop/' in path:
        return '/petshop/compare/'
    elif '/digital/' in path:
        return '/digital/compare/'
    return '/orderimo/compare/'


def add_to_compare(request, product_id):
    """Add a product to the comparison list (max 3)."""
    compare_ids = request.session.get('compare_ids', [])
    if product_id not in compare_ids and len(compare_ids) < 3:
        compare_ids.append(product_id)
        request.session['compare_ids'] = compare_ids
    return redirect(_get_compare_redirect_url(request))


def remove_from_compare(request, product_id):
    """Remove a product from the comparison list."""
    compare_ids = request.session.get('compare_ids', [])
    if product_id in compare_ids:
        compare_ids.remove(product_id)
        request.session['compare_ids'] = compare_ids
    return redirect(_get_compare_redirect_url(request))


def clear_compare(request):
    """Clear all products from comparison."""
    request.session['compare_ids'] = []
    return redirect(_get_compare_redirect_url(request))
