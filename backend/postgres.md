# Postgres Schema Design & Query Optimization

## Purpose

Design PostgreSQL schemas that stay fast and honest at 100× today's data, read query plans the way experts do, and run migrations that never take the site down.

## When to use

- Designing tables for a new feature or service.
- A query is slow, a dashboard times out, or p99 latency climbed after data growth.
- Planning a migration on a large or hot table.
- Choosing keys, indexes, or constraints.
- Reviewing schema PRs.

## Goals

- Access patterns known before schema exists; indexes match real queries.
- Constraints encode invariants so bad data is unrepresentable, not just discouraged.
- Zero-downtime migrations as the default discipline, not a special event.
- Every engineer on the team can read EXPLAIN ANALYZE output and act on it.

## Inputs

- The queries: top read and write patterns with expected frequency and latency targets.
- Data volumes now and at 10×: row counts, growth rate, hot vs cold distribution.
- Consistency requirements: what must be transactional, what can lag.
- Deployment reality: can you take locks? maintenance windows? replica lag tolerance?

## Outputs

- DDL with constraints (NOT NULL, FKs, CHECKs, uniques) and a written access-pattern → index mapping.
- Migration scripts that are lock-safe and reversible, with a rollout order.
- EXPLAIN ANALYZE baselines for the critical queries at realistic data volume.
- A pooling and timeout configuration (statement_timeout, lock_timeout, pool sizes).

## Expert Mental Model

- **Model the queries, not the world.** Normalization is the starting posture, but the schema exists to answer specific questions fast. Experts write the five most important queries first and let them pull the design.
- **An index is a bet.** Every index taxes every write and buys specific reads. Experts can name which query each index serves; indexes nobody can attribute are deleted.
- **The planner is a cost-based gambler using statistics.** When a plan is bad, the first question is not "how do I force the right plan" but "why were the row estimates wrong?" (stale stats, correlated columns, skew). Estimated-vs-actual rows in EXPLAIN ANALYZE is the first thing an expert's eye jumps to.
- **Locks, not speed, are what kill you in migrations.** An `ALTER TABLE` that needs 200 ms of ACCESS EXCLUSIVE lock behind a long-running query will queue every subsequent query behind it — a 200 ms operation becomes a full outage. Migration discipline is lock discipline.
- **MVCC means updates are copies and deletes are marks.** Bloat, vacuum health, and long-running transactions holding back cleanup are background physics you must respect; a "small" table updated constantly can be gigabytes of dead tuples.
- **Postgres is more capable than your first instinct.** Partial indexes, expression indexes, JSONB, SKIP LOCKED queues, LISTEN/NOTIFY, materialized views — experts reach for a Postgres feature before adding a new datastore.

## Workflow

1. **List access patterns with numbers.** "Fetch user's 50 newest orders — 500 qps, needs <10 ms" beats "orders belong to users."
2. **Design tables**: `bigint GENERATED ALWAYS AS IDENTITY` PKs (or UUIDv7 if IDs are generated across services — avoid random UUIDv4 as PK on big tables; index locality suffers). `timestamptz` never `timestamp`. `text` with CHECK constraints over `varchar(n)`. NOT NULL by default; every nullable column needs a reason.
3. **Encode invariants as constraints**: FKs on (indexed on the referencing side — Postgres doesn't do that automatically), UNIQUE for business keys, CHECK for enum-like domains and ranges, EXCLUDE for overlap rules (bookings). Constraint violations in production are cheaper than data-repair projects.
4. **Map each access pattern to an index.** Composite column order: equality columns first, then range/inequality, then sort columns (the "ESR" order). Partial indexes for sparse predicates (`WHERE status = 'pending'` on a mostly-done table). Expression indexes for `lower(email)`.
5. **Prototype with realistic volume** (generate 10–100× expected rows) and capture EXPLAIN ANALYZE for each critical query. A plan on 1,000 rows tells you nothing — the planner switches strategies as tables grow.
6. **Read plans in this order**: (a) estimated vs actual rows at each node — 10×+ misestimates explain most bad plans; (b) the node consuming the time (loops matter: 1 ms × 10,000 loops); (c) whether the join strategy and scan types are plausible for the cardinalities; (d) buffers (with BUFFERS): is it I/O or CPU?
7. **Write migrations lock-safe**: `SET lock_timeout = '2s'` (fail fast rather than queue the site behind you); `CREATE INDEX CONCURRENTLY`; add columns without defaults that rewrite (modern PG handles constant defaults cheaply, but verify); add constraints as `NOT VALID` then `VALIDATE CONSTRAINT` separately; backfills in batches of 1,000–10,000 with sleep, never one UPDATE.
8. **Deploy schema and code in compatible phases** (expand → migrate → contract): new column nullable → dual-write → backfill → constrain → cut reads over → drop old.
9. **Set the operational guardrails**: `statement_timeout` per role (web: 5–30 s), connection pooler (transaction mode; know its costs: no session state, prepared statements need care), autovacuum tuned down (more aggressive) for hot tables.
10. **Leave baselines behind**: store the EXPLAIN plans and latencies; future regressions get diffed against them.

## Decision Tree

- If a query is slow → run `EXPLAIN (ANALYZE, BUFFERS)`.
  - If actual rows ≫ estimated (or vice versa) at some node → `ANALYZE` the table; if persistent, raise the column's statistics target or create extended statistics for correlated columns.
  - Else if a Seq Scan on a big table where few rows qualify → missing/unusable index. Check: is the predicate sargable (no function on the column without an expression index, no type mismatch)?
  - Else if index used but slow with many loops → N+1 shape or nested loop misfire on bad estimates; consider join restructuring or fixing stats.
  - Else if the right rows but slow sort/aggregate → index providing the sort order (composite with sort columns last), or pre-aggregation.
  - Else if I/O bound (buffers read ≫ hit) → data doesn't fit cache: narrower rows, partial index, partitioning, or more memory.
- If pagination is deep and slow → replace OFFSET with keyset (`WHERE (created_at, id) < (?, ?) ORDER BY created_at DESC, id DESC LIMIT 50`).
- If a table is append-heavy and time-queried (events, logs) → partition by time range; detach-and-drop old partitions instead of DELETE.
- If you need a job queue → use `FOR UPDATE SKIP LOCKED` on a jobs table before adding a queue system; it's transactional with your data.
- If a column's value set is small and fixed-ish → CHECK constraint or lookup FK table; native ENUM only if you accept that removing values is painful.
- If storing flexible attributes → JSONB with GIN index for containment queries; but promote any key you filter/join on routinely to a real column.
- If counts are needed on big tables → estimated counts (`reltuples`), a counter cache, or a rollup table; exact `COUNT(*)` on 50M rows is a design smell in the hot path.

## Heuristics

- Every FK gets an index on the referencing column the same day — missing ones surface as mystery seq scans on DELETE cascades and joins.
- One composite index `(a, b, c)` serves `a`, `(a,b)`, `(a,b,c)` prefixes — don't also build `(a)` and `(a,b)`.
- Index hit rate on hot paths should be >99%; check `pg_stat_user_indexes` for never-used indexes quarterly and drop them.
- A transaction should span milliseconds, not user think-time. Nothing interactive inside BEGIN…COMMIT; long transactions block vacuum and bloat everything.
- Batch writes: 1 INSERT of 1,000 rows ≈ 10–50× faster than 1,000 INSERTs; use COPY for bulk loads.
- `IN (subquery)` vs `EXISTS` vs `JOIN`: don't memorize folklore — the planner usually equalizes them; when it doesn't, EXPLAIN tells you.
- LIMIT changes everything: the planner optimizes for first-rows; a query fine with LIMIT 50 may be catastrophic without it, and vice versa.
- Retry serialization failures: under REPEATABLE READ/SERIALIZABLE, 40001 errors are the design working — wrap in a retry loop, don't downgrade isolation.
- `random_page_cost` default (4.0) assumes spinning disks; on SSDs set ~1.1 or the planner unfairly shuns index scans.
- Advisory locks for app-level mutual exclusion (cron singleton), not row locks on a "locks" table.
- If you're about to add Elasticsearch for basic text search, try `tsvector` + GIN first; if about to add Redis for a queue, try SKIP LOCKED first. Add infrastructure when Postgres measurably can't, not preemptively.

## Quality Checklist

- [ ] Every critical query has an EXPLAIN ANALYZE baseline at ≥10× current volume, and each index maps to a named query.
- [ ] All FKs indexed on the referencing side; no unused indexes older than one quarter.
- [ ] NOT NULL, UNIQUE, CHECK, FK constraints encode the stated invariants (sampled: try inserting bad data, watch it fail).
- [ ] Migrations set `lock_timeout`, use CONCURRENTLY for indexes, NOT VALID + VALIDATE for constraints, batched backfills.
- [ ] No OFFSET pagination on unbounded tables; keyset with unique tiebreaker.
- [ ] `timestamptz` everywhere; UTC discipline; no `timestamp` without a written reason.
- [ ] statement_timeout and lock_timeout set per role; pooler configured and its transaction-mode caveats accounted for.
- [ ] Long-running transactions monitored/alerted (`pg_stat_activity` age); autovacuum health checked on hot tables.
- [ ] Rollback path exists for each migration step (or step is explicitly forward-only and flagged).

## Failure Modes

- **The 2 a.m. ALTER TABLE**: unbatched `ALTER`/`UPDATE` takes ACCESS EXCLUSIVE behind a long query; entire app queues. Cause: no lock_timeout, no awareness that lock *waiting* blocks others.
- **UUIDv4 primary keys on hot big tables**: random inserts shatter index locality; write amplification and cache misses grow with the table.
- **OFFSET 100000**: reads and discards 100k rows per page; deep pagination melts as data grows. Works fine in the demo.
- **Nullable everything**: every column nullable "for flexibility" → every query grows COALESCE and IS NOT NULL barnacles; invariants live in app code folklore.
- **ORM N+1**: 1 query for 50 orders + 50 queries for customers. Detected by query counts per request (assert in tests), fixed by eager loading/joins.
- **Ignoring dead tuples**: high-churn table with default autovacuum; bloat grows, scans slow, disk fills. `pg_stat_user_tables.n_dead_tup` tells the story.
- **Type-mismatch index miss**: `WHERE bigint_col = '123'::text`-shaped comparisons or `lower(email)` without expression index — index exists, planner can't use it.
- **Pooler prepared-statement surprise**: transaction-mode pooling + named prepared statements → "prepared statement does not exist" errors in production only.
- **Counting for UI**: exact COUNT(*) over millions of rows on every page load for a pagination widget nobody scrolls.

## Edge Cases

- **NULLs in UNIQUE constraints**: NULLs don't conflict (multiple rows with NULL pass UNIQUE) — use `NULLS NOT DISTINCT` (PG15+) or partial unique indexes when NULL should mean "one allowed."
- **NULLs and NOT IN**: `x NOT IN (subquery returning a NULL)` matches nothing, silently. Use NOT EXISTS.
- **Concurrent upserts**: `INSERT ... ON CONFLICT DO UPDATE` is the atomic answer; check-then-insert races under load, guaranteed.
- **CREATE INDEX CONCURRENTLY failures** leave an INVALID index behind — detect and drop/rebuild; it still taxes writes while helping no reads.
- **Foreign keys + cascading deletes on big graphs**: one DELETE fans out to millions of rows in one transaction; prefer soft-delete + async cleanup, or batched deletes.
- **Replica lag and read-your-writes**: user writes then reads from a replica and sees stale state — route post-write reads to primary (sticky sessions or LSN tracking).
- **Timezone of DATE boundaries**: "today's signups" differs by 8 hours between UTC and PT; every date-bucketed query must state its timezone (`date_trunc('day', created_at AT TIME ZONE 'America/Los_Angeles')`) — dashboards silently lie otherwise.
- **Lock queue behind idle-in-transaction**: an app that opens a transaction and awaits an external API holds locks and blocks vacuum; set `idle_in_transaction_session_timeout`.

## Tradeoffs

- **Normalize vs denormalize**: normalized schemas stay consistent by construction; denormalization (counter caches, materialized rollups) buys read speed at the cost of maintenance logic and drift risk. Denormalize only measured hot paths, keep the normalized source of truth, and add reconciliation checks.
- **Indexes vs write throughput**: each index adds ~10%-ish write cost and WAL volume. Read-heavy tables tolerate many; ingest-heavy tables want the minimum set.
- **Strict constraints vs migration flexibility**: heavy constraints make refactors more careful (you must relax/revalidate); the alternative — invariants in app code — fails the day a second writer appears (jobs, backfills, other services). Constraints win at scale of contributors.
- **JSONB vs columns**: JSONB absorbs heterogeneous data without migrations; costs type safety, statistics quality (planner estimates suffer), and constraint power. Rule: JSONB for payloads you store and fetch; columns for anything you filter, join, or aggregate on.
- **Partitioning**: buys pruning and cheap retention (drop partition) at the cost of DDL complexity, unique-constraint limits (must include partition key), and per-partition planning overhead. Usually earns its keep >100M rows or with time-based retention; premature before that.
- **Bigger box vs sharding**: vertical scaling and read replicas are operationally free compared to sharding's tax on every future query and migration. Exhaust them first; when sharding, the partition key is a one-way door — pick the key your access patterns already scope by (usually tenant).

## Optimization Strategies

- Fix statistics before adding indexes: `ANALYZE`, raised statistics targets, extended statistics on correlated columns — free and often sufficient.
- Covering indexes (`INCLUDE` columns) to convert index scans into index-only scans for hot read paths — watch that visibility map stays healthy (vacuum) or index-only degrades.
- `pg_stat_statements` is the map: rank by `total_exec_time`, fix the top 3, re-rank. Optimizing anything not on the list is entertainment.
- Reduce round trips: batch queries, use CTEs/joins to fetch object graphs, move multi-statement dances into single statements (`ON CONFLICT`, CTE-with-RETURNING pipelines).
- Cache at the application layer only after query-level fixes are exhausted — a fixed 5 ms query beats a cached 500 ms one (no invalidation bugs).
- For write bursts: `synchronous_commit = off` for tolerable-loss writes (analytics events), COPY for loads, and consider unlogged tables for rebuildable data.

## Self Review

- Can I name the query each index serves? Can I show the plan proving it's used?
- What happens to each critical query at 10× rows — did I actually test with generated data, or am I extrapolating from 1,000 rows?
- Which migration step takes which lock, for how long, and what happens if it waits behind a 10-minute query? Did I set lock_timeout?
- If a backfill dies at 60%, is the system consistent? Can it resume?
- Are there transactions that can span user interactions or external calls?
- Do my date/time queries state their timezone explicitly?
- What's my slowest query per `pg_stat_statements` right now — and is my planned work aimed at it, or at something more fun?

## Examples

**1. Reading the plan, fixing the stats.**
Query joining `orders` → `users` filtered by `orders.status = 'pending' AND orders.region = 'EU'` takes 4 s. Plan shows Nested Loop with estimate 12 rows, actual 48,000 (status and region are correlated: EU launched recently, everything's pending). Fix: `CREATE STATISTICS orders_status_region (dependencies) ON status, region FROM orders; ANALYZE orders;` Planner switches to Hash Join; 90 ms. No index added, no hint needed — the estimate was the bug.

**2. Zero-downtime NOT NULL on a 200M-row table.**
Goal: `ALTER TABLE events ADD COLUMN account_id bigint NOT NULL`. Direct path = table rewrite + long lock. Expert sequence: (1) add column nullable; (2) deploy code dual-writing; (3) backfill in 10k batches keyed by PK range with 50 ms sleeps, resumable via progress marker; (4) `ADD CONSTRAINT events_account_id_not_null CHECK (account_id IS NOT NULL) NOT VALID;` (5) `VALIDATE CONSTRAINT` (takes only SHARE UPDATE EXCLUSIVE); (6) PG12+: `ALTER COLUMN SET NOT NULL` now uses the validated constraint proof, no scan. Each step reversible; total exclusive lock time: milliseconds.

**3. Keyset pagination rescue.**
Admin list at page 2,000 (`OFFSET 100000 LIMIT 50`) takes 12 s and gets slower weekly. Replace with `WHERE (created_at, id) < ($1, $2) ORDER BY created_at DESC, id DESC LIMIT 50` backed by index `(created_at DESC, id DESC)`; cursor = last row's `(created_at, id)` encoded. Every page now ~2 ms regardless of depth; pages are stable under concurrent inserts. UI trades "jump to page N" for infinite scroll + date filter — a product conversation the expert has upfront.

**4. Job queue without new infrastructure.**
Need: background email jobs, exactly-once-ish, transactional with order creation. Instead of Redis+worker framework: `jobs` table; enqueue in the same transaction as the order (outbox by construction); workers run `UPDATE jobs SET state='running', locked_by=$1 WHERE id = (SELECT id FROM jobs WHERE state='queued' AND run_at <= now() ORDER BY run_at FOR UPDATE SKIP LOCKED LIMIT 1) RETURNING *;` Crash recovery via `locked_at` timeout sweep. Handles thousands of jobs/minute; revisit only if volume demands it.

## Evaluation Rubric

Score 1–10:

- **1–2**: Schema mirrors objects with nullable-everything; no constraint strategy; indexes guessed; migrations run raw ALTERs in peak hours; no plan literacy.
- **3–4**: Sensible normalized schema; some indexes but unattributed; EXPLAIN consulted but misread (fixates on "Seq Scan bad"); migrations mostly safe by luck.
- **5–6**: Access patterns documented; indexes mapped to queries; lock-aware migrations with CONCURRENTLY and batched backfills; plans read correctly for common cases; timezone and pagination handled.
- **7–8**: Full checklist; realistic-volume baselines; stats-first plan debugging; expand/contract deploys routine; pooler and timeout guardrails set; pg_stat_statements-driven optimization.
- **9–10**: Additionally: constraints encode the domain (EXCLUDE, partial uniques where apt); partitioning/retention strategy where warranted with written rationale; reconciliation for denormalizations; failure-mode drills (backfill dies midway, invalid index) rehearsed; the schema survives a hostile "insert bad data" review.
