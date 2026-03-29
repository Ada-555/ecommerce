"""
Context processor that detects which store is being accessed from the URL
and injects store metadata into all templates.
"""
from stores.store_views import STORE_META

STORE_MAP = {'orderimo': 'orderimo', 'petshop': 'petshop-ie', 'digital': 'digitalhub'}
STORE_NAME_MAP = {'orderimo': 'Orderimo', 'petshop': 'PetShop Ireland', 'digital': 'DigitalHub'}
# Maps URL slug -> CSS class suffix
STORE_CSS_MAP = {'orderimo': 'orderimo', 'petshop': 'petshop-ie', 'digital': 'digitalhub'}


def store_context(request):
    path = request.path
    if '/petshop/' in path:
        url_slug = 'petshop'
    elif '/digital/' in path:
        url_slug = 'digital'
    elif '/orderimo/' in path:
        url_slug = 'orderimo'
    else:
        # Global / root route — use Orderimo defaults
        return {
            'store': 'orderimo',
            'store_slug': 'orderimo',
            'store_name': 'Orderimo',
            'store_css_class': 'store-orderimo',
        }

    db_store = STORE_MAP.get(url_slug, 'orderimo')
    css_class = STORE_CSS_MAP.get(url_slug, 'orderimo')
    meta = STORE_META.get(db_store, STORE_META['orderimo'])

    return {
        'store': db_store,
        'store_slug': url_slug,
        'store_name': STORE_NAME_MAP.get(url_slug, 'Orderimo'),
        'store_css_class': f'store-{css_class}',
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
