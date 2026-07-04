# Production Debugging & Incident Response

## Purpose

Diagnose live systems under fire: stabilize before root-causing, preserve evidence before it evaporates, read dashboards that lie by averaging, and run incidents so the same fire needs solving once.

## When to use

- An alert fires, error rates spike, latency climbs, or users report outage-shaped symptoms.
- A deploy went out and "something feels off."
- Intermittent production-only failures that staging never shows.
- Post-mitigation: converting "it stopped" into "we know why."
- Designing on-call runbooks and debugging affordances before you need them.

## Goals

- User impact stopped fast (mitigate first), with evidence captured so diagnosis remains possible after mitigation.
- Blast radius quantified early: who, what %, which segments, since when.
- The recent-change hypothesis checked before exotic theories.
- Every incident ends with: timeline, contributing factors, and at least one detection/prevention improvement shipped.

## Inputs

- Telemetry access: metrics (with deploy markers), logs (searchable, correlated by request/trace ID), traces, error tracker.
- Change feeds: deploys, config/flag changes, infra events, dependency/vendor status, cron/batch schedules.
- Mitigation levers and their costs: rollback, feature flags, scaling, traffic shedding, cache flush, failover — each with "how long" and "what breaks."
- Escalation map: who owns which dependency, how to reach them, severity definitions.

## Expert Mental Model

- **Stabilize, then understand.** During user impact, the goal is stopping the bleeding — rollback, flag off, scale up, shed load — not finding the bug. Debugging live fire is for when no safe mitigation exists. The discipline that makes this workable: *capture evidence in the minutes before mitigating* (snapshot dashboards, save log queries, keep one bad pod aside, note timestamps), because rollback often destroys the failing state you'll need at 2 pm.
- **It's almost always a change.** ~80% of incidents trace to something someone changed: deploy, config, feature flag, data migration, dependency version, certificate, quota, or a customer changing *their* usage. The first question is never "what's wrong with the system" but "what changed, and when, versus when the symptom started?" Deploy markers on every graph make this a glance instead of an interrogation.
- **Dashboards lie by aggregation.** An average hides a p99 catastrophe; a global success rate of 99.5% hides one tenant at 100% failure; a healthy mean hides one AZ, one shard, one node melting. The expert move is *segmentation*: break every symptom metric by version, region, tenant, endpoint, node, and device until the failure's shape appears — the shape IS the diagnosis half the time ("only shard B" ≈ "it's shard B's data/config/hardware").
- **Evidence evaporates on a schedule.** Logs rotate, metrics downsample (your 10-second resolution becomes 5-minute averages by tomorrow), pods restart, caches cycle, auto-scaling replaces the sick node. Time-sensitive capture is a first-class incident task, assigned to a person, not an afterthought.
- **Cascades hide their first domino.** By the time you look, six alarms are red: OOM kills, timeouts, queue backups, circuit breakers open. The skill is walking backward to the *earliest anomaly* — the 09:01 connection-pool warning that preceded the 09:14 avalanche — because everything after it is physics, not cause (see root-cause-analysis).
- **The system under incident is a crime scene AND a patient.** Every diagnostic action must be triaged for safety: read-only queries with LIMIT and timeouts, EXPLAIN before executing, no "quick fixes" typed into prod shells under adrenaline. A signal that pattern-matches a known failure may have a different cause this time — check that the evidence supports the *specific* action before restarting/deleting/failing-over.

## Workflow

1. **Acknowledge and frame (first 2 minutes)**: what's the user-visible symptom? Since when (exact time)? Declare severity by impact, not by fear. Open the incident channel; one person coordinates, others investigate — roles beat heroics.
2. **Quantify blast radius**: error rate, affected endpoints, % of users/requests, segments (region, tenant, platform, version). This drives severity, comms, and — via the failure's shape — the diagnosis.
3. **Sweep the change feed**: deploys/configs/flags/migrations/vendor status in the window [symptom onset − 60 min, onset]. A candidate change → prepare its reversal immediately (even before proof, have the rollback staged).
4. **Capture evaporating evidence (assign it)**: screenshot/pin dashboards at incident resolution, save raw log queries + samples, `kubectl describe`/thread-dump/heap-snapshot one sick instance and cordon it (keep it out of the LB, alive for autopsy), note all timestamps in UTC.
5. **Mitigate by the cheapest safe lever**: matching change found → roll it back / flag it off. No change found → symptomatic relief: scale (if saturation), restart (if leak/state corruption — after capturing!), shed/queue traffic, fail over, serve degraded (cached/stale) — see Decision Tree.
6. **Verify mitigation with the same metric that defined impact** — watch it recover to baseline, not to "seems better." Announce recovery with the graph.
7. **Then diagnose properly** (calm-mode): correlate the earliest anomaly across logs/metrics/traces; segment until the shape is sharp; trace one failing request end-to-end by ID; hand to root-cause-analysis for repro/bisection.
8. **Confirm the mechanism** with a discriminating test — staging repro, controlled canary re-enable, or the cordoned pod's autopsy — before writing "root cause" in the doc.
9. **Run the blameless postmortem**: timestamped timeline (detection → diagnosis → mitigation → recovery), user impact quantified, trigger vs root cause vs contributing factors (plural — there are always several), and action items each with an owner and a due date. The two mandatory action items: *detect it faster* (what alert/SLO would have caught it in 1 minute?) and *prevent the class* (guardrail, not vigilance).
10. **Close the loop**: verify action items actually shipped (the postmortem graveyard is where reliability goes to die); add the incident's signature to the runbook ("if you see X + Y, check Z first").

## Decision Tree

- If a recent change matches the timeline → roll it back / flag it off *now*; confirm afterward. (Rollback safety check: does it involve schema/data migrations? Then forward-fix or restore path — see ci-cd expand/contract.)
- Else if saturation signals (CPU, memory, connections, queue depth at limits) →
  - Sudden traffic jump: legitimate (launch, press) → scale out + raise limits; illegitimate (bot, retry storm, one client looping) → rate-limit/block the offender (top-talkers by IP/token/tenant).
  - Flat traffic but rising resource use → leak or degradation (see memory-leaks); capture then restart as mitigation; schedule diagnosis.
- Else if one dependency is slow/erroring (DB, cache, third party) →
  - Verify with *its* metrics, not just your timeouts (your symptom might be your own connection pool).
  - Mitigate: open circuit breakers / serve degraded / fail over replica / call vendor with evidence (request IDs, timestamps).
- Else if errors localize to one segment (one node, AZ, shard, tenant, version) → remove/drain the sick member (cordon a node, shift the shard, pin the version) — segmentation already found your fault domain.
- Else if "everything is slow" with no saturation → suspect the hidden shared thing: DNS, service mesh, TLS/cert (check expiry dates!), clock skew, a logging/tracing backend backpressuring the apps, or a lock in a shared datastore.
- If no lever is safe and impact continues → degrade deliberately: disable expensive features (flags), serve stale caches, static fallback pages, queue writes — partial service beats none, and buys diagnosis time.
- If the symptom pattern-matches last month's incident → treat as hypothesis, not conclusion: verify this instance's evidence supports the same action before repeating the fix (same alarm, different arsonist is common).

## Heuristics

- Onset time is gold — pin it to the minute from the metric, then hunt ±60 min in the change feed. "Gradual since last Tuesday" vs "cliff at 14:02" already split the hypothesis space (degradation/leak vs change/trigger).
- p50 fine + p99 exploding = a subset is suffering: contention, one slow shard, GC pauses, or a single bad node behind the LB. Averages will tell you everything is fine while a tenth of users churn.
- Error *rate* must be read against *traffic*: 500s doubled but traffic tripled = improvement; success-count flat while traffic drops = your users gave up (the silent outage).
- Check cert expiries and quota limits early on "nothing changed" incidents — the calendar is a change agent nobody announces (certs, quotas, license expiries, first-of-month data volumes, DST).
- Retry storms turn a blip into an outage: if traffic spiked *after* errors began, your clients' retries are the load — mitigation includes backing them off (jitter, Retry-After), not just scaling to absorb.
- One request end-to-end beats ten aggregate graphs: pick a failing request ID and walk it through every hop's logs/trace — the hop where it dies or stalls is the neighborhood of truth.
- The node you restart is evidence you incinerate: always capture (or cordon one) first if the fleet has more than one sick member.
- Read-only prod discipline: SELECTs with LIMIT and statement_timeout, EXPLAIN before any heavy query, no ad-hoc writes without a second pair of eyes — the incident you cause during an incident is the one they write case studies about.
- If the fix is "turn it off and on again," write down *what state was corrupted* as a mandatory follow-up — restarts fix symptoms by amnesia.
- Communicate on a cadence (every 15–30 min even if "still investigating") — silence during incidents costs more trust than the outage.
- Two competing theories? Prefer the probe that discriminates between them over the probe that confirms your favorite.

## Quality Checklist

- [ ] Severity declared from quantified user impact; roles assigned (coordinator ≠ investigator).
- [ ] Onset pinned to the minute; change feed swept for the prior hour; deploy markers visible on graphs.
- [ ] Blast radius segmented (version/region/tenant/endpoint/node) before deep-diving.
- [ ] Evidence captured pre-mitigation: pinned dashboards, saved queries, one cordoned instance where applicable.
- [ ] Mitigation chosen from the lever table with its cost acknowledged; recovery verified on the impact metric.
- [ ] Earliest anomaly identified; cascade effects labeled as effects.
- [ ] Mechanism confirmed by a discriminating test before "root cause" is written.
- [ ] Postmortem: UTC timeline, impact numbers, trigger/root/contributing separated, blameless language.
- [ ] Action items include one faster-detection and one class-prevention, owned and dated.
- [ ] Runbook updated with this incident's signature.

## Failure Modes

- **Debugging while users burn**: 45 minutes of fascinating investigation with a rollback available at minute 2. The mitigation-first reflex wasn't installed.
- **Mitigating away the evidence**: fleet-wide restart cures it; nothing was captured; the leak returns in 26 hours and you're at zero again.
- **Average-gazing**: global dashboards green while a whale tenant is 100% down; discovered via angry email, not telemetry. Segmentation was one groupby away.
- **Recent-change blindness**: three hours of exotic theories before someone asks "wait, what shipped at 13:58?" — the change feed wasn't the first stop.
- **Pattern-match misfire**: "this looks like the March cache incident" → cache flushed → made it worse (this time it was the DB failover). The evidence check before action was skipped.
- **Retry-storm misread**: scaling up to absorb "traffic growth" that is actually your own clients hammering retries into a down dependency — feeding the fire.
- **Hero soloing**: one engineer holds everything in their head, no channel updates, no notes; they hit their knowledge limit at hour two and handoff is impossible.
- **Postmortem theater**: doc written, actions unowned, nothing ships; the same incident re-runs quarterly with new participants and identical shape.
- **The prod-shell casualty**: an "obvious quick fix" UPDATE without WHERE, mid-incident. Now there are two incidents.

## Edge Cases

- **Gray failures**: the health check passes while real requests fail (health endpoint doesn't exercise the broken path) — LB keeps routing to a sick node. Fix class: health checks that touch real dependencies shallowly.
- **Metastable failures**: system stays down even after the trigger clears (cold caches → DB overload → timeouts → retries → overload). Recovery needs *stepped* reintroduction: warm caches, throttle inbound, raise limits temporarily — not just "trigger removed, why isn't it better?"
- **The observer down**: your logging/metrics pipeline is the thing broken — you're blind, not down (or both: telemetry backpressure crashing apps). Keep an out-of-band health probe and know your blind-flying runbook.
- **Multi-tenant noisy neighbor**: one tenant's pathological query/usage degrades everyone — segmentation by tenant finds it; mitigation is per-tenant limits, not global scaling.
- **Timezone/DST incidents**: cron avalanches at DST shifts, "daily" jobs running twice/zero times; UTC discipline in the timeline or you'll misorder cause and effect by an hour.
- **Slow-burn incidents**: error rate creeping 0.1%→0.9% over three weeks — no alert fired (thresholds), no change correlates (it was data growth). Trend alerts and weekly SLO reviews catch what threshold alerts can't.
- **Vendor incidents**: your dashboards say "dependency slow," their status page says green (status pages lag). Evidence package (request IDs, timestamps, rates) + escalation path beats waiting; design your degraded mode for their outage *before* it happens.
- **The deploy that can't roll back**: migration already ran, old code can't read new data — this is why expand/contract exists (ci-cd); mid-incident, the answer is roll *forward* with a minimal fix, which is why fast pipelines are an incident tool.

## Tradeoffs

- **Mitigate fast vs diagnose deep**: rollback in minute 2 may leave the cause unknown (it "went away") — accept it: capture evidence, then schedule the calm investigation with the canary re-enable. User-minutes outrank engineer curiosity.
- **Rollback vs roll forward**: rollback is rehearsed and fast but loses everything else in the release and can't cross data migrations; forward-fix is precise but you're compiling under fire. Default rollback; forward only when rollback is unsafe or the fix is truly one line — with a second reviewer even at 3 a.m.
- **Restart now vs autopsy first**: every minute of capture is a minute of impact. Fleet sick → capture one, restart the rest. Singleton sick → capture aggressively; that instance is your only witness.
- **Alert sensitivity vs fatigue**: catching slow-burns wants tight thresholds; on-call sanity wants quiet nights. Resolve with SLO burn-rate alerts (fast-burn pages, slow-burn tickets) instead of static thresholds on everything (see observability).
- **Freeze vs flow after incidents**: change freezes feel safe and rot into risk (bigger batches, staler branches). Prefer smaller changes with better gates over freezes; reserve freezes for genuinely fragile windows.

## Optimization Strategies

- Pre-build the segmentation dashboard: one screen that breaks the golden signals by version/region/tenant/node — the first 10 minutes of every incident, automated.
- Deploy markers + change-feed aggregation (deploys, flags, configs, crons in one queryable stream) — turns "what changed?" from archaeology into a filter.
- Rehearse the levers: game-day the rollback, the flag-off, the failover, the shed. A lever you've never pulled has unknown cost — measured during a drill, not an outage.
- Keep golden queries in the runbook: top-talkers, slowest endpoints, error-by-segment, "one request end-to-end" — copy-paste-ready, because incident-you types worse than calm-you.
- Cordon-and-capture automation: one command that pulls a node from rotation, snapshots its state (threads, heap, tcpdump window), and labels it for autopsy.
- Track MTTD/MTTM (time to detect / to mitigate) per incident and aim improvements at the larger one — most teams need detection more than they need smarter debugging.
- Feed every incident's signature into alerting: the goal is that no incident class pages you twice without a purpose-built detector existing.

## Self Review

- Could I have mitigated sooner than I did? What was I doing instead?
- What evidence did I capture before the state was destroyed — and what do I wish I had?
- Did I check the change feed before theorizing? Did I segment before averaging?
- What was the *earliest* anomaly, and is everything else in my story downstream of it?
- Is the mechanism confirmed by a test, or does the timeline merely fit?
- Does the postmortem name contributing factors (plural) without blaming a person?
- What now detects this in one minute? What makes this class impossible? Who owns those, by when?
- If I handed this incident doc to a stranger, could they run the recurrence?

## Examples

**1. The textbook change-rollback with evidence discipline.**
14:07 pager: checkout error rate 4%→22%. Coordinator declared SEV2, split roles. Segmentation: all regions, only `POST /payment`, only app version 2214. Change feed: 13:58 deploy touching the payment client. Evidence capture (2 min): pinned error dashboard, saved a failing request trace, kept one pod cordoned. 14:13 rollback; 14:16 metric back to baseline — announced with graph. Calm-mode diagnosis on the cordoned pod: new SDK defaulted a 2 s timeout (was 10 s); p95 to the payment gateway is 2.3 s. Root: unvalidated default change; contributing: no canary on payment paths, gateway p95 SLO absent. Actions shipped: canary stage for payment services (prevention), gateway-latency SLO alert (detection). Total user impact: 9 minutes.

**2. Averages hiding a whale.**
Support escalation: "Acme says the app is down"; dashboards green (99.6% success). Segment success rate by tenant: Acme at 0%, everyone else fine. Their traffic: every request 403. Change feed: a permissions migration at 09:00 backfilled a new column — for all tenants except those with legacy SSO config (null handling). Mitigation: targeted data fix for the three affected tenants (verified read-only first, then a reviewed UPDATE with WHERE and row-count check). Prevention: migration checklist gains "verify against legacy-config fixtures"; detection: per-tenant success-rate alerting for the top 50 accounts. The postmortem's sharpest line: the global dashboard was working exactly as designed — that was the problem.

**3. Metastable recovery: the outage that outlived its cause.**
Cache cluster rebooted (vendor maintenance, announced, missed). DB immediately saturated by cold-cache misses; latency → timeouts → client retries → more load; cache refilled too slowly under the storm. Trigger long gone, system still down 40 minutes later. Recovery sequence that worked: enable request shedding at 50% (stop the retry storm), raise DB connection limits temporarily, warm the top-1000 cache keys from a script (the hot-key list existed from caching design), then step shedding down 50→25→0 over 15 min, watching DB headroom. Postmortem actions: stampede protection on the hot keys (single-flight — see caching), retry budgets with jitter in the clients (see async-processing), and a "cold cache" game-day. The lesson institutionalized: removing the trigger doesn't recover a metastable system; you must break the loop.

**4. The slow burn nobody paged.**
Quarterly SLO review (not an alert) notices checkout p99 degraded 800 ms → 2.1 s over six weeks. No change correlates. Segmentation: latency grows with account age — oldest accounts slowest. One slow request traced end-to-end: 1.8 s in a single query; EXPLAIN ANALYZE (read-only, calm) shows a sequential scan — a table grew past the planner's tipping point as data accumulated (stats stale, index partial). The "change" was data volume; the calendar and growth are change agents too. Fix per postgres skill (extended stats + index); detection gap closed with trend-based SLO burn alerts — threshold alerts can't see a six-week ramp, and this incident had zero minutes of "outage" while quietly costing conversions.

## Evaluation Rubric

Score 1–10:

- **1–2**: Investigation before mitigation with users burning; no impact quantification; restart-and-pray; evidence destroyed; no writeup.
- **3–4**: Mitigation eventually chosen but slow; change feed consulted late; averages read at face value; postmortem written but actionless.
- **5–6**: Mitigate-first executed; blast radius segmented; change-correlation checked early; evidence partially captured; postmortem with owned actions.
- **7–8**: Full checklist: roles, evidence capture assigned, discriminating confirmation of mechanism, trigger/root/contributing separated, detection+prevention actions shipped, runbook updated.
- **9–10**: Additionally: rehearsed levers with known costs; segmentation dashboard and golden queries pre-built; metastable/gray-failure literacy visible in the response; MTTD/MTTM tracked and improving; no incident class has paged twice without a purpose-built detector in between.
