---
name: memory-leaks
description: "Use when memory grows to OOM, services need periodic restarts, latency degrades over hours, or hitting 'too many open files'/pool exhaustion/rising thread counts — snapshot diffs, growth curves, leak forensics."
---

# Memory Leaks & Resource Exhaustion

## Purpose

Diagnose and fix memory leaks and their cousins (goroutine/thread leaks, connection/file-descriptor exhaustion) using measurement — snapshot diffs, growth curves, restart-cadence forensics — instead of staring at code hoping to spot the missing `free`.

## When to use

- Memory grows until OOM-kill; services need periodic restarts to stay healthy.
- Latency degrades over hours/days (GC pressure) then resets on restart.
- "Too many open files," connection pool exhaustion, or thread/goroutine counts that only go up.
- After adding caches, event listeners, subscriptions, or long-lived processes.
- Capacity planning keeps being wrong because usage creeps.

## Goals

- Leak confirmed and characterized (rate, correlation with traffic/feature) before any code is read.
- The retaining path identified from evidence (snapshot diffs), not intuition.
- Fix addresses ownership (who releases this?), verified by a soak test measured in hours.
- Guardrails installed: growth alerts, bounded caches, leak-canary tests.

## Expert Mental Model

- **First, prove it's a leak.** Healthy managed-runtime memory looks like a sawtooth (grow, GC, drop); rising RSS can be: normal heap growth to a plateau, fragmentation, page cache (not your problem), or an actual leak (baseline after full GC climbs monotonically under steady load). The discriminator: *trough-to-trough growth* — compare post-GC floors across hours at constant load. Chasing "high memory" that's actually a correctly-sized cache wastes weeks.
- **Leaks are ownership bugs.** Every allocation needs an answer to "who releases this, and when?" Leaks happen where ownership is ambiguous: globals and statics that accumulate, caches without eviction, listeners/subscriptions registered but never unregistered, closures capturing more than they meant, pools that grow but never shrink. The fix is almost never "call free here" — it's making ownership explicit (scope-bound lifetimes, weak references, bounded structures).
- **Snapshots diff; eyes don't.** The three-snapshot technique: snapshot at baseline → perform the suspected operation N times → snapshot → perform N more → snapshot. Objects that grew by ~N between all snapshots (and whose growth tracks the operation count) are your leak; the *retaining path* (what chain of references keeps them alive) names the culprit. Memory profilers exist because "read the code for leaks" fails against closures, framework internals, and the 40 places a listener might be held.
- **Every runtime has its top-5 usual suspects** — check them before deep analysis:
  - JS/Node/browser: event listeners not removed, timers (`setInterval`) never cleared, closures capturing large scopes, detached DOM trees held by JS references, unbounded module-level Maps-as-caches.
  - Java/JVM: static collections, `ThreadLocal` in thread pools (the thread lives forever, so does the value), unclosed resources, classloader leaks on redeploy, listener registries.
  - Python: module-level caches, `lru_cache` on unbounded key spaces, reference cycles involving `__del__`, C-extension allocations invisible to `gc`, large default-arg accumulators.
  - Go: goroutine leaks (blocked forever on a channel no one closes — memory follows the goroutine), slices re-slicing giant backing arrays, `time.Ticker` not stopped, maps that only grow.
  - Any: connection/file handles opened without `finally`/defer/with, caches without max-size+TTL+eviction (all three — see caching).
- **Restart cadence is forensic data.** "We restart it nightly" encodes the leak rate: memory limit ÷ hours-to-OOM = bytes/hour; correlate that with traffic (per-request leak?) or time (per-tick leak — a timer?). A leak proportional to requests lives in request handling; one proportional to wall-clock lives in background loops; one proportional to *deploys* lives in reload/plugin machinery.
- **Exhaustion cousins obey the same logic**: goroutines/threads, FDs, sockets, DB connections leak by the same ownership failures and diagnose the same way — count them over time (they're cheaper to count than heap!), diff what's holding them (stack dumps for goroutines, `lsof` for FDs), find the acquire-without-release path. Often the "memory leak" is actually 40k leaked goroutines each holding buffers.

## Workflow

1. **Confirm and characterize**: plot memory (or FD/thread/goroutine count) over 24–48 h against load. Establish: monotonic trough growth? rate? correlated with traffic, time, or specific operations? A leak with a rate and a correlation is half-diagnosed.
2. **Check the cheap counters first**: goroutine/thread count, FD count (`lsof | wc`), connection pool stats, cache entry counts. If one of these grows in lockstep with memory, chase *it* — object counts beat byte counts for diagnosis.
3. **Run the usual-suspects sweep for your runtime** (list above): grep for `setInterval`/`addEventListener` without teardown, static collections, unbounded caches, unclosed resources. Many leaks die in this 30-minute audit.
4. **Reproduce locally at accelerated rate**: drive the suspected operation in a loop (the correlation from step 1 tells you which); watch memory. No local repro → the leak needs production data shape (big tenants, specific features) — enable heap profiling in production (modern profilers: pprof, async-profiler, `--heapsnapshot-signal`) at acceptable overhead.
5. **Three-snapshot diff**: baseline → N operations → snap2 → N more → snap3. Filter to objects growing ≈ linearly with N. Read the *retaining path* to the GC root — the frame/structure that holds the chain is the bug's address.
6. **Identify the ownership failure**: who should have released/unregistered/evicted, and why don't they? (Scope outlives intent? Registration without symmetric teardown? Cache without bounds? Pool without shrink?)
7. **Fix by restoring ownership**: pair every acquire with a scoped release (defer/with/finally/RAII); make listener registration return an unsubscribe handle called on teardown; bound every cache (max entries + TTL + eviction); close over *values*, not whole scopes; for goroutines, ensure every launch has a guaranteed exit path (context cancellation, closed channels).
8. **Verify with a soak test**: run the accelerated loop for hours (or overnight at realistic load): trough line flat. A 10-minute "looks stable" is how leaks ship twice — the verification unit for leaks is hours, matching the leak's discovery constant.
9. **Install guardrails**: trend alert on memory/FD/goroutine growth (slope over hours, not just an absolute threshold at 95%); expose cache sizes and pool stats as metrics; add a leak-canary test to CI where feasible (run the hot operation 10k× in a bounded-memory harness).
10. **Audit siblings**: the same ownership failure (missing unsubscribe, unbounded map) usually has copies — grep the pattern (see root-cause-analysis class-fixing).

## Decision Tree

- If memory climbs but *trough after full GC* is flat → not a leak: it's working-set growth, fragmentation, or allocator behavior. Right-size limits; consider allocator tuning; stop hunting.
- Else if growth correlates with request volume → per-request leak: something in the request path retains beyond the request (request-scoped data captured by a global: logger context, metrics registry with unbounded labels [see observability cardinality], per-request listeners).
- Else if growth is steady against wall-clock, traffic-independent → background loop: timers accumulating state, a ticker/subscription per instance created repeatedly, a queue growing because its consumer died silently.
- Else if growth steps up at deploys/reloads and never returns → reload leak: old classloaders/modules/plugin instances retained (a static in the old generation holds them); common in hot-reload frameworks and app servers.
- Else if memory is flat but latency degrades over time → look at GC metrics (pause time, frequency rising = heap pressure just below leak-visibility) or *other* resources: FDs, threads, connection pools, disk (logs/tmp).
- If the process is native/mixed (C extensions, off-heap buffers) and heap profilers show nothing → the leak is off-heap: track RSS vs heap-reported delta; suspects: native buffers (arena allocators), memory-mapped files, C-extension allocations; tools shift to jemalloc profiling/valgrind/eBPF.
- If it's goroutines/threads growing → dump stacks, group by creation site: the top group's blocked-on (channel receive, lock, network read with no timeout) names the missing exit path.
- If it's FDs/connections → `lsof` by type; sockets in CLOSE_WAIT = you're not closing after peer hangup; pool at max with all "in use" for hours = acquire-without-release in some error path (the leak is in the `catch` block that skips the release).

## Heuristics

- Count objects before weighing bytes: "50,000 EventEmitter listeners" diagnoses faster than "300 MB somewhere."
- The leak is often in the error path: `open → process → close` leaks exactly when `process` throws and `close` wasn't in a finally. Audit unhappy paths first; happy paths get exercised and fixed early.
- Any map/dict/array at module/static scope is guilty until proven bounded. Add its size to metrics on suspicion.
- Caches need all three: max entries, TTL, and eviction policy. Two of three still leaks (unbounded keys with TTL leaks between expiry sweeps; bounded without TTL pins stale data).
- `WeakMap`/weak references solve "cache keyed by object lifetime" — using a strong Map keyed by request/session objects is a leak factory.
- ThreadLocal + thread pool = values immortal as the pool: always `remove()` in a finally, or don't use ThreadLocal.
- In Go, every `go func()` should answer "how does this exit?" in review; a goroutine without a termination story is a leak with a start date.
- Beware metrics/label cardinality: a per-user or per-request label on a Prometheus metric is an unbounded in-process map growing forever (see observability) — the monitoring became the leak.
- Restart-as-mitigation is legitimate triage and illegitimate resolution: schedule it, cap it, and keep the diagnosis ticket open (see production-debugging).
- Heap limits should leave autopsy headroom: configure OOM behavior to dump (heap snapshot on OOM) so every crash is evidence, not just downtime.
- Fragmentation masquerades as leaking in long-lived processes with mixed allocation sizes: RSS grows, heap-in-use doesn't. Different fix (allocator tuning, arena strategies, periodic recycle) — don't hunt references you'll never find.

## Quality Checklist

- [ ] Leak confirmed by trough-to-trough growth under known load (not just "memory is high").
- [ ] Rate and correlation established (per-request / per-time / per-deploy).
- [ ] Cheap counters checked: goroutines/threads, FDs, pool stats, cache sizes.
- [ ] Runtime usual-suspects sweep done and documented.
- [ ] Retaining path identified from snapshot diffs (or off-heap tooling for native).
- [ ] Fix names the ownership rule restored (who releases, when).
- [ ] Soak-test verification in hours at accelerated rate; trough flat.
- [ ] Growth-trend alerts on memory AND the cousin resources; cache/pool sizes exported as metrics.
- [ ] OOM configured to leave a dump; restart mitigation (if any) documented as temporary with a ticket.
- [ ] Sibling patterns audited.

## Failure Modes

- **Code-staring**: three engineers reading diffs for "the leak" for days, when one snapshot diff would have printed the retaining path in minutes. Measurement postponed is time incinerated.
- **Fixing high memory that wasn't a leak**: heroic surgery on a service whose "growth" was a cache warming to its designed size; the OOM was a limit set below working-set. Characterization skipped.
- **The 10-minute victory lap**: fix deployed, memory "looks flat," ticket closed; the leak needed 6 hours to show. Recurrence with interest.
- **Restart normalization**: nightly restart cron quietly added; two years later nobody remembers memory ever being investigated; the restart is now load-bearing and fails during a traffic peak (see production-debugging state-accumulation).
- **Bounding the symptom cache**: the leaked objects were *reachable from* a cache, so the cache got bounds — but the true retainer was a listener registry; the leak continues, now harder to see.
- **GC-blaming**: "the GC is broken/slow" filed against the runtime; the heap was 95% live objects the app retained. GCs collect garbage, not regrets.
- **Leak fixed, alert never added**: the next leak (there is always a next) again discovered by OOM-page instead of by slope alert at 20% growth.
- **Off-heap blindness**: weeks in the JS heap profiler while the leak sat in native Buffer pools / a C extension — RSS vs heap-reported was never compared.

## Edge Cases

- **Leaks only at production data shape**: the unbounded cache keys on tenant-specific values; local repro flat, prod climbs. Production-safe continuous profilers (low-overhead sampling) exist for exactly this — budget the ~1–5% overhead.
- **Sawtooth with rising peaks but flat troughs**: allocation churn growing (perf problem, GC pressure) without retention growing — fix allocation rate (pooling, fewer temporaries), not references.
- **Leak in the monitoring/logging layer**: APM breadcrumbs, log buffers awaiting a dead upstream, trace spans never finished — the observability stack holds request data forever. Check spans/breadcrumb counts.
- **Session/WebSocket accumulation**: each connection holds state; slow client leak (connections that never quite die — missing heartbeat/timeouts) reads as memory leak; fix is connection lifecycle, not heap.
- **Sidecar/child-process leaks**: your process is flat; the container OOMs anyway — the leak is in a sidecar, a spawned ffmpeg, or shared memory segments. Meter the whole cgroup, per-process.
- **Kubernetes limit interplay**: OOMKilled at limit while the runtime's GC thought it had headroom (runtime not cgroup-aware, or limit < heap-max + off-heap + stack). Align runtime memory flags with container limits explicitly.
- **Weak-reference caches that empty under pressure**: "leak fixed itself in testing" because GC pressure cleared weak caches; in production with headroom, they grow. Verify at realistic memory limits.
- **Redeploy-only leaks in dev**: hot-reload retaining old module graphs — annoying locally, irrelevant in prod (fresh processes). Confirm the leak exists in the production lifecycle before spending on it.

## Tradeoffs

- **Restart mitigation vs diagnosis time**: scheduled restarts stop the bleeding for the cost of hiding the evidence and normalizing decay. Acceptable as a bridge with an expiry date; unacceptable as an ending. Capture a heap dump before each restart while diagnosis proceeds.
- **Profiling overhead vs visibility**: always-on sampling profilers cost single-digit % and make leaks findable in production; snapshot-on-demand is free until you need history you didn't record. Hot services earn always-on.
- **Bounded caches vs hit rate**: adding max-size to an unbounded cache may drop hit rate and shift load (see caching); size from measured working set, and alert on eviction storms rather than reflexively raising the bound.
- **Pooling to cut allocation churn vs leak surface**: object pools reduce GC pressure and create manual-lifetime bugs (use-after-release, pool growth). Pool only measured-hot allocation sites.
- **Memory headroom vs cost**: generous limits mask slow leaks longer (fewer 3 a.m. pages, later discovery); tight limits surface leaks fast and page you fast. Middle path: honest limits + slope alerts, so discovery is a ticket, not an outage.

## Optimization Strategies

- Make snapshot-diffing a paved road: documented one-liners per runtime (how to trigger, where dumps land, which tool reads them), tested quarterly — the difference between minutes and days is tooling familiarity.
- Export the leak-prone gauges by default: cache sizes, pool in-use/idle, goroutine/thread counts, FDs, listener-registry sizes. Leaks announce themselves in object counts long before OOM.
- Slope-based alerting: "memory grew >10%/6h at steady traffic" catches every leak class; "memory >90%" catches them at the worst possible time.
- Leak-canary CI: for the top 3 hot paths, a harness that runs the operation 10k× and asserts post-GC heap within tolerance of baseline — cheap, catches regressions at PR time.
- Adopt lifecycle linters/patterns: eslint rules for `addEventListener` without cleanup in components, Go vet + custom checks for `Ticker`/`context` misuse, code-review checklist line "every acquire has a scoped release."
- On every leak postmortem, add the retainer pattern to the team's usual-suspects list — the local bestiary converges on your codebase's actual habits.

## Self Review

- Did I prove trough growth under known load, or am I chasing "memory is high"?
- What's the leak rate, and what does it correlate with? Does my candidate mechanism predict that correlation?
- Have I looked at object counts and the cousins (goroutines, FDs, pools) before heap bytes?
- Does the snapshot diff's retaining path point at my suspect, or did I fix a bystander that was merely reachable?
- Who owns the release now, and is it scope-guaranteed (finally/defer/unsubscribe-on-teardown), not convention-guaranteed?
- Did the soak run long enough (hours at accelerated rate) to have shown the original leak?
- What alert fires at 20% of the way to the next OOM? What dump exists if it happens anyway?

## Examples

**1. Node service, nightly-restart archaeology.**
Inherited service with a 03:00 restart cron, origin unknown. Characterization: 4 GB limit, OOM at ~22 h → ~180 MB/h; rate tracks request volume. Cheap counters: listener count on a shared `EventEmitter` grows unboundedly. Sweep finds it: every request registers a `config.on('update', ...)` to pick up hot config changes — and never unregisters; each closure retains the request's context (~40 KB). Fix: single listener at module scope updating a shared snapshot; requests read the snapshot. Ownership restored: subscription lifetime = process, not request. Soak: 12 h accelerated replay, trough flat. Cron deleted *deliberately* in a PR that links the diagnosis — so the restart doesn't outlive its reason. Guardrail: `emitter.listenerCount` exported; slope alert added.

**2. JVM: ThreadLocal in a pool, found by snapshot diff.**
Symptom: API latency degrades over ~3 days (GC pause creep), heap climbing. Three-snapshot diff around a suspicious export operation: `byte[]` retained count grows ~N; retaining path: `Thread → ThreadLocalMap → ExportBuffer (8 MB each)`. Mechanism: worker threads live forever (pool), each accumulating one buffer per *distinct export type* via ThreadLocal caching — 40 types × 200 threads × 8 MB. Fix: buffer pool with bounds replaces ThreadLocals; `remove()` in finally where ThreadLocal remains legitimate. Soak overnight: flat. Sibling audit greps ThreadLocal usage — two more, one benign (documented why), one fixed.

**3. Go: the goroutine leak wearing a memory-leak costume.**
Memory grows ~90 MB/h regardless of traffic. Goroutine count: 1,400 → 38,000 over a day (the real story — checked in minute five because cheap counters come first). Stack-dump grouping: 36k goroutines blocked on `resultCh <-` in a fan-out helper. Mechanism: worker sends results to a channel; on early-return timeout, the *reader* leaves; unbuffered channel → worker blocked forever, retaining its 2 MB buffer. Fix: context cancellation in the worker's select (`case <-ctx.Done(): return`), buffered channel as belt-and-braces; the launch site now answers "how does this exit?" Soak + goroutine-count alert (slope >10%/h). CI leak-canary runs the fan-out 10k× asserting goroutine count returns to baseline.

**4. The leak that was fragmentation.**
Python service RSS grows 300 MB/day; `tracemalloc` and object counts: flat. RSS vs heap-reported divergence flags off-heap/allocator. Workload: large mixed-size numpy/protobuf buffers, long-lived process → glibc malloc arenas fragmenting. Verified by allocator stats (`malloc_stats`: huge free-but-unreturned). Fix path chosen by cost: `MALLOC_ARENA_MAX=2` + jemalloc trial (both measurably flatten RSS), plus periodic worker recycling at 10× the old restart interval as defense. Weeks of reference-hunting avoided because RSS-vs-heap was compared on day one — the discriminator question ("is the runtime even seeing this memory?") is step zero for native-adjacent stacks.

## Evaluation Rubric

Score 1–10:

- **1–2**: Code-staring without measurement; "fixed" by restart cron or limit raise; no rate, no correlation, no verification.
- **3–4**: Growth observed and a plausible suspect patched; snapshot tooling unused; verification minutes-long; cousins (FDs, goroutines) unchecked.
- **5–6**: Trough-growth confirmed with rate/correlation; usual-suspects sweep; snapshot diff locates retainer; fix restores ownership; soak-tested.
- **7–8**: Full checklist: cheap counters first, retaining-path evidence, scope-guaranteed release, hours-long soak, slope alerts + gauge exports, siblings audited.
- **9–10**: Additionally: off-heap/fragmentation discrimination when relevant; OOM-dump configured; leak-canary CI on hot paths; restart mitigations time-boxed and traceably retired; the writeup adds the retainer pattern to the team bestiary.
