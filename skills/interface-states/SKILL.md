---
name: interface-states
description: "Use when building any view that fetches or waits, designs only show the ideal populated state, error handling is inconsistent, or the app 'feels broken' during loads/failures — loading, empty, error, skeletons, toasts."
---

# Interface States: Empty, Loading, Error & Partial

## Purpose

Design the non-ideal 80% of an interface's life — empty states, loading states, errors, partial failures, offline — so users always know what's happening, whether their data is safe, and what to do next.

## When to use

- Building any view that fetches, computes, or waits on anything.
- Reviewing designs that only show the ideal, fully-populated state.
- Error handling is inconsistent: raw error codes, dead-end alerts, silent failures.
- Users report the app "feels broken/janky" during loads or after failures.
- Defining design-system patterns for skeletons, spinners, toasts, and error surfaces.

## Goals

- Every view has all five states designed: empty, loading, error, partial, ideal.
- Wait feedback matches wait length (nothing → skeleton → progress → async).
- Every error answers three questions: what happened, is my data safe, what do I do now.
- Empty states convert dead ends into starting points.

## Inputs

- The view inventory and, per view: data sources, realistic latency distribution (p50/p95), failure modes of each source.
- What "empty" means per surface: brand-new user? cleared inbox? filtered-to-nothing? no results?
- Which operations are retryable, which mutate state (retry-safety), which degrade partially.
- Latency budget and honesty constraints (can you show progress truthfully?).

## Outputs

- A state matrix: view × {empty, loading, error, partial, ideal} with a design or explicit pattern reference per cell.
- Error copy per failure class following the three-questions template.
- Loading pattern rules (thresholds, skeleton specs) and retry semantics wired to actually work.

## Expert Mental Model

- **The ideal state is a special case.** Users meet your product loading (every session), empty (first run), erroring (inevitably), and partial (any multi-source screen). Experts design the state matrix as the deliverable; the populated happy screen is one row of it. Teams that design only the ideal state ship the other states by accident — as blank divs, spinner purgatory, and `[object Object]`.
- **Loading feedback is a ladder keyed to duration**: under ~100 ms — show nothing (a flash of spinner is worse than nothing); 100 ms–1 s — lightweight indicator or skeleton; 1–10 s — skeleton/progress with real structure; beyond ~10 s — determinate progress + cancel, or convert to async job with notification ("we'll email you"). The wrong rung reads as broken: an instant spinner-flash feels janky, a 20-second spinner feels crashed.
- **Skeletons are a layout contract.** They work by promising the shape of what's coming — so they must match the real layout (same heights, same regions), or the swap-in shift is worse than a spinner. Skeleton ≠ decoration; it's CLS prevention plus perceived speed.
- **Errors are a conversation at the worst moment.** The user is already frustrated; the error surface must answer, in order: (1) what happened, in human terms; (2) is my stuff safe ("your draft is saved"); (3) what do I do now (retry that actually retries, or a concrete alternative). Blame the system, never the user; skip the apology theater; include the request-ID for support.
- **Partial failure beats total failure.** On multi-source screens (dashboards, feeds), one dead widget must not blank the page — degrade per region with per-region retry. The blast radius of an error is a design decision, made by where you place error boundaries.
- **Empty is either a dead end or an invitation.** Four different empties demand different designs: first-use (teach + primary action), user-cleared (celebrate — inbox zero is an achievement, not an absence), no-results (show the escape: clear filters, fix typo), and error-empty (that's an error state, don't dress it as empty — "no results" when the search service is down is a lie that costs trust).

## Workflow

1. **Build the state matrix**: rows = views/regions, columns = the five states. Fill every cell with a design or a named pattern. Empty cells are future bugs.
2. **Get real latency numbers** (p50/p95 per data source) — the loading design follows the distribution, not the demo环境. A p95 of 4 s needs skeleton+progress; designing for the 200 ms p50 alone ships spinner purgatory for the tail.
3. **Apply the loading ladder** per region: delay indicators ~100–150 ms before showing (debounce the flash); skeletons for structured content, spinners only for small/unknown-shape regions; one loading treatment per view level (screen vs region vs inline-button) — never three spinners stacked.
4. **Differentiate the four empties** per view and design each: first-use empties get: what this is (one line), why it matters (one line), one primary action, optionally an illustration that doesn't outweigh the action. No-results empties get the query echoed + one-click filter reset.
5. **Classify failures and write the copy**: per failure class (network, validation, permission, server, timeout, conflict) apply the three-questions template; map codes → human copy centrally (no raw `ECONNRESET` reaching pixels); attach request-ID discreetly.
6. **Wire retry semantics honestly**: retry buttons re-invoke the actual operation (not `location.reload()` unless that's truly it); disable-while-retrying; exponential backoff for auto-retries with a visible "retrying… (2/3)"; mutation retries must be idempotent-safe (pair with idempotency keys) or become "try again" ambushes that double-charge.
7. **Place error boundaries deliberately**: per widget/region on composite screens; per route elsewhere; global boundary as last resort with a real recovery page (nav intact, state preserved where possible), never a white screen.
8. **Design the transitions**: loading→ideal without layout shift (skeleton contract), loading→error in place (same region), stale→fresh with subtle refresh indication (stale-while-revalidate surfaces: show the old data + a quiet updating cue rather than blanking to skeleton on every refetch).
9. **Handle offline/degraded** as first-class where relevant: detect, banner quietly, queue what's queueable, mark what's stale; on reconnect, sync and confirm.
10. **Test by sabotage**: throttle to 3G, kill endpoints one at a time (each source!), return 500s/403s/empty arrays, mid-flight cancel — walk the matrix cell by cell in a staging environment. If you haven't seen it, you haven't designed it.

## Decision Tree

- If wait <100 ms expected → no indicator; if occasionally slower → indicator delayed 150 ms so fast paths never flash.
- Else if shape of incoming content is known → skeleton matching final layout (2–3 pulse cycles max before it starts feeling stuck — if p95 exceeds ~5 s, add progress text).
- Else if shape unknown / action-inline → spinner (sized to context) or button busy-state.
- Else if >10 s or unpredictable → determinate progress if honest, else staged status text ("Analyzing 3 of 7 files…"); offer cancel; consider async conversion with notify-on-done.
- If the operation was user-initiated and blocking (save, submit) → busy state on the trigger + optimistic UI only where rollback is designed (see state-management skill).

On failure:
- If input problem (4xx validation) → inline at the field/object, specific fix instructions (see forms skill); never a toast for something with a location.
- Else if permission (403) → explain the boundary + who to ask / how to request access; don't retry-bait.
- Else if transient (network, 5xx, timeout) → in-place error with retry; auto-retry once or twice with backoff before even bothering the user, then manual.
- Else if conflict (409, stale edit) → show both versions or the diff; offer merge/overwrite/copy — never silent last-write-wins.
- Else if partial (some sources failed) → render successes, error the failed regions with per-region retry; add a quiet page-level note only if >half failed.
- If the failure destroyed nothing but looks like it did → say so explicitly ("Your changes are saved; we just couldn't refresh the preview").

Empty classification:
- New user, feature unused → first-use empty (teach + act).
- Had content, cleared it → completion state (celebrate + what's next).
- Filter/search excludes everything → no-results (echo query, offer reset/suggestions).
- Upstream failed → error state, honestly labeled — never masquerading as "nothing here."

## Heuristics

- One skeleton per screen region hierarchy: screen-level skeleton OR region skeletons, not nested Russian dolls of pulse.
- Skeleton pulse: slow (1.5–2 s cycle), subtle (4–8% lightness delta); fast bright pulsing communicates anxiety.
- Never blank existing content to show a loader for its refresh — stale-while-revalidate presentation: keep content, add a quiet indicator, swap seamlessly.
- Toasts are for confirmations and non-blocking notices, never for errors that need action — toasts auto-dismiss, and the error's context evaporates with them. Errors live where the problem lives.
- Error copy formula: [what happened] + [data safety] + [next step], ≤2 sentences + a button. "Couldn't save your changes — they're kept locally. Retry now or we'll auto-retry in 10 s."
- Ban the words: "Oops!", "Something went wrong" (alone), "Error 500". The first is tone-deaf at scale, the second is content-free, the third is for the request-ID line.
- Retry buttons that might have side effects must be labeled by their operation ("Resend invite"), not generic "Try again" — the user needs to know what's being repeated.
- Auto-refresh/auto-retry loops need caps and visibility; infinitely spinning silent retries drain batteries and hide outages.
- Empty-state illustrations: smaller than the action, on-language, never so charming they outshine broken functionality elsewhere.
- Cancel must actually cancel (abort the request, stop the job) — a cancel that merely hides the spinner leaves ghosts that surprise later.
- Track state-frequency in analytics: how often users see each error and empty state. The most-seen error screen deserves design attention proportional to a top feature.

## Quality Checklist

- [ ] State matrix complete: every view × five states designed or pattern-referenced.
- [ ] Loading ladder applied against measured p50/p95, indicator-flash debounced.
- [ ] Skeletons match final layout; swap-in shift ≈ 0.
- [ ] The four empty types distinguished per view; every empty has one primary action or honest explanation.
- [ ] Error copy passes three-questions on every failure class; codes mapped centrally; request-ID present.
- [ ] Retries re-invoke the real operation, are idempotency-safe for mutations, and show retry state.
- [ ] Composite screens degrade per-region; boundary placement documented.
- [ ] Refetches never blank existing content.
- [ ] Offline/reconnect behavior defined where relevant.
- [ ] Matrix walked in sabotage testing (each source killed, throttled, 4xx/5xx/empty).

## Failure Modes

- **Spinner purgatory**: one centered spinner for a 12-second load, no structure, no progress, no cancel. Users refresh (doubling load) or leave.
- **The optimistic blank**: fetch fails, error swallowed in a `.catch`, view renders empty — user believes their data is gone. The most trust-destroying bug in the class, and it's usually one missing error branch.
- **Skeleton bait-and-switch**: skeleton promises a table, delivers cards — double layout shift, worse than honest spinning.
- **Toast-error evaporation**: destructive failure announced in a 4-second toast; user looks up from keyboard to a normal-looking screen and a lost edit.
- **`[object Object]` / raw stack traces in pixels**: the error pipeline had no human-mapping layer.
- **Reload-as-retry**: "Try again" → full page reload → user loses scroll, form state, and faith.
- **All-or-nothing dashboards**: one widget's 500 blanks six healthy widgets; boundary placement defaulted to "page."
- **Fake progress**: a bar animating to 90% then parking — users learn your progress is theater and distrust the honest ones too.
- **Error-shaped empty**: search backend down renders "No results found" — user rewrites their query three times, then blames themselves.

## Edge Cases

- **The flash cascade**: cached-fast paths flash skeleton for 30 ms — debounce indicators (show after 150 ms) AND minimum-display (if shown, keep 300–500 ms) to prevent flicker in both directions.
- **Race: slow request A resolves after newer request B** → stale render overwrites fresh (key requests, ignore stale — see state-management).
- **Empty during first sync**: integration connected, data arriving over 30 min — needs a progress-honest "syncing (12%)…" state distinct from both empty and loading.
- **Partial page with pagination**: page 2 fails while page 1 rendered — inline "couldn't load more" + retry at the list tail, not a page-level error.
- **Long-running with browser close**: >10 s operations must survive tab death (server-side job + notification), or warn before close.
- **Permission changes mid-session**: a 403 on a previously-visible resource needs "access changed" framing, not generic failure.
- **Error inside an error**: the error-reporting call fails, or the retry endpoint differs — global boundary must be dependency-free (static, no data fetch).
- **Screen readers**: state changes need `aria-live` announcements (polite for loading-done, assertive for errors); a visual skeleton is silent to a blind user — announce "loading" and "loaded, 12 items".
- **Clock-based staleness**: "updated 5 minutes ago" computed client-side drifts with device clocks; compute server-side or tolerate.

## Tradeoffs

- **Optimistic vs honest UI**: optimism (instant success rendering) feels fast and demands rollback + failure-surfacing design; honesty (wait for confirmation) is slower and simpler. Optimize per operation: reversible+high-success → optimistic; destructive/financial → honest (see state-management).
- **Skeleton fidelity vs maintenance**: pixel-perfect skeletons drift as layouts evolve; low-fi gray blocks age better but promise less. Mid-fi (structure without detail) is the durable compromise; co-locate skeleton with component so they change together.
- **Auto-retry vs user control**: silent auto-retries smooth transient blips but hide systemic failure and burn battery/quota; manual-only retries surface every hiccup. Ladder: 1–2 quick auto-retries, then surface with manual control and status.
- **Rich error detail vs alarm**: engineers want codes and traces visible; users want calm. Resolve with layering — human copy front, request-ID quietly, "details" disclosure for the curious/support-guided.
- **Celebratory empty vs efficient empty**: inbox-zero art delights consumers, wastes a power-user's glance. Density and audience decide (see visual-hierarchy); both must still answer "what now?"

## Optimization Strategies

- Centralize the pattern kit: `<ErrorState/>`, `<EmptyState/>`, `<Skeleton/>` components with enforced slots (title/safety/action) — three-questions compliance becomes the path of least resistance.
- Instrument state views as events (`error_state_viewed{class, view}`) and rank by frequency × severity — design effort flows to the states users actually inhabit.
- Build a state-forcing devtool (query param or panel: `?state=error`) so designers/QA can see any cell of the matrix in one click; sabotage testing becomes routine instead of heroic.
- Review latency percentiles quarterly and re-fit the loading ladder — a backend improvement can turn skeleton-screens into flash-problems silently.
- Convert your top recurring error into a prevention: the most-seen error state is a product bug wearing UX clothes (e.g., "session expired" errors → silent token refresh).
- Copy-review error messages with support: they know which phrasings generate tickets vs self-resolution; error copy is a deflection tool.

## Self Review

- Can I show the filled state matrix? Which cells did I hand-wave with "standard spinner"?
- What does the user see at p95 latency, not p50? Did I watch it at 3G throttle?
- For each failure: what happened / is data safe / what now — are all three answered in pixels, not intentions?
- Does any retry button lie (reload, or re-fire a non-idempotent mutation unsafely)?
- Kill each data source one at a time: what actually renders? (Do it, don't reason about it.)
- Which of my empties is secretly an error state?
- Does refresh of existing content ever blank it?
- What does a screen reader hear during load → error → retry → success?

## Examples

**1. Dashboard with per-region dignity.**
Six widgets, independent sources. Design: region skeletons (matching each widget's real layout) with staggered 150 ms indicator delay; per-widget error cards ("Couldn't load revenue — your data is fine, the connection to Stripe timed out. [Retry]") with widget-level retry; page-level banner only if ≥4 widgets fail ("We're having trouble reaching several sources — [request-ID]"). Refetch every 60 s keeps old data visible with a quiet pulse dot, never re-skeletoning. Sabotage test kills each source: five healthy widgets keep working every time.

**2. The three-questions rewrite.**
Before: toast — "Oops! Something went wrong (500)". After, in-place at the affected panel: "Couldn't publish your post. Your draft is saved on this device. Retrying automatically… (attempt 2 of 3) — or [Retry now] · [Copy draft]" with request-ID in the details disclosure. Same failure, same backend; support tickets for this flow drop by half because the user knows their data survived and what happens next — the two things the old toast never said.

**3. Four empties in one search view.**
Product list screen: (a) first-use → "Track your first product — pull inventory from Shopify in ~2 minutes [Connect Shopify]" + smaller "or add manually"; (b) filters-exclude-all → "No products match *status: archived* + *tag: summer* — [Clear filters]" with the filter chips shown; (c) user archived everything → "All archived. 🎉 [View archive] [Add product]"; (d) search service down → an honest error state with retry — explicitly NOT "no results". Four different cells, four different jobs; the code enforces the distinction by requiring a reason enum to render any empty.

**4. Long export converted to async.**
CSV export ran 25–90 s behind a spinner; users clicked repeatedly, spawning duplicate jobs. Redesign: click → button busy 300 ms → inline card "Preparing export (4,210 rows)… ~1 min" with real progress from the job API + Cancel (which aborts the job); past 10 s a note: "You can leave — we'll notify you." Completion → notification + download persists in an exports list for 7 days. Duplicate jobs eliminated by disable+idempotency key; support tickets titled "export broken" (it never was — it was just silent) go to zero.

## Evaluation Rubric

Score 1–10:

- **1–2**: Only ideal states designed; failures blank or `[object Object]`; single global spinner; empties are dead ends.
- **3–4**: Some loading/empty patterns; errors generic ("Something went wrong"); retries reload the page; composite screens fail whole.
- **5–6**: State matrix mostly filled; loading ladder applied; three-questions copy on major flows; per-region degradation on key screens.
- **7–8**: Full checklist: measured-latency-fit loading, four empties distinguished, idempotent-safe retries, boundary placement deliberate, sabotage-tested, aria-live announced.
- **9–10**: Additionally: state-forcing devtool in use; state-view analytics driving prevention work; stale-while-revalidate presentation throughout; support-calibrated error copy; the matrix is a living artifact that new views must fill before shipping.
