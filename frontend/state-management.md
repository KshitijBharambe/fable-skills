# State Management

## Purpose

Decide where every piece of frontend state lives — server cache, URL, local, global store, form library — and keep the number of global stores, sync effects, and stale-data bugs near zero.

## When to use

- Starting an app or feature and choosing state architecture.
- A global store has become a dumping ground and every change ripples.
- Data is stale, duplicated, or flickering between values.
- Deciding whether to adopt Redux/Zustand/Jotai/MobX/signals or a server-cache library.
- Multi-step flows (wizards, checkout) whose boolean flags no longer describe reality.

## Goals

- Every state atom classified by kind, with placement following the classification.
- Server data handled by a cache layer with explicit staleness policy — never hand-mirrored into stores.
- Global client state is small (viewer, theme, feature flags, cross-cutting UI) and enumerable.
- Complex flows modeled as explicit states, not boolean combinations.

## Inputs

- Inventory of state the feature touches: fetched data, user input, UI toggles, navigation state, session identity.
- Sharing requirements: which components, routes, or tabs need which state.
- Persistence requirements: survive refresh? survive logout? shareable via link?
- Team's existing stack and conventions.

## Outputs

- A state map: each atom → kind → home (query cache / URL / local / store / form lib) → staleness/persistence policy.
- Store slices (if any) with narrow, documented scope.
- Explicit state machines for multi-step or async-critical flows.

## Expert Mental Model

- **The first question is never "which library" — it's "which kind of state?"** Five kinds, five homes:
  1. **Server cache** (fetched entities): belongs to a query layer (React Query/SWR-pattern) with staleness, dedupe, invalidation. It is a *cache of someone else's truth*, not your state.
  2. **URL state** (filters, tab, page, selected id): belongs in the URL — it's the only store with back-button, refresh, and share built in.
  3. **Local UI state** (open/closed, hover, draft text): `useState` next to its user.
  4. **Shared client state** (viewer session, theme, unsaved cross-view selections): the only legitimate global-store tenant — and it's small.
  5. **Form state**: high-frequency, validation-coupled — a form library's job, isolated from everything else.
  Most "state management pain" is category error: server data in Redux, filters in memory, wizard state in nine booleans.
- **Server state is a cache, so think in cache terms**: staleness tolerance, invalidation triggers, optimistic updates with rollback. "Store the API response in a global store and update it manually" reinvents a cache with no policy — the flicker, staleness, and double-fetch bugs follow from the missing policy, not the library choice.
- **Derived state is not state.** Totals, filtered lists, `canSubmit` — compute from sources; storing them creates sync obligations that WILL be violated. A selector/computed is a contract that it's always right.
- **Booleans breed impossible states.** `isLoading && isError`, `isSubmitting && isSuccess` — 2^n combinations, most meaningless. A discriminated union (`status: 'idle' | 'loading' | 'error' | 'success'`) or a state machine makes impossible states unrepresentable — the single highest-leverage modeling move in frontend.
- **Re-render blast radius is architecture.** Every subscriber to a store slice re-renders on its change. Global stores with hot values (keystroke-frequency) melt; the fix is scoping (move state down) and slicing (subscribe narrow), not memo confetti.

## Workflow

1. **Inventory and classify** every state atom into the five kinds. This 20-minute table prevents the month of pain.
2. **Route server data through a query layer.** Define per entity: `staleTime` (how old is acceptable — mirrors product's staleness budget), invalidation triggers (which mutations invalidate which queries), and key structure (`['orders', {status, page}]` — keys are the cache's API design).
3. **Put URL-worthy state in the URL** via typed search-param helpers. Test: "if the user refreshes or shares this link, should they see the same view?" Yes → URL.
4. **Default the rest to local state**, lifted per component-architecture rules. Escalate to a store only when: consumed across distant subtrees AND not server/URL/form state AND context re-render cost is real.
5. **Design store slices narrowly** (if needed): named domain slices (`session`, `notifications`) with actions as the only writers. No `misc` slice — that's the dumping ground's front door.
6. **Model async operations as unions**: `{status: 'idle'|'pending'|'success'|'error', data?, error?}` — never independent booleans. For multi-step flows, write the state machine: states, events, allowed transitions; make illegal transitions throw in dev.
7. **Plan optimistic updates deliberately**: apply local change → fire mutation → on error, roll back AND surface the failure visibly (silent rollback = gaslighting the user). Only for high-success operations (toggles, reorders); pessimistic for payments and destructive actions.
8. **Define persistence explicitly**: what survives refresh (URL, storage-backed slices), what survives logout (nothing user-scoped — flush on logout is a security behavior, test it).
9. **Wire devtools and invariants early**: store devtools, query devtools, a dev-mode check for storing derived values (code review rule at minimum).

## Decision Tree

- If the data came from the server → query cache. (If you're about to `dispatch(setUsers(response))` — stop; that's the cache layer's job.)
- Else if refresh/share/back-button should preserve it → URL.
- Else if it's input being edited → form library (complex forms) or local state (a field or two).
- Else if exactly one component (or its subtree) uses it → local state, colocated.
- Else if it changes rarely and is read widely (theme, viewer, flags) → context or a small store slice.
- Else if it changes often and is read widely → store with granular subscriptions (or signals/atoms model); re-check whether it truly needs to be global.
- Else (multi-step flow, complex async choreography) → explicit state machine, stored wherever its consumers dictate.

Library selection (when a store is genuinely needed):
- Small app / few global atoms → context + reducer, or Zustand-class minimal store.
- Large team, complex domain interactions, audit/devtools culture → Redux Toolkit-class (conventions and tooling repay the ceremony at scale).
- Fine-grained perf-sensitive graphs of derived state → atom/signal-based (Jotai/Recoil-class).
- Whatever your framework blesses (Vue: Pinia; Svelte: stores/runes) unless it demonstrably fails a requirement — ecosystem fit beats micro-benchmarks.

## Heuristics

- If you can delete state and compute it, delete it. Every stored derived value is a future inconsistency.
- Query keys are cache API design: include every parameter that changes the result; structure hierarchically so invalidation can target prefixes (`['orders']` invalidates all order queries).
- `staleTime` default of 0 (always refetch) is rarely what product wants; set it consciously per entity (user profile: minutes; notification count: seconds; reference data: hours).
- One writer per atom: if two unrelated code paths write the same state, one of them is a bug incubating.
- Selectors return primitives/stable references where possible; returning fresh objects/arrays per call defeats every downstream memo.
- The "flag graveyard" check: any component reading >3 booleans to decide what to render is a state machine wearing a trench coat.
- Cross-tab state (auth, theme) needs a sync story (storage events / BroadcastChannel) or users get logged out in one tab and not another.
- Undo/redo, drafts, and offline are 10× easier with immutable-update patterns and explicit event/state models — retrofit is brutal; know upfront if you need them.
- Storage-persisted state needs versioning + migration or the first schema change strands users on corrupt state.
- If a state bug report includes "sometimes" or "after a while," suspect: two sources of truth, a stale cache without invalidation, or a race — in that order.

## Quality Checklist

- [ ] State map exists: every atom classified and homed, staleness/persistence stated.
- [ ] Zero server responses hand-copied into client stores.
- [ ] Filters/tabs/pagination/selection survive refresh (URL), verified.
- [ ] No stored derived values (spot-check: totals, counts, filtered lists computed).
- [ ] Async/multi-step modeled as unions or machines; impossible states unrepresentable in types.
- [ ] Mutations declare their invalidations (or optimistic update + rollback + error surface).
- [ ] Store slices narrow, actions-only writes, no `misc`.
- [ ] Logout flushes user-scoped state everywhere (test exists).
- [ ] Persisted slices versioned with migration.
- [ ] Re-render blast radius checked on hot interactions (profiler, mid-tier device).

## Failure Modes

- **The Redux mirror**: every API response dispatched into a global store, manually "updated" on mutations → stale lists after edits, flicker on navigation, double-fetch logic, and eventually a homegrown 70%-correct cache. The query layer existed to prevent exactly this.
- **Dumping-ground store**: `ui.modalStack`, `temp.selectedRow`, `misc.lastClicked` — global by laziness. Everything couples to everything; deleting anything is scary forever.
- **Boolean soup races**: `isLoading` true while `data` present, `isSuccess` and `isError` both true after a retry — UI renders contradictions "randomly." Union types eliminate the category.
- **Optimistic update, silent rollback**: toggle flips back with no message; user toggles five more times; support ticket says "it's possessed."
- **Two sources of truth**: form state initialized from a query, query refetches, form silently ignores or clobbers edits — decide explicitly (lock the query while editing, or merge policy) instead of letting timing decide.
- **Context as hot store**: keystroke-frequency values in context → app-wide re-renders → memo sprinkled everywhere as a tourniquet.
- **Persistence without flush**: previous user's data visible after logout on a shared machine — a privacy incident, not a bug.
- **Selector identity churn**: `useStore(s => ({a: s.a, b: s.b}))` returning a new object each time → every subscriber renders on every store change; the store gets blamed.

## Edge Cases

- **Race: slow first request beats fast second** — switching filters quickly shows results for the old filter. Query layers keyed correctly handle it; hand-rolled needs request-id/abort discipline.
- **Pagination + mutation**: delete an item on page 3 → does the list shift, refetch, or ghost? Decide invalidation vs surgical cache update per list.
- **Multi-tab writes**: same record edited in two tabs — last-write-wins silently loses work; at minimum detect via updated-at and warn.
- **WebSocket + query cache**: pushed updates must write into the cache (setQueryData), not a parallel store, or the two truths diverge on next refetch.
- **Auth expiry mid-session**: queries start 401ing — global handler must transition session state and flush user caches once, not per-query error spam.
- **Suspense/streaming boundaries**: state initialized during render on the server must serialize/hydrate consistently; client-only stores need mount gates.
- **Draft vs committed**: editing an entity in a modal over a live-updating list — the draft must be isolated (copy-on-open, `key`-reset) or background refetches stomp keystrokes.
- **Storage quota/corruption**: persisted store hydration must survive malformed/absent data (fallback to defaults, never crash-loop).

## Tradeoffs

- **Query-cache magic vs explicit control**: query libraries bring refetch-on-focus, retries, dedupe — brilliant defaults that surprise you (unexpected refetches firing mutations of side-effectful queries). Learn the defaults, configure per-entity; the alternative (hand-rolling) rebuilds them badly.
- **Global convenience vs coupling**: global access saves prop-plumbing today, buys invisible dependencies tomorrow. The plumbing was documentation.
- **Optimistic vs pessimistic UI**: optimism buys perceived speed, costs rollback complexity and trust when wrong. Optimistic for reversible high-success ops; pessimistic + loading affordance for money and deletion.
- **Normalization vs nesting** in caches: normalized (entities by id) keeps every view consistent on update, at real bookkeeping cost; nested-per-query is simpler and fine when entities rarely appear in multiple live views. Normalize on demonstrated cross-view staleness pain.
- **State machine ceremony vs ad-hoc**: machines pay off proportionally to (number of states × concurrency of events × cost of impossible states). A checkout flow: yes. A tooltip: no.

## Optimization Strategies

- Move state down before memoizing — placement fixes beat subscription micro-tuning and improve the design.
- Subscribe narrow: per-slice/per-atom selectors with stable outputs; batch related atoms into one selector only when they change together.
- Tune query `staleTime`/`gcTime` per entity to kill redundant network chatter — the biggest "app feels heavy" fix in query-layer apps.
- Prefetch on intent (hover/route-load) so navigation reads from cache.
- Use transitions/deferred values for expensive derived renders (filtering 10k rows) so typing stays responsive.
- Audit with devtools: log which mutations invalidate which queries; prune over-broad invalidations (`invalidate everything` = hidden full-app refetch).

## Self Review

- Can I produce the state map from the code — every atom, kind, home, policy? Where does it disagree with what's written?
- Is any server response living in a client store? Why does it think it's not a cache?
- What survives refresh, and does that match what users expect to survive?
- Where are my optimistic updates, and what exactly does the user see on rollback?
- Which states are boolean-combinations that types would forbid if I modeled them as unions?
- After logout on a shared computer, what remains in memory/storage? Proof?
- On the hottest interaction (typing, dragging), what re-renders? Have I looked?

## Examples

**1. Un-mirroring the store (classic rescue).**
Symptom: list stale after edits, flicker on nav, `usersSlice` with `fetchUsersStart/Success/Failure` × 12 entities. Migration: introduce query layer; entity by entity — delete slice, replace with `useQuery(['users', filters])`; mutations become `useMutation` + `invalidateQueries(['users'])`; optimistic toggle for the one high-frequency case. Redux shrinks to `session` + `notifications`. Bug class "edited but list didn't update" disappears because invalidation is now policy, not memory.

**2. Wizard as a state machine.**
Checkout with `isShippingDone, isPaymentOpen, isReviewing, isSubmitting, hasError` — QA finds "back from review during submit" duplicates orders. Remodel: `state: 'shipping' | 'payment' | 'review' | 'submitting' | 'confirmed'`, events `NEXT/BACK/SUBMIT/FAIL(err)`, transitions table; `SUBMIT` only legal from `review`, `BACK` illegal in `submitting` (button disabled *because the machine says so*, not by a sixth boolean). URL syncs to the state name so refresh restores position. The duplicate-order bug becomes unrepresentable.

**3. Filters to the URL.**
Dashboard filters in a store: refresh loses them, links can't share views, back button surprises. Move to URL: `?status=open&assignee=me&page=2` via a typed params hook (parse/serialize/defaults in one module); query keys derive from parsed params, so navigation = cache hits. Bookmarkable views ship for free; the store slice is deleted.

**4. Live data + edit draft coexistence.**
Support inbox: ticket list live-updates via WebSocket; an agent edits a ticket in a panel. Design: pushed events write into the query cache (`setQueryData`) — list stays live; the edit panel copies data on open (`key={ticket.id}`, form owns the draft) and locks refetch-overwrite of open fields; on save, mutation + targeted cache update + conflict check on `updated_at` (409 → "changed while editing" merge prompt). Two truths coexist because their boundary and merge policy are explicit.

## Evaluation Rubric

Score 1–10:

- **1–2**: Server data mirrored into a global dumping-ground store; booleans everywhere; nothing in URL; staleness bugs normalized.
- **3–4**: Query layer present but fought (manual copies persist); some URL state; derived values stored; blast radius unexamined.
- **5–6**: Five-kinds classification applied; invalidation declared per mutation; unions replace boolean soup on key flows; store small; some edges (multi-tab, logout flush) unhandled.
- **7–8**: Full checklist; state map documented and accurate; optimistic updates with visible rollback; persistence versioned; profiler-verified hot paths.
- **9–10**: Additionally: conflict policies for concurrent edits; socket-cache integration; machine-modeled critical flows with illegal-transition guards; per-entity staleness tuned to product budgets; the architecture explains itself — a new engineer places new state correctly without asking.
