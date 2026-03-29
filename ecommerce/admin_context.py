"""
Admin context processor that provides per-store stats for the admin dashboard.
"""
from products.models import Product


def admin_store_stats(request):
    if not request.path.startswith('/admin'):
        return {}
    stats = {}
    for store in ['orderimo', 'petshop-ie', 'digitalhub']:
        stats[f'{store}_products'] = Product.objects.filter(store=store).count()
    # Try to get order counts - Order model is in checkout app
    try:
        from checkout.models import Order
        for store in ['orderimo', 'petshop-ie', 'digitalhub']:
            if hasattr(Order, 'store'):
                stats[f'{store}_orders'] = Order.objects.filter(store=store).count()
            else:
                # Derive from line items (store is on product)
                stats[f'{store}_orders'] = Order.objects.filter(
                    lineitems__product__store=store
                ).distinct().count()
    except Exception:
        pass
    return stats
