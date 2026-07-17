---
name: auth
description: "Use when building login/signup, OAuth/OIDC/SSO, sessions vs JWTs, or any code touching tokens/passwords/reset — plus roles, permissions, sharing, multi-tenant isolation, and resource-by-ID (IDOR) enforcement — RBAC, ABAC, ReBAC, fail-closed."
---

# Auth: Authentication & Authorization

## Purpose

Design and implement the two halves of access control: **authentication** — verifying identity (sessions, tokens, passwords, OAuth/OIDC, MFA) without the subtle lifecycle flaws that make auth the highest-severity bug class in most codebases — and **authorization** — permission systems (RBAC, ABAC, relationship-based access, multi-tenant isolation) that fail closed, live in one enforceable place, and don't rot into an unauditable pile of `if user.role == "admin"` checks.

## When to use

- Building login/signup, service-to-service auth, or "Sign in with Google/GitHub."
- Adding roles, permissions, sharing, team features, or multi-tenant isolation.
- Any endpoint that fetches or mutates a resource by ID (the IDOR surface).
- Reviewing code that touches tokens, sessions, passwords, reset flows, or inline access checks.
- Deciding sessions vs JWTs, cookie vs header transport, or migrating from a two-role system customers have outgrown.

## Goals

- Credentials cannot be stolen at rest (hashing) or in transit; sessions revocable server-side in under a minute.
- Every auth failure path uniform enough to prevent account enumeration.
- Every access decision made in one architectural layer, deny-by-default; zero IDOR surface.
- The permission model explainable in one table a PM can read; adding a role doesn't touch 40 call sites.
- Flows survive the real world: retries, multiple tabs, expired tokens mid-request, clock skew.

## Inputs

- Client types: browser SPA, server-rendered web, native mobile, CLI, other services.
- Threat context: consumer app, B2B with SSO requirements, internal tool; compliance constraints (SOC2, HIPAA).
- The access matrix: actors × actions × resources, from product requirements (draw it even if nobody asks).
- Tenancy model and sharing requirements: is access role-shaped ("editors can edit") or relationship-shaped ("people I shared this doc with")?
- Session requirements: lifetime, concurrent-session policy, revocation urgency; existing identity infrastructure (IdP, SSO).

## Outputs

- Chosen mechanism per client type with written rationale; token/session lifetime table with rotation and revocation paths.
- Flow diagrams for login, logout, refresh, password reset, email verification.
- The access matrix document; a single policy module where all decisions route (`can(actor, action, resource)`).
- Enforcement placement map (route guard, service check, query scoping, DB RLS) and audit log design for privileged actions.
- Test plan covering the deny paths — authentication and authorization both — not just the allow paths.

## Expert Mental Model

**Authentication:**

- **Authentication is a state-management problem wearing a security costume.** Most auth bugs are lifecycle bugs: tokens that outlive their sessions, resets that don't invalidate old sessions, logout that only clears the client.
- **Default to boring: server-side sessions in httpOnly cookies for first-party web.** JWTs are a tool for stateless verification across trust boundaries, not an upgrade to sessions. Every JWT-as-session design must answer "how do I revoke this in under a minute?" — and the honest answers (denylist, short TTL + refresh) reinvent server state.
- **The deny path is the product.** Login success is trivial; the security lives in what happens on wrong password, expired token, reused refresh token, and reset-link replay. Enumerate deny paths first.
- **Anything the browser's JavaScript can read, an XSS can steal.** Token storage location (httpOnly cookie vs localStorage) is decided by this single sentence.
- **Uniformity defeats enumeration.** Response text, status code, AND timing must be identical for "user doesn't exist" and "wrong password."

**Authorization:**

- **Authorization is a function: `can(actor, action, resource) → allow/deny`.** Roles, policies, scopes are just how you compute it. If you can't point at the one place this function lives, you have authz folklore scattered across handlers, not an authz system.
- **Route-level checks are not object-level checks.** "Is this user logged in and an editor?" says nothing about "is this THEIR document 123?" IDOR — fetching someone else's object by guessing IDs — is the most common real-world authz hole because teams stop at route guards.
- **The UI is a suggestion; the server is the law.** Hiding a button is UX. Assume attackers call endpoints directly with crafted IDs.
- **Deny by default means the absence of a rule is a 403.** Systems that "allow unless denied" leak every time someone adds an endpoint and forgets the check. The framework should make forgetting impossible.
- **Model shape follows question shape.** "Can editors publish?" → roles (RBAC). "Can users see documents in their region during business hours?" → attributes (ABAC). "Can Bob see the doc Alice shared via a group?" → relationships (ReBAC). Forcing sharing semantics into roles creates the role-explosion death spiral.
- **Tenancy is authorization's load-bearing wall.** The tenant check is not one rule among many — it's a structural invariant that belongs in query scoping and, ideally, database row-level security as a second layer.
- **Auth bugs are silent — both halves.** A broken check doesn't throw; it succeeds for the wrong person. This inverts normal testing instinct: you must write tests that assert failure.

## Workflow

**Authentication:**

1. **Inventory client types and pick transport per type.** First-party browser → httpOnly, Secure, SameSite=Lax session cookie. Native mobile → refresh token in secure OS keystore. Service-to-service → mTLS or short-lived signed tokens, never long-lived shared secrets.
2. **Choose session mechanism and write down the revocation answer before proceeding.** Server-side session store (default) or JWT access + rotating refresh (when statelessness across services is genuinely required).
3. **Set lifetimes.** Access JWT: 5–15 min. Session idle timeout: 15 min–24 h by sensitivity. Refresh: days–weeks, single-use with rotation and family revocation on reuse (the theft alarm).
4. **Implement password handling.** argon2id (or bcrypt cost ≥12) tuned to ~100–250 ms on production hardware; normalize (NFC) before hashing; don't truncate silently (bcrypt's 72-byte limit); check breached-password lists on set.
5. **Build the reset flow as its own security surface.** Single-use token, ≥128 bits entropy, stored hashed, 15–60 min expiry; on success, invalidate all sessions and outstanding reset tokens; respond identically whether or not the email exists.
6. **Rotate session ID on privilege change** — login, password change, role elevation (kills session fixation).
7. **If integrating OAuth/OIDC:** authorization code flow with PKCE, always. Validate `state`, exact-match `redirect_uri`, and `iss`/`aud`/`exp`/`nonce` on ID tokens; never use an ID token as an API credential or vice versa.
8. **Add MFA:** TOTP/passkeys first, WebAuthn where possible, SMS only as legacy fallback; design recovery (backup codes) at the same time — recovery is where MFA gets bypassed.

**Authorization:**

9. **Write the access matrix first.** Rows: roles/relationships. Columns: action × resource type. Ambiguities found here are product decisions — cheaper now than as CVEs.
10. **Classify the model shape**: RBAC, ABAC, ReBAC, or the common layered combination (RBAC for app-wide capabilities + ReBAC for per-resource sharing + tenant scoping underneath).
11. **Choose the enforcement architecture.** One policy module with a `can()` API; route middleware for coarse checks; service-layer `can()` for object-level; ORM default scopes for tenant filtering; DB row-level security as belt-and-braces where stakes justify it. Configure the router so an unannotated handler fails closed or fails CI.
12. **Implement object-level checks as data access, not post-filtering.** Prefer `WHERE tenant_id = ? AND id = ?` (not-found for foreign objects) over fetch-then-check — it can't be forgotten on new query paths. Decide the 403-vs-404 policy per resource class and apply uniformly.
13. **Wire audit logging** for privileged actions — who, what, target, when, from where — in the same transaction as the action where feasible. Design the admin/support story deliberately: scoped, time-boxed, logged; not a god-mode boolean.
14. **Write the deny matrix tests**: for each ID-accepting endpoint — wrong tenant, wrong owner, insufficient role, revoked grant; for auth flows — expired token, tampered token, `alg:none`, reused refresh, replayed reset link. Parameterize; this is a matrix, not bespoke tests. Plan cache invalidation so revoked access takes effect within a stated SLA.

## Decision Tree

Client transport:

- If first-party browser app → server session in httpOnly+Secure+SameSite=Lax cookie; CSRF protection on mutations; no tokens in localStorage.
- Else if native mobile → OAuth code+PKCE; refresh token in Keychain/Keystore; short-lived access token in memory.
- Else if third-party developers → API keys (hashed at rest, prefixed, e.g. `sk_live_`) or OAuth client credentials; scoped; ≥2 active keys per client for zero-downtime rotation.
- Else if your services call each other → workload identity (mTLS, cloud IAM, OIDC federation) with minutes-long tokens.
- Else if enterprise SSO demanded → SAML/OIDC via an abstraction; map IdP assertions to your internal session, never trust IdP session lifetime blindly.

Permission model:

- If permissions are uniform per role and resources aren't individually shared → RBAC. Keep roles ≤7; more means the model is wrong.
- Else if access depends on attributes (region, plan tier, time) → ABAC with a small, authoritative attribute set.
- Else if users share individual resources or access derives from hierarchy → ReBAC: relationship tuples (`subject, relation, object`) or an engine (SpiceDB/OpenFGA-style), not role rows faking it.
- Else (it's usually a mix) → tenant scoping at the data layer + RBAC for capabilities + ReBAC for sharing, composed in one `can()` facade.

Role design: adding a role that's "X but without Y" (`admin_but_not_billing`) → stop; switch to roles-as-permission-bundles: check `can(user, "billing.view")`, never `user.role == "admin"`. Customers asking for custom roles → permissions become first-class named strings; roles become customer-editable sets.

403 vs 404: if IDs are guessable or existence is sensitive (multi-tenant business data) → 404 for both missing and forbidden; else (collaborative tools) → 403 with a request-access affordance.

## Heuristics

- If your JWT design includes a revocation denylist checked on every request, you've built a session store with extra steps — use sessions.
- Hash anything that grants access: passwords, API keys, reset tokens, refresh tokens. The database WILL leak eventually.
- Access credential lifetime ≈ how long you can tolerate a stolen credential being valid. 5–15 minutes for JWTs is not paranoia. "Remember me" extends the refresh/session lifetime, never the access credential's.
- Timing uniformity: on unknown user, still run the password hash against a dummy hash — the 2 ms vs 200 ms difference is a working enumeration oracle.
- Never log tokens, passwords, or authorization headers — including error reporters and APM breadcrumbs. Grep your log pipeline for `Bearer ` today.
- Rate limit by (IP × account) pair, not IP alone (botnets) or account alone (lockout DoS against victims).
- Email change and password change are auth events: re-authenticate first, notify the old address, rotate sessions.
- Grep test: `role ==` or `isAdmin` in handlers is the smell; permission names (`can("invoice.export")`) are the fix. Roles are assigned, permissions are checked.
- Every function that takes a resource ID either takes the actor too, or is provably behind something that did the check. No third option.
- Tenant ID comes from the session/token, never from the request body or URL — the URL's tenant is what the user claims; the token's tenant is what they are.
- Composite indexes lead with `tenant_id`; a query without tenant scope should look wrong in review.
- Privilege escalation hides in write endpoints: can a user edit their own `role` field via a generic PATCH? Mass-assignment allowlists are authz controls.
- Invitation, transfer-ownership, and "leave team" flows are where relationship models break — walk them explicitly.

## Quality Checklist

- [ ] Passwords hashed with argon2id/bcrypt at measured ~100–250 ms; session ID ≥128 bits from a CSPRNG; cookie httpOnly+Secure+SameSite.
- [ ] Logout invalidates server-side; reset flow single-use, expiring, hashed at rest, session-invalidating.
- [ ] Refresh token rotation with family revocation on reuse; session ID rotated on login and privilege change.
- [ ] Identical response body, status, and timing for existing vs non-existing accounts (login, reset, signup).
- [ ] OAuth: PKCE + `state` + exact `redirect_uri` match + full ID token validation (signature, alg allowlist, `iss`, `aud`, `exp`, `nonce`).
- [ ] One policy module; zero inline role comparisons in handlers; unannotated routes fail closed (verified by a test hitting a fresh route).
- [ ] Every ID-accepting endpoint has object-level authorization, enforced at query scope where possible.
- [ ] Deny matrix tests: wrong tenant, wrong owner, wrong role, revoked grant, expired/tampered/reused tokens, replayed reset links.
- [ ] Mass-assignment protection on role/permission/tenant fields; 403/404 policy consistent per resource class.
- [ ] Privileged actions audited; revocation SLA stated and tested; admin/support access scoped, time-limited, logged.
- [ ] The access matrix document exists and matches the code (spot-check 5 cells).

## Failure Modes

- **JWT-as-session with no revocation story** — compromise means waiting out the token or an emergency key rotation that logs out everyone.
- **Tokens in localStorage** — one XSS anywhere (including a compromised npm dependency) exfiltrates every user's session.
- **Client-side-only logout / reset that doesn't kill sessions** — stolen credentials survive the victim's defensive actions.
- **Accepting `alg: none` or mismatched algorithms** — verify against an allowlist of expected algorithms and keys, not whatever the token header claims.
- **Different error messages** ("no such user" vs "wrong password") — free enumeration oracle; also leaks via signup and reset flows.
- **Redirect URI validated by prefix** — `https://yourapp.com.evil.com` walks through; exact-match registered URIs only.
- **IDOR**: route guard passes, object check missing — `GET /invoices/12345` returns another company's invoice. The single most common serious web vulnerability in practice.
- **Scattered checks drifting**: three handlers implement "can edit project" three ways; a rule change updates two. The third is now a vulnerability with no failing test.
- **Role explosion**: each business nuance mints a role; conditionals multiply; nobody can answer who-can-what.
- **Post-filter pagination leak**: fetch 50 rows, filter to 3 — page sizes and total counts leak existence and pagination lies. Scope the query instead.
- **Confused deputy**: a privileged internal service acts on behalf of callers without propagating the original actor — background jobs and webhooks bypass every check.
- **Stale grants**: removed team member's cached permissions keep working for hours because nothing rechecks.

## Edge Cases

- **Concurrent refresh from multiple tabs**: naive reuse-detection logs the user out. Allow a short grace window (~10 s) where the previous token is accepted once, or serialize refresh via a shared worker.
- **Half-logged-in states**: MFA passed first factor, second pending — needs its own limited session type, not a full session with a flag.
- **Email case and unicode**: normalize on signup AND login identically, or users "lose" accounts; never block paste; never silently truncate passwords.
- **OAuth account linking**: provider email matches an existing local account — auto-linking without verified email enables takeover via attacker-controlled IdP accounts. Require verified email + explicit confirmation.
- **Deleted/disabled users with live sessions**: session validation must re-check account status, not just session existence.
- **Ownership transfer**: mid-transfer, who can act? Define the transaction boundary; two owners or zero owners are both bugs.
- **The last admin**: prevent removing the final admin of a tenant, or the tenant bricks itself.
- **Cross-tenant actors** (agencies, contractors): session must carry *current* tenant context explicitly; "all my tenants" queries are where isolation dies.
- **Resource creation authz**: `can(user, "create", Project)` has no object yet — parent-scoped check (`create-in-workspace-X`); novices check nothing because "there's no object."
- **Public links**: an authz grant to the anonymous principal — model as a grant (revocable, auditable, expirable), not a `public: true` boolean that bypasses the policy layer.
- **Async jobs and exports**: a report generated with yesterday's permissions delivered today — decide evaluation time (at request vs at delivery) per feature.

## Tradeoffs

- **Sessions vs JWTs**: sessions cost a store lookup but give instant revocation; JWTs skip the lookup but push you into short lifetimes, refresh machinery, and revocation compromises. One Redis GET is almost never the real bottleneck — choose sessions unless crossing trust boundaries.
- **Security vs friction**: constant re-auth trains users to autopilot through prompts. Spend friction budget on sensitive operations (step-up auth for payout changes), not uniformly.
- **Building vs buying**: auth providers remove implementation risk but add vendor coupling, per-MAU cost, and migration pain. Build on frameworks' vetted primitives; buy when the SSO/SAML/compliance matrix exceeds team capacity; never hand-roll crypto either way.
- **Lockout vs availability**: hard lockout hands attackers a DoS button. Prefer escalating delays + CAPTCHA + credential-stuffing detection.
- **Query-scoping vs fetch-then-check**: scoping can't be forgotten and paginates correctly, but complex relationship rules don't fit SQL cleanly. Common resolution: scoping for tenancy/ownership, `can()` for fine-grained action rules.
- **Centralized policy engine vs in-app module**: an engine gives one source of truth across services at the cost of a network hop and ops burden. In-app is fine until ≥3 services need identical decisions.
- **Expressiveness vs auditability**: ABAC can encode anything, and then nobody can enumerate who has access. RBAC is dumber and auditable. Regulated contexts often prefer dumber.
- **Caching permission decisions**: caching makes checks free and revocation slow. Short TTLs (≤60 s) or version-stamped invalidation; never cache across privilege changes silently.

## Optimization Strategies

- Cache session lookups in-process for a few seconds only if the revocation SLA tolerates it; otherwise optimize the Redis path.
- Use passkeys/WebAuthn to delete the password + phishing problem for returning users; keep password as fallback during adoption.
- Precompute risk signals at login (new device, new geo, impossible travel) and gate step-up MFA on them instead of always-on prompts.
- Load actor grants once per request into a context object; individual `can()` calls become in-memory lookups. For list views, compile permissions into the query (join against grants/tuples) instead of N checks.
- Denormalize hot relationship paths (materialized `document_accessors`) with event-driven maintenance when ReBAC traversal becomes the latency driver — tuple store stays source of truth.
- Add a `WHY` debug mode to `can()` returning the matched rule — cuts authz-support tickets and de-risks refactors.
- Property-based tests: random (actor, resource) pairs across tenants asserting cross-tenant access is never granted — catches whole classes the matrix tests miss.
- Standardize on one auth middleware; every hand-rolled "quick check" in a route handler is a future CVE.

## Self Review

- Can I revoke a specific user's access in under 60 seconds? Walk the exact mechanism.
- What can an attacker do with a stolen access token? a stolen refresh token? a database dump? Each answer bounded and written down.
- Do login, signup, and reset behave identically for existing and non-existing accounts — body, status, and time?
- Can I point to the single module where `can()` lives, and is there any handler deciding access without it?
- For each endpoint taking an ID: where exactly is the object-level check? (Answer per endpoint, not "the middleware handles it.")
- Do my tests prove every resource type is invisible cross-tenant — including list endpoints, search, and exports?
- Can a user modify their own role, tenant, or permissions through any generic write path?
- Do background jobs and webhooks carry and re-check the original actor?
- Did I write at least one test per deny path, asserting 401/403 (not just "doesn't 200")?
- Could a security auditor reconstruct who-can-what from documentation alone?

## Examples

**1. Choosing boring correctly.**
B2B SaaS, React SPA + Rails API, same domain. Team proposes JWTs in localStorage "for scalability." Expert choice: server sessions in httpOnly SameSite=Lax cookie, Redis store, 24 h idle timeout, CSRF token on mutations. Rationale recorded: one Redis GET per request is nothing at their scale; instant revocation required by enterprise customers; XSS blast radius contained. JWT complexity deferred until an actual cross-service boundary exists.

**2. Refresh rotation catching real theft.**
Mobile app: access JWT 10 min, refresh 30 days, rotate-on-use. Attacker exfiltrates a refresh token from a backup; uses it. Later the legitimate app refreshes with its now-stale token → server sees reuse of a consumed token → revokes the whole family, forces re-login, raises a security event with device metadata. Without rotation + reuse detection, that theft was invisible for 30 days.

**3. Killing an IDOR class structurally.**
Found: `GET /api/documents/:id` does `Document.find(id)` after a login check. Fix is not adding `if doc.user_id != current_user.id` in this handler — it's introducing `current_user.documents.find(id)` (scoped repository) as the only sanctioned lookup, deprecating raw `Document.find` via lint rule, and adding the parameterized deny test (`other_tenant_doc → 404`) across all 14 ID-accepting endpoints. Three more IDORs surface immediately from the test sweep.

**4. Escaping role explosion.**
B2B product at 11 roles (`admin_readonly`, `billing_admin`, ...) with a sales request for #12. Redesign: define ~25 permission strings (`members.invite`, `billing.view`, `reports.export`...), convert roles to named permission sets, check only permissions in code, then ship customer-defined custom roles as an enterprise feature. The sales request becomes configuration, not engineering.

**5. Confused deputy in an export job.**
Bug report: a member's scheduled CSV export contains admin-only salary columns. Root cause: the export worker runs as a service account with full DB access; permissions were checked at scheduling, columns added later. Fix: persist the requesting actor on the job, re-evaluate `can()` at execution time against current grants, and add the regression test "downgraded user's pending exports respect new permissions."

**6. OAuth integration review catch.**
PR adds "Login with Google": code flow, but no `state`, `redirect_uri` checked by prefix, and account auto-linked by email. Three findings — CSRF-able flow, open redirect to `yourapp.com.evil.com`, and takeover via unverified-email IdP accounts. All three are bug-bounty top-10 staples; none throw errors in testing.

## Evaluation Rubric

Score 1–10:

- **1–2**: Plaintext or fast-hash passwords; tokens in localStorage; no revocation; enumeration oracles everywhere; inline role checks; no object-level authorization; cross-tenant reads by ID guessing.
- **3–4**: bcrypt present but flows unspecified; logout client-side; JWT with no lifetime policy; route-level RBAC consistent but ID endpoints unscoped; no deny tests; role explosion underway.
- **5–6**: Sound mechanism choices with rationale; lifetimes defined; reset flow mostly correct; central policy module; tenant scoping at query layer; deny tests exist but matrix incomplete.
- **7–8**: Full checklist passes both halves: rotation with reuse detection, OAuth to spec, deny matrix parameterized across resource types, mass-assignment guarded, revocation SLA tested, admin access scoped and logged.
- **9–10**: Additionally: step-up auth for sensitive ops; passkey path; key-rotation runbook rehearsed; enumeration verified with timing measurements; structural prevention (scoped repositories/RLS, fail-closed routing verified by test); property-based cross-tenant tests; access matrix doc kept in sync and used by support/PM.
