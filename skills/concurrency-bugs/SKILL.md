---
name: concurrency-bugs
description: "Use when bugs are intermittent, load-dependent, or 'can't reproduce locally,' seeing duplicate records/lost updates/drifting counters/deadlocks, or reviewing check-then-act and shared mutable state — races, atomicity."
---

# Concurrency Bugs

## Purpose

Hunt and fix races, deadlocks, lost updates, and async ordering bugs — the intermittent, load-dependent failures that vanish under debuggers — by amplifying them into reproducibility and fixing them with atomicity, not sleeps.

## When to use

- Bugs described with "sometimes," "under load," "only in production," or "can't reproduce locally."
- Duplicate records, lost updates, counters that drift, double-sent effects.
- Hangs and freezes (deadlock-shaped) or throughput collapse under contention.
- Reviewing code with check-then-act patterns, shared mutable state, or await points inside critical sections.
- After adding retries, parallelism, or background jobs to a previously serial system.

## Goals

- The race is amplified into a repro you can run on demand (probability engineering, not patience).
- The fix removes the *window* (atomicity/ordering), never narrows it (sleeps, "unlikely timing").
- The invariant that was violated is named, and enforced by construction where possible (constraints, single-writer, immutability).
- A stress/soak test guards the fix in CI.

## Inputs

- Symptom evidence: duplicated/lost/mangled state examples, thread dumps or event-loop traces from hangs, timestamps of occurrences vs load.
- The shared state map: what data is accessed by multiple threads/processes/requests/workers, and who writes it.
- The concurrency topology: threads? async event loop? multiple processes? multiple nodes? (each has different tools and different possible bugs).
- Isolation/atomicity primitives available: DB transactions and constraints, locks, CAS, queues, idempotency stores.

## Expert Mental Model

- **A race is a violated invariant with a timing window.** Somewhere, an operation assumed "nothing changes between my read and my write" — and something did. The debugging goal is naming the invariant ("one welcome email per user," "balance never negative," "config read matches config validated"); the fixing goal is making the check and the act *atomic*, or removing the sharing entirely.
- **Check-then-act is the universal smell.** `if not exists → create`, `read → modify → write`, `check balance → deduct`, `list files → process them` — any gap between observation and action is a window for another actor. Experts grep for the *shape* (a read whose result justifies a later write) across DB code, memory structures, and filesystems alike; the same bug wears all three costumes.
- **Make it worse, not better.** Intermittent bugs are probability problems: a 1-in-10,000 window becomes debuggable at 1-in-10 by *widening the window* (inject sleeps at the suspected seam), *raising attempts* (loop the operation 100k×, hammer with concurrent load), or *perturbing the scheduler* (stress the CPU, randomize delays). The instinct to make the bug rarer while investigating is exactly backwards — you can't fix what you can't see, and you can't *verify* a fix without a frequency baseline.
- **Disappears under the debugger = timing perturbation = it's a race.** Breakpoints, verbose logging, even print statements serialize execution and hide the window. This symptom is itself diagnostic. Use low-perturbation observation: atomic counters, lock-free ring buffers, sampled tracing, post-hoc state diffs.
- **The fix hierarchy, best to worst**: (1) *don't share* — immutable data, message passing, single-writer ownership; (2) *atomic primitives* — DB unique constraints + upsert, transactions with the right isolation, compare-and-swap, atomic increments; (3) *locks* — correct but contention-prone and deadlock-capable; (4) *sleeps and retries-without-idempotency* — not fixes; they're apologies to the race. When a reviewer sees a sleep "fixing" concurrency, the bug is still there, now rarer and angrier.
- **Deadlock is a cycle, and cycles need four ingredients** (mutual exclusion, hold-and-wait, no preemption, circular wait) — break any one. In practice: global lock ordering (always acquire A before B, everywhere) kills circular wait; lock timeouts give preemption; the thread dump showing two threads each holding what the other wants is the smoking gun and reads in 30 seconds once you know to look.
- **Distributed makes it worse, not different**: two app servers, a DB, and a queue have all the same shapes (check-then-act across processes) with fewer primitives — no shared mutex, only the DB's atomicity, fencing tokens, and idempotency (see async-processing). "It works because we only run one instance" is a time bomb with a deploy-shaped fuse.

## Workflow

1. **Characterize the symptom into a family**: duplicate effects (creation race), lost update (write-write race), torn/inconsistent reads (read seeing mid-transaction state), hang (deadlock/starvation), drift (non-atomic increments), crash on shared structure (unsynchronized mutation). The family points at the shape to hunt.
2. **Name the violated invariant** precisely: "at most one X per Y," "A happens before B," "total is conserved." Write it down — the fix will be "enforce this atomically."
3. **Map the actors**: who reads/writes the state — requests, threads, workers, cron jobs, admin tools, other services. The actor everyone forgot (the retry middleware, the second pod, the backfill script) is usually the second party to the collision.
4. **Find the window**: locate the check-then-act (or the unordered pair). Read the code path and mark the exact lines between observation and action; everything between them is the crime scene. For async code: every `await` inside that span is a yield point where the world can change.
5. **Amplify to repro**: build a harness that runs the operation concurrently (10–1000 parallel) in a tight loop; inject a deliberate sleep inside the window to widen it (temporarily, in a test build) — if frequency jumps, you've confirmed the window's location. Record the baseline failure rate.
6. **Fix by the hierarchy**: prefer removing sharing (single writer, immutable snapshot); else atomic ops — for DB: unique constraint + `ON CONFLICT`, `SELECT FOR UPDATE`, optimistic version column with retry loop, or serializable isolation with retry; for memory: mutex/CAS/atomics with minimal critical sections; for cross-service: idempotency keys + constraints (see async-processing).
7. **For deadlocks**: extract the lock graph from the dump (who holds what, who waits for what); establish a global acquisition order (document it!), or collapse multiple locks into one coarser lock (correct-but-slower beats fast-but-deadlocked; refine later), add timeouts as the backstop.
8. **Verify with the amplifier**: fix in place → run the harness at ≥10× the volume that produced the baseline failures → zero occurrences. A race "fixed" without a frequency baseline is a guess wearing a merge badge.
9. **Enforce by construction**: keep the unique constraint even after the app-level fix (defense in depth); make the invariant a DB constraint, a type (send-once wrapper), or an architecture rule (this table has one writer service) so the *class* dies (see root-cause-analysis).
10. **Institutionalize the harness** as a stress/soak test in CI (nightly if too slow for PR); concurrency regressions reappear with innocent-looking refactors.

## Decision Tree

- If duplicates are created (rows, emails, charges) → creation race: fix with a unique constraint on the natural key + upsert/`ON CONFLICT`/catch-and-fetch. App-level "check first" stays as a UX nicety, never as the guard.
- Else if updates vanish (last write wins over concurrent edit) → lost update: optimistic locking (version column; `UPDATE ... WHERE version = ?` + retry on 0 rows) for low contention; `SELECT FOR UPDATE` for hot rows; atomic expression updates (`SET count = count + 1`) when the operation is expressible in-place.
- Else if a value is computed from stale reads (balance checks, quota enforcement) → move check and act into one transaction with the right isolation (and handle serialization failures with retries), or restructure to an atomic conditional write (`UPDATE ... WHERE balance >= amount`).
- Else if the system hangs →
  - Thread dump / async stack capture *first*.
  - Two+ threads in `WAITING` on each other's locks → deadlock: impose lock ordering or coarsen.
  - All threads waiting on a pool (connections, workers) → exhaustion/starvation: something leaks or holds too long (look for I/O inside locks, transactions spanning external calls — see postgres idle-in-transaction).
  - Event loop blocked (async runtime) → a synchronous/CPU call on the loop: find it with loop-lag instrumentation.
- Else if counters/aggregates drift slowly → non-atomic read-modify-write somewhere: replace with atomic increments or event-sourced recomputation; add a reconciliation job to detect residual drift.
- Else if crash/corruption in in-memory structures → unsynchronized concurrent mutation: use the runtime's race detector (Go `-race`, TSan for C/C++/Rust-unsafe, `ThreadSanitizer`) — these tools find in minutes what inspection misses for weeks; for single-threaded async (JS/Python asyncio), look for interleaved awaits mutating shared objects mid-"transaction."
- If retries exist anywhere in the path → check them first: retries multiply every race's attempt count and create duplicate-effect races on their own (see async-processing idempotency).

## Heuristics

- Every `await`/yield inside a read-modify-write is a suspect: "single-threaded" async code races at every suspension point — the interleaving is cooperative, not absent.
- The window between "SELECT showed it's fine" and "UPDATE assumed it still is" should be zero lines long, or wrapped in something atomic. Count the lines; that's your risk surface.
- Grep bait: `if.*exists`, `get.*then.*save`, `count == 0`, `INSERT` after `SELECT` on the same key, filesystem `exists()` before `open()` — audit each hit for atomicity.
- Locks guard *data*, not code: name every lock by the state it protects; a lock nobody can name protects nothing reliably.
- Keep critical sections tiny and I/O-free: a lock held across a network call converts one slow response into a system-wide convoy.
- Lock ordering: define one global order (alphabetical by resource name works); any code acquiring two locks documents why and in what order. Most deadlocks are two innocent functions each locking (A,B) and (B,A).
- Prefer one coarse lock that's obviously correct over three fine locks that are probably correct; refine only with contention *measurements* in hand.
- "It's fine, GIL/single-instance/low-traffic protects us" — each of those is one deployment decision away from false. Write the code as if concurrent, because it will be.
- Timestamps don't order events across machines: clock skew makes "later timestamp" a lie; use versions, sequences, or fencing tokens for ordering decisions.
- Amplifier math: to claim a 1/10,000 race fixed, run ≥100,000 clean iterations post-fix (10× the inverse frequency) — otherwise you've measured luck.
- The race detector is cheaper than your time: Go `-race` in CI always; TSan on test suites for native code; the categories they catch never re-litigate.

## Quality Checklist

- [ ] Symptom classified into a race family; the violated invariant written in one sentence.
- [ ] All actors on the shared state enumerated (including retries, crons, other services, admin scripts).
- [ ] The exact window located (lines between check and act; await points marked).
- [ ] Repro amplified with a measured baseline frequency.
- [ ] Fix removes the window via the hierarchy (sharing removed / atomic primitive / correctly-ordered locks) — no sleeps, no "unlikely now."
- [ ] Deadlock fixes establish documented lock ordering or coarsening; timeouts as backstop.
- [ ] Post-fix verification: ≥10× inverse-frequency clean runs on the amplifier.
- [ ] Invariant enforced by construction (constraint/type/single-writer) surviving future refactors.
- [ ] Race detector / stress harness wired into CI.
- [ ] Sibling windows audited (the same shape elsewhere in the codebase).

## Failure Modes

- **The sleep "fix"**: `sleep(100ms)` between check and act — narrows the window, ships the bug, and adds latency as a bonus. Reappears at 3× traffic.
- **Fixing the duplicate, keeping the race**: dedupe cleanup job added while the creation race lives — the symptom is managed, the invariant still violated, and every new consumer of the data re-inherits the mess.
- **Double-checked locking folklore**: hand-rolled "check, lock, check again" on primitives without memory-model understanding — correct in some runtimes, silently broken in others; use the language's blessed once/lazy primitives.
- **Lock scope creep**: the mutex that guarded a counter now wraps an HTTP call "to be safe" — throughput collapses under load; the outage is the fix's.
- **Retry without idempotency**: timeout → retry → both succeed → duplicate effect; the "network resilience" PR created the race (see async-processing).
- **Debugging by logging into disappearance**: enough printf serializes the interleaving; bug "gone," ships, returns without the logs. The perturbation was the anesthetic, not the cure.
- **Trusting the test that passed once**: race tests are probabilistic; a single green run proves nothing. No baseline, no iteration count, no claim.
- **Cross-node blindness**: mutex added in-process while the second pod races merrily past it — the sharing was distributed; the fix wasn't.

## Edge Cases

- **DB isolation surprises**: READ COMMITTED (common default) allows two transactions to both read "no row exists" and both insert — transactions alone don't fix creation races; constraints do. REPEATABLE READ/SERIALIZABLE throw serialization errors *by design* — code must retry them, not report them (see postgres).
- **Upsert race on multiple unique keys**: `ON CONFLICT` targets one constraint; concurrent inserts violating a *different* unique key still error — handle both paths.
- **Async cancellation mid-critical-section**: a cancelled task (timeout, user abort) that had acquired a lock or partially mutated state — cleanup paths (`finally`) must restore invariants, and lock releases must be cancellation-safe.
- **Fork/threads + connection pools**: forked workers sharing the parent's sockets/connections produce interleaved protocol streams — re-initialize pools post-fork; the corruption looks like impossible protocol errors.
- **File systems as shared state**: `exists → write` races between processes; `O_EXCL`/atomic rename (`write temp → rename`) are the filesystem's CAS; NFS makes even those interesting.
- **Read-your-own-write across replicas**: the "race" is replication lag wearing a race costume — the fix is routing/stickiness, not locks (see postgres).
- **Time-of-check-to-time-of-use in auth**: permission checked, then used seconds later after revocation — security-flavored TOCTOU; re-check at use for sensitive ops (see authorization).
- **GC pauses and lease expiry**: a node holding a lease stalls (GC, VM pause), lease expires, another node takes over, the first wakes and *keeps writing* — fencing tokens (monotonic epoch checked at the resource) are the only real fix; "the lease guarantees exclusivity" alone does not.

## Tradeoffs

- **Coarse vs fine locking**: coarse is provably correct and serializes throughput; fine scales and multiplies deadlock/ordering risk. Start coarse, refine under measured contention — the reverse order (clever first) produces the bugs this file is about.
- **Optimistic vs pessimistic concurrency**: optimistic (version+retry) wins at low contention (no lock waits) and degrades ugly at high contention (retry storms); pessimistic (`FOR UPDATE`) serializes hot rows predictably. Choose by measured collision rate; hybrid per-entity is normal.
- **Throughput vs simplicity of single-writer**: routing all writes for an entity through one owner (partition, actor, queue) eliminates classes of races at the cost of a serialization point and routing machinery. For genuinely hot shared state, it's usually the sane trade (see async-processing per-key ordering).
- **Stronger isolation vs retry complexity**: SERIALIZABLE hands you correctness and a new obligation (retry loops, latency variance); manual locking hands you performance and a proof obligation. Prefer the database's proof over yours where the retry cost fits the latency budget.
- **Determinism in tests vs realism**: deterministic schedulers/loom-style model checkers explore interleavings exhaustively for small cores; stress tests are realistic but probabilistic. Critical primitives deserve the deterministic treatment; app-level flows get the amplifier.

## Optimization Strategies

- Build the concurrency harness as reusable infrastructure: parameterized (operation, parallelism, iterations, injected-delay points), with failure-rate reporting — every future race investigation starts at step 5 instead of step 1.
- Adopt race detectors in CI as non-negotiable where available (Go `-race` on tests; TSan builds weekly for native) — they convert weeks of hunting into build failures.
- Inventory shared mutable state periodically: each entry gets an owner and a protection story (constraint/lock/single-writer); unowned shared state is scheduled work.
- Prefer designs that make races unrepresentable in review: immutable messages, append-only logs with derived state, database-enforced invariants — the review question becomes "where's the constraint?" not "did you think about timing?"
- Teach the grep-bait patterns to the team lint/review culture; check-then-act caught at review costs one comment; caught in production costs an incident.
- Capture thread/async dumps automatically on hang detection (watchdog) — deadlocks become mail with attachments instead of 2 a.m. archaeology.

## Self Review

- Can I state the violated invariant in one sentence? Where is it now enforced, and does that enforcement survive a refactor by someone who never read this ticket?
- Did I find the actual window (lines/awaits), or did I fix where the symptom appeared?
- What was the baseline failure frequency, and how many clean amplified runs back my "fixed" claim?
- Is there any sleep, "should be rare now," or narrowed-window reasoning in the fix?
- If a second process/pod/actor appears tomorrow, does the fix still hold, or did I fix single-node only?
- Which awaits/yields sit inside my critical spans? Who else writes this state that I haven't listed?
- Where else in this codebase does the same shape live?

## Examples

**1. Duplicate signup emails (creation race + retry multiplier).**
Symptom: ~1/5,000 users gets two welcome emails. Invariant: "at most one welcome email per user." Actors: signup handler ×N pods, plus the HTTP retry middleware everyone forgot. Window: `SELECT sent WHERE user=? → (send email) → INSERT sent` — three statements, one network call in the middle. Amplifier: 50-way concurrent signup loop + 50 ms injected delay → 12 dupes/10k (baseline). Fix by hierarchy: unique constraint on `welcome_email(user_id)` + insert-first (`ON CONFLICT DO NOTHING` → only the inserting winner sends), making check-and-act one atomic statement; retry now harmless. Verification: 200k amplified runs, zero dupes. CI gains the harness as a nightly soak.

**2. Deadlock between transfer and audit.**
Symptom: payment service freezes daily around report time; restart "fixes." Thread dump: thread A holds `accounts:42`, waits `audit_log`; thread B (report job) holds `audit_log`, waits `accounts:42`. Classic circular wait. Fix: global lock order documented (`accounts before audit_log, accounts by ascending ID`); report job restructured to snapshot-read accounts without locks (it never needed exclusivity — the lock was cargo cult); lock timeouts (5 s) added as backstop with alerting. The dump-reading took 3 minutes; the prior three weeks of "random freeze" investigation had never captured one — hang-watchdog now auto-dumps.

**3. Drifting inventory counter (lost updates in async JS).**
Symptom: stock counts drift negative over weeks. Code: `const item = await get(id); item.stock -= qty; await save(item);` — single-threaded Node, "no threads, no races"? Two requests interleave at the awaits: both read 5, both write 4 after selling 1 each. Invariant: stock conservation. Fix: atomic conditional write — `UPDATE items SET stock = stock - $1 WHERE id = $2 AND stock >= $1` (0 rows → sold-out path); drift reconciliation job compares event log vs counters to catch residuals (finds two more legacy paths doing read-modify-write — sibling audit pays off). The team's takeaway sentence: every await is a context switch.

**4. Lease + GC pause: the zombie writer.**
Symptom: rare corrupted exports — two workers wrote the same output. Design review said impossible: a Redis lease guarantees one owner. Timeline reconstruction: worker A acquires lease (30 s TTL), hits a 45 s GC pause/VM stall, lease expires, worker B acquires and starts writing, A wakes *mid-function* and resumes writing. Fix: fencing token — lease grants a monotonically increasing epoch; the storage layer rejects writes bearing an epoch older than the highest seen. B's first write bumps the fence; A's resurrected writes bounce. Lesson encoded in the design docs: a lease says you *were* the owner; only a fence checked at the resource says your write still is.

## Evaluation Rubric

Score 1–10:

- **1–2**: Sleeps and retries as fixes; no repro attempted; "works now" after multi-variable changes; invariant never named.
- **3–4**: Race suspected and window roughly located; fix plausible (a lock somewhere) but scope unverified; no baseline or amplified verification; single-node assumptions unexamined.
- **5–6**: Family classified, window found, amplifier built with baseline; fix uses atomic primitives or ordered locks; verification runs meaningful volume.
- **7–8**: Full checklist: invariant enforced by construction, actors fully enumerated (retries/crons/pods), deadlock ordering documented, harness in CI, siblings audited.
- **9–10**: Additionally: race detectors institutionalized; distributed cases handled with fences/idempotency where relevant; shared-state inventory maintained; the fix survives the hostile review question "what if two of everything run at once, twice?"
