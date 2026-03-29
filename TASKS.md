# Plurino / Orderimo — Build Task Dashboard

## 🚦 Status Legend
- 🟡 **IN PROGRESS** — actively being built
- ✅ **DONE** — completed and merged
- ⏳ **NEXT** — queued up
- 🔜 **SOON** — planned

---

## 🔧 Fixes & Polish (This Week)

| # | Task | Status | Agent | Notes |
|---|------|--------|-------|-------|
| 1 | Per-store admin | ✅ DONE | per-store-admin | Store-scoped admin views |
| 2 | Phase 12 Reviews — star ratings, moderation, verified buyer | 🟡 IN PROGRESS | orderimo-phase12-reviews | Running 2h+, deep in implementation |
| 3 | Order tracking page — trackable link after purchase | 🟡 IN PROGRESS | order-tracking-retry | Respawning with 30m timeout |
| 4 | Email notifications — confirmation, shipping, delivery | 🟡 IN PROGRESS | email-notifications-retry | Respawning with 30m timeout |
| 5 | Wishlist / Save for later — heart icon | 🟡 IN PROGRESS | wishlist-retry | Respawning with 30m timeout |
| 6 | Store-specific search — scoped to active store | ✅ DONE | store-search | Search per store (orderimo/petshop/digital/search/) |

---

## 🚀 Features (This Month)

| # | Task | Status | Agent | Notes |
|---|------|--------|-------|-------|
| 7 | Product comparisons — side-by-side 2-3 products | ⏳ NEXT | — | |
| 8 | Abandoned cart emails | ⏳ NEXT | — | |
| 9 | Multi-coupon system — credits, % off, free shipping | ⏳ NEXT | — | |
| 10 | PDF invoices — auto-generation per order | ⏳ NEXT | — | |

---

## 💰 Revenue Features

| # | Task | Status | Agent | Notes |
|---|------|--------|-------|-------|
| 11 | **Crypto payments — BTC, USDC, XMR via Stripe** | 🟡 IN PROGRESS | crypto-payments | Kay's priority — launched 08:17 |
| 12 | Newsletter signup — Mailchimp or equivalent | ⏳ NEXT | — | |
| 13 | Subscription products — recurring billing | 🔜 SOON | — | |
| 14 | GA4 analytics dashboard — revenue, conversions, top products | 🔜 SOON | — | |
| 15 | Affiliate program — per-store affiliate links | 🔜 SOON | — | |
| 16 | Multi-currency — EUR, USD, GBP | 🔜 SOON | — | |

---

## 📋 Agent Log

| Timestamp | Agent | Action | Status |
|-----------|-------|--------|--------|
| 2026-03-29 07:00 | per-store-admin | Committed store-scoped admin | ✅ Done |
| 2026-03-29 07:46 | qa-test-sweep | Fixed profile URL, bag URL param, all 101 tests pass | ✅ Done |
| 2026-03-29 08:16 | store-search | Added store-scoped search URLs & templates | ✅ Done |
| 2026-03-29 08:00 | order-tracking, email, wishlist | Initial runs timed out (10m) | ⚠️ Timeout |
| 2026-03-29 08:18 | order-tracking-retry, email-notifications-retry, wishlist-retry | Respawning with 30min timeouts — resuming from partial work | 🟡 Running |
| 2026-03-29 08:19 | crypto-payments | Starting crypto payments (BTC, USDC, XMR) | 🟩 Started |

---

## 📊 Site Health
- All 3 stores: ✅ 200 OK on all pages
- Tests: ✅ 101/101 passing
- Django check: ✅ passing

---

_Last updated: 2026-03-29 08:19 GMT+1_

