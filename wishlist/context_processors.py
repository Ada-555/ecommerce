def wishlist_context(request):
    """Inject wishlist product IDs into template context."""
    wishlist_product_ids = []
    wishlist_count = 0
    if request.user.is_authenticated:
        try:
            wishlist = request.user.wishlist
            wishlist_product_ids = list(
                wishlist.products.values_list('id', flat=True)
            )
            wishlist_count = wishlist.count
        except Exception:
            pass
    return {
        'wishlist_product_ids': wishlist_product_ids,
        'wishlist_count': wishlist_count,
    }
