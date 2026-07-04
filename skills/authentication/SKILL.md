---
name: authentication
description: "Use when building login/signup, adding service-to-service auth, integrating OAuth/OIDC/SSO, choosing sessions vs JWTs, or reviewing code touching tokens/sessions/passwords/reset."
---

# Authentication

## Purpose

Design and implement systems that verify identity — sessions, tokens, passwords, OAuth/OIDC, MFA — without introducing the subtle flaws that make auth the highest-severity bug class in most codebases.

## When to use

- Building login/signup for a web or mobile app.
- Adding service-to-service authentication.
- Integrating "Sign in with Google/GitHub/etc." or acting as an OAuth provider.
- Reviewing any code that touches tokens, sessions, passwords, or password reset.
- Deciding between sessions and JWTs, or between cookie and header transport.

## Goals

- Credentials cannot be stolen at rest (hashing) or in transit (transport + storage choices).
- Sessions can be revoked server-side, immediately, when compromise is suspected.
- Every auth failure path is uniform enough to prevent account enumeration.
- Auth flows survive the real world: retries, multiple tabs, expired tokens mid-request, clock skew.

## Inputs

- Client types: browser SPA, server-rendered web, native mobile, CLI, other services.
- Threat context: consumer app, B2B with SSO requirements, internal tool.
- Session requirements: lifetime, concurrent-session policy, remember-me, revocation urgency.
- Compliance constraints (SOC2, HIPAA) and existing identity infrastructure (IdP, SSO).

## Outputs

- Chosen mechanism per client type with written rationale (session cookie vs token, storage location).
- Token/session lifetime table: access lifetime, refresh lifetime, rotation policy, revocation path.
- Flow diagrams for: login, logout, refresh, password reset, email verification.
- Test plan covering the deny paths, not just the allow paths.

## Expert Mental Model

- **Authentication is a state-management problem wearing a security costume.** Most auth bugs are lifecycle bugs: tokens that outlive their sessions, resets that don't invalidate old sessions, logout that only clears the client.
- **Default to boring: server-side sessions in httpOnly cookies for first-party web.** JWTs are a tool for stateless verification across trust boundaries (services, third parties), not an upgrade to sessions. Every JWT-as-session design must answer: "how do I revoke this in under a minute?" — and the honest answers (denylist, short TTL + refresh) reinvent server state.
- **The deny path is the product.** Login success is trivial; the security lives in what happens on wrong password, expired token, reused refresh token, and reset-link replay. Experts enumerate deny paths first.
- **Anything the browser's JavaScript can read, an XSS can steal.** Token storage location (httpOnly cookie vs localStorage) is decided by this single sentence.
- **Auth bugs are silent.** A broken permission check doesn't throw; it succeeds for the wrong person. This inverts normal testing instinct: you must write tests that assert failure.
- **Uniformity defeats enumeration.** Response text, status code, AND timing must be identical for "user doesn't exist" and "wrong password."

## Workflow

1. **Inventory client types and pick transport per type.** First-party browser → httpOnly, Secure, SameSite=Lax session cookie. Native mobile → refresh token in secure OS keystore. Service-to-service → mTLS or short-lived signed tokens (OIDC federation), never long-lived shared secrets.
2. **Choose session mechanism.** Server-side session store (default) or JWT access + rotating refresh (when statelessness across services genuinely required). Write down the revocation answer before proceeding.
3. **Set lifetimes.** Access token/session idle timeout: 15 min–24 h by sensitivity. Access JWT: 5–15 min. Refresh: days–weeks, single-use with rotation. Absolute session cap for sensitive apps.
4. **Implement password handling.** argon2id (or bcrypt cost ≥12) tuned so hashing takes ~100–250 ms on production hardware. Normalize (NFC) before hashing, don't truncate silently (bcrypt's 72-byte limit — pre-hash or reject), check against breached-password lists on set.
5. **Implement refresh rotation with reuse detection.** Each refresh issues a new refresh token and invalidates the old; if an already-used refresh token is presented, revoke the entire token family (this is the theft alarm).
6. **Build the reset flow as its own security surface.** Single-use token, ≥128 bits entropy, stored hashed, 15–60 min expiry, tied to the email at issuance; on successful reset, invalidate all sessions and all outstanding reset tokens; respond identically whether or not the email exists.
7. **Rotate session ID on privilege change.** On login, on password change, on role elevation — new session identifier (kills session fixation).
8. **If integrating OAuth/OIDC:** authorization code flow with PKCE, always. Validate `state` (CSRF), validate `redirect_uri` by exact match, validate `iss`/`aud`/`exp`/`nonce` on ID tokens, and never use an ID token as an API access credential or vice versa.
9. **Add MFA in this order:** TOTP/passkeys first, WebAuthn where possible, SMS only as legacy fallback. Design MFA recovery (backup codes) at the same time — recovery is where MFA gets bypassed.
10. **Write the deny-path test matrix** (see Quality Checklist) and wire auth events (login, failure, reset, MFA change) into audit logging and alerting.

## Decision Tree

- If first-party browser app (SPA or SSR) → server session in httpOnly+Secure+SameSite=Lax cookie. CSRF protection on state-changing requests. Do not put tokens in localStorage.
- Else if native mobile app → OAuth code+PKCE against your auth server; refresh token in Keychain/Keystore; short-lived access token in memory.
- Else if third-party developers call your API → API keys (hashed at rest, prefixed for identification, e.g. `sk_live_`) or OAuth client credentials; scope them; support ≥2 active keys per client for zero-downtime rotation.
- Else if your services call each other → workload identity (mTLS, cloud IAM, OIDC federation) with minutes-long tokens; never a shared static secret in env vars if the platform offers identity.
- Else if enterprise customers demand SSO → SAML/OIDC via an abstraction (or product like WorkOS/Auth0); map IdP assertions to your internal session, never trust IdP session lifetime blindly.

Token storage in browser, if forced to handle tokens client-side:
- If you can use a cookie → httpOnly cookie, always.
- Else → in-memory only (variable, not localStorage), accept re-auth on refresh, mitigate with silent refresh via httpOnly refresh cookie.

## Heuristics

- If your JWT design includes a revocation denylist checked on every request, you've built a session store with extra steps — use sessions.
- Hash anything that grants access: passwords, API keys, reset tokens, refresh tokens. The database WILL leak eventually; design for that day.
- Lifetime rule of thumb: access credential lifetime ≈ how long you can tolerate a stolen credential being valid. 5–15 minutes for JWTs is not paranoia.
- "Remember me" extends the refresh/session lifetime, never the access credential's.
- Timing uniformity: on unknown user, still run the password hash against a dummy hash. The 2 ms vs 200 ms difference is a working user-enumeration oracle.
- Never log tokens, passwords, or authorization headers — including in error reporters and APM breadcrumbs. Grep your log pipeline for `Bearer ` today.
- Rate limit by (IP × account) pair, not IP alone (botnets) or account alone (lockout DoS against victims).
- Clock skew allowance for token validation: 30–60 s leeway on `exp`/`nbf`, no more.
- If two systems disagree about who the user is, the one closer to the credential wins; never forward identity as a plain header without a signature (or a trusted boundary that strips client-set copies).
- Email change and password change are auth events: re-authenticate first, notify the old address, rotate sessions.

## Quality Checklist

- [ ] Passwords hashed with argon2id/bcrypt at measured ~100–250 ms; no MD5/SHA-family anywhere near passwords.
- [ ] Session cookie: httpOnly, Secure, SameSite set; session ID ≥128 bits from a CSPRNG.
- [ ] Logout invalidates server-side, not just clears the cookie.
- [ ] Password reset invalidates all sessions and all prior reset tokens; token single-use and expiring.
- [ ] Refresh token rotation with family revocation on reuse.
- [ ] Identical response body, status, and timing for existing vs non-existing accounts (login, reset, signup).
- [ ] Session ID rotated on login and privilege change.
- [ ] OAuth: PKCE + `state` + exact `redirect_uri` match + full ID token validation (`iss`, `aud`, `exp`, `nonce`, signature, alg allowlist).
- [ ] Deny-path tests exist: expired token, tampered token, `alg:none`, reused refresh, replayed reset link, concurrent logout.
- [ ] Auth events audited: login, failed login, resets, MFA enrollment/removal, API key creation.

## Failure Modes

- **JWT-as-session with no revocation story** — compromise means waiting out the token, or an emergency signing-key rotation that logs out everyone.
- **Tokens in localStorage** — one XSS anywhere (including a compromised npm dependency) exfiltrates every user's session.
- **Client-side-only logout** — cookie cleared, server session still valid; stolen cookie keeps working.
- **Reset flow that doesn't kill sessions** — attacker with a live session survives the victim's password change.
- **Accepting `alg: none` or mismatched algorithms** when verifying JWTs — verify against an allowlist of expected algorithms and keys, not whatever the token header claims.
- **Different error messages** ("no such user" vs "wrong password") — free enumeration oracle; also leaks via signup ("email already registered") and reset flows.
- **Redirect URI validated by prefix/substring** — `https://yourapp.com.evil.com` walks through; exact-match registered URIs only.
- **Long-lived static service secrets** shared via env and never rotated — one leaked staging config compromises production indefinitely.
- **MFA with SMS-only recovery** — SIM swap converts your MFA into single-factor with extra steps.

## Edge Cases

- **Concurrent refresh from multiple tabs**: two tabs race to use the same refresh token; naive reuse-detection logs the user out. Allow a short grace window (~10 s) where the previous token is accepted once, or serialize refresh via a shared worker/lock.
- **Half-logged-in states**: MFA prompt passed but second factor pending — this intermediate state needs its own limited session type, not a full session with a flag.
- **Email case and unicode**: `User@x.com` vs `user@x.com` vs homoglyph domains; normalize on signup AND login identically, or users "lose" accounts.
- **Password managers and paste**: never block paste; never silently truncate (bcrypt 72 bytes) — users' 100-char passwords will "work" at signup and fail at login if truncation differs.
- **Session across subdomains**: cookie Domain scoping too wide leaks sessions to every subdomain, including user-generated-content ones. Scope tight.
- **Deleted/disabled users with live sessions**: session validation must re-check account status, not just session existence.
- **OAuth account linking**: email from provider matches existing local account — auto-linking without verified email enables account takeover via attacker-controlled IdP accounts. Require verified email + explicit link confirmation.
- **Clock skew on mobile devices**: user's phone is 5 minutes wrong; if your client checks `exp` locally before sending, it dies mysteriously. Let the server be the clock.

## Tradeoffs

- **Sessions vs JWTs**: sessions cost a store lookup per request but give instant revocation and small cookies; JWTs skip the lookup but push you into short lifetimes, refresh machinery, and revocation compromises. Latency of one Redis GET is almost never the real bottleneck — choose sessions unless crossing trust boundaries.
- **Security vs friction**: 15-min absolute timeouts and constant re-auth train users to autopilot through prompts. Spend friction budget on sensitive operations (step-up auth for payout changes) rather than uniformly.
- **Building vs buying**: auth providers (Auth0/Cognito/etc.) remove implementation risk but add vendor coupling, per-MAU cost, and migration pain (password hash export). Build on frameworks' vetted primitives, buy when SSO/SAML/compliance matrix exceeds team capacity, never hand-roll crypto either way.
- **Lockout vs availability**: aggressive account lockout stops brute force but hands attackers a DoS button against arbitrary victims. Prefer escalating delays + CAPTCHA + credential-stuffing detection over hard lockout.

## Optimization Strategies

- Cache session lookups in-process for a few seconds only if revocation SLA tolerates it; otherwise keep the Redis hop and optimize the Redis path.
- Use passkeys/WebAuthn to delete the password + phishing problem for returning users; keep password as fallback during adoption.
- Precompute risk signals at login (new device, new geo, impossible travel) and gate step-up MFA on them instead of always-on prompts.
- Issue scoped, short-lived tokens for high-volume internal calls derived from the user session once, rather than re-validating the full session at every hop.
- Standardize on one auth middleware; every hand-rolled "quick check" in a route handler is a future CVE.

## Self Review

- Can I revoke a specific user's access in under 60 seconds? Walk the exact mechanism.
- What can an attacker do with: a stolen access token? a stolen refresh token? a database dump? Each answer should be bounded and written down.
- Are all four reset-flow properties present: single-use, expiring, hashed at rest, session-invalidating?
- Do login, signup, and reset behave identically for existing and non-existing accounts — body, status, and time?
- Is there any place a token or password can end up in logs, URLs, or Referer headers?
- Did I write at least one test per deny path, and do they actually assert 401/403 (not just "doesn't 200")?
- If my JWT signing key leaked today, what's the rotation procedure and blast radius?

## Examples

**1. Choosing boring correctly.**
B2B SaaS, React SPA + Rails API, same domain. Team proposes JWTs in localStorage "for scalability." Expert choice: server sessions in httpOnly SameSite=Lax cookie, Redis store, 24 h idle timeout, CSRF token on mutations. Rationale recorded: one Redis GET per request is nothing at their scale; instant revocation required by enterprise customers; XSS blast radius contained. JWT complexity deferred until an actual cross-service boundary exists.

**2. Refresh rotation catching real theft.**
Mobile app: access JWT 10 min, refresh 30 days, rotate-on-use. Attacker exfiltrates a refresh token from a backup; uses it. Later the legitimate app refreshes with its (now-stale) token → server sees reuse of a consumed token → revokes the whole family, forces re-login, raises a security event with device metadata. User re-authenticates; attacker's chain is dead. Without rotation+reuse detection, that theft was invisible for 30 days.

**3. Password reset done to spec.**
`POST /password-resets {email}` → always `202 Accepted`, same latency (dummy hash executed when user unknown). Email contains `https://app/reset?token=<256-bit-random>`; DB stores `sha256(token)`, `expires_at: +30m`, `used: false`. On submit: verify hash, expiry, unused → set password (argon2id), mark used, delete all other reset tokens, destroy all sessions, notify email, rotate any "remember me" tokens. Replay of the link → generic "link expired" page.

**4. OAuth integration review catch.**
PR adds "Login with Google": code flow, but no `state`, `redirect_uri` checked by prefix, and account auto-linked by email. Review verdict: three findings — CSRF-able flow (attacker can log victim into attacker's account), open redirect to `yourapp.com.evil.com`, and takeover via unverified-email IdP accounts. All three are common enough to be in bug-bounty top-10 lists; none throw errors in testing.

## Evaluation Rubric

Score 1–10:

- **1–2**: Plaintext or fast-hash passwords; tokens in localStorage; no revocation; enumeration oracles everywhere.
- **3–4**: bcrypt present but flows unspecified; logout client-side; reset flow keeps old sessions; JWT with no lifetime/rotation policy.
- **5–6**: Sound mechanism choice with rationale; lifetimes defined; reset flow mostly correct; some deny paths untested; uniformity not verified by timing.
- **7–8**: Full checklist passes; rotation with reuse detection; deny-path test matrix implemented; audit events wired; OAuth validated to spec.
- **9–10**: Additionally: step-up auth for sensitive ops; passkey path; key rotation runbook rehearsed; enumeration verified with timing measurements; a written answer to "what does a DB dump cost us" that a security reviewer accepted.
