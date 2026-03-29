from decimal import Decimal
from django.utils import timezone
from .models import Coupon


def validate_coupon_code(code, store_slug=None):
    """
    Validate a single coupon code.

    Returns:
        (coupon_instance, None) if valid
        (None, error_message) if invalid
    """
    code = code.strip().upper()

    if not code:
        return None, "Please enter a coupon code."

    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        return None, "This coupon code does not exist."

    if not coupon.is_active:
        return None, "This coupon is no longer active."

    if coupon.is_expired:
        return None, "This coupon has expired."

    if coupon.is_maxed_out:
        return None, "This coupon has reached its usage limit."

    return coupon, None


def apply_coupon_discount(coupon, order_subtotal):
    """Calculate the discount amount from a coupon."""
    return coupon.calculate_discount(order_subtotal)


def validate_and_apply_coupons(codes, order_subtotal, store_slug=None):
    """
    Validate a list of coupon codes and return total discount.

    Args:
        codes: list of coupon code strings (up to 3)
        order_subtotal: decimal order subtotal before discount
        store_slug: optional store slug to filter coupons

    Returns:
        (total_discount, list_of_valid_coupons, error_message)
    """
    if not codes:
        return Decimal('0.00'), [], None

    # Limit to 3 coupons
    codes = codes[:3]

    total_discount = Decimal('0.00')
    applied_coupons = []
    first_error = None

    for code in codes:
        coupon, error = validate_coupon_code(code, store_slug)
        if error:
            if first_error is None:
                first_error = error
            continue

        # Check minimum order amount
        if order_subtotal < coupon.min_order_amount:
            if first_error is None:
                first_error = f"Order must be at least €{coupon.min_order_amount} to use coupon {coupon.code}."
            continue

        discount = coupon.calculate_discount(order_subtotal)
        total_discount += discount
        applied_coupons.append(coupon)

    return total_discount, applied_coupons, first_error
