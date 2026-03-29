import re
from difflib import SequenceMatcher

from django.core.paginator import Paginator
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Lower

from .models import Product, Category
from .forms import ProductForm


def _fuzzy_match(query, candidates, threshold=0.6):
    """Simple fuzzy match — returns best match or None."""
    query = query.lower()
    best = None
    best_ratio = 0
    for candidate in candidates:
        name = candidate.lower()
        ratio = SequenceMatcher(None, query, name).ratio()
        if ratio > best_ratio and ratio >= threshold:
            best_ratio = ratio
            best = candidate
    return best


def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.order_by('id')
    query = None
    categories = None
    sort = None
    direction = None
    suggested_query = None
    suggested_category = None
    paginate_by = 12

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(
                    request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))

            queries = Q(name__icontains=query) | Q(description__icontains=query) | Q(brand__icontains=query)
            products = products.filter(queries)

            # Fuzzy "Did you mean?" suggestion
            if not products.exists():
                all_names = list(
                    Product.objects.values_list('name', flat=True)
                ) + list(
                    Category.objects.values_list('name', flat=True)
                )
                suggested_query = _fuzzy_match(query, all_names)
                # Also check category name match
                suggested_category = _fuzzy_match(
                    query, list(Category.objects.values_list('friendly_name', flat=True))
                )
                if suggested_category:
                    cats = Category.objects.filter(
                        Q(name__icontains=suggested_category) |
                        Q(friendly_name__icontains=suggested_category)
                    )
                    if cats.exists():
                        suggested_category = cats.first()

            # Category match on results
            if 'category' not in request.GET:
                matching_cat = Category.objects.filter(
                    Q(name__icontains=query) | Q(friendly_name__icontains=query)
                ).first()
                if matching_cat:
                    suggested_category = matching_cat

    current_sorting = f'{sort}_{direction}'

    paginator = Paginator(products, paginate_by)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
        'is_paginated': page_obj.has_other_pages(),
        'suggested_query': suggested_query,
        'suggested_category': suggested_category,
    }

    return render(request, 'products/products.html', context)


def category_detail(request, slug):
    """ A view to show products in a specific category """
    category = get_object_or_404(Category, name=slug)

    sort = request.GET.get('sort', None)
    direction = request.GET.get('direction', None)

    products = Product.objects.filter(category=category)

    if sort:
        sortkey = sort
        if sort == 'name':
            products = products.annotate(lower_name=Lower('name'))
            sortkey = 'lower_name'
        elif sort == 'category':
            sortkey = 'category__name'
        elif sort == 'popular':
            sortkey = '-views_count'
        elif sort == 'newest':
            sortkey = '-id'
        elif sort == 'featured':
            sortkey = '-featured'
        else:
            sortkey = sort
        if direction == 'desc':
            sortkey = f'-{sortkey}'
        products = products.order_by(sortkey)

    # Subcategories (categories that share the same parent or are top-level)
    # Get sibling categories + this category's own children (if any)
    subcategories = Category.objects.filter(display_order__gte=0).exclude(
        id=category.id
    )[:8]

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Related featured products
    featured_products = list(
        Product.objects.filter(category=category, featured=True)[:4]
    )
    if len(featured_products) < 4:
        additional = list(
            Product.objects.filter(category=category).exclude(
                id__in=[p.id for p in featured_products]
            ).order_by('-views_count')[:4 - len(featured_products)]
        )
        featured_products.extend(additional)

    current_sorting = f'{sort}_{direction}'

    context = {
        'category': category,
        'page_obj': page_obj,
        'products': products,
        'subcategories': subcategories,
        'featured_products': featured_products[:4],
        'current_sorting': current_sorting,
        'is_paginated': page_obj.has_other_pages(),
    }

    return render(request, 'products/category_detail.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)

    # Track recently viewed (store up to 4 product IDs in session)
    recently_viewed = request.session.get('recently_viewed', [])
    # Remove current product if already in list
    if product_id in recently_viewed:
        recently_viewed.remove(product_id)
    # Prepend current product
    recently_viewed.insert(0, product_id)
    # Keep only last 4
    recently_viewed = recently_viewed[:4]
    request.session['recently_viewed'] = recently_viewed

    # Increment views
    Product.objects.filter(pk=product_id).update(views_count=product.views_count + 1)

    # Related products (same category)
    related_products = list(
        Product.objects.filter(category=product.category).exclude(
            pk=product_id
        ).order_by('-views_count')[:4]
    )

    # Recently viewed products (from session, excluding current product)
    recently_viewed_ids = request.session.get('recently_viewed', [])
    recently_viewed = []
    for pid in recently_viewed_ids:
        if pid != product_id:
            try:
                recently_viewed.append(Product.objects.get(pk=pid))
            except Product.DoesNotExist:
                pass
        if len(recently_viewed) >= 4:
            break

    # Build JSON-LD Product schema
    product_schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.name,
        "description": product.description,
        "sku": product.sku or str(product.id),
        "brand": {
            "@type": "Brand",
            "name": product.brand or "Orderimo"
        },
        "image": request.build_absolute_uri(product.image.url) if product.image else None,
        "url": request.build_absolute_uri(request.path),
        "offers": {
            "@type": "Offer",
            "price": str(product.price),
            "priceCurrency": "EUR",
            "availability": (
                "https://schema.org/InStock" if product.is_in_stock
                else "https://schema.org/OutOfStock"
            ),
            "seller": {
                "@type": "Organization",
                "name": "Orderimo"
            }
        },
    }
    if product.rating:
        product_schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(product.rating),
            "bestRating": "5",
            "worstRating": "1",
            "reviewCount": "1"
        }

    context = {
        'product': product,
        'related_products': related_products,
        'recently_viewed': recently_viewed,
        'product_schema': product_schema,
    }

    return render(request, 'products/product_detail.html', context)


@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(
                request, 'Failed to add product. Check the form is valid.')
    else:
        form = ProductForm()

    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(
                request,
                'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """ Delete an product """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('products'))

    product = get_object_or_404(Product, pk=product_id)

    if request.method == "POST":
        username = request.POST.get("username")

        if username == request.user.username:
            product.delete()
            messages.success(request, 'Product deleted!')
            return redirect(reverse('products'))

        else:
            messages.error(
                request, 'Incorrect username. The product was not deleted.')

    template = 'products/product_detail.html'
    context = {
        'product': product,
    }

    return render(request, template, context)
