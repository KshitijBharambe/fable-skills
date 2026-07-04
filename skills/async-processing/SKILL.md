---
name: async-processing
description: "Use when moving work out of the request path (queues, background workers), absorbing traffic spikes, keeping two systems consistent without distributed transactions, or reviewing dual-write designs — retries, DLQs, idempotency."
---

# Async Processing: Queues, Workers & Idempotency

## Purpose

Move work out of the request path safely — message queues (Kafka, RabbitMQ, SQS), background workers, retries, dead-letter queues, and the idempotency discipline that makes at-least-once delivery survivable.

## When to use

- A request does work the caller doesn't need synchronously (emails, exports, image processing, third-party syncs, fan-out updates).
- Request latency is dominated by a slow dependency that could be deferred.
- Traffic spikes need absorbing (buffer writes, smooth load).
- Two systems must stay consistent without distributed transactions.
- Reviewing designs that dual-write to a database and a queue.

## Goals

- No message is lost, and no message's redelivery corrupts state (idempotent consumers everywhere).
- Failures are visible and bounded: retries with backoff, dead-letter queues that page someone.
- The queue depth and consumer lag are first-class health metrics with alerts.
- Enqueueing is atomic with the business transaction that caused it (outbox), never a dual-write.

## Inputs

- The work inventory: what jobs, triggered by what, at what volume, with what latency tolerance (seconds? minutes? overnight?).
- Ordering requirements: none, per-entity, or global (be suspicious of "global").
- Side effects per job: which are naturally idempotent, which need dedup (payments, emails).
- Failure tolerance: what happens to the business if this job silently doesn't run for 4 hours?
- Existing infrastructure: what's already operated well (Postgres? SQS? Kafka?).

## Outputs

- Topology: queues/topics, producers, consumer groups, concurrency, partition/ordering keys.
- Per-job spec: payload schema (IDs, not blobs), idempotency mechanism, retry policy (attempts, backoff, jitter), timeout, DLQ destination, alerting.
- Outbox or equivalent atomicity mechanism for enqueue-with-write.
- Runbook: how to inspect, replay, and drain; graceful-shutdown behavior verified.

## Expert Mental Model

- **At-least-once is the only delivery guarantee that exists in practice.** "Exactly-once delivery" across a network is marketing; what's achievable is exactly-once *processing effects* = at-least-once delivery + idempotent consumers. Every consumer must be written assuming it will see duplicates — because during crashes, rebalances, and timeouts, it will.
- **Dual-writes are the original sin.** `db.commit(); queue.publish()` — the process dies between the two, and the systems disagree forever. The transactional outbox (write the event to an `outbox` table in the same DB transaction; a relay publishes it) is the standard cure. Any design that writes two systems without a coordinating mechanism is a data-inconsistency generator.
- **The queue is a buffer, not a bin.** Work in a queue is invisible-by-default; the system "works" while silently falling behind. Consumer lag / queue depth / oldest-message-age are the health metrics — an expert checks lag graphs the way they check error rates.
- **Ordering is expensive; scope it ruthlessly.** Global ordering serializes your whole system through one lane. Almost every real requirement is per-entity ordering ("events for order 123 in order"), achieved by partitioning/sharding on the entity key.
- **Retries without design are a weapon pointed at yourself.** Naive immediate retries turn one failure into a self-DDoS; retries without idempotency turn transient errors into double-charges. Backoff + jitter + max attempts + DLQ is one atomic decision, made per job.
- **Poison messages are inevitable.** Some message will always fail (bad data, code bug). Without a DLQ + max attempts, it blocks or crash-loops the consumer forever. With an unmonitored DLQ, it fails silently — which is worse.

## Workflow

1. **Classify each job**: latency tolerance, ordering needs, volume, idempotency of side effects, blast radius if delayed/dropped. This table drives every later choice.
2. **Pick the transport** (see Decision Tree). Bias to what the team already operates; a Postgres-backed queue run well beats Kafka run badly.
3. **Design payloads as references**: carry IDs + version/timestamp, let the consumer fetch current state. Fat payloads go stale, blow size limits, and leak PII into queue storage. (Exception: event-carried state transfer where consumers must not call back — then version the schema seriously.)
4. **Make enqueue atomic**: outbox table written in the business transaction; relay (poller or CDC) publishes with at-least-once semantics. For simple cases with a DB-backed queue, the job row IS the outbox.
5. **Design idempotency per consumer**: natural key where possible (`charge for invoice #123` — unique constraint does the work), else a processed-message dedup store: `INSERT message_id INTO processed` in the same transaction as the state change; conflict → skip. TTL the dedup store beyond max redelivery window.
6. **Set the retry policy per job**: exponential backoff with jitter (e.g., 30 s → 2 m → 10 m → 1 h), max attempts (3–7 typical), then DLQ. Distinguish retryable (timeouts, 5xx, deadlocks) from terminal (validation, 4xx) — terminal goes straight to DLQ, no retries.
7. **Size timeouts honestly**: visibility timeout / ack deadline > p99 processing time × safety factor, or you get duplicate processing *by design*. Long jobs heartbeat or extend leases.
8. **Implement graceful shutdown**: stop consuming, finish in-flight (bounded), ack/nack cleanly, exit. Deploys must not strand or duplicate work — test this specifically.
9. **Wire observability**: lag/depth/oldest-age per queue, processing latency, failure rate, DLQ count (alert on ≥1 for critical jobs), correlation IDs flowing producer→consumer logs.
10. **Write the replay runbook** before you need it: how to inspect a DLQ message, fix, and re-drive; how to replay a time range; which consumers are safe to replay (idempotent) and which need care.

## Decision Tree

- If jobs are simple app tasks (emails, thumbnails), volume <~1k/min, and you run Postgres → DB-backed queue (SKIP LOCKED) or the ecosystem's standard (Sidekiq/Celery/BullMQ on Redis). Operational simplicity wins.
- Else if you need a task queue with routing, per-message ack, delays, priorities → RabbitMQ/SQS-style broker. SQS if you're on AWS and can take 'managed' as the answer.
- Else if you need an event log: many consumers reading the same stream independently, replay, per-key ordering at high volume → Kafka (or cloud equivalent). Accept the operational and cognitive cost.
- Else if it's multi-step workflows with human waits, compensation, long timers → a workflow engine (Temporal-style) beats hand-rolled saga state machines.
- If someone says "we need Kafka" for 100 messages/minute of background jobs → they need a task queue; Kafka's costs (partitions, rebalances, no per-message ack/delay) buy nothing here.

Ordering:
- If no ordering requirement → maximize concurrency, done.
- Else if per-entity → partition/shard by entity key (Kafka partition key, or per-entity locks/FIFO groups); consumers keep per-key serial, cross-key parallel.
- Else "global ordering required" → challenge it; if it survives, single partition/single consumer and accept the throughput ceiling.

On failure of a message:
- If error is terminal (bad payload, validation) → DLQ immediately with error context.
- Else if transient → retry with backoff+jitter up to max attempts → DLQ.
- If the same message crashes the consumer process → poison-pill guard: catch, count attempts (in headers/store), quarantine past threshold.

## Heuristics

- Idempotency first question: "what happens if this handler runs twice with the same input, concurrently?" If the answer isn't "same end state," it isn't done.
- Prefer idempotency by construction (upserts, unique constraints, absolute state-setting `set status = X` rather than increments) over dedup bookkeeping.
- Consumer lag alert threshold: oldest message age > the job's latency tolerance — alert on time, not message count (count is meaningless across volume changes).
- DLQ with no alert = silent data loss with extra steps. Every DLQ has an owner and a page/ticket rule.
- Keep handlers under ~30 s; longer work should checkpoint into stages (chained jobs) — long handlers magnify redelivery duplication and deploy pain.
- One job type per queue (or per priority tier): a flood of cheap jobs must not starve critical ones behind it. Isolate by SLA.
- Retry storms: always jitter. Synchronized retries from a mass failure re-kill the recovering dependency at exact intervals.
- Never enqueue inside a not-yet-committed transaction via an external broker (the job can run before the data exists — the classic "job can't find the row it was enqueued for" race). Outbox or after-commit hooks.
- Payload schema changes: additive only; consumers tolerate unknown fields; version field from day one.
- Measure end-to-end latency (event occurred → effect applied), not just processing time — the queue wait is where SLAs die.
- Kafka specifics: partition count is your concurrency ceiling per group; keys with skew (one giant tenant) create one hot partition — plan key design around your whale customers.

## Quality Checklist

- [ ] Every consumer idempotent, with the mechanism named (constraint, dedup store, absolute writes) and a duplicate-delivery test.
- [ ] No dual-writes: outbox or same-DB job row for anything enqueued alongside a state change.
- [ ] Retry policy per job: backoff + jitter + max attempts + terminal-vs-transient classification.
- [ ] DLQs exist, alerted, with a written replay procedure.
- [ ] Visibility timeout / ack deadline > p99 processing time; long jobs heartbeat.
- [ ] Lag/oldest-age alerts tied to each job's latency tolerance.
- [ ] Graceful shutdown verified: deploy under load loses and duplicates nothing (test it, don't assume).
- [ ] Payloads are IDs + version, schema versioned, PII audited.
- [ ] Ordering requirements written per job; partition/key design documented where relevant.
- [ ] Correlation IDs flow through; a message's journey is traceable in logs.

## Failure Modes

- **Dual-write drift**: order saved, event publish failed (or vice versa) → downstream systems disagree; discovered weeks later via customer complaint. Outbox prevents; reconciliation jobs detect.
- **Duplicate side effects**: consumer processes, crashes before ack, message redelivered → second email, second charge. At-least-once + non-idempotent handler.
- **Poison message crash loop**: malformed payload kills consumer → restart → same message → down forever, lag grows unboundedly. Missing max-attempts/quarantine.
- **Silent DLQ graveyard**: thousands of failed critical jobs discovered during an unrelated audit. DLQ existed; alerting didn't.
- **Visibility timeout shorter than processing**: every slow job processed 2–3× concurrently, "randomly." Looks like a mystery duplication bug; it's a config number.
- **Queue-as-database**: business state living only in queue messages; a purge or retention expiry destroys it. Queues carry signals; databases hold state.
- **Head-of-line blocking**: one tenant's million-item backfill starves everyone's password-reset emails sharing the queue. No SLA isolation.
- **Rebalance thrash (Kafka)**: slow handlers exceed max.poll.interval → consumer kicked from group → rebalance → duplicates and lag oscillation. Tune poll intervals to real processing time or hand off to worker pools carefully.
- **Deploy amnesia**: workers SIGKILLed mid-job with no graceful drain; in-flight work duplicated or (with auto-ack) lost.

## Edge Cases

- **Concurrent duplicates**: two deliveries of the same message processed simultaneously on different workers — dedup must be atomic (unique constraint / SETNX), not check-then-act.
- **Out-of-order state events**: `updated(v2)` arrives before `updated(v1)` — consumers compare versions/timestamps and ignore stale, or use last-write-wins on version, never blind-apply.
- **Replay meets side effects**: replaying a day of events through a consumer that sends emails — idempotency store saves you only if it retains history that long; otherwise gate side effects on current state ("send only if not already sent per DB").
- **Scheduled jobs double-firing**: two scheduler instances both enqueue the nightly job — singleton via advisory lock or unique `(job, date)` constraint.
- **The zombie worker**: network partition — worker still processing while broker redelivered to another. Effects must tolerate two concurrent executors (idempotency again, plus lease-fencing tokens for the strict cases).
- **Giant messages**: broker limits (256 KB SQS, 1 MB Kafka default) — claim-check pattern: payload to object storage, reference in message.
- **Time-based edge**: backoff schedules crossing DST/leap boundaries — schedule in UTC epoch, always.
- **Queue-empty vs consumer-dead**: zero lag can mean healthy or means producers stopped — alert on producer throughput too (absence of expected traffic).

## Tradeoffs

- **Latency vs durability**: sync-in-request is immediate and consistent but couples uptime and latency to the dependency; async is resilient and fast but eventually consistent — UX must handle "processing..." states. Choose per operation, not per system.
- **DB-backed queue vs dedicated broker**: DB queue gives transactional enqueue for free and one system to operate, but competes with OLTP for resources and caps at thousands/min; brokers scale and isolate but reintroduce the dual-write problem (hence outbox) and an ops burden.
- **Fat events vs thin events**: thin (IDs) always-fresh but consumers hammer source APIs and can't work if source is down; fat (full state) decouples but demands schema governance and tolerates staleness. Thin by default; fat for genuine decoupling needs.
- **Auto-ack vs manual ack**: auto-ack maximizes throughput and loses messages on crash; manual ack is the default for anything that matters.
- **One queue per job type vs shared**: isolation costs infrastructure sprawl; sharing costs head-of-line risk. Tier by SLA: critical / default / bulk is usually enough.
- **Strict FIFO vs throughput**: FIFO/single-key serialization caps parallelism; pay it only where causality genuinely matters (per-aggregate), never globally by default.

## Optimization Strategies

- Batch at every layer: consume in batches, write effects in bulk (multi-row upserts), publish in batches — often 10× throughput for free.
- Right-size concurrency empirically: raise workers until the downstream (DB/API) saturates, then back off 20%; more workers past the bottleneck just moves the queue into lock contention.
- Split queues by cost class so cheap-and-many never queues behind slow-and-few; give each its own concurrency budget.
- Preflight-fetch in batch: if handlers each fetch the same reference data, load once per batch, not per message.
- Compress or claim-check large payloads; broker throughput is often bandwidth-bound.
- For Kafka: choose partition counts for target concurrency ×2 headroom (repartitioning is disruptive); monitor per-partition lag to catch key skew early.
- Reserve capacity for drain scenarios: can consumers run at 5× steady-state to clear a 4-hour backlog in under an hour? If not, an incident becomes a day.

## Self Review

- For each consumer: what exactly happens on duplicate delivery — and is there a test proving it?
- Where is the atomicity between "state changed" and "message sent"? Point at the outbox/transaction, or admit the race.
- If this queue silently stops for 4 hours, who notices, how, and how fast? (Answer must be an alert, not "a customer.")
- Which messages are unprocessable by design (bad data), and where do they land? Who looks at that place?
- Did I test a deploy under load — messages neither lost nor double-applied?
- What's the replay story after a consumer bug ships and mangles a day of events?
- Are my ordering assumptions written down, and does the partition/key design actually deliver them?

## Examples

**1. Order-placed pipeline with outbox.**
`POST /orders`: one transaction inserts `orders` row + `outbox` row (`event: order.placed, payload: {order_id, version}`). CDC relay publishes to `orders` topic keyed by `order_id` (per-order ordering). Consumers: email (dedup via unique `(order_id, email_type)` — sends exactly one confirmation even across replays), inventory (idempotent reservation upsert), analytics (at-least-once fine, dedup downstream). Retry: 5 attempts, 30 s→1 h jittered backoff; terminal validation errors DLQ immediately with payload snapshot. Alerts: oldest-age >5 min (email), >30 min (analytics); DLQ ≥1 pages for inventory only.

**2. Webhook receiver that survives the sender's retries.**
Stripe-style webhooks arrive at-least-once, out of order. Endpoint does only: verify signature → `INSERT INTO webhook_events (provider_event_id UNIQUE, payload) ON CONFLICT DO NOTHING` → 200. A worker processes rows transactionally, comparing event `created` timestamps against current subscription state, ignoring stale transitions. Receiving is now idempotent-by-constraint, fast (never times out → fewer sender retries), and replayable — the events table is an audit log.

**3. The backfill that didn't take production down.**
Task: re-render 8M thumbnails. Naive: enqueue 8M jobs into the default queue → email jobs starve for a day. Expert: separate `bulk` queue with its own worker pool capped at 20% of image-service capacity; producer enqueues in 10k chunks with a pacing loop reading consumer lag (backpressure); jobs are idempotent (render keyed by `(image_id, version)`, skip if output exists); progress tracked in a checkpoints table so the producer resumes after interruption. Default queue p99 unaffected; backfill completes overnight.

**4. Diagnosing "random duplicate charges."**
Two charges, minutes apart, same invoice, "intermittent." Investigation path: correlation ID → both executions logged on different workers → same message ID delivered twice → first execution took 95 s; SQS visibility timeout was 60 s → redelivery *by configuration*. Fixes in order of correctness: (1) idempotency — charge creation gains unique `(invoice_id)` constraint + provider idempotency key (should have existed regardless); (2) visibility timeout raised to 5 min with heartbeat extension; (3) alert on processing-time-vs-timeout ratio >0.5. The duplicate was never "random" — it was arithmetic.

## Evaluation Rubric

Score 1–10:

- **1–2**: Fire-and-forget publishes; no retries or infinite immediate retries; no DLQ; consumers assume exactly-once; dual-writes everywhere.
- **3–4**: Broker used with defaults; some retries; DLQ exists unmonitored; idempotency ad-hoc ("we haven't seen duplicates"); deploys drop in-flight work.
- **5–6**: Idempotency designed for key consumers; backoff+jitter+max attempts; outbox on the critical path; lag metrics exist; ordering scoped per-entity where needed.
- **7–8**: Full checklist: duplicate-delivery tests, alerted DLQs with replay runbook, graceful shutdown verified, SLA-tiered queues, timeout>p99 discipline, correlation IDs end-to-end.
- **9–10**: Additionally: reconciliation jobs detecting drift between systems; backpressure-aware bulk operations; drain capacity planned and rehearsed; schema evolution policy enforced; the design doc explains transport choice against alternatives with the team's operational reality as a first-class input.
