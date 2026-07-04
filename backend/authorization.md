# Authorization

## Purpose

Design permission systems — RBAC, ABAC, relationship-based access, multi-tenant isolation — that fail closed, live in one enforceable place, and don't rot into an unauditable pile of `if user.role == "admin"` checks.

## When to use

- Adding roles, permissions, sharing, or team features to a product.
- Any endpoint that fetches or mutates a resource by ID (the IDOR surface).
- Building multi-tenant systems where tenant data must never cross.
- Reviewing code where access decisions appear inline in handlers.
- Migrating from a two-role system ("admin"/"user") that customers have outgrown.

## Goals

- Every access decision is made in one architectural layer, deny-by-default.
- Object-level checks exist everywhere object IDs are accepted — zero IDOR surface.
- The permission model is explainable in one table a PM can read.
- Adding a new role or permission doesn't require touching 40 call sites.

## Inputs

- The access matrix: actors × actions × resources, from product requirements (draw it even if nobody asks).
- Tenancy model: single-tenant, multi-tenant shared schema, or hybrid.
- Sharing requirements: is access role-shaped ("editors can edit") or relationship-shaped ("people I shared this doc with")?
- Compliance/audit requirements for privileged actions.
- Existing enforcement points: middleware, ORM scopes, API gateway.

## Outputs

- The access matrix document (roles/relationships × actions × resource types).
- A single policy module/service where all decisions route (`can(actor, action, resource)`).
- Enforcement placement map: which layer enforces what (route guard, service check, query scoping, DB RLS).
- Test suite: the deny matrix — assertions that wrong-tenant, wrong-owner, wrong-role access fails.
- Audit log design for privileged operations.

## Expert Mental Model

- **Authorization is a function: `can(actor, action, resource) → allow/deny`.** Everything else — roles, policies, scopes — is just how you compute that function. If you can't point at the one place this function lives, you don't have an authz system, you have authz folklore scattered across handlers.
- **Route-level checks are not object-level checks.** "Is this user logged in and an editor?" says nothing about "is this THEIR document 123?" IDOR — fetching someone else's object by guessing IDs — is the most common real-world authz hole because teams stop at route guards.
- **The UI is a suggestion; the server is the law.** Hiding a button is UX. Every enforcement decision must exist server-side; assume attackers call endpoints directly with crafted IDs.
- **Deny by default means the absence of a rule is a 403.** Systems that "allow unless denied" leak every time someone adds an endpoint and forgets the check. The framework should make forgetting impossible (unauthorized-by-default middleware, lint rule, or type-level requirement).
- **Model shape follows question shape.** "Can editors publish?" → roles (RBAC). "Can users see documents in their region during business hours?" → attributes (ABAC). "Can Bob see the doc Alice shared with him via a group?" → relationships (ReBAC/Zanzibar). Forcing sharing semantics into roles creates the role-explosion death spiral.
- **Tenancy is authorization's load-bearing wall.** In multi-tenant systems, the tenant check is not one rule among many — it's a structural invariant that belongs in query scoping and, ideally, database row-level security as a second layer.

## Workflow

1. **Write the access matrix first.** Rows: roles/relationships. Columns: action × resource type. Cells: allow/deny/conditional. Ambiguities you find here are product decisions — cheaper now than as CVEs.
2. **Classify the model shape**: RBAC, ABAC, ReBAC, or layered combination (common: RBAC for app-wide capabilities + ReBAC for per-resource sharing + tenant scoping underneath everything).
3. **Choose the enforcement architecture.** One policy module with a `can()` API; route middleware for coarse checks; service-layer `can()` calls for object-level; ORM default scopes or repository methods for tenant filtering; DB row-level security as belt-and-braces where stakes justify it.
4. **Make the default deny.** Configure the router/framework so a handler without an explicit authz declaration fails closed or fails CI.
5. **Implement object-level checks as data access, not post-filtering.** Prefer `WHERE tenant_id = ? AND id = ?` (not-found for foreign objects) over fetch-then-check where feasible — it can't be forgotten on new query paths.
6. **Decide the 403 vs 404 policy** per resource class (leak existence or not) and apply uniformly.
7. **Wire audit logging** for privileged actions: who, what, target, when, from where — written in the same transaction as the action where feasible.
8. **Write the deny matrix tests**: for each endpoint accepting an ID — wrong tenant, wrong owner, insufficient role, expired/revoked grant. Parameterize; this is a matrix, not bespoke tests.
9. **Design the admin story deliberately**: support/impersonation access must be scoped, time-boxed, logged, and visible to the customer where appropriate — not a god-mode boolean.
10. **Plan cache invalidation for permission changes**: revoked access must take effect within a stated SLA (seconds for sessions-based recheck, or短 short-TTL permission caches).

## Decision Tree

- If permissions are the same for every user of a given role, and resources aren't individually shared → RBAC. Keep roles ≤7 or so; more means the model is wrong.
- Else if access depends on resource/user attributes (region, plan tier, time, clearance) → ABAC via policy rules over attributes; keep the attribute set small and authoritative.
- Else if users share individual resources with users/groups, or access derives from hierarchy (folder → doc, org → team → member) → ReBAC. Build a relationship store (`subject, relation, object` tuples) or adopt an engine (SpiceDB/OpenFGA-style) rather than faking it with role rows.
- Else if it's a mix (it usually is) → tenant scoping at the data layer + RBAC for capabilities + ReBAC for sharing, composed in one `can()` facade.

Role design:
- If you're adding a role that's "X but without Y" (`admin_but_not_billing`) → stop; switch from roles-as-identity to roles-as-permission-bundles: check `can(user, "billing.view")`, never `user.role == "admin"`.
- If customers ask for custom roles → permissions become first-class named strings; roles become customer-editable sets of them.

403 vs 404:
- If resource IDs are guessable or existence itself is sensitive (multi-tenant business data) → 404 for both missing and forbidden.
- Else (collaborative tools where "ask for access" is a feature) → 403 with a request-access affordance.

## Heuristics

- Grep test: `role ==` or `isAdmin` string-matched in handlers is the smell; permission names (`can("invoice.export")`) are the fix. Roles are assigned, permissions are checked.
- Every function that takes a resource ID either takes the actor too, or is provably behind something that did the check. No third option.
- Tenant ID comes from the session/token, never from the request body or URL — the URL's tenant is what the user claims; the token's tenant is what they are.
- Composite indexes should lead with `tenant_id`; if a query doesn't include tenant scope, it should look wrong in review.
- Permission checks are cheap; permission *listing* ("what can this user see?") is the expensive query — design list endpoints around scoped queries, not check-per-row.
- Count your conditionals: if `can()` is called with the same actor+resource 5 times in one request, memoize per-request, don't cache cross-request without an invalidation story.
- New endpoint checklist item: "which authz declaration covers this?" should be answerable in one sentence.
- If explaining who-can-what requires reading code, the model has already failed its audit.
- Privilege escalation paths hide in write endpoints: can a user edit their own `role` field via a generic PATCH? Mass-assignment allowlists are authz controls.
- Invitation, transfer-ownership, and "leave team" flows are where relationship models break — walk them explicitly.

## Quality Checklist

- [ ] One policy module; zero inline role comparisons in handlers.
- [ ] Deny by default: unannotated routes fail closed (verified by a test hitting a fresh route).
- [ ] Every ID-accepting endpoint has object-level authorization (tenant/ownership), enforced at query scope where possible.
- [ ] Deny matrix tests: wrong tenant, wrong owner, wrong role, revoked grant — per resource type.
- [ ] Mass-assignment protection on role/permission/tenant fields.
- [ ] 403/404 policy consistent per resource class.
- [ ] Privileged actions audited with actor, target, and origin.
- [ ] Permission revocation takes effect within a stated, tested SLA.
- [ ] Admin/support access is scoped, time-limited, and logged — no shared god accounts.
- [ ] The access matrix document exists and matches the code (spot-check 5 cells).

## Failure Modes

- **IDOR**: route guard passes (user is logged in), object check missing — `GET /invoices/12345` returns another company's invoice. The single most common serious web vulnerability in practice.
- **Scattered checks drifting**: three handlers implement "can edit project" three ways; a rule change updates two. The third is now a vulnerability with no failing test.
- **Role explosion**: `admin`, `super_admin`, `regional_admin_readonly`... Each new business nuance mints a role; conditionals multiply; nobody can answer who-can-what.
- **Allow-by-default frameworks**: authz as opt-in decorator; the one forgotten decorator is the breach.
- **Client-enforced authz**: API returns everything, UI filters. Attacker reads the network tab.
- **Post-filter pagination leak**: fetch 50 rows, filter to what's permitted, return 3 — page sizes and total counts leak existence and make pagination lie. Scope the query instead.
- **Confused deputy**: a privileged internal service performs actions on behalf of callers without propagating the original actor — background jobs and webhooks bypass every check. Propagate actor identity through async boundaries.
- **Stale grants**: removed team member's session/cached permissions keep working for hours because nothing rechecks.

## Edge Cases

- **Ownership transfer**: mid-transfer, who can act? Define the transaction boundary; two owners or zero owners are both bugs.
- **The last admin**: prevent removing/demoting the final admin of a tenant, or the tenant bricks itself (support ticket generator).
- **Cross-tenant actors**: agencies/contractors legitimately in many tenants — session must carry *current* tenant context explicitly; "all my tenants" queries are where isolation dies.
- **Resource creation authz**: `can(user, "create", Project)` has no object yet — parent-scoped check (`create-in-workspace-X`) — novices check nothing because "there's no object."
- **Soft-deleted resources**: do viewers see them? Do admins? Restore permission ≠ delete permission.
- **Public/anonymous access**: "public link" is an authz grant to the anonymous principal — model it as a grant (revocable, auditable, expirable), not a `public: true` boolean shortcut that bypasses the policy layer.
- **Hierarchies with exceptions**: "everyone in folder except Bob" — negative grants complicate everything; push back on the requirement before implementing deny-tuples.
- **Async jobs and exports**: a report generated with yesterday's permissions delivered today — decide evaluation time (at request vs at delivery) per feature.

## Tradeoffs

- **Query-scoping vs fetch-then-check**: scoping (`WHERE tenant_id=?`) can't be forgotten and paginates correctly, but complex relationship rules don't fit SQL cleanly; fetch-then-check centralizes logic but risks unfiltered query paths. Common resolution: scoping for tenancy/ownership, `can()` for fine-grained action rules.
- **Centralized policy engine vs in-app module**: an engine (OPA/SpiceDB-style) gives one source of truth across services at the cost of a network dependency in the hot path and operational burden. In-app module is fine until ≥3 services need identical decisions.
- **Expressiveness vs auditability**: ABAC policies can encode anything, and then nobody can enumerate who has access. RBAC is dumber and auditable. Regulated contexts often prefer dumber.
- **DB row-level security**: strongest tenant guarantee, but adds migration complexity and can surprise ORMs. Worth it when a cross-tenant leak is existential (fintech, health); overhead when it isn't.
- **Caching permission decisions**: caching makes checks free and revocation slow. Cache with short TTLs (≤60 s) or version-stamped invalidation; never cache across privilege changes silently.

## Optimization Strategies

- Load actor grants once per request into a context object; individual `can()` calls become in-memory lookups.
- For list views, compile permissions into the query (join against grants/relationship tuples) instead of N checks.
- Denormalize hot relationship paths (e.g., materialized `document_accessors`) with event-driven maintenance when ReBAC traversal becomes the latency driver — keep the tuple store as source of truth.
- Add a `WHY` debug mode to `can()` returning the matched rule — cuts authz-support tickets and de-risks refactors.
- Property-based tests: random (actor, resource) pairs across tenants asserting cross-tenant access is never granted — catches whole classes the matrix tests miss.

## Self Review

- Can I point to the single module where `can()` lives, and is there any handler that decides access without it?
- For each endpoint taking an ID: where exactly is the object-level check? (Answer per endpoint, not "the middleware handles it.")
- If I create two tenants and one user in each, do my tests prove every resource type is invisible cross-tenant — including via list endpoints, search, and exports?
- Can a user modify their own role, tenant, or permissions through any generic write path?
- When a grant is revoked, what is the worst-case seconds-until-enforced? Is that written down?
- Do background jobs and webhooks carry and check the original actor?
- Could a security auditor reconstruct who-can-what from documentation alone?

## Examples

**1. Killing an IDOR class structurally.**
Found: `GET /api/documents/:id` does `Document.find(id)` after a login check. Fix is not adding `if doc.user_id != current_user.id` in this handler — it's introducing `current_user.documents.find(id)` (scoped repository) as the only sanctioned lookup, deprecating raw `Document.find` via lint rule, and adding the parameterized deny test (`other_tenant_doc → 404`) across all 14 ID-accepting endpoints. Three more IDORs surface immediately from the test sweep.

**2. Escaping role explosion.**
B2B product at 11 roles (`admin_readonly`, `billing_admin`, ...) with a sales request for #12. Redesign: define ~25 permission strings (`members.invite`, `billing.view`, `reports.export`...), convert roles to named permission sets, check only permissions in code, then ship customer-defined custom roles as an enterprise feature. Code churn: replace every `role in [...]` with one `can()` call. The sales request becomes configuration, not engineering.

**3. Sharing that actually needed ReBAC.**
Requirement: "share a folder with a group; docs inherit; guests see only shared items." Attempt #1 as RBAC (roles per folder) collapses combinatorially. Redesign as relationship tuples: `(user:bob, member, group:design)`, `(group:design, viewer, folder:42)`, `(folder:42, parent, doc:99)`; `can(bob, view, doc:99)` = graph walk. List views answered by joining tuples, not checking per row. 403 vs 404 decision: 404 outside shares, with "request access" only where a share once existed.

**4. Confused deputy in an export job.**
Bug report: a member's scheduled CSV export contains admin-only salary columns. Root cause: the export worker runs as a service account with full DB access; permissions were checked at scheduling, columns added later. Fix: persist the requesting actor on the job, re-evaluate `can()` at execution time against current grants, and add the regression test "downgraded user's pending exports respect new permissions."

## Evaluation Rubric

Score 1–10:

- **1–2**: Inline role string checks; no object-level authorization; UI-only enforcement; cross-tenant reads possible by ID guessing.
- **3–4**: Route-level RBAC consistent, but ID endpoints unscoped in places; no deny tests; role explosion underway.
- **5–6**: Central policy module; tenant scoping at query layer; object checks on major endpoints; deny tests exist but matrix incomplete; audit logging partial.
- **7–8**: Full checklist passes; deny matrix parameterized across resource types; mass-assignment guarded; revocation SLA tested; admin access scoped and logged.
- **9–10**: Additionally: structural prevention (scoped repositories/RLS, fail-closed routing verified by test); property-based cross-tenant tests; `can()` explain mode; access matrix doc kept in sync and used by support/PM; model shape (RBAC/ReBAC split) matches question shape with written rationale.
