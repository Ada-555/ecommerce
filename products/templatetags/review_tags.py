from django import template

register = template.Library()


@register.simple_tag
def is_verified_buyer(user, product):
    """Return True if the user has purchased the given product (completed order)."""
    if not user or not user.is_authenticated:
        return False

    from checkout.models import OrderLineItem

    return OrderLineItem.objects.filter(
        order__user_profile__user=user,
        product=product,
        order__status__in=['confirmed', 'shipped', 'out_for_delivery', 'delivered']
    ).exists()


@register.simple_tag
def rating_breakdown(product):
    """Return a dict of {1: count, 2: count, ..., 5: count} for approved reviews."""
    from collections import Counter

    reviews = product.reviews.filter(approved=True)
    counts = Counter(reviews.values_list('rating', flat=True))
    return {i: counts.get(i, 0) for i in range(1, 6)}


@register.filter
def get_star_count(breakdown_dict, star_num):
    """Get the count for a given star number from a rating breakdown dict."""
    return breakdown_dict.get(int(star_num), 0)


@register.simple_tag
def approved_reviews(product):
    """Return only approved reviews for a product, newest first."""
    return product.reviews.filter(approved=True).order_by('-created_at')
