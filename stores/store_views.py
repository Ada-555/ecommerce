from difflib import SequenceMatcher

from django.core.paginator import Paginator
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower

from products.models import Product, Category


STORE_NAME_MAP = {
    'orderimo': 'Orderimo',
    'petshop-ie': 'PetShop Ireland',
    'digitalhub': 'DigitalHub',
}


STORE_NAME_MAP = {
    'orderimo': 'Orderimo',
    'petshop-ie': 'PetShop Ireland',
    'digitalhub': 'DigitalHub',
}


STORE_META = {
    'orderimo': {
        'primary': '#00b4d8', 'secondary': '#0077b6', 'accent': '#90e0ef',
        'dark': '#0a0a0f', 'card': '#12121a', 'text': '#e0e0e0', 'muted': '#888',
        'border': 'rgba(255,255,255,0.07)', 'shadow': 'rgba(0,180,216,0.4)',
        'card_shadow': 'rgba(0,180,216,0.15)', 'dropdown_hover': 'rgba(0,180,216,0.12)',
        'nav_bg': '10,10,15', 'switcher_bg': '#111118',
        'google_fonts': "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600&display=swap",
        'nav_font': "'Outfit', sans-serif", 'body_font': "'Outfit', sans-serif",
        'heading_font': "'Space Grotesk', sans-serif",
        'icon': 'fa-solid fa-store',
        'promo_text': '🚚 Free delivery over €80',
        'tagline': 'One platform. Multiple curated stores. Shop tech, home, fashion and more.',
        'copyright': '© 2026 Orderimo',
        'nav_items': [
            {'label': 'Home', 'url': '/orderimo/'},
            {'label': 'Products', 'url': '/orderimo/products/'},
            {'label': 'Blog', 'url': '/orderimo/blog/'},
            {'label': 'About', 'url': '/orderimo/about/'},
        ],
        'footer_columns': [
            {'title': 'Shop', 'links': [
                {'label': 'All Products', 'url': '/orderimo/products/'},
                {'label': 'Electronics', 'url': '/orderimo/products/?category=electronics'},
                {'label': 'Home & Living', 'url': '/orderimo/products/?category=home'},
                {'label': 'Fashion', 'url': '/orderimo/products/?category=fashion'},
            ]},
            {'title': 'Company', 'links': [
                {'label': 'About', 'url': '/orderimo/about/'},
                {'label': 'Blog', 'url': '/orderimo/blog/'},
                {'label': 'Contact', 'url': '/orderimo/contact/'},
            ]},
        ],
    },
    'petshop-ie': {
        'primary': '#228B22', 'secondary': '#2d9a3e', 'accent': '#90EE90',
        'dark': '#0a150a', 'card': '#111a11', 'text': '#e8f5e9', 'muted': '#7a9a7a',
        'border': 'rgba(34,139,34,0.15)', 'shadow': 'rgba(34,139,34,0.4)',
        'card_shadow': 'rgba(34,139,34,0.15)', 'dropdown_hover': 'rgba(34,139,34,0.15)',
        'nav_bg': '10,15,10', 'switcher_bg': '#080f08',
        'google_fonts': "https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap",
        'nav_font': "'Nunito', sans-serif", 'body_font': "'Nunito', sans-serif",
        'heading_font': "'Poppins', sans-serif",
        'icon': 'fa-solid fa-paw',
        'promo_text': '🚚 Fast delivery across Ireland — all 32 counties',
        'tagline': "Ireland's best pet supplies. Fast delivery across all 32 counties.",
        'copyright': '© 2026 PetShop Ireland — Delivering to Ireland 🇮🇪',
        'nav_items': [
            {'label': 'Home', 'url': '/petshop/'},
            {'label': 'Dogs', 'url': '/petshop/products/?category=dogs'},
            {'label': 'Cats', 'url': '/petshop/products/?category=cats'},
            {'label': 'Fish', 'url': '/petshop/products/?category=fish_aquatics'},
            {'label': 'Birds', 'url': '/petshop/products/?category=birds'},
            {'label': 'All', 'url': '/petshop/products/'},
        ],
        'footer_columns': [
            {'title': 'Pets', 'links': [
                {'label': 'Dogs', 'url': '/petshop/products/?category=dogs'},
                {'label': 'Cats', 'url': '/petshop/products/?category=cats'},
                {'label': 'Fish', 'url': '/petshop/products/?category=fish_aquatics'},
                {'label': 'Birds', 'url': '/petshop/products/?category=birds'},
            ]},
            {'title': 'Info', 'links': [
                {'label': 'About', 'url': '/petshop/about/'},
                {'label': 'Contact', 'url': '/petshop/contact/'},
                {'label': 'FAQ', 'url': '/petshop/faq/'},
            ]},
        ],
    },
    'digitalhub': {
        'primary': '#800080', 'secondary': '#da70d6', 'accent': '#ff69b4',
        'dark': '#06060f', 'card': '#0e0e1a', 'text': '#e8e8f0', 'muted': '#8888aa',
        'border': 'rgba(128,0,128,0.15)', 'shadow': 'rgba(128,0,128,0.5)',
        'card_shadow': 'rgba(128,0,128,0.25)', 'dropdown_hover': 'rgba(128,0,128,0.15)',
        'nav_bg': '6,6,15', 'switcher_bg': '#04040c',
        'google_fonts': "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap",
        'nav_font': "'Inter', sans-serif", 'body_font': "'Inter', sans-serif",
        'heading_font': "'JetBrains Mono', monospace",
        'icon': 'fa-solid fa-bolt',
        'promo_text': '⚡ Instant delivery — lifetime access',
        'tagline': 'Instant delivery. Lifetime access. Download immediately after purchase.',
        'copyright': '© 2026 DigitalHub — Instant Digital Delivery',
        'nav_items': [
            {'label': 'Home', 'url': '/digital/'},
            {'label': 'Products', 'url': '/digital/products/'},
            {'label': 'About', 'url': '/digital/about/'},
            {'label': 'Contact', 'url': '/digital/contact/'},
        ],
        'footer_columns': [
            {'title': 'Products', 'links': [
                {'label': 'All Products', 'url': '/digital/products/'},
                {'label': 'E-books', 'url': '/digital/products/?category=ebooks'},
                {'label': 'Courses', 'url': '/digital/products/?category=courses'},
                {'label': 'Software', 'url': '/digital/products/?category=software'},
            ]},
            {'title': 'Info', 'links': [
                {'label': 'About', 'url': '/digital/about/'},
                {'label': 'Contact', 'url': '/digital/contact/'},
                {'label': 'FAQ', 'url': '/digital/faq/'},
            ]},
        ],
    },
}


def _build_context(store_slug, db_store, store_name, extra=None):
    """Build the shared context dict for any store page."""
    meta = STORE_META.get(db_store, STORE_META['orderimo'])
    ctx = {
        'store': db_store,
        'store_slug': store_slug,
        'store_name': store_name,
        'store_description': f"{store_name} — Official Store",
        'store_primary': meta['primary'],
        'store_secondary': meta['secondary'],
        'store_accent': meta['accent'],
        'store_dark': meta['dark'],
        'store_card': meta['card'],
        'store_text': meta['text'],
        'store_muted': meta['muted'],
        'store_border': meta['border'],
        'store_shadow': meta['shadow'],
        'store_card_shadow': meta['card_shadow'],
        'store_dropdown_hover': meta['dropdown_hover'],
        'store_nav_bg': meta['nav_bg'],
        'store_switcher_bg': meta['switcher_bg'],
        'store_google_fonts_url': meta['google_fonts'],
        'store_nav_font': meta['nav_font'],
        'store_body_font': meta['body_font'],
        'store_heading_font': meta['heading_font'],
        'store_icon': meta['icon'],
        'store_promo_text': meta['promo_text'],
        'store_tagline': meta['tagline'],
        'store_copyright': meta['copyright'],
        'nav_items': meta['nav_items'],
        'footer_columns': meta['footer_columns'],
    }
    if extra:
        ctx.update(extra)
    return ctx


def orderimo_home(request):
    products = Product.objects.filter(store='orderimo').select_related('category').order_by('-id')
    featured = list(products.filter(featured=True)[:4])
    new_arrivals = list(products[:8])
    if not featured:
        featured = list(products[:4])
    ctx = _build_context('orderimo', 'orderimo', 'Orderimo', {
        'featured': featured,
        'new_arrivals': new_arrivals,
    })
    return render(request, 'stores/orderimo/home.html', ctx)


def petshop_home(request):
    products = Product.objects.filter(store='petshop-ie').select_related('category').order_by('-id')
    featured = list(products.filter(featured=True)[:4])
    new_arrivals = list(products[:8])
    if not featured:
        featured = list(products[:4])
    ctx = _build_context('petshop', 'petshop-ie', 'PetShop Ireland', {
        'featured': featured,
        'new_arrivals': new_arrivals,
    })
    return render(request, 'stores/petshop/home.html', ctx)


def digital_home(request):
    products = Product.objects.filter(store='digitalhub').select_related('category').order_by('-id')
    featured = list(products.filter(featured=True)[:4])
    new_arrivals = list(products[:8])
    if not featured:
        featured = list(products[:4])
    ctx = _build_context('digital', 'digitalhub', 'DigitalHub', {
        'featured': featured,
        'new_arrivals': new_arrivals,
    })
    return render(request, 'stores/digital/home.html', ctx)


def store_search(request, store_slug):
    """Search view — delegates to store_products with search query."""
    store_map = {'orderimo': 'orderimo', 'petshop': 'petshop-ie', 'digital': 'digitalhub'}
    db_store = store_map.get(store_slug, 'orderimo')
    query = request.GET.get('q', '')
    products = Product.objects.filter(store=db_store).select_related('category')
    if query:
        from django.db.models import Q
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    store_name_map = {'orderimo': 'Orderimo', 'petshop': 'PetShop Ireland', 'digital': 'DigitalHub'}
    store_name = store_name_map.get(store_slug, store_slug.title())
    ctx = _build_context(store_slug, db_store, store_name, {
        'products': products,
        'search_term': query,
    })
    return render(request, 'stores/products.html', ctx)


def store_products(request, store_slug):
    store_map = {'orderimo': 'orderimo', 'petshop': 'petshop-ie', 'digital': 'digitalhub'}
    store_name_map = {'orderimo': 'Orderimo', 'petshop': 'PetShop Ireland', 'digital': 'DigitalHub'}
    db_store = store_map.get(store_slug, 'orderimo')
    store_name = store_name_map.get(store_slug, store_slug.title())
    products = Product.objects.filter(store=db_store).select_related('category')
    ctx = _build_context(store_slug, db_store, store_name, {'products': products})
    return render(request, 'stores/products.html', ctx)


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


def store_search(request, store_slug):
    """Store-scoped search — filters products by active store."""
    store_map = {'orderimo': 'orderimo', 'petshop': 'petshop-ie', 'digital': 'digitalhub'}
    store_name_map = {'orderimo': 'Orderimo', 'petshop': 'PetShop Ireland', 'digital': 'DigitalHub'}
    db_store = store_map.get(store_slug, 'orderimo')
    store_name = store_name_map.get(store_slug, store_slug.title())

    # Start with store-scoped products
    products = Product.objects.filter(store=db_store).select_related('category').order_by('id')
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
                messages.error(request, "You didn't enter any search criteria!")
                search_url = reverse(f'{store_slug}_search')
                return redirect(f'{search_url}?sort={sort or "name"}&direction={direction or "asc"}')

            queries = Q(name__icontains=query) | Q(description__icontains=query) | Q(brand__icontains=query)
            products = products.filter(queries)

            # Fuzzy "Did you mean?" suggestion
            if not products.exists():
                all_names = list(
                    Product.objects.filter(store=db_store).values_list('name', flat=True)
                ) + list(
                    Category.objects.values_list('name', flat=True)
                )
                suggested_query = _fuzzy_match(query, all_names)
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

    # Build search URL for the navbar form
    search_url = reverse(f'{store_slug}_search')

    ctx = _build_context(store_slug, db_store, store_name, {
        'page_obj': page_obj,
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
        'is_paginated': page_obj.has_other_pages(),
        'suggested_query': suggested_query,
        'suggested_category': suggested_category,
        'search_url': search_url,
        # Store-specific search action for navbar form
        'store_search_url': search_url,
    })
    return render(request, 'stores/search_results.html', ctx)
