# Domain Modeling & Business Logic

## Purpose

Give business logic a home — explicit domain concepts, invariants enforced at construction, state machines for lifecycles, and a layering that keeps the rules out of controllers, ORMs, and utils — so the code answers "what does this business actually do" in its types and names instead of in tribal memory and scattered ifs.

## When to use

- Building the core logic of a feature: pricing, eligibility, lifecycle rules, quotas, workflows.
- The same business rule exists in three places and they've started to disagree.
- Controllers/handlers have grown hundreds of lines of ifs; "where does this rule live?" has no answer.
- A domain concept exists in every conversation but nowhere in the code (the "shopping session," the "grace period").
- Bugs are of the shape "that state should never happen" or "we applied the discount twice."

## Goals

- Every business rule has exactly one home, named after the domain concept it implements.
- Illegal states are unrepresentable or rejected at construction — objects can't exist invalid.
- Lifecycles are explicit state machines with defined transitions, not boolean combinations and hope.
- The domain layer is pure enough to test without infrastructure (see testing-strategy: the cheapest layer).
- Code vocabulary matches business vocabulary — the PM's sentence and the function name agree.

## Inputs

- The domain experts' actual language and rules — including the contradictions between what they say and what the system does (see decomposing-ambiguity: those contradictions are decisions to route).
- The invariants: what must always/never be true, and what it costs when violated.
- Lifecycle realities: the states things pass through, including the awkward ones (disputed, partially-refunded, suspended).
- The existing code's implicit model — where rules currently hide (see refactoring: archaeology).

## Outputs

- A ubiquitous-language glossary the code actually follows: entities, value objects, states, events, named rules.
- Domain types with enforced invariants; state machines with transition tables.
- A layering map: what lives in domain vs application vs infrastructure — and the dependency direction.
- Domain logic covered by fast, infrastructure-free tests (see testing-strategy).

## Expert Mental Model

- **Business logic scatters by default; cohesion is a fight you pick deliberately.** Nobody decides to smear the refund rules across two controllers, a model callback, and a cron job — it accrues, one convenient placement at a time. Then the rules drift (three implementations, three behaviors), and changing "how refunds work" means an archaeology project (see refactoring: shotgun surgery is this smell's name). The countermove is a *home* per concept: a `RefundPolicy` that is the only place refund rules live, referenced by everything that needs them. Scattered ifs are the debt; named concepts are the paydown.
- **The type system is your first business-rules engine.** `EmailAddress`, `Money`, `DateRange`, `OrderId` instead of strings and floats: each value object validates at construction (an invalid one *cannot exist*), carries its operations (`Money.add` refuses mixed currencies), and turns a whole bug class into compile/construction errors (see data-modeling: constraints, the storage edition of the same law). "Parse, don't validate": convert raw input into rich types once at the boundary — past that line, the domain never re-checks what the type already guarantees. Primitive obsession — everything a string, an int, a bool — is the smell that says the domain's concepts never made it into the code.
- **Entities have identity and lifecycle; value objects have neither; the distinction organizes everything.** An Order is the same order as its status changes (identity, mutable, lifecycle); $10 USD is $10 USD, interchangeable with any other (value, immutable, no identity). Value objects are free — immutable, trivially testable, safely shared. Entities are where invariants and transitions concentrate — which is why they deserve guarded methods (`order.cancel(reason)`) instead of public setters (`order.status = 'cancelled'` skips every rule the cancel method would have enforced).
- **Every lifecycle is a state machine; the only question is whether you've drawn it.** `is_active`, `is_cancelled`, `is_trial`, `pause_until` on one record encode 2⁴ combinations, most meaningless, all representable (see data-modeling: booleans breed). The expert draws the actual machine: states, legal transitions, what triggers each, what side effects fire on transition — then makes illegal transitions *fail* (`cancel()` from `delivered` raises; the transition table is the spec). Half of "impossible bug" tickets are undrawn state machines being explored by production.
- **Invariants live where the data lives together.** "Order total equals sum of lines" is enforceable only if lines change *through the order* — the aggregate: a cluster with one entry point (the root), where every mutation path runs the invariant checks. Aggregate boundaries are transaction boundaries (what must be consistent *now* — see data-modeling; what can be eventually consistent crosses aggregates via events — see event-driven). Small aggregates scale; god-aggregates serialize every write through one lock (see concurrency-bugs).
- **Domain logic wants to be pure; infrastructure wants to be thin; the dependency arrow points inward.** The domain layer computes decisions (pure: input state → new state + events); the application layer orchestrates (load, invoke domain, persist, publish); infrastructure implements the ports (DB, queue, HTTP — see api-design; postgres). The payoff is testability (the pricing engine tests in milliseconds with no containers — see testing-strategy) and honesty (a `PricingPolicy` that secretly queries three tables isn't a policy, it's a controller in a costume). You don't need the full hexagonal ceremony to get this — you need the *direction*: domain code imports nothing that talks to the network.
- **The model is a conversation artifact, not a code artifact.** Ubiquitous language — the discipline that code, tests, tickets, and domain-expert conversation use the *same words* — is what keeps the model true. When sales says "quote," support says "estimate," and the code says `PriceProposal`, every conversation is a translation with loss (see decomposing-ambiguity: same words, different problems). The moment the expert says "well, actually a return isn't a refund" — that's a modeling event; two concepts just split.

## Workflow

1. **Mine the language**: listen to how domain experts describe the process; collect the nouns (candidate entities/values), verbs (operations/events), and rules ("we never ship before payment clears" — an invariant with an owner). Write the glossary; flag where the same word means two things.
2. **Identify entities vs value objects**: what has identity and lifecycle vs what is interchangeable by value. Model the values first — they're cheap and immediately delete primitive-obsession bugs.
3. **Draw the state machines**: per entity with a lifecycle — states, transitions, triggers, side effects. Review the drawing *with the domain expert*; the awkward states they mention ("well, it can be kind of both...") are the design's real content.
4. **Locate the invariants and draw aggregate boundaries around them**: what must be transactionally consistent clusters together behind one root; everything else coordinates via events or application services. Keep aggregates small; justify every growth.
5. **Give every rule a named home**: policies (`RefundPolicy`, `EligibilityRule`), domain services for logic spanning aggregates, guarded entity methods for self-contained transitions. The test: a rule change should be a one-place edit (see refactoring: shotgun surgery inverted).
6. **Enforce at construction and transition**: constructors/factories reject invalid values; entity methods reject illegal transitions; setters that bypass rules don't exist. Make the compiler/runtime the first reviewer.
7. **Layer with the arrow inward**: domain (pure logic) ← application (orchestration, transactions) ← infrastructure (adapters). Push I/O to the edges; inject the clock and randomness (see testing-strategy: injected dependencies).
8. **Emit domain events at meaningful transitions** (`OrderPlaced`, `SubscriptionLapsed`) — the vocabulary for cross-aggregate coordination, audit, and integration (see event-driven; data-modeling: the audit rung).
9. **Test the domain layer exhaustively and fast**: every rule, every transition (legal and illegal), every invariant — pure tests, milliseconds, no mocks needed because there's nothing to mock (see testing-strategy: this is the pyramid's base earning its keep).
10. **Keep the model and the language in sync**: when the business changes vocabulary or rules, the rename/remodel is part of the change, not deferred polish (see refactoring: rename first) — a model that drifts from the business is scattering with better structure.

## Decision Tree

- If a primitive carries rules (email format, currency pairing, range validity) → value object with construction-time validation; the primitive stops at the boundary.
- If a concept appears in every planning conversation but no file is named after it → reify it; the "shopping session" that lives as five query params is the design gap.
- If an entity's booleans/statuses combine into meaningless states → draw the state machine, replace the booleans with one status + transition methods (see data-modeling for the schema half).
- If the same rule is checked in N places → extract the policy object; the N sites call it; divergence becomes impossible rather than undetected.
- If logic reads multiple aggregates to make a decision → domain service (pure, takes what it needs as arguments) — not a fatter aggregate, not a controller.
- If an invariant spans aggregates ("email unique across users") → it's not an aggregate invariant; enforce at the infrastructure chokepoint (the unique constraint — see data-modeling) or accept eventual consistency with reconciliation (see event-driven).
- If the "domain logic" is actually CRUD (forms in, rows out, no rules) → don't build the cathedral; transaction scripts with good names are honest and sufficient (see abstraction-and-simplicity: match machinery to complexity). Domain modeling earns its cost where *rules* concentrate.
- If a workflow spans time and services (order → payment → fulfillment) → model the process explicitly (a process manager/saga with its own state machine) instead of hiding the workflow in queue handlers (see event-driven: sagas; async-processing).
- If the expert's correction contradicts the code's model ("a return isn't a refund") → split the concepts now; every week the code conflates them mints new misbehavior.
- If two subdomains use the same word differently (product-catalog "price" vs billing "price") → separate models per context with explicit translation at the boundary — one unified model for both is how god-objects are born (see system-design: boundaries; abstraction-and-simplicity).

## Heuristics

- Name the rule after the business reason, not the mechanism: `LateCancellationFee`, not `check_date_diff_gt_24h`.
- If you can't test a business rule without a database, the rule is entangled with infrastructure — extract until you can (see testing-strategy: the seam is the design).
- Guarded transitions over setters, always: every public setter on an entity is an invariant bypass waiting for a caller.
- The constructor is the bouncer: if an object can be constructed invalid, every method must re-check what construction should have guaranteed.
- Make the implicit explicit: the `if user.created_at < '2023-01-01'` scattered around is a concept ("legacy cohort") wanting a name.
- Ask "what would the domain expert call this?" before naming anything; if they'd stare blankly at the class name, it's a developer concept leaking into the domain.
- Model behavior, not data bags: an entity with only getters/setters and no methods is a database row cosplaying as a domain object — its rules live somewhere else, scattered.
- Prefer returning events/results over void mutations: `order.cancel() → CancellationResult` makes outcomes explicit and testable.
- Time is an input: `is_expired(now)` not `is_expired()` reading the clock — the hidden clock is the most common purity leak (see testing-strategy).
- Two rules that change for different reasons don't share a home even if they look similar today (see refactoring: divergence likelihood arbitrates).
- The state machine's transition table belongs in one place the tests iterate over — not distributed across handler ifs.
- When a method needs six parameters from three aggregates, the operation is telling you where it wants to live — listen (feature envy, domain edition; see refactoring).

## Quality Checklist

- [ ] Glossary exists; code names match expert vocabulary; one meaning per word per context.
- [ ] Value objects for every ruled primitive; construction-time validation; no re-validation downstream.
- [ ] Entities expose guarded transitions, not setters; illegal transitions fail loudly.
- [ ] State machines drawn and enforced; transition tables tested exhaustively.
- [ ] Every business rule has one named home; a rule change is a one-place edit.
- [ ] Aggregate boundaries = transaction boundaries; aggregates small with justified exceptions.
- [ ] Domain layer imports no infrastructure; clock/randomness injected.
- [ ] Domain events emitted at meaningful transitions.
- [ ] Domain tests: fast, pure, covering legal + illegal paths (see testing-strategy deny paths).
- [ ] Cross-context translations explicit; no shared god-model spanning subdomains.

## Failure Modes

- **The anemic domain**: entities as getter/setter bags, all logic in "services" that are really transaction scripts, every rule re-implemented per endpoint — the structure of domain modeling with none of the protection.
- **The god aggregate**: `Order` owning payments, shipments, invoices, and customer prefs — every write locks the world (see concurrency-bugs), every test builds the world, and the aggregate is the new monolith.
- **Primitive obsession at scale**: `send_invoice(str, str, float, str, bool)` — the currency lives in a parallel variable somewhere, the bool means three things, and the type system watches idly as arguments transpose.
- **State by boolean archaeology**: `if active and not cancelled and (not paused or resumed_at)` — the machine exists, undrawn, and every new flag doubles its dark corners.
- **Framework bleed**: ORM callbacks running business rules (surprise side effects on save), validation split between model annotations and controllers — the domain's logic distributed across the framework's lifecycle hooks, untestable in isolation and triggered in orders nobody chose (see refactoring: framework-managed code).
- **The translation-free boundary**: billing imports catalog's `Product` and reaches into its fields — two contexts fused; catalog can no longer change without billing's permission (see system-design: coupling through shared models).
- **Modeling ceremony without rules**: full DDD stack — repositories, factories, value objects — wrapped around CRUD with no invariants; the machinery costs daily and protects nothing (see abstraction-and-simplicity: overengineering has a shape).
- **The drifting glossary**: business renamed "trials" to "previews" two quarters ago; the code still says trial; every conversation now requires a translation layer carried in heads — and new hires implement rules against the wrong concept.

## Edge Cases

- **Rules that vary by tenant/plan/region**: the policy object pattern earns its keep — `CancellationPolicy` resolved per context (strategy), not `if tenant.plan == 'enterprise'` sprinkled through transitions (see auth for the permission flavor of this).
- **Retroactive rule changes**: "new refund policy applies to orders after March 1" — policies need effective dates; the *old* policy must survive for old orders (see data-modeling: temporal truth; the policy is data, versioned).
- **Long-running processes with external waits**: the saga whose next step depends on a webhook arriving (or not) — model timeouts as first-class transitions (`AwaitingPayment --48h--> Expired`), because the state machine that only handles messages that *arrive* is half a machine (see event-driven; resilience-engineering).
- **Concurrent transitions on one entity**: two admins cancel/refund simultaneously — optimistic locking with version checks at the aggregate root; the second writer gets a conflict, not a silent lost update (see concurrency-bugs; postgres).
- **Bulk operations vs per-entity invariants**: importing 50k orders through the aggregate one-at-a-time is correct and slow; raw-inserting bypasses every rule — the honest middle: batch paths that run the *same* named policies, with the invariant checks vectorized where measured necessary (see optimization-method: earn the bypass with numbers).
- **The rule the business can't state**: "we just know which customers are risky" — don't encode vibes as ifs; make the human decision an explicit state (`PendingReview`) with the human as the transition trigger (see judgment-under-uncertainty; ai-product-ux if a model later assists).
- **Legacy code with implicit models**: the model exists — in the ifs; extraction order: characterize behavior first (see refactoring), name the concepts, then move rules into them one at a time; big-bang re-modeling of live business logic is the rewrite death spiral at module scale.
- **Cross-language/cross-service model duplication**: the same `Money` logic in the frontend, backend, and worker — accept duplication across process boundaries with contract tests pinning agreement (see api-design; testing-strategy), rather than fantasy sharing.

## Tradeoffs

- **Rich model vs simple scripts**: guarded entities and policies pay off where rules are dense and changing; transaction scripts win where logic is thin and stable. The honest split is per-module, not per-codebase — the billing core deserves the model; the settings page doesn't (see abstraction-and-simplicity).
- **Invariant strictness vs operational reality**: construction-time rejection keeps the model pure and makes importing historical dirt impossible — deliberate escape hatches (a `Legacy` variant, staged validation) beat loosening the front door (see data-modeling: same tension, same answer).
- **Aggregate size**: bigger aggregates enforce more invariants transactionally and serialize more writes; smaller ones scale and push consistency to eventual (see event-driven). Default small; grow only for invariants that genuinely can't wait.
- **Purity vs convenience**: injecting the clock and passing context is ceremony; reading globals is convenient and couples every test to the world. The ceremony is fixed cost; the coupling compounds.
- **One model vs context-specific models**: sharing a model across subdomains saves duplication and welds the contexts together; separate models with translation cost mapping code and keep change independent — past two contexts, translation is almost always cheaper (see system-design boundaries).
- **Events for everything vs direct calls**: domain events decouple and add indirection (the reader must find the handlers); reserve events for genuinely cross-boundary or async coordination — same-transaction, same-aggregate logic can just be a method call (see event-driven: not everything is an event).

## Optimization Strategies

- Start every feature with a ten-minute glossary pass: nouns, verbs, rules, from the ticket and the expert — cheapest modeling step, catches the concept-splits before code exists (see decomposing-ambiguity).
- Build the value-object library early (Money, Email, DateRange, Percentage, the domain's units): each one deletes a bug class forever and they compound (see the same move in data-modeling types).
- Table-drive the state machine tests: iterate (state × event → expected) over the whole matrix — exhaustive for the cost of a loop (see testing-strategy: property thinking).
- Review PRs for rule placement, not just correctness: "does this rule live in its home?" as a standing review question — scattering is prevented one review at a time (see code-review).
- Run event-storming-style sessions for gnarly flows: experts + engineers mapping events/commands/policies on a wall — the cheapest way to surface the states everyone forgot (see brainstorming: structured divergence applied to modeling).
- Track "rule-change diff size" as a health metric: when changing a business rule touches one file, the model is working; when it touches nine, the scattering is back (see refactoring: shotgun surgery as a measurable).

## Self Review

- Could the domain expert read my class and method names and nod?
- What invariants does this feature have — and can each one point to the single place it's enforced?
- Can any object in this module exist in an invalid state? Any transition happen that the business forbids?
- Where does the clock enter? The database? Could I test every rule with neither?
- If the business changes this rule next quarter, how many files change? (If >2: why?)
- Which concepts am I representing as primitives that carry rules I'm re-checking everywhere?
- Did I draw the state machine, or am I assuming the booleans behave?
- Is there a word my code uses that the business doesn't — or two business words my code conflates?

## Examples

**1. The refund rules, gathered into one home.**
Refund logic found in four places: the API handler (14-day check), a model callback (restocking fee), the support console (its own 30-day check — drift, already), and a cron (auto-refund on cancellations, no fee logic — drift again). Customers get different outcomes by which door they enter. Remodel: `RefundPolicy.evaluate(order, request, now) → RefundDecision` — window rules, fee schedule, method-specific limits in one pure, exhaustively tested object (48 table-driven cases, milliseconds — see testing-strategy); all four call sites reduced to invoking it and acting on the decision. The support-console discrepancy surfaces *during* consolidation as a failing table row — resolved by the product owner as a real policy question, not silently by whichever implementation survived (see decomposing-ambiguity: routed, not guessed).

**2. The subscription state machine, drawn at last.**
Five booleans (`active, trial, cancelled, paused, past_due`) and their 32 combinations, of which 7 are meaningful and 3 of the meaningless ones exist in production. The machine gets drawn with the billing expert: 7 states, 12 legal transitions, each with trigger and side effects (`PastDue --payment_ok--> Active` restores access + emits `SubscriptionRecovered`). Implementation: one `status`, transition methods that raise on illegal moves, the transition table as data iterated by tests, domain events per transition feeding the email and analytics consumers (see event-driven). The 3 impossible-state rows get a one-time triage script (see data-modeling: migration rungs). The following quarter, "pause during trial" arrives as a feature — it's a *drawing* change first (one new state, three transitions, expert-reviewed on the diagram), then an hour of code; before the machine, the same feature would have been a sixth boolean.

**3. Knowing when NOT to model.**
A team fresh from DDD training builds the notification-preferences service with aggregates, repositories, factories, and seven value objects — for a feature whose entire logic is "store toggles, read toggles." Review question: what invariants exist? One ("at least one channel enabled for security alerts") — enforceable by a single check constraint (see data-modeling) plus one guard function. The ceremony is dismantled to a transaction script + constraint; the deleted machinery was costing every reader and protecting nothing (see abstraction-and-simplicity: the machinery must earn its keep). The budget saved goes where the rules actually concentrate — the billing engine — which *does* get the full treatment. Domain modeling is a scalpel, not a lifestyle.

## Evaluation Rubric

Score 1–10:

- **1–2**: Logic smeared across controllers, callbacks, and crons; primitives everywhere; states as boolean archaeology; rules discoverable only by reading everything; "where does X live?" has no answer.
- **3–4**: Some service objects exist but rules duplicate across layers; entities are data bags; state machines implicit; domain tests require the full stack.
- **5–6**: Value objects for ruled primitives; status enums with guarded transitions on core entities; rules mostly homed; domain layer testable without infrastructure for the important paths.
- **7–8**: Full checklist: glossary honored in code, invariants enforced at construction, drawn-and-tested state machines, small aggregates on transaction boundaries, events at transitions, one-place rule changes, ceremony proportional to rule density.
- **9–10**: Additionally: policy objects versioned where rules change over time; cross-context translations explicit; rule-change diff size tracked and small; modeling sessions standing practice with domain experts — and the model demonstrably steering: impossible-state bugs extinct, and business rule changes shipping in hours because the code already speaks the business's language.
