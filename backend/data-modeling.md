# Data Modeling

## Purpose

Design the shape of stored data — entities, relationships, constraints, identifiers, history — so it tells the truth about the domain, survives schema evolution, and serves the actual access patterns; the schema outlives every application that touches it, and its mistakes compound with every row written.

## When to use

- Designing the schema for a new feature, service, or product.
- Choosing between normalization and denormalization, or between relational/document/wide-column shapes.
- Modeling something notoriously slippery: money, time, addresses, hierarchies, polymorphism, history.
- Reviewing a migration that adds tables or changes relationships (see postgres for the mechanics).
- Data quality problems keep surfacing: duplicates, orphans, states that "shouldn't be possible."

## Goals

- The schema makes illegal states unrepresentable where practical: constraints enforce what the domain forbids.
- Every entity has a stable identity; every relationship has explicit cardinality and deletion behavior.
- Normalized by default with denormalization as a documented, maintained decision — never an accident.
- The model serves the measured access patterns, not just the domain diagram.
- Evolution is planned: the schema can change without archaeology (see refactoring: expand-migrate-contract).

## Inputs

- The domain's real entities, relationships, and invariants — from domain experts, not just the ticket (see domain-modeling; decomposing-ambiguity).
- Access patterns: the queries that will run, their frequency and latency budgets (see postgres; system-design).
- Cardinality realities: how many of each, growth rates, hot vs cold data.
- Consistency requirements per relationship: what must be transactionally true vs eventually true (see event-driven).
- Compliance/retention constraints on the data (see compliance-and-privacy).

## Outputs

- An entity-relationship model with cardinalities, constraints, and deletion semantics per edge.
- DDL with the invariants encoded: types, nullability, uniques, foreign keys, checks.
- A written record of denormalizations and their maintenance mechanism.
- The identifier strategy (surrogate/natural, ID type, exposure policy) and the history/audit strategy per entity class.

## Expert Mental Model

- **The schema is the longest-lived artifact you'll ship.** Applications get rewritten; the data survives and migrates (see refactoring: the data outlasts the code around it). A wrong column type is a day-one typo and a year-three migration project. This asymmetry justifies more care per decision here than almost anywhere else — and explains the prime directive: model the *domain's truths*, not the current UI's convenience. Screens change quarterly; "an order has exactly one currency" is forever.
- **Constraints are executable domain knowledge.** Every NOT NULL, unique, foreign key, and check constraint is a fact about the domain that the database now *enforces against every writer forever* — including the future batch job, the intern's script, and the bug. "We validate in the application" protects one write path of many; the constraint protects all of them, at the only chokepoint that sees every write. When you find yourself writing cleanup jobs for orphans and duplicates, you're doing by hand what a constraint would have done for free (see postgres: constraints and the planner both love them).
- **Normalization is about update anomalies, not aesthetics.** A fact stored once has one version of the truth; a fact stored in five rows can disagree with itself after any partial update — that's the actual argument, not third-normal-form piety. Normalize until it hurts the read paths that matter, then denormalize *deliberately*: named, measured, with a maintenance mechanism (trigger, event, rebuild job) and a source of truth designated — a denormalization without a sync story is a data-corruption schedule (see caching: same invalidation law, storage edition).
- **Model the questions, not just the things.** The ER diagram answers "what exists"; production answers "what gets asked ten thousand times a second" (see system-design: access patterns drive storage). Relational engines tolerate flexible querying over a normalized core; document and wide-column stores demand you know the questions first (the model *is* the query plan). Either way, a model that mirrors the domain but can't answer its top-five questions without heroics is wrong — and the fix is usually a maintained projection (read model), not abandoning the normalized core (see event-driven: CQRS is this pattern with ceremony).
- **Identity is a design decision with a blast radius.** Surrogate keys (auto-int, UUID) decouple identity from mutable attributes — emails change, "natural keys" turn out to be neither natural nor stable (see the auth edge cases on email identity). Choose ID types for their properties: sequential ints are compact and enumerable (an IDOR invitation when exposed — see security); UUIDv4 is unguessable and index-hostile at scale; UUIDv7/ULID gets both time-locality and opacity. Decide *at design time* which IDs are external (exposed in URLs/APIs — see api-design) and which stay internal; retrofitting opacity later is a migration.
- **Time is a dimension, not a column afterthought.** "What is true now" (current state), "what was true then" (history), and "when did we learn it" (audit) are three different questions; conflating them corrupts all three. The ladder: mutable-in-place (no history) → `updated_at`/soft-delete flags (breadcrumbs) → audit/event log alongside current state (who changed what when — see compliance-and-privacy: often required) → full temporal/bitemporal modeling (validity periods as first-class, for domains like pricing, contracts, payroll where "the rate *as of* March" is a business question). Choose the rung per entity class deliberately — upgrading later means reconstructing history you didn't record.

## Workflow

1. **Extract entities and invariants from the domain**: nouns that have identity and lifecycle (Order, Customer) vs values that don't (Money, Address — see domain-modeling for the behavioral side). For each invariant, ask: enforceable in the schema, or application-level with a documented reason?
2. **Map relationships with their full contracts**: cardinality (1:1, 1:N, M:N), optionality, and deletion behavior (cascade, restrict, nullify) — "what happens when the parent dies" is a domain decision to make now, not an ON DELETE clause to guess later.
3. **Gather the access patterns**: top queries by frequency and latency budget, write patterns, growth projections. This list arbitrates every normalization and indexing debate downstream (see postgres for index design against it).
4. **Design the normalized core**: one fact, one place; separate tables for separate concepts; junction tables for M:N (which usually turn out to have their own attributes — the relationship is often an entity in disguise: `Enrollment`, not `student_course`).
5. **Choose types with the domain's precision**: money as integer minor units or NUMERIC (never floats — see the classic corruption), timestamps with timezone in UTC, text with checks over enums-by-convention, domain types where the engine offers them.
6. **Encode the invariants**: NOT NULL by default (nullable is the exception that needs a reason), uniques on business identity, FKs on every reference, checks for ranges and state rules; partial/composite uniques for the subtle ones ("one active subscription per customer").
7. **Decide the identity strategy** per entity: surrogate internal key + business identifiers as unique attributes; external ID type chosen for exposure properties; never overload meaning into keys.
8. **Add the time dimension** per entity class: which rung of the history ladder, and where audit requirements force append-only structures (see compliance-and-privacy).
9. **Apply deliberate denormalization** only against measured read pain: name the source of truth, build the maintenance mechanism, monitor drift (a reconciliation query in a scheduled job is cheap insurance).
10. **Review the model against evolution**: what changes when the business adds a second currency / country / product line / tenant? The model needn't support them now — it must not make them archaeologically expensive (see system-design: one-way doors; multi-tenancy from day one is usually the right paranoia — see auth: tenant scoping).

## Decision Tree

- If a "field" can disagree with itself across rows (customer name on every order) → it's an entity reference, not a column; normalize it out. Exception: point-in-time *snapshots* (the shipping address as it was at order time) are facts about the order, not references — copy deliberately, name it a snapshot.
- If two entities relate M:N → junction table; then ask what the relationship itself knows (dates, status, role) — attributes on the junction usually reveal a real domain concept.
- If modeling polymorphism (comments on posts *and* photos) → exclusive-arc FKs (one nullable FK per target + check that exactly one is set) for integrity; single `target_type/target_id` pair only when target sets are open-ended, accepting lost FK enforcement, with application discipline documented.
- If modeling hierarchies (categories, org charts) → adjacency list + recursive CTEs for most cases (see postgres); materialized paths or closure tables only when tree-read patterns are hot and measured.
- If a status/state column appears → define the legal transitions (see domain-modeling: state machines); enforce the vocabulary (enum/check) and consider whether history of transitions is a requirement (it usually becomes one).
- If tempted to store JSON → is it *opaque payload* (vendor webhook, user-defined fields — genuinely schemaless: fine, JSONB it) or *lazy schema* (your own domain fields you didn't feel like modeling: every query, index, and constraint gets harder — model it)? The test: will you ever WHERE/JOIN on its contents?
- If reads need five joins at high frequency with a tight budget → maintained projection (materialized view, event-updated read table) over the normalized core; the core stays truthful, the projection stays fast (see caching; event-driven).
- If choosing the store itself → relational by default (flexible questions, constraints, transactions); document store when the aggregate is genuinely the unit of everything (always read/written whole); wide-column/KV when one massive access pattern rules (see system-design: boring tech until the numbers argue).
- If deletion is requested → distinguish: domain state ("cancelled" — model it explicitly, it's not deletion), operational undo (soft delete with `deleted_at`, filtered everywhere — mind the partial-index and unique-constraint interactions), and compliance erasure (hard delete or crypto-erasure on schedule — see compliance-and-privacy; soft delete is *not* erasure).
- If multi-tenant → `tenant_id` on every tenant-owned row from day one, in every unique constraint and every index's leading columns (see auth: tenancy as structural invariant; postgres: RLS as the second layer).

## Heuristics

- Nullable is a tri-state trap: every NULL column makes queries answer three-valued questions; default NOT NULL and let nullability be argued for, not defaulted into.
- If you can't name the table's row in a sentence ("one row = one payment attempt"), the table doesn't know what it is — and neither will its writers.
- Booleans breed: `is_active`, `is_archived`, `is_deleted` on one table encode a state machine in denial — model the status once, with legal transitions (see domain-modeling).
- Wide tables confess mixed concerns: 60 columns usually means three entities cohabiting (the 1:1 split by lifecycle/access is normalization too).
- Store money as (amount_minor_units INTEGER/NUMERIC, currency CHAR(3)) — an amount without a currency is a number, not money; arithmetic across currencies is a bug wearing a sum.
- Timestamps: UTC in storage, timezone at the edge; `date` when the domain means a calendar date (birthdays don't have timezones); "created/updated/happened" are three different times — name which one you mean.
- The unique constraint is the deduplication strategy: dedup jobs exist where uniques don't.
- Enum-by-check beats enum-by-convention beats enum-by-magic-number; and every enum column's values will grow — plan the addition path (see postgres: enum migration pain).
- Count the 9s of cardinality honestly: "a user has a few addresses" — is 500 legal? The model should know its own limits or admit it has none.
- Foreign keys off "for performance" is a diagnosis, not a strategy — the integrity you disabled becomes the reconciliation job you now own (exception: genuinely append-only analytics ingestion, documented).
- Reference data (currencies, countries, plans) gets tables with FKs, not string literals scattered through code and rows.
- Name for the domain, not the ORM: `subscription_periods` not `sub_data_2`; the schema is documentation read by every future debugger (see technical-writing: names are the API).

## Quality Checklist

- [ ] Every table's row nameable in one sentence; every column's owner unambiguous (one fact, one place — or a named snapshot/denormalization).
- [ ] NOT NULL default; every reference an FK with explicit ON DELETE; uniques on business identity including the partial/composite subtleties.
- [ ] Types carry the domain: money with currency, UTC timestamps, checked enums, no floats near money.
- [ ] Identity strategy decided: internal surrogate, external exposure type, natural candidates as unique attributes.
- [ ] Status columns have defined transition rules; history/audit rung chosen per entity class.
- [ ] Denormalizations documented with source of truth + maintenance mechanism + drift check.
- [ ] Access patterns listed; top queries answerable within budget on the proposed shape (see postgres for verification).
- [ ] Deletion semantics per entity: domain state vs soft delete vs compliance erasure.
- [ ] Multi-tenant: tenant_id structural everywhere it applies.
- [ ] Evolution sanity: the known-plausible business changes don't require archaeology.

## Failure Modes

- **The anomaly farm**: customer email copied to orders, invoices, and tickets; a support update fixes one; three systems now disagree about the truth — the normalization argument, lived.
- **Constraints in the app only**: "the API validates it" — then the backfill script, the admin console, and the message consumer each write their own dialect; the cleanup job becomes a permanent fixture (see the class-fix instinct in root-cause-analysis: the constraint was the class fix).
- **The stringly-typed domain**: statuses, categories, and references as free text — `'Active'`, `'active'`, and `'ACTIVE'` are three states now; every query grows `LOWER()` and every report footnotes its numbers.
- **Float money**: `0.1 + 0.2` in the ledger; cents leak at scale; the accounting reconciliation finds it in month nine and trust in the whole dataset dies with it.
- **The JSON junk drawer**: core domain fields living in a `data JSONB` column "for flexibility" — no constraints, no types, keys misspelled per-writer; flexibility for the writer, archaeology for every reader since.
- **EAV for everything**: entity-attribute-value as the schema — infinitely flexible, unqueryable, uncheckable; the database reduced to a key-value store with joins as decoration. (Legitimate EAV exists — user-defined fields — as a bounded island, not the mainland.)
- **Accidental denormalization**: the cached count, the copied status, added in a hot fix with no maintenance mechanism — drifts silently, and the drift is discovered by a customer (see caching: invalidation, storage edition).
- **Soft-delete blindness**: `deleted_at` added, one query in forty forgets the filter — deleted users get emails; unique constraints block re-registration of "deleted" emails; the partial-unique that was needed was never written.
- **Identity built on sand**: email as the primary key — the user changes email, and the migration touches nine tables; the "natural key" was an attribute all along.

## Edge Cases

- **Historical truth vs current reference**: the invoice must show the address *as shipped* and the price *as charged* — snapshot at transaction time by design; joining to current rows silently rewrites history (the auditor notices — see compliance-and-privacy).
- **Bitemporal needs**: payroll/insurance/pricing domains ask "what did we believe on date X about period Y" — validity time and transaction time as separate dimensions; heavyweight, so confine it to entities whose corrections are business events.
- **Merged entities**: two customer records turn out to be one human — identity merge needs a strategy (tombstone + reference rewrite, or merge table) *before* it's needed; retrofitting merge over FKs from twelve tables is a project (see the auth account-linking edge).
- **Ordering and gaps**: sequences guarantee uniqueness, not gaplessness — invoice numbers with legal gap rules need their own counter table with locking (see concurrency-bugs); and client-visible ordering by auto-ID breaks across shards (see system-design).
- **Very large text/blob attributes**: row bloat poisons scans of the hot columns — split the payload to a side table or object storage with a reference (access patterns again).
- **The 100M-row table with a new NOT NULL column**: schema evolution at scale is its own discipline — expand-migrate-contract, backfill in batches, validate-then-enforce (see postgres; refactoring).
- **Cross-store consistency**: the search index, cache, and analytics copy of the row are denormalizations across engines — same laws (source of truth, maintenance mechanism, drift detection), bigger blast radius (see event-driven: outbox; observability for the drift alarms).
- **Time zones and calendars**: "daily report" means midnight *somewhere* — store the tenant's zone as data, compute boundaries per-tenant; DST makes some local days 23/25 hours and the aggregation code must already know.

## Tradeoffs

- **Normalization vs read cost**: joins are cheap but not free at scale; denormalized reads are fast and can drift. Resolution is sequencing: normalized core as truth, projections for measured hotspots — pay the sync machinery only where the read numbers demand it.
- **Constraint strictness vs operational flexibility**: hard FKs and checks block bad data *and* block the emergency backfill with historical dirt — pair strictness with deliberate escape hatches (deferred constraints, staged validation) rather than choosing looseness (see postgres: NOT VALID → VALIDATE pattern).
- **Schema-first vs schemaless**: upfront modeling costs design time and buys every reader a contract; schemaless defers cost to *every* future query and migration. Bounded flexibility (JSONB islands in a modeled sea) usually beats either pole.
- **Surrogate vs natural keys**: surrogates are stable and meaning-free (good) and one more join to answer business questions (mild cost); naturals encode meaning and change when the business does (catastrophic cost). The asymmetry decides: surrogate keys, natural uniques.
- **Generic vs specific modeling**: the `parties` supertable handling customers/vendors/employees is elegant and makes every query a filtered special case; separate tables repeat some columns and stay obvious. Model generically only when the *behavior* is genuinely shared (see abstraction-and-simplicity: rule of three applies to schemas too).
- **History completeness vs volume and privacy**: full audit trails answer everything and grow forever *and* collide with erasure obligations (see compliance-and-privacy) — retention windows and PII-lean event payloads reconcile them; decide at design, not at the first deletion request.

## Optimization Strategies

- Prototype the top queries against the proposed schema with realistic cardinalities *before* committing — an afternoon of EXPLAIN against generated data beats a quarter of migration regret (see postgres; the cheap-test instinct from brainstorming).
- Write the reconciliation queries for every denormalization the day you create it; schedule them; alert on drift (see observability) — denormalization with a drift alarm is a tool; without one it's a time bomb.
- Keep a data dictionary that lives with the schema (comments in DDL, generated docs): every table's sentence, every subtle column's meaning — the model's intent survives its authors (see technical-writing).
- Review schema changes with the same severity as API changes — the schema *is* an API with more consumers and slower rollbacks (see api-design: compatibility discipline; code-review).
- Seed realistic data volumes in staging: models behave differently at 10⁷ rows; the N+1 and the missing index show up before production does (see testing-strategy: realistic data shapes).
- Learn the engine's modeling idioms deeply (see postgres): partial indexes, exclusion constraints, generated columns, RLS — half of "we'll enforce it in the app" is a feature the database already ships.

## Self Review

- Can I state each table's row-sentence and each relationship's deletion behavior without looking?
- Which invariants live only in application code — and what writes bypass that code today?
- Where does the same fact live twice — and is each copy a named snapshot/projection with a sync story, or an accident?
- What are the top five queries, and does the model answer them within budget without heroics?
- What happens to this model when the business adds a currency, a country, a tenant, a second product line?
- For each entity: what does "deleted" actually mean — domain state, soft delete, or erasure — and does the code agree?
- Which IDs leak to the outside world, and are their properties (guessability, sortability) chosen or inherited?
- If I had to answer "what was true on March 3rd" — which entities could, and which should?

## Examples

**1. The subscription model that made illegal states unrepresentable.**
First draft: `subscriptions(user_id, plan, status TEXT, trial BOOL, cancelled BOOL, paused_until, ...)` — booleans breeding, "cancelled but also trialing" representable, one user with three "active" rows. Remodel: `status` as a checked enum with documented transitions (see domain-modeling: the state machine is the domain); partial unique `ON (user_id) WHERE status IN ('trialing','active','paused')` — *one live subscription per user* becomes a database fact; `subscription_periods` as an append-only child (validity ranges, price snapshot at period start — historical truth by construction); money as minor units + currency. Three months later, a billing bug writes a duplicate activation — the constraint rejects it, turning a silent revenue incident into a 500 with a stack trace (see the constraint-as-class-fix argument). The "as of March" revenue question is a query, not a reconstruction.

**2. Deliberate denormalization with a drift alarm.**
A marketplace's search page needs seller name, rating, and review count on every listing card — a five-join read at 3k qps blowing its 50 ms budget. Not: scatter seller columns into `listings` in a hotfix. Instead: `listing_search_view`, an event-maintained projection (seller-updated and review-created events rebuild affected rows — see event-driven) over the normalized core, which remains the only write target. A nightly reconciliation query diffs projection against source; drift alerts at >0.1% (see observability). Two quarters in, a consumer bug drops review events for a day — the alarm fires, the rebuild runs, and the incident report's timeline starts at "drift alarm" rather than "seller complaint," which is the entire argument for the alarm.

**3. The polymorphic comments decision, priced both ways.**
Comments must attach to posts, photos, and (someday) events. Option A: `commentable_type` + `commentable_id` — one table, open-ended, zero FK integrity (orphans arrive with the first cascade-delete bug). Option B: exclusive-arc — nullable `post_id`, `photo_id`, `event_id` + CHECK that exactly one is set — full FK enforcement, schema change per new target. The team measures the actual variability: new commentable types arrive ~yearly, via a migration anyway. Option B wins; the check constraint catches a bug in week two (a service writing comments with *both* IDs set). The rule recorded in the data dictionary: polymorphism by exclusive arc until target types are genuinely user-defined — flexibility priced, not assumed (see abstraction-and-simplicity).

## Evaluation Rubric

Score 1–10:

- **1–2**: Schema mirrors whatever the first UI needed; no FKs or uniques; statuses as free text; floats near money; JSON junk drawers; every invariant "enforced" in one app's validation layer.
- **3–4**: Basic normalization but constraints sparse; nullable-by-default; identity ad hoc (naturals as PKs somewhere); denormalizations accidental and unmaintained; history via `updated_at` and hope.
- **5–6**: Normalized core with FKs, uniques, and checked enums; sane types (money, UTC); surrogate identity with exposure-appropriate external IDs; access patterns considered; deletions distinguished (state vs soft vs erasure).
- **7–8**: Full checklist: invariants pushed into the schema including partial/composite subtleties, history rungs chosen per entity, denormalizations documented with drift checks, evolution rehearsed against plausible business changes, schema reviews as rigorous as API reviews.
- **9–10**: Additionally: prototyped against realistic volumes before commit; data dictionary alive; reconciliation jobs standing on every projection; temporal modeling where the domain truly asks time-travel questions; and constraint-caught incidents on record — the schema demonstrably stopping bugs the application layer missed.
