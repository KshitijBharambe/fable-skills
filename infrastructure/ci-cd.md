# CI/CD & Deployment

## Purpose

Build pipelines and deployment practices where shipping is boring: fast trustworthy CI, build-once artifacts, progressive delivery with auto-rollback, migration discipline, and rollbacks rehearsed enough to be a non-event.

## When to use

- Setting up or overhauling a build/test/deploy pipeline.
- Deploys are scary, rare, manual, or bundled ("release trains" out of fear).
- CI is slow (>10–15 min) or flaky enough that reruns are ritual.
- A deploy caused an outage and rollback wasn't clean (often: a migration).
- Designing branch strategy, environments, or release gating.

## Goals

- Trunk stays releasable; a merged PR can reach production the same day without heroics.
- CI verdict in ≤10 minutes for the common path; flakes quarantined, not rerun-until-green.
- One artifact built once, promoted through environments unchanged.
- Rollback ≤5 minutes, rehearsed, and safe across schema changes (expand/contract discipline).
- Deploy ≠ release: feature flags decouple code arrival from user exposure.

## Inputs

- Current pain map: cycle time (merge→prod), deploy frequency, change-failure rate, MTTR — the four DORA-style numbers, even roughly.
- Test suite reality: duration, flake rate, coverage of the deploy-blocking paths.
- Runtime topology: how many services, environments, regions; stateful components and their migration mechanics.
- Compliance constraints: approvals, audit trails, segregation-of-duties (design them in, don't bolt on).

## Expert Mental Model

- **Pipeline speed is a feature with compounding interest.** Past ~10 minutes, developers batch changes, context-switch away, and stop running CI pre-merge; batching makes each deploy bigger and riskier, which makes people deploy less, which makes deploys bigger. The death spiral runs on minutes. Experts treat CI latency like p99 latency: measured, budgeted, defended.
- **Small changes are the safety mechanism.** Deploy risk scales superlinearly with diff size (more interactions, harder review, harder bisection, harder rollback attribution). Everything in delivery discipline — trunk-based flow, flags, fast pipelines — exists to make *small and frequent* the path of least resistance. A team deploying 20× a day with 200-line changes is safer than one deploying monthly with 20k lines, and the incident data (change-failure rate vs deploy frequency) backs it.
- **Build once, promote the artifact.** Rebuilding per environment means staging tested one binary and production runs another (different dependency resolution, different flags, different timestamp). The artifact (image/tarball) is immutable, versioned, signed; environments differ only by *config injected at deploy*. "Works in staging" is only evidence if staging ran the same bytes.
- **Deploy ≠ release.** Deploying is moving code to servers; releasing is exposing users to behavior. Feature flags separate them: ship dark, enable gradually, kill instantly without a deploy (see production-debugging mitigation levers). This one distinction removes most deploy fear — the deploy stops being the moment of truth.
- **Flaky tests are pipeline poison, not weather.** A suite that fails 5% of the time randomly teaches everyone that red means "rerun," and then real reds get rerun too — the pipeline's entire epistemic value evaporates. The discipline: flake detected → quarantined same day (removed from blocking, ticketed with owner) → fixed or deleted within the sprint. Rerun-until-green as culture is CI theater.
- **Migrations are deploys' hardest problem** because code rolls back in seconds and data doesn't. Expand/contract (see postgres, legacy-migrations): every schema change ships in a backward-compatible expansion (new code and old code both work), then the contraction ships *separately* after old code is gone. The invariant: at every moment, the running code set works against the current schema — which is exactly what makes rollback safe.
- **Rollback is a product you build, not a hope you keep.** It has requirements (artifact registry retention, config versioning, migration compatibility window, one-command execution), a latency SLO (≤5 min), and a test schedule (rehearse it — an unrehearsed rollback is a second incident waiting inside the first; see production-debugging).

## Workflow

1. **Measure the four numbers** (cycle time, deploy frequency, change-failure rate, MTTR) — crude is fine; they rank everything below and prove the improvements later.
2. **Stabilize trunk flow**: short-lived branches (≤1–2 days) merged to trunk behind CI; kill long-lived env branches (`dev`→`staging`→`prod` branch promotion is where merge conflicts and "what's even deployed?" live). Big features → flags, not branches.
3. **Structure CI fail-fast**: static/lint+typecheck (seconds) → unit (minutes, parallelized) → build artifact → integration/API tests against the artifact → deploy to preview/staging → smoke + e2e (small, critical-path only). Push heavy suites (full e2e matrix, load, security scans) to post-merge/nightly with alerting, keeping the PR gate ≤10 min.
4. **Make the artifact the contract**: reproducible-ish build, content-addressed tag (commit SHA), pushed once to a registry; deployment = "point environment at artifact + inject config/secrets" (config in env/secret manager, never baked in — see secrets skill).
5. **Install the flag system before you need it**: kill-switch-grade flags for risky paths, percentage rollouts, per-tenant targeting; flag hygiene (owner + expiry per flag; a quarterly flag-cleanup ritual — stale flags are config-space debt that multiplies test surface).
6. **Choose the deploy strategy per service** (see Decision Tree) and wire *automated* post-deploy verification: smoke tests + a metrics watch window (error rate, p99, key business metric vs baseline) with auto-halt/rollback on breach — the canary that "someone watches dashboards" is not a canary.
7. **Codify migration discipline**: migrations run as their own pipeline step (before code deploy), always expand-phase compatible with the previous release; `lock_timeout` and batched backfills enforced by review checklist (see postgres); contraction migrations require proof (telemetry) that no old readers/writers remain.
8. **Build the rollback product**: one command/button → previous artifact + its config; registry retains N versions; DB compatibility window documented (roll back ≤K releases safely); rehearse quarterly in staging *and* once in production on a calm day.
9. **Quarantine machinery for flakes**: detection (track pass-rate per test), one-click quarantine (skip+ticket), a visible flake budget (quarantined count trending down or the team stops and fixes).
10. **Secure the pipeline itself**: OIDC federation to cloud (no long-lived deploy keys in CI — see secrets-and-supply-chain), pinned actions/images, least-privilege deploy roles, artifact signing/provenance where the org warrants it; the pipeline is production-grade infrastructure with prod-grade access — treat its compromise as a top-tier threat.

## Decision Tree

- Deploy strategy per service:
  - Stateless, ≥2 replicas → rolling deploy with health-gated batches (default).
  - User-facing, high blast radius → canary: 1–5% traffic, automated metric comparison vs baseline for 10–30 min, then progressive (25→50→100) with auto-rollback on SLO breach (see observability for the SLOs).
  - Need instant atomic cutover/rollback and can afford 2× capacity briefly → blue/green.
  - Stateful/singleton (DBs, schedulers) → maintenance-window or leader-handoff choreography; don't pretend rolling works for singletons.
- If a change involves schema:
  - Additive (new nullable column, new table, new index CONCURRENTLY) → migrate-then-deploy, same release.
  - Behavioral (rename,型 type change, NOT NULL, drop) → expand/contract across ≥2 releases: expand + dual-write/read → backfill → verify → cut over → contract later (see legacy-migrations for the full ladder).
  - If someone proposes a migration that old code can't survive → that's a rollback-blocker; split it or accept (in writing) that this deploy is one-way.
- If CI exceeds the 10-min budget → in order: parallelize (shard tests), cache (deps, build layers), split PR-blocking vs post-merge suites, delete low-value slow tests (a 40-min suite nobody trusts is worth less than a 8-min one everyone does).
- If a test flakes → quarantine now, fix or delete this sprint. Never: retry-annotation as the permanent fix.
- If deploys need human approval (compliance) → put the approval on *release* (flag/promotion), keep *deploy* automated; audit trails from the pipeline, not from screenshots.
- If you're on release trains out of fear → fix the fear (flags, canary, rollback) and dissolve the train; scheduled releases are legitimate only for coordinated marketing/platform events, not as a risk blanket.

## Heuristics

- Merge→prod under an hour is a healthy reflex arc; under a day is acceptable; over a week means your "continuous" is decorative.
- The PR gate tests what the *deploy* risks, not everything you know how to test: unit+contract+smoke gate; the exhaustive matrix runs post-merge (and pages on failure).
- Preview environments per PR (ephemeral, seeded) kill the staging-contention queue and catch integration issues pre-merge — worth the infra for any team >5.
- Staging drifts unless refreshed: scheduled data refresh (scrubbed — see secrets/PII) and config parity checks; a staging that differs from prod in load balancer, data shape, and versions "passes" nothing (see root-cause-analysis environment-diff bugs).
- Deploy on Mondays-through-Thursdays mornings by *default availability* not superstition: deploy when the team is present to respond; "no Friday deploys" as dogma usually means rollback isn't trusted — fix that instead.
- Every deploy visible: marker on dashboards (see observability), notification in the team channel with diff link and deployer; "what changed?" should never require forensics (see production-debugging change feeds).
- Version everything that shapes behavior: app artifact, config, flags state, infra (IaC), migrations — an environment is a tuple, and rollback restores the tuple, not just the binary.
- Pipelines are code: reviewed, versioned, DRY-ed with shared templates; ten hand-edited YAML copies across services is how one fixed vulnerability stays unfixed in nine.
- Cache aggressively, verify honestly: dependency and layer caches make speed; a cache-poisoning path (unpinned mutable tags) makes incidents — pin by digest.
- The smoke test is 5–10 requests hitting the deployed instance's real critical paths (login, core read, core write against real dependencies) in <60 s — it exists to catch "deployed but dead," the most embarrassing outage class.
- Track flake-rate and pipeline-duration on the team dashboard next to error rates — the delivery system is a system; give it the observability you give production (see observability).

## Quality Checklist

- [ ] Four delivery metrics known and trending (cycle time, frequency, change-failure, MTTR).
- [ ] PR gate ≤10 min; stage order fail-fast; heavy suites post-merge with paging.
- [ ] One artifact, content-addressed, promoted unchanged; config/secrets injected, never baked.
- [ ] Flags provide kill-switch + progressive rollout; flag inventory has owners/expiries and a cleanup cadence.
- [ ] Post-deploy verification automated (smoke + metric watch window + auto-halt/rollback).
- [ ] Migrations: expand/contract enforced; every deploy's rollback-compatibility stated; lock-safety reviewed (see postgres).
- [ ] Rollback: one command, ≤5 min, registry retention set, rehearsed within the last quarter.
- [ ] Flake quarantine machinery live; quarantine count visible and bounded.
- [ ] Pipeline security: OIDC (no static cloud keys), pinned dependencies/actions, least-privilege deploy roles.
- [ ] Deploy markers + notifications wired to dashboards and the incident change-feed.

## Failure Modes

- **The 45-minute flaky gate**: devs batch commits, rerun ritual, "merge and see" culture — the pipeline exists but its verdicts mean nothing; delivery decays while CI dashboards stay green-ish.
- **Rebuild-per-environment**: staging validated build #482, prod ran a fresh build with a floated dependency — the "tested" change fails in prod with a bug staging can't reproduce (see root-cause-analysis: verify what's actually executing).
- **The one-way deploy**: migration dropped a column in the same release that stopped using it; deploy bad → rollback impossible (old code SELECTs the dropped column) → forward-fix under fire at 2 a.m. (see production-debugging rollback-blocked).
- **Release-train risk bundling**: three weeks of changes ship at once; something breaks; bisection is a 40-commit haystack; the postmortem's action item — "test more" — makes the train slower and the batches bigger.
- **Flag graveyard**: 300 flags, 260 stale, some load-bearing in unknown ways; a "cleanup" flips one and takes checkout down. Flags without owners/expiry are config landmines.
- **Canary theater**: 5% canary "watched" by a human who's in a meeting; metrics breach for 20 minutes before anyone looks. Unautomated verification is a wish.
- **Snowflake staging**: hand-edited config, ancient data, missing services — green in staging predicts nothing; teams learn to skip it, then it exists only as cost.
- **CI as security hole**: long-lived AWS keys in CI secrets, unpinned third-party actions — the pipeline has prod access and weaker security than any prod service; attackers know this ordering (see secrets-and-supply-chain).
- **Deploy amnesia during incidents**: "did anything ship?" takes 20 minutes to answer because deploys aren't marked anywhere (see production-debugging: the change feed is the first stop).

## Edge Cases

- **Long-running jobs vs rolling deploys**: workers mid-task SIGKILLed by the rollout — graceful drain with deadline, checkpointable jobs, and deploy strategies that respect in-flight work (see async-processing graceful shutdown).
- **Config-only changes**: config is a deploy (it changes behavior) — version it, roll it out progressively, mark it on dashboards; "just a config change" precedes a notable fraction of incidents (see production-debugging change sweep).
- **Mobile/desktop clients**: no rollback of shipped binaries — server-driven flags, forced-upgrade machinery, and API versioning discipline (see api-design) carry the weight; server deploys must tolerate a long tail of old clients.
- **Monorepo selective CI**: path-based test selection speeds everything and silently skips affected-but-unmapped tests — invest in dependency-graph-based selection and a periodic full run to catch drift.
- **Shared-infra migrations** (message schemas, cache formats): expand/contract applies beyond SQL — consumers tolerate both formats before producers switch (see event-driven schema evolution).
- **Semantic version + package publishing**: libraries have "deploys" too (publish); the pipeline needs: changelog discipline, semver honesty (breaking = major), and yank/deprecate procedures — a broken patch release is an outage distributed to every consumer.
- **Multi-region rollouts**: region-by-region progression with bake time; config/flag state must be region-scoped or a "global kill switch" kills globally when one region needed it.
- **Compliance environments**: approvals and audit requirements are pipeline features (protected environments, signed approvals, immutable logs) — bolted-on manual gates outside the pipeline create the shadow process that fails the audit anyway.

## Tradeoffs

- **Gate coverage vs speed**: every test in the PR gate buys risk-reduction and costs every developer minutes forever. Price tests by (defect-catch rate × blast radius) ÷ runtime; move or delete the losers. A slightly riskier fast gate + strong post-deploy verification usually beats an exhaustive slow gate — production verification catches what staging fundamentally can't.
- **Canary depth vs velocity**: 30-minute bakes per stage × 4 stages = 2-hour deploys; fine for high-blast services, absurd for an internal tool. Tier services by blast radius; give each tier a strategy (see system-design nines-by-flow logic).
- **Blue/green cost vs rollback speed**: 2× capacity during deploys buys instant cutover; rolling is cheap and gradual. Pay for blue/green where seconds-to-rollback matter (payments edge), roll elsewhere.
- **Flag power vs flag debt**: every flag is a conditional multiplying test surface and a stale-config risk; the discipline (owner, expiry, cleanup ritual) is the price of the kill-switch capability — teams that won't pay it should use fewer, coarser flags.
- **Standardized pipelines vs team autonomy**: golden-path templates make security/speed improvements land everywhere at once, at the cost of special-case friction; the platform-team pattern (paved road + escape hatch with ownership) resolves most of it (see observability golden middleware — same shape).
- **Ephemeral envs vs cost**: preview-per-PR costs real infra money and saves integration surprises + staging queues; scope them (spin down aggressively, seed minimally) rather than debating them binary.

## Optimization Strategies

- Attack pipeline latency like a perf problem (see optimization-method): profile stages, fix the biggest bar (usually: unparallelized tests, then uncached dependencies, then container build layers), re-measure, repeat until ≤10 min.
- Test-impact analysis: run first the tests most likely to fail for this diff (path-based or history-based) — median time-to-red drops even when total time doesn't.
- Bake auto-rollback into the metric watch: deploys that breach the window revert without human decision (humans confirm after) — MTTR for bad deploys drops to the bake time.
- Deployment frequency itself is a lever: consciously push it up (smaller PRs, flag-gated merges) and watch change-failure rate — teams discover the safety was in the smallness all along.
- Run a quarterly "delivery retro" on the four metrics + flake count + rollback rehearsal result — the delivery system gets the same continuous improvement loop as the product.
- Template the golden pipeline (build→test→scan→deploy→verify) as versioned shared config; upgrading the template upgrades every service — one security fix, org-wide, in a day (see secrets-and-supply-chain pinning).

## Self Review

- What are my four numbers this quarter vs last? Which one is the constraint now?
- Can I trace any production incident to "what changed" in under two minutes from deploy markers?
- Is the artifact in prod byte-identical to what CI tested? How would I prove it?
- For the last schema change: could we have rolled back mid-deploy? Was that stated in the PR?
- When did we last *execute* a rollback (drill or real)? How long did it take?
- How many tests are quarantined right now, and is the count shrinking?
- What in the PR gate hasn't caught a defect in six months, and what does it cost per day?
- If CI's secrets leaked today, what could the attacker deploy, and to where?

## Examples

**1. The 45→8 minute gate rescue.**
Symptoms: 45-min PR gate, 7% flake rate, rerun culture, merge batching. Sequence: (1) test profiling — one e2e suite = 28 min → moved post-merge with paging, PR gate keeps 6 critical-path e2e (4 min); (2) unit tests sharded 4-way (12→4 min); (3) dependency + Docker layer caching (6→2 min); (4) flake quarantine machinery: pass-rate tracking flags 23 tests, quarantined with tickets, 19 fixed / 4 deleted in two sprints. Gate: 8 min, flake <0.5%. Second-order effects (the real prize): median PR size drops 40% within a month, deploys go 2/week → 6/day, change-failure rate *halves* — smallness was the safety.

**2. Expand/contract in anger: renaming a column on a hot table.**
Goal: `users.fullname` → `display_name` on 40M rows, zero downtime, rollback-safe throughout. Release 1 (expand): add `display_name` nullable; deploy code writing both, reading `display_name ?? fullname`; batched backfill (10k rows, lock-safe — see postgres) with progress marker. Release 2: reads/writes on `display_name` only, telemetry counter confirms zero `fullname` reads for 7 days. Release 3 (contract): drop the old column. Every release rolls back cleanly against the schema it runs on; the PR template's "rollback compatibility" line is filled honestly at each step. Time cost: three small releases over two weeks. The alternative — one clever release — was a one-way deploy with a 40M-row hostage.

**3. Canary with automated judgment.**
Payments-adjacent service, tiered as high-blast. Deploy: 5% canary for 15 min; the pipeline (not a human) compares canary vs baseline on error rate, p99, and payment-success business metric with statistical thresholds; breach → auto-rollback + page with the diff link. Third week of operation: a dependency bump ships a subtle serialization bug — 5% canary error rate rises 0.4% (below any human-noticeable dashboard wiggle), automation halts and reverts at minute 9; total user impact: 5% of traffic × 9 min × 0.4%. The postmortem is one paragraph; the system was the responder (see production-debugging: the best incident is the one automation ended).

**4. Deploy≠release unlocking a scary launch.**
A pricing-engine rewrite — the kind of change that used to justify a release train and a war room. Instead: code merges to trunk continuously behind `pricing_v2` (dark, months); shadow mode runs v2 alongside v1 comparing outputs on real traffic (see legacy-migrations shadow pattern), discrepancy dashboard drives fixes; release = flag rollout 1% → internal tenants → 10% → 100% over two weeks, kill-switch tested beforehand; deploys during this period: dozens, boring. The launch moment users noticed: a flag flip at 10 a.m. on a Tuesday, reverted-capable in seconds. War room attendance: zero.

## Evaluation Rubric

Score 1–10:

- **1–2**: Manual deploys from laptops; env-branch promotion; rebuilds per env; no rollback story; migrations YOLO; CI slow, flaky, and ignored.
- **3–4**: Pipeline exists; artifact discipline partial; deploys weekly-ish and feared; flags ad-hoc; rollback theoretical; flakes rerun.
- **5–6**: Trunk-based flow; ≤15-min gate; build-once promotion; expand/contract on schema changes; smoke tests post-deploy; rollback documented and occasionally exercised.
- **7–8**: Full checklist: ≤10-min gate with quarantine machinery, automated canary/watch-window verification, flag hygiene, rehearsed ≤5-min rollback, pipeline security (OIDC, pinning), four metrics tracked.
- **9–10**: Additionally: auto-rollback on metric breach; preview environments; golden pipeline templates org-wide; delivery retro cadence with improving DORA-class numbers; deploys frequent enough to be uninteresting — the culture artifact that proves the system.
