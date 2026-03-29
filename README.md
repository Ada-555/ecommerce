# Orderimo — Multi-Store E-commerce Platform

**One platform. Multiple branded stores.**

Orderimo is a Django-based multi-store e-commerce platform designed for entrepreneurs who want to run multiple independent online stores from a single codebase. Each store has its own branding, product catalog, and customer experience while sharing infrastructure.

---

## 🚀 Features

### Core E-commerce
- **Multi-Store Architecture** — Run 3 independent stores (Orderimo, PetShop Ireland, DigitalHub) from one Django project, switchable via a store selector in the navigation
- **Product Management** — Full CRUD for products with categories, variants, images, SKUs, stock tracking, and rating/reviews
- **Shopping Bag** — Add/remove items, quantity updates, subtotal/delivery calculation, persistent sessions
- **Stripe Checkout** — Full payment integration with Stripe Checkout, webhook support for order confirmation
- **Order Processing** — Order history, status tracking, confirmation emails on status change
- **User Accounts** — Registration/login via Django AllAuth, profile management, order history
- **Search & Filter** — Full-text product search with category, price, and rating filters

### CMS & Content
- **Blog System** — AI-generated blog posts (via MiniMax API) with scheduled daily generation per store, full blog listing and detail pages, Schema.org Article markup
- **About Pages** — Admin-managed about pages with rich text (CKEditor), create/edit/delete via admin UI
- **Contact Page** — Contact form with name, email, subject, message — sends email via Django's `send_mail`
- **FAQ Page** — Bootstrap 5 accordion FAQ with Schema.org FAQPage JSON-LD structured data
- **Privacy Policy** — GDPR-compliant privacy policy covering data collected, third parties (Stripe), user rights, retention
- **Terms & Conditions** — Full legal T&C covering ordering, payment, delivery, returns, liability, governing law (Ireland)
- **Cookie Policy** — Detailed cookie policy with browser management instructions and third-party cookie table
- **Cookie Consent Banner** — Fixed bottom banner for EU cookie law compliance, stored in session

### Admin & Management
- **Django Jazzmin Admin** — Customised admin UI with Orderimo branding, per-model search, collapsible forms, top menu links
- **CKEditor Rich Text** — Rich text editing for blog and about pages
- **Sitemap** — Auto-generated `sitemap.xml` for SEO
- **Robots.txt** — Auto-generated `robots.txt`
- **WhiteNoise** — Static file serving optimized for production

### Security (Phase 8)
- **XSS Protection** — Django template auto-escaping + `SECURE_BROWSER_XSS_FILTER = True`
- **SQL Injection Protection** — All queries via Django ORM (parameterised)
- **CSRF Protection** — Django CSRF middleware + `CSRF_COOKIE_HTTPONLY = True`
- **Clickjacking Protection** — `X_FRAME_OPTIONS = 'DENY'`
- **Content Sniffing Protection** — `SECURE_CONTENT_TYPE_NOSNIFF = True`
- **Session Security** — `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'`
- **Rate Limiting** — AllAuth login rate limits (5 failed attempts per 10 minutes), `django-ratelimit` configured
- **Hardened Production Settings** — `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, secure cookies when `DEBUG=False`
- **Login Attempt Tracking** — Account rate limits configured

### Stores
- **Orderimo** — Generic dropshipping store, cyan/neon theme, general merchandise
- **PetShop Ireland** — Pet supplies store, green/earthy theme, Irish market focus (petshop-ie slug)
- **DigitalHub** — Digital products store, purple/modern theme, e-books/courses/downloads (digitalhub slug)

### Automation
- **Blog Generation** — `python manage.py generate_blogs --all` generates AI blog posts via MiniMax API
- **Cron-Ready** — Blog generation command is cron-schedulable (e.g., `0 6 * * *`)
- **Low Stock Alerts** — Stock level tracking in admin
- **Auto Status Emails** — Order status change triggers email to customer

---

## 📦 Stores

| Store | Domain | Theme | Niche |
|-------|--------|-------|-------|
| Orderimo | orderimo.com | Cyan/Neon | General dropshipping |
| PetShop Ireland | petshopie.com | Green/Earthy | Pet supplies (IE) |
| DigitalHub | digitalhub.store | Purple/Modern | Digital products |

Switch stores via the store selector in the top navigation bar.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 5.2 + Python 3 |
| Frontend | Bootstrap 5.3, Vanilla JS, Font Awesome 6 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Payments | Stripe Checkout + Webhooks |
| Authentication | Django AllAuth |
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
# Clone the repository
git clone https://github.com/Ada-555/ecommerce.git
cd ecommerce

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver 0.0.0.0:8023
```

Visit `http://localhost:8023` — admin panel at `http://localhost:8023/admin/`

---

## 🔑 Environment Variables

```bash
# Django
SECRET_KEY=your_secret_key_here
DEVELOPMENT=1          # Remove for production
DEBUG=False           # Set to False in production

# Stripe
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WH_SECRET=whsec_...

# Email (Gmail SMTP example)
EMAIL_HOST_USER=you@gmail.com
EMAIL_HOST_PASS=your_app_password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True

# Database (PostgreSQL — production)
DATABASE_URL=postgres://user:password@localhost:5432/orderimo

# AWS S3 (production static/media)
USE_AWS=1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=kc-ecommerce
AWS_S3_REGION_NAME=eu-north-1

# Site
SITE_DOMAIN=orderimo.com
LIVE_LINK=https://orderimo.com/
```

### Generating a Django Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🏪 Adding a New Store

### Step 1: Add Store Configuration

Edit the store switcher in `templates/includes/main-nav.html` and `templates/base.html`. Add a new route:

```python
# stores/urls.py
path('set_my-store/', views.set_active_store, {'store_slug': 'my-store'}, name='set_my_store'),
```

### Step 2: Create Store Theme

Add theme variables in `static/css/store_themes.css`:

```css
.store-my-store { --brand-primary: #FF6B00; --brand-secondary: #FF8C42; }
```

### Step 3: Add Products

Products are filtered by `store` field (FK to `StoreConfig`). Assign products to the new store in the admin panel at `/admin/products/product/`.

### Step 4: Customise Branding

Update the store-specific section in `templates/base.html` to display the correct logo, hero content, and footer per active store.

### Step 5: Add Blog Topics

Add topics to `store_blog_topics.json` for the new store, then run:

```bash
python manage.py generate_blogs --store my-store --topic "My Topic"
```

---

## 📧 Email Setup

### Gmail SMTP

1. Enable 2-Factor Authentication on your Google account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Generate an app password for "Mail"
4. Set environment variables:

```bash
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASS=your-16-char-app-password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

### Mailgun

```bash
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_HOST_USER=postmaster@yourdomain.com
EMAIL_HOST_PASS=your-mailgun-smtp-password
EMAIL_USE_TLS=True
```

### SendGrid

```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASS=your-sendgrid-api-key
EMAIL_USE_TLS=True
```

---

## 🌐 Deployment

### Raspberry Pi 4 + Nginx + PostgreSQL

#### 1. Server Setup

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip nginx postgresql
sudo systemctl start postgresql
```

#### 2. Create Database

```bash
sudo -u postgres psql
CREATE DATABASE orderimo;
CREATE USER orderimo_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE orderimo TO orderimo_user;
\q
```

#### 3. Install Application

```bash
git clone https://github.com/Ada-555/ecommerce.git
cd ecommerce
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Configure Environment

Create `/home/pi/ecommerce/.env`:

```bash
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://orderimo_user:your_password@localhost:5432/orderimo
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WH_SECRET=whsec_...
EMAIL_HOST_USER=...
EMAIL_HOST_PASS=...
DEBUG=False
ALLOWED_HOSTS=your-domain.com
LIVE_LINK=https://your-domain.com/
```

#### 5. Run Migrations & Collect Static

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

#### 6. systemd Service

Create `/etc/systemd/system/orderimo.service`:

```ini
[Unit]
Description=Orderimo Django App
After=network.target postgresql.service

[Service]
Type=oneshot
User=pi
WorkingDirectory=/home/pi/ecommerce
ExecStart=/home/pi/ecommerce/venv/bin/python manage.py runserver 0.0.0.0:8023
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable orderimo
sudo systemctl start orderimo
```

#### 7. Nginx Reverse Proxy

Create `/etc/nginx/sites-available/orderimo`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8023;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/pi/ecommerce/static/;
    }

    location /media/ {
        alias /home/pi/ecommerce/media/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/orderimo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 8. SSL with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
sudo systemctl reload nginx
```

#### 9. Cron Jobs for Blog Generation

```bash
# Edit crontab
crontab -e

# Add: generate blogs at 6 AM daily, one store per day
0 6 * * * cd /home/pi/ecommerce && /home/pi/ecommerce/venv/bin/python manage.py generate_blogs --all >> /var/log/blog_gen.log 2>&1
```

---

## 📊 API Reference

### Internal Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Homepage |
| `/products/` | GET | Product listing with filters |
| `/products/<slug>/` | GET | Product detail |
| `/bag/` | GET | Shopping bag view |
| `/bag/add/<id>/` | POST | Add item to bag (CSRF required) |
| `/bag/adjust/<id>/` | POST | Adjust item quantity (CSRF required) |
| `/bag/remove/<id>/` | POST | Remove item from bag (CSRF required) |
| `/checkout/` | GET/POST | Checkout form & Stripe payment |
| `/checkout/wh/` | POST | Stripe webhook handler |
| `/blog/` | GET | Blog listing |
| `/blog/<slug>/` | GET | Blog post detail |
| `/about/` | GET | About pages listing |
| `/about/contact/` | GET/POST | Contact form |
| `/about/faq/` | GET | FAQ accordion page |
| `/about/privacy/` | GET | Privacy policy |
| `/about/terms/` | GET | Terms & Conditions |
| `/about/cookies/` | GET | Cookie policy |
| `/accounts/signup/` | GET/POST | User registration |
| `/accounts/login/` | GET/POST | User login |
| `/accounts/logout/` | GET/POST | User logout |
| `/accounts/dashboard/` | GET | User account dashboard |
| `/admin/` | GET | Admin panel |
| `/sitemap.xml` | GET | XML sitemap |
| `/robots.txt` | GET | robots.txt |

### Store Switching

| URL | Store |
|-----|-------|
| `/set-store/orderimo/` | Orderimo (default) |
| `/set-store/petshop-ie/` | PetShop Ireland |
| `/set-store/digitalhub/` | DigitalHub |

---

## 🔒 Security

- **HTTPS required** in production (`DEBUG=False`)
- **All secrets** via environment variables (never committed to git)
- **Django ORM** for all database queries (parameterised, SQL injection safe)
- **Django auto-escapes** all template output (XSS safe)
- **CSRF tokens** on all POST forms
- **Rate limiting** on login attempts (5 per 10 min) and contact form
- **Session cookies**: `HttpOnly`, `SameSite=Lax`, `Secure` in production
- **Stripe** handles all card data (PCI DSS compliant)
- **定期审计**: Run `python manage.py check --deploy` for production readiness

### Dependency Audit

```bash
# Check for known vulnerabilities
pip install safety 2>/dev/null
safety check --file=requirements.txt

# Django production check
python manage.py check --deploy
```

---

## 🤖 Automation

### Generate Blog Posts

```bash
# Generate for all stores
python manage.py generate_blogs --all

# Generate for specific store
python manage.py generate_blogs --store orderimo

# Generate for specific topic
python manage.py generate_blogs --store petshop-ie --topic "Best Dog Breeds for Irish Apartments"
```

### Low Stock Alerts

Configure in admin under Products → Products. Products with stock ≤ 5 appear with a low-stock indicator.

### Order Status Emails

Automatically sent when an order's status is updated in the admin panel.

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test --verbosity=2

# Run specific app tests
python manage.py test about --verbosity=2
python manage.py test blog --verbosity=2

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Manual Testing Checklist

- [ ] Homepage loads with correct store theme
- [ ] Store switcher changes product catalog
- [ ] Add product to bag, adjust quantity, remove item
- [ ] Checkout form validates and processes payment
- [ ] Stripe webhook fires and creates order
- [ ] User registration, login, logout work
- [ ] Blog listing and detail pages render
- [ ] AI blog generation creates new posts
- [ ] About/FAQ/Contact/Privacy/Terms/Cookies pages load
- [ ] Contact form sends email (console backend in dev)
- [ ] Cookie consent banner appears, accepts correctly
- [ ] Admin panel loads with Jazzmin UI
- [ ] Sitemap and robots.txt accessible

---

## 📁 Project Structure

```
KC-7-ecommerce/
├── about/                  # About pages app (views, models, admin, templates)
│   ├── templates/about/    # contact.html, faq.html, privacy_policy.html, terms.html, cookies.html
│   ├── views.py            # contact, faq, privacy_policy, terms, cookies, accept_cookies
│   ├── models.py           # AboutPage model
│   ├── forms.py            # AboutPageForm
│   └── urls.py             # URL routing for about pages
├── accounts/               # User accounts app (AllAuth customisations)
├── avatar/                 # User avatar app
├── bag/                    # Shopping bag app
│   ├── contexts.py         # bag_contents context processor
│   └── views.py            # add_to_bag, adjust_bag, remove_from_bag
├── blog/                   # Blog app
│   ├── management/commands/ # generate_blogs command
│   └── templates/blog/     # blog.html, blog_detail.html
├── checkout/               # Checkout & Stripe app
│   ├── webhook_handler.py  # Stripe webhook processing
│   └── views.py            # checkout view
├── custom_storages.py      # AWS S3 storage backends
├── ecommerce/              # Django project settings
│   ├── settings.py         # All settings, security hardening
│   ├── urls.py              # Root URL config
│   └── wsgi.py             # WSGI application
├── home/                   # Homepage app
├── media/                  # User-uploaded media files (gitignored)
├── products/               # Product catalog app
│   ├── admin.py            # Product & Category admin
│   ├── models.py            # Product, Category, Review models
│   └── views.py             # products, product_detail views
├── profiles/               # User profile app
├── static/                  # Static files (CSS, JS, fonts, images)
│   ├── css/
│   │   ├── base.css         # Core styles
│   │   ├── brands.css       # Brand-specific styles (Orderimo, PetShop, DigitalHub)
│   │   └── store_themes.css # Per-store theme variables
│   └── favicon/             # Favicon assets
├── stores/                 # Multi-store configuration app
├── templates/               # Global templates
│   ├── base.html            # Base template with nav, footer, cookie banner
│   └── includes/
│       ├── footer.html      # Footer with legal links
│       ├── main-nav.html    # Main navigation
│       └── mobile-nav.html  # Mobile navigation
├── venv/                    # Virtual environment
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── db.sqlite3               # SQLite database (dev)
├── SECURITY_AUDIT_REPORT.md # Phase 8 security audit results
└── README.md                # This file
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

### Coding Standards

- Python: Follow PEP 8, max line length 88 (Black compatible)
- Templates: Django template syntax, Bootstrap 5 classes
- JavaScript: Vanilla JS only (no jQuery), ES6+
- CSS: Bootstrap 5 utility classes + custom CSS in `base.css`

---

## 📄 License

MIT License — © 2026 Orderimo Ltd, Dublin, Ireland

Permission is hereby granted, free of charge, to any person obtaining a copy of this software to deal in the Software without restriction. See LICENSE file for full details.
