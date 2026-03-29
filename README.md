# Orderimo E-Commerce Platform

Multi-store e-commerce platform running on Django 5.x with Stripe, PostgreSQL, and Bootstrap 5 dark theme.

**3 Live Stores:**
- Orderimo: http://192.168.0.59:8023/orderimo/
- PetShop Ireland: http://192.168.0.59:8023/petshop/
- DigitalHub: http://192.168.0.59:8023/digital/
- Also: http://192.168.0.59:8023/digitalhub/

---

## 🚀 Quick Start

```bash
cd /home/aipi/.openclaw/workspace/KC-7-ecommerce
DEVELOPMENT=1 SECRET_KEY=test venv/bin/python manage.py runserver 0.0.0.0:8023
```

---

## 🔑 API Keys Needed

The platform needs these keys to be added to `.env`:

### Required (for payments to work)

| Service | Key | Get it free |
|--------|-----|------------|
| **Stripe** | `STRIPE_PUBLIC_KEY=pk_test_...` | https://dashboard.stripe.com/test/apikeys |
| **Stripe** | `STRIPE_SECRET_KEY=sk_test_...` | https://dashboard.stripe.com/test/apikeys |

### Optional (for emails)

| Service | Key | Get it free |
|--------|-----|------------|
| **Brevo (Sendinblue)** | `BREVO_API_KEY=...` | https://www.brevo.com/ — 300 emails/day free, no credit card |
| **Mailchimp** | `MAILCHIMP_API_KEY=...` | https://mailchimp.com/developer/ |
| **CoinGate** | `COINGATE_API_KEY=...` | https://coingate.com/ (for XMR crypto) |

### Optional (for analytics)

| Service | Key | Get it free |
|--------|-----|------------|
| **Google Analytics GA4** | `GA_MEASUREMENT_ID=G-...` + service account JSON | https://analytics.google.com |

---

## 📋 .env File Template

Create `/home/aipi/.openclaw/workspace/KC-7-ecommerce/.env`:

```env
# Django
SECRET_KEY=your-super-secret-key-here
DEBUG=True
DEVELOPMENT=1
ALLOWED_HOSTS=192.168.0.59,localhost,127.0.0.1

# Database
DATABASE_URL=postgres://user:password@localhost:5432/orderimo

# Stripe (TEST MODE - free forever)
STRIPE_PUBLIC_KEY=pk_test_YOUR_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET

# Email (Brevo - free, 300/day)
BREVO_API_KEY=YOUR_BREVO_API_KEY
DEFAULT_FROM_EMAIL=orders@orderimo.com

# Crypto (CoinGate - for Monero)
COINGATE_API_KEY=YOUR_COINGATE_API_KEY

# Mailchimp (optional - alternative to Brevo)
MAILCHIMP_API_KEY=YOUR_MAILCHIMP_KEY
MAILCHIMP_SERVER=us21
MAILCHIMP_LIST_ID=YOUR_LIST_ID

# Multi-currency (Frankfurter API - free, no key needed)
# Currency conversion is automatic via Frankfurter API
```

---

## ✅ Features Built (16 Complete)

1. **Multi-store** — Orderimo, PetShop Ireland, DigitalHub
2. **Per-store admin** — store-scoped admin views
3. **Product reviews** — star ratings, verified buyer badges, moderation
4. **Order tracking page** — track by order number + email
5. **Email notifications** — order confirmation, shipped, delivered
6. **Wishlist** — heart icon, HTMX toggle, per-store
7. **Store-specific search** — scoped to active store
8. **Crypto payments** — BTC/USDC via Stripe, XMR via CoinGate
9. **Multi-currency** — EUR, USD, GBP with auto-conversion
10. **Affiliate program** — referral links, commission tracking
11. **Newsletter signup** — Mailchimp/Brevo integration
12. **Subscriptions** — Stripe recurring billing
13. **Product comparisons** — side-by-side compare page
14. **GA4 analytics** — ORM-based dashboard at /admin/analytics/
15. **PDF invoices** — HTML invoice view
16. **Multi-coupon system** — stackable discount codes
17. **Abandoned cart emails** — 24h reminder management command

---

## 🧪 Running Tests

```bash
cd /home/aipi/.openclaw/workspace/KC-7-ecommerce
venv/bin/python manage.py test --verbosity=0
```

---

## 🌐 Production Deployment

1. Set `DEBUG=False`
2. Add your domain to `ALLOWED_HOSTS`
3. Use Gunicorn + Nginx
4. Set up PostgreSQL
5. Configure Stripe live keys
6. Run `python manage.py collectstatic`
7. Set up HTTPS (Let's Encrypt)

---

_Last updated: 2026-03-29_
