---
name: dashboard-ux
description: "Use when building analytics/monitoring/executive/operational dashboards, engagement is low or users export to spreadsheets, stakeholders keep asking for 'another chart,' or choosing which metrics earn the screen."
---

# Dashboard UX

## Purpose

Design dashboards that answer their users' actual questions in seconds — metric hierarchy, comparison context, drill-down paths, time handling — instead of walls of charts that demo well and inform nobody.

## When to use

- Building analytics, monitoring, executive, or operational dashboards.
- An existing dashboard gets low engagement or users export to spreadsheets instead.
- Stakeholders keep requesting "just add another chart."
- Choosing which metrics deserve the screen and which die.
- Designing KPI cards, chart selection, filters, and refresh behavior.

## Goals

- The 5-second test passes: a target user states the main takeaway within 5 seconds of looking.
- Every number on screen has comparison context (target, trend, or prior period) — no naked numbers.
- Overview → drill-down paths exist for every question the overview raises.
- Time semantics (zones, partial periods, refresh) are consistent and honest everywhere.

## Inputs

- The question list: the 3–7 actual questions users need answered, ranked (from interviews/support asks — not from "what data do we have?").
- The audience and cadence: daily operator? weekly manager? monthly exec? (density and depth follow).
- Decision-action mapping: for each question, what would the user *do* differently based on the answer?
- Data realities: freshness, timezone of record, known quality gaps, cardinalities.

## Outputs

- Question-ranked layout: one primary answer zone, supporting metrics, drill paths per widget.
- Metric definitions doc: each metric's formula, source, timezone, refresh cadence, and owner — visible or one hover away.
- Comparison policy (vs target / prior period / cohort) applied uniformly.
- Empty/loading/error states per widget (per interface-states skill).

## Expert Mental Model

- **A dashboard is answers, not data.** Start from questions ("are we going to hit the quarter?", "is anything on fire?", "which channel is underperforming?"), not from available tables. Every widget must be the answer to a namable question; widgets that answer nothing are decoration that taxes every glance. The intake question for any chart request: "what will you do differently based on this?" No action, no pixel.
- **A number without comparison is noise.** "4,382 signups" means nothing; "4,382 — ▲12% vs last week, 89% of target" is an answer. Comparison is the meaning-making machinery: vs target (am I okay?), vs prior period (which way is it going?), vs peers/segments (where specifically?). Experts enforce a comparison policy so every KPI card carries context by construction.
- **Hierarchy mirrors question priority.** The single most important answer gets the top-left (LTR) and the largest treatment; secondary metrics support it; the long tail lives behind drill-downs. A dashboard where 12 equal widgets shout equally answers nothing first — see visual-hierarchy; dashboards are its hardest exam.
- **Overview first, then zoom and filter, then details on demand** (Shneiderman's mantra — still undefeated). The overview raises questions; every widget must offer the path to its own "why?" — click a spiking line → segmented breakdown → the underlying records. Dead-end widgets convert curiosity into support tickets or spreadsheet exports.
- **Time is the hardest data type on the page.** One global time-range control governing all widgets (mixed silent ranges = lying dashboard); explicit timezone policy shown, not assumed; partial periods marked ("today so far" — else today always looks like a crash); comparisons aligned like-for-like (this Monday vs last Monday, not vs Sunday).
- **Live-ness is a cost, not a feature.** Realtime updating earns its complexity only where a user can act within minutes (ops, trading, support queues). Exec dashboards updating per-second are theater; worse, numbers that wiggle during a meeting destroy confidence. Match refresh to decision cadence and *show* data freshness ("as of 09:02").

## Workflow

1. **Interview for questions, rank them**: watch users work, collect the questions they ask of data today (including the ones answered by exporting to Excel). Rank by frequency × decision impact. Cap the dashboard at answering the top 5–7.
2. **Map each question → decision → widget**: question ("is revenue on track?") → decision (reallocate spend) → the *minimum* visualization answering it (a number + target + sparkline, not a 12-series chart). Write the metric definition (formula, source, timezone, refresh) at the same time.
3. **Choose chart types by the question's shape**: trend over time → line; compare categories → horizontal bar (sorted); part-of-whole → stacked bar/treemap (pie only ≤3 slices, if at all); distribution → histogram; correlation → scatter; single status → big number + delta. Novelty charts must beat the boring choice in a real comprehension test or die.
4. **Lay out by hierarchy**: primary answer top-left, large; its supporting breakdowns adjacent; monitoring row below; admin/rare below fold or on a second view. Group by question, not by data source.
5. **Enforce the comparison policy**: every KPI card = value + delta vs chosen baseline + micro-trend (sparkline); every chart carries target lines or prior-period ghosting where a target exists. Deltas colored semantically *by desirability* (cost going down = green) not by sign.
6. **Wire the drill paths**: each widget's click → the natural next question (segment breakdown, then record-level list, filtered to what was clicked). URL-encode dashboard state (time range, filters) so every view is shareable — a dashboard link that reproduces exactly what the sender saw.
7. **Install the global time system**: one range picker; presets matching the audience's cadence (today/7d/30d/QTD); explicit timezone label; partial-period markers; comparison auto-aligned to like periods.
8. **Set refresh honestly**: per-widget or global "as of" timestamps; auto-refresh only at decision cadence; never silent-wiggle numbers mid-view (batch updates with a subtle refresh cue).
9. **Design the non-ideal states** per widget (interface-states): new-account empty (what will appear here + setup path), no-data-in-range vs error distinguished, per-widget degradation.
10. **Test with the 5-second and takeaway protocol**: show target users the live dashboard for 5 seconds → "what's the headline?"; then 60 seconds → "what would you do?" Iterate until the top question's answer is what they say. Then instrument usage (widget interactions, filter usage, export clicks) and prune quarterly.

## Decision Tree

- If the user checks it many times daily to catch problems (ops) → dense, dark-mode-friendly, thresholds/alerts visually loud, realtime where actionable, minimal decoration.
- Else if weekly/monthly steering (exec/manager) → few big numbers with targets and trends, stable layouts (same chart positions every week builds reading fluency), annotations for anomalies ("price change Mar 3"), PDF/share-friendly.
- Else if analytical exploration → this isn't a dashboard, it's an analysis tool: invest in filter/segment/pivot mechanics, saved views, and export — don't cram exploration into KPI cards.
- If a stakeholder requests a new widget → route through the intake: question? decision? frequency? If it can't displace something above the fold by rank, it goes to a secondary view or dies. The dashboard's scarcest resource is glanceable area.
- If two audiences need different questions answered → two dashboards (or role-based views) — the merged version serves neither; "one dashboard for everyone" is how walls of charts happen.
- If a metric is requested "just to watch it" → alerting, not dashboard: set a threshold notification and keep the pixels.
- If the data can't support the question honestly (quality gaps, missing joins) → show the limitation explicitly or don't ship the widget; a confident wrong number is the worst artifact a dashboard can produce.

## Heuristics

- Naked-number ban: value + comparison + period label, always. "Revenue $48.2k" → "Revenue $48.2k ▲8% vs prior 30d · 92% of target".
- Delta desirability: color deltas by good/bad for the business, and mark direction with arrows/sign for the colorblind (never hue alone).
- Sort every categorical bar chart by value (or by a meaningful fixed order); alphabetical sorting hides the answer the chart exists to give.
- Axis honesty: bar charts start at zero (length encodes value); line charts may zoom but label it; truncated bars are how dashboards lie by accident.
- Max ~7 series per line chart; beyond that, "top 5 + other" with interaction to swap series in.
- Tabular numbers, right-aligned, consistent precision (2 sig-figs-ish for glancing; full precision on hover/drill). $1,204,392.18 on a KPI card is false precision theater — $1.2M reads.
- Sparklines beat mini-charts on cards: trend shape without axes; the card's job is "which way is it going," not "read values."
- Every widget hover reveals: exact values, definition, "as of" time, and the drill link — the metadata layer that prevents "what does this even count?" meetings.
- Annotations are cheap gold: deploy markers, campaign starts, price changes on time-series turn "weird spike" into "oh, right."
- Rotate nothing: carousels/auto-cycling widgets mean the answer is invisible 80% of the time.
- Export respects filters and shows applied filters in the file header — the exported CSV becomes tomorrow's argument; make it self-describing.
- Filter state visible as chips; "why is this number weird" is usually "a filter you forgot is on."

## Quality Checklist

- [ ] Question list exists, ranked; every widget maps to one; intake process live for new requests.
- [ ] 5-second test passed by a real target user; 60-second action test coherent.
- [ ] No naked numbers; comparison policy uniform; deltas desirability-colored + direction-marked.
- [ ] One global time control; timezone labeled; partial periods marked; comparisons like-for-like.
- [ ] Every widget drills to its "why" and terminates at records; dashboard state URL-shareable.
- [ ] Chart types justified by question shape; bars zero-based; categories sorted.
- [ ] "As of" freshness visible; refresh cadence matches decision cadence; no mid-view wiggle.
- [ ] Metric definitions one hover away; formula/source/owner documented.
- [ ] Non-ideal states per widget (new, empty-range, error) distinguished.
- [ ] Usage instrumented; quarterly prune scheduled; export self-describing.

## Failure Modes

- **The wall of charts**: 24 widgets, all data no answers — built from "what can we plot" instead of "what do they ask." Engagement rounds to zero; the org's real dashboard becomes a spreadsheet someone maintains by hand.
- **Vanity metrics center-stage**: cumulative registered users (up and to the right, forever) headlining while activation quietly declines in a corner. The dashboard exists to comfort, not steer.
- **Naked numbers**: "Churn 3.2%" — is that good? For us? This month? The reader supplies context from memory or anxiety.
- **Mixed silent time ranges**: revenue MTD next to signups-last-7-days next to all-time NPS; cross-widget mental math produces confident nonsense.
- **The today-cliff**: today's partial data plotted as a full period — every morning, metrics "crash" and someone panics. A "so far" marker or excluding the partial bucket fixes a recurring fire drill.
- **Timezone roulette**: server-UTC buckets shown to PT users — "yesterday" spans 4 pm–4 pm and daily numbers never match the team's lived day.
- **Dead-end widgets**: a spike with no click-through; the analyst gets Slacked, runs SQL, and the dashboard has taught users it's a poster.
- **Realtime theater**: exec KPIs re-rendering every 5 s, numbers wiggling during the board meeting; trust in every number drops with each twitch.
- **Definition drift**: two dashboards, two "active users" formulas, one angry meeting. No definitions layer, no owner.

## Edge Cases

- **Sparse/low-volume data**: daily granularity on 3 events/day produces noise theater — auto-coarsen granularity (weekly) below density thresholds, or show "insufficient data for trend."
- **New accounts / cold start**: every widget empty — the dashboard should degrade into onboarding (what will appear here + setup action per widget), not render a grid of zeros.
- **Extreme values**: one whale customer flattens every other series — log scales (labeled!), "excluding top 1" toggles, or breakout treatment; design for the magnitude distribution you actually have.
- **Negative and zero-crossing metrics**: net revenue retention, P&L — diverging color scales and zero-lines; a "growth" palette breaks on negatives.
- **DST and month-length**: week-over-week across DST shifts an hour; Feb vs Jan comparisons are 10% off by calendar alone — compare rates/daily-averages where lengths differ, or annotate.
- **Late-arriving data**: yesterday's numbers revise as events trickle in — mark revisable windows ("last 48h may update") or freeze-and-restate policy; silent revisions burn trust ("the number changed since I screenshotted it").
- **Percentiles vs averages**: latency/duration metrics need p50/p95/p99, never mean alone (see observability skill); dashboards are where averages hide outages.
- **Very long category names / i18n**: horizontal bars + truncation-with-tooltip; the German label will come.
- **Screen contexts**: wall-mounted TV mode (bigger, fewer, auto-rotating exempted from the rotation ban *only* here), mobile glance (top 3 KPIs, not the grid squeezed).

## Tradeoffs

- **Density vs approachability**: operators want everything co-visible; occasional users drown. Split by audience/views rather than averaging (see visual-hierarchy density decision).
- **Stability vs freshness of layout**: rearranging widgets to feature the current fire breaks the spatial memory weekly readers rely on. Keep positions stable; use alert states within stable slots to make fires loud.
- **Flexibility vs opinionation**: user-configurable everything (drag widgets, custom metrics) serves power users and produces 500 slightly-wrong personal dashboards with divergent definitions. Opinionated core + saved filter-views is usually the right cut; full BI-builder is a different product.
- **Answer completeness vs glanceability**: each added widget dilutes every existing one. The prune is not optional maintenance; it's the design.
- **Precompute vs on-the-fly**: precomputed aggregates load instantly and constrain drill paths; live queries flex and lag. Precompute the overview, go live at the drill — the user's patience grows as their question sharpens.

## Optimization Strategies

- Instrument the dashboard like a product: widget views, hovers, drills, filter usage, export clicks, time-on-view. The widgets nobody touches are your prune list; the most-exported view is a missing feature.
- Run the 5-second test quarterly with fresh eyes; dashboards decay via accretion, and insiders stop seeing it.
- Add annotation infrastructure early (deploys, campaigns, incidents on all time-series) — the cheapest 10× to interpretation speed.
- Precompute + cache the overview aggressively (see caching); a dashboard that loads in 400 ms gets checked; 8 s gets a spreadsheet replacement.
- Publish the metric dictionary from the same source that renders the numbers (one definition, two surfaces) — kills definition drift structurally.
- Convert watched-but-never-acted widgets into alerts: threshold notification replaces pixels; the dashboard shrinks and sharpens.
- Pair with a "weekly narrative" mode where it matters: the same numbers with auto-generated deltas-and-annotations text for the Monday email — meets the audience where they already read.

## Self Review

- Can I name the question each widget answers, and the decision it feeds? Which widgets failed intake and got in anyway?
- Did a real user pass the 5-second test, or did I pass it for them?
- Is there a naked number anywhere? A truncated bar? An unsorted categorical chart?
- Pick any widget: where does its drill path end? Records, or a dead end?
- What timezone is this dashboard in, where does it say so, and is today marked partial?
- Which numbers revise after the fact, and how would a screenshot-taker learn that?
- What did we prune last quarter? (If nothing: the intake is theater.)

## Examples

**1. From wall-of-charts to answers (SaaS exec view).**
Before: 22 widgets, mixed ranges, no targets. Question workshop yields top 5: on track for quarter? / where's new revenue coming from? / is churn moving? / is the funnel healthy? / anything anomalous? After: headline zone = QTD revenue vs target (big number, pace projection "tracking to 94%", sparkline); channel breakdown bar (sorted, click → channel view → account list); churn KPI with cohort drill; funnel strip with stage-over-stage deltas; anomaly feed (auto-flagged deviations with annotations). 22 → 9 widgets, one time system (company TZ labeled), stable layout. The Monday meeting now opens with the dashboard instead of a hand-built deck — the actual success metric.

**2. Ops dashboard where seconds matter.**
Support-queue ops: top row = SLA-at-risk count (red past threshold, click → the at-risk tickets themselves), current wait p90, agents online vs scheduled. Realtime (30 s) because operators act in minutes; everything else 5-min. Dense dark theme, thresholds as visual states in fixed slots (stability under stress), one accent for "needs human now." The drill from any number lands on actionable records with bulk actions — the dashboard is a dispatch surface, not a report.

**3. The today-cliff and timezone repair.**
Recurring panic: "signups crashed today!" Every day. Diagnosis: UTC day buckets + partial today shown as full. Fix: company timezone label top-right, applied everywhere; today's bucket rendered hollow with "so far · updates live"; WoW comparison auto-aligns same-weekday like-for-like; late-arriving events documented with "last 48h may revise ±2%". Panic pings stop; more importantly, screenshots taken at different hours stop contradicting each other in exec threads.

**4. Intake process defeating widget sprawl.**
Request: "add a map of users by country." Intake: question? ("where are users?" — curiosity); decision? (none identified — no regional strategy exists); frequency? (would glance monthly). Verdict: not a dashboard widget — shipped as a quarterly analytics report instead. Counter-request from same team: "which self-serve signups are sales-touchable?" — question maps to a daily SDR workflow decision → earns a ranked list widget with score drill-down, placed in the SDR view. The dashboard stayed at 9 widgets; both stakeholders got served. The intake question list is doing the design.

## Evaluation Rubric

Score 1–10:

- **1–2**: Chart wall from available data; naked numbers; mixed time ranges; no drills; vanity metrics headline.
- **3–4**: Some KPI cards with deltas; layout by data source; time control partial; drill paths sporadic; definitions tribal.
- **5–6**: Question-driven layout; comparison policy mostly enforced; global time with labeled TZ; drills on main widgets; freshness shown.
- **7–8**: Full checklist: 5-second test passed by users, like-for-like comparisons, partial-period honesty, shareable state, metric dictionary, per-widget states, intake gate.
- **9–10**: Additionally: usage-instrumented with quarterly prunes actually executed; annotations infrastructure; revision policy for late data; watched-metrics converted to alerts; the dashboard demonstrably changed a decision cadence (meetings open with it; exports declined).
