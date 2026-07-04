---
name: frontend-performance
description: "Use when the app is slow to load or laggy, Core Web Vitals fail (LCP/INP/CLS), before/after adding heavy features, or setting performance budgets — measure on real conditions, spend where the profile says."
---

# Frontend Performance

## Purpose

Make web UIs fast where users actually feel it — load (LCP), interaction (INP), and visual stability (CLS) — by measuring on real conditions first and spending effort where the profile says, not where the folklore points.

## When to use

- Users or metrics say the app is slow to load or laggy to use.
- Core Web Vitals fail thresholds (LCP >2.5 s, INP >200 ms, CLS >0.1 at p75).
- Before/after adding heavy features (editors, charts, big tables, third-party scripts).
- Bundle size or third-party scripts are growing unchecked.
- Setting performance budgets for a team.

## Goals

- p75 field metrics (not your MacBook) pass: LCP <2.5 s, INP <200 ms, CLS <0.1.
- A performance budget exists and CI enforces it (bundle size, LCP on lab runs).
- Every optimization is justified by a profile and verified by re-measurement.
- Perceived performance designed deliberately: skeletons, optimistic UI, transitions.

## Inputs

- Field data: CrUX / RUM percentiles by page and device class — the ground truth.
- Lab reproduction setup: throttled CPU (4×) + network (Fast 3G/slow 4G), mid-tier device profile.
- Bundle analysis output (what's in the JS, per route).
- Waterfall of the critical page (what loads, in what order, what blocks).
- The product's tolerance: which interactions are hot paths, which pages are landing surfaces.

## Outputs

- Ranked findings: metric affected → cause → estimated win → fix.
- Fixes with before/after measurements at p75-representative conditions.
- Performance budget (per-route JS size, LCP target, INP target) wired into CI.
- Regression guardrails: RUM dashboards + alerts on p75 degradation.

## Expert Mental Model

- **Your machine is a lie.** M-series laptop on fiber is 5–20× the median user's phone. Experts profile with 4–6× CPU throttle and 3G/4G network, and trust field percentiles (p75, not median) over any lab number. The gap between lab and field is itself diagnostic (caching, device mix, geography).
- **The three metrics map to three different physics**: LCP is a network/waterfall problem (bytes, order, priorities), INP is a main-thread problem (long tasks, JS volume, render cost), CLS is a layout-contract problem (reserved space). A fix for one rarely fixes another; diagnose which one you actually have before touching anything.
- **JavaScript is the most expensive byte.** 200 KB of JS costs far more than 200 KB of image: download + parse + compile + execute + retained memory, all on the main thread that also handles taps. Bundle analysis comes before image optimization in any JS-framework app — but images dominate LCP on content pages. Know which app you have.
- **The fastest work is the work not done**: not shipped (code-split, tree-shake), not run yet (defer, lazy), not run again (memoize, cache), not on this thread (worker), not visible so skip it (virtualize). Experts walk this ladder before optimizing any specific function.
- **Waterfalls are where load time hides.** Sequential dependency chains — HTML → JS → data fetch → render → image discovered late — each hop adds a round trip. Flattening the chain (preload, server-render with data, early hints) beats shrinking any single step.
- **Perceived ≠ actual.** A 3 s load that paints a correct skeleton at 300 ms and streams in feels faster than a 2 s blank-then-pop. After real wins, spend on perception: stable layout, immediate input echo, optimistic transitions.

## Workflow

1. **Get field truth**: RUM/CrUX p75 per key page × device class. Pick the one worst (metric, page) pair as the target. No field data? Instrument first (web-vitals library → analytics), fix later.
2. **Reproduce in lab** at throttled conditions until the lab number is within ~20% of field p75 — now your iterations are trustworthy.
3. **Diagnose by metric**:
   - LCP: identify the LCP element (usually hero image or headline) → walk its dependency chain in the waterfall. Late-discovered image? Render-blocking CSS/JS? Server slow (TTFB >800 ms)? Font swap repainting the headline?
   - INP: Performance panel → find long tasks (>50 ms) near interactions → attribute (framework re-render? third-party? synchronous layout thrash — read-write-read of layout props?).
   - CLS: Layout Shift regions → find the mover (image without dimensions, injected banner, font swap, ad slot).
4. **Fix in impact order** (see Decision Tree), one change at a time, re-measuring after each — multiple simultaneous changes hide which one regressed you.
5. **For LCP**: server-render the shell; `preload` the LCP image / set `fetchpriority="high"`; never lazy-load above-the-fold images; inline critical CSS; kill render-blocking third-party JS from `<head>` (async/defer/move); TTFB — cache HTML at CDN if content allows.
6. **For INP**: code-split routes and heavy components (`import()` on demand); defer non-visible work (`requestIdleCallback`, after-interaction); chunk long loops (`scheduler.yield`/setTimeout batching); virtualize lists >~200 complex rows; fix re-render storms (state colocation, memo boundaries — measured via React/Vue profiler); move pure computation to workers only past ~50 ms chunks.
7. **For CLS**: width/height (or aspect-ratio) on ALL media; reserve slots for async content (min-height skeletons); `font-display: swap` + size-adjusted fallback metrics; never insert content above existing content post-load (banners animate in from a reserved slot or push nothing).
8. **Attack the bundle**: analyzer → top 10 modules → for each: needed at all? needed on this route? needed at boot? lighter alternative (date lib → native Intl; lodash → es-toolkit/native)? duplicate versions? Polyfills for browsers you don't support?
9. **Fonts**: subset (unicode-range), woff2 only, preload the 1–2 critical faces, max ~2 families × 2–3 weights, `font-display: swap` with fallback tuned via `size-adjust` to kill both invisible text and swap-shift.
10. **Lock it in**: size-limit/bundle budget in CI (fail PR on +10% route JS), Lighthouse CI on key pages, RUM alert on p75 regression week-over-week, and a third-party script review gate (each tag names an owner and a byte cost).

## Decision Tree

- If p75 LCP >2.5 s:
  - If TTFB >800 ms → server/CDN problem first (cache HTML, move compute post-response, edge-render); client tweaks can't save a slow origin.
  - Else if LCP element is an image discovered late → preload + `fetchpriority="high"` + remove lazy-loading on it + responsive `srcset` sized to layout.
  - Else if render-blocked → inline critical CSS, defer JS, async third parties.
  - Else (client-rendered shell waits for JS+data) → SSR/streaming or at minimum a meaningful static shell.
- If p75 INP >200 ms:
  - If long tasks at startup overlap first interactions → ship less JS (split, defer hydration/islands).
  - Else if interaction handlers themselves are slow → profile the handler: framework re-render blast (fix state placement/memo) vs synchronous layout thrash (batch reads/writes) vs heavy compute (chunk or worker).
  - Else if third-party (tag managers, chat widgets) owns the long tasks → defer them post-interaction/idle, or remove (bring the byte-cost receipt to the meeting).
- If CLS >0.1 → find movers in order of shift score: media without dimensions → reserved-space fix; font swap → metric-tuned fallback; injected UI → reserve or relocate.
- If everything passes but users still say "feels slow" → it's perceived performance: skeleton accuracy, input echo <100 ms, optimistic updates, view transitions; also check p95 — pain may live past p75.

## Heuristics

- Budget anchors (mid-tier mobile): ≤200 KB compressed JS per route is comfortable, 350 KB is the warning track, 500 KB+ will fail INP for real users. Landing/content pages should be far below app-shell numbers.
- 100 ms is the threshold of "instant" for input echo; 50 ms per task is the long-task line; one frame is 16.7 ms — a handler doing 200 ms of sync work eats 12 frames of tap feedback.
- Images: correct-size responsive images typically cut 50–80% of image bytes; AVIF/WebP another 20–40%. But image bytes off the main thread ≠ JS bytes on it — never trade "smaller images" for "skip the bundle work" on an app.
- Preload is a scalpel, not a shotgun: >3–4 preloads and you've just reordered the congestion.
- `content-visibility: auto` on long below-fold sections is a one-line render-cost win.
- Third-party rule: every marketing tag is a perf regression with a business justification attached — make the byte/ms cost visible per tag, review quarterly, load none of them before first paint.
- Memoize at boundaries, not everywhere: blanket `memo`/`useMemo` adds comparison cost and hides the real problem (state placement).
- Animate only `transform` and `opacity`; anything animating layout properties (top/left/width/height) janks on principle.
- The double-keyed cache reality: cross-site "CDN font/library is probably cached" hasn't been true for years; self-host.
- Measure the 90th-percentile row, not the demo data: tables/charts built on 10-row fixtures meet their real data in production.
- A perf PR without before/after numbers at stated throttle conditions is a vibes PR.

## Quality Checklist

- [ ] Field p75 by page/device known; target (metric, page) chosen from data.
- [ ] Lab setup reproduces field within ~20%; all measurements at declared throttle.
- [ ] LCP element identified; its full dependency chain walked and shortened; no lazy-load above fold; hero preloaded.
- [ ] All media carries dimensions/aspect-ratio; async slots reserved; fonts swap with tuned fallbacks.
- [ ] Route-level code splitting; bundle top-10 audited with named outcomes; no duplicate libraries.
- [ ] Long tasks near interactions attributed and fixed/chunked; lists virtualized past threshold.
- [ ] Third-party scripts inventoried with owners and costs; none render-blocking.
- [ ] Budgets in CI (JS size + Lighthouse); RUM regression alerts live.
- [ ] Each fix has before/after numbers; regressions bisectable (one change per measurement).
- [ ] Perceived-performance pass done: skeletons match layout, input echo immediate, transitions cover latency.

## Failure Modes

- **Optimizing on a MacBook**: shipped "fast" app fails p75 phones; the entire effort mis-targeted because the profile was fiction.
- **Cargo-cult memoization**: hundreds of `useMemo`s while a context re-renders the world per keystroke; the profiler was never opened.
- **Lazy-loading the LCP image**: the single most common self-inflicted LCP wound — `loading="lazy"` copy-pasted onto the hero.
- **The tag-manager tumor**: 30 marketing scripts, 900 KB, injected pre-paint, nobody owns any of them. Perf work elsewhere is rounding error until this is governed.
- **Spinner→layout pop**: skeleton-less loading that shifts everything on arrival — CLS *and* perceived jank; skeletons that don't match final layout do the same.
- **Optimizing the wrong metric**: shaving 40 KB of images to fix an INP problem, or memoizing renders to fix a TTFB problem. Metric→physics mapping skipped.
- **One-time heroics, no guardrails**: quarterly perf sprint fixes it; three months of unreviewed PRs regress it; repeat. Budgets in CI are the exit from this loop.
- **Waterfall blindness**: every asset optimized, still slow — because render waits on a 4-hop sequential chain nobody drew.

## Edge Cases

- **Hydration uncanny valley**: SSR paints fast, but JS hasn't hydrated — buttons visible and dead. Prioritize hydrating interactive-above-fold (islands/progressive hydration), or at minimum queue clicks.
- **Font metric shift**: swap from fallback to webfont reflows the headline → CLS despite "everything reserved." Fix with `size-adjust`/`ascent-override` on the fallback.
- **Back/forward cache (bfcache) breakage**: `unload` handlers or open connections disable the instant back-navigation — audit; bfcache is the cheapest "instant" you'll ever get.
- **Memory as the hidden perf killer**: long-session SPAs leak → GC pauses grow → INP degrades over hours. Profile a 2-hour session, not a fresh load.
- **Low-end thermal throttling**: sustained JS (animations, polling) heats phones → CPU clocks drop → everything slows. Sustained load matters, not just peaks.
- **Analytics double-counting SPAs**: route changes measured as "page loads" corrupt your RUM — soft-nav metrics need explicit instrumentation.
- **Third-party CSS**: a chat widget's stylesheet can be render-blocking; scripts aren't the only third-party surface.
- **Prefetch vs data caps**: aggressive prefetching on metered mobile connections is hostile; respect `Save-Data`/connection hints.

## Tradeoffs

- **SSR/streaming vs client-render**: SSR buys LCP and works-without-JS at the cost of server infra, hydration complexity, and per-request compute; pure CSR is operationally simple and fine behind login where SEO/first-paint matter less. Streaming SSR + islands is the current sweet spot for content+app hybrids — when the framework supports it well.
- **Code-splitting granularity**: more chunks = less unused JS but more request overhead and waterfall risk (lazy chunk needing lazy chunk). Split by route always; split components only when heavy (>30–50 KB) or rarely shown (modals, editors).
- **Optimistic UI vs correctness feel**: instant echo that occasionally rolls back vs honest waiting — optimistic for reversible high-success ops; never for money movement.
- **Cache aggressiveness vs freshness**: immutable-hashed assets forever-cached is free win; HTML caching trades staleness windows for TTFB — needs a revalidation story.
- **Perf vs developer velocity**: budgets add PR friction; no budgets adds user friction. Budget hot paths strictly (landing, checkout), loosen internal admin surfaces — uniform strictness burns the political capital perf work needs.

## Optimization Strategies

- Re-rank quarterly by (traffic × metric gap): the worst page users actually visit beats the worst page absolutely.
- Kill dependency chains at the source: co-locate data with render (loader patterns / RSC-style), emit `103 Early Hints`/preloads for the known-critical path.
- Adopt native lazies before libraries: `loading="lazy"` (below fold), `decoding="async"`, `content-visibility`, `IntersectionObserver`.
- Speculative loading on intent: prefetch route chunks + data on link hover/viewport-entry — 100–300 ms head start feels like teleportation.
- Delete before you optimize: unused features, A/B test corpses, duplicate libs, dead polyfills; deletion has no maintenance cost.
- Run a monthly "slowest interaction" review from RUM INP attribution — one fixed interaction/month compounds into a different product by year-end.

## Self Review

- Am I fixing the metric the field data indicts, on the page users hit, at conditions matching p75?
- Can I draw the LCP element's dependency chain from memory? Where's the longest hop?
- What's in my top-10 bundle modules, and can I defend each one's presence at boot?
- Did each change get its own before/after at declared throttle? Would I bet on the delta replicating in field data?
- What regresses this next quarter, and what alarm fires when it does?
- Have I watched the page load on a real mid-tier phone — not DevTools emulation — at least once?

## Examples

**1. LCP triage on a landing page.**
Field: LCP p75 = 4.1 s mobile. Waterfall shows: HTML (600 ms TTFB) → CSS → JS bundle → React renders → hero image *discovered* → downloads. Chain fixes: hero to `<img fetchpriority="high">` in SSR HTML with preload (discovery moved from 2.8 s to 0.7 s), `loading="lazy"` removed from it (was copy-pasted), critical CSS inlined, marketing tags moved post-onload, HTML edge-cached (TTFB 600→180 ms). Result: 4.1 → 1.9 s. No image was compressed and no component memoized — the problem was the chain.

**2. INP hunt in a dashboard.**
Field INP p75 = 460 ms, attributed to a filter dropdown. Profile at 4× throttle: 380 ms long task on selection — flame graph shows the entire 800-row table re-rendering unmemoized, each row computing a date format. Fixes: table rows memoized on stable props, `Intl.DateTimeFormat` instance hoisted (was constructed 800×), list virtualized (23 visible rows), filter state moved from page-level context into the table container. Interaction task: 380 → 40 ms. Each fix measured solo; virtualization was the biggest single win (−210 ms).

**3. CLS from fonts, the sneaky version.**
CLS 0.18 with all images sized. Layout Shift regions point at the headline: brand font loads → metrics differ from fallback → two-line headline becomes three. Fix: `font-display: swap` retained, plus `@font-face` fallback override (`size-adjust: 97%; ascent-override: 92%`) tuned until swap is visually motionless; preload the one critical woff2 subset. CLS → 0.02. Total code: ~10 lines of CSS.

**4. Bundle governance installed.**
Route JS crept to 710 KB. Analyzer findings: moment+locales (68 KB) → `Intl` + date-fns/esm on the two call sites; three chart libs from acquisitions → standardized on one; `lodash` full import → per-method; dev-only error overlay shipped to prod → env-gated; duplicate React from a mislinked package → dedupe. 710 → 260 KB. Then the lock-in: `size-limit` per route in CI at current+10%, bundle-diff comment on every PR, and a quarterly third-party review with per-tag costs — eighteen months later it's still 260–290 KB.

## Evaluation Rubric

Score 1–10:

- **1–2**: No measurement; optimizations by folklore (memo confetti, image tinkering for a JS problem); dev-machine-only testing; no budgets.
- **3–4**: Lighthouse run occasionally on desktop; some code-splitting; fixes unverified by re-measurement; third parties ungoverned; CLS/fonts unhandled.
- **5–6**: Field data consulted; correct metric→cause mapping on main issues; throttled lab reproduction; before/after numbers; media dimensioned; route splitting done.
- **7–8**: Full checklist: budgets enforced in CI, RUM alerts, third-party inventory with owners, waterfall-chain fixes, virtualization where warranted, perceived-perf pass complete.
- **9–10**: Additionally: p95 and long-session behavior examined (memory, thermal); bfcache/soft-nav instrumentation correct; speculative loading on intent; a quarterly data-ranked perf process exists; every claim in the perf doc reproduces from the attached traces.
