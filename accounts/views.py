from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

from checkout.models import Order
from .models import WishlistItem
from products.models import Product


@login_required
def dashboard(request):
    orders = Order.objects.filter(email=request.user.email).order_by('-date')[:10]
    context = {'orders': orders}
    return render(request, 'accounts/dashboard.html', context)


def wishlist(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    items = WishlistItem.objects.filter(user=request.user).select_related('product')
    context = {'wishlist_items': items}
    return render(request, 'accounts/wishlist.html', context)


def add_to_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    product = get_object_or_404(Product, pk=product_id)
    item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    return JsonResponse({'added': created, 'wishlist_count': WishlistItem.objects.filter(user=request.user).count()})


def remove_from_wishlist(request, product_id):
    WishlistItem.objects.filter(user=request.user, product_id=product_id).delete()
    return JsonResponse({'removed': True})
