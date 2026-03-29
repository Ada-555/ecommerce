from django.shortcuts import render
from products.models import Product, Category


def index(request):
    """ A view to return the index page """

    # Featured products (featured=True, up to 4)
    featured_products = list(Product.objects.filter(
        featured=True
    ).exclude(image='').exclude(image__isnull=True)[:4])

    # If not enough featured, fill with random products
    if len(featured_products) < 4:
        additional = list(Product.objects.exclude(
            id__in=[p.id for p in featured_products]
        ).order_by('?')[:4 - len(featured_products)])
        featured_products.extend(additional)

    # New arrivals (4 most recent)
    new_products = list(
        Product.objects.order_by('-id')[:4]
    )

    # Best sellers (4 products with highest views_count)
    best_sellers = list(
        Product.objects.order_by('-views_count')[:4]
    )

    # All categories for "Shop by Category" section
    categories = list(Category.objects.all()[:8])

    context = {
        'featured_products': featured_products[:4],
        'new_products': new_products[:4],
        'best_sellers': best_sellers[:4],
        'categories': categories,
    }

    return render(request, 'home/index.html', context)
