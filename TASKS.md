# Plurino / Orderimo — Build Task Dashboard

## 🚦 Status Legend
- ✅ **DONE** — completed and merged
- 🟡 **IN PROGRESS** — actively being built
- ⏳ **QUEUED** — next to spawn
- 🔜 **SOON** — planned

---

## ✅ Completed This Session

| Task | Commit | Lines |
|------|--------|-------|
| Store-scoped search | `6e12240` | — |
| Email notifications (full) | `5a07479` | 1,851 |
| Order tracking (full) | `5a07479` | (with email) |
| Crypto payments (BTC/USDC/XMR) | `dd1084b` | — |

---

## 🟡 In Progress (Partitioned by Directory)

| # | Task | Agent | Owns | Status |
|---|------|-------|------|--------|
| 1 | Wishlist — heart icon, save for later | wishlist-retry | `wishlist/` | 🟡 Running |
| 2 | Phase 12 Reviews — templates, star rating, verified buyer | phase12-frontend | `products/templates/` | 🟡 Running |
| 3 | Multi-coupon + Subscriptions | agent-payments | `coupons/`, `subscriptions/` | 🟡 Running |
| 4 | Order Tracking — verify + finish | order-tracking-retry | `tracking/` | 🟡 Running |

---

## ⏳ Queued (spawn as slots free)

| # | Task | Agent | Owns |
|---|------|-------|------|
| 5 | Product Comparisons + GA4 Dashboard | agent-seo | `comparison/`, `analytics/` |
| 6 | Newsletter (Mailchimp) + Abandoned Cart Emails | agent-ops | `notifications/`, emails |
| 7 | PDF Invoices | agent-ops | new `invoices/` |
| 8 | Multi-Currency (EUR/USD/GBP) | next-free | settings + templates |
| 9 | Affiliate Program | next-free | `affiliates/` |

---

## 🔜 Soon (not started)

| # | Task |
|---|------|
| 10 | GA4 External API (optional, on top of ORM dashboard) |
| 11 | Stripe Customer Portal for subscriptions |
| 12 | Multi-currency price conversion |

---

## 📋 Agent Log

| Time | Agent | Action |
|------|-------|--------|
| 08:44 | email-notifications | ✅ Committed 1,851 lines — full email system |
| 08:44 | crypto-payments | ✅ Committed — BTC/USDC via Stripe, XMR via CoinGate |
| 08:44 | store-search | ✅ Committed — store-scoped search |
| 08:44 | orderimo-phase12-reviews | ❌ KILLED — stuck in git loop 2.5h |
| 08:44 | phase12-frontend | 🟡 Running — templates only |
| 08:44 | agent-payments | 🟡 Started — coupons + subscriptions |
| 08:45 | wishlist-retry | 🟡 Running — wishlist app |
| 08:45 | order-tracking-retry | 🟡 Running — tracking app |

---

## 📊 Site Health
- All 3 stores: ✅ 200 OK
- Tests: ✅ 101/101 passing

---

_Last updated: 2026-03-29 08:45 GMT+1_
