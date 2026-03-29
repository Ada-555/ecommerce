# Orderimo — Multi-Store E-Commerce Platform

> One platform. Multiple branded stores.

Orderimo is a production-ready Django e-commerce platform that powers multiple branded stores from a single codebase. Each store (Plurino, HomeNest, StyleVault) has its own visual identity while sharing infrastructure.

![Platform](https://img.shields.io/badge/Platform-Django_5.2-purple)
![Python](https://img.shields.io/badge/Python_3.13-cyan)
![Bootstrap](https://img.shields.io/badge/Bootstrap_5.3-darkpurple)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Git
- SQLite (default, swap for PostgreSQL in production)

### 1. Clone & Set Up

```bash
# Clone the repository
git clone https://github.com/Ada-555/Orderimo.git
cd Orderimo

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Load category data
python manage.py loaddata products/fixtures/categories.json

# Create a superuser
python manage.py createsuperuser

# Run the development server
DEVELOPMENT=1 SECRET_KEY=test python manage.py runserver 0.0.0.0:8023
```

Visit `http://localhost:8023` — admin at `http://localhost:8023/admin/`

---

## 🏪 The Three Stores

| Store | Theme | Description |
|-------|-------|-------------|
| **Plurino** | Cyan | Tech gadgets & accessories |
| **HomeNest** | Amber | Homeware & interiors |
| **StyleVault** | Pink | Fashion & streetwear |

Each store has:
- Custom CSS variable overrides in `static/css/brands.css`
- Category filtering in the mega-menu
- Brand-specific product filtering

---

## ⚙️ Configuration

### Environment Variables

```bash
# Development
DEVELOPMENT=1
SECRET_KEY=your-secret-key-here

# Production — disable DEVELOPMENT, set:
SECRET_KEY=your-production-secret
DEBUG=False
ALLOWED_HOSTS=.yourdomain.com

# Stripe
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WH_SECRET=whsec_...

# Email (Gmail SMTP)
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASS=your-app-password

# AWS (optional — for S3 media storage)
USE_AWS=True
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=...
```

### Store Configuration

Stores are defined in `ecommerce/store_config.py`:

```python
STORES = {
    'plurino': {'name': 'Plurino', 'tagline': 'Tech Gadgets & Accessories', 'theme': 'cyan'},
    'homenest': {'name': 'HomeNest', 'tagline': 'Curated Home & Living', 'theme': 'amber'},
    'stylevault': {'name': 'StyleVault', 'tagline': 'Fashion & Streetwear', 'theme': 'pink'},
}
```

---

## 📦 Apps Overview

| App | Purpose |
|-----|---------|
| `home` | Homepage, hero, store cards |
| `products` | Products, categories, variants, stock tracking |
| `bag` | Shopping bag, session management |
| `checkout` | Stripe payments, order management |
| `profiles` | User profiles, default addresses |
| `blog` | Blog/CMS with CKEditor |
| `about` | About pages, contact info |
| `accounts` | Dashboard, wishlist |
| `stores` | Multi-store configuration |
| `avatar` | User avatars (allauth) |

---

## 🛠️ Management Commands

```bash
# Load categories
python manage.py loaddata products/fixtures/categories.json

# Generate blog posts (AI-powered)
python manage.py generate_blogs --count 5 --store plurino

# Collect static files (production)
python manage.py collectstatic
```

---

## 🗄️ Product Data Model

Key fields on the `Product` model:

- `stock_quantity` — current stock level
- `low_stock_threshold` — threshold for "Low Stock" warning
- `sku` — unique product identifier
- `featured` — featured on homepage
- `brand` — store brand (Plurino / HomeNest / StyleVault)
- **Stock Status** computed property: `In Stock` / `Low Stock` / `Out of Stock`

`ProductVariant` model for size/color variants with override pricing and per-variant stock.

---

## 💳 Stripe Setup

1. Create a Stripe account at [stripe.com](https://stripe.com)
2. Get your API keys from the Stripe Dashboard
3. Set up a webhook endpoint at `/checkout/wh/` pointing to these events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
4. Set `STRIPE_WH_SECRET` in your environment

---

## 📧 Email Setup (Gmail SMTP)

1. Enable 2-Factor Authentication on your Google account
2. Create an App Password: Google Account → Security → App Passwords
3. Set `EMAIL_HOST_USER` and `EMAIL_HOST_PASS` environment variables

For production, use a transactional email service (SendGrid, Mailgun, etc.) via SMTP.

---

## 🚀 Deployment to Raspberry Pi + nginx

### 1. Set Up the Pi

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-venv python3-pip nginx supervisor -y
```

### 2. Create the service file

```bash
sudo nano /etc/systemd/system/orderimo.service
```

```ini
[Unit]
Description=Orderimo Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/pi/Orderimo
ExecStart=/home/pi/Orderimo/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/tmp/orderimo.sock \
    ecommerce.wsgi:application \
    --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. nginx config

```bash
sudo nano /etc/nginx/sites-available/orderimo
```

```nginx
upstream orderimo {
    server unix:/tmp/orderimo.sock fail_timeout=0;
}

server {
    listen 80;
    server_name orderimo.com;

    client_max_body_size 10M;

    location /static/ {
        alias /home/pi/Orderimo/static/;
    }

    location /media/ {
        alias /home/pi/Orderimo/media/;
    }

    location / {
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://orderimo;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/orderimo /etc/nginx/sites-enabled/
sudo systemctl reload nginx
sudo systemctl enable orderimo
sudo systemctl start orderimo
```

### 4. SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d orderimo.com
```

### 5. First Deployment Steps

```bash
# Clone to the Pi
git clone https://github.com/Ada-555/Orderimo.git /home/pi/Orderimo
cd /home/pi/Orderimo

# Set up venv and install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
# Add to /etc/environment or use a .env file with python-dotenv

# Run migrations
python manage.py migrate

# Collect static
python manage.py collectstatic --noinput

# Restart
sudo systemctl restart orderimo
```

---

## 🔒 Security Notes

- Set `DEBUG=False` in production
- Use `SECRET_KEY` from environment, never hardcode
- Use HTTPS in production (Let's Encrypt)
- Keep `ALLOWED_HOSTS` restricted to your domain
- Run `python manage.py check --deploy` before going live

---

## 📁 Project Structure

```
KC-7-ecommerce/
├── accounts/          # User dashboard, wishlist
├── about/             # About/CMS pages
├── bag/               # Shopping bag
├── blog/              # Blog app + AI blog generator
├── checkout/          # Stripe checkout + webhooks
├── ecommerce/         # Core settings + store_config
├── home/              # Homepage
├── products/          # Products, categories, variants
├── profiles/          # User profile + addresses
├── stores/            # Multi-store configuration
├── templates/          # Base templates + includes
├── static/            # CSS, JS, fonts
└── media/             # User-uploaded images
```

---

## 📝 License

MIT License — feel free to use, modify, and distribute.
