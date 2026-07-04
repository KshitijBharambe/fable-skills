# Onboarding & Activation

## Purpose

Design first-run experiences that get users to their first moment of real value ("aha") in minimum time and clicks — activation as a funnel you instrument and shorten, not a tour you bolt on.

## When to use

- Designing signup → first-value flow for a new product or feature.
- Activation/retention metrics are poor; users sign up and evaporate.
- Someone proposes a product tour, tooltip carousel, or onboarding checklist.
- Adding a heavy prerequisite (connect data source, invite team, install SDK) to first-run.
- Reviewing empty first-screens.

## Goals

- Time-to-first-value measured in minutes and clicks, with a target and a funnel per step.
- Users *do* the core action in their first session — with their own (or realistic sample) data.
- Setup questions deferred, inferred, or deleted; nothing asked before it's needed.
- Every drop-off step known, quantified, and owned.

## Inputs

- The product's "aha" definition: the earliest event correlated with retention (e.g., "created first invoice," "saw own data in a chart," "first reply received"). If unknown, the first task is defining and validating it.
- Current funnel data: step-by-step conversion from landing → signup → activation (or a plan to instrument it).
- Prerequisites inventory: what genuinely must exist before value (account? data? teammates? payment?), and which are actually deferrable.
- Segments: distinct intents at signup (evaluator vs invited teammate vs migrator) — each may need a different path.

## Outputs

- Activation metric definition + instrumented funnel with drop-off per step.
- The first-run flow: screens/steps, what's asked when, what's inferred, what's defaulted.
- Empty-state and sample-data designs for every surface a new user can reach.
- A deferral map: every setup demand → when it's actually needed → where it moved.

## Expert Mental Model

- **Time-to-value is the metric; everything else is commentary.** Count the minutes and clicks from signup to the aha event. Every field, screen, decision, and permission prompt between the user and that moment is paying rent it must justify. Experts walk the flow with a stopwatch, then again with a click counter.
- **Do, don't tour.** Product tours get skipped or forgotten because passive information doesn't build competence — doing does. The gold standard is a guided *first real task*: the user creates/imports/sends the actual thing, learning the interface as a side effect. Tooltip carousels teach the map; a first task teaches the territory.
- **The empty state IS the onboarding.** New users spend their first session staring at empty screens; each one either says "dead end" or "here's exactly what to do." Every empty surface gets: what this is, why it's valuable, one primary action to fill it (see interface-states skill).
- **Ask at the moment of need, not at the door.** Progressive profiling: every question moves as late as possible — role/team-size questions to when they personalize something real; notification permissions to right after the user does something worth notifying about; payment to the value boundary. Upfront questionnaires trade your activation rate for a marketer's convenience.
- **The blank canvas is hostile; ship momentum.** Sample data, templates, or a pre-built example workspace let users experience the "after" before doing the work. Endowed progress (a checklist where step 1 — "create account" — is already checked) measurably increases completion; humans finish what feels started.
- **Segments diverge at the door.** An evaluating admin, an invited teammate, and a migrator from a competitor need different first tasks (evaluate: see value fast with sample data; teammate: land directly in the shared context that invited them; migrator: import). One-size-fits-all onboarding fits nobody; 2–3 declared-intent branches are worth the fork.

## Workflow

1. **Define and validate the activation event**: correlate candidate early actions with week-4+ retention (cohort analysis); pick the earliest strong predictor. Write it down as *the* target.
2. **Map the current path**: every screen/click/field from first touch to activation. Stopwatch it. Count decisions. This artifact makes the bloat undeniable.
3. **Interrogate every step**: for each ask — delete (don't need it), infer (from email domain, geo, invite context), default (best-guess, editable later), or defer (to moment of need)? Only survivors stay upfront. Target: signup itself ≤1 screen.
4. **Design the first task, not a tour**: choose the single workflow that produces the aha; guide it inline (spotlight the next control, prefill what you can) with real or sample data; celebrate completion once, briefly.
5. **Fill every empty surface**: sample data clearly marked (and one-click removable), templates for the cold-start, or an interactive example. The user should never face a blank screen and a toolbar.
6. **Branch by declared intent** if segments differ: one question, 2–3 options, visibly shaping the path ("What brings you here?" → different first tasks). Invited users skip to the inviter's context — the invite IS their onboarding.
7. **Sequence the hard asks after first value**: data connection, team invites, payment, notifications — each gets a contextual moment ("you've built a report — connect live data to keep it fresh") rather than a gate at the door. Exception: products where value is impossible without the prerequisite (see Decision Tree).
8. **Add the checklist as scaffolding, not homework**: 3–5 items max, first pre-checked, each linking to a guided action, dismissible, gone when done. It's a progress indicator for the first session, not a permanent LMS.
9. **Instrument the funnel** per step + time-between-steps; alert on step regressions; watch session recordings of the first 10 minutes monthly — the funnel says where, recordings say why.
10. **Design re-entry**: most users don't activate in session one. Email/notification nudges tied to their actual stopping point ("your report is one click from live data"), and a first-return screen that resumes, not resets.

## Decision Tree

- If value is demonstrable without user data (dashboards, editors, planners) → sample data/template first-run; ask for real data after the aha.
- Else if value requires their data (analytics SDK, email client, integrations) → the connection IS the first task: invest everything in making it feel 5 minutes (one-click OAuth over API keys, copy-paste snippets with their token prefilled, a live "waiting for first event…" screen that celebrates arrival) and provide a demo-data escape hatch for evaluators who can't connect yet.
- Else if value requires other people (chat, review tools) → single-player mode first (value alone: notes-to-self, solo review), invites framed as amplification; never a "invite 3 teammates to continue" wall.
- If the user arrived via invite → skip marketing onboarding entirely; land in the inviting context with one inline orientation moment.
- If the user is migrating from a named competitor → importer as first task; their old data appearing in your product is the aha.

Checklist or not:
- If activation needs ≥3 distinct actions across surfaces → checklist earns its place.
- Else → a single guided task beats a checklist of one real item padded with filler ("explore the dashboard!" is not a step, it's an admission).

When teams propose a tour:
- If the UI is genuinely novel (new paradigm) → one short orientation moment (≤3 beats) then the guided task.
- Else → redirect the effort into the first task and empty states; tours are where onboarding budgets go to die.

## Heuristics

- Clicks-to-aha budget: single digits. Every click past ~7 costs measurable activation; every form field costs more than a click.
- Signup form: email + password (or SSO) only. Name can come later; company size can come never (infer from domain + seats).
- "Skip" must exist on every onboarding step and be honest — users who skip and explore convert too; trapped users bounce.
- Sample data must be *plausible and flattering* — a beautiful example teaches what good looks like; `test test 123` teaches nothing. Mark it, and make deletion one click.
- First session ending = save everything. Returning to lost progress is the cruelest churn trigger.
- Ask for the notification permission only in the moment after an event the user would want to hear about; cold permission prompts get denied and can't be re-asked cheaply.
- The activation email sequence mirrors the in-product funnel: each email targets the user's actual stuck-step, not a generic drip.
- Beware vanity activation ("completed onboarding checklist") — the metric is the retained-correlated event, not your flow's completion.
- Time-to-value for developer products = time-to-first-successful-API-call from a cold terminal; test it quarterly with a new hire.
- Every onboarding element must have a removal path: what users see at day 30 should be zero onboarding residue.
- Measure rage signals in first-run: back-button loops, field re-entry, pricing-page detours mid-flow — each marks a step that's asking too much.

## Quality Checklist

- [ ] Activation event defined, retention-validated, instrumented.
- [ ] Funnel dashboard: per-step conversion + time-between-steps; owner assigned.
- [ ] Signup ≤1 screen; every upfront question survived delete/infer/default/defer interrogation.
- [ ] First-run is a guided real task producing the aha, not a tour.
- [ ] Zero blank screens: sample data/templates/examples on every reachable surface.
- [ ] Hard asks (data, invites, payment, permissions) placed at moments of need with context.
- [ ] Invited-user and migrator paths distinct from evaluator path.
- [ ] All steps skippable; skipping lands somewhere sane.
- [ ] Re-entry designed: resume state + stuck-step-targeted nudges.
- [ ] Session recordings of first-10-minutes reviewed within the last month.

## Failure Modes

- **The questionnaire wall**: 9 fields about company size and use case before the product appears. Activation pays; the CRM gets slightly richer; the trade was never priced.
- **Tour theater**: 8-step tooltip carousel; users click × or Next-Next-Next; two minutes later they've retained nothing and face the same blank screen.
- **Blank-canvas abandonment**: signup lands on an empty workspace with a toolbar. The product asked the user to imagine the value it was supposed to demonstrate.
- **The teamwall**: "Invite 3 colleagues to get started" before any solo value; the user needed proof to justify inviting anyone.
- **Checklist homework**: 11 items including "watch a video" and "follow us on X" — the checklist became a marketing channel and lost its scaffold function.
- **Activation theater metrics**: optimizing checklist-completion while retention stays flat — the checklist didn't point at the aha.
- **One-path-fits-all**: the invited teammate forced through the admin's setup wizard for a workspace that already exists.
- **Permission ambush**: notification + contacts + location prompts stacked at first launch; all denied; growth loops dead on arrival.
- **No re-entry design**: user leaves at step 3 of 5; returns to step 1 or, worse, to the post-onboarding app with no path back.

## Edge Cases

- **The second user problem**: teammate joins a configured workspace — their aha differs (see the team's real activity immediately, contribute once); design their first-contribution moment explicitly.
- **Free-trial cliffs**: value discovered on day 13 of a 14-day trial = churn shaped like "product wasn't ready." Trial clocks should start at activation (or extend on it), not at signup.
- **Empty-because-integration-is-syncing**: first sync takes 30 minutes — that gap needs progress honesty + something to do (explore sample, configure preferences), or it reads as broken.
- **Re-onboarding on major changes**: existing users are new users for the redesigned area; a one-beat "what moved" moment beats both silence and a full tour.
- **Multiple products/entry points**: users landing from an ad for feature X must onboard toward X's aha, not the generic one — intent from the landing page should thread through signup.
- **Compliance-heavy signups** (KYC, medical): where legal gates are immovable, interleave value between them (show the dashboard between document uploads) rather than stacking all pain first.
- **Returning churned users**: "welcome back" ≠ new-user flow; acknowledge their history, surface what's new, restore their artifacts.
- **B2B bought-not-chosen users**: procurement bought it; end users didn't ask for it — onboarding must sell the personal win ("this saves *you* the Friday report"), not the company pitch they didn't buy.

## Tradeoffs

- **Personalization vs friction**: each segmentation question can genuinely improve the path — and costs conversion at the door. Rule: a question earns its place only if the answer *visibly changes the next screen*. Otherwise infer or defer.
- **Guided rails vs exploration**: heavy guidance activates the median user and irritates experts who want to poke around. Skippable rails + a sane skip-destination serve both; forced rails serve the metric until experts churn quietly.
- **Sample data vs real-data urgency**: samples demonstrate value instantly but can become a comfortable dead end ("played with the demo, never connected"). Pair samples with a persistent, contextual bridge to real data, and measure sample→real conversion as its own funnel step.
- **Speed-to-aha vs depth of setup**: some setup (SSO, permissions) done early prevents pain later; done upfront it kills activation. Split: admin-track (thorough, expected by the persona) vs member-track (instant value) rather than averaging the two.
- **Checklist persistence vs cleanliness**: keeping the checklist visible drives completion but clutters the product for the already-activated. Auto-collapse on progress, disappear on completion, never resurrect.

## Optimization Strategies

- Attack the single worst funnel step first (biggest absolute drop × traffic); resist redesigning the whole flow when one step owns 60% of the loss.
- Shorten before you polish: deleting a step reliably beats animating it. Run a quarterly "what can we stop asking?" review.
- A/B big swings on first-run (sample-data-first vs connect-first, task vs tour) — onboarding effects are large; micro-tests waste the traffic.
- Watch 5 session recordings per month of first-runs; one recording of a confused user redirects a quarter of roadmap better than dashboards.
- Prefill aggressively from every signal: invite context, UTM/landing intent, email domain, OAuth profile — each prefilled field is friction deleted.
- Treat the activation email/nudge sequence as part of the product: same funnel, same experiments, targeted at actual stuck-points.
- Re-run the new-hire test: someone who's never seen the product signs up cold while you watch silently. Calibrates the team's curse of knowledge better than any metric.

## Self Review

- What exactly is the aha event, and what's the evidence it predicts retention?
- Minutes and clicks from signup to aha, measured today? What's the biggest single drop in the funnel?
- Which upfront questions survived interrogation, and what does each one visibly change?
- Is the first-run a task the user *does*, or information the user *receives*?
- What does every empty screen offer a brand-new user?
- Where do invited users and migrators diverge from evaluators?
- What happens to a user who leaves at each step and returns tomorrow?
- If I signed up right now with a fresh email, what would annoy me first?

## Examples

**1. Analytics SDK: the connection IS the onboarding.**
Aha: "sees own live event in the dashboard." Old flow: 6-field signup → team questionnaire → docs link → 9% activation. New flow: email+SSO signup → one question ("what are you building?" → picks platform, changing the snippet) → copy-paste snippet with API key prefilled → live "listening…" screen that fires confetti once on first event → then a prebuilt dashboard of their events; demo-data toggle for those who can't install yet ("explore with sample data" — 31% of whom convert to real install within a week via a persistent banner). Invites and alert-permissions asked only after the first dashboard view. Time-to-aha: 4 minutes median; activation 9% → 34%.

**2. Project tool: single-player first, teamwall demolished.**
Old: "Invite your team (minimum 2)" as step 2; massive drop. New: signup lands in a personal workspace pre-populated with a plausible, well-crafted sample project (marked, one-click clearable) + a 4-item checklist (first item pre-checked): create a task ✓(guided, 30 s), complete a task, create your own project, invite a teammate — the invite framed after the user has real content worth sharing ("get feedback on *Website Redesign*"). Teammates who accept skip everything and land on the shared project with an inline "you're in Maya's workspace — here's your first task" beat. Invite step conversion doubled *because* it moved later.

**3. Funnel surgery on a fintech signup.**
Data: landing→signup 42%, signup→KYC-start 81%, KYC-start→KYC-done 39% (!), KYC-done→first-transfer 71%. Whole-flow redesign resisted; the 39% step decomposed: document-upload screen had no progress indication, rejected blurry photos silently, and lost state on app backgrounding. Fixes: live capture guidance, explicit per-document progress, resume-on-return, and value interleaving (account dashboard visible in read-only behind a "verification in progress" banner). KYC completion 39% → 68%; nothing else changed that quarter.

**4. Killing a tour, shipping a task.**
Design review: 7-step tooltip tour proposed for a BI tool. Counter-proposal shipped instead: first-run opens a half-built chart of sample revenue data with one spotlighted control ("drag *Region* here to break this down") — completing it triggers the second beat ("save to your first dashboard"). Two interactions teach drag-to-pivot and save-to-dashboard — the two behaviors that define retained users — by *doing*. Tour-completion was never measurable; task completion is 74% and correlates with week-4 retention at 3× baseline.

## Evaluation Rubric

Score 1–10:

- **1–2**: Questionnaire wall, tour theater, blank canvas after; no activation definition; no funnel.
- **3–4**: Some funnel awareness; checklist exists but points at flow-completion, not value; empty states partially addressed; one path for all segments.
- **5–6**: Retention-validated aha; guided first task; sample data; hard asks mostly deferred; funnel instrumented with owners.
- **7–8**: Full checklist: segment branches, moment-of-need asks, re-entry design, recordings reviewed, skip-paths honest, single-digit clicks-to-aha.
- **9–10**: Additionally: trial clocks tied to activation; sample→real bridges measured; email/nudge sequence funnel-targeted; quarterly deletion review; activation improvements demonstrated in cohort retention, not just funnel completion.
