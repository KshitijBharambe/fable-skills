# Refactoring & Legacy Migrations

## Purpose

Change structure without changing behavior, at two scales. **Code scale**: refactor in steps small enough that nothing is ever broken for long — smells as symptoms (not sins), refactoring in service of a goal rather than aesthetics, debt as a portfolio with interest rates instead of a guilt list. **System scale**: change systems you didn't build and can't fully know — pin behavior with characterization tests, replace incrementally via strangler and shadow patterns, survive the two-system period, finish the long tail — while resisting the rewrite death spiral that has consumed better teams than yours.

## When to use

- A feature or fix is hard because the code's current shape resists it ("make the change easy, then make the easy change").
- The same bug family keeps recurring in one area; the third duplicate of some logic just appeared.
- Before extending code you don't fully understand — refactoring as the highest-bandwidth way to *learn* code.
- Inheriting a system with thin tests, thinner docs, and departed authors — and needing to change it anyway.
- Any migration: database engine, framework, service extraction, vendor swap, "v1 to v2."
- When "let's just rewrite it" enters the room (especially when you're the one saying it).
- When a previous migration stalled at 60% and you've inherited *two* systems.
- Explicitly *not*: the week before a deadline on untested code, or as a standalone "cleanup project" with no behavioral goal.

## Goals

- Behavior provably preserved: tests green at every step, each step committable, red steps reverted not debugged forward.
- Every refactor serves a named beneficiary: the next feature, the recurring bug family, the onboarding engineer.
- Structure and behavior changes never mixed in one commit; one variable per migration cutover.
- Replacements shipped incrementally: every step reversible, mainline always serving real traffic, correctness proven by shadow comparison against production reality.
- Debt tracked as a portfolio: high-interest debt (touched weekly) paid down; low-interest debt consciously held.
- The long tail planned as its own phase with its own owner — and the old system *deleted* at the end.

## Inputs

- The upcoming change, bug family, or comprehension problem the structural work serves.
- Churn data (`git log` frequency × defect density) — the map of where structure work pays.
- For migrations: consumer inventory from measurement (traffic, callers), incident history, the weird branches and their archaeology.
- Existing test coverage over the surgery zone; seams (or their absence).

## Outputs

- Structure commits verifiably behavior-neutral; behavior commits small and deliberate.
- Characterization tests pinning current behavior, weirdness annotated ("null for pre-2019 accounts — preserved deliberately").
- For migrations: a seam, per-capability slices with rehearsed rollback, shadow-diff logs, a shrinking burn-down of the old side, a tail campaign with owner and deadlines.
- A debt register that's a priced portfolio, not a guilt list — held items have triggers, paid items get closed.

## Expert Mental Model

**Code scale:**

- **Refactoring is defined by an invariant, not an intention.** If observable behavior might have changed, it wasn't a refactor — it was an edit wearing the word. The discipline: tests that pin current behavior *before* surgery, steps so small each is trivially checkable, and the rule that a red test means *revert the step*, not debug forward. Experts move in absurdly small steps precisely because it makes courage unnecessary.
- **"Make the change easy, then make the easy change."** Structure work is justified by the behavior change it enables — which also supplies the prioritization function: refactor where change is *about to happen*, not where the code offends you. Ugly-but-stable code nobody touches has near-zero carrying cost.
- **Smells are symptoms with differential diagnoses.** Long method, feature envy, shotgun surgery (one concept change → nine files), divergent change (one file, nine unrelated reasons), data clumps — each *suggests* a hidden structure wanting out (see abstraction-and-simplicity). But smells earn investigation, not automatic surgery: the "duplicate" that will diverge next quarter is coincidence, not duplication.
- **Duplication is cheaper than the wrong abstraction.** The most expensive failure is premature unification: two similar paths merged under one parameterized abstraction that grows flags as the paths diverge — until every caller pays for every other caller's needs. The rule of three exists because three instances reveal *which parts actually vary*; two invite guessing, and guessed abstractions are load-bearing guesses.
- **Technical debt is a portfolio with interest rates.** Interest = the ongoing tax (slower changes, recurring bugs); principal = the cost to fix. High-churn + high-pain → pay down now, attached to feature work. Zero-churn + working → hold forever, honorably. Deliberate debt with a documented paydown trigger is a financing decision; the toxic kind is the unrecorded loan nobody knows the team is servicing.
- **Structure diffs and behavior diffs are different documents.** A commit that reshapes *and* changes logic is unreviewable and unbisectable (see code-review). Sequence: refactor commits (mechanical, "no behavior change," tests untouched and green), then behavior commits (small, tests changed deliberately).

**System scale:**

- **Legacy code is code whose behavior you can't cheaply verify — and the behavior is the spec.** Docs lie, comments lie; only the running system tells the truth, and consumers depend on *that truth, including its bugs*. The foundational move is the **characterization test**: feed real inputs, record real outputs, assert *those* — not what "should" happen. When one surprises you ("it returns null for February?!"), that's the method working: you found a behavior somebody depends on. Fix-or-preserve is a *decision with an owner*, never a silent side effect.
- **The rewrite death spiral, memorized as a vaccine.** The rewrite starts clean and fast; the old system keeps taking features (business doesn't pause), so v2 chases a moving target; the "easy 80%" ships in months, then v2 hits the swamp of edge cases that *were the actual system* — each weird branch a customer, an incident, a regulation; the team maintains two systems while shipping in neither; v2 launches partial or never. The root error is epistemic: **old complexity mistaken for accident when most of it is undocumented requirements.** Rewrites are occasionally right (dead platform, no seams, trivial scope) — but the burden of proof is on the rewrite, and "the code is ugly" is not proof (see first-principles).
- **Strangler fig: replace by routing, not by switchover.** An interception layer in front of the old system; build the replacement one capability at a time; move traffic per-capability; the old system atrophies until deletion. Every increment small, independently shippable, revertible in seconds. Branch-by-abstraction is this pattern at code scale; the strangler converts a bet-the-company cutover into a hundred boring deploys (see ci-cd).
- **Shadow mode proves correctness against reality.** Mirror production traffic to old and new; serve users from old; *diff the outputs*. Every mismatch is a new-system bug (fix) or an undocumented old behavior (decide: preserve or formally change). Ship only when the diff rate is ~zero *over a window long enough to include the rare paths* (month-end billing, the annual job). For writes, invert: dual-write with old as source of truth, reconcile asynchronously, promote when reconciliation stays clean (see postgres).
- **The two-system period is the tax; budget and time-box it.** Dual patterns, dual on-call, adapters, "which system owns this?" in every incident. Unavoidable — the failure is treating it as free or letting it become permanent. The stalled migration is *worse than either endpoint*: all of the tax, none of the payoff, forever. Drive the window ruthlessly short per capability; keep a visible burn-down; treat "90% done" with the suspicion any 90% deserves (see planning-and-estimation).
- **The long tail is the migration.** Moving 95% takes weeks; the last 5% takes quarters and is where migrations die: locked accounts, the enterprise contract pinning the old API, malformed rows from a 2017 bug, the cron nobody owns. Plan the tail as a distinct phase: named owner, measured inventory, per-holdout strategies, and *done = old system deleted*.

## Workflow

**Code-scale refactor:**

1. **Name the beneficiary** — which change, bug family, or comprehension problem this serves. Write it in the PR; "cleanup" is not a beneficiary.
2. **Pin current behavior**: run existing tests; where coverage is thin over the surgery zone, add characterization tests first (see testing-strategy for their quality).
3. **Plan the step sequence** as named, catalogued moves (extract, inline, move, rename, replace-conditional-with-polymorphism) — each independently green-to-green.
4. **Execute one step**: smallest possible; green → commit; red → *revert the step* and cut it smaller. Prefer IDE/language-server transforms wherever one exists — automated moves carry guarantees hand-editing can't.
5. **Stop at the beneficiary's doorstep**: when the intended change is easy, make it — in its own behavior commit — and *stop refactoring*. The further reshape you can now see goes in the debt register, priced.
6. **For refactors that can't be atomic**: branch by abstraction — introduce a seam, move callers one by one, delete the old side; mainline always green.

**System-scale migration:**

7. **Archaeology before surgery**: read the code where it's hot, the incident history, the weird branches; interview survivors; inventory consumers — every caller, cron, report, and Excel macro.
8. **Instrument the old system first** (see observability): usage per endpoint/feature, callers identified. You'll usually find 30% of the surface has zero traffic — deletion candidates before migration starts.
9. **Characterize the surfaces you'll change**; route surprises to owners as preserve-or-fix decisions.
10. **Find or create the seam** (gateway, facade, DNS, queue); no seam = build the seam first.
11. **Slice by capability, ordered by risk-and-learning**: first slice thin but end-to-end and *representative* — a walking skeleton through the new path, not the easiest corner.
12. **Shadow before serving**: mirror traffic, diff outputs, run the mismatch triage loop; drive diffs to ~zero across a window covering the rare cycles. Cut over progressively (1% → 10% → 50% → 100%) with rollback rehearsed at each stage.
13. **Migrate data with expand-migrate-contract**: new schema added (expand), dual-write with reconciliation, backfill in throttled idempotent checksummed batches, reads flipped gradually, then old side removed (contract) — never a stop-the-world migration weekend.
14. **Run the tail campaign**: holdout inventory, per-holdout owner and strategy, deadlines with dates and migration support, grandfathering only as a *priced decision*. Then **delete**: code, adapters, dual-writes, router rules, docs. Deletion is the definition of done.

## Decision Tree

- If the change you need is hard because of code shape → refactor first, then change; if the deadline can't absorb it → make the change minimally, log the debt with a trigger, and *actually schedule it*.
- If there are no tests over the surgery zone → behavior checkable: write characterization tests first (this *is* the refactor's first half); not cheaply checkable: find the seam, extract the untestable edge, test the core — or downgrade to tool-automated mechanical moves only.
- If you see duplication → two instances: wait and note; three: extract, letting the three reveal what varies; already-abstracted-and-growing-flags: consider *inlining back* to duplicates and re-splitting along the real seam.
- If a behavior bug surfaces mid-refactor → stop; finish-then-fix (usually) or revert-and-fix (if urgent) — never fix *inside* the refactor commits.
- If the refactor keeps growing ("while I'm here…") → land what's green, re-queue the rest as new items with their own beneficiaries.
- If tempted to rewrite → interrogate: Is the platform actually dead? Truly no seam (and can't one be built)? Scope genuinely small *including the edge-case swamp you haven't inventoried*? Two-plus evidence-backed yeses → rewrite a *thin slice* first as proof; otherwise strangle.
- If characterization reveals a bug consumers may rely on → preserve it through the migration (bug-for-bug), file the fix as its own versioned change — never bundle behavior fixes into cutovers.
- If old and new disagree in shadow → old is innocent until proven guilty: assume the new side is wrong first (it usually is).
- If the migration must pause → pause at a *stable* point: a capability fully on one side, adapters minimal, burn-down documented — never mid-capability with unreconciled dual-writes.
- If a previous stalled migration is discovered → finishing it almost always beats starting a third pattern; three patterns is worse than one mediocre one.
- If a holdout won't move → classify: *can't* (missing feature — build it), *won't-yet* (inertia — deadline plus white-glove help), *won't-ever* (contract/economics — escalate to the business: grandfather with a price tag or buy out; a business decision wearing a technical costume).
- If deadline pressure says "skip shadow mode" → shrink the slice until shadow fits; the shadow week is cheaper than the incident *and* the trust repair.

## Heuristics

- Steps should be so small they're boring — if a step needs courage, cut it in half; if it needs a plan document, it's a migration.
- Rename first: the cheapest, highest-yield refactor is making names tell the truth — half the "restructuring" urge dissolves once parts are honestly labeled.
- Follow the churn, not the smell: `git log` frequency × bug density is the map; aesthetics is not a heat map.
- The Boy Scout rule has a radius: leave code you *touch* slightly better — but the campsite is the diff, not the forest.
- Delete before you organize: dead code, unused flags, commented-out blocks — deletion is the refactor with no risk of wrong abstraction.
- Test churn during "pure refactor" is a smell about the tests: structure-coupled tests break on every reshape — refactor toward testing the surface (see testing-strategy).
- Price debt in the currency stakeholders spend: "this area's bugs cost ~2 engineer-weeks per quarter" moves roadmaps; "the code is ugly" moves nothing.
- The weird branch is a requirement wearing a disguise: every `if account_type == 7` was somebody's outage, contract, or regulator — archaeology before deletion.
- Measure before you migrate: the endpoint with zero calls in 90 days doesn't get migrated, it gets deleted.
- Old system is source of truth until the new one has *earned* it in shadow — the burden flips by diff rate, never by calendar.
- One variable per cutover: migrate *or* fix behavior *or* add features — never two in the same flip.
- Keep the revert warm: rollback rehearsed per stage; a revert that hasn't run in six weeks is a hypothesis.
- The adapter you write "temporarily" needs a deletion ticket the day it's born, or it outlives you.
- Watch the burn-down, not the burn-up: "capabilities remaining on old" trending to zero is the honest metric.
- Deprecation comms follow 3-2-1: announced with dates and alternatives, warned in-band to *measured* users, then enforced with brownouts before shutoff — brownouts find the consumers your inventory missed (see api-design).
- If nobody owns the migration end-to-end, the two-system period is permanent — a named owner with the deletion date in their goals is the difference between a migration and a hobby.

## Quality Checklist

- [ ] Beneficiary named; behavior pinned before surgery (characterization where thin).
- [ ] Every step green-to-green; red steps reverted, not debugged forward.
- [ ] Structure commits and behavior commits separated; each message says which it is.
- [ ] No new abstraction from fewer than three instances without a written reason; scope held, leftovers registered.
- [ ] Consumer inventory built from measurement, not memory; surprises annotated and routed as decisions.
- [ ] Seam exists; every increment independently shippable and revertible in minutes; first slice representative, not easy.
- [ ] Shadow/dual-write comparison ran across a window covering rare cycles; diff rate ~zero before each cutover.
- [ ] Behavior fixes decoupled from migration flips; data moves via expand-migrate-contract with idempotent, resumable, checksummed backfills.
- [ ] Two-system tax visibly budgeted; burn-down maintained and shrinking.
- [ ] Tail phase has an owner, inventory, per-holdout strategies, communicated deadlines.
- [ ] Debt register is a priced portfolio with triggers; old systems actually deleted — "done" not declared before the funeral.

## Failure Modes

- **The refactor that changed behavior**: "just restructuring" that quietly fixed—or broke—an edge case consumers depended on; the invariant was asserted, never verified.
- **Big-bang restructure**: three weeks on a branch, unmergeable against a moved mainline, abandoned — the sunk-cost museum piece every team has one of.
- **Premature abstraction**: two similar functions unified on resemblance; six months later the "shared" code is a flag-forest.
- **Scope ratchet**: "while I'm here" applied recursively; the one-hour extract becomes a nine-file PR nobody can review.
- **Refactor-and-fix soup**: behavior fixes threaded through structural commits — the reviewer can't find the logic change, the bisect can't isolate the regression.
- **The guilt-list debt register**: every imperfection logged, nothing priced, nothing triggered — a shame archive; unranked debt is unpayable debt.
- **The rewrite death spiral**: v2 chases the moving v1, drowns in the edge-case swamp, launches partial or never; the org runs two systems or zero morale.
- **The two-system trap**: migration stalled at 60%, team reassigned, adapters fossilized — permanent double tax, no payoff.
- **Silent behavior "fixes"**: the migration "cleans up" the null-for-February quirk; the downstream billing report that *keyed on it* corrupts quietly for a quarter.
- **Test-suite overconfidence**: unit tests green on the new side, shadow skipped — production traffic contained the twelve input shapes the tests never imagined.
- **Tail abandonment**: 95% migrated, victory declared, team disbanded — the old system runs *forever* for 5% of traffic at 100% of its maintenance cost.
- **Unowned deprecation**: the sunset announced, never enforced — consumers rationally ignore deadlines that have slipped twice.

## Edge Cases

- **Refactoring at a public boundary**: internal reshaping is free; anything touching a published API, event schema, or wire format is a *migration* with versioning and consumers, however small the diff (see api-design; event-driven).
- **Performance-sensitive paths**: "cleaner" allocations or extra indirection change the profile — pin performance with a benchmark alongside the tests (see optimization-method). Performance parity is a hidden migration requirement too: correct-in-shadow but 2× latency fails consumers whose timeouts were tuned to the old profile.
- **Refactoring concurrent code**: reordering "equivalent" statements changes interleavings; extraction moves work across lock boundaries; test suites rarely pin races (see concurrency-bugs) — treat lock-scoped regions as no-fly zones for casual reshaping.
- **Shared code with invisible consumers**: the "unused" parameter fed by a caller in another repo; the partner's cron hitting the old IP; the 2021 mobile app version pinned by slow-updating users — search all consumers; measured inventory catches most, brownouts catch the rest; app-store realities mean some tails run on year scales.
- **Refactoring the tests themselves**: same discipline, inverted safety — the production code now pins *their* behavior; a deliberately broken assertion should fail, or the test was dead.
- **Migrating data models under live writes**: dual-write windows create ordering and conflict edges; reconciliation must be directional and idempotent; flip *write* authority per-tenant or per-shard, never globally (see postgres; concurrency-bugs).
- **Compliance across the seam**: regulated data may require the old system's records retained, immutable, and reachable for years — "delete the old system" becomes "archive to read-only queryable form with a retention owner" (see compliance-and-privacy).
- **Migrating a queue or event schema**: consumers at mixed versions read the topic — additive-only evolution during transition, versioned envelopes, per-consumer-group cutovers replace the router pattern (see event-driven).
- **The system that is also a product surface**: users see the old UI's quirks as features — machine parity is diffable; human parity needs the UX treatment and sometimes a long opt-in period with both UIs alive.
- **Original team gone**: archaeology shifts to logs, tests-as-docs, and the debugger as historian; budget the learning curve explicitly (see learning-new-stacks).

## Tradeoffs

- **Refactor-first vs ship-first**: reshaping first is cleaner but delays visible progress; minimal-change-now compounds the mess — route by interest rate and deadline reality, and log whichever debt you take *on purpose*.
- **Duplication vs abstraction**: duplication costs sync-maintenance; abstraction costs coupling and generality tax — the rule of three arbitrates; the tie-break is divergence likelihood.
- **Incremental vs atomic**: branch-by-abstraction keeps mainline green but carries dual-shape overhead; atomic is cleaner and only safe when small — threshold ≈ "can this land green in a day."
- **Strangle vs rewrite**: the strangler pays continuous routing tax and always works; the rewrite pays nothing until it pays everything — and when a true rewrite is warranted, run it *as* a strangler anyway: slice-by-slice with shadow, not moonshot-then-switch.
- **Bug-for-bug fidelity vs cleanup**: preserving quirks costs grotesque code; fixing them mid-migration risks silent breakage — default to fidelity through the flip, cleanup as versioned follow-ups; exception: quirks *no measured consumer exercises* (delete, with the measurement as receipt).
- **Shadow duration vs calendar**: longer windows catch rarer cycles but hold the two-system tax open — match the window to the slowest important cycle of that slice: billing shadows a quarter, the avatar service a week.
- **Grandfathering vs finishing**: keeping the old path for three enterprise contracts converts the last mile into a permanent product line — price it honestly and charge or sunset; "free forever for the loudest customer" is how companies run four API versions.
- **Boy-scouting vs diff purity**: opportunistic cleanups improve the codebase and pollute the diff — keep them waveable-through or split into a preceding structure commit.

## Optimization Strategies

- Mine churn data quarterly: file-frequency × defect density → the top-ten paydown map, usually shockingly concentrated.
- Build refactoring into estimation: feature estimates in hot areas include their enabling refactor by default (see planning-and-estimation).
- Invest in the safety infrastructure that makes small steps cheap: fast test suite, automated transforms, trunk-based flow (see ci-cd) — refactoring frequency is downstream of refactoring *cost*.
- Build migration infrastructure as a reusable asset: traffic-mirroring rig, diff engine, reconciliation framework, idempotent backfill runners — the second migration on shared rails costs a third of the first.
- Maintain the deprecation pipeline as standing process: every surface gets usage metrics at birth, so "who still uses this?" is a dashboard, not a research project.
- Keep a migration ledger: what moved, cost vs estimate, where the tail pain lived — the reference class that fixes the next migration's plan.
- Schedule quarterly fossil hunts: grep for adapters, dual-writes, and router rules past their deletion dates.
- Practice un-abstracting: the occasional inline-back of a flag-grown abstraction keeps the codebase honest — teams that only add abstraction ratchet toward frameworks.

## Self Review

- Who benefits from this refactor, concretely — and would they agree it served them?
- What pins the behavior I'm about to reshape — and have I watched those tests fail, or just pass?
- Can a reviewer tell my structure commits from my behavior commits without asking me?
- Am I abstracting from three real instances, or from two and a prophecy?
- Did I stop when the change became easy — or am I still going because momentum feels like progress?
- Do I know who consumes this system — from measurement, or from the folklore that's about to get someone paged?
- Is my first slice representative, or did I pick the easy corner and defer all the learning?
- What does the shadow diff say — and has it run through the rare cycles, or just a quiet Tuesday?
- Am I bundling a behavior fix, a redesign, or a feature into a migration flip — and which incident will that cost me?
- Who owns the tail, and what date does the old system *die*? If this paused today, stable point or fossil?
- Honestly: is my rewrite urge evidence-backed, or the death spiral's opening move?

## Examples

**1. Make the change easy: the pricing engine.**
Task: add regional tax rules to checkout. The change is hard — pricing logic smeared across a controller, two helpers, and a template. First a pure-structure PR: characterization tests pin current totals for 30 real carts (including discounts + gift cards), then extract a `PricingPolicy` owning the whole computation; behavior byte-identical, tests untouched and green. Then the behavior PR: regional tax lands as ~40 lines in one place. Two reviewable diffs, one afternoon each — versus the 400-line mixed PR with a tax bug hiding in a "harmless" restructure.

**2. The rule of three, honored in both directions.**
Two report exporters (CSV, PDF) look 70% similar; the tempting `BaseExporter` waits. The third (Excel) arrives and reveals the real seams: row *generation* is genuinely shared (extracted cleanly), formatting and pagination are not (left separate — PDF's pagination would have poisoned the base class with flags). Meanwhile the cautionary twin: a `BaseSyncJob` abstracted from two instances years ago, now sprouting `if self.kind == 'inventory'` branches — scheduled for inline-back-and-resplit using the same green-to-green discipline.

**3. The billing engine strangled, not rewritten.**
A 9-year-old billing monolith — no tests, departed authors — needs usage-based pricing it can't express. The rewrite proposal (12 months, clean slate) fails the interrogation: seams exist (all billing flows through one internal API) and the edge-case swamp is demonstrably deep (200+ special-case branches, each with an incident number). Instead: facade at the API, characterization from 10k real invoices replayed (three "bugs" found and *preserved* — one was load-bearing for a partner's reconciliation), then capability-by-capability strangling: proration first, shadowed for one full billing cycle — the diff caught a leap-year branch no one knew existed. Eleven months, features shipping the whole time, old engine deleted at month twelve — with a funeral in the team channel.

**4. The death spiral, survived by amputation.**
A team is 14 months into a v2 rewrite (estimate: 6). v1 has taken 30 features meanwhile; v2's parity checklist *grows* monthly. Honest accounting: at current divergence rate, parity arrives never. Decision: stop chasing — invert. v2's genuinely-superior core (the pricing calculator) is extracted and *strangled into v1* behind a facade; the rest of v2 is deleted — 14 months of code, one week of grief. The salvaged module ships value in six weeks. The death spiral's exit is rarely "finish the rewrite" — it's "salvage the best organ and bury the body" (see brainstorming: sunk cost is not a criterion).

**5. The tail campaign that actually finished.**
API v1→v2: 94% of traffic moved in eight weeks; the last 6% is 41 consumers. A named tail owner classifies every holdout from gateway logs: 11 integrations with zero owner (brownouts flushed no complaints — dead, deleted), 19 friendly-but-inert (white-glove help, two-week deadlines, done in a month), 8 internal crons (tickets, one escalation), 3 enterprise contracts pinning v1 *contractually* — sent to the business with a price tag. Business buys out one, charges one, eats one with a renewal-date sunset. v1 dies fourteen months after "94% done" — which is fast; the unowned version of this tail is immortal.

## Evaluation Rubric

Score 1–10:

- **1–2**: "Refactors" routinely change behavior; no tests before surgery; structure and logic mixed; rewrite by default; big-bang cutovers; behavior fixes bundled silently; two-system fossils everywhere; debt untracked or a guilt list.
- **3–4**: Tests exist but aren't run per-step; abstractions from two instances; prioritization by aesthetics; migrations incremental in name only — slices cut for ease, shadow skipped, tail unplanned, old systems lingering unowned.
- **5–6**: Behavior pinned first; green-to-green with revert-on-red; structure/behavior commits separated; strangler routing with revertible slices; shadow before cutovers; expand-migrate-contract for data; a burn-down that shrinks.
- **7–8**: Full checklist: churn-driven prioritization, branch-by-abstraction, measured consumer inventory, representative-first slicing, rare-cycle shadow windows, one-variable flips, owned tail campaigns, debt portfolio priced with triggers, old systems actually deleted.
- **9–10**: Additionally: refactoring priced into estimates by default; migration infrastructure reused across projects; deprecation metrics standing from birth of every surface; a migration ledger feeding estimates; un-abstracting practiced; at least one rewrite urge on record converted to a strangler — and funerals held, because deletion is the definition of done.
