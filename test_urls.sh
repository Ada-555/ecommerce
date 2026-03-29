#!/bin/bash

BASE="http://localhost:8023"
STORES="orderimo petshop digital"
RESULTS_FILE="/tmp/url_test_results.txt"

# URLs to test (relative paths)
declare -A URLS=(
  ["/"]="home"
  ["/products/"]="products"
  ["/about/"]="about"
  ["/contact/"]="contact"
  ["/faq/"]="faq"
  ["/privacy/"]="privacy"
  ["/terms/"]="terms"
  ["/cookies/"]="cookies"
  ["/blog/"]="blog_index"
  ["/bag/"]="bag"
  ["/compare/"]="compare"
  ["/accounts/login/"]="login"
  ["/accounts/signup/"]="signup"
  ["/accounts/logout/"]="logout"
)

echo "Testing all stores..."
echo "======================="

> "$RESULTS_FILE"

for store in $STORES; do
  echo "=== $store ===" >> "$RESULTS_FILE"
  
  for url_path in "${!URLS[@]}"; do
    url="${BASE}/${store}${url_path}"
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>&1)
    echo "/${store}${url_path} -> $status" >> "$RESULTS_FILE"
  done
  
  # Test products listing to get a product ID
  products_url="${BASE}/${store}/products/"
  first_product=$(curl -s "$products_url" | grep -oP 'href="[^"]*/products/\d+/"' | head -1 | grep -oP '\d+' | head -1)
  if [ -n "$first_product" ]; then
    url="${BASE}/${store}/products/${first_product}/"
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>&1)
    echo "/${store}/products/${first_product}/ -> $status" >> "$RESULTS_FILE"
  else
    echo "/${store}/products/<id>/ -> NO_PRODUCTS" >> "$RESULTS_FILE"
  fi
  
  # Test blog post
  blog_url="${BASE}/${store}/blog/"
  first_post=$(curl -s "$blog_url" | grep -oP 'href="[^"]*/blog/[^/]+/"' | head -1 | sed 's|href="||;s|/".*||' | sed 's|.*/||')
  if [ -n "$first_post" ]; then
    # Get full path
    post_slug=$(curl -s "$blog_url" | grep -oP 'href="[^"]*/blog/[^/]+/"' | head -1 | grep -oP '/blog/[^/]+/' | tr -d '/')
    url="${BASE}/${store}/blog/${post_slug}/"
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>&1)
    echo "/${store}/blog/${post_slug}/ -> $status" >> "$RESULTS_FILE"
  else
    echo "/${store}/blog/<slug>/ -> NO_POSTS" >> "$RESULTS_FILE"
  fi
  
  echo "" >> "$RESULTS_FILE"
done

echo "Done. Results:"
cat "$RESULTS_FILE"
