---
name: deployment
description: "Use when designing how a service ships to production, deploys are scary/manual/rare, choosing rolling vs blue-green vs canary, coordinating schema changes with code, or introducing feature flags and rollback — zero-downtime, expand-migrate-contract, progressive delivery."
---

# Deployment & Release Engineering

## Purpose

Get artifacts into production safely and reversibly — environment parity, config as code, progressive release strategies (rolling, blue-green, canary), rollback that's rehearsed rather than hoped, deploy/release decoupled by flags, and the migration choreography that lets code and schema change without downtime. The ci-cd skill builds the pipeline; this skill governs what happens when the artifact meets production.

## When to use

- Designing the deployment story for a new service or replatforming an old one.
- Deploys are scary, rare, manual, or need announcements and war rooms.
- An incident traced to a deploy: config drift, migration lock, half-rolled-out surprise, unrollbackable release.
- Choosing between rolling, blue-green, and canary; or introducing feature flags and staged rollouts.
- Coordinating risky releases: schema changes, breaking API changes, big features, traffic events.

## Goals

- Any deploy is reversible in minutes by a rehearsed path — rollback is a button, not a project.
- Deploy (bits on servers) and release (users see it) are separate decisions, connected by flags.
- Config and infrastructure are versioned code; environments differ by config values only.
- Schema and code changes are choreographed so every deployed version pair is compatible.
- Releases are observed: every rollout watches its health signals and can halt itself.

## Inputs

- The artifact and its pipeline (see ci-cd: build-once, content-addressed, tested).
- Traffic patterns and tolerance: peak windows, session lengths, what "downtime" costs here.
- The dependency reality: databases, queues, caches, and the other services mid-flight during any deploy.
- Health signals worth gating on: error rates, latency, business metrics (see observability — no signals, no safe automation).
- Compliance constraints on release process: approvals, audit trails, change windows (see compliance-and-privacy).

## Outputs

- A deployment spec per service: strategy, batch/canary sizes, gate metrics, abort thresholds, rollback path.
- Config management: environment values in versioned config, secrets injected at runtime (see security), drift detection.
- The migration playbook: expand-migrate-contract as the default choreography (see postgres; refactoring).
- Flag lifecycle policy: creation, ownership, kill-switch registry, expiry dates.
- A release calendar posture: deploy frequency, freeze policy (if any), and who owns the button.

## Expert Mental Model

- **Deploys fail; the design variable is blast radius and recovery speed.** Some fraction of deploys will always be bad — the mature posture optimizes MTTR and exposure, not the fantasy of zero bad deploys. Small changes, progressively exposed, quickly reversible: each property multiplies the others (a small change is easy to diagnose; progressive exposure caps who it hurt; fast rollback caps how long — see ci-cd: same law from the pipeline side; production-debugging: "what changed" is usually "what deployed").
- **Deploy ≠ release.** Deploying is copying bits; releasing is exposing behavior. Fusing them means every deploy is a user-facing event with a war room. Decoupling them — dark launches (code deployed, flag off), staged percentage rollouts, kill switches — turns releases into *product* decisions made calmly and deploys into boring plumbing that happens continuously. The flag is the mechanism (see resilience-engineering: the same switches serve the degradation ladder).
- **During any deploy, two versions run simultaneously — design for it or be surprised by it.** Rolling deploys, canaries, and rollbacks all mean version N and N+1 serving side by side: sharing a database, exchanging messages, honoring each other's sessions and caches. Every change must be compatible one version in each direction — which is why schema changes go expand-migrate-contract (add nullable column → dual-read/write → backfill → flip → drop old, each step deployed separately — see postgres; refactoring: the same pattern at migration scale), why message schemas evolve additively (see event-driven), and why serialized session/cache formats are versioned (see caching). "It worked in staging" often means "staging never ran two versions at once."
- **Rollback is a product requirement with a test suite, not an aspiration.** The honest questions: does rolling back the code also require rolling back the schema (then you don't have rollback — see the choreography above)? Does the previous artifact still exist, still deploy, still pass health checks? When did anyone last actually roll back? A rollback path unexercised for six weeks is a hypothesis (see resilience-engineering: untested failure paths don't exist). Roll-forward-only is a legitimate posture *if chosen* — with the compensating investments (flags to disable anything, fast pipeline for fixes) — but most teams have it by accident, discovering the missing rollback during the incident that needed it.
- **Environments diverge by default; parity is enforced, not assumed.** "Works in staging, dies in prod" is almost always drift: a config value hand-edited, a dependency version unpinned, an infra difference nobody recorded. The countermeasures: same artifact promoted through environments (never rebuilt per env — see ci-cd), configuration as versioned code with per-env values in one reviewable place, infrastructure as code so environments are *instantiated*, not *maintained*, and secrets injected at runtime from a manager (see security). Staging earns trust only to the degree it's mechanically derived from the same sources as production.
- **Progressive delivery is an observability contract.** Canaries and staged rollouts only work if something *watches*: define the gate metrics (error rate, latency percentiles, and the business signal — orders, sign-ins) and abort thresholds *before* the rollout, automate the halt where possible (see observability: the deploy marker on every dashboard). A canary nobody watches is a rolling deploy with extra steps and false confidence. The flip side: fleet-wide instant flips (big-bang blue-green) trade the gradual-detection window for atomicity — sometimes right (protocol switches that can't mix), never default.

## Workflow

1. **Establish the substrate**: build-once artifacts promoted across environments (see ci-cd); infra as code; config as versioned per-env values; secrets from the manager at runtime (see security). Delete every hand-edited environment difference you find — each is a future 3am mystery.
2. **Choose the strategy per service**: rolling (default: batched replacement with health-checked draining), blue-green (two full stacks, atomic traffic flip — pay double infra for instant cutover/rollback), canary (small real-traffic slice gated on metrics before fleet rollout — the default for user-facing services with enough traffic to read signals).
3. **Define the health gates**: per-rollout metrics, thresholds, soak time per stage; wire automated abort where the platform supports it, and a one-command manual abort regardless.
4. **Make deploys zero-downtime mechanically**: connection draining, readiness vs liveness distinguished (see resilience-engineering: health checks lie in both directions), graceful shutdown handling in-flight work (finish or hand back the queue message — see async-processing), session externalization so instance death is a non-event.
5. **Choreograph schema with code**: expand-migrate-contract as the standing pattern; migrations deploy *separately* from the code that depends on them; long migrations run online (batched backfills, concurrent index builds — see postgres); every step's rollback story written before step one runs.
6. **Wire the flag layer**: kill switches on new risky paths, percentage rollouts for user-facing changes, flags registered with owner and expiry — flag debt is real debt (a hundred stale flags is a state space nobody can reason about — see refactoring: the register with triggers).
7. **Rehearse the reverses**: rollback drill per service on a calendar (deploy previous artifact, verify health, measure time); restore-from-backup drill for the data layer — the two recoveries that only exist if practiced.
8. **Instrument the release itself**: deploy markers on dashboards, version labels on all telemetry (see observability), release annotations in the incident timeline — "what changed" answerable in one query.
9. **Set the cadence policy deliberately**: frequency (higher is safer per-deploy — smaller diffs), freeze windows only where evidence justifies them (freezes batch risk, they don't remove it), and the deploy authority explicit (anyone with green CI? on-call approval? — write it down).
10. **Review deploy incidents as process bugs**: every deploy-caused incident feeds back — a missing gate metric, an untested path, a drift source — the postmortem's fix lands in the deployment spec, not in "be more careful" (see root-cause-analysis; production-debugging).

## Decision Tree

- If the service has real traffic and user-facing changes → canary with metric gates; if traffic is too thin for canary statistics → staged rollout by environment/tenant ring (internal → friendly → all — see the same routing in refactoring's migration cutovers).
- If the change cannot run mixed-version (wire protocol flip, incompatible cluster upgrade) → blue-green with atomic flip, rehearsed against the *drained* state; question first whether an expand-contract intermediate could dissolve the atomicity requirement.
- If the change is risky-but-flaggable → deploy dark, release by flag percentage, watch, ramp — the deploy stops being the risk event at all.
- If a schema change is needed → expand-migrate-contract steps as separate deploys; never "rename column + code change" in one release; never a migration that locks a hot table in traffic hours (see postgres for the mechanics).
- If the rollback answer to any deploy is "we can't" → stop; either build the compensating path (flag off, forward-fix pipeline measured in minutes) or re-slice the change until reversibility returns (see judgment-under-uncertainty: one-way doors get the full apparatus).
- If deploys need announcements, approvals, and heroics → the deploys are too big; increase frequency to shrink each one (see ci-cd: integration frequency and deploy frequency are the same dial).
- If config differs between staging and prod beyond values-in-one-file → that's the incident inventory; converge it into declared config before the next feature ships.
- If a traffic event looms (launch, sale) → pre-scale ahead of it, freeze *risky* releases (not all releases), pre-warm caches (see caching), and rehearse the degradation ladder (see resilience-engineering) — the event plan is a deployment artifact.
- If deploying an on-prem/mobile/app-store artifact → progressive rollout still applies (staged app-store rollout, versioned installers) but rollback becomes *user-paced* — the compatibility window stretches from minutes to months (see api-design: versioning discipline; the mobile note in refactoring's tail).
- If two services must release "together" → they can't, reliably; make one tolerate both versions of the other (compatibility window), then release in sequence — lockstep releases are a coupling smell (see system-design: deployment coupling is coupling).

## Heuristics

- Deploy frequency is a health metric: the team that deploys daily has boring deploys; the team that deploys quarterly has release events with disaster potential — causation runs both ways.
- The previous artifact is part of the current release: keep N-1 (and N-2) deployable at all times; "we'd have to rebuild it" is not a rollback path.
- Migrations are deploys: they go through the pipeline, they're reviewed like code (see code-review), and their locks are load-tested like queries (see postgres).
- Readiness gates traffic, liveness gates restarts — conflate them and a slow dependency triggers a restart storm (see resilience-engineering: the deep-health-check cascade).
- Never deploy at maximum-traffic hour by choice; never *only* deploy at 2am either — 2am-only deploys mean nobody trusts the process, and the fix is the process.
- One change per deploy where risk concentrates: the schema flip doesn't share a release with the feature that uses it.
- Feature flags are code with a lifecycle: created with an owner and an expiry, removed on schedule — the flag check that survives two years is dead code with runtime cost (see refactoring: fossil hunts).
- Config changes are deploys: reviewed, versioned, rolled out progressively, rollback-able — the outage caused by a hand-edited env var is indistinguishable from a bad code deploy except for being invisible in the deploy log.
- Watch the canary's *business* metric, not just its error rate: the checkout canary with clean 200s and zero completed orders is failing loudly in the only metric that matters (see observability; product-thinking).
- Drain before you kill: every deploy interrupts something — the in-flight request, the half-consumed message, the open websocket (see resilience-engineering: reconnect storms are deploy artifacts too).
- Version everything that crosses the deploy boundary: cache entries, session blobs, queue messages, API responses — the N/N+1 pair will disagree about formats exactly once per unversioned format.
- The deploy log is an incident-response tool: timestamped, attributed, diffable — "what shipped in the last 4 hours" answered in seconds (see production-debugging: the first question).

## Quality Checklist

- [ ] Same artifact promoted through all environments; per-env differences are config values in versioned files only.
- [ ] Zero-downtime mechanics verified: draining, graceful shutdown, readiness/liveness split, session externalization.
- [ ] Strategy + gate metrics + abort thresholds written per service; canary/staged rollout for user-facing changes.
- [ ] Rollback: previous artifacts retained, path rehearsed within the quarter, timed.
- [ ] Schema changes follow expand-migrate-contract; every deployed version pair compatible.
- [ ] Flags: registry with owners and expiries; kill switches on new risky paths; stale flags actively removed.
- [ ] Secrets injected at runtime from the manager; nothing baked into artifacts (see security: docker history remembers).
- [ ] Deploy markers and version labels on all telemetry; deploy log queryable.
- [ ] Deploy authority and cadence policy written; freezes evidence-based and rare.
- [ ] Deploy-caused incidents feed structural fixes into the deployment spec.

## Failure Modes

- **The fused deploy-release**: every deploy is a user-visible event, so deploys are rare, so they're huge, so they're dangerous, so they're rarer — the doom loop that flags and frequency break.
- **The unrollbackable release**: code + destructive migration in one shot; the bug appears at 60% rollout and there's nothing to roll back *to* — the schema already moved. Expand-contract existed for exactly this.
- **Mixed-version amnesia**: N+1 writes the new session format, N crashes reading it, the rolling deploy oscillates half the fleet into a crash loop — nobody designed the version pair.
- **Config drift archaeology**: prod has 40 env vars, staging has 34, six were hand-edited during past incidents, none are documented — the next deploy works in staging and dies in prod, on schedule.
- **The unwatched canary**: 5% canary running for an hour, nobody looking, no automated gate — then fleet rollout ships the bug the canary had been demonstrating to an empty room.
- **Flag graveyard**: 200 flags, 12 owners departed, interactions untested — a "cleanup" flips one and takes down checkout; the state space nobody could reason about finally got explored, in production.
- **The heroic deploy**: 19-step runbook, three engineers, a maintenance window, and a prayer — executed monthly, feared always; the process *is* the outage risk.
- **Freeze-thaw whiplash**: a six-week freeze batches sixty changes into the thaw-day mega-deploy — the freeze designed to reduce risk manufactured the riskiest deploy of the year.
- **Staging theater**: staging at 1% of prod's data and none of its traffic patterns blesses everything; the lock that takes 40 minutes on prod's table took 200ms on staging's (see postgres: test migrations against realistic volume).

## Edge Cases

- **Stateful services** (databases, brokers, anything with disks): replacement deploys become orchestrated failovers — replica promotion order, quorum maintenance, rebalance storms; the platform's operator/runbook is the deploy strategy (see system-design; the data layer's failover is its own rehearsed skill).
- **Long-running jobs across deploys**: the 4-hour batch mid-flight when the deploy lands — jobs need checkpointing and resume, or deploy windows that respect them, or graceful handoff (see async-processing: idempotent, resumable is the same requirement).
- **Websockets and sticky sessions**: every deploy disconnects the fleet's clients — jittered reconnect on clients, draining that honors long connections, and capacity for the reconnect wave (see resilience-engineering).
- **Serverless/edge deploys**: versioning and traffic-shifting are platform-native (aliases, weighted routing) but cold starts spike at flip time and "the fleet" is invisible — the canary discipline transfers, the mechanics rename themselves.
- **Client-side rollout** (SPA bundles, mobile apps): the "fleet" is browsers and phones you don't control — cache-busting and long-tail old versions mean weeks-long compatibility windows with your own API (see api-design: the client version histogram is a deployment artifact; frontend-performance for bundle mechanics).
- **Multi-region sequencing**: region-by-region rollout is a free canary ring *and* a consistency question — schema and message compat across regions mid-rollout, plus "which region has which version" as first-class dashboard state (see system-design).
- **Third-party gatekeepers** (app stores, marketplace reviews): release timing is not yours — decouple harder: ship dormant code on *their* schedule, activate by flag on *yours*; emergency fixes need the expedited-review playbook written before the emergency (see the same decoupling logic throughout).
- **Compliance-gated releases**: regulated environments demand approvals and audit trails — build them into the pipeline (automated evidence, approval steps as code) rather than around it (spreadsheets and meetings), or the process rots into ceremony that everyone routes around (see compliance-and-privacy; ci-cd).

## Tradeoffs

- **Canary depth vs release velocity**: longer soaks catch slow-burn issues (memory leaks — see memory-leaks: hours-scale curves) and delay every release; tier by risk — routine changes get minutes-scale gates, schema flips and money-path changes get hours.
- **Blue-green's cost vs cutover cleanliness**: double infrastructure buys atomic flips and instant rollback; for most services, rolling + flags buys 90% of the safety at half the cost — reserve blue-green for the changes that genuinely can't mix.
- **Roll-forward vs rollback culture**: rollback-first is safest when the previous version is knowable-good; roll-forward-only suits continuous deployers with minutes-scale pipelines — the failure is the unchosen middle: slow pipeline *and* unrehearsed rollback.
- **Flag power vs flag debt**: every flag is release safety now and state-space complexity forever; the discipline (owners, expiries, removal cadence) is the price of the power — teams unwilling to pay it should flag less and canary more.
- **Deploy automation vs human judgment**: auto-gates halt rollouts faster than humans and misfire on noisy metrics (the deploy aborted by an unrelated blip); automate the halt, keep the resume human, tune thresholds from history (see observability: alert quality laws apply to gates).
- **Environment fidelity vs cost**: prod-identical staging is expensive and still isn't prod (traffic, data, scale); spend fidelity where it pays — realistic data volume for migration testing (see postgres), traffic replay for risky changes (see refactoring: shadow mode) — and accept that the last risk tranche is only retired by progressive exposure in production itself.

## Optimization Strategies

- Drive deploy size down and frequency up as the standing investment — every other safety mechanism works better on smaller diffs (see ci-cd: the same compounding).
- Template the deployment spec: strategy, gates, thresholds, rollback path as a per-service config file, reviewed like code — new services inherit the discipline by scaffold (see the same move in resilience-engineering's client wrapper).
- Automate the rollback drill: a scheduled job that deploys N-1 to a staging ring and verifies health keeps the path honest without human ceremony.
- Put the version histogram on the wall: which versions are live where (fleet, regions, clients) — mixed-version reality made visible turns compatibility from folklore into a dashboard (see observability).
- Run game days on deploy failure modes: kill a deploy mid-rollout, corrupt a config value, expire a certificate — the deploy system's failure paths need the same fault-injection the runtime gets (see resilience-engineering).
- Track DORA-style metrics honestly (frequency, lead time, change-failure rate, MTTR) as *trend* instruments, not scoreboards — they tell you whether the system is getting safer to change (see optimization-method: measure, then optimize).
- Invest in preview environments per PR (see ci-cd) so "how does this behave deployed" is answered before merge, shrinking what production has to discover.

## Self Review

- If this deploy goes wrong at 60% rollout, what exactly do I do — and when did I last actually do it?
- Can version N and N+1 coexist against the same database, queues, caches, and sessions? What breaks first?
- What's flagged, what's the kill switch, and who flips it at 3am (see production-debugging: mitigation levers)?
- Is anything in this release a one-way door (destructive migration, protocol flip) — and did it get the one-way-door treatment?
- What will I watch during the rollout, what threshold aborts it, and does the business metric have a seat?
- Does staging's blessing mean anything for this change — realistic data volume, mixed versions, real traffic shape?
- What config differs between environments right now, and could I produce the diff in one command?
- Which flags in my area are past expiry, and what's the removal plan?

## Examples

**1. Breaking the fused deploy-release doom loop.**
A team deploys fortnightly: each deploy bundles ~40 changes, needs a release manager, an announcement, and routinely a hotfix day. The intervention sequence: zero-downtime mechanics first (draining, health-check split — the prerequisite), then trunk-based flow with flags on anything user-visible (see ci-cd), then deploys unblocked to daily. Six months later: deploys are 3–5 changes, unannounced, auto-canaried with a 20-minute gate; releases are flag ramps product owns; change-failure rate down 70% — not because engineers got careful, but because small diffs + progressive exposure + rehearsed rollback made carefulness structural. The fortnightly "release event" survives only as a marketing calendar entry, decoupled from any deploy.

**2. The column rename that took five deploys and zero incidents.**
`users.email_verified` (boolean) must become `email_verified_at` (timestamp). The one-shot version — migration + code together — would break mixed-version instances and be unrollbackable. Instead: (1) expand — add nullable `email_verified_at`; (2) dual-write behind the ORM layer, backfill in batches off-peak (see postgres); (3) reads flip to the new column, verified by a reconciliation query; (4) old-column writes stop; (5) contract — drop the boolean, a week later, after the version histogram shows no N-2 stragglers. Each step deploys alone, each is independently rollback-able, and the hot-table lock never exceeds milliseconds. Total calendar: nine days. Total incidents: zero. The pattern goes in the team's playbook as the *only* way schema changes ship (see refactoring: one variable per flip).

**3. The canary gate that paid for itself on a Tuesday.**
A pricing-service change passes all tests and ships to a 5% canary with automated gates: error rate, p99, and — because the deployment spec requires a business metric — quote-to-order conversion. Errors stay clean; latency's fine; conversion on the canary cohort drops 12%. The gate halts the rollout at minute 14 and pages the owner. Root cause: a rounding change displaying prices a cent higher in three currencies — no error, no exception, pure business damage (see the unwatched-canary failure mode; observability: business signals on deploy dashboards). Fixed, redeployed, ramped clean. The incident that didn't happen becomes the team's argument for why every canary gate includes a business metric — and why 95% of users never saw a mispriced quote.

## Evaluation Rubric

Score 1–10:

- **1–2**: Manual, rare, feared deploys; hand-edited environments; no rollback story; migrations and code fused; releases are war-room events.
- **3–4**: Pipeline exists (see ci-cd) but deploys are big and fused to releases; staging drifts; rollback theoretical; flags ad hoc and immortal; canaries absent or unwatched.
- **5–6**: Zero-downtime mechanics in place; config as code; rolling deploys with health gates; expand-contract practiced on risky schema changes; kill switches on new paths; deploy markers on dashboards.
- **7–8**: Full checklist: canary/staged rollouts with automated abort on defined metrics (business included), rehearsed timed rollbacks, version-pair compatibility as a design norm, flag lifecycle enforced, deploy authority and cadence explicit.
- **9–10**: Additionally: deploy specs templated org-wide; rollback drills automated; version histograms and mixed-version state first-class; DORA trends improving and cited in decisions; freezes extinct or evidence-based — and deploys so boring that the release conversation is entirely a product conversation.
