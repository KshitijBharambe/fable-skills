---
name: data-tables
description: "Use when building a list of records (admin panels, CRMs, order/user lists, logs), users export to Excel to do real work, choosing pagination vs infinite scroll or inline edit, or fixing slow/lying sort and dangerous bulk ops."
---

# Data Tables

## Purpose

Design tables for the real jobs — scan, compare, select, act — with correct alignment, server-side data handling, bulk actions, and states, so business tools don't degrade into unusable grids or spreadsheet-envy.

## When to use

- Any list of records with more than a couple of attributes: admin panels, CRMs, order lists, user management, logs.
- Users export the table to Excel to do their actual work (the table is failing).
- Choosing between pagination and infinite scroll, inline editing vs detail views.
- Tables are slow, sorting lies, or bulk operations are dangerous.
- Responsive/mobile table decisions.

## Goals

- The table serves its top 3 user tasks (findable in seconds, comparable at a glance, actionable in place).
- Reading mechanics correct: identifier first, numbers right-aligned with tabular figures, sane density.
- Sort/filter/search/pagination are server-truthful (operate on the full dataset, not the loaded page).
- Bulk selection and actions are safe: visible counts, confirmations scaled to risk, undo where possible.

## Inputs

- Task inventory: what do users *do* here (find one record? compare? triage many? audit?), ranked.
- The data: columns available, cardinalities, value distributions (longest strings, widest numbers), total row counts now and at 10×.
- Action inventory: per-row actions, bulk actions, their risk levels and reversibility.
- Usage context: daily power users vs occasional; keyboard-heavy vs mouse; screen sizes.

## Outputs

- Column spec: order, alignment, width behavior, formatting, truncation rules per column.
- Interaction spec: sort/filter/search semantics (and where they execute), selection model, row-click vs action targets, keyboard map.
- Data contract with the backend: pagination type, sort/filter params, count strategy (see api-design).
- States per interface-states: loading skeleton rows, empty vs no-results, partial failure, saving states for inline edits.

## Expert Mental Model

- **A table is a tool for scan → compare → act, in that order.** Scanning wants a stable left anchor (the identifier column) and ruthless column curation; comparing wants aligned, consistently formatted values; acting wants unambiguous targets. Design each mechanic deliberately — a table is not "the data, gridded."
- **Column order is task order, not schema order.** First column: how users identify the row (name/order#/email — whatever they say when they talk about the record). Then the columns that drive the top tasks, left to right by importance. `created_at` first because the database put it there is how default tables announce nobody designed them.
- **Alignment is reading physics**: numbers right-aligned with tabular figures (so magnitudes compare down the column), text left-aligned, dates consistently formatted in one column style, headers aligned with their content. Center-aligned anything (except narrow status glyphs) slows scanning measurably.
- **The dataset is bigger than the page — behave accordingly.** Sort, filter, search, and counts must run server-side over the full data the moment the table paginates; client-side sorting a loaded page while implying full-data sorting is a *lie* users discover at the worst time ("I sorted by amount and the biggest invoice wasn't there"). This contract with the backend is the table's foundation, decided first.
- **Selection and bulk action are where tables hurt people.** "Select all" ambiguity (page vs all 14,202 matching), invisible selections lost on page-change, bulk-delete with a casual confirm — these produce the incidents. The selection model needs explicit design: persistent count chip, cross-page semantics, risk-scaled confirmation, undo or dry-run for the destructive.
- **Density is the power user's feature, whitespace is the newcomer's** — same tension as everywhere (visual-hierarchy), sharpest in tables. Default comfortable (~44–48 px rows), offer compact (~32–36 px) as a persisted preference for the daily crowd; don't average.

## Workflow

1. **Rank the tasks, then audit columns against them**: every column must serve a ranked task; move the rest behind a column-picker (hidden by default). Target ≤7–9 visible columns; past that, horizontal scroll with pinned identifier or a redesign (maybe it's two views).
2. **Nail the data contract with the backend** (before UI): keyset pagination for large/user-facing (see postgres), sort allowlist (indexed columns only, stable tiebreak), filter param allowlist, count strategy (exact when cheap, estimated or "1,000+" when not). Everything below flows from this.
3. **Spec each column**: alignment (numbers→right + `tabular-nums`, text→left), format (dates: one style, relative for recency + absolute on hover; money: currency-aware; enums: chips only if color adds meaning), width (fixed for predictable types, flexible for names), truncation (ellipsis + full-value tooltip; never wrap identifiers), null display (an explicit "—", never blank — blank reads as "loading" or "bug").
4. **Design row interaction targets**: decide the row-click (open detail? select? nothing?) and make it consistent app-wide; separate interactive zones cleanly (checkbox zone, row-click zone, actions zone) — checkbox-click must never trigger row-open (the classic collision). Per-row actions: ≤2 icons inline + overflow menu; destructive lives in the overflow, never as a bare inline trash icon next to a hover target.
5. **Build the selection model**: header checkbox = page scope with an explicit escalation banner ("All 50 on this page selected · Select all 14,202 matching"); selection count chip persistent and sticky with the bulk-action bar; selections survive page navigation (or are explicitly cleared with notice); bulk bar shows count in the button ("Delete 14,202 records…").
6. **Scale confirmation to risk**: reversible bulk actions → do + undo toast (with count); destructive irreversible → typed confirmation for large N ("type DELETE to remove 14,202") + async job with progress + partial-failure report ("14,190 deleted, 12 failed — view failures").
7. **Make sort/filter state legible and durable**: applied filters as removable chips above the table; sort indicator visible; the whole state (filters, sort, page/cursor) in the URL — shareable, refresh-proof, back-button-correct (see state-management).
8. **Sticky the anchors**: header sticks under scroll; identifier column pins under horizontal scroll; the bulk-action bar sticks when selections exist.
9. **Apply the states** (interface-states): skeleton rows at final row height (no jump), empty vs filtered-to-empty distinguished (with filter-reset), inline-edit saving/error per cell, partial page-load failure at the list tail.
10. **Add keyboard support proportional to audience**: minimum — focusable rows, Enter to open, Space to select; power tools — j/k navigation, x to select, shift-click ranges, bulk shortcuts. Test the tab order and screen-reader semantics (`<table>` markup or full ARIA grid — half-ARIA is worse than plain markup).

## Decision Tree

- Pagination vs infinite scroll vs virtual scroll:
  - If business tool with reference/return needs (find it again, share "page 3", footer must be reachable) → pagination (keyset-backed), page size 25–50 default with a chooser.
  - Else if feed-like consumption (logs, activity streams) → infinite scroll with URL-preserved position anchors and a jump-to-time control.
  - If DOM performance with thousands of loaded rows → virtualization is an *implementation* layer under either (see frontend-performance), not a UX choice by itself.
- Inline edit vs detail panel vs edit page:
  - If single-field, low-validation edits are a top task (rename, status, assignee) → inline edit (click-to-edit affordance visible on hover/focus, save on blur/Enter, per-cell saving/error states).
  - Else if edits touch multiple dependent fields → side panel keeping list context.
  - Else (complex validation, long forms) → dedicated page; inline editing complex objects produces half-saved states.
- Row click:
  - If a detail view exists → row-click opens it (in a side panel for triage workflows — preserves list position; full page for deep records); actions/checkbox zones excluded from the click target.
  - Else → row-click selects, and say so via affordance.
- Mobile/narrow:
  - If the table's job survives with 2–3 key fields → card list on mobile (identifier + the two decision fields + status), detail on tap.
  - Else (genuinely tabular comparison work) → horizontal scroll with pinned identifier column and honest advice that this is a desktop workflow.
- Counts:
  - If exact count cheap → show it ("14,202 results").
  - Else → "10,000+" style estimate; a slow exact count on every keystroke of a filter is how tables get 4-second interactions (see postgres).

## Heuristics

- Row height rhythm: comfortable 44–48 px, compact 32–36 px, header slightly shorter than rows; wrapped two-line cells break scan rhythm — truncate instead, except designated description columns.
- One line per row. If a row needs three stacked lines, it wants to be a card list or needs column surgery.
- Column headers are labels, not sentences: "Amount" not "Total Amount ($USD)" — units go in a subheader or the values.
- Zebra striping OR row borders OR generous row padding — pick one separator strategy; stacking all three is grid soup. Hover highlight always (it's the row-tracking aid).
- Status chips: ≤6 distinct statuses with icon/shape + color (colorblind), muted backgrounds; 14 statuses in candy colors is a taxonomy problem wearing UI.
- Relative dates for recency ("2h ago") flip to absolute past ~7 days; always absolute on hover with timezone; log/audit tables: absolute always, sortable format.
- Default sort must be defensible for the top task (newest first for activity; risk/priority for triage queues) — and stated (visible indicator), not silent.
- Search-within-table searches what the user thinks it searches (visible columns at minimum; say if it's server-wide) — scope ambiguity generates "search is broken" tickets.
- Numbers: consistent precision per column, thousands separators, currency symbol once (header) or per value, negatives clearly marked (−, red only if semantically bad).
- Export button exports current filters/sort, states the row count before running, and goes async past ~10k rows (see interface-states example).
- Never let a hover-only affordance be the only path to an action (touch devices, discoverability): hover-reveal is a de-cluttering technique layered over persistent access (overflow menu).
- Persist per-user: column visibility/order/width, density, page size. Reset-to-default one click away.

## Quality Checklist

- [ ] Top-3 tasks written; every visible column maps to one; identifier column first and pinned.
- [ ] Numbers right-aligned tabular; dates one consistent style; nulls explicit "—"; truncation with tooltips.
- [ ] Sort/filter/search/count execute server-side over the full dataset; sort columns indexed; stable tiebreak.
- [ ] Filter chips + sort indicator visible; full table state in URL; back button correct.
- [ ] Selection: count chip, cross-page semantics explicit, select-all escalation banner, sticky bulk bar.
- [ ] Confirmations risk-scaled; destructive bulk = typed confirm + async + partial-failure report; undo for reversible.
- [ ] Row-click, checkbox, and action zones collision-free; destructive not bare-inline.
- [ ] Sticky header; pinned identifier under horizontal scroll.
- [ ] All states: skeleton rows (final height), empty vs no-results (with reset), cell-level save/error.
- [ ] Keyboard: at minimum row focus/Enter/Space; screen reader semantics valid (`<table>` or complete grid pattern).

## Failure Modes

- **Client-sorting the current page**: user sorts by amount, sees the loaded 50 sorted, believes it's the dataset. The table lied; trust doesn't recover fast.
- **Schema-order columns**: `id, uuid, created_at, updated_at, tenant_id, name...` — the user's identifier in column 7. Nobody designed this; everybody suffers it.
- **Selection amnesia**: user selects 12 across three pages, hits an action — only the current page's 4 apply. Or worse: filters change, selection silently persists onto now-invisible rows and the bulk action hits them.
- **The casual mass-delete**: "Delete selected?" [OK] — with 14,202 selected via select-all. One misread, no undo, restore-from-backup afternoon.
- **Checkbox/row-click collision**: every third selection attempt opens the record; users slow down and start distrusting their clicks.
- **Center-aligned number columns with proportional fonts**: magnitude comparison destroyed; the column looks decorative and reads as nothing.
- **Wrap-everything rows**: long names wrap to 3 lines, row heights vary wildly, scanning rhythm dead, table 3× taller than needed.
- **Filter ghosts**: an applied filter with no visible chip; "where did my orders go?" tickets; the reset button is buried in a menu.
- **Empty-cell ambiguity**: blank cells that could be null, zero, loading, or broken — the reader can't tell and assumes the worst.
- **Half-ARIA grids**: divs with `role="grid"` but broken arrow-key semantics — worse for screen readers than a plain `<table>` would have been.

## Edge Cases

- **Live updates under interaction**: new rows arriving while the user scrolls/selects — never shift rows under a cursor; buffer with "3 new rows ↑" affordance; freeze order during selection mode.
- **Concurrent edits**: two admins inline-editing the same cell — last-write-wins silently loses; version-check and surface conflicts (see forms).
- **Deep-link to a row**: sharing "row 4,381" — support `?highlight=id` that fetches that row's page/cursor and scrolls+flashes it; otherwise shared links say "page 88" and mean nothing after tomorrow's inserts.
- **Duplicate-looking rows**: legitimately similar rows (same name, same date) need a visible discriminator column or users will act on the wrong one.
- **Extreme widths**: 400-char user-generated names, 12-digit amounts, emoji in identifiers — width and truncation rules must survive the fixture set, not the demo data.
- **Timezone in date columns**: an ops team spanning zones sorting by "today" — column header states the zone (or per-user zone applied consistently; see dashboard-ux).
- **Sort by computed/joined columns**: sorting by "total spend" that's a JOIN aggregate — needs a materialized/denormalized strategy server-side or the sort times out at scale (see postgres); the UI must not offer sorts the backend can't honor.
- **Selection across filter change**: define it — clearing selection with notice on filter change is the least-surprising rule.
- **Print/export fidelity**: hidden columns, truncated values, and chips must resolve to full values in exports; the CSV is the table's testimony in tomorrow's dispute.

## Tradeoffs

- **Feature richness vs spreadsheet envy**: every added grid feature (multi-sort, grouping, pivots, formulas) approaches rebuilding Excel badly. If users need spreadsheet-grade manipulation, give them a great filtered export and keep the table focused on its ranked tasks; build pivots only when they're the product.
- **Inline actions everywhere vs calm rows**: inline edit/actions accelerate power users and clutter+risk-expose everyone; hover-reveal + overflow menus + keyboard paths serve both, at a discoverability tax you mitigate once (onboarding hint, visible on focus).
- **Infinite scroll immersion vs pagination orientation**: scroll removes friction and destroys place-keeping, footer access, and "share where I am"; business tools nearly always want pagination. Choosing scroll for a work table because it demos smoothly is optimizing the demo.
- **Column flexibility vs consistency**: user-configurable columns serve diverse workflows and fragment shared vocabulary ("my table shows X, yours doesn't"). Persist personal layouts, but keep a canonical default and make "reset" trivial.
- **Exact counts vs speed**: exact counts on filtered 50M-row tables cost seconds per keystroke; estimates cost a little precision. Users need magnitude, not audit-grade counts, at filter time — exactness can arrive lazily or on demand.

## Optimization Strategies

- Instrument: which columns get sorted/filtered, which are never looked at (eye-tracking proxy: column-picker analytics), which bulk actions run, where export clicks happen. Prune and reorder from data quarterly.
- Ship density + column persistence early — the cheapest "this tool respects me" signal for daily users.
- Precompute the expensive sortables (denormalized aggregate columns maintained by events) so the UI never offers a lying or timing-out sort.
- Keyboard-power the top workflow end-to-end (navigate→select→act without mouse) for the daily-triage crowd; measure adoption before expanding shortcuts.
- Replace "search everything" hedges with scoped quick-filters for the top 3 real queries (status:open assignee:me) — chips beat a mystery search box.
- Watch 3 session recordings of real table work per quarter: the misclicks, the hover-hunting, and the export-then-Excel moves tell you what the grid analytics can't.

## Self Review

- What are the top 3 tasks, and can I demonstrate each in under 10 seconds on this table?
- Does sorting/filtering/searching operate on the full dataset — verified against a multi-page fixture?
- Select all → what exactly is selected, and how does the user know? What happens on page 2? After a filter change?
- What's the worst thing one misclick can do here, and what stands between the user and it?
- Do the numbers align? Do the dates match style? What does a null look like?
- Where does row-click go, and can I hit checkbox/actions without triggering it — on touch too?
- Does the URL reproduce this exact view for a colleague?
- What does the table look like with the fixture set (longest name, 12-digit amount, 10k rows, zero rows)?

## Examples

**1. Orders table, contract-first.**
Tasks ranked: (1) find a specific order (support calls), (2) triage today's problem orders, (3) bulk-update fulfillment status. Backend contract: keyset pagination on `(created_at, id)`, sort allowlist {created_at, amount, status}, filter allowlist {status, date-range, customer}, estimated counts past 10k. UI: Order# first (pinned), Customer, Amount (right, tabular), Status chip (5 states, icon+color), Age (relative→absolute), Actions overflow. Quick-filters as chips: "Problems today" (the #2 task, one click). Bulk: select-page → escalation banner → "Update status for 1,204 orders" → async job with partial-failure report. URL carries everything; support pastes links into tickets instead of screenshots.

**2. The select-all incident, redesigned.**
Postmortem: admin filtered to a customer, select-all'd, deleted — the filter had silently cleared on a back-navigation and select-all meant *everything*; 40k records into restore. Fixes shipped: selection always cleared-with-notice on filter change; select-all escalation shows the *filter summary* in the banner ("Select all 312 matching **customer: Acme**"); destructive bulk >100 requires typing the count; delete is soft (30-day restore) with an immediate undo toast. Each fix targets one link in the incident chain — the redesign is the incident's causal diagram inverted.

**3. Inline edit with cell-level truth.**
CRM table where "assignee" and "stage" edits are the daily job. Click-to-edit dropdowns per cell; save on select; cell shows 300 ms spinner → checkmark fade, or error state (red outline + retry, value reverted-but-recoverable). Version check on save; conflict → "Maya changed this 10 s ago → [Take theirs] [Keep mine]". Full-record edits stay in the side panel. The two hot fields got inline speed; the risky complexity stayed in the form where validation lives.

**4. Mobile: the table that became cards honestly.**
Field-sales order list on phones: the desktop 9-column grid became a card list — Order# + customer (line 1), amount right-aligned (line 2), status chip + age (line 3), tap → detail, swipe → the single most-used action (mark delivered, with undo). Comparison workflows (rep performance across 6 metrics) were *not* squeezed in — that screen says "best on desktop" and links out. Usage data later: mobile completes the top task 2× faster than the old pinch-zoom grid did; nobody missed the columns that didn't fit.

## Evaluation Rubric

Score 1–10:

- **1–2**: Schema-order columns; client-side sort over paginated data; no selection model; blank nulls; happy-path states only.
- **3–4**: Reasonable columns but alignment/format inconsistent; server sort partial; select-all ambiguous; filters invisible; mobile is a shrunken grid.
- **5–6**: Task-ranked columns; server-truthful operations; visible filter/sort state in URL; risk-scaled confirms on main actions; core states designed.
- **7–8**: Full checklist: collision-free interaction zones, cross-page selection semantics, async bulk with failure reports, sticky anchors, keyboard minimum, fixture-tested extremes.
- **9–10**: Additionally: persisted per-user layout/density; precomputed honest sortables; deep-linkable rows; live-update buffering; usage-instrumented pruning; the export-to-Excel rate measurably drops because the table finally does the job.
