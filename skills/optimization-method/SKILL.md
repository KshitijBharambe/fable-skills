---
name: optimization-method
description: "Use when something is measurably too slow or expensive (endpoint, query, build, render, bill), before optimizing anything, when a team optimizes by instinct without profiles, or capacity/load planning — measure, then optimize."
---

# The Optimization Method

## Purpose

Make systems faster (or cheaper) with a discipline that survives contact with reality: define the metric and its budget first, measure before touching anything, fix the biggest bar, re-measure, and stop when the budget is met — including the expert's most-used move: recognizing when *not* to optimize at all.

## When to use

- Something is measurably too slow or too expensive: an endpoint, a query, a build, a render, a batch job, a cloud bill.
- Before optimizing anything — this skill's first half is deciding whether the work is worth doing.
- When a team is "optimizing" by instinct: rewriting hot-looking code, adding caches, upgrading instances — without profiles.
- Capacity planning and load testing: will it survive 10× — and which part dies first?
- Reviewing a PR whose justification is "this is faster" (is it? where's the measurement?).

## Goals

- A user- or business-anchored target ("p95 checkout < 500ms", "build < 10 min", "$X per 1M requests") — not "as fast as possible."
- Every optimization preceded by a profile and followed by a re-measurement under the same conditions; wins stated with numbers.
- Effort spent on the actual bottleneck (the biggest bar), not the most interesting or most visible code.
- Complexity paid only where measured wins justify it, quarantined behind clean interfaces (see abstraction-and-simplicity).
- A stopping point honored: budget met → stop; the last 20ms is not free.

## Expert Mental Model

- **Measure first, always — intuition about bottlenecks is reliably wrong.** Decades of profiling folklore agree: engineers guess the hot spot correctly a minority of the time, and the real cost hides in the boring place — serialization, not the algorithm; the N+1 query, not the "slow" framework (see postgres); the synchronous DNS lookup; the logger. The expert's iron law: *no optimization without a profile, no claimed win without a before/after measurement under identical conditions.* Everything else in this skill is scaffolding around that law.
- **The metric must be anchored to a user or a bill, with a budget.** "Faster" is not a goal; "p95 < 500ms because checkout abandonment doubles past that" is (see product-thinking metrics; frontend-performance for the UX thresholds). The budget does three jobs: it makes *done* defined (optimization without a stopping criterion runs forever — see the failure modes), it prioritizes (which endpoints are over budget?), and it licenses *not* optimizing (under budget = leave it alone, however offensive the code). Averages lie systematically here: p50 hides the p99 experienced by your heaviest users — and the heaviest users are often the most valuable (see dashboard-ux data honesty; observability percentiles).
- **Amdahl's arithmetic disciplines the effort.** Speeding a component by 10× helps overall latency only in proportion to that component's share: a 10× win on 5% of the request is a 4.5% improvement — invisible; a 1.3× win on 60% of it is 14% — visible. The profile's biggest bar sets the ceiling on every optimization's payoff, which is why the workflow is "fix the biggest bar, re-measure, repeat" and never "fix everything plausible in one pass." Re-measuring matters because the biggest bar *moves*: after the query is fixed, serialization is the new leader, and yesterday's plan is stale.
- **The hierarchy of wins: delete > don't do it twice > don't do it now > do it in bulk > do it faster.** The best optimization removes the work entirely (the report nobody reads, the double-fetch, the redundant validation — see first-principles: dissolving beats optimizing). Next: cache it (see caching — with its invalidation taxes priced in), then defer it out of the critical path (async/queue — see async-processing), then batch it (the N+1 → one query; the chatty loop → one bulk call), and only *then* micro-optimize the code that survives all four. Micro-optimization first is the novice's tell — tuning a loop that shouldn't exist.
- **Complexity is the currency you pay — spend it only at proven hot spots, and quarantine the purchase.** Optimized code is usually worse code: denormalized, cache-invalidation-haunted, unrolled, clever (see abstraction-and-simplicity: the clever-vs-boring trade). The discipline: pay only where the profile proves the need, hide the ugliness behind a boring interface (depth as containment), document the trick where it lives, and *pin the win with a benchmark* so the next refactor doesn't silently refund it (see refactoring: performance-sensitive paths).
- **Load behavior is nonlinear — systems don't degrade gracefully, they cliff.** The p99 at 80% utilization tells you little about 95%: queues that were invisible begin to dominate (queueing theory's hockey stick), retries amplify load exactly when capacity is scarcest (the metastable failure — see production-debugging; async-processing retry storms), caches that made everything fast make everything slow when they're cold. Capacity questions are answered by load tests that model *real* traffic shapes (bursts, heavy users, cold starts — see the edge cases), not by extrapolating quiet-Tuesday averages.

## Workflow

1. **Anchor the target**: which metric, which percentile, what budget, and *why that number* — traced to a user experience or a bill (see decomposing-ambiguity: instantiate "slow"). No budget → negotiate one before any engineering.
2. **Check it's worth doing**: current vs budget, how many users/dollars affected, what the win is worth — optimization competes with features on ROI, and often loses honestly (see the not-optimizing decision below).
3. **Measure the current state under representative conditions**: production data shapes, realistic concurrency, warm/cold states noted (see observability for the always-on version; the lab number that ignores production's data skew is a fiction).
4. **Profile end-to-end first, then zoom**: where does the time/money actually go across the whole path (client, network, service, query, downstream — see production-debugging tracing)? Get the biggest bar. Only then profile *inside* that component.
5. **Generate candidates against the hierarchy**: can the biggest bar be deleted? cached? deferred? batched? — only then, made faster. Estimate each candidate's ceiling with Amdahl's arithmetic before building anything.
6. **Fix one thing**: the smallest change that attacks the biggest bar. One variable — bundled optimizations make the re-measure unattributable (see root-cause-analysis: one change per experiment).
7. **Re-measure under the same conditions**: state the delta with numbers ("p95 620→410ms, n=10k requests, prod-shadow traffic"). No improvement → *revert it* — unproven complexity doesn't get to stay (see refactoring: revert-on-red, performance edition).
8. **Repeat until the budget is met — then stop**: write down the stopping point and the remaining known opportunities (the not-yet ledger for performance — see abstraction-and-simplicity), so the next regression starts from a map.
9. **Pin the wins**: a benchmark or SLO alert on the optimized path (see observability; ci-cd performance gates where they earn their flake-risk), so regressions announce themselves instead of accreting.
10. **Document the tricks where they live**: the denormalization's invalidation rules, the cache's staleness budget, the reason the loop is weird — the constraint the code can't show (see technical-writing; abstraction-and-simplicity comments).

## Decision Tree

- If nobody can say why the current performance is a problem (which user, which bill) → don't optimize; write the budget question down and route it (see product-thinking) — "it feels slow" gets the instantiation treatment first.
- If under budget → stop. Offensive-but-fast-enough code is a refactoring question (see refactoring: churn-driven, not disgust-driven), not a performance one.
- If over budget → profile end-to-end before opening any code:
  - Biggest bar is a database query → the postgres playbook (indexes, N+1s, query shape — see postgres) before any application cleverness.
  - Biggest bar is network chatter → batch, coalesce, or move the computation to the data (see api-design: chatty interfaces; system-design: latency numbers).
  - Biggest bar is third-party/downstream → cache it, parallelize it, or cut the dependency from the critical path (see async-processing; caching) — you can't optimize code you don't own, but you can stop waiting on it.
  - Biggest bar is "everywhere, a little" → suspect per-call overhead (serialization, logging, middleware) multiplied by call count — the death-by-a-thousand-cuts profile; fix the multiplier, not the thousand sites.
- If the fix candidate is a cache → price the full cost first: invalidation correctness, staleness budget, stampede protection, cold-start behavior (see caching — a cache is a bet that reads outnumber changes; verify the bet).
- If the fix candidate is "scale up/out" → legitimate when the work is genuinely necessary and parallel (see system-design); a subsidy when the work is waste (the N+1 at 4× the instance size is still an N+1, now with a bigger bill) — profile before paying.
- If the win requires algorithmic change vs micro-tuning → check n first: O(n²) at n=50 is fine forever; the constant-factor fix on the O(n log n) path may beat the elegant rewrite (big-O guides at scale; measurement decides at your n).
- If two candidates tie → take the one that *deletes* complexity over the one that adds it; ties broken by maintenance cost, not cleverness.
- If the regression arrived suddenly → that's debugging, not optimization: diff what changed (deploy, data volume crossing an index threshold, a dependency's behavior — see production-debugging: what changed; postgres: the query plan that flipped).
- If the optimization is for a benchmark nobody experiences (the synthetic 100-concurrent-writes case; the cold-start that happens once a day) → name the audience honestly; optimizing the unexperienced path is résumé-driven performance work.

## Heuristics

- The profiler's biggest bar is the only opinion that matters; yours is a hypothesis it will usually embarrass.
- Know the latency ladder by heart (memory ~100ns, SSD ~100µs, same-DC network ~1ms, cross-region ~100ms, disk-backed DB query ~1–10ms warm): most wins come from moving work *up* the ladder or off it entirely (see system-design five numbers).
- Count round trips before counting instructions: one query returning 100 rows beats 100 queries returning one, by two orders of magnitude, in every stack ever built (see postgres N+1; api-design batching).
- Percentiles over averages, always — and watch the p99 *of your best customers* specifically (heavy users have heavy data; the slowest experience often maps to the biggest account — see data-tables at scale).
- Measure with production-shaped data: the dev dataset with 200 rows will happily hide every index miss, cache stampede, and O(n²) in the codebase.
- Warm-up and variance are part of the measurement: single-run benchmarks lie; report medians across runs, note the cold path separately (see memory-leaks: observation windows match phenomena).
- The second-fastest code is usually the simplest that meets budget — take it; the fastest version's extra 8% costs you at every future change.
- Beware the optimization that helps p50 and hurts p99 (bigger batches, deeper caches, aggressive prefetch): tail users pay for median users' speed — check both before declaring victory.
- Cloud bills profile like latency: find the biggest line item first (it's usually egress, logs nobody reads, or the over-provisioned tier — see observability log costs), apply the same delete>cache>defer hierarchy to dollars.
- Build-time and CI are performance surfaces with the same method (see ci-cd: attack pipeline latency like a perf problem) — profile stages, fix the biggest bar, cache dependencies, parallelize honestly.
- If you can't explain *why* the fix worked, you haven't finished: unexplained wins regress unexplained (the mechanism is the pin — see root-cause-analysis: verify the mechanism, not just the symptom).

## Quality Checklist

- [ ] Target anchored: metric, percentile, budget, and the user/bill reason for the number.
- [ ] Worth-it check done: the win's value stated against the effort's cost.
- [ ] Baseline measured under representative conditions and recorded.
- [ ] End-to-end profile identifies the biggest bar; effort matches it.
- [ ] Candidates ran the hierarchy (delete/cache/defer/batch) before micro-tuning.
- [ ] One change per measurement; every claimed win has before/after numbers under identical conditions.
- [ ] Non-improving changes reverted, not kept as vibes.
- [ ] p99 checked alongside p50; best-customer path checked specifically.
- [ ] Budget met → stopped; remaining opportunities written to the ledger.
- [ ] Wins pinned (benchmark/alert); tricks documented where they live.

## Failure Modes

- **Optimization by instinct**: two weeks rewriting the parser that profiling would have shown at 3% of runtime; the actual cost was the unindexed `ORDER BY` — the iron law skipped, the payoff Amdahl-capped at invisible.
- **No stopping criterion**: the endpoint hits 300ms against a 500ms budget and the tuning continues — pride-driven engineering burning weeks on margins no user perceives, while the backlog ages (see product-thinking: opportunity cost).
- **The unmeasured win**: "this should be faster" merged without numbers; three such PRs later the system is more complex and *slower*, and nobody knows which change did it (one variable, before/after — both skipped).
- **Cache-as-reflex**: the slow query wrapped in a cache instead of fixed — now it's fast, stale, stampede-prone, and the invalidation bug is a support ticket generator (see caching: a cache is not a fix, it's a trade); the query was one index away from not needing any of it.
- **Benchmark theater**: the synthetic benchmark (tiny data, no concurrency, warm everything) proves the win; production (skewed data, contention, cold paths) refunds it — measurement conditions weren't representative, so the measurement measured nothing.
- **Tail sacrifice**: batching and buffering that improve the average while pushing p99 past timeout thresholds — the dashboard improves, the biggest customer's experience degrades, and the correlation surfaces a quarter later (percentiles, unchecked).
- **Premature optimization as architecture**: complexity bought before any measurement existed — the sharded-from-day-one system serving 200 users (see system-design: scale costs paid on spec), carrying distributed-systems taxes forever against a load that never came.
- **The unpinned win**: the hard-won 400ms→150ms path regresses to 380ms across six unrelated PRs, invisibly — no benchmark guarded it, so entropy took it back on the installment plan.

## Edge Cases

- **Cold starts and warm-up cliffs**: JITs, connection pools, caches, and serverless containers make the first-N requests a different system — measure cold and warm as separate distributions, and decide which one your users actually experience (the daily-cron user lives entirely in cold-start land; see frontend-performance for the first-load twin).
- **Coordinated omission**: naive load-test clients wait for slow responses before sending the next request, systematically under-counting the pain during stalls — the classic measurement bug that makes terrible tails look fine; use load tools that account for it, and distrust suspiciously smooth p99s.
- **The optimization that shifts cost, not removes it**: moving work client-side (see frontend-performance: someone still pays), pushing load to a downstream service, or trading CPU for memory until the OOM killer arbitrates (see memory-leaks) — profile the *system*, or the win in your component is an invoice in someone else's.
- **Data-dependent performance**: the algorithm fine at uniform data and quadratic on the skewed real thing (the celebrity-follower problem, the one tenant with 2M rows — see postgres skew; system-design hot keys) — representative data isn't a nicety, it's the difference between testing your system and testing a different one.
- **GC and allocation rhythms**: throughput fine, tail ruined by collection pauses — the profile that samples CPU misses time spent *not running*; watch pause metrics and allocation rates as their own dimension (see memory-leaks; concurrency-bugs for the pause-that-looks-like-a-hang).
- **Mobile and low-end reality**: your p95 measured from the office wifi and an M-series laptop is another planet from a mid-range Android on hotel wifi (see frontend-performance: test on the devices users own) — the budget must name its device/network floor, or it's a budget for employees.
- **Optimizing the measurement itself**: instrumentation overhead (verbose tracing, sampling profilers in hot loops, debug logging) can *be* the biggest bar — the observer effect is real at the millisecond scale; measure with production-level instrumentation, and check what the instruments cost (see observability sampling).
- **When the budget itself is wrong**: sometimes the honest finding is that no engineering meets the budget at acceptable cost (physics — cross-region light-speed; economics — the vendor's latency floor) — the escalation is a *requirement* negotiation, not a heroic tuning campaign (see first-principles: constraint tagging; decomposing-ambiguity: route the essential decision).

## Tradeoffs

- **Latency vs throughput**: batching raises throughput and adds latency; the right point depends on which the user experiences (interactive paths buy latency; pipelines buy throughput — see async-processing) — optimizing one blindly degrades the other.
- **Speed vs memory**: caches, indexes, denormalization, and precomputation all trade space for time — priced correctly until memory pressure becomes the new bottleneck (eviction storms, GC pressure, swap death); the trade has a budget on both sides.
- **Simplicity vs the last 20%**: the boring fix gets you to budget; the clever one gets 20% past it and costs every future maintainer — take clever only when budget *demands* it, quarantined and documented (see abstraction-and-simplicity: the clever-vs-boring trade, verbatim).
- **Read vs write optimization**: every index, materialized view, and denormalization taxes writes to speed reads (see postgres) — profile which side your load actually skews toward before buying; write-heavy systems wearing read-optimized schemas pay twice.
- **Freshness vs speed**: the staleness budget is a product decision wearing an engineering costume (see caching staleness budgets; first-principles: "what if it didn't need to be real-time?") — the cheapest performance win in many systems is an honest conversation about how fresh the data must be.
- **Engineering time vs hardware money**: at small scale, the bigger instance beats the two-week optimization on pure ROI (hardware is cheap, engineers aren't); at large scale the multiplication flips (1% of a fleet is real money) — do the arithmetic per case instead of holding a doctrine (see system-design cost thinking).

## Optimization Strategies

- Make profiling ambient, not episodic: continuous profilers and always-on tracing (see observability) turn "we should profile" from a project into a lookup — the teams with profiles on tap optimize 10× cheaper because step 3 is already done.
- Maintain performance budgets in CI for the paths that matter (see ci-cd): the p95 gate on checkout, the bundle-size gate (see frontend-performance), the build-time gate — with honest flake-tolerance, so regressions cost a red build instead of a quarter's slow drift.
- Keep the performance ledger: each optimized path with its budget, current number, pinned benchmark, and known remaining opportunities — the map that makes the next regression a diff instead of an expedition (see technical-writing: the living doc).
- Practice the estimation arithmetic until it's reflexive: back-of-envelope (calls × cost-per-call against the latency ladder) before building *anything* — experts often skip the profiler for the first pass because the arithmetic already found the impossible number (see system-design five numbers; the profiler then confirms).
- Run load tests as rehearsals before the traffic arrives (launches, seasonal peaks — see planning-and-estimation: the known cliff), with production-shaped data and coordinated-omission-aware tooling; the cliff you find in rehearsal costs a config change, the one you find live costs an incident (see production-debugging).
- Review "faster" claims in PRs like security claims (see code-review): where's the measurement, what were the conditions, what's the complexity price — the team norm that kills vibes-optimization at the source.

## Self Review

- What exactly is the budget, and who or what does the current number actually hurt?
- Did I profile before I hypothesized — or am I about to optimize my guess?
- What share of the total does my target component hold — and what's the Amdahl ceiling on my planned win?
- Did I try to delete, cache, defer, or batch before making anything faster?
- Are my before/after numbers from identical, production-shaped conditions — and is the delta attributable to exactly one change?
- What happened to p99 while I was improving p50 — and to the biggest customer's path specifically?
- Am I past budget and still tuning? What is the next feature this time is being taken from?
- What pins this win against the next six months of unrelated PRs?

## Examples

**1. The dashboard that didn't need the rewrite.**
"The analytics dashboard is slow — we should rewrite the aggregation service in Rust" (instinct, meet iron law). Budget negotiated first: p95 dashboard load < 2s (currently 11s). End-to-end trace (see observability): aggregation service = 400ms; the other 10.6s = the frontend firing 43 sequential API calls, one per widget-metric pair (round trips, not computation — the ladder heuristic). Fixes in hierarchy order: 12 calls deleted (widgets below the fold — lazy-loaded; see frontend-performance), the rest batched into one endpoint (see api-design), responses cached 60s with an honest staleness budget the PM approved in one Slack message (see caching; freshness tradeoff). Result: p95 = 1.4s, budget met, tuning stopped. The Rust rewrite would have optimized 400ms of an 11-second problem — Amdahl's arithmetic, ignored, is a quarter of wasted work.

**2. The N+1 wearing a bigger instance.**
The orders API degrades monthly; the standing fix has been instance upsizing (4× the original size, 4× the bill — scale-as-subsidy). A profile with production-shaped data (staging's 200-row dataset had hidden everything) shows 92% of request time in the database: one ORM association loading line items per-order — 1 + N queries, N growing with the business (see postgres N+1). Fix: eager-load with a join, one query — p95 drops 3.1s → 240ms *on the original instance size*. The instance downsizes; the bill drops below where it started. Pin: a query-count assertion in the endpoint's test (regressions to N+1 now fail CI — see ci-cd) and a p95 alert (see observability). Total time including the profile: one day. The subsidy had been running for a year.

**3. The tail that averages hid.**
Search "feels slow" for enterprise customers; the dashboard says p50 = 180ms — green. Percentile discipline: p99 = 8.2s, and the slow requests correlate with the largest tenants (data-dependent performance: the skew edge — biggest customer, biggest index, slowest experience). Profile of the slow cohort: a filter clause unindexed *for one query shape* that only large tenants hit (small tenants' data fit the fast path). Fix: a partial index shaped for the heavy-tenant query (see postgres); p99 → 400ms. Second finding from the same investigation: the batch-prefetch added last quarter had improved p50 by 30ms while *adding* 800ms to p99 (tail sacrifice, unmeasured at the time) — reverted, since it had never been pinned or priced. Two lessons institutionalized: percentile dashboards split by tenant size, and "faster" PRs now require both p50 and p99 before/after (see code-review).

**4. Stopping, on purpose, in writing.**
Checkout p95: 620ms against a 500ms budget. Iteration one: the biggest bar is a synchronous fraud-check call (38% of request) — moved to a parallel call joined before the final commit (see async-processing) → 430ms. Budget met. The profile shows the *next* opportunities (serialization 11%, a redundant address validation 9%) and the temptation is real — projected floor ~340ms. The expert move: stop; ledger the remainder ("known ops: serializer swap ≈ -45ms medium effort; dedupe validation ≈ -35ms small effort — revisit if budget tightens"), pin the win (p95 alert at 500ms, benchmark on the fraud-call path), and return two backlog features to the sprint. Four months later the budget tightens to 400ms for a market launch — the ledger turns that request into a two-day task instead of a re-expedition (see technical-writing: the doc that answers in one link).

## Evaluation Rubric

Score 1–10:

- **1–2**: Optimization by instinct and folklore; no budgets, no profiles, no before/after; caches as reflex; wins claimed in adjectives; complexity accreting with each "should be faster."
- **3–4**: Occasional profiling but effort still follows interest; averages only; measurement conditions unrepresentative; no stopping criterion; wins unpinned and quietly regressing.
- **5–6**: Anchored budgets; profile-first discipline; biggest-bar targeting with one-change-per-measurement; hierarchy (delete/cache/defer/batch) run before micro-tuning; p99 checked.
- **7–8**: Full checklist: worth-it analysis before engineering, production-shaped measurement, non-wins reverted, budget-met stopping honored with a ledger, wins pinned by benchmarks and alerts, tricks documented in place.
- **9–10**: Additionally: ambient profiling and CI performance budgets standing; back-of-envelope arithmetic reflexive before building; load rehearsals before known peaks; cost optimized with the same method as latency — and the cultural tell: "faster" claims without numbers don't survive review here, and neither does tuning past budget.
