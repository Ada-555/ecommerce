from django.shortcuts import render
from products.models import Product


def index(request):
    """ A view to return the index page """
    # Featured products (random 4)
    featured_products = list(Product.objects.filter(featured=True).exclude(
        image='').exclude(image__isnull=True)[:4])
    # If not enough featured, fill with random products
    if len(featured_products) < 4:
        additional = list(Product.objects.exclude(
            id__in=[p.id for p in featured_products]
        ).order_by('?')[:4 - len(featured_products)])
        featured_products.extend(additional)

    # New arrivals (random 4)
    new_products = list(Product.objects.order_by('?')[:4])

    context = {
        'featured_products': featured_products[:4],
        'new_products': new_products[:4],
    }

    return render(request, 'home/index.html', context)
