# Plurino / Orderimo — Build Task Dashboard

## 🚦 Status (2026-03-29 09:55 GMT+1)

- **Tests:** ✅ 112/112 passing
- **Stores:** ✅ Orderimo, PetShop Ireland, DigitalHub (200 OK)
- **Core Build:** ✅ Complete (see completed list)

---

## ✅ Completed Features

| Feature | Commit |
|---------|--------|
| Store-scoped search | `6e12240` |
| Email notifications | `5a07479` |
| Order tracking page | `dd6886b` |
| Wishlist (heart icon) | `5bfc59a` |
| Crypto payments | `dd1084b` |
| Phase 12 Reviews (frontend) | `2d8192b` |
| Multi-currency (EUR/USD/GBP) | `35bc9fe` |
| Affiliate program | `a504dbf` |
| Newsletter signup with Mailchimp | `236b781` |
| Stabilization (set_currency, URL fixes) | `5ad684e` |

---

## 🟡 Final Sprint — In Progress (now)

| Agent | Task | Status |
|-------|------|--------|
| agent-coupon-ui | Integrate multi-coupon into checkout UI (apply button, discount line) | 🟡 Running |
| agent-subscriptions-checkout | Subscription checkout flow (Stripe mode='subscription') | 🟡 Running |
| agent-abandoned-cart | Management command for abandoned cart emails | 🟟 Running |
| agent-invoices-finish | PDF invoice generation with ReportLab | 🟡 Running |

---

## 🔜 Scoped but not started (can do any time)

| Feature | Notes |
|---------|-------|
| Product comparisons | templates/comparison/compare.html + compare buttons in product cards |
| GA4 analytics dashboard | Admin analytics page template already created |
| Multi-coupon backend | Model exists, needs checkout integration (in progress above) |
| Subscription admin UI | Show in admin, subscription management page (in progress) |
| Final deployment checklist | DEPLOYMENT.md, .env.example, production settings |

---

_Last updated: 2026-03-29 09:55 GMT+1_
