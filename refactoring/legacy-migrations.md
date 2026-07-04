# Legacy Systems and Migrations

## Purpose

Change systems you didn't build and can't fully know — safely: pin behavior with characterization tests, replace incrementally via strangler and shadow patterns, survive the two-system period, and finish the long tail — while resisting the rewrite death spiral that has consumed better teams than yours.

## When to use

- Inheriting a system with thin tests, thinner docs, and departed authors — and needing to change it anyway.
- Any migration: database engine, framework, service extraction, vendor swap, data model overhaul, "v1 to v2."
- When "let's just rewrite it" enters the room (especially when you're the one saying it).
- Planning deprecations: an old API, a config format, a feature with three users somewhere.
- When a previous migration stalled at 60% and you've inherited *two* systems.

## Goals

- Current behavior pinned by characterization tests before surgery — including the weird behaviors, bug-for-bug.
- Replacement shipped incrementally: every step reversible, the mainline always serving real traffic, value landing before the end.
- Correctness proven by shadow comparison against production reality, not by test suites alone.
- The long tail (last 5% of data, traffic, consumers) planned as its own phase with its own owner — and actually finished.
- The old system *deleted* at the end: a migration isn't done until the predecessor is gone.

## Expert Mental Model

- **Legacy code is code whose behavior you can't cheaply verify — and the behavior is the spec.** Docs lie, comments lie, the original author's memory lies; only the running system tells the truth, and consumers depend on *that truth*, including its bugs. The foundational move is the **characterization test**: capture what the system actually does — feed it real inputs, record real outputs, assert *those* (not what "should" happen). When a characterization test surprises you ("it returns null for February?!"), that's the method working: you just found a behavior somebody, somewhere, depends on. Fix-or-preserve is a *decision with an owner* (see decomposing-ambiguity: essential ambiguity), never a silent side effect of the migration.
- **The rewrite death spiral, memorized as a vaccine.** The pattern that has killed a thousand v2s: the rewrite starts clean and fast (green field, no edge cases yet); meanwhile the old system keeps taking features and fixes (business doesn't pause), so v2 chases a moving target; the "easy 80%" ships in months, then v2 hits the swamp of edge cases that *were the actual system* (each weird branch in the old code was a customer, an incident, a regulation); the team is now maintaining two systems while shipping features in neither; eighteen months in, v2 launches partially, misses behaviors nobody knew existed, and the org quietly runs both forever — or cancels v2 and morale with it. The root error is epistemic: **the old system's complexity is mistaken for accident, when most of it is undocumented requirements.** Rewrites are occasionally right (dead platform, no seams at all, trivial scope) — but the burden of proof is on the rewrite, and "the code is ugly" is not proof (see first-principles: fence archaeology at system scale).
- **Strangler fig: replace by routing, not by switchover.** Put an interception layer in front of the old system (proxy, facade, router); build the replacement one capability at a time; move traffic per-capability from old to new; the old system atrophies until deletion. Every increment: small, independently shippable, independently *revertible* (the router flips back in seconds), and delivering value immediately. The strangler converts a bet-the-company cutover into a hundred boring deploys (see ci-cd: same law — smaller changes, lower risk; refactoring branch-by-abstraction is this pattern at code scale).
- **Shadow mode is how you prove correctness against reality.** Run new alongside old: mirror real production traffic to both, serve users from old, *diff the outputs*. The diff log is the truth engine — every mismatch is either a new-system bug (fix it) or an undocumented old behavior (decide: preserve or formally change). Ship the new side only when the diff rate is effectively zero *over a window long enough to include the rare paths* (month-end billing, the annual job — the observation window must match the phenomenon; see memory-leaks soak logic). For writes, invert: dual-write with old as source of truth, reconcile asynchronously, promote new only when reconciliation stays clean (see postgres migration patterns; event-driven for the messaging version).
- **The two-system period is the tax, and it must be budgeted and time-boxed.** Mid-migration you run both: dual patterns, dual on-call surface, adapters, sync jobs, "which system owns this?" questions in every incident (see production-debugging: seams multiply hypotheses). This period is unavoidable — the failure is treating it as free or letting it become permanent. The stalled migration (60% done, team reassigned, "temporary" adapters fossilizing) is *worse than either endpoint*: all of the tax, none of the payoff, forever. Experts drive the two-system window ruthlessly short per capability, keep a visible burn-down of what remains on the old side, and treat "the migration is 90% done" with the same suspicion as any 90% (see planning-and-estimation 90% syndrome).
- **The long tail is the migration.** Moving 95% of users/data/traffic takes weeks; the last 5% takes quarters and is where migrations die: the locked accounts, the enterprise customer with a contract pinning the old API, the malformed rows from a 2017 bug, the integration owned by a team that dissolved, the cron job nobody can find the owner of (see decomposing-ambiguity: second-hand systems). Plan the tail as a distinct phase with a named owner, an inventory (who exactly is still on the old path — measured, not guessed; see observability: instrument the old path *first*), per-holdout strategies (migrate for them, deadline them, buy them out, or consciously grandfather them with a price tag), and an explicit definition of *done = old system deleted*.

## Workflow

1. **Archaeology before surgery**: read the code where it's hot (git churn), the incident history, the weird branches; interview survivors; inventory consumers — every caller, cron, report, and Excel macro that touches the thing (see first-principles fence archaeology; research: primary sources are the code and its logs).
2. **Instrument the old system first**: usage per endpoint/feature/flag, callers identified, traffic shapes (see observability). You cannot deprecate what you can't measure — and you'll usually find 30% of the surface has zero traffic (deletion candidates before migration even starts).
3. **Write characterization tests over the surfaces you'll change**: real inputs → recorded outputs, weirdness preserved and *annotated* ("null for pre-2019 accounts — cause unknown, preserved deliberately"). Surprises get routed to owners as preserve-or-fix decisions.
4. **Find or create the seam**: the interception point where routing can happen — an API gateway, a facade module, a DNS name, a queue. No seam = build the seam first; it's the enabling investment for everything after (see system-design boundaries).
5. **Slice the migration by capability, ordered by risk-and-learning**: first slice = thin but end-to-end and *representative* (touches real data, real consumers — a walking skeleton through the new path; see planning-and-estimation), not the easiest corner.
6. **Shadow before serving**: mirror traffic, diff outputs, run the mismatch triage loop (new bug / preserved behavior / formal change). Drive diffs to ~zero across a window covering the rare cycles.
7. **Cut over per-slice, progressively**: 1% → 10% → 50% → 100% behind the router, with comparison metrics live and rollback rehearsed at each stage (see ci-cd progressive delivery). Old path stays warm until the slice's tail clears.
8. **Migrate data with expand-migrate-contract**: new schema/store added (expand), dual-write with reconciliation, backfill in throttled batches with checksums, reads flipped gradually, then old side removed (contract) — never a stop-the-world "migration weekend" where a rename would do (see postgres).
9. **Run the tail campaign**: holdout inventory, per-holdout owner and strategy, deadlines communicated with dates and migration support (see technical-writing: deprecation comms), grandfathering only as a *priced decision*.
10. **Delete**: the old code, the adapters, the dual-write, the router special-cases, the docs pointing at the corpse. Deletion is the definition of done — and the celebration is earned (see first-principles: deletions ship too).

## Decision Tree

- If tempted to rewrite → run the interrogation: Is the platform actually dead (vendor EOL, unhirable stack)? Is there truly no seam (and can't one be built)? Is scope genuinely small *including the edge-case swamp you haven't inventoried yet*? Two-plus yeses with evidence → rewrite a *thin slice* first as proof; otherwise strangle (see judgment-under-uncertainty: the burden sits on the one-way door).
- If there are no tests and no seam → build the seam at the coarsest honest boundary (wrap the whole binary/API if needed), characterize at that boundary, then work inward.
- If characterization reveals a bug consumers may rely on → preserve it through the migration (bug-for-bug), file the fix as its own versioned change with its own comms — never bundle behavior fixes into migration cutovers (two variables, one incident; see refactoring: structure vs behavior).
- If the old and new disagree in shadow → old is innocent until proven guilty: assume the new side is wrong first (it usually is), and when it isn't, the old behavior becomes a preserve-or-change decision with an owner.
- If the migration must pause → pause at a *stable* point: a capability fully on one side, adapters minimal, burn-down documented — never mid-capability with dual-writes running unreconciled ("temporarily," says the fossil record).
- If a previous stalled migration is discovered (two patterns, 60% moved) → finishing the old migration almost always beats starting a third pattern (see refactoring: the half-finished predecessor); inventory what remains, resume the burn-down.
- If a holdout won't move → classify: *can't* (missing feature in new — build it), *won't-yet* (inertia — deadline plus white-glove help), *won't-ever* (contract/economics — escalate to the business: grandfather with a maintenance price tag, or buy out the contract; this is a business decision wearing a technical costume; see technical-leadership stakeholders).
- If data backfill hits malformed history → triage classes, not rows: fixable-by-rule (script it), ambiguous (owner decides the rule), garbage (archive-don't-migrate, with a paper trail) — and the backfill is idempotent and resumable, because it *will* be interrupted (see async-processing idempotency).
- If the deadline pressure says "skip shadow mode" → shrink the slice until shadow fits, don't skip the proof; the shadow week is cheaper than the incident *and* the trust repair (see judgment-under-uncertainty: shrink blast radius, not confidence bars).

## Heuristics

- The weird branch is a requirement wearing a disguise: every `if account_type == 7` in old code was somebody's outage, contract, or regulator — archaeology before deletion (see first-principles Chesterton).
- Measure before you migrate: the endpoint with zero calls in 90 days doesn't get migrated, it gets deleted — the cheapest migration is the one you don't do.
- Old system as source of truth until the new one has *earned* it in shadow — burden of proof never flips by calendar, only by diff rate.
- One variable per cutover: migrate *or* fix behavior *or* add features — never two in the same flip; incidents with two variables take four times as long to diagnose (see production-debugging).
- Route by consumer, not by percentage, when consumers differ in risk: internal traffic first, then friendly externals, then the enterprise contracts with the sharp lawyers.
- Keep the revert warm: rollback rehearsed per stage, old path load-tested even while shadowed — a revert that hasn't run in six weeks is a hypothesis (see ci-cd rollback).
- The adapter you write "temporarily" needs a deletion ticket the day it's born, or it outlives you.
- Watch the burn-down, not the burn-up: "capabilities remaining on old" trending to zero is the honest metric; "features shipped on new" can grow forever while the old system lives.
- The migration's real calendar = your estimate × your team's historical migration multiplier (see planning-and-estimation reference-class) — and the tail is usually half the total, budgeted as a tenth.
- Deprecation comms follow the 3-2-1 shape: announced with dates and alternatives, warned in-band (headers, banners, emails to *measured* users of the old path), then enforced with brownouts before shutoff (short deliberate outages of the old path find the consumers your inventory missed — see api-design deprecation).
- If nobody owns the migration end-to-end, the two-system period is permanent — a named owner with the deletion date in their goals is the difference between a migration and a hobby.

## Quality Checklist

- [ ] Consumer inventory built from measurement (traffic, callers), not memory.
- [ ] Characterization tests pin the surfaces under change; surprises annotated and routed as decisions.
- [ ] Seam exists; every increment is independently shippable and revertible in minutes.
- [ ] First slice was representative (end-to-end, real data), not merely easy.
- [ ] Shadow/dual-write comparison ran across a window covering rare cycles; diff rate ~zero before each cutover.
- [ ] Behavior fixes decoupled from migration flips — one variable per change.
- [ ] Data moves used expand-migrate-contract; backfills idempotent, resumable, checksummed.
- [ ] Two-system tax visibly budgeted; burn-down of old-side capabilities maintained and shrinking.
- [ ] Tail phase has an owner, an inventory, per-holdout strategies, and communicated deadlines.
- [ ] Old system deleted — code, adapters, infra, docs; "done" was not declared before the funeral.

## Failure Modes

- **The rewrite death spiral** (see mental model): v2 chases the moving v1, drowns in the edge-case swamp, launches partial or never; the org runs two systems or zero morale. Root cause: old complexity misread as accident.
- **The two-system trap**: migration stalled at 60%, team reassigned to features, adapters fossilized — permanent double tax, no payoff; every new engineer now learns two patterns and a war story (see refactoring: the half-finished predecessor).
- **Silent behavior "fixes"**: the migration "cleans up" the null-for-February quirk; the downstream billing report that *keyed on it* corrupts quietly for a quarter — bug-for-bug wasn't honored, and nobody decided that on purpose.
- **Big-bang cutover**: the migration weekend — freeze, switch, pray; the plan's first contact with the malformed 2017 rows happens at 3am with the business closed and rollback "complicated" (see judgment-under-uncertainty: ruin-class bets).
- **Test-suite overconfidence**: unit tests green on the new side, shadow mode skipped — production traffic contained the twelve input shapes the tests never imagined; the diff log would have caught all twelve for the cost of a week.
- **Tail abandonment**: 95% migrated, victory declared, team disbanded — the old system now runs *forever* for 5% of traffic at 100% of its maintenance cost, unowned and rotting (see the deletion definition of done).
- **Migration + feature bundling**: "while we're migrating, let's also redesign the API" — two projects sharing one deadline and one incident budget; each masks the other's regressions (one variable per flip, violated at scale).
- **Unowned deprecation**: the sunset announced, never enforced — consumers rationally ignore deadlines that have slipped twice; the brownout that would have flushed them out was "too aggressive," so the old path lives another three years.

## Edge Cases

- **Consumers you cannot see**: the partner's cron hitting the old IP, the warehouse team's Excel macro, the mobile app version from 2021 pinned by a slow-updating user base — measured inventory catches most; brownouts catch the rest; app-store realities mean some old paths need *year*-scale tails (see api-design versioning).
- **Migrating the data model under live writes**: dual-write windows create ordering and conflict edges (write succeeds old-side, fails new-side); reconciliation must be directional and idempotent, and the cutover of *write* authority is the single scariest flip — do it per-tenant or per-shard, never globally (see postgres; concurrency-bugs).
- **The system that is also a product surface**: users see the old UI's quirks as features (keyboard shortcuts, quirky sort orders) — behavioral parity for machines is diffable; for humans it needs the UX treatment (see onboarding; interface-states) and sometimes a long opt-in period with both UIs alive.
- **Compliance and audit trails across the seam**: regulated data may require the old system's records retained, immutable, and *reachable* for years post-migration — "delete the old system" becomes "archive to a read-only, queryable form with a retention owner" (see authorization compliance edges).
- **Migrating a queue or event schema**: consumers at mixed versions read the topic — schema evolution rules (additive-only during transition, versioned envelopes) and per-consumer-group cutovers replace the router pattern (see event-driven schema evolution; async-processing).
- **Performance parity as a hidden requirement**: the new system is correct in shadow but 2× the latency — consumers with timeouts tuned to the old profile fail on cutover even though every byte matched (see optimization-method: pin the profile alongside the behavior; frontend-performance for the client-visible version).
- **The vendor-forced march**: EOL platform, hard external deadline — the strangler still applies, but slicing is ordered by *risk-of-missing-the-date* rather than learning; grandfathering options vanish, so the tail campaign starts on day one, in parallel, not at the end.
- **Migrating with the original team gone**: no survivors to interview — archaeology weight shifts to logs, tests-as-docs, and *the debugger as historian* (step through the weird branch with real inputs); budget the learning curve explicitly (see learning-new-stacks: reading unfamiliar code; the multiplier is real).

## Tradeoffs

- **Strangle vs rewrite**: the strangler pays continuous adapter/routing tax and always works; the rewrite pays nothing until it pays everything — route by seam-availability, edge-case density, and whether the business can pause features (it can't); when a true rewrite is warranted (dead platform, small honest scope), run it *as* a strangler anyway: slice-by-slice with shadow, not moonshot-then-switch.
- **Bug-for-bug fidelity vs cleanup opportunity**: preserving quirks costs grotesque code in the new system ("faithfully reimplementing the February null"); fixing them mid-migration risks silent consumer breakage — default to fidelity through the flip, cleanup as versioned follow-ups; the exception is quirks *no measured consumer exercises* (delete, with the measurement as receipt).
- **Shadow duration vs calendar**: longer windows catch rarer cycles (month-end, year-end) but hold the two-system tax open — match the window to the *slowest important cycle* of that slice, not to a uniform policy; billing shadows a quarter, the avatar service shadows a week.
- **Per-consumer routing granularity vs router complexity**: fine-grained routing de-risks cutovers and turns the router into its own legacy system — keep routing rules declarative, inventoried, and deleted aggressively post-cutover (the router special-case is an adapter with better PR).
- **Grandfathering vs finishing**: keeping the old path for three enterprise contracts converts the migration's last mile into a permanent product line — price it honestly (maintenance, on-call, security patching of the fossil) and charge or sunset accordingly; "free forever for the loudest customer" is how companies end up running four API versions (see product-thinking: the feature tax; technical-leadership for the negotiation).
- **Speed of tail enforcement vs relationship cost**: brownouts and hard deadlines flush holdouts fast and burn goodwill; infinite patience is free and never finishes — the calibration is consumer-by-consumer (internal teams get brownouts early; paying customers get white-glove migration help *then* deadlines), with the business owning the sharpest calls.

## Optimization Strategies

- Build migration infrastructure as a reusable asset: the traffic-mirroring rig, the diff engine, the reconciliation framework, idempotent backfill runners — the second migration on shared rails costs a third of the first (see platform thinking in system-design).
- Maintain the deprecation pipeline as a standing process: every surface gets usage metrics at birth, so "who still uses this?" is a dashboard, not a research project (see observability; api-design: instrument at the boundary from day one).
- Keep a migration ledger across the org: what moved, what it cost vs estimate, where the tail pain lived — the reference class that fixes the next migration's plan (see planning-and-estimation reference-class library).
- Rehearse the revert as part of each slice's definition of done — cutover and rollback are one skill, and only one of them gets practiced for free.
- Schedule "fossil hunts" quarterly: grep for adapters, dual-writes, and router rules past their deletion dates — the two-system tax is paid in fossils, and fossils are findable (see refactoring: dead code deletion).
- Write the "why the old system was weird" doc as you excavate — every archaeology finding recorded turns the next team's fence-check from a dig into a lookup (see technical-writing; first-principles constraint maps).

## Self Review

- Do I actually know who consumes this system — from measurement, or from the same folklore that's about to get someone paged?
- Which behaviors have I pinned with characterization tests — and which am I about to change without knowing I'm changing them?
- Is my first slice representative, or did I pick the easy corner and defer all the learning?
- What does the shadow diff say — and has it run through the rare cycles, or just through a quiet Tuesday?
- Can I revert the current stage in minutes, and when did I last prove that?
- Am I bundling a behavior fix, a redesign, or a feature into a migration flip — and which incident will that cost me?
- Who owns the tail, what's the holdout inventory, and what date does the old system *die*?
- If this migration paused today, would it rest at a stable point — or fossilize into the two-system trap?
- Honestly: is my rewrite urge evidence-backed, or is it the death spiral's opening move?

## Examples

**1. The billing engine strangled, not rewritten.**
A 9-year-old billing monolith — no tests, departed authors, every invoice quirk a mystery — needs usage-based pricing it can't express. The rewrite proposal (12 months, clean slate) fails the interrogation: seams exist (all billing flows through one internal API), and the edge-case swamp is demonstrably deep (200+ special-case branches, each with an incident number). Instead: facade at the internal API (seam), characterization tests from 10k real invoices replayed (three "bugs" found and *preserved* — one was load-bearing for a partner's reconciliation), then capability-by-capability strangling: proration first (shadowed for one full billing cycle — the diff caught a leap-year branch no one knew existed), then discounts, then the new usage-based engine as a *new* capability on the new side only. Eleven months total, features shipping the whole time, old engine deleted at month twelve — with a funeral in the team channel.

**2. The death spiral, survived by amputation.**
A team is 14 months into a v2 rewrite (original estimate: 6). v1 has taken 30 features meanwhile; v2's parity checklist *grows* monthly; both systems are on-call surfaces. New lead runs the honest accounting: v2 has better architecture and 60% parity; at current divergence rate, parity arrives never (see the burn-down heuristic — theirs pointed up). Decision: stop chasing parity — invert the relationship. v2's genuinely-superior core (the pricing calculator) is extracted and *strangled into v1* behind a facade; the rest of v2 is deleted — 14 months of code, one week of grief. The pricing module ships value in six weeks. The postmortem's finding: the death spiral's exit is rarely "finish the rewrite" and never "keep chasing" — it's "salvage the best organ and bury the body" (see convergent-evaluation: sunk cost is not a criterion).

**3. Expand-migrate-contract under live fire.**
User profiles move from a document store to Postgres (see postgres) with zero downtime and 40M rows. Expand: Postgres schema up, dual-write behind a flag, reconciliation job diffing both sides hourly. Backfill: idempotent, checksummed batches, throttled to protect production, resumable (it was interrupted twice — a deploy and a regional failover; resumability was not optional). The reconciler surfaces a class of ambiguity: 12k rows with a `country` field that's sometimes a code, sometimes free text ("USA", "us", "United Staes") — triaged as classes: rule-fixable (mapped), ambiguous (product owner picks the rule), garbage (archived with paper trail). Reads flip per-tenant over two weeks, write authority flips per-shard over one more, old store contracts to a read-only archive for the compliance window, then dies. Total diff-caught incidents: zero. Total "migration weekend"s: zero.

**4. The tail campaign that actually finished.**
An API v1→v2 migration hits the classic wall: 94% of traffic moved in eight weeks; the last 6% is 41 consumers. Instead of victory-and-abandon: a named tail owner, and an inventory from gateway logs (see observability) classifying every holdout. Findings: 11 integrations with zero owner (deleted after brownouts flushed no complaints — they were dead), 19 friendly-but-inert (white-glove migration help, two-week deadlines, done in a month), 8 internal crons (tickets on the owning teams, escalated once — see technical-leadership), and 3 enterprise contracts pinning v1 *contractually*. The three go to the business with a price tag: maintaining v1 for them costs $X/quarter in on-call and patching. Business buys out one contract, charges one, and eats one with a renewal-date sunset written into the new contract. v1 dies fourteen months after "94% done" — which is fast; the unowned version of this tail is immortal.

## Evaluation Rubric

Score 1–10:

- **1–2**: Rewrite by default; no characterization, no consumer inventory; big-bang cutovers; behavior "fixes" bundled silently; migrations declared done at 90% and abandoned; two-system fossils everywhere.
- **3–4**: Incremental in name (a router exists) but slices cut for ease, shadow skipped ("tests pass"), tail unplanned; adapters undated; the old system lingers unowned.
- **5–6**: Characterization over changed surfaces; strangler routing with revertible slices; shadow or dual-write comparison before cutovers; expand-migrate-contract for data; a burn-down that shrinks.
- **7–8**: Full checklist: measured consumer inventory, representative-first slicing, rare-cycle shadow windows, one-variable flips, owned tail campaign with per-holdout strategies, old system actually deleted.
- **9–10**: Additionally: migration infrastructure reused across projects; deprecation metrics standing from birth of every surface; a migration ledger feeding estimates; fossil hunts on calendar; at least one rewrite urge on record converted to a strangler (or one death spiral exited by honest salvage) — and funerals held, because deletion is the definition of done.
