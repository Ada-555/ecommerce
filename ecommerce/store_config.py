"""
Orderimo — Multi-Store Configuration
=====================================
Simple store registry for the three brands.
"""

STORES = {
    'plurino': {
        'name': 'Plurino',
        'tagline': 'Tech Gadgets & Accessories',
        'theme': 'cyan',
        'description': 'Smart, sleek, cutting-edge tech for modern life.',
        'primary_color': '#00FFFF',
        'secondary_color': '#0099CC',
        'accent_color': '#00CCCC',
    },
    'homenest': {
        'name': 'HomeNest',
        'tagline': 'Curated Home & Living',
        'theme': 'amber',
        'description': 'Warm, cozy, curated pieces for the home.',
        'primary_color': '#FFB347',
        'secondary_color': '#CC8800',
        'accent_color': '#FFD700',
    },
    'stylevault': {
        'name': 'StyleVault',
        'tagline': 'Fashion & Streetwear',
        'theme': 'pink',
        'description': 'Bold, urban, expressive fashion for every vibe.',
        'primary_color': '#FF69B4',
        'secondary_color': '#FF1493',
        'accent_color': '#FFB6C1',
    },
}


def get_store(slug):
    """Return store config dict or None."""
    return STORES.get(slug)


def get_all_stores():
    """Return list of all store configs."""
    return list(STORES.items())
