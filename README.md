# Orderimo — Multi-Store E-Commerce Platform

> **One platform. Multiple branded stores.**

Orderimo is a production-ready Django e-commerce platform that powers multiple branded online stores from a single codebase. Each store has its own visual identity and product catalog while sharing infrastructure, payments, and admin. Currently runs three stores: Orderimo (general dropshipping), PetShop Ireland (pet supplies), and DigitalHub (digital products).

![Platform](https://img.shields.io/badge/Platform-Django_5.2-purple)
![Python](https://img.shields.io/badge/Python_3.13-cyan)
![Bootstrap](https://img.shields.io/badge/Bootstrap_5.3-darkpurple)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Table of Contents

1. [Features](#features)
2. [Quick Start](#-quick-start)
3. [Domain & Subdomain Setup](#-domain--subdomain-setup)
4. [Email Setup](#-email-setup)
5. [Stripe Setup](#-stripe-setup)
6. [Nginx Configuration](#-nginx-configuration)
7. [PostgreSQL Setup on Raspberry Pi](#-postgresql-setup-on-raspberry-pi)
8. [Deployment to Raspberry Pi](#-deployment-to-raspberry-pi)
9. [Adding a New Store](#-adding-a-new-store)
10. [Blog AI Generator](#-blog-ai-generator)
11. [API Keys Reference](#-api-keys-reference)
12. [Troubleshooting](#-troubleshooting)
13. [Testing](#-testing)
14. [Contributing](#-contributing)
15. [License](#license)

---

## 🎯 Features

### E-Commerce
- **Multi-Store Architecture** — Run 3 stores (Orderimo, PetShop Ireland, DigitalHub) from one Django project via store selector in the nav
- **Product Catalog** — Full CRUD, categories, variants (size/color), images, SKUs, stock tracking, ratings, featured/onsale flags
- **Shopping Bag** — Add/remove/adjust items, persistent sessions, delivery calculation, free delivery threshold
- **Stripe Checkout** — Full payment integration with Stripe Checkout Sessions + webhook handler for order confirmation
- **Order Management** — Order history, status tracking (Pending/Processing/Shipped/Delivered), confirmation emails on status change
- **User Accounts** — Registration/login via Django AllAuth, profile, order history, wishlist
- **Search & Filter** — Full-text product search, category/price/rating filters, sort by newest/popular/featured/price

### CMS & Content
- **Blog System** — AI-generated blog posts via MiniMax API, blog listing + detail pages, Schema.org Article markup
- **About Pages** — Admin-managed rich text pages via CKEditor (django-ckeditor)
- **Contact Page** — Working contact form (name, email, subject, message) → sends email via Django `send_mail`
- **FAQ Page** — Bootstrap 5 accordion FAQ with Schema.org FAQPage JSON-LD structured data
- **Privacy Policy** — GDPR-compliant policy covering data collected, third parties, user rights, retention
- **Terms & Conditions** — Full legal T&C: ordering, payment, delivery, returns, liability, governing law (Ireland)
- **Cookie Policy** — Detailed cookie policy with browser management instructions and third-party cookie table
- **Cookie Consent Banner** — Fixed bottom banner for EU cookie law, stores consent in session

### Admin & SEO
- **Django Jazzmin Admin** — Custom admin UI with Orderimo branding, collapsible forms, top menu links
- **CKEditor** — Rich text editing for blog and about pages
- **Auto Sitemap** — `sitemap.xml` with products, categories, and blog pages
- **Robots.txt** — Properly configured with allow/disallow rules for checkout, admin, accounts
- **Open Graph + Twitter Cards** — SEO meta tags on every page ( overridable per page via `{% block extra_meta %}`)
- **JSON-LD Structured Data** — Product (breadcrumbs, offers, aggregateRating), FAQPage, Article schemas

### Security (Phase 8)
- XSS, SQL injection, CSRF protections (Django built-ins)
- Clickjacking + content-type sniffing protection
- Rate limiting on login (5 failed attempts/10 min) via `django-ratelimit`
- Secure session cookies (`HttpOnly`, `SameSite=Lax`, `Secure` in production)
- Production hardening: `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, secure cookies
- Login attempt tracking via AllAuth rate limits

### Tech Stack
| Layer | Technology |
|-------|-----------|
| Framework | Django 5.2 + Python 3.13 |
| Frontend | Bootstrap 5.3, Vanilla JS, Font Awesome 6 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Payments | Stripe Checkout + Webhooks |
| Auth | Django AllAuth |
| Admin | Django Jazzmin |
| Rich Text | CKEditor (django-ckeditor) |
| Static Files | WhiteNoise |
| CDN/Storage | AWS S3 (production) |
| AI Generation | MiniMax API |
| Web Server | Nginx (production) |
| Deployment | Raspberry Pi 4 compatible |

---

## ⚡ Quick Start

```bash
# 1. Clone
git clone https://github.com/Ada-555/ecommerce.git
cd ecommerce

# 2. Create virtual environment
python3 -m venv venv && source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations + create superuser
python manage.py migrate
python manage.py createsuperuser

# 5. Start development server
DEVELOPMENT=1 SECRET_KEY=test python manage.py runserver 0.0.0.0:8023
```

Visit `http://localhost:8023` — admin at `http://localhost:8023/admin/`

---

## 🌐 Domain & Subdomain Setup

Orderimo serves three stores via subdomains in production:

| Store | Domain | Theme | Niche |
|-------|--------|-------|-------|
| Orderimo | orderimo.com | Cyan/Neon | General dropshipping |
| PetShop Ireland | petshopie.com | Green/Earthy | Pet supplies (IE) |
| DigitalHub | digitalhub.store | Purple/Modern | Digital products |

### DNS Records

Add A records for each subdomain pointing to your server IP:

```
orderimo.com        → 192.0.2.1
petshopie.com       → 192.0.2.1
digitalhub.store     → 192.0.2.1
```

Or use CNAME records if using a CDN:

```
orderimo.com        → orderimo.herokuapp.com  (or your server)
petshopie.com       → orderimo.herokuapp.com
digitalhub.store     → orderimo.herokuapp.com
```

### Nginx Subdomain Routing

Configure nginx to route each subdomain to the same Django app, which then handles store selection:

```nginx
# /etc/nginx/sites-available/orderimo

# ─── Primary domain ───
server {
    listen 80;
    server_name orderimo.com www.orderimo.com;
    return 301 https://orderimo.com$request_uri;
}

server {
    listen 443 ssl;
    server_name orderimo.com www.orderimo.com;
    include /etc/nginx/ssl-params.conf;  # SSL cert from Let's Encrypt

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8023;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/  { alias /home/pi/ecommerce/static/; }
    location /media/  { alias /home/pi/ecommerce/media/; }
}

# ─── PetShop Ireland subdomain ───
server {
    listen 80;
    server_name petshopie.com www.petshopie.com;
    return 301 https://petshopie.com$request_uri;
}

server {
    listen 443 ssl;
    server_name petshopie.com www.petshopie.com;
    include /etc/nginx/ssl-params.conf;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8023;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Store-Slug petshop-ie;
    }

    location /static/  { alias /home/pi/ecommerce/static/; }
    location /media/  { alias /home/pi/ecommerce/media/; }
}

# ─── DigitalHub subdomain ───
server {
    listen 80;
    server_name digitalhub.store www.digitalhub.store;
    return 301 https://digitalhub.store$request_uri;
}

server {
    listen 443 ssl;
    server_name digitalhub.store www.digitalhub.store;
    include /etc/nginx/ssl-params.conf;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8023;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Store-Slug digitalhub;
    }

    location /static/  { alias /home/pi/ecommerce/static/; }
    location /media/  { alias /home/pi/ecommerce/media/; }
}
```

### SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Generate certificates for all domains
sudo certbot --nginx -d orderimo.com -d www.orderimo.com
sudo certbot --nginx -d petshopie.com -d www.petshopie.com
sudo certbot --nginx -d digitalhub.store -d www.digitalhub.store

# Auto-renewal (Certbot auto-configures this)
sudo systemctl status certbot.timer
```

### Django ALLOWED_HOSTS

Set these in your environment or `.env`:

```bash
ALLOWED_HOSTS=orderimo.com,www.orderimo.com,petshopie.com,www.petshopie.com,digitalhub.store,www.digitalhub.store,localhost,127.0.0.1
```

---

## 📧 Email Setup

Orderimo uses Django's `send_mail` for transactional emails (order confirmations, contact form, status updates).

### Gmail SMTP

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password: [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Set environment variables:

```bash
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASS=your-16-char-app-password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=Orderimo <noreply@orderimo.com>
```

### Mailgun

```bash
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_HOST_USER=postmaster@your-domain.com
EMAIL_HOST_PASS=your-mailgun-smtp-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=Orderimo <noreply@your-domain.com>
```

### SendGrid

```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASS=your-sendgrid-api-key
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=Orderimo <noreply@your-domain.com>
```

### Development (Console Backend)

In development, emails print to the console instead of being sent:

```python
# settings.py — already configured for DEVELOPMENT=1
if 'DEVELOPMENT' in os.environ:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

---

## 💳 Stripe Setup

### 1. Get API Keys

1. Create an account at [stripe.com](https://stripe.com)
2. Go to **Developers → API Keys**
3. Copy your **Publishable Key** (`pk_live_...` or `pk_test_...`)
4. Copy your **Secret Key** (`sk_live_...` or `sk_test_...`)

### 2. Set Environment Variables

```bash
STRIPE_PUBLIC_KEY=pk_test_51...        #pk_live_... in production
STRIPE_SECRET_KEY=sk_test_51...        #sk_live_... in production
STRIPE_WH_SECRET=whsec_...            # Webhook signing secret
```

### 3. Set Up Webhook Endpoint

1. Go to **Developers → Webhooks → Add endpoint**
2. Endpoint URL: `https://orderimo.com/checkout/wh/` (or your domain)
3. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
4. Copy the **Signing Secret** (`whsec_...`) to `STRIPE_WH_SECRET`

### 4. Test Webhook Locally

```bash
# Install Stripe CLI
# https://stripe.com/docs/stripe-cli

# Login
stripe login

# Forward events to your local server
stripe listen --forward-to localhost:8023/checkout/wh/

# Copy the webhook signing secret shown and set it:
STRIPE_WH_SECRET=whsec_...
```

### 5. Stripe Test Mode

Use test card numbers:
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- Requires authentication: `4000 0025 0000 3155`

---

## 🖥️ Nginx Configuration

### Full Nginx Config for Orderimo

```nginx
# /etc/nginx/sites-available/orderimo

upstream orderimo_app {
    server 127.0.0.1:8023 fail_timeout=0;
}

# HTTP → HTTPS redirect (primary domain)
server {
    listen 80;
    server_name orderimo.com www.orderimo.com;
    return 301 https://orderimo.com$request_uri;
}

# HTTPS main site
server {
    listen 443 ssl http2;
    server_name orderimo.com www.orderimo.com;

    ssl_certificate /etc/letsencrypt/live/orderimo.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/orderimo.com/privkey.pem;
    include /etc/nginx/ssl-params.conf;

    client_max_body_size 10M;

    root /home/pi/ecommerce;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/rss+xml application/atom+xml image/svg+xml;

    location /static/ {
        alias /home/pi/ecommerce/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/pi/ecommerce/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://orderimo_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }
}

# Additional subdomain servers (petshopie.com, digitalhub.store)
# See Domain & Subdomain Setup section above
```

```bash
# Activate
sudo ln -s /etc/nginx/sites-available/orderimo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🗄️ PostgreSQL Setup on Raspberry Pi

### 1. Install PostgreSQL

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Create Database and User

```bash
sudo -u postgres psql
```

```sql
-- Create database
CREATE DATABASE orderimo_db;

-- Create user
CREATE USER orderimo_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE orderimo_db TO orderimo_user;

-- Allow user to create schemas (needed for extensions)
GRANT ALL ON SCHEMA public TO orderimo_user;

-- Set default schema for user
ALTER DATABASE orderimo_db OWNER TO orderimo_user;

\q
```

### 3. Configure Django to Use PostgreSQL

```bash
# Option A: DATABASE_URL environment variable (recommended)
DATABASE_URL=postgres://orderimo_user:your_secure_password@localhost:5432/orderimo_db

# Option B: Direct settings in .env / settings
DB_NAME=orderimo_db
DB_USER=orderimo_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

```python
# In settings.py — already handles DATABASE_URL automatically
if 'DATABASE_URL' in os.environ:
    DATABASES = {'default': dj_database_url.parse(os.environ['DATABASE_URL'])}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

### 4. Run Migrations on PostgreSQL

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## 🚀 Deployment to Raspberry Pi

### Prerequisites

- Raspberry Pi 4 (4GB+ RAM recommended)
- Raspberry Pi OS (64-bit) or Ubuntu Server 22.04
- Domain name pointed to your Pi's IP
- Python 3.10+, nginx, PostgreSQL (see above)

### Step 1: Server Setup

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip nginx postgresql postgresql-contrib git certbot python3-certbot-nginx
```

### Step 2: Clone & Configure Application

```bash
# Clone repository
git clone https://github.com/Ada-555/ecommerce.git /home/pi/ecommerce
cd /home/pi/ecommerce

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Gunicorn (production WSGI server)
pip install gunicorn
```

### Step 3: Environment Variables

Create `/home/pi/ecommerce/.env`:

```bash
SECRET_KEY=your_django_secret_key_here
DATABASE_URL=postgres://orderimo_user:your_secure_password@localhost:5432/orderimo_db
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WH_SECRET=whsec_...
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASS=your-app-password
DEBUG=False
ALLOWED_HOSTS=orderimo.com,www.orderimo.com,petshopie.com,www.petshopie.com,digitalhub.store,www.digitalhub.store
LIVE_LINK=https://orderimo.com/
USE_AWS=1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=eu-north-1
```

### Step 4: Database Migrations & Static Files

```bash
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### Step 5: systemd Service (Gunicorn)

Create `/etc/systemd/system/orderimo.service`:

```ini
[Unit]
Description=Orderimo Gunicorn Service
After=network.target postgresql.service

[Service]
User=pi
Group=www-data
WorkingDirectory=/home/pi/ecommerce
ExecStart=/home/pi/ecommerce/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8023 \
    --timeout 120 \
    --access-logfile /var/log/orderimo/access.log \
    --error-logfile /var/log/orderimo/error.log \
    ecommerce.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo mkdir -p /var/log/orderimo
sudo chown pi:pi /var/log/orderimo
sudo systemctl daemon-reload
sudo systemctl enable orderimo
sudo systemctl start orderimo
sudo systemctl status orderimo
```

### Step 6: Nginx Reverse Proxy

See [Nginx Configuration](#-nginx-configuration) section above.

### Step 7: SSL with Let's Encrypt

```bash
sudo certbot --nginx -d orderimo.com -d www.orderimo.com
sudo systemctl reload nginx
```

### Step 8: Cron Jobs

```bash
# Edit crontab
crontab -e

# Add: generate AI blog posts daily at 6 AM
0 6 * * * cd /home/pi/ecommerce && /home/pi/ecommerce/venv/bin/python manage.py generate_blogs --all >> /var/log/blog_gen.log 2>&1

# Certbot auto-renewal is handled by systemd timer
sudo systemctl status certbot.timer
```

---

## 🏪 Adding a New Store

### Step 1: Add Store Configuration

Add to `ecommerce/store_config.py`:

```python
STORES = {
    # ... existing stores ...
    'my-store': {
        'name': 'My Store',
        'tagline': 'Your Store Tagline',
        'theme': 'teal',  # Must match a theme in brands.css
        'slug': 'my-store',
        'contact_email': 'hello@mystore.com',
    },
}
```

### Step 2: Add Store Theme CSS

In `static/css/brands.css`:

```css
.store-my-store {
    --brand-primary: #0d9488;
    --brand-secondary: #14b8a6;
    --brand-accent: #5eead4;
    --brand-bg: #f0fdfa;
}
```

### Step 3: Add Products

Assign products to the new store via the `store` field in admin (`/admin/products/product/add/`), or bulk-assign via Django shell:

```bash
python manage.py shell
```
```python
from products.models import Product
Product.objects.filter(id__in=[1,2,3]).update(store='my-store')
```

### Step 4: Add Blog Topics

Create `my_store_blog_topics.json`:

```json
[
    {"topic": "Getting Started with Our Products"},
    {"topic": "Top 10 Product Tips"}
]
```

### Step 5: Generate Initial Blog Posts

```bash
python manage.py generate_blogs --store my-store
```

---

## 🤖 Blog AI Generator

Orderimo generates AI-powered blog posts via the MiniMax API.

### Setup

```bash
# Set your MiniMax API key
export MINIMAX_API_KEY=your_api_key_here
export MINIMAX_API_HOST=https://api.minimax.chat
```

### Generate Blog Posts

```bash
# All stores
python manage.py generate_blogs --all

# Specific store
python manage.py generate_blogs --store orderimo

# Specific topic
python manage.py generate_blogs --store petshop-ie --topic "Best Dog Breeds for Irish Apartments"

# Multiple posts
python manage.py generate_blogs --store digitalhub --count 3

# Preview (don't save)
python manage.py generate_blogs --store orderimo --preview
```

### Blog Topics by Store

Store-specific topics are defined in JSON fixture files:
- `orderimo_blog_topics.json`
- `petshopie_blog_topics.json`
- `digitalhub_blog_topics.json`

### Cron Schedule

```bash
# Generate 1 post per store daily at 6 AM
0 6 * * * cd /home/pi/ecommerce && /home/pi/ecommerce/venv/bin/python manage.py generate_blogs --all >> /var/log/blog_gen.log 2>&1
```

---

## 🔑 API Keys Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | ✅ | Django secret key. Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEVELOPMENT` | ✅ (dev) | Set to `1` for development mode (console email backend, debug toolbar) |
| `DEBUG` | ✅ (prod) | Set to `False` in production |
| `ALLOWED_HOSTS` | ✅ (prod) | Comma-separated list of allowed domains |
| `DATABASE_URL` | ✅ (prod) | PostgreSQL connection string: `postgres://user:pass@host:5432/dbname` |
| `STRIPE_PUBLIC_KEY` | ✅ | Stripe publishable key (`pk_test_...` or `pk_live_...`) |
| `STRIPE_SECRET_KEY` | ✅ | Stripe secret key (`sk_test_...` or `sk_live_...`) |
| `STRIPE_WH_SECRET` | ✅ | Stripe webhook signing secret (`whsec_...`) |
| `EMAIL_HOST_USER` | For email | SMTP username (e.g., Gmail app password username) |
| `EMAIL_HOST_PASS` | For email | SMTP password (e.g., Gmail 16-char app password) |
| `EMAIL_HOST` | For email | SMTP server (`smtp.gmail.com`, `smtp.mailgun.org`, etc.) |
| `EMAIL_PORT` | For email | SMTP port (`587` for TLS, `465` for SSL) |
| `EMAIL_USE_TLS` | For email | Set to `True` for TLS |
| `DEFAULT_FROM_EMAIL` | For email | Sender email address |
| `USE_AWS` | Optional | Set to `1` to use AWS S3 for static/media files |
| `AWS_ACCESS_KEY_ID` | If USE_AWS | AWS access key ID |
| `AWS_SECRET_ACCESS_KEY` | If USE_AWS | AWS secret access key |
| `AWS_STORAGE_BUCKET_NAME` | If USE_AWS | S3 bucket name |
| `AWS_S3_REGION_NAME` | If USE_AWS | S3 region (e.g., `eu-north-1`) |
| `LIVE_LINK` | Optional | Production URL (e.g., `https://orderimo.com/`) |
| `SITE_DOMAIN` | Optional | Primary domain |
| `MINIMAX_API_KEY` | For AI blogs | MiniMax API key for blog generation |
| `MINIMAX_API_HOST` | For AI blogs | MiniMax API base URL |

---

## 🔧 Troubleshooting

### Development Server Won't Start

```bash
# Check port is not in use
lsof -i :8023

# Kill any existing process
sudo kill $(lsof -t -i:8023)

# Run with explicit settings
DEVELOPMENT=1 SECRET_KEY=test python manage.py runserver 0.0.0.0:8023
```

### Migration Errors

```bash
# Check for conflicting migrations
python manage.py makemigrations --check

# If models changed and migrations exist, fake the initial migration
python manage.py migrate --fake-initial

# Reset migrations (dev only!)
python manage.py reset_db --router products
python manage.py makemigrations products
python manage.py migrate
```

### Test Failures — Session/Cache Errors

If tests fail with `AttributeError` on `force_insert` or cache backend errors:

```bash
# Ensure cache is using LocMemCache (not DummyCache) during tests
# The settings.py automatically switches to LocMemCache when 'test' is in sys.argv

# Run tests with explicit flag
python manage.py test --verbosity=2

# If BlogPage.save() errors appear, ensure the model accepts **kwargs:
# models.py: super().save(*args, **kwargs)  ← must pass kwargs
```

### Stripe Webhook Not Working

1. **Check webhook is reachable:**
   ```bash
   curl -X POST https://orderimo.com/checkout/wh/ \
     -H "Content-Type: application/json" \
     -d '{"type": "test"}'
   ```

2. **Use Stripe CLI to test locally:**
   ```bash
   stripe listen --forward-to localhost:8023/checkout/wh/
   # Then trigger a test payment in Stripe dashboard
   ```

3. **Verify WH_SECRET matches:**
   ```bash
   # Check the signing secret in Stripe Dashboard → Developers → Webhooks
   # Ensure it matches STRIPE_WH_SECRET environment variable exactly
   ```

### 500 Error on Product Detail

- Check the product has a valid category FK (nullable, but some queries may fail)
- If using `is_in_stock` in filters: this is a **property**, not a DB field — use `stock_quantity__gt=0` instead
- Check the template exists at `products/templates/products/product_detail.html`

### Email Not Sending in Production

```bash
# Test email from Django shell
python manage.py shell
```
```python
from django.core.mail import send_mail
send_mail('Test', 'Body', 'noreply@yoursite.com', ['your@email.com'], fail_silently=False)
```

- If using Gmail: ensure you've generated an **App Password**, not your regular password
- If using Mailgun: verify your domain is verified and SMTP credentials are correct
- Check `DEFAULT_FROM_EMAIL` matches your authenticated SMTP domain

### CSS/Branding Not Updating

```bash
# Clear browser cache (hard refresh: Ctrl+Shift+R)
# Or in Django:
python manage.py collectstatic --noinput
# WhiteNoise serves updated static files automatically

# If using S3:
# Ensure STATICFILES_STORAGE is set correctly and CloudFront cache is invalidated
```

### Cookie Consent Banner Not Appearing

- Check `accept_cookies` view is wired up at `/accept-cookies/`
- The banner only shows when `request.session.get('cookies_accepted')` is not `True`
- In tests: the session engine needs to be configured (see Test Failures section above)

### Blog AI Generation Fails

```bash
# Check MiniMax API key is set
echo $MINIMAX_API_KEY

# Test API connection
curl -X POST https://api.minimax.chat/v1/text/chatcompletion_pro?GroupId=your_group_id \
  -H "Authorization: Bearer $MINIMAX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"abab5.5-chat","messages":[{"role":"user","content":"hello"}]}'

# Check blog topics JSON files exist
ls -la */fixtures/*blog*.json
```

### Nginx 502 Bad Gateway

```bash
# Check Gunicorn is running
sudo systemctl status orderimo

# Check Gunicorn socket
curl 127.0.0.1:8023

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart orderimo nginx
```

### Database Locked (SQLite in Production)

**Switch to PostgreSQL for production** (see [PostgreSQL Setup](#-postgresql-setup-on-raspberry-pi)). SQLite is not suitable for production deployments with concurrent access.

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test --verbosity=1

# Run specific app
python manage.py test bag --verbosity=2
python manage.py test products --verbosity=2
python manage.py test blog --verbosity=2

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # opens htmlcov/index.html
```

### Manual Testing Checklist

```
Store & Navigation
  ☐ Homepage loads with correct store theme
  ☐ Store switcher changes product catalog and branding
  ☐ Mega menu categories display correctly
  ☐ Footer links: About, FAQ, Privacy, Terms, Cookies all load

Products
  ☐ Product listing page with pagination (12 per page)
  ☐ Product search returns relevant results
  ☐ Category filter works
  ☐ Sort by price/name/rating works
  ☐ Product detail page renders with images, price, stock status
  ☐ Add to bag works with and without sizes

Bag & Checkout
  ☐ Add item to bag → redirects correctly
  ☐ Adjust quantity → grand total updates
  ☐ Remove item → bag updates
  ☐ Free delivery threshold (£80) shows correct delivery cost
  ☐ Checkout form validates all fields
  ☐ Stripe payment flow completes (test card)

User Accounts
  ☐ Register new account
  ☐ Login / Logout
  ☐ Account dashboard shows order history
  ☐ Wishlist add/remove works

Legal Pages
  ☐ /about/contact/ — form submits and shows success message
  ☐ /about/faq/ — accordion expands/collapses
  ☐ /about/privacy/ — page loads with all sections
  ☐ /about/terms/ — page loads with all sections
  ☐ /about/cookies/ — cookie table renders

Admin
  ☐ /admin/ — Jazzmin UI loads
  ☐ Products, Categories, Orders, Blog all manageable via admin
  ☐ CKEditor renders on blog/about edit pages
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Add tests: `python manage.py test` must pass
5. Commit: `git commit -m 'Add my feature'`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request

### Coding Standards

- **Python**: Follow PEP 8, max line length 88 (Black-compatible)
- **Templates**: Django template syntax, Bootstrap 5 utility classes
- **JavaScript**: Vanilla JS only (no jQuery), ES6+
- **CSS**: Bootstrap utilities + custom CSS in `base.css` / `brands.css`
- **Testing**: All new features must include tests; 101 tests must pass before merging

### Git Commit Format

```
Phase N: [Short description of what was done]

- Bullet points of specific changes
- Any breaking changes noted
```

---

## 📄 License

MIT License — © 2026 Orderimo Ltd, Dublin, Ireland

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
