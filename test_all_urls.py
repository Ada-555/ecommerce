#!/usr/bin/env python3
"""Comprehensive URL testing for all 3 KC-7 stores."""
import urllib.request
import urllib.error
import urllib.parse
import ssl
import re
import sys

BASE = "http://localhost:8023"
STORES = ["orderimo", "petshop", "digital"]

# Create SSL context that doesn't verify
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get_url(url, follow_redirects=True):
    """Fetch a URL and return status code, final URL, and response text."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        if follow_redirects:
            response = urllib.request.urlopen(req, timeout=10, context=ctx)
            status = response.getcode()
            final_url = response.geturl()
            content = response.read().decode('utf-8', errors='replace')
        else:
            class NoRedirect(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, req, fp, code, msg, headers, newurl):
                    return None
            opener = urllib.request.build_opener(NoRedirect)
            response = opener.open(req, timeout=10)
            status = response.getcode()
            final_url = url
            content = response.read().decode('utf-8', errors='replace')
        return status, final_url, content
    except urllib.error.HTTPError as e:
        return e.code, url, f"HTTPError: {e}"
    except urllib.error.URLError as e:
        return 0, url, f"URLError: {e.reason}"
    except Exception as e:
        return 0, url, f"Error: {e}"

def extract_first_product_id(content):
    """Extract first product ID from product listing page."""
    patterns = [
        r'/orderimo/products/(\d+)/',
        r'/petshop/products/(\d+)/',
        r'/digital/products/(\d+)/',
        r'href="[^"]*/products/(\d+)/"',
        r'"product_id":\s*(\d+)',
        r'/products/(\d+)/',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, content)
        if matches:
            return matches[0]
    return None

def extract_first_blog_slug(content):
    """Extract first blog post slug."""
    patterns = [
        r'href="[^"]*/blog/([^/]+)/"',
        r'/blog/([^/]+)/"',
        r'"slug":\s*"([^"]+)"',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, content)
        if matches and matches[0] not in ['page', '1', '2', '3']:
            return matches[0]
    return None

def check_compare_button(content, store):
    """Check if product cards have compare buttons."""
    patterns = [
        r'compare.*button',
        r'compare-btn',
        r'data-action="compare"',
        r'class="[^"]*compare[^"]*"',
        r'Add to Compare',
        r'Compare',
    ]
    for pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False

def test_store(store):
    """Test all URLs for a store."""
    results = {}
    
    pages = [
        ("home", f"/{store}/"),
        ("products", f"/{store}/products/"),
        ("bag", f"/{store}/bag/"),
        ("checkout", f"/{store}/checkout/"),
        ("wishlist", f"/{store}/wishlist/"),
        ("compare", f"/{store}/compare/"),
        ("about", f"/{store}/about/"),
        ("contact", f"/{store}/contact/"),
        ("faq", f"/{store}/faq/"),
        ("privacy", f"/{store}/privacy/"),
        ("terms", f"/{store}/terms/"),
        ("cookies", f"/{store}/cookies/"),
        ("blog_index", f"/{store}/blog/"),
        ("login", f"/{store}/accounts/login/"),
        ("signup", f"/{store}/accounts/signup/"),
        ("logout", f"/{store}/accounts/logout/"),
    ]
    
    # Get products page to find a product ID
    status, _, content = get_url(f"{BASE}/{store}/products/")
    product_id = extract_first_product_id(content)
    if product_id:
        pages.append(("product_detail", f"/{store}/products/{product_id}/"))
    
    # Get blog index to find a post slug
    status, _, content = get_url(f"{BASE}/{store}/blog/")
    blog_slug = extract_first_blog_slug(content)
    if blog_slug:
        pages.append(("blog_post", f"/{store}/blog/{blog_slug}/"))
    
    # Test all pages
    for name, path in pages:
        url = f"{BASE}{path}"
        status, final_url, content = get_url(url)
        results[name] = {
            'path': path,
            'status': status,
            'final_url': final_url,
            'has_compare_btn': check_compare_button(content, store),
        }
    
    return results, product_id, blog_slug

def test_add_to_cart(store, product_id):
    """Test add-to-cart flow."""
    if not product_id:
        return None
    
    url = f"{BASE}/{store}/products/{product_id}/"
    status, _, content = get_url(url)
    
    # Find the add-to-cart form action
    form_match = re.search(r'action="([^"]*)"', content)
    if form_match:
        form_action = form_match.group(1)
    else:
        form_action = f"/{store}/bag/add/"
    
    # Try POST to add to cart
    try:
        data = urllib.parse.urlencode({
            'product_id': product_id,
            'quantity': 1,
            'csrfmiddlewaretoken': 'test',
        }).encode()
        
        req = urllib.request.Request(
            f"{BASE}{form_action}",
            data=data,
            method='POST',
            headers={
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': url,
            }
        )
        response = urllib.request.urlopen(req, timeout=10, context=ctx)
        cart_status = response.getcode()
    except Exception as e:
        return {'error': str(e)}
    
    # Check if bag now has items
    bag_url = f"{BASE}/{store}/bag/"
    bag_status, _, bag_content = get_url(bag_url)
    
    return {
        'add_to_cart_status': cart_status,
        'bag_view_status': bag_status,
    }

def main():
    all_results = {}
    
    print("Testing all stores...")
    print("=" * 80)
    
    for store in STORES:
        print(f"\n=== {store.upper()} ===")
        results, product_id, blog_slug = test_store(store)
        all_results[store] = results
        
        print(f"Product ID found: {product_id}")
        print(f"Blog slug found: {blog_slug}")
        
        for name, data in results.items():
            status = data['status']
            path = data['path']
            flag = "OK" if status in [200, 301, 302] else "FAIL"
            print(f"  [{flag}] {path}: {status}")
    
    print("\n" + "=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)
    
    # Print table
    print(f"{'Store':<12} {'Page':<18} {'Status':<8} {'OK?'}")
    print("-" * 60)
    
    for store in STORES:
        for name, data in all_results[store].items():
            status = data['status']
            ok = "OK" if status in [200, 301, 302] else "FAIL"
            print(f"{store:<12} {name:<18} {status:<8} {ok}")
    
    # Check for errors
    print("\n" + "=" * 80)
    print("ERRORS (404, 500, 503, etc.)")
    print("=" * 80)
    
    errors_found = False
    for store in STORES:
        for name, data in all_results[store].items():
            status = data['status']
            if status not in [200, 301, 302]:
                errors_found = True
                print(f"ERROR: {store}/{name} returned {status}")
                print(f"  URL: {data['path']}")
    
    if not errors_found:
        print("No errors found!")
    
    # Test add to cart for each store
    print("\n" + "=" * 80)
    print("ADD-TO-CART FLOW TEST")
    print("=" * 80)
    
    for store in STORES:
        product_id = extract_first_product_id(get_url(f"{BASE}/{store}/products/")[2])
        if product_id:
            result = test_add_to_cart(store, product_id)
            print(f"{store}: {result}")
    
    return 0 if not errors_found else 1

if __name__ == "__main__":
    sys.exit(main())
