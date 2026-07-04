---
name: secrets-and-supply-chain
description: "Use when a credential is created or leaked, adding/upgrading/auditing dependencies (especially install scripts), designing CI/CD secret handling, onboarding a vendor SDK, or after a package-compromise incident."
---

# Secrets and Supply Chain Security

## Purpose

Keep credentials out of code, logs, and history; scope every credential to least privilege with rotation as a rehearsed routine; and treat the dependency graph as the attack surface it is — pinning, verifying, and gating what runs inside your trust boundary wearing your permissions.

## When to use

- Any credential is created, needed, found somewhere it shouldn't be, or suspected leaked.
- Adding, upgrading, or auditing dependencies — especially anything with install scripts, network access, or millions of transitive users.
- Designing CI/CD, where secrets, third-party actions, and publish rights concentrate (see ci-cd).
- Onboarding a vendor/SaaS whose SDK or webhook enters your codebase.
- Post-incident, when a leak or a compromised package forces the questions you should have answered calmly.

## Goals

- No secrets in source, config files in repos, logs, error trackers, or shell history — enforced by scanners, not vigilance.
- Every credential: least-privilege scoped, individually attributable, short-lived where possible, and rotatable in minutes without a war room.
- Dependencies pinned by lockfile with integrity hashes; upgrades reviewed as code; automated scanning as a floor, not the strategy.
- CI is treated as production: scoped tokens, pinned actions, no secret exposure to untrusted PRs.
- A rehearsed leak playbook: rotate first, investigate second, with blast-radius questions answerable from audit logs.

## Expert Mental Model

- **A secret in git history is public; a secret in a log is published.** History is forever — force-pushes don't unclone forks, and scanners crawl public commits within *seconds* of push (leaked AWS keys get exploited in under a minute; this is measured, not folklore). The expert reflex on any exposure is therefore rotation-first: the credential is dead the moment it touched the wrong medium; cleaning the medium is secondary hygiene, not the fix. Corollary: "we removed it from the repo" without rotation is a status update about the repo, not about the risk.
- **Least privilege is blast-radius engineering.** The question isn't "is this credential safe?" (it will leak eventually — a laptop, a log line, a dependency) but "what does the world look like *when* it leaks?" A read-only, single-bucket, IP-restricted, 1-hour token leaking is a log entry; an org-admin PAT leaking is an incident with a name. Experts scope by the *verb the workload actually performs* — the app that only reads S3 gets a role that only reads that bucket (see authorization: same principle, machine principals). Wildcard scopes are convenience borrowing against a breach.
- **Your dependencies run with your permissions.** `npm install` executes someone else's code on your machine and ships it inside your trust boundary (see web-security: boundaries) — every package is a vendor you've granted prod access without an interview. The real-world attack shapes: typosquats (`lodahs`), maintainer-account takeover pushing a malicious patch version, install-script exfiltration, protestware, and dependency confusion (a public package shadowing your internal name). None of these are exotic; all have shipped. The posture: lockfiles with integrity hashes decide what runs (pinning), floating ranges decide nothing, and *new* dependencies are an architecture decision, not an import statement.
- **Machine identity beats distributed static secrets.** The modern move is to eliminate long-lived secrets rather than guard them better: cloud IAM roles instead of embedded AWS keys, OIDC federation from CI to cloud instead of stored deploy credentials, workload identity between services (see system-design service auth), short-lived tokens minted per-use from a secrets manager. Every static secret you delete is a rotation you'll never botch and a leak that can't happen. The hierarchy: no secret > short-lived minted secret > vaulted static secret > env var > file in repo (never).
- **Rotation unrehearsed is rotation that won't happen.** If rotating the database password requires a maintenance window, three teams, and courage, it won't happen during the incident that demands it in minutes — and it hasn't happened for two years, which is why the incident is bad. Rotation is a *deploy-shaped* problem: dual-secret overlap windows (new and old valid during cutover), automation, and a schedule that keeps the muscle warm (see ci-cd: the same "if it hurts, do it more often" law). Attribution is the twin discipline: one credential per consumer, so audit logs answer "which key did this" and revocation doesn't take down five services to stop one.
- **CI/CD is where both threads meet — and where attackers know to look.** The pipeline holds the deploy keys, runs third-party actions by the dozen, and executes on every PR — it is production with worse review habits. The classics: a malicious PR modifying the workflow to dump secrets; a compromised action (pinned by tag, which moved) exfiltrating the environment; publish tokens with org-wide scope sitting in repo settings. Treat pipeline changes like prod changes, pin actions by commit SHA, scope tokens per-job, and never expose secrets to workflows triggered by untrusted forks (see ci-cd security).

## Workflow

1. **Inventory**: list every secret the system uses — where stored, what scope, who/what consumes it, when last rotated, how you'd know it leaked. The spreadsheet is embarrassing exactly once; then it's an asset.
2. **Centralize into a secrets manager** (cloud-native or vault-class): injection at runtime (env/volume/API), access audited, versioned. Config files hold *references*, never values.
3. **Eliminate where possible**: replace static credentials with platform identity — IAM roles, OIDC CI federation, workload identity. Every deletion beats any encryption.
4. **Scope what remains to least privilege**: per-consumer credentials, minimum verbs, resource-level restrictions, expiry where supported. One credential = one consumer = one audit trail.
5. **Gate the repo**: secret-scanning in CI *and* pre-commit (the pre-commit catch never enters history); block-merge on findings; scan the existing history once and rotate everything it finds — assume found = burned.
6. **Scrub the telemetry path**: redaction in the logging layer for token-shaped strings, auth headers, and known secret fields; error trackers configured to drop request bodies on auth routes (see observability scrubbing; web-security secret-bearing logs).
7. **Pin the supply chain**: lockfiles committed and enforced (`npm ci`, `--frozen-lockfile`, hash-pinned Python requirements); CI actions pinned by SHA; base images by digest. Automated vulnerability and malware scanning on every build as the floor.
8. **Put a review gate on new dependencies**: before adding — maintenance health, install scripts, transitive weight, does 20 lines of code replace it? Additions and upgrades reviewed as code (lockfile diffs are diffs).
9. **Harden the pipeline**: per-job scoped tokens, no secrets to fork-triggered workflows, workflow-file changes require code-owner review, publish rights behind 2FA and provenance/trusted publishing where the ecosystem offers it.
10. **Write and rehearse the leak playbook**: rotate → assess blast radius from audit logs (what did this credential touch since when?) → hunt persistence (new keys minted? IAM changes?) → then clean mediums and fix the entry path (see production-debugging: stabilize first; root-cause-analysis for the class-fix after).

## Decision Tree

- If a secret is found anywhere it shouldn't be (repo, log, ticket, Slack) → rotate *now*, unconditionally — before investigating how it got there, before cleaning history. Exposure time is the attacker's budget.
- If you need to give a workload access to a cloud resource → platform identity (role/workload identity) first; minted short-lived token second; static key in a vault a distant third; static key in an env file only with a written reason and an expiry.
- If a credential must be shared across services "for simplicity" → don't; per-consumer copies cost minutes and buy attribution plus surgical revocation.
- If adding a dependency →
  - Does it run install scripts, touch the network, or want broad permissions? → elevated review.
  - Trivial functionality (left-pad-shaped)? → write it; the dependency's transitive risk outprices 20 lines (see abstraction-and-simplicity: dependencies are complexity).
  - Healthy, maintained, widely-used, genuinely hard to replicate? → adopt, pin, record why.
- If upgrading dependencies → lockfile diff reviewed like code; patch-version bumps of deep-transitive packages are precisely where takeover attacks live (recent to your training or not — the shape recurs). Automated PRs (Renovate-class) with CI + a human glance beat both extremes (never upgrade / auto-merge everything).
- If CI needs cloud access → OIDC federation with per-repo, per-environment trust conditions; a stored cloud key in CI settings is the previous decade.
- If a vendor webhook/SDK enters the codebase → its credentials scoped like yours, its calls egress-controlled where feasible (see web-security SSRF posture), its packages pinned like any other.
- If an internal package name exists → register/claim it in the public namespace or configure registry scoping — dependency confusion is a five-minute prevention or a very bad Tuesday.
- If rotation of some credential is "too risky to attempt" → that's the top of the backlog, not a reason to skip: build the dual-secret overlap path now, calmly, before an incident demands it at 3am (see judgment-under-uncertainty: buy reversal speed).

## Heuristics

- The best secret is the one that no longer exists; the second best expires in an hour.
- One secret, one consumer, one purpose — the moment a credential's audit log mixes two services, you've lost attribution and surgical revocation.
- `.env` in `.gitignore` is a seatbelt, not a strategy: the example file (`.env.example`) carries names-not-values, and the scanner catches the day someone forgets.
- Treat "last rotated" like "last backup tested": a date nobody knows is a control nobody has (see the backup-restore parallel in ci-cd/disaster thinking).
- Read the lockfile diff on upgrade PRs — five new transitive packages arriving with a patch bump of a date library is the alarm shape.
- Prefer packages that are boring, few, and heavy over many and micro: each dependency is a maintainer account that can be phished (see system-design boring-tech — same instinct).
- Pin by immutable reference everywhere: SHA for actions, digest for images, hash for packages — tags move, and "moved tag" is an attack primitive.
- Scanners are floors, not ceilings: SCA tools catch *known*-bad; the takeover that shipped an hour ago is caught by pinning, review, and egress alarms, not CVE feeds.
- A secret that reaches the client (mobile app, SPA bundle, browser) is published — design as if the attacker has it, because they do (see frontend: no privileged keys client-side; api-design: proxy privileged calls).
- New-dependency PRs deserve the question "what's our exit cost?" — the wrapper you write today (see abstraction-and-simplicity: thin adapters) is the migration you don't write later.
- Audit unused scopes quarterly: permissions accrete monotonically unless something prunes them, and every unused verb is free blast radius.

## Quality Checklist

- [ ] Secret inventory exists: location, scope, consumer, rotation date, leak-detection path per credential.
- [ ] All secrets in a manager; repos hold references; runtime injection only.
- [ ] Static credentials replaced by platform identity everywhere the platform allows.
- [ ] Per-consumer, least-privilege scoping; expiries set where supported.
- [ ] Secret-scanning in pre-commit and CI, block-on-find; history scanned once, findings rotated.
- [ ] Log/error-tracker redaction for tokens, auth headers, secret-shaped fields.
- [ ] Lockfiles with integrity hashes enforced in CI; actions SHA-pinned; images digest-pinned.
- [ ] New-dependency review gate; upgrade PRs show reviewed lockfile diffs.
- [ ] CI: per-job token scopes, OIDC to cloud, fork PRs secret-less, workflow changes owner-reviewed.
- [ ] Leak playbook written, and rotation of the scariest credential rehearsed within the last quarter.

## Failure Modes

- **Rotation postponed after exposure**: "it was only in the private repo for an hour, and we force-pushed" — forks, clones, CI caches, and scanner bots don't attend your force-push; the key is burned and the clock is running.
- **The god credential**: one org-admin token powering CI, deploys, and three cron jobs — leaks somewhere eventually, and revocation means an outage, so revocation waits, so the attacker doesn't.
- **Secrets laundered through telemetry**: the auth header logged at debug level, the request body in the error tracker, the connection string in the crash dump — the vault immaculate, the logs a credential buffet (see observability scrubbing).
- **Floating-range roulette**: `^1.2.3` across the tree, no lockfile enforcement — the build that works today runs different code tomorrow, and one maintainer takeover away from running hostile code with prod credentials.
- **Tag-pinned CI actions**: `uses: some-action@v2` — v2 is a pointer someone else controls; when it moves maliciously, your pipeline exfiltrates its own environment on the next push.
- **Dependency confusion unclaimed**: internal package `acme-utils` unregistered publicly; a resolver misconfiguration later, the public `acme-utils` (malicious, version 99.9.9) wins the version race inside your build.
- **Scanner-as-strategy**: SCA green, therefore safe — the feed knows yesterday's CVEs, not this morning's takeover; pinning and review were the actual controls, and they were skipped because the dashboard was green.
- **The unrotatable secret**: two years old, wired into everything, rotation "too risky" — which is precisely the state the leak finds it in; the war-room rotation then costs 100× the calm dual-secret migration that kept getting deprioritized.

## Edge Cases

- **Secrets in build artifacts**: bundlers inline env vars — the "server-side" key baked into the JS bundle, the API token in the Docker layer (`docker history` shows all) — audit what the *artifact* contains, not what the source intends; multi-stage builds and runtime injection are the fixes.
- **The fork/CI trust hole**: workflows triggered by fork PRs must never see secrets — `pull_request_target` misuse is a recurring breach shape; test untrusted code with zero-privilege jobs, gate privileged steps on the merged commit.
- **Git history archaeology**: rotating the found secret handles the live risk; the history rewrite (filter-repo/BFG) is optional hygiene for private repos and near-pointless for anything once-public — budget accordingly.
- **Vendored and copy-pasted code**: the dependency you inlined to "avoid supply-chain risk" no longer receives security updates — vendoring trades takeover risk for staleness risk; if you vendor, you own the CVE watch (see legacy-migrations: owned forks age).
- **Machine-to-machine in the browser era**: OAuth client secrets in native/mobile apps are decorative (extractable) — PKCE flows exist for exactly this; "confidential client" is a server-only concept (see authentication).
- **Secrets in AI-era surfaces**: prompts, fine-tuning data, and agent tool-configs are new logging paths for old leaks — the API key pasted into a prompt is a key in a third party's storage; the same scrubbing discipline extends to LLM telemetry (see agents tool-permission scoping; prompt-engineering).
- **Emergency break-glass access**: least privilege needs an override path for real incidents — pre-provisioned, sealed, heavily audited, auto-expiring; without it, incidents route through credential-sharing over Slack, which is worse than the exception path you refused to design.
- **The departing employee**: personal PATs powering team automation die with the account (or worse, don't) — service accounts for service work; the offboarding checklist runs the credential inventory, which is another reason the inventory exists.

## Tradeoffs

- **Security vs velocity on dependency review**: a heavyweight gate on every `npm install` and teams route around it (the copy-paste, the personal fork); calibrate — elevated review for install-scripts/network/new-maintainers, lightweight for the boring center, automated for patch bumps *with* lockfile-diff eyes.
- **Pinning vs freshness**: hard pins mean you choose when code changes (good) and that security patches wait for you (bad) — the resolution is pins *plus* automated upgrade PRs on a short cadence, not loose ranges; staleness is a managed queue, not a default.
- **Centralized secrets manager vs single point of failure**: the vault concentrates risk and audit; its own availability and access controls become critical path (see system-design: the config service that can down everything) — worth it, but treat the manager as tier-zero infrastructure.
- **Short-lived tokens vs operational complexity**: hourly credentials shrink exposure windows and add minting infrastructure, clock-skew edges, and refresh failure modes (see async-processing retry thinking) — the complexity is front-loaded and amortizes; the exposure risk compounds.
- **Attribution granularity vs credential sprawl**: per-consumer keys multiply inventory rows — manageable with automation, unmanageable by hand; the inventory-and-manager investment is what makes least privilege operationally honest.
- **Vendor SDK convenience vs supply-chain surface**: the official SDK is 40 transitive packages; the raw API call is 30 lines (see api-design) — for one endpoint, write the call; for deep integration, take the SDK and pin it. Decide per depth-of-use, not per habit.

## Optimization Strategies

- Drive static-secret count as a metric: inventory size trending down quarter over quarter — every conversion to platform identity permanently deletes a failure mode; celebrate deletions like features (see first-principles: deletions ship too).
- Automate rotation on a schedule for whatever must stay static — scheduled rotation is the rehearsal, and the automation is the playbook executing itself; the incident-day difference is minutes vs meetings.
- Wire egress monitoring on build and runtime environments: the compromised package's exfiltration is a network event (see observability) — unexpected destinations from CI runners are a five-alarm signal with near-zero false-positive cost.
- Adopt provenance where ecosystems offer it (signed builds, trusted publishing, SLSA-shaped attestation) — verifying *who built this artifact from what source* closes the gap scanners can't.
- Run a quarterly "leak drill": plant a canary token, verify the scanner catches it pre-commit, rotate a real credential end-to-end, time it — the drill's timing *is* your incident-response forecast (see planning-and-estimation: reference class from rehearsal).
- Keep a dependency budget per service: additions require a removal or a reason — the graph that only grows is the attack surface that only grows (see abstraction-and-simplicity: the accretion default).

## Self Review

- Could I list every secret this system uses, and would the list say when each was last rotated?
- For the credential I just created: what's the *smallest* scope that does the job — and is that what I granted?
- If this key leaked right now: what could an attacker do, how would I know, and how long until it's dead?
- What does my lockfile diff say on this upgrade — did I read it, or did green CI read it for me?
- Are my CI actions and base images pinned to immutable references, or to names someone else controls?
- Where would this secret appear if the code threw an exception mid-request — and have I checked the error tracker's scrubbing, or assumed it?
- Which credential am I afraid to rotate — and what's the plan that retires that fear?
- Does anything privileged reach a client bundle, a prompt, or a log — the three places teams forget are "storage"?

## Examples

**1. The pushed key, handled by reflex.**
A developer pushes a commit containing a live cloud key to a public repo; pre-commit scanning was skipped via `--no-verify` under deadline pressure. The playbook runs in order: key rotated within 4 minutes (before the "how did this happen" conversation); audit logs pulled — the key was used from an unknown IP *90 seconds* after push (scanner bots are that fast), one S3 list call, denied by the key's read-only-single-bucket scope. Least privilege turned a breach into a log line. Follow-ups: history rewrite skipped (public = burned regardless), `--no-verify` disabled org-wide in favor of a fast scanner (the class fix — the bypass existed because the check was slow; see root-cause-analysis: fix the reason the guardrail was bypassed).

**2. The patch bump that wasn't.**
Renovate opens a routine PR: a date-formatting library, 2.4.1 → 2.4.2. The lockfile diff shows the alarm shape — three *new* transitive packages, one with a fresh install script. Review pause; upstream check: the maintainer's account shows a new publisher added days earlier; the ecosystem's advisory lands 26 hours later — account takeover, exfiltrating env vars at install. The team was never exposed: `npm ci` + hash-checked lockfile meant nothing unreviewed ever ran, and the reviewer read the diff because the process said lockfile diffs are code. The scanner (CVE-feed-based) flagged it a day after the human did.

**3. Deleting the deploy keys entirely.**
Legacy CI: a stored cloud admin key in repo settings, shared by build, deploy, and a nightly cron — unrotated for 20 months ("too wired-in"). Migration: OIDC federation from CI to cloud with per-repo, per-environment trust policies; three scoped roles (build: push to registry; deploy: that service's infra only; cron: one bucket, read-write). The static key is deleted, not vaulted — the leak class now *cannot occur*. Bonus discovered in the audit: the old key's permissions included IAM write; any CI compromise for 20 months could have minted persistent access. The migration took two days; it had been "too risky" for two years (see judgment-under-uncertainty: the unrotatable secret is the top of the backlog).

**4. Dependency confusion, prevented for the cost of lunch.**
Internal packages named `acme-core`, `acme-auth` live on a private registry; nothing claims those names publicly. A security review flags the shape: one resolver misconfiguration (a laptop, a new CI image, a default registry fallback) and the public namespace wins with a higher version. Fix: public names claimed with stub packages, registry scoping enforced (`@acme/*` → private only) in the shared config, and a canary — the stubs report any download with requester metadata. Eight months later the canary fires from a contractor's misconfigured machine: the hole existed; it was just plugged with a tombstone instead of exploited (see web-security: attacks are loud if you've placed the microphone).

## Evaluation Rubric

Score 1–10:

- **1–2**: Secrets in repos and logs; shared god-credentials, never rotated; floating dependency ranges without lockfile enforcement; CI holds admin keys and runs tag-pinned actions on fork PRs.
- **3–4**: A secrets manager exists but env files and Slack-shared keys persist; scanning advisory-only; lockfiles present but diffs unread; rotation theoretical.
- **5–6**: Secrets centralized with per-consumer least-privilege scoping; pre-commit + CI scanning block on find; lockfiles and SHA-pinning enforced; new dependencies gated; rotation-first reflex on exposure.
- **7–8**: Full checklist: platform identity replacing static keys, telemetry scrubbing verified, OIDC-federated CI with per-job scopes, upgrade diffs reviewed, playbook rehearsed with timed drills.
- **9–10**: Additionally: static-secret count measurably shrinking, scheduled automated rotation as the standing rehearsal, egress monitoring on build/runtime, provenance verification adopted, dependency-confusion canaries placed — and at least one incident on record where scoping and pinning demonstrably turned an attack into a non-event.
