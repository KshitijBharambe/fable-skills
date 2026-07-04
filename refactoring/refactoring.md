# Refactoring

## Purpose

Change code structure without changing behavior, in steps small enough that nothing is ever broken for long — reading smells as symptoms (not sins), refactoring in the service of a goal rather than as aesthetics, and managing technical debt as a portfolio with interest rates instead of a guilt list.

## When to use

- A feature or fix is hard to make because the code's current shape resists it ("make the change easy, then make the easy change").
- The same bug family keeps recurring in one area; the third duplicate of some logic just appeared.
- Before extending code you don't fully understand — refactoring as the highest-bandwidth way to *learn* code.
- During review, when a change works but deepens a structural problem.
- Explicitly *not*: the week before a deadline on untested code, or as a standalone "cleanup project" with no behavioral goal in sight (see the tradeoffs).

## Goals

- Behavior provably preserved: tests green at every step, each step seconds-to-minutes in size, committable at any moment.
- The refactor serves a named beneficiary: the next feature, the recurring bug family, the onboarding engineer — not abstract beauty.
- Smells treated as diagnostics that earn investigation, with the fix priced against the change-frequency of the code.
- Debt tracked as a portfolio: high-interest debt (touched weekly) paid down; low-interest debt (stable, working, untouched) consciously held.
- Structure and behavior changes never mixed in one commit — reviewers always know which kind of diff they're reading.

## Expert Mental Model

- **Refactoring is defined by an invariant, not an intention.** If observable behavior might have changed, it wasn't a refactor — it was an edit wearing the word. The discipline that makes the invariant real: tests that pin current behavior *before* structural surgery (characterization tests when none exist — see legacy-migrations characterization), steps so small each one is trivially checkable, and the rule that a red test means *revert the step*, not debug forward. Experts move in absurdly small steps precisely because it makes courage unnecessary.
- **"Make the change easy, then make the easy change."** Refactoring's economic engine: structure work is justified by the behavior change it enables. Facing a hard change, the expert first reshapes the code so the change becomes natural (rename, extract, move, invert a dependency), *then* makes it — two clean phases instead of one entangled fight. This also supplies the prioritization function: refactor where change is *about to happen*, not where the code offends you. Ugly-but-stable code that nobody touches has near-zero carrying cost (see the debt portfolio below).
- **Smells are symptoms with differential diagnoses, not sins with penalties.** Long method, feature envy (a method more interested in another object's data than its own), shotgun surgery (one concept change → edits in nine files), divergent change (one file edited for nine unrelated reasons), primitive obsession, data clumps that travel together — each *suggests* a hidden structure wanting out (usually a missing abstraction or a misplaced responsibility — see abstraction-and-simplicity). But smells earn investigation, not automatic surgery: the "duplicate" code that will diverge next quarter is not duplication, it's coincidence (see the rule-of-three); the long function that reads top-to-bottom like a recipe may beat its exploded version.
- **Duplication is cheaper than the wrong abstraction.** The most expensive refactoring failure is premature unification: two similar-looking code paths merged under one parameterized abstraction, which then grows flags and branches as the paths diverge — until every caller pays the complexity of every other caller's needs. The rule of three (tolerate two, refactor on the third — see abstraction-and-simplicity rule-of-three) exists because three instances reveal *which parts actually vary*; two instances invite guessing, and guessed abstractions are load-bearing guesses.
- **Technical debt is a portfolio with interest rates, and the metaphor is load-bearing.** Interest = the ongoing tax a structural problem levies (slower changes, recurring bugs, onboarding drag). Principal = the cost to fix. The expert asks per-item: what's the interest *rate* (how often is this code touched, how badly does it hurt each time — git churn data answers this), and does paying principal beat paying interest? High-churn + high-pain → pay down now, attached to feature work. Zero-churn + working → hold the debt forever, honorably. Deliberate debt taken with eyes open (ship now, documented, with a paydown trigger) is a financing decision; the toxic kind is the unrecorded loan nobody knows the team is servicing (see planning-and-estimation: the invisible drag).
- **Structure diffs and behavior diffs are different documents.** A commit that renames, moves, and reshapes *and* changes logic is unreviewable — the reviewer can't see the behavior change inside the noise (see code-review: diff hygiene). Experts sequence: refactor commits (large, mechanical, "no behavior change" — verifiable by tests untouched and green), then behavior commits (small, meaningful, tests changed deliberately). This is also the safety story: a mechanical-refactor commit that breaks something is bisectable in minutes (see production-debugging: what changed).

## Workflow

1. **Name the beneficiary**: which upcoming change, bug family, or comprehension problem does this refactor serve? Write it in the ticket/PR — "cleanup" is not a beneficiary.
2. **Pin current behavior**: run the existing tests; where coverage is thin over the surgery zone, add characterization tests first — tests that assert what the code *does* (including its weird cases), not what it should do (see legacy-migrations characterization; enforce-first for their quality).
3. **Plan the step sequence**: decompose the reshape into named, catalogued moves (extract function, inline, move method, rename, replace conditional with polymorphism, introduce parameter object) — each independently green-to-green.
4. **Execute one step**: smallest possible; run tests. Green → commit (or checkpoint). Red → *revert the step* and take a smaller one; debugging forward inside a refactor is how refactors become incidents.
5. **Lean on the tools**: IDE renames/extractions and language servers do mechanical steps with guarantees hand-editing can't match — prefer the automated transform wherever one exists.
6. **Re-assess after each landing**: the code teaches as it moves; the plan from step 3 is a hypothesis, and step 7's shape often only becomes visible after step 4 lands.
7. **Stop at the beneficiary's doorstep**: when the intended change is now easy, make it — in its own behavior-change commit — and *stop refactoring*. The perfect further reshape you can now see goes in the debt register, priced, not in this PR.
8. **For large refactors that can't be atomic**: keep both shapes working in parallel — branch by abstraction (introduce a seam, move callers over one by one, delete the old side) — so the mainline is always green and the refactor ships incrementally (see legacy-migrations strangler: the same pattern at architecture scale; ci-cd: no long-lived branches).
9. **Record the debt decisions**: what you fixed, what you consciously left, and the trigger that would reopen it (see technical-writing decision docs) — the register is what keeps "we should clean this up someday" from being the team's entire debt strategy.

## Decision Tree

- If the change you need is hard because of code shape → refactor first (beneficiary named), then change; if the deadline genuinely can't absorb the refactor → make the change minimally, log the debt with a trigger, and *actually schedule it* (see judgment-under-uncertainty: deliberate debt is a financing decision).
- If there are no tests over the surgery zone →
  - Behavior is checkable → write characterization tests first; this is not optional prelude, it *is* the refactor's first half.
  - Behavior isn't cheaply checkable (deep I/O entanglement) → find the seam, extract the untestable edge, test the core (see legacy-migrations seams) — or downgrade ambition to tool-automated mechanical moves only.
- If you see duplication → count instances: two → wait (note it); three → extract, letting the three reveal what varies; already-abstracted-and-growing-flags → consider *inlining back* to duplicates and re-splitting along the real seam (un-abstracting is a refactor too — see abstraction-and-simplicity).
- If one change requires edits in many files (shotgun surgery) → the concept those edits share wants a home; introduce it where the churn concentrates.
- If one file changes for many unrelated reasons (divergent change) → it's several modules cohabiting; split along the reasons-to-change (see component-architecture; system-design: same axis, different altitude).
- If the smell lives in code with near-zero churn → record and leave; interest rate ≈ 0 (the *except*: it's a comprehension trap that keeps burning on-call — that's churn of a different currency; see production-debugging).
- If mid-refactor a behavior bug surfaces → stop; decide explicitly: finish the refactor then fix (usually), or revert and fix first (if urgent) — never fix *inside* the refactor commits (the invariant, and the bisect, both die).
- If the refactor keeps growing ("while I'm here…") → the scope ratchet is the failure shape; land what's green, re-queue the rest as new items with their own beneficiaries.
- If someone proposes a "refactoring sprint/project" with no behavioral deliverable → counter with attaching paydown to the next quarter's feature work in that area — refactoring travels safest as a passenger, not as the vehicle (see the tradeoffs).

## Heuristics

- Steps should be so small they're boring — if a step needs courage, cut it in half; if it needs a plan document, it's a migration (see legacy-migrations).
- Commit at every green; a refactor you can abandon at any commit with value retained is a refactor with no sunk-cost hostage.
- Rename first: the cheapest, highest-yield refactor is making names tell the truth (see abstraction-and-simplicity naming) — half the "restructuring" urge dissolves once the parts are honestly labeled.
- Follow the churn, not the smell: `git log` frequency × recent bug density is the map of where structure work pays; aesthetics is not a heat map.
- The Boy Scout rule has a radius: leave code you *touch* slightly better (a rename, an extracted function, a dead branch removed) — but "slightly" and "touch"; the campsite is the diff, not the forest.
- Feature envy points at the move: the method that mostly reads another object's fields is telling you its address; deliver it.
- When a conditional on type/kind appears the third time, polymorphism (or a dispatch map) wants to exist; the first two times, the `if` is fine.
- Test churn during "pure refactor" is a smell about the tests: tests coupled to structure rather than behavior break on every reshape — refactor toward testing the surface, and treat the breakage as a finding (see enforce-first: tests assert behavior).
- Delete before you organize: dead code, unused flags, commented-out blocks — deletion is the refactor with no risk of wrong abstraction (see first-principles: deletions ship).
- Un-nest by early return; invert the condition that wraps a whole function body — mechanical, safe, and buys more readability per keystroke than almost anything.
- Price debt in the currency your stakeholders spend: "this area's bugs cost us ~2 engineer-weeks per quarter" moves roadmaps; "the code is ugly" moves nothing (see technical-leadership: translating).

## Quality Checklist

- [ ] Beneficiary named — the change/bug/comprehension problem this serves is written down.
- [ ] Behavior pinned before surgery: existing tests green, characterization added where thin.
- [ ] Every step green-to-green; red steps reverted, not debugged forward.
- [ ] Structure commits and behavior commits separated; each commit message says which it is.
- [ ] Mechanical transforms done by tooling where available.
- [ ] Scope held: the refactor stopped when the beneficiary was served; leftovers registered, not chased.
- [ ] No new abstraction from fewer than three instances without a written reason.
- [ ] Large refactors shipped incrementally (branch by abstraction), mainline always green.
- [ ] Debt register updated: paid items closed, held items priced with triggers.

## Failure Modes

- **The refactor that changed behavior**: "just restructuring" that quietly fixed—or broke—an edge case; consumers depended on the old behavior (see legacy-migrations: bug-for-bug compatibility); the invariant was asserted, never verified.
- **Big-bang restructure**: three weeks on a branch, everything reshaped at once, unmergeable against a moved mainline, abandoned — the sunk-cost museum piece every team has one of (see ci-cd: integration frequency; legacy-migrations rewrite death spiral for the architecture-scale version).
- **Premature abstraction**: two similar functions unified on resemblance; six months later the "shared" code is a flag-forest where every caller pays for every other caller — the wrong abstraction, compounding (the rule of three, skipped).
- **Aesthetic-driven prioritization**: the offensive-but-stable module beautified while the high-churn bug factory ships another regression — refactoring by taste instead of by interest rate.
- **Scope ratchet**: "while I'm here" applied recursively; the one-hour extract becomes a nine-file PR nobody can review and a merge conflict with three teammates (see code-review: reviewability is a constraint).
- **Refactor-and-fix soup**: behavior fixes threaded through structural commits — the reviewer can't find the logic change, the bisect can't isolate the regression, and the "no behavior change" label is now folklore.
- **Test-shaped obstruction**: structure-coupled tests (mock-heavy, private-method-poking) failing on every rename — so tests get updated *to match the refactor*, which means nothing was pinned and the safety net was decorative (see enforce-first).
- **The guilt-list debt register**: every imperfection logged, nothing priced, nothing triggered — a shame archive instead of a portfolio; unranked debt is unpayable debt.

## Edge Cases

- **Refactoring at a public boundary**: internal reshaping is free; anything touching a published API, event schema, or wire format is a *migration* with versioning and consumers, however small the diff looks (see api-design versioning; event-driven schema evolution) — the refactor/migration boundary is the trust boundary.
- **Performance-sensitive paths**: "cleaner" allocations, extra indirection, or exploded loops can change the profile — pin performance with a benchmark alongside the tests where it matters (see optimization-method: measure across the change).
- **Refactoring concurrent code**: reordering "equivalent" statements changes interleavings; extraction can move work across lock boundaries — the test suite rarely pins races (see concurrency-bugs); treat lock-scoped regions as no-fly zones for casual reshaping.
- **Generated, vendored, and framework-managed code**: refactoring output instead of source (codegen), or fighting a framework's expected shape, buys churn with no owner — find the true source, or leave it.
- **Refactoring during review**: reviewer-requested restructuring mid-PR tempts squashing everything together — append as separate commits (structure vs behavior discipline survives review pressure; see respond-review).
- **Shared code with invisible consumers**: the "unused" parameter fed by a caller in another repo; the helper imported by the analytics job (see decomposing-ambiguity: second-hand knowledge) — search *all* consumers before reshaping shared surfaces; monorepo grep is not the universe.
- **Refactoring the tests themselves**: test suites accrue their own smells (copy-paste setup, mystery fixtures) — same discipline, inverted safety: the production code now pins *their* behavior (a deliberately broken assertion should fail; if it doesn't, the test was dead — see enforce-first).
- **The half-finished predecessor**: you inherit a codebase mid-refactor — two patterns coexisting, migration stalled at 60% (see legacy-migrations: the two-system trap). Finishing the old refactor usually beats starting your better one; three patterns is worse than one mediocre one.

## Tradeoffs

- **Refactor-first vs ship-first**: reshaping before the feature is cleaner but delays visible progress; minimal-change-now is faster and compounds the mess — route by interest rate (is this area hot?) and deadline reality, and log whichever debt you take *on purpose*.
- **Duplication vs abstraction**: duplication costs sync-maintenance (fix in one, forget the other); abstraction costs coupling and generality tax — the rule of three arbitrates, and the tie-break is divergence likelihood: things that *will* evolve apart deserve to stay apart (see abstraction-and-simplicity).
- **Incremental vs atomic**: branch-by-abstraction keeps mainline green but carries dual-shape overhead (two patterns alive, adapters, longer total calendar); atomic is conceptually cleaner and only safe when small — the threshold is roughly "can this land green in a day"; past that, incremental wins on survival probability.
- **Boy-scouting vs diff purity**: opportunistic cleanups improve the codebase and pollute the diff — keep them small enough to wave through, or split them into a preceding structure-commit; the reviewer's ability to see your *actual* change is worth more than any drive-by (see code-review).
- **Paydown cadence vs feature pressure**: dedicated cleanup time is honest but fights the roadmap every quarter; attached-to-features paydown travels free but only visits hot areas — most teams need the attached mode as default plus rare, surgically-scoped dedicated efforts for structural debt no feature will ever visit.
- **Consistency vs local improvement**: the better pattern introduced in one corner makes that corner nicer and the codebase *less* consistent (two ways to do X now exist) — new patterns deserve a migration intention (even a slow one), or they're just entropy with good taste (see design-language for the aesthetic version of the same law).

## Optimization Strategies

- Mine churn data quarterly: `git log` file-frequency × defect density → the top-ten list is your paydown map, and it's usually shockingly concentrated (see the Pareto instinct in optimization-method).
- Build the refactoring reflex into estimation: feature estimates in hot areas include their enabling refactor by default (see planning-and-estimation) — "make the change easy" priced in, not begged for.
- Invest in the safety infrastructure that makes small-steps cheap: fast test suite (see enforce-first: Fast is a feature), automated transforms, trunk-based flow (see ci-cd) — refactoring frequency is downstream of refactoring *cost*.
- Run the debt register as a real portfolio review: quarterly, re-price interest (churn moved?), close what got paid, delete guilt-items with zero interest — a register people trust because it shrinks.
- Teach the catalogue: named moves (extract, inline, move, replace-conditional-with-polymorphism) give the team a shared vocabulary that turns vague "cleanup" PRs into reviewable, discussable steps (see code-review shared standards).
- Practice un-abstracting: schedule the occasional inline-back of a flag-grown abstraction — teams that only ever add abstraction ratchet toward frameworks; the inverse move keeps the codebase honest (see abstraction-and-simplicity).

## Self Review

- Who benefits from this refactor, concretely — and would they agree it served them?
- What pins the behavior I'm about to reshape — and have I watched those tests fail, or just pass?
- Is every step in my sequence individually green-and-committable, or am I carrying a broken state between steps?
- Can a reviewer tell my structure commits from my behavior commits without asking me?
- Am I abstracting from three real instances, or from two and a prophecy?
- Did I stop when the change became easy — or am I still going because momentum feels like progress?
- What am I *choosing* not to fix, and did I write that choice down with a trigger?
- If this refactor were abandoned right now at the last commit, is the codebase better, worse, or hostage?

## Examples

**1. Make the change easy: the pricing engine.**
Task: add regional tax rules to checkout. The change is hard — pricing logic is smeared across a controller, two helpers, and a template (shotgun surgery). Instead of threading tax through all four: first a pure-structure PR — characterization tests pin current totals for 30 real carts (including the weird ones: discounts + gift cards), then extract a `PricingPolicy` that owns the whole computation, callers delegating; behavior byte-identical, tests untouched and green. Then the behavior PR: regional tax lands as ~40 lines in one place with its own tests. Two reviewable diffs, one afternoon each — versus the alternate universe's 400-line mixed PR with a tax bug hiding in a "harmless" restructure.

**2. The rule of three, honored in both directions.**
Two report exporters (CSV, PDF) look 70% similar; the tempting `BaseExporter` waits. Team notes-and-waits instead. The third exporter (Excel) arrives and reveals the real seams: row *generation* is genuinely shared (extracted, cleanly — the three instances agreed); formatting and pagination are not (left separate — the three instances disagreed loudly, and PDF's pagination would have poisoned the base class with flags). Meanwhile the codebase's cautionary twin: a `BaseSyncJob` abstracted from two instances years ago, now sprouting `if self.kind == 'inventory'` branches — scheduled for inline-back-and-resplit, the un-abstracting refactor, using the same green-to-green discipline.

**3. Debt portfolio over guilt list.**
A team inherits a "tech debt" wiki page: 61 undifferentiated grievances, none ever actioned. Re-run as a portfolio: churn × bug-density data shows 70% of the last quarter's defects came from *two* modules — the order state machine (touched weekly, feared universally) and the notification dispatcher; meanwhile 40 registered offenses live in code untouched for two years (interest rate ~0 → held, closed as "won't fix, working"). The two hot modules get paydown attached to their next features: characterization tests, then replace-conditional-with-state-pattern on the order machine (see model-domain thinking). Next quarter's defect count in that area drops by half — reported to leadership in engineer-weeks saved, which is why the *following* paydown didn't need a fight (see technical-leadership).

**4. The revert that saved the week.**
Mid-refactor (extracting a rate-limit policy from a request handler), one test goes red on step 7 of 12 — a subtle behavior shift: the old code counted failed auth attempts against the limit, the new shape didn't. Two temptations, resisted: debug forward inside the refactor (invariant dies), or "fix" the behavior since the old counting looks like a bug (scope dies — and *is it* a bug? Consumers may rely on it; see legacy-migrations bug-for-bug). Executed instead: revert step 7, re-cut it smaller with the counting behavior explicitly preserved and a characterization test added to pin it, land the refactor — then file the "should failed auths count?" question as a *product decision* with the evidence attached (see decomposing-ambiguity: essential ambiguity routed). The refactor shipped green; the behavior question got answered by its actual owner a week later.

## Evaluation Rubric

Score 1–10:

- **1–2**: "Refactors" routinely change behavior; no tests before surgery; structure and logic mixed in unreviewable diffs; big-bang branches; debt untracked or a guilt list.
- **3–4**: Tests exist but aren't run per-step; steps large and courage-dependent; abstractions built from two instances; prioritization by aesthetics; occasional abandoned mega-refactor.
- **5–6**: Behavior pinned first (characterization where thin); green-to-green steps with revert-on-red; structure/behavior commits separated; rule of three mostly honored; beneficiary usually nameable.
- **7–8**: Full checklist: churn-driven prioritization, branch-by-abstraction for large work, scope held with leftovers registered, debt portfolio priced with triggers, tooling-assisted mechanical moves.
- **9–10**: Additionally: refactoring priced into feature estimates by default; safety infrastructure (fast tests, trunk flow) invested in as refactoring throughput; un-abstracting practiced; portfolio reviews that close and delete items; and a measurable line — defect rates or lead time in paid-down areas — that the paydown demonstrably moved.
