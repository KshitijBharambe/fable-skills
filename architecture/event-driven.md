# Event-Driven Architecture

## Purpose

Design systems that communicate through events — event schemas, sagas, CQRS, eventual consistency — capturing the decoupling and replay superpowers without drowning in event soup, ordering bugs, and consistency surprises.

## When to use

- Multiple services/consumers need to react to the same business facts.
- Cross-service workflows need coordination without distributed transactions.
- Read models diverge structurally from write models (reporting, feeds, search indexes).
- Audit/replay requirements ("what happened, in order, and can we rebuild state?").
- Reviewing designs that dual-write, or that propose "just publish an event" as glue.

## Goals

- Events are well-defined facts (past-tense, immutable, versioned) with clear ownership.
- Eventual consistency is a *product decision* with designed UX, made before the architecture ships.
- Every consumer is idempotent; every producer is atomic with its state change (outbox).
- The event flow is observable and documented — anyone can answer "what fires when, and who listens?"

## Inputs

- The workflow inventory: which state changes matter beyond their own service, who needs to react, how fast.
- Consistency requirements per flow: what must be immediate, what tolerates seconds/minutes of lag (with product sign-off).
- Ordering requirements: per-entity? cross-entity? (Be suspicious of any "global.")
- Existing messaging infrastructure and the team's operating maturity with it (see async-processing for transport mechanics).

## Expert Mental Model

- **Events are facts; commands are requests.** `OrderPlaced` (past tense, immutable, already true) vs `ReserveInventory` (imperative, addressed to one handler, can be rejected). Mixing them corrupts the architecture: an "event" that exists to make one specific service do one specific thing is a command wearing a costume — and its publisher now secretly depends on that consumer's behavior. Events announce; commands instruct. Choose consciously per interaction.
- **Event-driven trades knowing-what-happens-next for decoupling.** A synchronous call gives you an answer and a failure you can handle in-line; an event gives you freedom from the consumer's existence — and eventual consistency, invisible control flow, and debugging-across-a-topic. This trade is worth it when consumers genuinely multiply and vary independently; it's pure cost when there's one consumer that must succeed for the user's request to mean anything. "Just publish an event" as default glue produces systems where nobody can trace a workflow.
- **Eventual consistency is a UX problem before it's a technical one.** "The order shows Placed but inventory hasn't confirmed" — the product must decide what users see in the gap (optimistic display, pending states, read-your-writes islands). Experts get this signed off *before* choosing the architecture, because retrofitting "actually, the dashboard lags by up to a minute" onto stakeholders who assumed immediacy is how event-driven projects lose their sponsors (see interface-states, system-design consistency budgets).
- **Fat vs thin events is the coupling dial.** Thin events (`OrderPlaced {order_id}`) force consumers to call back — fresh data, but the producer's API is now load-bearing for every consumer, and a producer outage stops all downstream processing. Fat events (event-carried state transfer: the order's relevant state in the payload) decouple availability — consumers work from the event alone — at the price of schema governance and staleness-at-read. Default: carry the state consumers need to *act*, keep the ID for those who need to *verify*.
- **Schema evolution is the long game.** Events outlive code: additive-only changes (new optional fields), never rename/retype/remove without a versioned migration path; consumers are tolerant readers (ignore unknown fields, don't require the optional); a schema registry (or at minimum a reviewed schemas repo) is the difference between evolution and archaeology. The event you published in 2024 will be replayed in 2027 against code that has forgotten it.
- **Sagas replace transactions across services** — a sequence of local transactions each emitting the next step, with *compensating actions* for rollback (can't un-charge? refund). Choreography (each service reacts to events) stays simple to ~3 steps then becomes invisible control flow; orchestration (a coordinator drives the steps, state machine explicit) scales to complex flows and adds a component. The compensation design IS the hard part: compensations can fail too, some actions can't be compensated (sent emails), and the saga's intermediate states leak into UX.
- **Replay is the superpower with a safety on.** An event log lets you rebuild read models, backfill new consumers, and debug by re-running history — *if* consumers are idempotent and side effects are gated (replaying a year of `OrderPlaced` must not send a year of confirmation emails). Design consumers replay-safe from day one (idempotency + side-effect gating on current state) or the superpower is a loaded footgun (see async-processing).

## Workflow

1. **Model the events from the domain**: name the business facts (event storming with domain experts is the efficient route — see domain-modeling): past-tense, entity-anchored, meaningful to a business person (`InvoiceSettled`, not `RowUpdated`). Data-change events (`XChanged {diff}`) are a smell of CDC-thinking where domain-thinking was needed.
2. **Classify each interaction**: event (many/varying consumers, fact announcement) vs command (one accountable handler) vs synchronous call (caller needs the answer now). Write the classification down; it's the architecture.
3. **Get the consistency budget signed** per flow: max acceptable lag, what the UX shows in the gap, which reads must be read-your-writes (those stay in the write model's transaction/database).
4. **Design the schemas**: envelope (event_id, type, version, occurred_at, correlation_id, causation_id, producer) + payload (state needed to act; IDs to verify); additive-evolution rules; registry/repo with review.
5. **Wire producer atomicity**: outbox pattern in every producer (event written in the same transaction as the state change; relay publishes) — no dual-writes, ever (see async-processing).
6. **Design consumers idempotent and replay-safe**: dedup by event_id or natural key; version-compare for out-of-order tolerance; side effects gated on current state ("send email only if not sent per DB"), not on event receipt.
7. **Scope ordering**: per-aggregate ordering via partition keys (see async-processing); design consumers to tolerate cross-aggregate disorder; challenge any global-ordering requirement until it confesses or dies.
8. **For multi-step workflows, choose saga style**: ≤3 steps with obvious compensation → choreography; more steps, branching, timeouts, human waits → orchestrator (explicit state machine, persisted, resumable). Design every compensation path and the "compensation failed" escalation (usually: park + alert + human).
9. **Make the flow observable**: correlation IDs through every hop; a topology document or generated catalog (event → producers → consumers); lag alerts per consumer group (see async-processing); a trace of one business transaction should read end-to-end (see observability).
10. **Plan the replay/backfill mechanics** before the first new-consumer request: retention policy, snapshot+replay procedure for rebuilds, side-effect kill-switch for replays, and a rehearsed runbook.

## Decision Tree

- If the caller needs the result to respond to the user (payment authorization, validation) → synchronous call with the reliability quartet (see system-design). Don't event-wash request/response.
- Else if exactly one service must act and its failure must be handled → command on a queue (with DLQ + alerting — see async-processing).
- Else if multiple consumers react independently to a fact → event on a topic/stream.
- If consumers need data the producer has:
  - Consumers act autonomously / must survive producer outage → fat event (state transfer), schema-governed.
  - Consumers occasionally enrich / data is sensitive or huge → thin event + callback API (accept the availability coupling) or claim-check (payload in object storage).
- If a workflow spans services with rollback needs →
  - ≤3 steps, linear → choreographed saga (events trigger next steps; compensating events on failure).
  - Complex/branching/timed → orchestrated saga (state machine persisted; consider a workflow engine before hand-rolling one — see async-processing).
- If read models need different shapes than the write model →
  - One DB can serve both with views/indexes → do that (CQRS-lite: separate read queries, same store). 
  - Genuinely divergent scale/shape (search, feeds, analytics) → event-projected read models, rebuilt from the log, with lag budgets stated.
- If someone proposes event *sourcing* (events AS the source of truth, state derived) → demand the driver: audit-grade history, temporal queries, or replay-as-requirement. Without one, take event-driven (events as *notifications*, DB as truth) — event sourcing's costs (versioning forever, snapshotting, query complexity) need a real payer.
- If two services keep needing each other's events synchronously-ish → the boundary is probably wrong; consider merging them (see system-design service extraction — this is its inverse).

## Heuristics

- Name test: an event name a PM understands (`SubscriptionRenewed`) marks a domain fact; `UserTableUpdated` marks database plumbing leaking into architecture.
- Every event carries correlation_id (the business transaction) and causation_id (the event that triggered this one) — the two fields that make production debugging possible (see production-debugging).
- Consumers own their cursor: a new consumer starts from wherever it needs (beginning for rebuilds, now for reactions) — producers never track who consumed.
- The producer must not know its consumers; the moment producer code says "publish this so billing does X," you've built a command — either own that (queue, DLQ, accountability) or restore the fact-framing.
- Publish after commit, always (outbox); an event about a rolled-back transaction is a lie propagating at wire speed.
- Version from day one (`v: 1` costs nothing; retrofitting versioning onto unversioned streams costs a migration).
- Consumer lag is the health metric; oldest-unprocessed-age beats message counts (see async-processing); every consumer group gets an alert tied to its flow's consistency budget.
- Test consumers with: duplicate delivery, out-of-order pairs, unknown fields, replay-of-history — the four horsemen of event consumption; a consumer test suite without them tests the happy path only (see concurrency-bugs for the shapes).
- Compensation ≠ undo: design compensations as *new forward facts* (`PaymentRefunded`, not deleting `PaymentCaptured`) — history is append-only or it isn't history.
- Keep the event catalog generated or CI-checked against code; hand-maintained topology docs are fiction within a quarter.
- If debugging a flow requires reading five consumers' code to find who reacts to what, the system has event soup — invest in the catalog and consider consolidating gratuitous hops.

## Quality Checklist

- [ ] Events are past-tense domain facts; commands and sync calls explicitly classified separately.
- [ ] Consistency budget per flow signed by product; gap UX designed; read-your-writes islands identified.
- [ ] Envelope standard (ids, version, correlation/causation, occurred_at) enforced; schemas registered and additive-only.
- [ ] Outbox (or equivalent) on every producer; zero dual-writes.
- [ ] Consumers idempotent, out-of-order-tolerant, replay-safe (side effects gated on state); the four-horsemen tests exist.
- [ ] Ordering scoped per-aggregate via keys; no unexamined global-ordering assumptions.
- [ ] Sagas: every step's compensation designed; compensation-failure path parks+alerts; orchestration state persisted and resumable.
- [ ] Correlation IDs traverse end-to-end; event catalog current (generated/CI-verified); lag alerts per consumer tied to budgets.
- [ ] Replay/backfill runbook exists with side-effect kill-switch; retention policy deliberate.
- [ ] Read-model rebuild procedure tested, not theoretical.

## Failure Modes

- **Event soup**: 200 event types, ambient reactions everywhere, no catalog — a change to one producer breaks three consumers nobody knew existed; onboarding engineers takes months because control flow is archaeology.
- **Dual-write drift**: state committed, publish failed (or reversed) — systems disagree forever, discovered by reconciliation-by-customer-complaint (see async-processing; the outbox exists for this).
- **Commands in event costumes**: `SendWelcomeEmailEvent` — one consumer, mandatory success, but no DLQ accountability because "it's just an event"; the email silently stops for three weeks.
- **Eventual consistency ambush**: dashboard lags 45 s behind the write; support tickets say "my data disappeared"; product learns about the consistency model from customers. The budget was never surfaced.
- **Blind-apply consumers**: applying `v2` then `v1` of an update because ordering was assumed — state regresses; version-compare was one field away.
- **Replay with live ammunition**: rebuilding a read model replays 2M events through a consumer that emails on each; the kill-switch didn't exist; neither does customer goodwill.
- **Saga without compensation design**: step 4 of 5 fails; steps 1–3 are permanent; the "rollback" is an engineer with a SQL console at midnight. The saga was a happy-path pipeline wearing a pattern's name.
- **Schema big-bang**: renamed field ships; every consumer breaks simultaneously; the registry that would have failed the PR was "overhead."
- **Event sourcing by fashion**: the entire domain event-sourced because a talk was inspiring; a year later: snapshot infrastructure, upcasters for 14 event versions, and a team begging for `SELECT * FROM accounts`.

## Edge Cases

- **Out-of-order across topics**: `OrderPlaced` (orders topic) and `PaymentCaptured` (payments topic) race; any consumer joining both needs state-based tolerance (park-and-wait or re-drive) — cross-topic ordering doesn't exist.
- **The poison replay**: historical events that current validation rejects (schema was looser then) — replay paths need tolerant readers or era-aware upcasting; "clean data" assumptions die against 2019's events.
- **Consumer needs data the event's era didn't carry**: new consumer requires a field producers only started emitting last month — backfill strategy: enrich-on-read from source, or synthetic backfill events, chosen per cost.
- **GDPR/erasure vs immutable log**: right-to-be-forgotten against append-only history — crypto-shredding (per-subject keys, delete the key) or payload-tombstoning designed *before* the first PII event, not after the first request.
- **Clock skew in occurred_at**: producers' clocks disagree; ordering decisions use sequence/offsets, `occurred_at` is metadata for humans (see concurrency-bugs).
- **The whale aggregate**: one tenant's aggregate receives 100× the events — its partition heats (see async-processing key skew); per-aggregate ordering for the whale may need its own lane.
- **Cyclic reactions**: service A's consumer emits events consumed by B whose consumer emits events consumed by A — a feedback loop invisible until an infinite amplification incident; the catalog + causation_id chains are how you detect cycles pre-production.
- **Local dev/test topology**: engineers can't run 12 consumers locally — contract tests against schemas + a lightweight in-proc bus for tests beat requiring a laptop Kafka; otherwise testing atrophies to "deploy and pray."

## Tradeoffs

- **Decoupling vs traceability**: every event hop removes a compile-time dependency and adds a runtime mystery. Buy decoupling where consumers genuinely vary/multiply; keep direct calls where the flow is one path that must be reasoned about under incident pressure.
- **Fat vs thin events**: availability-independence and replayable self-sufficiency vs schema-governance burden and staleness; the dial is per-event, not per-architecture — carrying `order_total` is cheap decoupling; carrying the whole customer object is a schema tax with PII interest.
- **Choreography vs orchestration**: choreography has no coordinator to operate and no single place to read the flow; orchestration has one of each. Below ~3 steps the coordinator is overhead; above, its absence is the overhead.
- **Event-driven vs event-sourced**: notifications with DB-as-truth gives most decoupling benefits at familiar query cost; sourcing gives perfect history and temporal queries at permanent complexity. The middle exists: source the one aggregate that needs audit-grade history, notify for everything else.
- **Consistency budget vs infrastructure spend**: shrinking lag from minutes to seconds to sub-second climbs an exponential cost curve (bigger clusters, hotter paths, more failure modes). Negotiate the budget before engineering the latency.
- **One shared bus vs per-domain topics**: centralization eases discovery and governance; it also couples blast radius and tempts a "god topic." Per-domain topics with a shared catalog is the usual adult compromise.

## Optimization Strategies

- Generate the event catalog from code/schemas in CI (producers, consumers, payloads, owners) — the single highest-leverage artifact against soup; stale docs are worse than none.
- Invest in the developer experience: local contract tests, consumer test harness with the four horsemen built in, golden-path templates (outbox+consumer skeleton) — the pattern's discipline survives only if the paved road is easier than the shortcut.
- Add reconciliation jobs on the money paths: periodic comparison of source-of-truth vs projections (counts, sums, spot checksums) with drift alerts — the safety net under all eventual machinery (see async-processing).
- Trace one business transaction end-to-end weekly (pick a random correlation_id, walk it) — the ritual that keeps observability honest and finds broken causation chains before incidents do.
- Snapshot aggressively where rebuilds matter: read-model rebuild time grows with history; periodic snapshots + tail-replay keeps "rebuild the search index" an hours job, not a weekend.
- Prune events nobody consumes (catalog + consumer metrics show them) — every dead event type is schema surface and mental load; deprecate with the same ceremony as APIs (see api-design).

## Self Review

- For each interaction: is it truly an event (fact, N consumers) — or a command/call I'm event-washing? Who is accountable when it's not consumed?
- What does the user see during each flow's consistency gap, and who signed off on that?
- Where exactly is the atomicity between state change and publish? (Point at the outbox.)
- Can every consumer survive: a duplicate, a reorder, a replay, an unknown field? Where are those tests?
- For each saga step: what's the compensation, can *it* fail, and what happens then?
- Could I hand a correlation_id to a new engineer and have them walk the whole flow from the catalog + traces?
- What's my rebuild story for each projection, and when was it last rehearsed?
- Which events exist because the domain speaks them — and which because a database sneezed?

## Examples

**1. Order flow with the full discipline.**
`OrderPlaced` (fat: items, totals, address — what fulfillment/email/analytics need to act; IDs for verification) published via outbox in the order transaction, keyed by `order_id`. Consumers: fulfillment (idempotent reservation, upsert on `(order_id, sku)`), notifications (send gated on `emails.confirmation_sent_at IS NULL` — replay-safe), analytics (append + downstream dedup). Payment authorization stays a *synchronous* call in checkout (user needs the answer) — classified, not event-washed. Consistency budget: fulfillment lag ≤2 min (alerted at 5), dashboard lag ≤60 s with a "processing" chip in the UI (product signed the Figma). Catalog entry generated from schema registry; correlation_id from the HTTP request through every hop.

**2. Saga: subscription upgrade with real compensations.**
Steps: charge card → upgrade plan → provision seats → notify. Orchestrated (4 steps, timeout on provisioning, human-visible intermediate states): persisted state machine per upgrade. Compensations designed per step: charge → refund (a forward event `PaymentRefunded`, not a deletion); plan → revert with version check; provisioning timeout → park in `needs_attention` + page (compensation-failure path is explicit: no infinite auto-retry against a broken provisioner). UX shows "Upgrading… (2/4)" from the machine's state — the saga's intermediate states are product surface, designed with interface-states. The rejected choreography sketch is in the doc: four services reacting to each other's events made the timeout path unreadable.

**3. CQRS-lite: the read model that earned itself.**
Search page needs faceted queries the OLTP schema serves at 4 s. Options priced: (a) heroic SQL + indexes (tried: 800 ms, still coupling search shapes to the write schema), (b) event-projected Elasticsearch read model. Chosen (b) *with the receipts*: `ProductUpdated` events (already existed) project into search docs; lag budget 30 s (product-approved — new products may take a moment to appear in search, banner on the product page bridges it); rebuild runbook: snapshot + replay, rehearsed at 40 min for 5M products; reconciliation: hourly count-and-checksum diff with drift alert. Write model untouched; the projection is disposable by design — "we can delete and rebuild it" is the property that keeps it honest.

**4. Untangling event soup (the rescue).**
Inherited: 140 event types, no registry, three incidents from unknown consumers breaking on schema changes. Rescue sequence: (1) instrument consumption — which events have zero consumers (31: deprecated), which consumers exist per event (generated catalog from consumer-group introspection + code scan); (2) envelope+versioning standard enforced on new events, CI schema-diff gate (additive-only) on all; (3) the five business-critical flows traced, documented, and given correlation-ID lint + lag alerts; (4) command-costume events (single mandatory consumer) reclassified onto queues with DLQs — accountability restored; (5) quarterly prune ritual. Not rewritten — *governed*. Six months later: schema change incidents zero, onboarding doc is the generated catalog, and the soup is a menu.

## Evaluation Rubric

Score 1–10:

- **1–2**: Dual-writes; events as ad-hoc glue; no schemas/versioning; consumers assume order and uniqueness; consistency gaps discovered by users; no catalog.
- **3–4**: Broker used with some conventions; outbox partial; idempotency ad-hoc; sagas are happy-path pipelines; topology in someone's head.
- **5–6**: Facts vs commands classified; outbox on critical producers; consumers pass duplicate/reorder tests; consistency budgets stated; basic catalog and lag alerts.
- **7–8**: Full checklist: replay-safe side-effect gating, compensation-designed sagas with failure parking, generated catalog, correlation tracing end-to-end, rebuild runbooks rehearsed, reconciliation on money paths.
- **9–10**: Additionally: event sourcing scoped only where drivers exist; erasure/PII strategy in the log design; cycle detection via causation chains; whale/skew handling; the architecture's consistency model is documented product surface — support and PMs can answer "why does it lag?" without paging engineering.
