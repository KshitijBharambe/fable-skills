# Resilience Engineering

## Purpose

Design systems that degrade instead of collapse when dependencies fail — timeouts on everything, retries that don't amplify outages, circuit breakers that fail fast, backpressure that sheds load before drowning, and graceful degradation that keeps the core working while the periphery burns.

## When to use

- Any service that calls another service, database, cache, or third-party API (i.e., all of them).
- Designing the failure behavior of a new integration or dependency.
- After an incident where a slow dependency took down the whole system, or a retry storm turned a blip into an outage.
- Reviewing code with network calls and no timeout, or `catch { retry }` anywhere.
- Capacity planning, load testing, or preparing for traffic events.

## Goals

- Every network call has a timeout, a retry policy (or an explicit no-retry decision), and a defined failure behavior.
- One slow or dead dependency degrades one capability — it never cascades into whole-system collapse.
- Overload sheds load deliberately (rejection, queues with bounds, priority) instead of collapsing throughput for everyone.
- Degraded modes are designed, named, and tested — not discovered by users during the incident.
- Failure paths are exercised regularly (tests, fault injection), because untested failure handling is decoration.

## Inputs

- The dependency graph: every downstream call, its criticality (hard vs soft dependency), and its real latency distribution (p50/p99).
- Traffic shape: normal load, spike patterns, and the ceiling the system must survive (not necessarily serve).
- Business priorities under duress: which capabilities must survive, which may degrade, which can vanish.
- Existing failure history: what actually breaks here (see production-debugging incident records; observability data).

## Outputs

- A per-dependency resilience spec: timeout, retry policy with backoff and budget, breaker thresholds, fallback behavior.
- A degradation ladder: named service levels ("full → no recommendations → read-only → static page") with triggers and owners.
- Load-shedding policy: what gets rejected first, what queues (bounded, with TTL), what never gets dropped.
- Failure-path tests and fault-injection runs proving the above (see testing-strategy: deny paths).

## Expert Mental Model

- **Failures cascade through waiting, and slow is worse than dead.** A dead dependency returns errors instantly; a *slow* one holds your threads, connections, and memory hostage — callers pile up, their callers pile up, and the whole graph tips over. Most large outages are queueing collapses, not crashes. This is why the timeout is the foundational control: it converts "slow" (contagious) into "failed" (handleable). No timeout = your availability is the *minimum* over every dependency's worst day.
- **Retries are load multipliers pointed at a sick system.** A dependency at 100% capacity fails half its requests; naive clients retry; it now faces 1.5–3× load and fails harder; more retries — the retry storm *is* the outage. Retries are only safe with: exponential backoff + jitter (desynchronize the herd), a retry *budget* (retries as a bounded % of traffic, not per-request heroics), idempotency on the retried operation (see async-processing; api-design idempotency keys), and retrying only retryable errors (timeouts and 503s, never 400s). One retry layer per stack — retries at client, gateway, service, and driver multiply into 81 attempts nobody designed.
- **Circuit breakers convert repeated failure into fast failure.** After N failures in a window, stop calling — fail immediately (or serve the fallback), probe occasionally (half-open), close when healthy. The breaker protects *both* sides: the sick dependency gets breathing room to recover; your service stops burning threads on doomed calls. Without breakers, every request pays full timeout on a dead dependency — 30 seconds of held resources apiece to learn what the last thousand requests already knew.
- **Backpressure: match intake to capacity, or the system chooses collapse for you.** Every system has a capacity; the only question is what happens above it. Unbounded queues *are* the failure mode — they convert overload into unbounded latency, then memory exhaustion, then total collapse serving nobody (see async-processing: bounded queues, DLQs). The disciplined system knows its capacity (measured — see optimization-method), bounds every queue, and rejects excess *early and cheaply* (a fast 429 at the edge costs microseconds; the same request dying deep in the stack cost everything it touched on the way down). Goodput under overload is the metric: a system shedding 30% serves 70%; a system shedding nothing serves 0%.
- **Graceful degradation is a product decision compiled into architecture.** "When recommendations are down, show bestsellers; when search is down, browse still works; when the DB is down, serve cached reads and queue writes" — each of these is a *designed* answer to "what matters most here?" (see product-thinking). Distinguish hard dependencies (can't function without: the database of record) from soft ones (feature-enhancing: the recommendation engine) — then enforce the distinction in code, because every soft dependency treated as hard is availability donated for nothing. Static fallbacks, caches serving stale (see caching: stale-while-revalidate as resilience), feature flags as kill switches — the ladder's rungs.
- **Redundancy only helps against uncorrelated failure.** Two instances in one rack, two replicas on one config pipeline, two services sharing one connection pool — redundancy theater; they fail together (see judgment-under-uncertainty: correlated failures). Real fault isolation partitions blast radius: bulkheads (separate pools/queues per dependency class, so the slow vendor API can't starve the checkout path), cell architectures (shard-per-customer-group, so an outage hits 5% of users not 100%), zone/region spread for infrastructure. Ask of every redundant pair: what do they *share*?
- **Untested failure paths don't exist.** The fallback that's never run, the breaker that's never tripped, the failover that's never exercised — these are hypotheses wearing production configs (see refactoring: the unrehearsed revert, same law). Fault injection — kill the dependency in staging, inject latency, run the game day — is how failure handling graduates from decoration to capability.

## Workflow

1. **Draw the dependency graph and classify each edge**: hard or soft, sync or async, criticality, current latency distribution and error behavior (see system-design; observability for the data).
2. **Set timeouts everywhere, from the caller's budget down**: end-to-end budget (e.g., 2 s for the page) allocated down the call tree — each hop's timeout < remaining budget, deadlines propagated so a doomed request stops working. Base per-hop values on measured p99, not vibes.
3. **Define retry policy per edge**: retryable errors only, exponential backoff with full jitter, capped attempts, a global retry budget, idempotency verified before any retry on writes (see async-processing). Explicitly mark the no-retry edges (non-idempotent writes without keys, user-facing latency budgets already spent).
4. **Add circuit breakers on unreliable or critical edges**: failure-rate threshold over a window, open → fallback (not exception, where a fallback exists), half-open probes, metrics on state transitions (see observability — breaker flips are events worth alerting on).
5. **Design the fallback per soft dependency**: cached last-good value, static default, feature hidden, queued-for-later — and make the *absence* of a fallback an explicit decision for hard dependencies.
6. **Bound every queue and pool**: connection pools sized to measured capacity, queues with length limits and item TTLs (serving a request that timed out client-side 30 s ago is pure waste), and rejection behavior defined at each bound.
7. **Implement load shedding at the edge**: rate limits per client/tenant, priority classes (health checks and payments above analytics), cheap rejection (429 + Retry-After) before expensive processing.
8. **Build the degradation ladder as switches**: feature flags/kill switches per soft capability, wired and reachable during incidents (see deployment: flags; production-debugging: mitigation levers) — the incident commander flips a named switch, not edits code.
9. **Test the failure paths**: unit/integration tests for timeout-retry-breaker-fallback behavior (see testing-strategy deny paths), fault injection in staging (latency, errors, dependency death), and periodic game days on the scariest scenarios.
10. **Instrument the resilience layer itself**: retry rates, breaker states, shed counts, fallback serve rates, queue depths — these are your early-warning system and your incident dashboard (see observability).

## Decision Tree

- If adding any network call → timeout (from the budget), error mapping, and an answer to "what does the user see when this fails?" — before merge, not after the incident.
- If the call is to a soft dependency → wrap with breaker + fallback; the feature disappears or degrades, the page ships.
- If the call is to a hard dependency → timeout + bounded retries with jitter; past that, fail the request *fast and clearly* (see interface-states for the user surface) — a hard dependency down is an incident, not something to paper over.
- If retrying a write → idempotency key or provable idempotency first (see async-processing); otherwise no retry — duplicate payments cost more than failed ones.
- If a dependency is slow but not down → this is the dangerous case: latency-based breaker criteria (p99 over threshold counts as failure), hedged requests for read-heavy idempotent paths (send a second attempt at p95, take the first answer) — and never let one slow edge's pool starve the others (bulkhead it).
- If traffic exceeds capacity → shed by priority at the edge; if the queue is growing monotonically → you are past capacity, and the queue is converting overload into a worse outage — cap it and reject.
- If the same work arrives repeatedly (thundering herd after cache expiry or restart) → request coalescing / singleflight, staggered cache TTLs with jitter (see caching stampede protection), warmup before serving.
- If designing for a dependency you can't test against (third-party prod) → build the fake with failure modes (see testing-strategy: contract tests + fakes), and verify your handling against the fake's worst behaviors.
- If everything is "critical" per stakeholders → it isn't; run the exercise "which failure loses the most in 30 minutes" (see product-thinking prioritization) — the degradation ladder *is* the priority list, decided calmly.
- If an incident revealed a cascade → the postmortem's fix is structural (missing bulkhead, unbounded queue, absent breaker), not "tune the timeout" (see root-cause-analysis: class over instance).

## Heuristics

- No timeout is an infinite timeout; a default timeout is somebody else's guess about your budget. Set both connect and request timeouts, explicitly, everywhere.
- Timeouts shrink as you go deeper: caller 2 s → service 1.5 s → DB query 1 s — inverted timeouts (inner > outer) mean inner work continues after the caller gave up.
- Jitter is not optional: synchronized retries from a thousand clients are a scheduled DDoS against your own recovering dependency.
- Retry budget over retry count: "retries ≤ 10% of request volume" caps amplification globally; per-request counts don't.
- The breaker's fallback should be cheaper than the call it replaces — a fallback that queries another struggling system is a cascade with extra steps.
- Bound every buffer: pool, queue, batch, in-flight set. Every unbounded structure between two systems is a landmine with a memory fuse.
- Reject early, reject cheap: the best place to drop excess load is the first line of code that can identify it.
- Health checks lie in both directions: shallow checks (port open) miss brokenness; deep checks (touch the DB) turn one dependency's blip into "everything unhealthy" and mass restarts. Check *own* functionality, report dependency status separately.
- Stale beats absent for most reads: a 5-minute-old recommendation list is indistinguishable from fresh; design caches to serve stale on backend failure (see caching).
- Fail open or fail closed is a per-feature decision: rate limiter down → usually fail open (availability); auth down → always fail closed (see auth; security). Decide before the incident does.
- Watch queue *depth trends*, not just error rates: growing depth is the outage announcing itself minutes early (see observability).
- The second system you add for resilience (failover DB, backup queue) doubles your failure modes until it's regularly exercised — untested redundancy is negative reliability.

## Quality Checklist

- [ ] Every network call: explicit timeout, mapped errors, defined user-visible failure behavior.
- [ ] Retries: backoff + jitter, capped, budgeted, idempotent-only, single layer in the stack.
- [ ] Breakers on unreliable/critical edges with fallbacks and state metrics.
- [ ] Hard vs soft dependencies classified; soft failures provably don't fail the request (tested).
- [ ] All pools and queues bounded, with TTLs and defined rejection behavior.
- [ ] Load shedding by priority at the edge; goodput-under-overload verified by load test.
- [ ] Degradation ladder documented with named switches, reachable mid-incident.
- [ ] Deadline propagation across service hops.
- [ ] Failure paths covered by tests and fault injection; scariest scenario game-dayed within recent memory.
- [ ] Resilience metrics (retry rate, breaker state, shed count, queue depth) dashboarded and alerted.

## Failure Modes

- **The missing timeout**: one vendor API hangs; every thread in the pool ends up parked on it; the service that "just calls an API" is down entirely. The outage report says "vendor issue"; the actual cause is the infinite timeout.
- **The retry storm**: dependency stumbles; every layer retries 3×; load quadruples; the stumble becomes a collapse; recovery is impossible until someone turns the clients off. Self-inflicted DDoS.
- **The unbounded queue**: intake exceeds capacity; the queue "absorbs" it; latency grows to minutes; memory exhausts; the crash loses everything queued — the system chose the worst failure mode because nobody chose one.
- **Cascade by shared pool**: the slow reporting endpoint exhausts the same connection pool checkout uses; a nice-to-have takes down the money path. The missing bulkhead.
- **Fallback to a fantasy**: "on cache miss, hit the DB" as the resilience plan — the cache failing *is* the DB's worst day arriving all at once (see caching: the cold-start stampede).
- **Deep health checks + orchestration**: DB blips; every instance reports unhealthy; the orchestrator restarts the fleet; a 30-second blip becomes a 20-minute rolling outage.
- **Retrying the non-idempotent**: timeout on a payment call retried "to be safe" — the customer is charged twice; the resilience mechanism created the incident (see async-processing idempotency).
- **The untested failover**: the standby that was never promoted, the replica that silently stopped replicating months ago, the DR region whose config drifted — discovered at the exact moment they were needed.
- **Degradation nobody designed**: overload arrives; instead of a chosen ladder, the system serves random 500s across all features equally — full collapse for everyone instead of full service for most.

## Edge Cases

- **Startup and recovery herds**: a recovering service faces cold caches, connection re-establishment storms, and the backlog — the moment of maximum fragility; slow-start (gradual traffic ramp), cache warming, and backlog TTLs (drop what's too old to matter) make recovery survivable (see deployment: progressive rollout is the same shape).
- **Breakers on low-traffic edges**: failure-rate math misbehaves at 3 requests/minute (one failure = 33%); use minimum-volume thresholds and longer windows, or accept timeouts without breaking.
- **Multi-tenant fairness under shedding**: global rate limits let one tenant's spike consume everyone's budget — per-tenant limits and isolation are resilience *and* product fairness (see system-design multi-tenancy; api-design rate limits).
- **Websockets and long-lived connections**: a restart disconnects everyone at once; reconnection storms hit like a launch event — jittered reconnect backoff on clients, connection draining on servers (see deployment), and capacity for the reconnect wave, not just steady state.
- **Batch/cron collisions**: the nightly job and the traffic spike sharing a database — resilience includes scheduling; batch work needs its own limits and yield-under-contention behavior (see async-processing; postgres).
- **Third-party outages with no fallback**: the payment provider is simply down — degradation here is *queuing intent* (accept the order, charge asynchronously with idempotent retry, message the user honestly — see interface-states; event-driven) rather than pretending a fallback exists.
- **Regional failover with state**: stateless compute fails over easily; the data layer is the hard part — replication lag means failover trades availability against consistency (split-brain, lost writes); the RPO/RTO decision is a business decision to make before the region dies (see system-design).
- **The resilience layer's own bugs**: breaker config that opens on deploys (deploy = brief errors = open breaker = fallback storm), retry code with an off-by-one storming at exactly the wrong time — resilience machinery is code; test it like the critical path it is (see testing-strategy).

## Tradeoffs

- **Resilience machinery vs complexity**: every breaker, bulkhead, and fallback is code, config, and a new way to misbehave (see abstraction-and-simplicity) — apply depth where blast radius justifies it (money paths, core reads), accept simple timeout-and-fail elsewhere. A three-service startup needs timeouts and bounded pools, not a service mesh.
- **Fail fast vs mask failure**: aggressive fallbacks keep UX smooth and hide dependency sickness from operators (the breaker serving stale for three days unnoticed) — every fallback serve must be *loud in telemetry* even when silent in UX (see observability).
- **Retry persistence vs latency budget**: more retries raise success rates and burn user patience; often correct: zero synchronous user-facing retries (fail fast, let the human decide) and patient async retries in the background (see async-processing).
- **Shedding fairness vs business priority**: pure FIFO under overload is fair and serves nobody well; priority classes serve the business and starve someone — make the starvation order an explicit product decision, not an emergent one.
- **Consistency vs availability under partition**: the classic — serve stale/queued (available, eventually consistent) or refuse (consistent, unavailable); per-operation, not per-system: reads usually degrade to stale, money writes usually refuse (see event-driven; system-design).
- **Static stability vs dynamic reaction**: autoscaling and adaptive limits react to load but react late and can flap during the exact chaos they're meant to absorb; pre-provisioned headroom is dumb, boring, and works instantly — buy headroom for the predictable, automation for the gradual.

## Optimization Strategies

- Standardize the resilience layer in one place: a shared client wrapper / mesh policy where timeout, retry, breaker, and metrics come free and consistently — per-team hand-rolled policies drift into the four-layer retry stack (see the same centralization instinct in security enforcement points).
- Load-test to the breaking point, not to the target: the goal is *knowing* the ceiling and verifying degradation kicks in — a system that's never been broken in staging will demonstrate its collapse mode in production.
- Run game days on a calendar: kill the cache, null-route the vendor, inject 500 ms on the DB — each drill either proves a fallback or files a bug; both are wins (see production-debugging: rehearsed incident muscle).
- Make fallback serves and breaker opens first-class metrics with budgets: "recommendation fallback > 1% for 1 h" pages someone — degraded-and-forgotten is the quiet failure mode of good resilience.
- Chaos-test the config, not just the code: the timeout set in four places, the retry policy per environment — config drift is where resilience silently rots (see deployment: config as code).
- Review new dependencies with the resilience spec as intake: no edge enters the graph without timeout/retry/fallback decisions written down — the cheapest moment to design failure behavior is before the first call ships (see research: vendor evaluation).

## Self Review

- For each call I just added: what's the timeout, what happens on failure, and what does the user see?
- If this dependency gets *slow* (not dead) — what holds my threads, and what stops the pileup?
- Are my retries idempotent, jittered, budgeted — and is mine the only layer retrying?
- What's unbounded between my intake and my capacity? (Find every queue and pool; name their limits.)
- Which of my dependencies are actually soft — and does the code know, or does everything fail everything?
- When did the fallback last actually run? The breaker last trip? The failover last fail over?
- Under 3× traffic, what does this system do — by design, or by accident?
- Is any resilience mechanism here masking a sickness that telemetry should be shouting about?

## Examples

**1. The bulkhead that saved checkout.**
An e-commerce backend calls: payments (hard), inventory (hard), recommendations (soft), a review-aggregation vendor (soft, flaky). Original design: one HTTP client, one connection pool. The vendor's API degrades to 20 s responses during a sale; the shared pool saturates with parked review calls; checkout — which never touches reviews — starts timing out. Post-incident redesign: per-dependency-class pools (bulkheads), the vendor edge gets a 800 ms timeout + breaker + "no reviews shown" fallback, recommendations get breaker + cached-bestsellers fallback, and hard edges get budgeted timeouts with deadline propagation. The vendor's next bad day: reviews vanish for 40 minutes, a dashboard annotation fires, checkout conversion doesn't move. The incident became a non-event by architecture (see system-design: isolation as the unit of blast radius).

**2. The retry storm, defused by budget and jitter.**
A mobile API's search backend blips for 90 seconds. Clients retry 3× immediately; the gateway retries 2×; the service's HTTP library retries 2× — a 90-second blip faces up to 18× amplification and stays down for 40 minutes under its own clients' love. Fixes: retries removed from gateway and library (one layer: the client), exponential backoff with full jitter and a 10% retry budget enforced at the edge, 429s with Retry-After during shedding, and the search edge gets a breaker serving cached recent-queries as fallback. The same blip next month: 92 seconds long, self-healed, page never fired. The postmortem's chart of "load offered vs load served" becomes the team's standard teaching artifact.

**3. Designing the degradation ladder before the launch.**
A ticketing platform expects a 30× spike at on-sale time. Instead of hoping: capacity measured by load test (the real ceiling: the seat-lock service at ~4k locks/s), then the ladder decided with product — Level 0 full service; L1: waiting room with honest queue position (intake bounded to measured capacity, excess queued at the edge with TTL); L2: browse-only for non-queue traffic (seat maps go static, personalization off via kill switches); L3: static status page, API 429s everything but the queue. Priority: purchase flow > queue > browse > everything else. Game-dayed twice, switches rehearsed. Launch day peaks at 22×: L1 engages automatically, ~8% of browse requests shed, zero purchase-path errors, goodput at 97% of the measured ceiling. The system was overloaded, and it *worked* — because overload had a design.

## Evaluation Rubric

Score 1–10:

- **1–2**: No timeouts; unbounded everything; naive retries everywhere; one dependency's bad day is a full outage; failure behavior is whatever the exceptions do.
- **3–4**: Timeouts on some calls (defaults, unexamined); retries without jitter or budgets; no breakers or bulkheads; degradation undesigned; failure paths untested.
- **5–6**: Explicit timeouts and disciplined retries on major edges; breakers with fallbacks on the flaky dependencies; queues and pools bounded; hard/soft classified; basic failure-path tests.
- **7–8**: Full checklist: deadline propagation, retry budgets, bulkheads by dependency class, edge shedding with priorities, degradation ladder with rehearsed switches, fault injection in the testing routine, resilience metrics alerted.
- **9–10**: Additionally: standardized resilience layer org-wide; load-tested to breaking with verified goodput; game days on calendar; fallback-serve budgets that page; new dependencies gated on resilience specs — and incidents on record where the machinery demonstrably turned a dependency failure into a footnote.
