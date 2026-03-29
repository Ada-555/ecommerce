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
| Email notifications (full) | `5a07479` | ✅ 1,851 lines — order confirmation/shipped/delivered, welcome |
| Order tracking page (full) | `dd6886b` | ✅ tracking/<int:order_number>/, status fields, success page |
| Wishlist / Save for later | `5bfc59a` | ✅ model, views, HTMX toggle, per-store |
| Crypto payments (BTC/USDC/XMR) | `dd1084b` | ✅ Stripe crypto + CoinGate for XMR |

---

## 🟡 Active — Partitioned by Directory

| Agent | Owns | Features |
|-------|------|----------|
| **phase12-frontend** | `products/templates/` | Review display, submit form, verified buyer badge |
| **agent-payments** | `coupons/`, `subscriptions/` | Multi-coupon + Stripe subscriptions |
| **agent-ops** | `newsletter/`, `invoices/` | Newsletter (Mailchimp), abandoned cart, PDF invoices |
| ~~**wishlist-retry**~~ | ~~`wishlist/`~~ | ✅ Done |
| **order-tracking-retry** | `tracking/` | Tracking page, order status view |

---

## ⏳ Queued (as slots free)

| # | Agent | Owns | Features |
|---|-------|------|----------|
| 6 | agent-seo | `comparison/`, `analytics/` | Product comparisons, GA4 dashboard |
| 7 | agent-currencies | `settings.py`, templates | Multi-currency (EUR/USD/GBP) |
| 8 | agent-affiliate | `affiliates/` | Affiliate program with referral tracking |
| 9 | agent-final | misc | Final polish, docs, deployment checks |

---

## 📋 Agent Log

| Time | Agent | Status |
|------|-------|--------|
| 08:44 | email-notifications | ✅ Done (1,851 lines) |
| 08:44 | crypto-payments | ✅ Done |
| 08:45 | wishlist-retry | ✅ Done (HTMX toggle) |
| 08:45 | order-tracking-retry | ✅ Done (tracking page + status) |
| 08:46 | agent-ops | 🟡 Running |
| 08:46 | agent-payments | 🟡 Running |
| 08:46 | phase12-frontend | 🟡 Running |

---

## 📊 Site Health
- Stores: ✅ All 3 live (200 OK)
- Tests: ✅ 101/101 passing
- Deployment: ready

---

_Last updated: 2026-03-29 08:50 GMT+1_

