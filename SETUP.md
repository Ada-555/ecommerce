# Orderimo — Setup Guide

Step-by-step instructions to get the Orderimo e-commerce platform running from scratch.

---

## Prerequisites

| Requirement | Version | Install |
|-------------|---------|---------|
| Python | 3.12+ | `sudo apt install python3.13 python3.13-venv` |
| PostgreSQL | 14+ | `sudo apt install postgresql postgresql-contrib` |
| Git | any | `sudo apt install git` |
| Stripe account | free | [stripe.com](https://stripe.com) (test mode is free forever) |

---

## Step 1 — Clone the Repository

```bash
cd /home/aipi/.openclaw/workspace
git clone <repository-url> KC-7-ecommerce
cd KC-7-ecommerce
```

---

## Step 2 — Create and Activate the Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal.

---

## Step 3 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

If you get build errors on `cryptography` or `lxml`, install system dependencies first:

```bash
sudo apt install -y \
  build-essential \
  python3-dev \
  libpq-dev \
  libxml2-dev \
  libxslt1-dev \
  zlib1g-dev \
  libjpeg-dev \
  libffi-dev \
  libssl-dev
pip install -r requirements.txt
```

---

## Step 4 — Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` in your editor and set the following:

### Minimum required for local development

```env
SECRET_KEY=any-random-string-here
DEBUG=True
DEVELOPMENT=1
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

### Recommended: add Stripe test keys

1. Go to [dashboard.stripe.com/test/apikeys](https://dashboard.stripe.com/test/apikeys)
2. Copy your **Publishable key** and **Secret key**
3. Add to `.env`:

```env
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

> Without Stripe keys, checkout will show a friendly "not configured" message instead of crashing.

---

## Step 5 — Set Up the Database

### Option A — SQLite (fastest, no setup)

Leave `DATABASE_URL=` blank in `.env`. SQLite will be used automatically.

### Option B — PostgreSQL

```bash
# Create the database and user
sudo -u postgres psql

CREATE DATABASE orderimo;
CREATE USER orderimo_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE orderimo TO orderimo_user;
\q

# Add to .env
DATABASE_URL=postgres://orderimo_user:your_secure_password@localhost:5432/orderimo
```

Then run migrations:

```bash
source venv/bin/activate
venv/bin/python manage.py migrate
```

---

## Step 6 — Load Sample Data (Optional)

```bash
# Load product fixtures if they exist
venv/bin/python manage.py loaddata products/fixtures/*.json
```

Or generate AI blog content:

```bash
venv/bin/python manage.py generate_blogs --count 5
```

---

## Step 7 — Create a Superuser

```bash
venv/bin/python manage.py createsuperuser
```

Visit `http://localhost:8023/admin/` to access the Django admin panel.

---

## Step 8 — Run the Development Server

```bash
source venv/bin/activate
DEVELOPMENT=1 SECRET_KEY=test venv/bin/python manage.py runserver 0.0.0.0:8023
```

The three stores will be available at:

| Store | URL |
|-------|-----|
| Orderimo | `http://localhost:8023/orderimo/` |
| PetShop Ireland | `http://localhost:8023/petshop/` |
| DigitalHub | `http://localhost:8023/digital/` |

---

## Step 9 — Verify Everything Works

```bash
# Run the test suite
venv/bin/python manage.py test --verbosity=0
```

Expected: **130/130 tests passing**

### Manual checks

- [ ] All 3 store URLs return HTTP 200
- [ ] Product pages load
- [ ] Add to bag works
- [ ] Checkout page loads (Stripe will ask for keys to complete payment)
- [ ] `/admin/` login works
- [ ] `/admin/analytics/` dashboard loads (staff only)
- [ ] Order tracking page loads at `/orderimo/track/<order_number>/`

---

## Step 10 — Stripe Webhooks (for local payment testing)

Install the Stripe CLI:

```bash
# macOS
brew install stripe/stripe-cli/stripe

# Linux
curl -s https://packages.stripe.com/stripe-signing-keys/stable | sudo apt-key add -
echo "deb https://packages.stripe.com/stripe-signing-keys/stable all main" | sudo tee /etc/apt/sources.list.d/stripe.list
sudo apt update && sudo apt install stripe
```

Forward webhooks to your local server:

```bash
stripe listen --forward-to localhost:8023/checkout/webhook/
```

Stripe CLI will output a webhook signing secret like `whsec_...`. Add it to your `.env`:

```env
STRIPE_WH_SECRET=whsec_your_signing_secret_here
```

---

## Step 11 — Email in Development

With `DEVELOPMENT=1`, all emails are printed to the terminal where `runserver` is running. No external email configuration needed.

To use real email in development (e.g., Gmail SMTP):

```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASS=your-app-password  # Generate at: https://myaccount.google.com/apppasswords
DEFAULT_FROM_EMAIL=your-email@gmail.com
# Remove DEVELOPMENT=1 or set DEVELOPMENT=0
```

---

## Step 12 — S3 Static File Storage (Optional)

For production, serve static files from AWS S3:

```env
USE_AWS=1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=eu-north-1
```

Then run `python manage.py collectstatic`.

---

## Common Issues

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'xyz'` | Run `pip install -r requirements.txt` with venv active |
| Checkout crashes | Add Stripe keys to `.env` |
| Static files missing | `venv/bin/python manage.py collectstatic` |
| Database connection error | Check `DATABASE_URL` in `.env`, ensure PostgreSQL is running |
| 403 Forbidden on forms | Ensure `CSRF_TRUSTED_ORIGINS` includes your domain in `settings.py` |
| Images not loading | Check `MEDIA_ROOT`/`MEDIA_URL` in settings and that `media/` directory is writable |

---

_Last updated: 2026-03-29_
