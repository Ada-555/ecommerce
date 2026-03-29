# Lighthouse QA Results — Orderimo E-Commerce Platform

**Audit Date:** 2026-03-29
**Dev Server:** http://localhost:8023
**Lighthouse Version:** Global npm package

---

## Summary

| Store | Performance | Accessibility | Best Practices | SEO |
|-------|-------------|---------------|----------------|-----|
| **Orderimo** (General) | 25 | 90 | 96 | 100 |
| **Petshop** | 25 | 91 | 96 | 100 |
| **Digital** | 25 | 86 | 96 | 100 |

**Overall Observation:** All three stores share near-identical Lighthouse profiles — they are likely served by a common Django template/asset pipeline. Performance is critically low across the board due to slow server response times and render-blocking resources. Accessibility and SEO are solid on Orderimo and Petshop; Digital has a contrast ratio issue.

---

## Store: Orderimo (General Store)

### Scores
- **Performance:** 25 / 100 ⚠️ CRITICAL
- **Accessibility:** 90 / 100 ✅
- **Best Practices:** 96 / 100 ✅
- **SEO:** 100 / 100 ✅

### Key Metrics
| Metric | Value | Target |
|--------|-------|--------|
| First Contentful Paint (FCP) | 9,198 ms | < 1,800 ms |
| Largest Contentful Paint (LCP) | 9,394 ms | < 2,500 ms |
| Speed Index | 24,604 ms | < 3,400 ms |
| Total Blocking Time (TBT) | 4,730 ms | < 200 ms |
| Max Potential FID | 4,970 ms | < 130 ms |
| Cumulative Layout Shift (CLS) | 0 ms | < 0.1 |
| Server Response Time | 6,270 ms | < 800 ms |

### Top Issues

#### Critical (score = 0)
1. **Server response time is ~6.3 seconds** — This is the #1 bottleneck. The Django dev server is extremely slow to respond.
2. **Excessive render-blocking resources** — CSS/JS files are blocking first paint.
3. **Main-thread work / JavaScript execution** — Heavy JS bundle blocking the main thread.
4. **Buttons lack accessible names** — `<button class="btn btn-outline-secondary btn-sm d-lg-none">` (mobile nav toggle) has no accessible label.
5. **Heading hierarchy violation** — `<h6>` elements are used for visible headings in sequentially-descending order (expecting h1→h2→h3).

### Top 3 Opportunities for Improvement
1. **Reduce server response time** — Switch from Django dev server to a production WSGI server (gunicorn/uvicorn) with caching. Target < 800 ms.
2. **Eliminate render-blocking CSS/JS** — Use `defer`/`async` for JS, inline critical CSS, and lazy-load non-critical stylesheets.
3. **Add accessible names to icon-only buttons** — Add `aria-label="Toggle navigation"` to the mobile nav button.

---

## Store: Petshop

### Scores
- **Performance:** 25 / 100 ⚠️ CRITICAL
- **Accessibility:** 91 / 100 ✅
- **Best Practices:** 96 / 100 ✅
- **SEO:** 100 / 100 ✅

### Key Metrics
| Metric | Value | Target |
|--------|-------|--------|
| First Contentful Paint (FCP) | 9,177 ms | < 1,800 ms |
| Largest Contentful Paint (LCP) | 9,266 ms | < 2,500 ms |
| Speed Index | 24,911 ms | < 3,400 ms |
| Total Blocking Time (TBT) | 5,552 ms | < 200 ms |
| Max Potential FID | 5,730 ms | < 130 ms |
| Cumulative Layout Shift (CLS) | 0 ms | < 0.1 |
| Server Response Time | 6,271 ms | < 800 ms |

### Top Issues

#### Critical (score = 0)
1. **Server response time is ~6.3 seconds** — Same root cause as Orderimo.
2. **Excessive render-blocking resources.**
3. **Main-thread work / JavaScript execution.**
4. **Buttons lack accessible names** — Same mobile nav button issue.
5. **Heading hierarchy violation** — Same h6 issue as Orderimo.

### Top 3 Opportunities for Improvement
1. **Reduce server response time** — Production WSGI server + response caching.
2. **Defer non-critical JavaScript** — Use `defer` attribute on `<script>` tags.
3. **Fix heading hierarchy** — Replace `<h6>` in nav footer with `<h3>` or `<p>` with proper ARIA roles.

---

## Store: Digital

### Scores
- **Performance:** 25 / 100 ⚠️ CRITICAL
- **Accessibility:** 86 / 100 ⚠️ WARNING
- **Best Practices:** 96 / 100 ✅
- **SEO:** 100 / 100 ✅

### Key Metrics
| Metric | Value | Target |
|--------|-------|--------|
| First Contentful Paint (FCP) | 9,554 ms | < 1,800 ms |
| Largest Contentful Paint (LCP) | 9,778 ms | < 2,500 ms |
| Speed Index | 24,821 ms | < 1,800 ms |
| Total Blocking Time (TBT) | 5,332 ms | < 200 ms |
| Max Potential FID | 5,460 ms | < 130 ms |
| Cumulative Layout Shift (CLS) | 0 ms | < 0.1 |
| Server Response Time | 6,262 ms | < 800 ms |

### Top Issues

#### Critical (score = 0)
1. **Server response time is ~6.3 seconds.**
2. **Excessive render-blocking resources.**
3. **Main-thread work / JavaScript execution.**
4. **Color contrast failure** — Some text/background combinations don't meet WCAG AA contrast ratio (4.5:1).
5. **Heading hierarchy violation.**

### Top 3 Opportunities for Improvement
1. **Reduce server response time** — Same recommendation; this is the single highest-impact fix.
2. **Fix color contrast** — Review foreground/background colors in the footer and branding elements.
3. **Add accessible names to icon buttons + fix heading hierarchy.**

---

## Cross-Store Recommendations

### Immediate Fixes
1. **Deploy behind gunicorn** (`gunicorn --workers 4 --bind 0.0.0.0:8023`) to eliminate Django dev server overhead (~6 s → sub-1s response).
2. **Add `aria-label="Toggle navigation"`** to the mobile nav collapse button on all three stores.
3. **Fix heading hierarchy** — audit all footers and replace `<h6>` with `<h3>` or styled `<p>`.

### Short-Term
4. **Defer JavaScript** — add `defer` to all `<script>` tags in `<head>` where possible.
5. **Inline critical CSS** — extract above-the-fold styles and inline them.
6. **Fix color contrast on Digital store** — use `#888` → `#333` or darker in footer.

### Long-Term
7. **Enable static file caching** (WhiteNoise or CDN) for CSS/JS/image assets.
8. **Set up a CDN** (Cloudflare, Fastly) to serve assets from edge locations.
9. **Add `font-display: swap`** for web fonts to prevent font-files from blocking render.

---

## Critical Issues Summary

| Severity | Issue | All Stores? |
|----------|-------|-------------|
| 🔴 CRITICAL | Server response time ~6.3 s | ✅ All 3 |
| 🔴 CRITICAL | Render-blocking CSS/JS | ✅ All 3 |
| 🔴 CRITICAL | Heavy main-thread work | ✅ All 3 |
| 🟡 MEDIUM | Buttons missing accessible names | ✅ All 3 |
| 🟡 MEDIUM | Heading hierarchy violations | ✅ All 3 |
| 🟡 MEDIUM | Reduce unused CSS (50% wasted) | ✅ All 3 |
| 🟠 WARNING | Color contrast failure | Digital only |

*Raw JSON results saved to: `/tmp/orderimo-lighthouse.json`, `/tmp/petshop-lighthouse.json`, `/tmp/digital-lighthouse.json`*
