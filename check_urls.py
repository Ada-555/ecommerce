#!/usr/bin/env python3
import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'ecommerce.settings'
import django
django.setup()
from django.urls import reverse, NoReverseMatch

# URL names that DON'T need arguments
url_names_no_args = [
    'home', 'orderimo_home', 'petshop_home', 'digital_home',
    'orderimo_products', 'petshop_products', 'digital_products',
    'orderimo_about', 'petshop_about', 'digital_about',
    'orderimo_contact', 'petshop_contact', 'digital_contact',
    'orderimo_faq', 'petshop_faq', 'digital_faq',
    'orderimo_privacy', 'petshop_privacy', 'digital_privacy',
    'orderimo_terms', 'petshop_terms', 'digital_terms',
    'orderimo_cookies', 'petshop_cookies', 'digital_cookies',
    'orderimo_accept_cookies', 'petshop_accept_cookies', 'digital_accept_cookies',
    'profile',
    'account_login', 'account_logout', 'account_signup',
    'view_bag', 'checkout',
    'products', 'blog',
]

# URL names that NEED arguments
url_names_with_args = [
    ('set_active_store', ('orderimo',)),
    ('orderimo_product_detail', (1,)),
    ('petshop_product_detail', (1,)),
    ('digital_product_detail', (1,)),
    ('order_history', ('ORD-123',)),
    ('add_to_bag', (1,)),
    ('adjust_bag', (1,)),
    ('remove_from_bag', (1,)),
    ('checkout_success', ('ORD-123',)),
    ('product_detail', (1,)),
    ('add_review', (1,)),
    ('blog_page_detail', (1,)),  # correct name (not blog_post)
]

failed = []

# Test URLs without args
for name in url_names_no_args:
    try:
        url = reverse(name)
        print(f"OK: {name} -> {url}")
    except NoReverseMatch as e:
        print(f"FAIL: {name} -> {e}")
        failed.append(name)

# Test URLs that need args
for name, args in url_names_with_args:
    try:
        url = reverse(name, args=args)
        print(f"OK: {name}{args} -> {url}")
    except NoReverseMatch as e:
        print(f"FAIL: {name} -> {e}")
        failed.append(name)

if failed:
    print(f"\n{len(failed)} FAILED URLs!")
    sys.exit(1)
else:
    print("\nAll URL names resolve correctly!")
