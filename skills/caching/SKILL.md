---
name: caching
description: "Use when adding a cache (Redis, in-process, CDN, HTTP) to a measured hot path, protecting a fragile dependency, reviewing a 'just cache it' PR, or debugging staleness bugs — invalidation, stampede protection."
---

# Caching

## Purpose

Add caches (Redis, in-process, CDN, HTTP) that make systems faster without making them wrong — with invalidation designed before the cache exists, stampede protection built in, and honest answers about staleness.

## When to use

- A measured hot path is dominated by repeated identical work (same query, same render, same API call).
- Read:write ratio is high and some staleness is tolerable.
- Protecting a fragile dependency (rate-limited third-party API, expensive query) from repeated load.
- Reviewing a PR that adds "just cache it" to fix a performance problem.
- Diagnosing bugs that smell like staleness ("works after a while", "different answers per server").

## Goals

- Every cache has a stated invalidation strategy AND a TTL backstop.
- Cold cache is survivable: the system degrades, it doesn't die.
- Staleness bounds are explicit, written, and product-approved ("prices may be 60 s stale").
- Hit rate, latency, and stampede behavior are observable from day one.

## Inputs

- Profile evidence: what exact computation repeats, how often, how expensive.
- Staleness tolerance per data type, from product: seconds? minutes? never?
- Write patterns: what mutates the underlying data, from where (all writers must be known — this is the invalidation surface).
- Cardinality: how many distinct keys? key size × count = memory budget.
- Failure posture: what should happen when the cache is down or cold?

## Outputs

- Cache design doc per cached item: key schema, TTL, invalidation trigger list, staleness bound, stampede protection, memory estimate.
- Implementation with metrics (hit/miss/error rates, latency, evictions) and a kill switch (feature flag to bypass).
- Load test evidence: behavior at 0% hit rate.

## Expert Mental Model

- **Choose the invalidation strategy first, then decide if the cache is worth it.** "Cache invalidation is hard" isn't a joke — it's a design gate. If you can't enumerate every writer that mutates the data, you can't invalidate correctly, and TTL-only with a product-approved staleness bound is the honest design.
- **A cache is a bet that the past predicts the near future.** Hit rate is the bet's payout. Caching something with low repeat-access (per-user unique queries, long-tail keys) is memory spent on nothing — check access distribution before building.
- **TTL is a backstop, not a strategy — but it's always there.** Even with perfect event-driven invalidation, a TTL caps the damage of the invalidation bug you haven't found yet. Every entry expires, no exceptions.
- **The cache must not become load-bearing by accident.** If your database can't survive a cold cache (deploy, Redis restart, mass eviction), your real capacity is a lie and Redis is your single point of failure. Experts capacity-plan for miss storms.
- **Staleness bugs look like ghosts.** "User updated their name but the old one shows sometimes" — per-node in-process caches make this per-server-nondeterministic. The more cache layers, the more you need one coherent story of who invalidates what.
- **Cache at the highest layer that tolerates the staleness** (CDN > HTTP > app object > query) — higher layers save more work per hit — but invalidate from the lowest layer up.

## Workflow

1. **Prove the need**: profile first. Identify the repeated computation, its cost, its call rate, and its key distribution (top 100 keys = what % of traffic?). No profile, no cache.
2. **Get the staleness budget from product**, in seconds, per data class. Write it down. "Real-time" answers get pushed back with the cost delta.
3. **Enumerate all writers** of the underlying data — app servers, admin tools, jobs, other services, manual SQL. This list is your invalidation surface; every writer must trigger invalidation or the strategy is TTL-only by definition.
4. **Choose the pattern**: cache-aside (default: read→miss→load→set), with explicit invalidation (delete-on-write) where writers are enumerable, TTL-only where they aren't. Write-through/write-behind only for specialized write-shaping needs.
5. **Design keys**: `{namespace}:{version}:{entity}:{id}` (e.g. `search:v3:results:sha256(params)`). Version segment enables mass invalidation by bumping. Hash unbounded inputs. Include every input that affects the value (locale, tenant, flags) — missing dimensions = the classic wrong-user-data leak.
6. **Set TTL with jitter**: base TTL from the staleness budget, ±10–20% random jitter so co-populated keys don't expire in synchronized waves.
7. **Add stampede protection** on expensive keys: single-flight locking (one loader per key, others wait or serve stale) or stale-while-revalidate (serve expired value, refresh async). Mandatory for anything >100 ms to compute or with >100 concurrent readers.
8. **Prefer delete over update on invalidation** (delete-then-next-read-repopulates avoids write-race inconsistency), and invalidate *after* the DB commit, tolerating the small race or using versioned keys if it matters.
9. **Instrument**: hit rate, miss latency, error rate, eviction count, memory, per-key-family if possible. Add the bypass flag.
10. **Test the ugly paths**: cold start under load, cache down (does the app work, slowly?), invalidation on every writer path, concurrent write+read races.

## Decision Tree

- If the data is static assets or full pages varying only by URL → CDN/HTTP caching (`Cache-Control`, `ETag`), not application cache.
- Else if computation is per-request repeatable within one request → request-scoped memoization (no invalidation problem at all — prefer this when sufficient).
- Else if data is small, read constantly, staleness of seconds OK → in-process cache (LRU + TTL + max-size); accept per-node inconsistency or add pub/sub invalidation broadcast.
- Else if shared across nodes, or needs coordinated invalidation → Redis/Memcached cache-aside.
- Else if the underlying query itself can be made <5 ms with an index → fix the query, skip the cache.

Invalidation choice:
- If all writers are in one codebase → delete-on-write triggered in the write path (after commit) + TTL backstop.
- Else if writers are multiple services → event-driven invalidation off a change stream (CDC/outbox events) + TTL backstop.
- Else (writers unknowable: manual SQL, external systems) → TTL-only, with TTL = product-approved staleness bound.

Redis eviction policy:
- If it's a pure cache → `allkeys-lru` (or `allkeys-lfu`), never `noeviction`.
- If Redis also holds real data (queues, sessions) → separate instances; mixing cache and data in one eviction domain corrupts one or the other.

## Heuristics

- Target hit rates: >90% for object caches on hot entities; if under 50%, the cache is probably mis-keyed or the access pattern isn't cacheable — remove it.
- Never cache: authorization decisions past seconds, anything used to authorize writes, un-jittered rate-limit state, data where wrong = money/safety.
- Negative caching (cache "not found" for 5–30 s) prevents miss-storms from retrying clients hammering the DB for nonexistent keys — cap it short so creations appear.
- Big keys are Redis poison: a 5 MB value blocks the single-threaded event loop on every access; keep values <100 KB, split or compress beyond.
- `KEYS *` in production is an outage; use SCAN, and design key schemas so you never need pattern scans on the hot path.
- Hot-key skew: one celebrity key taking 100k reads/s bottlenecks one shard — replicate hot keys (`key:{1..N}` random read) or promote them to in-process cache.
- Serialize compactly and versioned: a deploy that changes the cached object's shape must either bump the key version or read-tolerate old shapes; otherwise deploys cause deserialization error storms.
- Cache misses should be visibly cheap in code review: if the miss path fans out to 30 queries, the cache is hiding an unfixed N+1.
- Redis maxmemory at ~75% of instance RAM (fragmentation + fork headroom for persistence).
- The bypass flag is not optional: when staleness bugs strike at 2 a.m., "turn the cache off and survive" is the mitigation.

## Quality Checklist

- [ ] Profiling evidence justifies each cache (cost × frequency × hit-rate projection).
- [ ] Written invalidation strategy per cache naming every writer path; TTL backstop on every key.
- [ ] Staleness bound stated and product-approved per data class.
- [ ] Key schema includes version segment and ALL value-affecting dimensions (tenant, locale, flags).
- [ ] Stampede protection on expensive keys; TTL jitter applied.
- [ ] Cold-cache load test passed: DB survives 0% hit rate (or a documented degrade mode engages).
- [ ] Metrics live: hit/miss/error/eviction/latency; alert on hit-rate collapse and eviction spikes.
- [ ] Kill switch tested.
- [ ] Eviction policy explicit; cache and durable data not sharing an eviction domain.
- [ ] Concurrent write/read race behavior analyzed (delete-after-commit; acceptable inconsistency window stated).

## Failure Modes

- **Stampede/thundering herd**: hot key expires; 5,000 concurrent requests all miss and all run the 2 s query; DB falls over; recovering DB faces the same herd. Missing single-flight is the cause; the outage signature is "everything fine until :00 past the hour."
- **Cache as hidden capacity**: system runs for months at 99% hit rate; Redis restarts; DB gets 100× its provisioned load and dies; cascading failure. Capacity planning assumed the cache.
- **Missing key dimension**: response cached by `user_id` but value depends on locale/feature flag/tenant → users see each other's data or wrong variants. This is the caching bug that becomes a security incident.
- **Invalidate-then-write race**: delete cache, then commit DB — a reader between the two repopulates the cache with the old value, which now lives until TTL. (Delete after commit; the reverse race is rarer and shorter.)
- **Update-in-place races**: two writers set the cache in opposite order to their DB commits; cache holds the loser. Delete-on-write sidesteps this class.
- **Unbounded in-process caches**: a dict-as-cache without max-size = slow memory leak dressed as an optimization.
- **Caching errors**: a transient upstream 500 gets cached as the value for an hour. Cache only validated successes (negative-cache deliberate not-founds, briefly).
- **Deploy-time shape mismatch**: new code can't deserialize old cached blobs (or worse, silently misreads them). No version segment in keys.

## Edge Cases

- **Zero vs missing**: cache returning `nil` — is that "not cached" or "cached value is null"? Encode explicitly (sentinel or wrapper) or negative caching corrupts logic.
- **Mass invalidation without mass outage**: bumping a version segment invalidates millions of keys instantly = herd. Pair version bumps with gradual rollout or pre-warming.
- **Read-your-writes UX**: user saves profile, next read hits stale cache, user sees old data and re-saves. Per-session write-through, cache-busting on the writer's next read, or short TTL on user-own data.
- **Clock skew with expiry-at timestamps**: prefer relative TTLs set by the cache server, not absolute expiry computed on app servers.
- **Fan-out invalidation**: editing one product invalidates product page, category page, search results, recommendations... enumerate the dependency graph or accept TTL staleness on derived views (usually the right call).
- **Pub/sub invalidation loss**: in-process caches invalidated via Redis pub/sub silently miss messages during reconnects — always pair with short TTLs.
- **Multi-get partial failures**: MGET of 100 keys where Redis times out — degrade to source for all, don't fail the request.
- **Warming vs organic fill**: after deploys, pre-warm the top-N keys (from yesterday's hot list) if cold-start herds are dangerous.

## Tradeoffs

- **Freshness vs load**: shorter TTLs = fresher + more DB load; the right TTL comes from the product staleness budget, not from engineering comfort. Make the tradeoff visible: "60 s TTL = X qps on DB; 5 s = 12X."
- **In-process vs distributed**: in-process is ~1000× faster (ns vs ms) but per-node inconsistent and memory-multiplied; Redis is coherent but adds a network hop and an infrastructure dependency. Common layering: tiny in-process L1 (1–5 s TTL) over Redis L2.
- **Delete vs update on write**: delete is race-resistant and simple but causes a miss (latency spike) per write; update keeps hit rate but invites ordering races. Delete by default; update only for write-heavy hot keys with careful versioning (compare-and-set with monotonic versions).
- **Stale-while-revalidate vs strict freshness**: SWR gives flat latency and stampede immunity at the cost of guaranteed-bounded staleness (one refresh interval). Excellent default for read-mostly views; wrong for anything transactional.
- **Cache complexity vs query fixing**: a cache added over a 500 ms query trades an index migration for a permanent invalidation liability. Fixing the query is a one-time cost with zero ongoing correctness risk — always price that alternative first.

## Optimization Strategies

- Rank by (miss cost × miss rate): fixing a 2 s computation at 80% hit beats micro-tuning a 5 ms one at 95%.
- Batch on the miss path: coalesce N concurrent misses for related keys into one bulk load (MGET + single DB query with IN).
- Use request-collapsing gateways/SWR at the HTTP layer for anonymous traffic before building bespoke app caching.
- Track per-key-family hit rates; delete cache code with <50% hit rate — dead caches cost memory, deploy risk, and reader confusion.
- Compress values >10 KB (LZ4/zstd): network + memory win at negligible CPU, especially for JSON blobs.
- Move from cache-per-query to cache-per-entity + composition where invalidation is drowning you: fine-grained entity caches invalidate precisely; page-level caches invalidate constantly.

## Self Review

- Can I list every code path that writes the underlying data, and show the invalidation each triggers? If not, did I fall back to TTL-only with an approved staleness bound?
- What exactly happens at 0% hit rate — did I test it, or am I hoping?
- Does my key include every dimension that changes the value? (Walk each: tenant, user, locale, flags, version.)
- What happens when two requests race a write: worst-case staleness duration?
- If the cached object's class/schema changes next deploy, what reads the old blobs?
- Is there a single expensive key whose expiry causes a synchronized herd? Where's its lock/SWR?
- Can I turn this cache off in production in under a minute?

## Examples

**1. Cache-aside with the full discipline (product pages).**
600 qps reads, 2/min writes, staleness budget 30 s (product-approved). Design: key `prod:v2:item:{id}:{locale}`; TTL 30 s ± 15% jitter; delete-on-write after commit from the two writer paths (admin API, bulk importer — enumerated); single-flight lock on load (SETNX + 5 s lock TTL, waiters serve stale-if-present else brief poll); values ~8 KB; hit rate lands at 97%; cold-start test shows DB at 40% CPU at 0% hit — survivable. Metrics + `cache.products.enabled` flag shipped same PR.

**2. The stampede postmortem pattern.**
Symptom: every hour at :00, 30 s of DB saturation. Cause: 200 dashboard keys all set with TTL 3600 at deploy time, expiring in lockstep; each triggers a 1.5 s aggregate query × hundreds of waiting requests. Fix: jitter TTLs (3600 ± 300), stale-while-revalidate for the aggregates (serve old, refresh in background singleton), and an alert on p95 miss-path latency. The graph flatlines.

**3. Wrong-dimension incident (the one to fear).**
Bug report: "I saw someone else's cart count." Cache key was `header:{page_id}` for a fragment that included user-specific cart badge — key missing `user_id`. First user to render after expiry populated the fragment for everyone. Expert practice that prevents it: key review rule — "read the render function; every variable it consumes is either in the key or provably constant." Fix + audit of all fragment caches for the same class; two more found.

**4. Choosing NOT to cache.**
Endpoint slow at 800 ms; proposal: Redis cache, 5 min TTL. Investigation: query does OFFSET pagination + missing composite index; access pattern is long-tail (each user hits unique keys — projected hit rate <20%). Decision: fix index + keyset pagination → 12 ms; cache rejected in review with the numbers attached. Caching would have added an invalidation surface to mask a fixable query while barely helping.

## Evaluation Rubric

Score 1–10:

- **1–2**: Caches added on vibes; no TTLs or infinite TTLs; no invalidation plan; unbounded in-process dicts; no metrics.
- **3–4**: Cache-aside used but keys missing dimensions; TTLs arbitrary; invalidation partial (main writer only); no stampede thought; hit rate unknown.
- **5–6**: Profile-justified; writers enumerated; delete-on-write + TTL backstop; jitter present; basic metrics; cold-cache behavior reasoned about but untested.
- **7–8**: Full checklist: staleness budgets approved, single-flight/SWR on expensive keys, cold-start load test passed, kill switch, eviction policy deliberate, race windows analyzed and stated.
- **9–10**: Additionally: layered caches with a coherent invalidation story; hot-key and big-key handling; per-family hit-rate tracking with pruning of dead caches; version-bump rollouts pre-warmed; the "should this be a query fix instead?" alternative priced in the design doc.
