# System Design

## Purpose

Design systems that meet their actual numbers — QPS, data volume, latency, availability — with the least machinery that works, scaling the parts that need it and leaving the rest boring.

## When to use

- Designing a new service, product backend, or major feature's architecture.
- An existing system approaches its limits (latency creep, capacity ceilings).
- Evaluating proposals: microservices splits, new datastores, event-driven rewrites.
- System design interviews or architecture reviews.
- Choosing where to spend reliability/scale effort next.

## Goals

- Requirements quantified before boxes are drawn: 5 numbers minimum (read QPS, write QPS, data size + growth, latency SLO, availability target).
- Every component justified by a number it satisfies; nothing added for imagined scale.
- Failure behavior designed per dependency: degrade, queue, or die — chosen, not discovered.
- The next bottleneck is known and the path past it sketched.

## Inputs

- Load numbers: current and 12–24 month projections (reads/sec, writes/sec, payload sizes, concurrent users, data growth).
- Latency and availability requirements from the product ("p95 < 300 ms", "99.9%"), with honest source (real requirement vs vibes).
- Consistency needs per operation: what must be read-your-writes, what tolerates staleness (see event-driven).
- Team reality: size, ops maturity, what they already run well.
- Cost envelope.

## Expert Mental Model

- **Five numbers change everything.** Read QPS, write QPS, data size, latency SLO, availability target. 100 QPS vs 100k QPS are different professions; 10 GB vs 10 TB pick different databases; 99.9% (8.7 h/year down) vs 99.99% (52 min) differ by roughly 10× engineering effort. Experts refuse to draw boxes until the numbers exist — and they do the arithmetic: 10M requests/day ≈ 116/sec average ≈ ~500/sec peak. Most systems are smaller than their architects feel they are.
- **Start with the data model and access patterns, not the components.** What are the entities, how are they queried, what's the read:write ratio, what's the working set size? The datastore and its schema fall out of access patterns (see postgres); the services fall out of ownership boundaries. Architecture drawn component-first ("we'll need a queue, a cache, a search cluster") is shopping, not design.
- **A monolith + Postgres + cache is the right answer far longer than architects admit** — comfortably into thousands of QPS and hundreds of GB with competent tuning. Every added component (queue, second datastore, microservice split) buys a capability and costs: an operational surface, a failure mode, a consistency boundary, and cognitive load forever. "Boring tech" bias is not conservatism; it's correctly pricing the machinery.
- **Scale reads and writes differently.** Reads scale by copying (cache → replicas → CDN — each layer trades staleness for capacity; see caching). Writes scale by *splitting*: async absorption (queues smooth spikes — see async-processing) and eventually partitioning/sharding — where the partition key is a one-way door: pick the key your access patterns already scope by (usually tenant/user), because cross-partition queries and resharding are the two costs you'll pay forever.
- **Every network hop gets the reliability quartet**: timeout (deliberate, not default), retry (with backoff + jitter, only on idempotent ops — see async-processing), circuit breaker (stop hammering the dying), and a fallback decision (degrade or fail). A dependency without these has decided your availability for you. Corollary: your availability is roughly the product of your hard dependencies' availabilities — every hard dependency at 99.9% multiplies in; making a dependency soft (degradable) is how you exceed your weakest link.
- **Design the failure modes, not just the happy path.** For each box: what happens when it's slow (worse than down — slow poisons callers via held connections), down, or wrong? Which failures degrade features (search down → browse still works) vs which stop the world (payments DB)? The blast-radius map is the architecture; the component diagram is its shadow.
- **Know your next bottleneck.** Systems don't scale evenly; something hits the wall first (usually the database, specifically writes to it). Experts can name the current ceiling ("~4k writes/sec on the orders table"), the symptom that will appear as it approaches, and the pre-sketched move past it. Architecture is a sequence of deliberate next-moves, not a final state.

## Workflow

1. **Extract the numbers**: the five above + payload sizes, working set, growth rate, peak:average ratio, and read:write ratio per major operation. Back-of-envelope everything (requests/day → /sec; rows × row-size → table size; QPS × payload → bandwidth).
2. **Write the access patterns**: top 5–10 operations with their frequency, latency need, and consistency need. This is the design's spec; everything answers to it.
3. **Design the data model** around those patterns (see postgres); choose the primary datastore by access shape (relational default; specialized stores only for proven shapes: search → inverted index, massive key-value at extreme scale, time-series at volume).
4. **Draw the simplest topology that meets the numbers**: often client → LB → app (stateless, N instances) → Postgres (+ read replica) + Redis + object storage + a job queue. Justify each box with the number it serves; delete boxes that serve imagined numbers.
5. **Apply the read-scaling ladder where reads exceed comfort**: app-level cache → replicas → CDN/edge for cacheable content — each with an explicit staleness budget (see caching).
6. **Apply write strategies where writes exceed comfort**: absorb spikes via queues (with the UX consequences designed — see interface-states), batch, then partition — choosing the shard key from access patterns and pricing cross-shard operations honestly.
7. **Wire the reliability quartet on every hop** with explicit numbers (timeout = p99 × small multiple; retry budget; breaker thresholds); classify each dependency hard vs soft and design the soft ones' degraded modes.
8. **Walk the failure drills on paper**: kill each box — what do users see? Where does data loss become possible? What's the recovery step and time? Fix the answers you can't accept; write down the ones you accept (risk register).
9. **Capacity plan with headroom**: provision for peak × 2–3; know the ceiling of each tier and the leading indicator (queue depth, replication lag, connection pool saturation) that says it's approaching — wire those into alerts (see observability).
10. **Document as decisions, not just diagrams**: the numbers, the rejected alternatives and why, the known next bottleneck and its planned move, the consistency budget per flow. This document is what makes the architecture reviewable and evolvable.

## Decision Tree

- If total scale fits one beefy Postgres + stateless app tier (most products, honestly) → monolith + managed Postgres + Redis + object storage + queue for background work. Stop adding things.
- Else if reads are the pressure →
  - Cacheable with staleness budget → cache layers/CDN (see caching).
  - Complex queries slow → fix queries/indexes first (see postgres), then read replicas (with read-your-writes routing), then precomputed views/denormalization (see event-driven CQRS-lite).
- Else if writes are the pressure →
  - Spiky → queue + async absorption (see async-processing).
  - Sustained beyond one primary's ceiling → partition by the dominant access scope (tenant/user/region); avoid scatter-gather queries by design.
- Else if the organization is the pressure (teams stepping on each other, deploy contention) → service extraction along *ownership* boundaries — one team, one service, one datastore — never along technical layers ("the API service, the DB service"). Extract the piece with the clearest boundary and the most independent change rate first.
- If someone proposes microservices for a <20-engineer team without an org-pressure or independent-scaling argument → challenge: you're buying distributed-systems problems (network failures, tracing, versioned contracts, eventual consistency) to solve a problem you don't have.
- If two services need the same data → decide: one owns it and serves it (API), or events replicate it (see event-driven) — never two writers to one table.
- If strong consistency is demanded across services → first challenge the requirement (usually it's per-aggregate, satisfiable within one service/DB); genuinely cross-service invariants → saga with compensation (see event-driven), accepting its complexity price consciously.
- If availability target ≥99.99% → multi-AZ active-active for stateless, carefully-chosen failover for state; every 9 past that multiplies cost — make the business sign the check.

## Heuristics

- Arithmetic beats adjectives: "high scale" means nothing; "800 writes/sec peak against a table that benchmarks at 5k/sec on this hardware" is a design input.
- Peak:average is typically 2–5× for consumer daily cycles; 10–100× for launch/event spikes — design for the ratio your product actually has.
- The database is the bottleneck until proven otherwise; stateless tiers scale by adding instances, state doesn't.
- Slow is worse than down: a 30 s hang holds threads/connections everywhere upstream; timeouts convert slow into fast-failure, which the quartet can handle.
- Fan-out multiplies: a request touching 5 services each at p99=100 ms has terrible tail latency (tail amplification) — cap the hop count on latency-critical paths; parallelize what you can't remove.
- Idempotency everywhere writes cross a network (see async-processing) — retries exist, therefore duplicates exist.
- One datastore per service; one writer per table; caches are copies, never sources of truth.
- Cross-region adds ~50–150 ms per hop and a consistency headache — go multi-region for data-residency or disaster requirements, not vibes.
- Estimate storage in years: rows/day × row size × 365 × 3 — if it's <1 TB, stop designing for "big data."
- Every queue needs a lag alert; every replica needs a lag alert; every pool needs a saturation alert — the leading indicators of the next bottleneck are always queue-shaped.
- Buy before build for undifferentiated machinery (auth, email, search, payments) until scale or differentiation proves otherwise.
- If the design document has no rejected alternatives, it's a description, not a design.

## Quality Checklist

- [ ] The five numbers + access patterns documented; arithmetic shown.
- [ ] Every component maps to a number or named requirement; no speculative boxes.
- [ ] Data model designed from access patterns; datastore choice justified against them.
- [ ] Staleness budget stated wherever reads are scaled by copying.
- [ ] Partition key (if any) chosen from access patterns; cross-partition operations enumerated and priced.
- [ ] Reliability quartet with explicit numbers on every network hop; hard vs soft dependency classification with degraded modes.
- [ ] Paper failure drills done per component; unacceptable answers fixed; accepted risks registered.
- [ ] Capacity headroom ≥2× peak; each tier's ceiling and leading indicator named and alerted.
- [ ] Next bottleneck identified with its planned move.
- [ ] Design doc includes rejected alternatives with reasons.

## Failure Modes

- **Resume-driven architecture**: Kafka + microservices + DynamoDB for 50 QPS — a distributed system's operational burden purchased to solve problems the team wishes it had.
- **Numbers-free design**: boxes drawn from analogy ("this is how Big Co does it") without QPS/size arithmetic; over-built where cheap, under-built exactly where the load actually lands.
- **The hidden hard dependency**: a "soft" analytics call made synchronously in checkout; analytics goes down, checkout goes down. Nobody decided that; the code did.
- **Shared database between services**: two teams writing one schema — coupling with none of the monolith's transactional benefits; every migration a cross-team negotiation; the worst of both worlds.
- **Scatter-gather sharding**: partition key chosen by ID convenience; every real query hits all shards; the shard count became a query multiplier instead of a divisor.
- **Cache as the load-bearing wall**: system survives only at 95%+ hit rate; a cold cache (deploy, flush) collapses the DB (see caching) — capacity was a lie.
- **Retry storms by default**: default retries × 3 layers = 27 requests per user action during a partial outage; the retries are the outage (see production-debugging).
- **The 99.999% nobody asked for**: heroic multi-region active-active for an internal tool with a 9-to-5 audience; the complexity causes more downtime than it prevents.
- **Design-by-diagram**: beautiful component chart, no failure drills, no consistency budget, no bottleneck plan — the architecture exists only in its happy path.

## Edge Cases

- **Hot keys/tenants**: one celebrity user or whale tenant concentrates load a partition scheme assumed uniform — plan for skew: hot-key replication, tenant isolation tiers, per-tenant limits (see caching hot keys, data-tables noisy neighbor).
- **Thundering herds on recovery**: everything reconnecting/refilling at once after an outage (metastable failure — see production-debugging); design reconnect jitter, connection backoff, and warm-up throttles *into* the system.
- **Data gravity in migrations**: the architecture evolves, the 5 TB doesn't — every "we'll just move to X" plan must include the online migration path (dual-write/backfill/verify — see legacy-migrations) or it's fiction.
- **Fan-out writes (social-graph shapes)**: one action → N followers' feeds; at high N, precompute-on-write flips to compute-on-read for whales — hybrid strategies by follower count are the standard answer.
- **Long-tail payloads**: median request 2 KB, p99.9 is a 40 MB upload on the same path — separate the paths (direct-to-object-storage with signed URLs) or the whale requests starve the small ones.
- **Cold start / empty system**: caches empty, autoscaler at minimum, JIT cold — launch-day and region-failover behavior differ from steady state; drill them.
- **Compliance boundaries**: data residency, PII isolation, audit trails can force topology (regional stacks, separate stores) harder than any QPS number — surface them in step 1, not month 6.
- **Clock skew**: any design step that says "order by timestamp across machines" needs a re-think (sequences, logical clocks, single-writer ordering — see concurrency-bugs fencing).

## Tradeoffs

- **Simplicity vs headroom**: the boring stack hits a real ceiling; the scalable stack taxes every day before the ceiling arrives. Price it by *time-to-retrofit*: choose simple where the migration path to the next stage is known and incremental (monolith → extract hot service; Postgres → add replicas → partition); choose complex upfront only where retrofit is catastrophic (partition keys, multi-region data models).
- **Consistency vs availability/latency** (the CAP-flavored trade as it actually appears): per *flow*, not per system — strong within the aggregate (one DB transaction), eventual across boundaries with UX designed for it (see event-driven). Paying strong-consistency costs where the product tolerates staleness is pure waste; the reverse corrupts data.
- **Latency vs throughput**: batching raises throughput and p50-hurts latency; pick per path (interactive paths unbatched, pipelines batched).
- **Buy vs build vs run**: managed services cost money and control, save ops and pages; self-run costs expertise-on-call. Managed by default; self-run where it's differentiating or the bill proves otherwise.
- **Duplication vs coupling across services**: sharing a library/schema couples deploys; duplicating logic drifts. For data: duplicate via events with an owner (see event-driven); for logic: duplicate small things, extract truly-stable shared kernels only.
- **Availability nines vs cost/complexity**: each nine multiplies effort; map nines to business impact per flow (checkout ≠ admin panel) and spend unevenly — uniform nines are uniform waste.

## Optimization Strategies

- Load-test the real topology to find the actual ceiling (not the guessed one) — a day of load testing beats a quarter of speculative scaling; test to *failure*, note the failure mode, that's your next-bottleneck document.
- Instrument the leading indicators first (queue depth, pool saturation, replication lag, p99 per hop) — capacity problems telegraph weeks ahead through these (see observability).
- Shorten the dependency chains on the latency-critical path:每 each removed hop cuts tail latency more than optimizing any single hop.
- Precompute what's read hot and computed cold (rollups, feeds, denormalized views) with an events-driven refresh (see event-driven) — the cheapest 10× read win after caching.
- Re-run the five-numbers exercise quarterly against reality: growth curves bend; the architecture's assumptions should be versioned and re-checked like dependencies.
- Practice the next move before it's urgent: the replica promotion, the shard split, the service extraction — game-day them at small scale so the real one is a rehearsal, not a premiere (see production-debugging).

## Self Review

- Can I recite the five numbers, and does every box in my diagram answer to one?
- What's my peak multiplier, and does the capacity plan cover peak × 2?
- For each dependency: timeout value? retry policy? breaker? degraded mode? Which are hard, and is my availability math honest about them?
- Kill each component on paper — what does the user see? Which answer am I ashamed of?
- Where is my consistency strong, where eventual, and does the product UX know?
- What breaks first as load doubles, what's the symptom, what's the move?
- What did I reject, and would a reviewer find the reasons in the doc?
- Is anything here for a load that exists only in the pitch deck?

## Examples

**1. The right-sized design (B2B SaaS, honest numbers).**
Numbers: 40k users, peak 300 QPS reads / 30 QPS writes, 200 GB growing 15 GB/mo, p95 < 300 ms, 99.9%. Design: monolith on 6 stateless instances behind an LB; Postgres (primary + 1 replica, replica for reports only — read-your-writes stays on primary); Redis (sessions + cache-aside on hot entities, staleness budget 30 s); S3-style storage for files; Postgres-backed job queue (SKIP LOCKED — see postgres) for email/exports. Quartet on the two external hops (payments, email) with degraded modes (queue-and-retry email; checkout fails closed with clear error). Rejected: microservices (no org pressure at 9 engineers), Kafka (30 writes/sec), DynamoDB (relational access patterns). Next bottleneck named: report queries at ~3× data — move: precomputed rollups. The doc's arithmetic fits on one page; that's the point.

**2. Scaling reads by ladder, with staleness budgets.**
Content platform: reads grow 10×; writes flat. Sequence executed over two quarters: (1) query/index fixes (p95 −40%, free); (2) cache-aside on article pages, 60 s budget signed by product (hit 94%); (3) CDN for anonymous pages (ETag revalidation, 5 min budget) — origin traffic −85%; (4) replica for logged-in personalized reads with LSN-based read-your-writes routing. Each rung added only when the previous one's ceiling showed in the leading indicators (origin QPS, cache hit, replica lag). No rung skipped, no rung premature; the DB never noticed the 10×.

**3. The partition-key decision done with fear (correctly).**
Multi-tenant analytics ingest approaching one primary's write ceiling (leading indicator: WAL throughput + lock contention trending 70%→85% over a quarter). Partitioning inevitable → the one-way door treated as such: access-pattern audit shows 98% of queries scope by `tenant_id`; whale analysis shows top tenant = 12% of volume (fits a shard; isolation tier planned for the next whale). Chosen: hash(tenant) → 16 logical shards mapped to 4 physical DBs (logical>physical from day one so future splits move mappings, not data schemas). Cross-tenant admin queries (2%) routed to a nightly-synced analytics replica instead of scatter-gather. The rejected alternative (shard by event time) is documented with its fatal flaw: every tenant query would touch every shard.

**4. Failure-drill on paper catching the hidden hard dependency.**
Pre-launch review of a checkout flow: kill each box exercise. "Kill recommendations service" → expected: no recs strip; actual (from code walk): checkout page *blocks* on it, 10 s default timeout, no breaker — a soft feature wired as a hard dependency. Fixes: 300 ms timeout, breaker, render-without-recs fallback; same drill then catches the email provider called synchronously post-payment (moved to the outbox/queue — see async-processing). Two availability incidents deleted for the cost of an afternoon with a whiteboard; the drill is now a launch-gate ritual.

## Evaluation Rubric

Score 1–10:

- **1–2**: No numbers; component shopping by fashion or analogy; happy-path-only; shared DBs between services; no failure thinking.
- **3–4**: Some load estimates; mostly-sane topology with speculative extras; timeouts/retries at defaults; consistency undesigned; no bottleneck plan.
- **5–6**: Five numbers + access patterns drive the design; boring-tech bias visible; quartet on major hops; paper failure drills done; staleness budgets stated.
- **7–8**: Full checklist: justified components, hard/soft dependency map with degraded modes, partition decisions access-pattern-driven, headroom + leading indicators alerted, rejected alternatives documented.
- **9–10**: Additionally: load-tested to failure with the next bottleneck and move named; nines spent unevenly by business impact; migration paths (not just end states) designed; quarterly assumption re-checks scheduled; the doc lets a new senior engineer operate and evolve the system without oral tradition.
