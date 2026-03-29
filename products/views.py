from difflib import SequenceMatcher

from django.core.paginator import Paginator
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Lower

from .models import Product, Category, Review
from .forms import ProductForm, ReviewForm


@login_required
def create_review(request, product_id):
    """Create a review for a product."""
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        # Validate rating is 1-5
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                messages.error(request, 'Rating must be between 1 and 5.')
                return redirect(reverse('product_detail', args=[product_id]))
        except (TypeError, ValueError):
            messages.error(request, 'Invalid rating.')
            return redirect(reverse('product_detail', args=[product_id]))

        if not comment:
            messages.error(request, 'Please write a comment.')
            return redirect(reverse('product_detail', args=[product_id]))

        # Check for existing review
        if Review.objects.filter(user=request.user, product=product).exists():
            messages.error(request, 'You have already reviewed this product.')
            return redirect(reverse('product_detail', args=[product_id]))

        Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            comment=comment,
            approved=False,
        )
        messages.success(
            request,
            'Thank you! Your review has been submitted and is pending approval.'
        )
        return redirect(reverse('product_detail', args=[product_id]))

    return redirect(reverse('product_detail', args=[product_id]))


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
    # Detect store from URL path
    path = request.path
    if "/petshop/" in path:
        store_filter = "petshop-ie"
    elif "/digital/" in path:
        store_filter = "digitalhub"
    else:
        store_filter = "orderimo"
    products = Product.objects.filter(store=store_filter).select_related('category').order_by('id')
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
    active_store = request.session.get('active_store', 'orderimo')
    print(f"DEBUG: Filtering products by store={active_store}")

    sort = request.GET.get('sort', None)
    direction = request.GET.get('direction', None)

    products = Product.objects.filter(category=category, store=active_store).select_related('category')

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
    """Show individual product details, auto-detecting store from URL."""
    # Detect store from URL path
    path = request.path
    if "/petshop/" in path:
        store_slug = "petshop"
        db_store = "petshop-ie"
    elif "/digital/" in path:
        store_slug = "digital"
        db_store = "digitalhub"
    elif "/orderimo/" in path:
        store_slug = "orderimo"
        db_store = "orderimo"
    else:
        db_store = request.session.get("active_store", "orderimo")
        store_slug = db_store

    product = get_object_or_404(
        Product.objects.select_related("category"),
        pk=product_id,
        store=db_store
    )

    # Track recently viewed
    recently_viewed = request.session.get("recently_viewed", [])
    if product_id in recently_viewed:
        recently_viewed.remove(product_id)
    recently_viewed.insert(0, product_id)
    recently_viewed = recently_viewed[:4]
    request.session["recently_viewed"] = recently_viewed

    # Increment views (using F() to avoid race conditions)
    from django.db.models import F
    Product.objects.filter(pk=product_id).update(views_count=F("views_count") + 1)
    product.views_count = (product.views_count or 0) + 1

    # Related products
    related_products = list(
        Product.objects.filter(category=product.category, store=db_store)
        .exclude(pk=product_id)
        .select_related("category")
        .order_by("-views_count")[:4]
    )

    # Recently viewed
    recently_viewed_ids = request.session.get("recently_viewed", [])
    recently_viewed_products = list(
        Product.objects.filter(
            pk__in=[p for p in recently_viewed_ids if p != product_id],
            store=db_store
        ).select_related("category")[:4]
    )

    # Store metadata for template
    from stores.store_views import STORE_META, STORE_NAME_MAP
    store_name = STORE_NAME_MAP.get(db_store, "Orderimo")
    meta = STORE_META.get(db_store, STORE_META["orderimo"])

    # Build product schema
    product_schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.name,
        "description": product.description,
        "sku": product.sku or str(product.id),
        "brand": {"@type": "Brand", "name": product.brand or store_name},
        "image": request.build_absolute_uri(product.image.url) if product.image else None,
        "url": request.build_absolute_uri(request.path),
        "offers": {
            "@type": "Offer",
            "price": str(product.price),
            "priceCurrency": "EUR",
            "availability": "https://schema.org/InStock" if product.is_in_stock else "https://schema.org/OutOfStock",
            "seller": {"@type": "Organization", "name": store_name},
        },
    }
    if getattr(product, "rating", None):
        product_schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(product.rating),
            "bestRating": "5",
            "worstRating": "1",
            "reviewCount": "1",
        }

    # Check if user has already reviewed this product
    from products.models import Review
    has_user_reviewed = (
        request.user.is_authenticated and
        Review.objects.filter(product=product, user=request.user).exists()
    )

    context = {
        "product": product,
        "related_products": related_products,
        "recently_viewed": recently_viewed_products,
        "product_schema": product_schema,
        "review_form": ReviewForm(),
        "has_user_reviewed": has_user_reviewed,
        # Store context
        "store": db_store,
        "store_slug": store_slug,
        "store_name": store_name,
        "store_primary": meta["primary"],
        "store_secondary": meta["secondary"],
        "store_accent": meta["accent"],
        "store_dark": meta["dark"],
        "store_card": meta["card"],
        "store_text": meta["text"],
        "store_muted": meta["muted"],
        "store_border": meta["border"],
        "store_shadow": meta["shadow"],
        "store_card_shadow": meta["card_shadow"],
        "store_dropdown_hover": meta["dropdown_hover"],
        "store_nav_bg": meta["nav_bg"],
        "store_switcher_bg": meta["switcher_bg"],
        "store_google_fonts_url": meta["google_fonts"],
        "store_nav_font": meta["nav_font"],
        "store_body_font": meta["body_font"],
        "store_heading_font": meta["heading_font"],
        "store_icon": meta["icon"],
        "store_promo_text": meta["promo_text"],
        "store_tagline": meta["tagline"],
        "store_copyright": meta["copyright"],
        "nav_items": meta["nav_items"],
        "footer_columns": meta["footer_columns"],
        "store_css_class": f"store-{db_store}",
    }

    return render(request, "products/product_detail.html", context)


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
