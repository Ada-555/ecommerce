# Orderimo — Multi-Store E-Commerce Platform

> **One platform. Three branded stores.**

Django 5.2 powered e-commerce platform running 3 stores from a single codebase:
- **Orderimo** — General dropshipping
- **PetShop Ireland** — Pet supplies
- **DigitalHub** — Digital products

**Status:** 139 tests passing | Stripe test mode active | All stores live

---

## 🚀 Quick Start

```bash
cd /home/aipi/.openclaw/workspace/KC-7-ecommerce

# Start dev server
DEVELOPMENT=1 venv/bin/python manage.py runserver 0.0.0.0:8023

# Run tests
DEVELOPMENT=1 venv/bin/python manage.py test --verbosity=0
```

**Stores:** http://localhost:8023/orderimo/ | http://localhost:8023/petshop/ | http://localhost:8023/digital/

---

## 🔑 Required Setup

### 1. Stripe (payments — TEST MODE)

Get free test keys: https://dashboard.stripe.com/test/apikeys

Add to `.env`:
```
STRIPE_PUBLIC_KEY=pk_test_YOUR_KEY
STRIPE_SECRET_KEY=sk_test_YOUR_KEY
STRIPE_WH_SECRET=whsec_YOUR_WEBHOOK_SECRET
```

Webhook endpoint (when live): `https://yourdomain.com/checkout/wh/`
Test events: `payment_intent.succeeded`, `checkout.session.completed`, `invoice.paid`

---

## 📧 Email Setup (needed for order confirmations)

### Option 1: Brevo (FREE — recommended)
- Sign up: https://www.brevo.com/ (300 emails/day, no credit card)
- API key: Settings → SMTP & API → Your API key
- Add to `.env`:
  ```
  BREVO_API_KEY=YOUR_BREVO_API_KEY
  DEFAULT_FROM_EMAIL=orders@yourstore.com
  ```
- In `ecommerce/settings.py`, update `EMAIL_BACKEND` to use Brevo SMTP or API

### Option 2: Gmail SMTP (free but limited)
- Enable 2FA → App Passwords → https://myaccount.google.com/apppasswords
- Add to `.env`:
  ```
  EMAIL_HOST_USER=your@gmail.com
  EMAIL_HOST_PASS=your-app-password
  DEFAULT_FROM_EMAIL=your@gmail.com
  ```

### Option 3: Console (dev only — emails print to terminal)
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
Already configured when `DEVELOPMENT=1`.

---

## 🛠️ Everything Else Is Already Configured

| Feature | Status | Notes |
|---------|--------|-------|
| 3 stores | ✅ | Orderimo, PetShop, DigitalHub |
| User accounts | ✅ | Allauth (login/signup/reset) |
| Product reviews | ✅ | Star ratings, verified buyer |
| Order tracking | ✅ | Track by order number |
| Wishlist | ✅ | Heart icon, HTMX toggle |
| Product compare | ✅ | Side-by-side page |
| Crypto payments | ✅ | BTC/USDC via Stripe, XMR via CoinGate |
| Subscriptions | ✅ | Stripe recurring billing |
| Newsletter signup | ✅ | Brevo/Mailchimp API |
| PDF invoices | ✅ | HTML invoice view |
| Blog | ✅ | Public index + post pages |
| Affiliate program | ✅ | Referral codes, commissions |
| GA4 analytics | ✅ | ORM dashboard at /admin/analytics/ |
| Multi-currency | ✅ | EUR/USD/GBP via Frankfurter API |
| Multi-coupon | ✅ | Stackable discount codes |

---

## ⚠️ Known Limitations

- **Affiliate program** — basic implementation, commission payouts need manual PayPal/stripe transfer
- **Blog newsletter** — uses Brevo API, requires `BREVO_API_KEY`
- **Webhooks** — need `STRIPE_WH_SECRET` for production (test mode works without)

---

## 📁 Project Structure

```
KC-7-ecommerce/
├── about/          # Static pages (contact, faq, privacy, etc.)
├── bag/            # Shopping bag
├── blog/           # Blog + newsletter
├── checkout/       # Payments + order processing
├── comparison/     # Product comparison
├── coupons/        # Discount code system
├── home/           # Homepage
├── newsletter/     # Newsletter signup
├── notifications/  # Email notifications
├── products/       # Product catalog
├── profiles/       # User profiles
├── stores/         # Store routing + views
├── subscriptions/  # Stripe recurring
├── tracking/       # Order tracking
├── wishlist/       # Wishlist
└── affiliates/     # Affiliate program
```

---

## 🌐 Production Deployment

1. `DEBUG=False`
2. Add domain to `ALLOWED_HOSTS`
3. Use PostgreSQL: `DATABASE_URL=postgres://user:pass@host:5432/db`
4. `pip install gunicorn && gunicorn ecommerce.wsgi`
5. Nginx + Let's Encrypt
6. Stripe live keys + webhook endpoint

---

## 🧪 Testing

```bash
DEVELOPMENT=1 venv/bin/python manage.py test --verbosity=0
# 139 tests
```

---

_Last updated: 2026-03-29_
