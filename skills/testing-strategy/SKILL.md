---
name: testing-strategy
description: "Use when deciding what to test at which layer (unit/integration/E2E), the suite is slow, flaky, or distrusted, coverage is high but bugs ship anyway, reviewing tests that mock everything, or after an escaped bug — pyramid shape, deny paths, flake policy."
---

# Testing Strategy

## Purpose

Decide what to test, at which layer, with how much investment — so the suite catches the bugs that matter, runs fast enough to be consulted constantly, and doesn't calcify into a change-tax that tests implementation details while missing real regressions.

## When to use

- Setting up testing for a new service, feature, or team — deciding the pyramid/trophy shape before habits form.
- The suite is slow, flaky, or ignored; deploys wait 40 minutes on tests nobody trusts.
- Coverage is high but bugs ship anyway; or coverage is contested ("do we really need a test for this?").
- Reviewing a PR whose tests mirror the implementation line-by-line, or mock everything they touch.
- After an incident, deciding which test would have caught it — and which layer it belongs at.

## Goals

- Every behavior that matters has exactly one test that fails when it breaks — at the cheapest layer that can catch it.
- The suite is fast enough to run on every change (unit seconds, integration minutes), and trusted enough that red means stop.
- Tests assert behavior at boundaries, not implementation inside them — refactors don't shred the suite.
- Flakiness is treated as an outage of the safety system, not weather.
- Coverage is read as a map of what's *unprotected*, never chased as a target.

## Inputs

- The system's risk profile: what breaks badly (money, data loss, auth) vs what breaks embarrassingly (layout).
- The architecture's natural seams: pure logic, service boundaries, external dependencies, UI.
- Current suite health: runtime, flake rate, when it last caught a real bug vs last blocked a good deploy.
- Team context: how often code changes, who writes tests, what CI can afford.

## Outputs

- A layer map: which behaviors are tested where (unit / integration / contract / E2E), with rationale.
- A written testing policy the team actually follows: what every PR must cover, what's explicitly not tested.
- Flake policy: quarantine path, fix SLA, deletion criteria.
- The deny-path inventory for critical flows — failure cases enumerated and asserted, not just happy paths.

## Expert Mental Model

- **A test is a bet: cost (writing, running, maintaining) against the bug class it catches.** Bad suites lose the bet in both directions — expensive tests for trivial code, no tests where the money moves. The expert allocates like an investor: heavy coverage on complex logic with high blast radius (pricing, permissions, state machines), light coverage on glue, none on the framework's own behavior.
- **Test behavior at boundaries, not implementation inside them.** A test that breaks when you refactor without changing behavior is coupled to structure — it taxes every improvement and pins nothing (see refactoring: structure-coupled tests are decorative safety). The unit under test is a *contract*: given inputs, observable outputs/effects. If renaming a private method breaks tests, the tests are testing the wrong thing.
- **The pyramid is about cost physics, not dogma.** Unit tests are milliseconds and precise (a failure names the function); E2E tests are seconds-to-minutes, flaky by nature (network, timing, real browsers), and vague (a failure names nothing). So: many cheap-and-precise, few expensive-and-broad. The "trophy" variant (lean units, heavy integration) is right when the risk lives in wiring rather than logic — CRUD apps with thin domain logic. Choose the shape from where *your* bugs live, not from a conference talk.
- **Mock at the boundary you own; fake what you don't.** Mocking your own internals couples tests to structure. Mock/fake at architectural seams: the payment provider, the clock, the mail sender, the LLM call. For infrastructure you own (your database), prefer the real thing in integration tests — an in-memory fake of Postgres tests your fantasy of Postgres (see postgres: the planner has opinions your fake doesn't).
- **The deny path is where the bugs are.** Happy paths get exercised by developers and users constantly; the error paths run for the first time in production at 3am. Tests that assert failure behavior — wrong input, timeout, double-submit, permission denied, partial write — earn more than another happy-path variant (see auth: tests that assert failure; resilience-engineering: failure paths are code too).
- **A flaky test is worse than no test.** It trains the team to re-run on red — which means the day red is real, someone re-runs it. Flakes are almost always real concurrency, ordering, or isolation bugs *somewhere* (in the test or the code — see concurrency-bugs); quarantine immediately, root-cause within days, delete if unowned. The suite's authority is the asset; flakes spend it.
- **Coverage is a flashlight, not a scoreboard.** 90% coverage with assertions like `expect(result).toBeDefined()` is theater; the number can't tell asserting from executing. Use coverage to find the untested branch of the pricing logic; never use it as a gate that manufactures assertion-free tests. Mutation testing (does the suite fail when the code is deliberately broken?) measures what coverage pretends to.

## Workflow

1. **Map the risk**: list the behaviors whose breakage is expensive (money, data, auth, compliance) — this list, not the file tree, drives investment.
2. **Find the seams**: pure logic (unit-testable by construction), service boundaries (integration), external dependencies (contract/fake), full flows (E2E). Where logic is trapped inside I/O, extract it first — testability is a design property (see abstraction-and-simplicity; component-architecture for the frontend version).
3. **Assign each risk to its cheapest sufficient layer**: pricing math → unit; "order total survives the checkout flow" → one integration test; "user can actually buy" → one E2E smoke. A behavior tested at E2E that a unit test could catch is paying 1000× per run for the same protection.
4. **Write the deny-path matrix for critical flows**: enumerate failure cases (invalid input, timeout, concurrent modification, permission denied) and assert the *specified* behavior for each — error surfaced, state unchanged or recovered, retry safe.
5. **Set the speed budget and enforce it**: unit suite under a minute, integration under ten; anything slower gets profiled and fixed like a production latency problem (see optimization-method). Speed is what makes tests get *run*.
6. **Wire the layers into CI at the right gates** (see ci-cd): units on every push, integration on PR, E2E smoke on deploy candidates — not everything everywhere.
7. **Establish the flake protocol**: first flake → quarantine tag + ticket; fix SLA (days, not quarters); flake rate on the team dashboard next to uptime.
8. **Review tests as seriously as code**: in PR review, ask "what breaks that this catches?" and "does this survive a refactor?" — a test with no answer to the first question is deleted, not merged (see code-review).
9. **After every escaped bug**: write the test that would have caught it, at the cheapest layer that could have — the regression test is the postmortem's receipt (see root-cause-analysis).

## Decision Tree

- If the logic is pure (input → output, no I/O) → unit test it exhaustively; this is the cheapest protection that exists. Complex algorithms get property-based tests on top (invariants over generated inputs).
- If the behavior lives in wiring (queries, serialization, framework config) → integration test against real infrastructure (containerized DB, real HTTP through the stack); unit tests with mocks here test the mocks.
- If the behavior crosses a service you don't own → contract tests (record/verify the expectations both sides hold) + a fake for everyday runs; hitting the real sandbox belongs in a scheduled job, not the PR path.
- If the behavior is a full user journey → one E2E per critical journey (signup, purchase, the money path), smoke-depth only; everything else that journey touches is covered lower in the stack.
- If you're testing UI → component tests for logic and states (see interface-states: assert all five states render), visual/snapshot only where pixels are the product; asserting DOM structure pins implementation.
- If a test needs three mocks and knowledge of call order → the design is telling you the boundaries are wrong; fix the seam, not the test (see abstraction-and-simplicity).
- If a test flakes → quarantine now; diagnose as a real bug: shared state between tests, time dependence, order dependence, real race (see concurrency-bugs). Retry-until-green is evidence destruction.
- If legacy code has no tests and needs changing → characterization tests at the coarsest honest boundary first (see refactoring), then refactor toward testable seams; don't hand-write unit tests for structure that's about to change.
- If the team debates "is this worth testing" → price it: what's the blast radius when it breaks × how likely is change in this area? Glue code with no logic and instant failure visibility → skip with a clear conscience.
- If TDD or test-after → TDD where the spec is expressible as tests upfront (algorithms, APIs, bug fixes — the failing test proves you understood the bug); test-after where the shape emerges by exploration (UI, spikes) — but the *coverage bar is identical* either way; only the sequence differs.

## Heuristics

- One behavior, one test: when a behavior breaks, exactly one test should fail, and its name should say what broke. Ten failures for one bug means nine tests are duplicates.
- Test names are specifications: `refund_exceeding_original_charge_is_rejected` documents; `test_refund_2` doesn't.
- Arrange-act-assert, visible in the test body: setup hidden in six layers of fixtures makes every failure an archaeology project. Some duplication in tests is fine; tests optimize for *readability at failure time*, not DRY (see abstraction-and-simplicity: different context, different rules).
- Watch every new test fail once: a test that passes before the fix, or that you've never seen red, is unverified — it may assert nothing.
- The clock, randomness, and the network are injected dependencies — a test that sleeps is a test that flakes; control time, seed randomness, fake the network.
- Assert outcomes, not journeys: `mail_sent_to(user)` not `mailer.send.called_once_with(...)` — the second breaks when the mailer refactors.
- Each test builds its own world and cleans up (or runs in a transaction rolled back) — shared fixtures are how test-order dependence is born.
- If setup takes 50 lines, the code under test has too many dependencies — the test is reviewing your design and finding it wanting.
- Delete tests that no longer earn their run cost: the test for deleted behavior, the duplicate, the one that never fails — a suite is a portfolio, not an archive (see refactoring: debt portfolio).
- The bug you just fixed is the most valuable test you'll write today: it's a *proven* failure mode with a known reproduction.

## Quality Checklist

- [ ] Risk map exists; high-blast-radius behaviors identifiably covered at a named layer.
- [ ] Deny paths asserted for critical flows, not just happy paths.
- [ ] Tests assert behavior at boundaries; a rename-only refactor leaves the suite green.
- [ ] Mocks only at owned seams / unowned externals; real infrastructure in integration tests.
- [ ] Unit suite < 1 min, integration < 10; budgets enforced, not aspired to.
- [ ] Zero tolerated flakes: quarantine + SLA + dashboard.
- [ ] Every new test observed failing once; no assertion-free tests.
- [ ] E2E limited to critical journeys at smoke depth.
- [ ] Escaped bugs get regression tests at the cheapest sufficient layer.
- [ ] Coverage used to find gaps in risky code, not enforced as a global number.

## Failure Modes

- **The inverted pyramid**: 400 E2E tests, 30 units — every run is 50 minutes and 4 flakes; developers stop running tests locally; the suite becomes a deploy tax instead of a design tool.
- **Mock soup**: every collaborator mocked, call order asserted — the suite passes while production breaks (the mocks agreed with each other, not with reality), and every refactor breaks 40 tests without breaking behavior.
- **Coverage theater**: the 90% gate manufactures tests that execute code and assert nothing; the number climbs while protection doesn't.
- **The re-run culture**: flaky tests normalized ("just re-run it") — the suite's red signal carries no information, and the real regression sails through on the third retry.
- **Happy-path monoculture**: every test is a success case; error handling, the code most likely to be wrong and least often exercised, ships untested.
- **Test-after-never**: "we'll add tests once it stabilizes" — it never stabilizes because changes are terrifying because there are no tests; the debt spiral (see refactoring).
- **The frozen spec**: tests treated as immutable — behavior changes require test changes, but nobody distinguishes "test correctly failing on regression" from "test obsoleted by new requirements," so tests get commented out. A changed behavior changes its test *deliberately, in the same PR*.
- **Shared-fixture archaeology**: one giant fixture serving 200 tests — nobody can change setup without breaking distant tests; adding a test means understanding the whole fixture's implicit contracts.

## Edge Cases

- **Time-dependent behavior** (expiry, scheduling, billing periods): inject the clock everywhere; test the boundaries (the second before/after midnight, leap years, DST transitions, month-ends) — the calendar is an adversary (see legacy code lessons in refactoring's characterization examples).
- **Concurrency**: example-based tests rarely catch races — use stress harnesses for the hot invariants (N workers hammering the same row) and deterministic interleaving tools where the ecosystem has them; and accept that some classes are better caught by invariant-checking in production (see concurrency-bugs; observability).
- **Non-determinism from LLMs/ML**: exact-output assertions are wrong by design — assert properties (schema-valid, contains required fields, passes the judge rubric) and manage quality by eval suite, not unit test (see evals: that's what they're for).
- **Randomized logic** (shuffles, sampling): seed the generator in tests; property-based assertions over distributions ("all items appear," "no bias beyond ε") instead of golden outputs.
- **Migrations and data fixes**: test against a snapshot of realistic data shape — the migration that works on three fixture rows dies on the 2017 malformed rows (see refactoring: expand-migrate-contract; postgres).
- **Email/notification/webhook side effects**: capture-and-assert at the boundary (the outbox), never actually send in CI; and one scheduled job that exercises the real integration in a sandbox.
- **Performance as behavior**: where latency is a requirement, pin it with a benchmark test with generous-but-real budgets (see optimization-method) — separate from correctness suites so noise doesn't erode trust.
- **Generated code and config**: don't test the generator's output line-by-line (that's a snapshot of implementation); test that the generated artifact *behaves* — compiles, serves, validates.

## Tradeoffs

- **Speed vs realism**: real databases and real HTTP are slower and truer; mocks are instant and fictional. Resolve by layer: units get purity and speed, integration gets reality, and the budget keeps reality honest.
- **TDD vs test-after**: TDD front-loads design pressure and guarantees coverage; test-after allows exploration and risks "later." The non-negotiable is the destination (tested behavior), not the route.
- **DRY vs readable tests**: extracted helpers reduce duplication and hide the arrange step; inline setup is verbose and self-explanatory at failure time. Bias toward visible; extract only what's truly noise (auth headers, boilerplate builders).
- **Strict assertion vs brittle assertion**: asserting the full response object catches unintended changes and breaks on every intended one; asserting three fields misses regressions elsewhere. Match strictness to contract stability: public API responses strict (see api-design: the response IS the contract), internal shapes loose.
- **E2E confidence vs E2E cost**: each E2E test buys the most realism and the most flake surface, maintenance, and runtime — the discipline is a *fixed budget* (the N critical journeys) that new tests must displace, not extend.
- **Testing effort vs shipping**: under deadline, cutting tests is borrowing at the worst rate — but *scoping* tests (deny paths on the money flow now, edge cases on the settings page later) is legitimate triage; log the debt (see refactoring: deliberate debt has a trigger).

## Optimization Strategies

- Parallelize by default: tests that can't run in parallel are confessing shared state — fixing the isolation speeds the suite *and* removes flake sources.
- Profile the suite like production: the ten slowest tests are usually 60% of runtime; they're often integration tests wearing unit-test clothes (per-test app boot, un-pooled DB setup).
- Run only affected tests on save locally (watch mode), full suite in CI — the inner loop is where test speed compounds into design quality.
- Build test-data builders (`user(overrides)`, `order(state: :paid)`) — cheap worlds per test kill the shared-fixture pathology and make tests readable.
- Track suite health as a product: runtime trend, flake rate, escaped-bug count (bugs production found that tests didn't) — the last number is the suite's actual grade.
- Mutation-test the crown jewels quarterly: run the mutator over pricing/auth/billing and see what survives — surviving mutants are the coverage number's lies, enumerated.
- When an area churns constantly and its tests always break: stop patching tests; redesign the boundary they assert (the churn is the design review — see refactoring).

## Self Review

- For the riskiest behavior I touched: which single test fails if it breaks — and have I seen that test red?
- Am I asserting what the code *does* (outcomes at the boundary) or *how* it currently does it?
- Did I test the failure paths, or just the path where everything cooperates?
- Would this suite survive a rename-only refactor without a single edit?
- What's mocked — and is each mock standing in for something at a real architectural seam?
- If I deliberately broke the logic right now, would anything fail? (Try it.)
- Is there a test in this PR that exists to satisfy a number rather than to catch a bug?
- What did the last three production bugs have in common — and does the suite now catch that class?

## Examples

**1. Rebalancing an inverted pyramid.**
A checkout service: 340 E2E browser tests, 25-minute CI, ~3 flakes/run; developers merge on "probably fine." Risk mapping shows the actual danger: pricing math (discount stacking, tax, currency rounding) and inventory reservation races. Rebuild: pricing extracted from the controller into pure functions (see refactoring) → 180 unit tests covering every rule combination in 4 seconds, including property tests (total never negative, tax monotonic in price). Reservation gets an integration stress test against real Postgres (20 workers, one SKU, assert never oversold — see concurrency-bugs). E2E collapses to 6 smoke journeys. CI: 6 minutes, zero tolerated flakes. Next quarter: two pricing bugs caught at unit level pre-merge; escaped-bug count drops to one — a webhook edge, which gets its regression test at the contract layer, where it belonged.

**2. The mock suite that lied.**
An integration syncs CRM contacts: every test mocks the HTTP client, asserting exact call sequences. Production breaks three times in a month (pagination change, rate-limit header, a null company field) — all invisible to the suite because *the mocks encode last year's API*. Fix: contract tests recorded against the vendor sandbox (re-verified nightly, not per-PR), a fake built from those recordings for everyday tests, and assertions rewritten from "called with" to "after sync, local DB contains X." The refactor that follows (swapping the HTTP library) requires zero test changes — the previous suite would have needed all 60 rewritten.

**3. The deny-path matrix that paid for itself.**
A payouts feature ships with the usual happy tests. Applying the matrix before launch: what happens on — duplicate submit (double-payout?), provider timeout after debit (money limbo?), stale balance (overdraw?), permission revoked mid-flow (see auth)? Writing the assertions forces the answers: idempotency key on submit, a reconciliation state for provider-timeout, balance check moved inside the transaction, `can()` re-checked at execution. Two of the four behaviors *didn't exist* until the tests demanded them — the deny-path matrix wasn't verifying the design; it was finishing it (see resilience-engineering for the systemic version).

## Evaluation Rubric

Score 1–10:

- **1–2**: Tests absent, or a ceremonial suite nobody runs; manual QA as the only net; bugs found by users.
- **3–4**: Tests exist where easy (utils), absent where risky (money, auth); heavy E2E or heavy mocks; flakes normalized; coverage gamed if measured.
- **5–6**: Layer map roughly right; behavior-boundary assertions the norm; real infra in integration; deny paths on the most critical flows; flakes quarantined; suite fast enough to run locally.
- **7–8**: Full checklist: risk-driven allocation, enforced speed budgets, one-behavior-one-test discipline, regression tests per escaped bug, E2E on a fixed smoke budget, test review as rigorous as code review.
- **9–10**: Additionally: property/mutation testing on crown jewels; suite health tracked (escaped-bug rate trending down); test pain routinely converted into design improvements; and the suite demonstrably trusted — red stops the line, green ships without ceremony.
