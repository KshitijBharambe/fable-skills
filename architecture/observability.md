# Observability

## Purpose

Instrument systems so 3 a.m. questions — is it up, is it slow, who's affected, what changed — get answered in minutes: structured logs, RED/USE metrics, traces, SLOs, and alerts that page on user pain instead of CPU trivia.

## When to use

- Building a new service (instrumentation is part of "done").
- Incidents take hours because evidence is missing or unqueryable (see production-debugging).
- On-call is drowning in alerts nobody acts on, or sleeping through outages users noticed first.
- Costs from logs/metrics/traces are exploding.
- Defining SLOs or redesigning alerting.

## Goals

- The three signals wired to their questions: metrics (how much/how many), logs (what exactly happened), traces (where in the chain).
- Every log line correlated (request/trace ID); every request traceable end-to-end.
- Alerts page only on symptoms (user-facing pain) that are urgent AND actionable; everything else is a ticket or a dashboard.
- SLOs defined per critical flow, driving alerting via burn rates and engineering priorities via error budgets.

## Expert Mental Model

- **Instrument for the questions you'll ask under fire.** The 3 a.m. quartet: is it up? is it slow? who's affected? what changed? Every instrumentation decision is judged by whether it shortens one of those answers. Vanity instrumentation (dashboards nobody reads, logs nobody queries) is cost without a question.
- **The three signals answer different questions — use each for its job.** Metrics: cheap, aggregated, alertable — "how much, how often, is it trending" (but can't tell you about one specific request). Logs: expensive, detailed, searchable — "what exactly happened for request X" (but aggregating them badly reinvents metrics at 100× cost). Traces: the request's journey across services — "where did the time go / where did it die" (but sampled, so not for counting). Teams that use logs-as-metrics or metrics-where-they-need-traces pay double and answer slowly.
- **Averages are how dashboards lie** (see production-debugging). Latency is a distribution: p50 tells you the typical, p99 tells you the suffering, the mean tells you nothing actionable. Histograms from the start; percentiles per endpoint; and remember percentile math — you can't average p99s across nodes (aggregate the histograms, not the percentiles).
- **Cardinality is the metrics bill and the metrics killer.** Every label combination is a time series; `user_id` as a label = one series per user = a melted Prometheus and a five-figure bill. Labels are for *bounded* dimensions (endpoint, status class, region — tens to hundreds); unbounded identities (users, request IDs, emails) belong in logs and traces. This one discipline separates sustainable observability from the quarterly cost crisis (see memory-leaks — the monitoring-becomes-the-leak edge).
- **Alert on symptoms, not causes.** Page when *users hurt*: error rate on checkout, p99 SLO breach, queue age past budget. Don't page on CPU 80%, disk 70%, one pod restarting — those are causes that may never become symptoms; they're dashboard/ticket material. Every page must be urgent (now, not tomorrow), actionable (a human can do something), and novel (not the 40th duplicate) — a page failing any test trains on-call to ignore pages, and alert fatigue is how real outages get slept through.
- **SLOs turn reliability into a budget.** Define the user-meaningful objective per flow ("99.9% of checkout requests succeed in <500 ms over 30 days"); the complement is the error budget; burn-rate alerts (fast burn → page, slow burn → ticket) replace threshold whack-a-mole; a spent budget is a data-backed argument to ship reliability work instead of features. SLOs are the interface between engineering and the business about how reliable is reliable enough (see system-design nines).
- **Correlation is the connective tissue.** A request ID / trace ID minted at the edge and propagated through every hop, every log line, every queue message (see async-processing, event-driven) converts "grep five services and guess" into "follow one thread." Structured logging without correlation IDs is a filing cabinet without folders.

## Workflow

1. **List the critical user flows** and define SLIs per flow (availability: success rate; latency: p95/p99 against threshold) — measured as close to the user as feasible (edge/LB beats app-server self-report).
2. **Set SLOs with the business** (see system-design: nines cost money — sign them, don't assume them) and derive error budgets.
3. **Instrument metrics — RED per service** (Rate, Errors, Duration-as-histogram, labeled by endpoint/method/status-class) **and USE per resource** (Utilization, Saturation, Errors for pools, queues, DBs, hosts). Add the leading indicators: queue oldest-age, replication lag, pool saturation (see system-design).
4. **Structure the logs**: JSON, consistent field names (one org-wide schema: `timestamp, level, service, trace_id, user_id_hashed, event, ...`), events-not-prose ("order_placed" + fields beats "User order has been successfully placed!"), request/trace ID on *every* line, errors with stack + context. Log at boundaries (request in/out, dependency calls, state transitions), not per-line-of-code.
5. **Deploy tracing** with context propagation across HTTP/queues (W3C traceparent; instrument the frameworks once, centrally); sample intelligently — head-sample a few % for the ambient picture, tail-sample (keep all errors + slowest) for the interesting ones.
6. **Wire the correlation**: trace ID minted at edge → HTTP headers → log fields → queue message envelopes (see async-processing) → response header (support can ask users for it — see api-design request_id).
7. **Build burn-rate alerts on the SLOs** (fast: e.g., 14× burn over 5m+1h windows → page; slow: 2–3× over 6h+3d → ticket) plus a minimal set of symptom alerts for what SLOs don't cover (cert expiry, queue-age budgets, DLQ non-empty — see async-processing).
8. **Audit the pager**: every existing alert faces the urgent/actionable/novel test; survivors get a linked runbook ("if this fires: check X, mitigation Y"); the rest become tickets or die.
9. **Build the per-service standard dashboard** (golden signals top; saturation row; dependency row; deploy markers overlaid — see production-debugging) and the segmentation dashboard (by version/region/tenant) — pre-built, because incident-time is the wrong time to write queries.
10. **Manage the cost**: retention tiers (hot 7–30d, warm/cold archive), sampling policies (keep all errors, sample successes), cardinality budgets enforced in metrics-review, quarterly bill-vs-question audit ("which signals answered questions this quarter? which just cost?").

## Decision Tree

- "How many / how fast / is it trending?" → metric. If you're about to `grep | wc -l` logs on a schedule → it wanted to be a metric.
- "What exactly happened for THIS request/user?" → logs, keyed by correlation ID.
- "Where in the chain did latency/failure happen?" → trace. If you're adding timing logs at every hop to hand-assemble a waterfall → it wanted to be a trace.
- Should this alert page?
  - Users hurting now (SLO burn, checkout errors, queue age past budget) AND a human can act → page, with runbook.
  - Real but not urgent (slow burn, disk 70% with weeks of headroom, DLQ trickle on non-critical) → ticket.
  - Informational ("deploy happened", "autoscaled") → dashboard/log only. No notification channel at all.
- Label or log field?
  - Bounded dimension (endpoint, status, region, plan-tier) → metric label.
  - Unbounded (user, order, request) → log/trace field, never a label.
- Sampling:
  - Errors and outliers → keep 100% (tail sampling).
  - High-volume success traffic → sample logs/traces (0.1–10% by volume); keep full metrics (they're pre-aggregated anyway).
- If a question during an incident took >15 minutes to answer → post-incident action item: what one signal/dashboard/query would have made it 1 minute? Build that, not "more logging everywhere."

## Heuristics

- Wide events beat many events: one rich log line per request per service (all the fields) out-answers twenty breadcrumb lines — and costs less.
- Never log: secrets, tokens, passwords, full PII, raw card data — enforce with scrubbing middleware + CI grep, not vigilance (see web-security); hash user identifiers where correlation matters but identity shouldn't leak.
- Log levels mean things: ERROR = a human should eventually look (alertable in aggregate); WARN = suspicious, tolerated; INFO = business events; DEBUG = off in prod, sample-able on demand. An ERROR that's expected behavior is mislabeled noise that devalues the level.
- The health endpoint should exercise real shallow dependencies (DB ping, cache ping) — gray failures hide behind static-200 health checks (see production-debugging).
- Deploy markers on every dashboard: "what changed" is the first incident question; make it a glance (see production-debugging).
- Instrument the client edge for user-truth where it matters (RUM — see frontend-performance): server-side 200s don't see the CDN failure or the JS crash.
- Queue metrics that matter: oldest-message-age (not just depth), per consumer group (see async-processing); DB metrics that matter: replication lag, pool saturation, lock waits, slowest-queries (see postgres).
- One alert = one runbook link. An alert whose response starts with "figure out what this means" fails the actionable test.
- Test your alerts: fire drills (synthetic breach) quarterly — an alert that has never fired is a hypothesis, not a safety net.
- The on-call handoff review: pages this week, which were actionable, which were noise — the standing agenda item that keeps the pager honest (kill or fix every noise source weekly).
- Traces without service-boundary spans are just slow logs: instrument dependency calls (DB, HTTP, queue) as spans with status — the waterfall is the point.

## Quality Checklist

- [ ] SLIs/SLOs defined per critical flow, measured near the user, signed by the business.
- [ ] RED per service + USE per resource + leading indicators (queue age, replication lag, saturation) as histograms/gauges with bounded labels.
- [ ] Logs structured (org schema), correlated (trace ID every line), boundary-focused, PII-scrubbed.
- [ ] Traces propagate across all hops including queues; tail-sampling keeps errors/slowest; waterfalls show dependency spans.
- [ ] Burn-rate alerting live (fast→page, slow→ticket); every page passes urgent/actionable/novel; runbooks linked.
- [ ] Cause-alerts demoted to tickets/dashboards; pager audit done within the last quarter.
- [ ] Standard per-service dashboard + segmentation dashboard + deploy markers exist before the incident.
- [ ] Cardinality budget enforced; no unbounded labels (verified, not assumed).
- [ ] Retention/sampling tiers deliberate; cost reviewed against questions-answered quarterly.
- [ ] Correlation ID returned to clients (supportability) and threaded through async boundaries.

## Failure Modes

- **Alert fatigue spiral**: 40 pages/week, 38 ignorable → on-call auto-acks everything → the real outage scrolls past → post-incident adds *more* alerts. The exit is deletion and SLO-based paging, not addition.
- **Logging prose at volume**: unstructured "Successfully processed the user's request!" lines — unqueryable, expensive, and silent about the one field you needed (which request?).
- **The cardinality explosion**: someone labels a metric by user_id; the metrics backend melts; the bill triples; ironically, observability goes down (see memory-leaks edge).
- **Averages on the wall**: mean latency 80 ms on the big screen while p99 is 12 s and the top customer churns (see production-debugging average-gazing).
- **Health-check theater**: `/health` returns static 200; the LB routes traffic to a pod whose DB connections are all dead — gray failure with green dashboards.
- **Trace fragmentation**: tracing adopted but context dies at the queue boundary — every async workflow becomes two unlinked half-traces; the expensive tool answers half the question.
- **Instrument-everything-after-the-incident**: blanket DEBUG logging added in panic, never removed — signal-to-noise and cost both degrade, next incident is *harder* (see root-cause-analysis instrumentation tradeoff).
- **SLO cosplay**: SLOs defined in a doc, wired to nothing — no burn alerts, no budget consequences; thresholds still page on CPU. The ritual happened; the system didn't change.
- **Cost blindness then cost panic**: nobody owns the telemetry bill until finance does — then retention gets slashed uniformly, deleting the errors you needed with the noise you didn't.

## Edge Cases

- **The observer down** (see production-debugging): your logging pipeline backpressures the apps, or metrics vanish and you're blind, not down — need: out-of-band probes, non-blocking telemetry emission (drop, don't block), and a known blind-flying runbook.
- **Sampling vs the rare bug**: the 1-in-10k failure is exactly what head-sampling drops — tail sampling on error/latency criteria is the fix; for counting rare events, metrics (unsampled by design) not traces.
- **High-cardinality *questions* ("which tenant is affected?")**: the dimension is unbounded for metrics but essential for incidents — answer with exemplars (trace links attached to histogram buckets), logs-derived analytics, or bounded top-K tenant labels for your whales only.
- **Clock skew across services**: spans that end before they start, logs mis-ordered — NTP discipline plus trust trace-relative timing over absolute timestamps (see concurrency-bugs).
- **Multi-tenancy privacy in telemetry**: tenant-identifiable data in logs/traces crossing regions or retention policies — telemetry is a data store; it inherits compliance requirements (residency, erasure) nobody budgeted (see event-driven GDPR edge).
- **Batch/scheduled work**: RED fits requests badly for jobs — instrument jobs with: last-success-age ("freshness"), duration trend, records processed; alert on "hasn't succeeded in X" not just "failed" (the job that silently stops *scheduling* fires no failure alert — see production-debugging silent outage).
- **Client-side blind spots**: server metrics green, users on broken JS or a failing CDN — RUM + synthetic probes from outside your network are the only honest uptime (see frontend-performance).
- **Very low traffic services**: percentiles and error *rates* are noise at 3 requests/hour — alert on consecutive failures and synthetic probes instead of rates.

## Tradeoffs

- **Coverage vs cost**: 100% traces and debug logs answer everything and cost absurdly; aggressive sampling is cheap and occasionally blind. Resolve by value-tiering: full fidelity on errors/outliers/critical flows, sampled elsewhere, archived cold for the tail.
- **Page sensitivity vs sleep**: catching everything early means paging on maybes; SLO burn rates buy you a principled middle — fast-burn pages (real, now), slow-burn tickets (real, tomorrow) (see production-debugging alert tradeoff).
- **Standardization vs team autonomy**: one org logging schema/label taxonomy makes cross-service debugging possible and costs teams local convenience — pay the standardization; incidents are cross-service by nature.
- **Build vs buy**: self-hosted stacks (Prometheus/Loki/Tempo-class) cost ops and give control; SaaS observability costs real money at volume and gives velocity. Common failure both ways: unmanaged cardinality/retention — the discipline matters more than the vendor.
- **Instrumenting now vs shipping now**: telemetry added post-launch is added post-incident, under panic, badly. The standard middleware (metrics+logs+traces per request, free per service) makes the tradeoff mostly vanish — invest in the paved road once.

## Optimization Strategies

- Build the golden middleware once: every service gets RED metrics, correlated structured logs, and trace propagation by importing the platform library — per-service instrumentation cost drops to near zero, and consistency comes free.
- Run the "question audit" quarterly: list the incident/debug questions actually asked; check each answered in <5 min; build the gap-closers; delete telemetry that answered nothing (the bill audit and the quality audit are the same meeting).
- Exemplars everywhere: link histogram buckets to sample traces — the p99 spike becomes one click from graph to waterfall.
- Pre-aggregate expensive log analytics into metrics at emission (counter-per-event) rather than log-scanning dashboards — 100× cheaper, faster, and alertable.
- Synthetic probes for the flows that matter (login, checkout, API canary) from outside your infrastructure — user-truth uptime plus low-traffic-service coverage in one tool.
- Adopt OpenTelemetry-compatible instrumentation for portability — vendor negotiation leverage and survival across the inevitable backend migration.
- Treat runbooks as code-adjacent: linked from alerts, updated in incident PRs (see production-debugging postmortems), staleness-checked when alerts fire ("was the runbook right? fix it now").

## Self Review

- For the 3 a.m. quartet on my critical flow: how many minutes to each answer, demonstrated (not hoped)?
- Which of my alerts would page a human for something they can't act on right now? Why do those still exist?
- Can I follow one request from edge to DB to queue-consumer with a single ID? Where does the thread break?
- What's my highest-cardinality metric, and who approved it?
- Do my latency charts show percentiles from histograms — and do I ever aggregate percentiles wrongly across nodes?
- Which SLO would fire first in a real degradation, and when did it last fire (drill or reality)?
- What did telemetry cost last month, and which questions did it answer?
- If my logging pipeline died right now, what tells me — and what's the runbook?

## Examples

**1. The golden middleware installed org-wide.**
Platform team ships one library: every HTTP/queue handler automatically gets — RED histogram metrics (endpoint/method/status labels, bounded), one wide structured log per request (trace_id, hashed user, latency, status, dependency timings), W3C trace propagation including queue envelopes (see async-processing). Services adopt by import; the org logging schema is enforced by the library's types. Result measured a quarter later: cross-service incident queries standardized ("show me trace X" works everywhere), new-service instrumentation cost ≈ zero, and two legacy services' bespoke prose-logs stand out as the archaeology they are — migration scheduled.

**2. Pager bankruptcy, declared and exited.**
On-call: 47 alerts/week, 6% actionable. The audit: every alert faces urgent/actionable/novel — 31 deleted or demoted to tickets (CPU thresholds, single-pod restarts, disk-70%), 9 merged into 3 symptom alerts, the rest get runbooks. SLOs defined on the four user flows; burn-rate alerts installed (fast: page; slow: ticket into the weekly review). Three weeks later: 4 pages/week, all actionable; the DLQ trickle that used to page at 2 a.m. is a Monday ticket; the checkout-latency slow burn that *never* paged before (it crept under thresholds) opened a ticket that pre-empted an outage (see production-debugging slow-burn case). On-call handoff review keeps the ratchet: any noisy page gets killed or fixed that week.

**3. Cardinality incident and the budget that followed.**
Metrics bill triples in a month; Prometheus OOMs (see memory-leaks). Culprit: a well-meaning `http_requests_total{user_id=...}` label — 400k series. Fix: label deleted (identity moved to logs/traces where it belongs), exemplars wired so histograms still link to per-request traces, and a cardinality budget instituted: new metrics reviewed for label bounds, CI check flags unbounded-looking labels, per-team series quotas dashboarded. The postmortem's lesson generalized: *metrics are for aggregates over bounded dimensions* — printed, half-jokingly, on the team wiki's first line, and never violated since because the CI check doesn't rely on memory.

**4. Tracing across the async gap.**
Symptom: order-flow traces end at "published to queue"; the fulfillment half is a separate orphan trace — every async incident requires manual timestamp-joining. Fix: trace context injected into the message envelope (traceparent field — see event-driven envelope standard), consumers continue the trace as a linked span with explicit "queue wait" duration. First week's payoff: a p99 spike investigation reads as one waterfall — 9 s of "queue wait" (consumer lag), not slow processing — redirecting the fix from "optimize the consumer code" to "scale the consumer group" in one glance (see async-processing lag). The waterfall answered in seconds what logs would have taken an hour to reconstruct.

## Evaluation Rubric

Score 1–10:

- **1–2**: Prose logs, no correlation; threshold alerts on causes; no percentiles; no traces; incidents debugged by ssh-and-grep.
- **3–4**: Some structured logging and dashboards; alert noise high; traces partial (break at async); cardinality and cost unmanaged; SLOs absent or decorative.
- **5–6**: RED/USE metrics with histograms; correlated logs; symptom-first alerting emerging; traces cover sync paths; per-service dashboards with deploy markers.
- **7–8**: Full checklist: SLO burn-rate paging with runbooks, pager audited, async trace propagation, cardinality budgets, tiered retention, segmentation dashboards pre-built.
- **9–10**: Additionally: golden middleware makes instrumentation free; exemplars link metrics→traces; synthetic probes + RUM for user-truth; quarterly question-vs-cost audits; drills prove the 3 a.m. quartet answers in minutes; the pager is quiet and trusted.
