# API Design

## Purpose

Design HTTP/RPC APIs that are stable under evolution, cheap for clients to consume correctly, and hard to consume incorrectly. Covers resource modeling, error contracts, pagination, versioning, and compatibility.

## When to use

- Creating a new public or internal API surface.
- Adding endpoints to an existing API.
- Reviewing an API proposal or OpenAPI/proto spec before implementation.
- Deciding between REST, GraphQL, gRPC, or webhook delivery.
- A client team reports the API is "awkward" (many round trips, unclear errors, breaking changes).

## Goals

- Every screen or workflow a client builds should need 1–2 calls, not 5.
- Errors are machine-actionable, not just human-readable.
- The API can evolve for years without a v2.
- A new consumer can integrate from the spec alone, without reading server source.

## Inputs

- Concrete client use cases: the actual screens, jobs, or integrations that will call this API (not just entity list).
- Domain model and ownership boundaries.
- Expected scale: request volume, payload sizes, list cardinalities.
- Consumer types: first-party web/mobile, third-party developers, internal services.
- Existing conventions in the codebase (auth scheme, error envelope, naming).

## Outputs

- Endpoint list with methods, paths, request/response schemas.
- Error catalog: every error code a client can receive per endpoint, with recovery guidance.
- Pagination, filtering, and sorting contract for every list endpoint.
- Versioning and deprecation policy statement.
- Example request/response pairs for the 3 most important flows, including one failure.

## Expert Mental Model

What experienced designers think about first:

- **Design from the consumer inward, not the database outward.** The API's shape should match the client's tasks, not the table schema. If the API mirrors tables, every client rebuilds your domain logic and every schema change becomes a breaking change.
- **An API is a promise.** Removing a field, tightening validation, changing a default, or reordering enum semantics all break clients — even if the URL never changes. Compatibility is about behavior, not routes.
- **The error contract IS the contract.** Happy paths integrate themselves; teams spend 80% of integration time on failure handling. Experts design the error catalog before the success payloads.
- **Every collection becomes large.** Any endpoint returning a list will eventually need pagination, filtering, and ordering. Retrofitting pagination is a breaking change; shipping it on day one is cheap.
- **Chattiness is a design smell, not a client problem.** If rendering one screen needs N calls, the resource boundaries are wrong or an expansion/composition mechanism is missing.
- **Idempotency is a first-class feature.** Networks retry. Any unsafe operation (POST that charges, sends, creates) needs an idempotency key path, or clients will double-charge users during timeouts.

## Workflow

1. **Collect 3–5 concrete consumer scenarios.** Write them as "client X needs to do Y" sentences. Reject "expose the orders table" as a scenario.
2. **Model resources and their lifecycle.** Nouns with clear identity and state transitions. Draw the state machine for anything with a status field.
3. **Map scenarios to calls.** For each scenario, write the exact call sequence. If any scenario needs >2 calls, revisit resource boundaries or add a composite/expansion mechanism (`?include=customer,items`).
4. **Choose the protocol** using the Decision Tree below. Default to plain REST+JSON unless a specific force pushes elsewhere.
5. **Design the error envelope once, globally.** Machine-readable stable `code`, human `message`, `request_id` for support, optional `details[]` for field-level validation. Then enumerate per-endpoint error codes.
6. **Specify list behavior.** Cursor pagination by default; define max page size, sort stability, and filter parameters as an explicit allowlist.
7. **Specify write semantics.** Idempotency keys for unsafe POSTs; PUT vs PATCH semantics (merge-patch rules for nulls); what the response body of a write is (return the full resource — clients need it).
8. **Do the compatibility review.** For each field: could we ever need to remove or retype it? Prefer objects over scalars where growth is likely (`{"amount": 5, "currency": "USD"}` not `5`), enums documented as open sets.
9. **Write examples for the top 3 flows including one failure**, and have a client engineer attempt a paper integration from the spec alone.
10. **Define deprecation mechanics** (Sunset headers, telemetry on old-field usage) before launch, not at first deprecation.

## Decision Tree

- If consumers are third-party developers with varied needs → REST+JSON with expansion params; invest heavily in error catalog and docs.
- Else if one first-party frontend owns most queries and screens change weekly → consider GraphQL or a BFF (backend-for-frontend) layer; accept the caching and complexity cost.
- Else if service-to-service, high volume, both ends owned internally → gRPC/protobuf; you get contracts and performance, lose casual debuggability.
- Else if the consumer needs to be notified of events → webhooks (signed, retried, idempotent) or an event stream; do not make them poll.
- Else → REST+JSON, resource-oriented, boring on purpose.

For operations that don't fit CRUD:
- If it changes resource state → model as a subresource or action endpoint (`POST /orders/{id}/cancellation` or `POST /orders/{id}:cancel`), never `GET` with side effects.
- If it's a long-running job → return `202` with a job resource to poll (`GET /jobs/{id}`), never hold the connection open past ~10s.

For 404 vs 403 on unauthorized access:
- If revealing existence leaks information (multi-tenant data) → return 404 for both missing and forbidden.
- Else → 403 with a stable code, which is kinder to integrators.

## Heuristics

- If the client needs three calls to render one screen, the API is wrong, not the client.
- Design the error before the happy path; the happy path designs itself.
- Return the full resource from every write. The client always needs it, and it kills a follow-up GET.
- IDs are opaque strings. Never expose auto-increment integers (enumeration attacks, migration pain, and clients WILL do math on them).
- Timestamps: ISO-8601 with explicit UTC offset, suffixed field names (`created_at`), always server-generated.
- Booleans in payloads are usually premature enums. `status: "active" | "suspended"` survives; `is_active: true` needs a breaking change the day a third state appears.
- Cursor pagination over offset: stable under concurrent writes, index-friendly at depth. Offset is acceptable only for small, admin-facing, rarely-written data.
- Accept liberally on inputs you control the parsing of, but never silently drop unknown fields on writes if the client might be misspelling one — consider rejecting unknown fields in strict mode for developer APIs.
- A `request_id` in every response (success and failure) pays for itself the first support ticket.
- If two endpoints return the same entity with different shapes, clients will cache the wrong one. One resource, one canonical representation; use expansions or sparse fieldsets for variation.
- Rate limit headers (`X-RateLimit-Remaining`, `Retry-After`) turn your 429s from outages into backpressure.

## Quality Checklist

- [ ] Each target consumer scenario completes in ≤2 calls.
- [ ] Every list endpoint has pagination, a max page size, and a documented default sort that is stable (ties broken by unique key).
- [ ] Every error response carries a stable machine code, human message, and request id.
- [ ] Every unsafe POST accepts an idempotency key, and replay returns the original result.
- [ ] No breaking change is required for foreseeable growth (checked field-by-field).
- [ ] Write endpoints return the resulting resource.
- [ ] Auth failures, validation failures, and not-found are distinguishable by code, not by parsing messages.
- [ ] Long-running operations return job resources, no endpoint holds connections >10s.
- [ ] Spec includes at least one full failure example per critical flow.
- [ ] Naming is consistent with the rest of the API surface (same casing, same pluralization, same word for the same concept).

## Failure Modes

- **Database-schema mirroring.** Exposing tables as endpoints; every client reimplements the domain, every migration breaks the world.
- **The 200-with-error-body.** Returning `200 {"success": false}` breaks every HTTP client library's error handling, retry logic, and monitoring. Status codes are the contract.
- **Breaking change by validation tightening.** Adding a max length or required field to an existing endpoint breaks deployed clients just as surely as deleting the endpoint.
- **Boolean flags accumulating** (`?include_deleted=true&expanded=true&new_format=true`) until behavior is a 2^n matrix nobody tests.
- **Pagination added later** — changes response shape from array to envelope, breaking every consumer at once.
- **Errors designed for humans only.** Clients end up string-matching `message`, which you then can't ever reword.
- **Chatty-by-design plus "just cache it"** — pushing the N+1 problem to every client instead of adding `?include=`.
- **Version-in-URL as first resort.** `/v2/` forks the entire surface to change one endpoint; additive evolution should be exhausted first.

## Edge Cases

- **Empty vs missing vs null** in PATCH: define whether `null` clears a field and absence leaves it unchanged (JSON Merge Patch semantics) — and document it, because every client guesses differently.
- **Duplicate creation on retry**: client timeout after server success. Without idempotency keys this creates ghosts; with keys, the second attempt must return the first result, same status code.
- **Pagination under deletion**: cursor points at a deleted row. Cursors must tolerate missing anchors (resume after, not error).
- **Very large single resources** (an order with 10,000 line items): cap embedded collections and paginate subresources.
- **Unicode and normalization in identifiers**: emails, usernames, and tags need explicit normalization rules or lookups will mysteriously fail.
- **Clock skew**: client-supplied timestamps for ordering are lies; sequence on server time or version numbers.
- **Enum evolution**: clients switch on enum values; document that unknown values must be tolerated, and never reuse a retired value.
- **Zero results vs no permission**: an empty list can mean "nothing exists" or "you can't see them" — decide whether that distinction leaks and document it.

## Tradeoffs

- **Coarse vs fine-grained resources**: coarse endpoints (screen-shaped) minimize round trips but couple the API to today's UI; fine-grained resources are stable but chatty. Resolve with stable fine-grained resources plus expansion parameters or a BFF.
- **Strictness vs tolerance**: rejecting unknown fields catches client bugs early but makes additive client rollouts harder. Strict for third-party developer APIs, tolerant for internal high-velocity ones.
- **REST purity vs pragmatism**: action endpoints (`:cancel`) are impure but clearer than PATCHing a status field with hidden transition rules. Prefer clarity.
- **GraphQL flexibility vs operational cost**: you trade N endpoints for one endpoint that needs query cost analysis, persisted queries, and bespoke caching. Worth it with many diverse first-party views; rarely worth it for third parties.
- **Versioning**: URL versioning is visible and cache-friendly but forks the surface; header versioning is granular but invisible in logs. Best: don't version — evolve additively, and reserve versioning for true semantic breaks.

## Optimization Strategies

- Add `?fields=` sparse fieldsets and `?include=` expansions before considering GraphQL — they capture 80% of the benefit.
- Support `ETag`/`If-None-Match` on hot, cacheable GETs; a 304 is the cheapest response you'll ever serve.
- Batch endpoints (`POST /things:batchGet`) for N+1 hot paths, with per-item status in the response.
- Compress (gzip/brotli) and paginate before raising rate limits — most "we need higher limits" requests are payload problems.
- Instrument per-field usage (which fields, which expansions) so deprecation decisions are data, not guesses.
- Publish the OpenAPI spec and generate clients; hand-written clients drift and then their bugs become your compatibility constraints.

## Self Review

- Can I walk each real consumer scenario through the API in ≤2 calls, on paper, right now?
- For each field in each response: what happens to clients if this becomes null, absent, or a new type? Am I comfortable being unable to remove it for 5 years?
- Does every failure path return a code a client can `switch` on without string matching?
- What does a client see when it retries a timed-out write?
- Is there any GET with side effects, or any endpoint whose response shape depends on hidden state?
- Have I checked the naming against the existing surface — same concept, same word, same casing?
- If I deleted the server code, could a competent engineer reimplement it from my spec and examples?

## Examples

**1. Order cancellation (action modeling).**
Naive: `PATCH /orders/123 {"status": "cancelled"}` — hides transition rules, invites illegal transitions.
Expert: `POST /orders/123:cancel {"reason": "customer_request"}` → `200` with full order, or `409 {"code": "order_already_shipped", "message": "...", "request_id": "..."}`. The transition is explicit, its failure modes are enumerable, and the audit trail has a reason.

**2. List endpoint contract done right.**
`GET /invoices?status=open&created_after=2026-01-01T00:00:00Z&limit=50&cursor=eyJpZCI6...`
Response: `{"data": [...], "next_cursor": "...", "has_more": true}`.
Sort: `-created_at, -id` (unique tiebreak = stable pages). Max limit 200, documented. Filters are an allowlist; unknown filter params return `400 {"code": "unknown_filter", "details": [{"field": "statuss"}]}` instead of silently returning everything — silent full-table responses have caused real data leaks.

**3. Idempotent payment creation.**
`POST /charges` with header `Idempotency-Key: 7f9c...`. Server stores `(key, request_hash, response)` for 24h. Retry with same key + same body → replay stored response, same status code. Same key + different body → `409 {"code": "idempotency_key_reuse"}`. This one design decision eliminates the double-charge class of incident.

**4. Evolving without v2.**
Need: prices gain currency support. Breaking: change `"price": 500` to an object. Additive path: add `"price_detail": {"amount": 500, "currency": "USD"}`, keep `price` as deprecated alias emitting telemetry, announce sunset with `Deprecation` and `Sunset` headers, remove after usage <0.1% for 90 days. No version fork.

## Evaluation Rubric

Score the produced API design 1–10:

- **1–2**: Endpoints mirror database tables; no error contract; lists unpaginated; breaking changes inevitable within months.
- **3–4**: Consistent REST shapes but designed without consumer scenarios; errors human-readable only; pagination inconsistent; no idempotency story.
- **5–6**: Scenarios drive the shape; global error envelope with codes; cursor pagination on lists; some compatibility thinking; gaps in edge cases (PATCH null semantics, retry behavior undefined).
- **7–8**: All checklist items pass; idempotency on unsafe writes; error catalog per endpoint; deprecation mechanics defined; a client engineer completed a paper integration from spec alone.
- **9–10**: Additionally: expansion/sparse-fieldset mechanisms sized to real chattiness data; compatibility reviewed field-by-field with growth headroom; failure examples in docs; per-field usage telemetry planned; the design document records rejected alternatives and why.
