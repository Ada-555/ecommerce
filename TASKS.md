# Plurino / Orderimo — Build Task Dashboard

## 🚦 Status Legend
- ✅ **DONE** — completed and merged
- 🟡 **IN PROGRESS** — actively being built
- ⏳ **QUEUED** — next to spawn
- 🔜 **SOON** — planned

---

## ✅ Completed

| Task | Commit | Notes |
|------|--------|-------|
| Store-scoped search | `6e12240` | ✅ /orderimo/search/, /petshop/search/, /digital/search/ |
| Email notifications (full) | `5a07479` | ✅ order confirmation/shpped/delivered, welcome emails |
| Order tracking (full) | `5a07479` | ✅ tracking page, status fields, email integration |
| Crypto payments (BTC/USDC/XMR) | `dd1084b` | ✅ Stripe crypto + CoinGate for XMR |

---

## 🟡 Active — Partitioned by Directory

| Agent | Owns | Features |
|-------|------|----------|
| **wishlist-retry** | `wishlist/` | Heart icon, wishlist page, HTMX toggle |
| **phase12-frontend** | `products/templates/` | Review display, submit form, verified buyer badge |
| **agent-payments** | `coupons/`, `subscriptions/` | Multi-coupon + Stripe subscriptions |
| **order-tracking-retry** | `tracking/` | Tracking page, order status view |
| **agent-ops** | `newsletter/`, `invoices/` | Newsletter (Mailchimp), abandoned cart, PDF invoices |

---

## ⏳ Queued (next slots)

| # | Agent | Owns | Features |
|---|-------|------|----------|
| 6 | agent-seo | `comparison/`, `analytics/` | Product comparisons, GA4 dashboard |
| 7 | agent-currencies | `settings.py`, templates | Multi-currency (EUR/USD/GBP) |
| 8 | agent-affiliate | `affiliates/` | Affiliate program with referral tracking |
| 9 | agent-final | misc | Final polish, docs, deployment checks |

---

## 📋 Agent Log

| Time | Agent | Commit | Status |
|------|-------|--------|--------|
| 08:44 | email-notifications | `5a07479` — 1,851 lines | ✅ Done |
| 08:44 | crypto-payments | `dd1084b` | ✅ Done |
| 08:44 | store-search | `6e12240` | ✅ Done |
| 08:45 | agent-payments | — | 🟡 Running |
| 08:45 | phase12-frontend | — | 🟡 Running |
| 08:45 | wishlist-retry | — | 🟡 Running |
| 08:45 | order-tracking-retry | — | 🟡 Running |
| 08:46 | agent-ops | — | 🟡 Started |

---

## 📊 Site Health
- Stores: ✅ All 3 live (200 OK)
- Tests: ✅ 101/101 passing
- Deployment: ready

---

_Last updated: 2026-03-29 08:46 GMT+1_

