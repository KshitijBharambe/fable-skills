# Compliance & Privacy Engineering

## Purpose

Build the engineering substrate that makes compliance true rather than claimed — data inventories, PII minimization, retention and deletion that actually delete, consent that gates processing, audit trails, license hygiene, and platform-policy awareness — so regulations (GDPR/CCPA-class), certifications (SOC 2-class), and store policies are met by architecture instead of by scramble, and counsel's questions have engineering answers.

## When to use

- The product touches personal data (accounts, analytics, support — i.e., almost always), payments, or minors.
- Entering regulated territory: EU/UK users, California, health or financial data, enterprise customers sending security questionnaires.
- Designing data collection, retention, deletion, export, or consent flows.
- Shipping to app stores or platforms with policy gates; adopting dependencies or vendors (DPAs, licenses).
- SOC 2 / ISO / audit preparation, or a deletion/export request just arrived and nobody knows the procedure.

## Goals

- Every personal-data flow is known: what's collected, why, where it lives, who touches it, when it dies (the data map).
- Deletion and export requests are executable procedures with SLAs, covering backups, replicas, logs, and vendors.
- Consent and purpose actually gate processing in code — not banners decorating unconditional collection.
- Privileged access to personal data is scoped, logged, and reviewable (see auth; security).
- Dependency licenses and platform policies checked before they're load-bearing; audits answerable from evidence, not heroics.

## Inputs

- Jurisdictions and user populations (EU/UK, California, minors, health/finance verticals) — which regimes apply is a legal call; *knowing what you process* is engineering's input to it.
- The actual data flows: collection points, stores, third-party processors, analytics, logs, backups (see data-modeling; observability).
- Contractual obligations: enterprise DPAs, security questionnaires, platform developer agreements.
- Counsel/compliance guidance where it exists — this skill implements policy; it doesn't practice law.

## Outputs

- A living data map: personal-data categories × purpose × store × processor × retention, versioned with the schema (see data-modeling).
- Working deletion/export machinery with tests and SLAs; retention jobs that run and report.
- Consent/purpose enforcement in the data path; PII-scrubbed telemetry (see observability; security).
- Audit trails for privileged access and consequential actions; license and vendor inventories; an evidence trail that makes audits boring.

## Expert Mental Model

- **Compliance debt is invisible until it's existential — price it like security debt.** Nothing breaks in staging when you log PII, skip the deletion path, or ship a GPL dependency in proprietary code; the bill arrives later as a regulator's letter, a failed enterprise deal, a store takedown, or a breach disclosure amplified by everything you retained. The engineering asymmetry mirrors security's (see security: same curve): designed-in costs little; retrofitted costs quarters. And the trigger is often growth itself — the day the first EU customer signs, the day the app crosses into "health data," the day procurement sends the questionnaire.
- **You can't protect, delete, or disclose what you can't find.** The data map — what personal data, collected where, for what purpose, stored where, shared with whom, deleted when — is the substrate under *every* obligation: deletion requests, export requests, breach-notification scoping, consent enforcement, questionnaire answers. Without it, every request is a company-wide archaeology dig (see the same measured-inventory law in refactoring's migrations: folklore isn't inventory). It lives with the schema and the vendor list, versioned, or it rots into fiction within two quarters.
- **The cheapest data to protect is the data you never collected.** Minimization is the highest-leverage privacy control and it's pure engineering: don't collect what has no purpose, don't retain what's past its purpose, don't send the whole user object where an ID would do (see api-design: response shaping), don't log the payload when the event will do (see observability: scrubbing is the backstop, not the plan). Every field collected is permanent liability surface — it must be protected, inventoried, disclosed, exported, and deleted, forever. "We might need it someday" is how companies end up breached of data they never used.
- **Deletion is a distributed-systems problem wearing a legal costume.** "Delete my data" fans out across the primary DB, read replicas, caches, search indexes, analytics warehouses, logs, backups, and every vendor you've shared data with (see data-modeling: deletion semantics; event-driven: the projections too). Soft-delete flags satisfy none of it. The workable architecture is designed, not improvised: deletion as an orchestrated, idempotent, auditable job (see async-processing) with per-store strategies — hard delete where possible, crypto-erasure (destroy the per-user key) where deletion is impractical (immutable backups), TTL-alignment for backup rotation windows, and API calls to processors. Retention is deletion's proactive twin: data with a purpose has a lifespan; jobs enforce it on schedule, and "keep forever" becomes an explicit decision someone signed (see data-modeling: the retention column of the history ladder).
- **Consent and purpose are runtime state, not banner theater.** A consent banner that doesn't change what the code does is evidence *against* you. Consent/purpose enforcement means: preferences stored as auditable state (who consented to what, when, via which text version), checked *in the data path* (the analytics event drops pre-consent; the marketing pipeline filters the opted-out), propagated to processors, and honored on withdrawal with the same machinery as deletion. Purpose limitation is the quieter twin: data collected for login security doesn't silently become ad-targeting fuel — in code terms, purpose is a dimension on the data map that writes checks the readers must pass (see auth: the same shape as permission checks, applied to processing).
- **Audits and questionnaires run on evidence; evidence is a build artifact.** SOC 2-class certification and enterprise security reviews ask: do you control access, review changes, monitor, respond to incidents — *and can you prove it for the trailing year?* Teams that treat this as an annual scramble reconstruct evidence from memory; teams that treat it as telemetry emit it continuously: access reviews on calendar, deploy approvals in the pipeline (see deployment; ci-cd), audit logs append-only and queryable (see data-modeling), incident timelines from the postmortem process (see production-debugging). The controls you'd want anyway, instrumented — certification becomes a report over data you already have.

## Workflow

1. **Build the data map**: walk the schema, the event streams, the logs, and the vendor list; for every personal-data category — purpose, legal basis (with counsel), store, processors, retention, deletion path. Start embarrassing, iterate honestly (the same spreadsheet law as the secret inventory in security).
2. **Minimize against the map**: for each field/flow — is the purpose real and current? Kill collection without purpose; shorten retention to purpose-length; replace identifying data with IDs, aggregates, or nothing (see data-modeling; the deletion-is-cheapest instinct from first-principles).
3. **Classify and contain PII in the architecture**: tag PII at the schema level (see data-modeling: the data dictionary carries it), keep it out of URLs, logs, error trackers, and analytics by construction (see observability scrubbing; security: the telemetry path), and prefer PII-lean event payloads (IDs that dereference behind access control, not embedded emails — see event-driven).
4. **Build the deletion and export machinery**: orchestrated jobs fanning out per the data map — idempotent, resumable, logged (see async-processing); per-store strategy chosen (hard delete / crypto-erasure / TTL alignment); processor APIs wired; export assembling the same map's stores into a portable format. Test both with fixtures; measure the SLA.
5. **Enforce retention on schedule**: TTLs and cleanup jobs per category, monitored like any batch job (see observability) — a retention policy without a running job is a document, not a control.
6. **Wire consent/purpose into the data path**: preference store with versioned consent records; checks at the collection and processing points (the SDK that doesn't fire pre-consent; the pipeline that filters by purpose); withdrawal flows reusing the deletion machinery where required.
7. **Instrument privileged access**: admin/support access to personal data scoped, time-boxed, and audit-logged (see auth: the admin story); access reviews on calendar; the audit log itself append-only with its own retention (see data-modeling).
8. **Gate the supply chain**: license checks in CI (see ci-cd) with an allowlist policy (permissive fine; copyleft flagged for review before it's load-bearing); vendor intake includes DPA/subprocessor review alongside the security review (see security: vendor SDKs; research: evaluation before adoption).
9. **Prepare the incident path**: breach response is incident response plus notification obligations — the runbook answers "what data, whose, since when" from the data map and audit logs (see production-debugging: evidence preservation), with counsel's contact and the notification-clock reality (72-hour-class deadlines) written down before any incident.
10. **Make evidence continuous**: map controls to artifacts the pipeline already produces (reviews, approvals, access logs, drills); schedule the recurring rituals (access review, retention verification, restore drill, policy re-read) — audit prep becomes a query, not a quarter (see deployment: approvals as code).

## Decision Tree

- If collecting a new field/event → purpose named? retention chosen? map updated? If any answer is "someday/forever/later" → don't collect, or escalate the decision to whoever owns the liability (see product-thinking: features have costs beyond build).
- If a feature processes existing data for a *new* purpose → purpose-limitation flag: check the basis with counsel/compliance before shipping, not after the launch email.
- If PII wants to enter logs/analytics/prompts → redesign to IDs and events; scrubbing is the backstop for mistakes, not the transport plan (see observability; the AI-surface warning in security).
- If a deletion request arrives → execute the machinery; if there is no machinery → this request is the forcing function: build the orchestrated path now, handle this one manually with a written checklist against the data map, log everything.
- If data must survive deletion (legal hold, financial records, fraud) → that's an *exemption with an owner and a citation*, recorded per category in the map — not a silent default (see data-modeling: append-only vs erasure tension, resolved deliberately).
- If backups make hard deletion impractical → crypto-erasure (per-user/tenant keys, destroy on delete) or documented backup-rotation windows with counsel's sign-off — pick the strategy per store, write it down.
- If adopting a dependency → license in the allowlist? If copyleft/unclear → review before it's load-bearing (see research; the exit-cost question from security's dependency gate).
- If onboarding a vendor that touches user data → DPA, subprocessor list, deletion API, data residency — into the vendor inventory; no data flows until the paperwork and the deletion path exist.
- If shipping through app stores/platforms → read the current policy for your category *before* building (privacy labels, data-safety forms, purpose strings, payment rules) — platform policy is compliance with faster enforcement and no appeal to counsel (see research: primary sources).
- If enterprise deals stall on security questionnaires → the questionnaire is the requirements doc: map each "no" to a control gap, prioritize by deal value × implementation cost — and stop answering aspirationally (a false "yes" is worse than a "no, roadmapped").
- If minors, health, financial, or biometric data enter the picture → stop; these regimes (COPPA/HIPAA/PCI-class) are specialized — engineering's job is knowing *that* the threshold is being crossed and flagging it before launch, then implementing what counsel scopes (PCI's standard move: don't touch card data — tokenize via the payment processor so scope shrinks to nearly nothing).

## Heuristics

- Collect at need, not at hope: the field you add "for later analysis" is liability now and archaeology later.
- IDs travel, PII stays home: cross-system flows carry references; the PII lives in one access-controlled place (see event-driven: payload minimalism has a privacy reason too).
- Every copy weakens control: each replica, export, warehouse sync, and vendor share is another place deletion must reach — count copies before creating them (see data-modeling: cross-store consistency, liability edition).
- "Anonymized" is a strong claim: stripped names with retained user IDs, timestamps, and locations is *pseudonymized* — re-identifiable, still personal data; true anonymization (aggregation, k-anonymity thresholds) is harder than the word suggests. Use the weaker word until proven otherwise.
- The retention question is "when does this die," asked at creation — every table, topic, bucket, and log stream gets a TTL or an explicit "keep because X, owner Y."
- Consent text is versioned data: "user consented" is incomplete without *to which version, when, through what* — the record is the defense.
- Support tooling is a privacy surface: the admin panel that shows everything to every agent is the most-used breach vector you own (see auth: scoped, logged support access).
- Logs are data stores with the worst governance: they get retention, access control, and PII budgets like any database (see observability), or they become the shadow copy of everything.
- Dependency licenses are inherited obligations: `npm install` can encumber your codebase as surely as a contract — automate the check (see ci-cd), review the exceptions.
- The 72-hour clock starts before you're ready: breach-notification deadlines assume you can scope impact fast — the data map and audit logs are what "fast" is made of.
- Deletion requests are load-tested by adversity: the angry ex-employee, the litigious customer — the machinery must work for the hardest requester, which is why it's machinery and not favors.
- When the honest answer to a questionnaire is embarrassing, the fix is the control, not the wording.

## Quality Checklist

- [ ] Data map current: categories × purpose × store × processor × retention; reviewed on schedule; versioned with schema changes.
- [ ] Minimization pass done: no collection without purpose; PII-lean events and logs by design.
- [ ] Deletion machinery: orchestrated, idempotent, covers all stores + vendors per the map; tested with fixtures; SLA measured. Export likewise.
- [ ] Retention jobs running per category, monitored; exemptions documented with owners.
- [ ] Consent recorded (versioned text, timestamp, mechanism) and enforced in the data path; withdrawal works.
- [ ] Privileged access to personal data scoped, time-boxed, audit-logged; reviews on calendar (see auth).
- [ ] Telemetry PII-clean: scrubbing verified, log retention set, error trackers configured (see observability; security).
- [ ] License policy automated in CI; vendor inventory with DPAs and deletion paths.
- [ ] Breach runbook: scoping queries pre-written, counsel contact, notification clocks documented.
- [ ] Evidence continuous: controls mapped to artifacts; audit answerable from queries, not memory.

## Failure Modes

- **The banner Potemkin**: a consent banner over unconditional collection — the SDKs fire before the choice, "reject" changes nothing; discoverable by anyone with devtools, and regulators have devtools.
- **Soft-delete "deletion"**: `deleted_at` set, data intact in the primary, replicas, warehouse, logs, and four vendors — the deletion request "completed" while the data lives in six places (see data-modeling: soft delete is not erasure).
- **The shadow warehouse**: analytics ingesting full user objects for years — every deletion incomplete, every breach bigger, every questionnaire answer now a confession; payload minimization would have prevented the entire class.
- **PII in the exhaust**: emails in URLs, tokens in logs, user objects in error trackers, customer data pasted into LLM prompts — the primary stores immaculate, the telemetry a parallel unaudited copy (see security: secret-bearing logs, privacy edition).
- **Retention by inertia**: nothing ever deleted because nothing was ever scheduled — a decade of user data as breach amplifier and discovery liability, "kept" by no one's decision.
- **The license surprise**: a copyleft dependency deep in the tree of a proprietary product, discovered during acquisition due diligence — the fix is a rewrite under deadline pressure at the worst possible negotiating moment.
- **Questionnaire fiction**: "yes" to encryption-at-rest, access reviews, and DR drills that don't exist — the enterprise deal closes, the audit rider arrives, and the fiction becomes a contract breach.
- **The scramble audit**: SOC 2 prep as a quarter-long emergency of retroactive policy-writing and evidence reconstruction — annually, because nothing was instrumented (the continuous-evidence teams spend days).
- **Store-policy blindside**: the app built around a monetization or data flow the platform prohibits — discovered at review time, after the architecture ossified around it.

## Edge Cases

- **Legal holds vs deletion**: litigation freezes deletion for specific data — the machinery needs a hold mechanism (scoped, logged, expiring) that overrides retention *and* deletion jobs without disabling them globally.
- **Backups and immutable stores**: hard deletion from immutable/offline backups is impractical — crypto-erasure or documented rotation windows, decided with counsel; and restore drills (see deployment) must not resurrect deleted users into live systems — the restore path replays the deletion ledger.
- **Derived data and ML**: models trained on user data, embeddings, aggregates — deletion's reach into derived artifacts is a genuinely unsettled edge; the engineering posture: track lineage (which artifacts derive from user data — see data-modeling), prefer training pipelines that can retrain-on-schedule, and route the policy question to counsel *with* the lineage map (see rag; fine-tuning territory in evals).
- **Cross-border data flows**: residency requirements and transfer mechanisms change with regulation and case law — engineering's part is *capability*: knowing where data lives (the map), regional storage where architecture allows (see system-design: multi-region has a compliance dimension), and processors' regions in the vendor inventory.
- **The employee dimension**: HR data, workplace monitoring, internal tools — the same obligations point inward; the support-tooling audit trail is also an employee-privacy question.
- **Minors and age gates**: age signals create obligations (parental consent regimes) and are themselves sensitive data — crossing into child-directed territory is a legal-review trigger, not a checkbox (see the decision tree's stop-and-flag).
- **B2B processor role**: when enterprises' *users'* data flows through you, their DPA terms become your requirements — deletion/export on their instruction, subprocessor disclosure (your vendor list is now customer-facing), breach notification *to them* on contract clocks (see api-design: you're part of someone else's compliance story).
- **Public and scraped data**: "it was public" doesn't exempt processing obligations in several regimes — collection purpose and basis still apply; flag it, don't assume it.

## Tradeoffs

- **Data richness vs liability surface**: analytics and ML genuinely want data; every field kept is permanent obligation. Resolve by purpose-honesty: keep what has a *named* current use with an owner; aggregate or drop the rest — "we might need it" loses to "we must protect it forever."
- **Retention brevity vs debugging/support reality**: 30-day logs frustrate the investigation of the 45-day-old incident (see production-debugging) — tier it: PII-lean operational telemetry keeps longer windows; PII-bearing data gets short ones; the split is the point (see observability: cost tiers align with privacy tiers).
- **Friction of consent vs completeness of data**: honest consent reduces collection coverage; dark patterns recover it and are increasingly *themselves* violations — take the coverage hit, design analytics to work with cohorts and aggregates.
- **Centralized PII vault vs distributed convenience**: one access-controlled PII store with references elsewhere simplifies deletion, export, and audit, and adds a dependency and a hop (see the same shape in security's secrets manager) — worth it as personal-data surface grows; overkill for a tiny footprint.
- **Compliance rigor vs shipping speed**: a data-map line and a retention decision per feature is minutes; the retrofit is quarters — but full ceremony on a pre-product prototype with no users is also misallocation. Scale the rigor to the data actually held and the users actually served; install the *habits* (map, purpose, TTL) before the volume arrives.
- **Certification scope vs substance**: certifications open doors and can be gamed narrow; enterprise buyers increasingly probe past the badge. Build the controls for their operational value (they're mostly security and deployment hygiene you want anyway — see security; deployment), let the certificate be a report on reality.

## Optimization Strategies

- Attach the data-map update to the schema-migration ritual (see data-modeling; code-review): a PR adding a personal-data column without a map line fails review — the map stays true by construction.
- Centralize PII access behind a service/module with logging built in (see the enforcement-point pattern in security): deletion, export, audit, and scoping become one team's solved problem instead of every team's partial one.
- Make deletion a first-class async job with a dashboard (see async-processing; observability): per-store completion, vendor confirmations, SLA tracking — the request that used to take a quarter becomes a queue entry.
- Put license and PII-pattern checks in CI (see ci-cd): the copyleft dependency and the `email` field in a log statement caught at commit time cost nothing; caught at diligence/audit time they cost quarters.
- Run the drills on calendar: a synthetic deletion request end-to-end, a restore that respects the deletion ledger, a tabletop breach with the scoping queries — each drill either proves machinery or files the bug (see resilience-engineering: game days; deployment: rehearsed reverses).
- Template the questionnaire answers from the evidence base: a maintained controls doc with artifact links turns each enterprise review from a week of meetings into an afternoon of curation (see technical-writing).
- Treat policy changes (regulations, platform terms) like dependency upgrades: someone owns the watch, changes land as reviewed diffs to the map and controls — not as annual surprises (see research: the standing watch).

## Self Review

- Could I produce, today, the list of every store and vendor holding a given user's data? How long would deletion actually take, and would the logs prove it happened?
- What did this feature collect that it doesn't need, and what did it retain past its purpose?
- Where does PII leak into telemetry, prompts, or exports — verified, or assumed clean?
- Does consent state actually change what the code does? Could I show the auditor the check?
- Who accessed customer data through support tooling this month, and would the log show me?
- Which dependencies' licenses have I never checked? Which vendors have no deletion path?
- If a breach were discovered right now, could I scope whose data and since when within the notification clock?
- Which threshold is this product near (EU users, minors, health, payments) — and have I flagged it, or am I hoping?

## Examples

**1. The deletion request that built the machinery.**
A GDPR deletion request arrives at a 40-person startup; the honest inventory finds the user in: Postgres (plus replicas), Redis sessions, Elasticsearch, the analytics warehouse (full user objects — the shadow copy), S3 exports, log archives, and three vendors (email, support desk, product analytics). The first request executes as a written manual checklist against this map, logged step-by-step — two weeks, humbling, compliant. The build that follows: a deletion orchestrator (idempotent fan-out job with per-store adapters and vendor API calls — see async-processing), warehouse ingestion rewritten to IDs-plus-aggregates (killing the shadow copy — minimization retroactively), log pipeline scrubbing verified with canary PII (see observability), and a quarterly synthetic-deletion drill. Request two takes four days; request nine takes six hours, unattended, with a completion report. The retro's line: *the request was the audit; the machinery was always the requirement.*

**2. Consent made real in the data path.**
A consumer app's banner is discovered (by a customer's devtools screenshot, publicly) to be decorative — analytics SDKs fire on page load regardless of choice. The fix goes to architecture, not banner copy: a consent service stores versioned records (choice, timestamp, text version, mechanism); the SDK loader gates on it (no consent, no script — verified by an automated test that asserts zero third-party requests pre-consent, wired into CI — see testing-strategy); server-side events carry a purpose tag filtered against preferences in the pipeline; withdrawal triggers the deletion machinery for the analytics stores. Marketing's dashboards lose ~30% of raw volume and gain cohort-level honesty (see the tradeoff, taken openly). The screenshot that started it becomes the onboarding deck's slide one: *the banner is a promise; the code keeps it or breaks it.*

**3. The license check that saved the acquisition timeline.**
A due-diligence scan on a Series-B startup would have found: an AGPL charting library inside the proprietary SaaS frontend and a "non-commercial use" model weight file in the ML pipeline — each a rewrite-under-pressure at the worst table in the company's life. It doesn't find them, because eighteen months earlier a CI license gate (allowlist: MIT/BSD/Apache-class; flag-for-review: copyleft and custom terms — see ci-cd) had caught both at PR time: the chart library swapped for an Apache-licensed peer in a day (see research: alternatives exist when you look early); the model terms escalated, negotiated into a commercial license for $4k. Total prevention cost: an afternoon of CI config and two early substitutions. The diligence line item reads "clean"; nobody at the table knows it was ever otherwise — which is what prevention looks like.

## Evaluation Rubric

Score 1–10:

- **1–2**: No data map; collection by default, retention forever; deletion = soft-delete flag; consent decorative; PII throughout logs and vendors unknown; licenses unchecked; audits unanswerable.
- **3–4**: Privacy policy exists but describes aspirations; deletion manual and partial; some scrubbing, unverified; vendor DPAs signed unread; questionnaire answers optimistic; compliance work is annual panic.
- **5–6**: Data map real and maintained; deletion/export machinery covering the mapped stores; retention jobs on major categories; consent enforced at the main collection points; license gate in CI; privileged access logged.
- **7–8**: Full checklist: minimization as design habit, PII-lean telemetry verified, vendor lifecycle managed (intake through deletion), drills on calendar, breach runbook with pre-written scoping, evidence continuous, thresholds (minors/health/payments) actively watched.
- **9–10**: Additionally: PII centralized behind an enforcing service; map updates structural (schema-review-coupled); deletion SLAs measured in hours with proof; questionnaires answered from a living evidence base in an afternoon — and the pattern holds under stress: the audit, the deletion request, and the diligence scan are all boring, because the architecture made them queries.
