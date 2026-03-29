# Plurino / Orderimo — Build Task Dashboard

## 🚦 Status (2026-03-29 09:50 GMT+1)

- **Tests:** ✅ 112/112 passing
- **Stores:** ✅ All 3 live (200 OK)
- **Build:** ✅ Production-ready core features complete

---

## ✅ Completed Features

| Feature | Commit | Notes |
|---------|--------|-------|
| Store-scoped search | `6e12240` | /orderimo/search/, /petshop/search/, /digital/search/ |
| Email notifications | `5a07479` | 1,851 lines — confirmation, shipped, delivered, welcome |
| Order tracking page | `dd6886b` | tracking/<order_number>/, status fields, email integration |
| Wishlist (heart icon) | `5bfc59a` | HTMX toggle, per-store |
| Crypto payments | `dd1084b` | BTC/USDC via Stripe, XMR via CoinGate |
| Phase 12 Reviews | `2d8192b` | Frontend: star ratings, verified buyer badge, submission form |
| Multi-currency | `35bc9fe` | EUR/USD/GBP selector with Frankfurter API |
| Affiliate program | `a504dbf` | Referral tracking, commissions, dashboard |
| Stub invoices app | — | download_invoice placeholder (needs full implementation) |
| Stabilization | `5ad684e` | Set currency view, URL fixes, app disable for incomplete features |

---

## 🟡 In Progress / TBD

| Feature | Status | Next step |
|---------|--------|-----------|
| Multi-coupon system | Partially coded (coupons app exists, not integrated) | Integrate into checkout UI |
| Subscription products | Model exists, not integrated | Add subscription checkout flow |
| Newsletter signup | Newsletter app exists | Configure Mailchimp, add footer form |
| Abandoned cart emails | Signal design only | Implement management command + cron |
| PDF invoices | Stub view only | Build ReportLab PDF generation |
| Product comparisons | Comparison app exists | Build compare page (+ add compare buttons) |
| GA4 dashboard | Analytics app partial | Finish dashboard template, add to admin |

---

## 🧠 Notes

- **Option B partitions** — 6 dedicated agents ran in parallel without file conflicts
- **Max API burn** — used all available capacity
- **Test baseline** — currently 112/112 passing on stabilized HEAD
- **Uncommitted work:** None (all agent work either committed or stashed/stabilized)

---

## 📦 Next Steps (if continuing)

1. **Implement checkout integration for coupons**
2. **Add subscription mode to checkout**
3. **Finish newsletter footer form + Mailchimp settings**
4. **Implement abandoned cart email management command**
5. **Build PDF invoice generation**
6. **Create comparison page template & add compare buttons**
7. **Complete GA4 analytics admin page**

---

_Last updated: 2026-03-29 09:50 GMT+1_
