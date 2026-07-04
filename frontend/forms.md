# Forms

## Purpose

Build forms that never lose user input, validate at the right moments, map server errors back to fields, and stay accessible — the discipline behind the highest-friction surface in any product.

## When to use

- Any input surface: signup, checkout, settings, multi-step wizards, inline edits, bulk editors.
- Reviewing form code for validation timing, error handling, or submission behavior.
- Debugging "users abandon this form" or "support keeps getting validation complaints."
- Choosing a form library or designing form state.

## Goals

- User input is never lost — not by navigation, errors, re-renders, or crashes.
- Validation timing follows "reward early, punish late."
- Every server-side failure lands next to the field that caused it, with recovery instructions.
- The form is operable by keyboard and screen reader without special effort.

## Inputs

- Field inventory with types, constraints, and which constraints only the server knows (uniqueness, inventory, credit checks).
- Error catalog from the API (field-mappable codes vs global failures).
- Flow context: single form, multi-step, autosaved settings, inline edit?
- Data reality: prefilled? live-updating underneath? concurrent editors?

## Outputs

- Form with schema-based validation shared or aligned with the server's rules.
- Submission state machine (idle → submitting → success | field-errors | global-error) with defined UI per state.
- Error copy per validation rule, written to say how to fix.
- Draft-persistence / unsaved-changes policy implemented and stated.

## Expert Mental Model

- **A form is a state machine with a human in the loop.** Field values, per-field touched/dirty/error, and submission status — model these explicitly and the "weird form bugs" evaporate. Most form chaos is these states being implicit or contradictory.
- **Validation timing is an emotional design problem.** Yelling "invalid email" after one keystroke trains resentment. The expert default — "reward early, punish late": validate on blur for first contact with a field; once a field has shown an error, re-validate on every keystroke so the error disappears the moment it's fixed. Never block typing; never show errors for untouched fields on load.
- **The server is the only real validator.** Client validation is UX (fast feedback); server validation is truth (security, uniqueness, business rules). Design the round trip: server returns field-mapped error codes → client maps them onto fields as if they were local errors. Forms that show "Something went wrong" for a taken username have a missing contract, not a missing feature.
- **Losing input is the cardinal sin.** A failed submit that clears fields, a redirect that discards a half-written 20-minute answer, a validation error that wipes the password field's siblings — users forgive slow, they don't forgive retyping. Every design decision gets checked against "can this destroy typing?"
- **Every field is friction; earn it.** Experts fight for shorter forms before better forms: infer what you can (country from geo, name casing), defer what you don't need now (progressive profiling), delete what nobody uses.

## Workflow

1. **Trim the field list.** For each field: needed now, at all, or inferable? Move nice-to-haves out. Defaults for everything defaultable (sensible, not sneaky).
2. **Define the schema once** (types + constraints + messages) in a schema library; derive both client validation and TypeScript types from it. Align names/rules with the server's schema so error mapping is mechanical.
3. **Choose state ownership**: form library for >3 fields or any dynamic structure; local state for trivial cases. Keep form state out of global stores.
4. **Implement validation timing**: touched-on-blur → error shows; error-present → validate-on-change; on submit → validate all, focus the first invalid field, scroll it into view.
5. **Async validation** (username taken, address check): debounce ~300–500 ms, cancel stale requests, show a pending indicator in-field, and re-run on submit (the debounced check may not have fired).
6. **Design submission states**: disable double-submit (button busy-state, not just disabled — show progress), keep all values on failure, map field errors from the response (`{errors: [{field: "email", code: "taken"}]}` → set field error), global banner only for truly global failures (network, 500) with retry that preserves input.
7. **Write error copy per rule**: state what to do, not what's wrong. "Password needs at least 12 characters" not "Invalid password." Include format examples where formats exist.
8. **Handle the unsaved-changes lifecycle**: warn on navigation with dirty state (router guard + `beforeunload`), or autosave drafts (debounced, with visible "Saved" state) for long-form content. Decide per form; write it down.
9. **Wire accessibility as structure**: every input has a `<label>` (not placeholder-as-label); errors linked via `aria-describedby` + `aria-invalid`; error summary announced (`role="alert"`/live region) on submit failure; logical tab order; Enter submits where expected.
10. **Test the ugly paths**: submit → server field error → fix → resubmit; double-click submit; slow network submit + navigate; paste into masked fields; autofill.

## Decision Tree

- If the form edits persistent settings → autosave per field or per section (with saved/saving indicators, undo where possible); explicit Save buttons for grouped or risky changes.
- Else if long-form content (posts, applications) → draft autosave to storage/server every few seconds when dirty + restore-on-return; never rely on `beforeunload` alone.
- Else (transactional: signup, checkout) → explicit submit, dirty-navigation guard, full input preservation on any failure.

Validation placement per rule:
- If checkable locally (format, length, required) → client schema + server re-check.
- Else if requires server knowledge (uniqueness, funds) → async in-field check where UX warrants + authoritative check at submit; always handle the submit-time failure path since the async check races.
- If rules depend on other fields (end date > start date) → validate at the group level, show error at the field the user will fix, re-validate when *either* field changes.

Multi-step (wizard) decisions:
- Validate per step before advancing; allow backward navigation freely with state preserved.
- Persist step data (URL for position, storage/server for values) so refresh doesn't reset the journey.
- Review step before final submit for consequential flows (orders, applications).
- If steps are independent sections → consider one scrollable form with a sticky summary instead; wizards tax orientation.

Disabled submit button?
- Prefer enabled submit that validates and focuses the first error — disabled buttons don't explain *why* and users hammer them confused. If you disable, pair with a visible reason near the button. (Contested in the field; preserving input + explaining beats both extremes.)

## Heuristics

- Placeholder is not a label: it vanishes on type, fails contrast, and screen readers treat it inconsistently. Label above the field wins for scanning and translation growth.
- Match keyboard to field on mobile: `inputmode="numeric"` for codes, `type="email"`, `autocomplete` attributes everywhere (they also power password managers — never disable paste or autofill; that fights users' security tools).
- Trim and normalize on blur/server, not per keystroke (mid-typing normalization moves cursors). Accept `" x@y.com "` — the space was not the user's message to you.
- Phone/card/date masks: format on blur or with caret-preserving libraries; naive per-keystroke re-format = cursor teleportation.
- Error placement: adjacent to the field (below, by convention), plus a summary at top for long forms — the summary links to fields.
- Optional is the exception: mark optional fields "(optional)"; marking required with asterisks everywhere is noise when 90% is required.
- Group with `fieldset`/headings past ~7 fields; humans parse chunks.
- Select with >10 options wants search; >2 and <6 mutually exclusive options often wants radios (visible options, zero clicks to see them).
- Never validate emptiness on blur for a field the user tabbed *through* (touched-but-untyped skips required-error until submit — tabbing past isn't a mistake yet).
- Preserve scroll and focus after error render; focus management after submit-failure is the difference between "fix and go" and hunting.

## Quality Checklist

- [ ] No path destroys input: submit failure, validation, navigation warn/draft, re-render (verified by trying).
- [ ] Validation: blur-then-change timing; untouched fields silent; submit focuses first error.
- [ ] Server errors field-mapped; global failures preserve input with retry.
- [ ] Double-submit impossible; submitting state visible.
- [ ] Error copy says how to fix; formats shown by example.
- [ ] Labels real; errors `aria-describedby`-linked; `aria-invalid` set; summary announced; keyboard-complete.
- [ ] `autocomplete`/`inputmode`/`type` correct per field; paste and autofill work.
- [ ] Async validation debounced, cancelled, pending-indicated, re-checked at submit.
- [ ] Multi-step: per-step validation, free back-nav, refresh-safe persistence.
- [ ] Unsaved-changes policy explicit (guard or autosave) and tested.

## Failure Modes

- **The clearing form**: submit fails → fields reset (page reload semantics, or `key` change on error state). Users retype once, never twice — they leave.
- **Premature validation**: errors on first keystroke or on load; user starts typing email and reads "invalid email" at `j`. Trains users to ignore red.
- **Unmapped server errors**: API knows `email_taken`; UI shows "Error occurred." The contract existed; nobody wired it.
- **Masked-field paste rejection**: user pastes card number with spaces → rejected or mangled. Strip on input; accept human formats.
- **Double-submit orders**: no busy state; slow network; two clicks; two charges (pair with server idempotency keys — the form's busy state is UX, the key is truth).
- **Zombie validation state**: error set by async check never cleared because the fix path didn't re-trigger it.
- **beforeunload as the only draft strategy**: mobile browsers and crashes don't fire it; the 40-minute answer dies.
- **Wizard reset on refresh**: step in memory only; F5 → step 1 of 6, empty. Rage-quit fuel.
- **Accessibility afterthought**: div-buttons, placeholder labels, errors announced to no one — fails real users and audits at retrofit-price.

## Edge Cases

- **Autofill events**: browsers fill without keystrokes — validation must run on `change`/`input` from autofill, and styling shouldn't assume typing (`:autofill` quirks).
- **IME composition** (CJK input): validating/normalizing mid-composition corrupts input; respect `compositionstart/end`.
- **Unicode names and addresses**: single-letter names, no last name, RTL text, post codes with letters — validate structure only where a real system constraint exists; "must be at least 2 letters" is a bug report from someone named "O".
- **Copy-paste of formatted data**: currency `"1,234.56"`, phone `"+1 (555) ..."` — parse generously, store canonically.
- **Concurrent edits**: two tabs, or admin-edits-while-user-edits — detect via version/updated_at at submit; offer merge or overwrite explicitly.
- **Prefilled-from-query forms**: query refetch mid-edit must not clobber dirty fields (isolate the draft; merge policy explicit).
- **Timezone-sensitive date fields**: "date of birth" is a calendar date (no TZ math ever); "appointment time" is zoned — mixing the two shifts birthdays across midnight.
- **File inputs in drafts**: files can't serialize to storage — upload immediately to temp storage with the draft referencing tokens, or clearly exclude from restore.

## Tradeoffs

- **Autosave vs explicit save**: autosave prevents loss but makes "cancel/undo" harder and surprises with half-committed state; explicit save is predictable but loseable. Settings: autosave-per-control with undo; documents: autosave drafts + explicit publish; transactions: explicit only.
- **Inline async checks vs submit-time only**: inline (username taken) saves a round-trip of frustration but adds jitter, race handling, and server load; submit-time is calm but late. Inline for identity-defining fields, submit-time for the rest.
- **Client validation richness vs duplication drift**: duplicating every server rule client-side drifts; validating nothing client-side is laggy UX. Sharing one schema (or codegen from the API contract) dissolves the tradeoff where feasible; otherwise duplicate only high-frequency rules.
- **Single long form vs wizard**: long form = full context, orientation, easy review; wizard = focus, lower initial intimidation, mobile-friendlier. Wizard when steps are conditional or genuinely sequential; long form with sections otherwise.
- **Strict input formats vs generous parsing**: strictness simplifies code and corrupts UX; generosity ("accept anything plausible, canonicalize server-side") costs parsing effort once and pays per user forever.

## Optimization Strategies

- Measure field-level analytics on high-value forms: time-in-field, error rates per field, abandonment step — the worst field is usually one specific field, and it's usually a format or an unnecessary question.
- Cut a field, convert a field to inferred, or default a field — each beats any validation polish for completion rates.
- Uncontrolled inputs + on-demand reads (register-style form libs) for very large forms; controlled-everything re-renders 60 fields per keystroke.
- Prefetch/preload the submit path (warm the endpoint, load the next step's chunk) so success feels instant.
- Optimistic inline edits for low-risk fields (rename, toggle) with rollback+toast — settings pages feel 10× faster.
- Test with a password manager, mobile keyboard, and screen reader once per form — 15 minutes that catches the class of bugs analytics can't name.

## Self Review

- What are all the ways this form can lose input? Did I try each one (fail submit, navigate away, refresh mid-wizard, crash tab with draft)?
- Type an invalid email, tab away, come back, fix it — does the error clear at the fixing keystroke?
- Submit with the server returning `field: taken` — does the error land on the field, with the value intact and focus moved?
- Can I complete the entire form with only a keyboard? Does a screen reader announce each error?
- Paste real-world formatted data into phone/card/amount fields — survives?
- Is every field defensible ("we need it now for X"), or am I hoarding?
- Double-click submit on a throttled network — how many requests fired?

## Examples

**1. Signup form, full timing discipline.**
Email field: silent while typing (untouched); on blur → format check, then debounced 400 ms availability check with in-field spinner; error shown → revalidates per keystroke, clears at the fixing character. Submit: all-fields validate → first error focused; server `email_taken` (raced past the async check) maps onto the field with "This email already has an account — log in instead?" + link. Password field: requirements listed upfront as a live checklist (turns green as met) — punishment converted to reward. Nothing clears on any failure.

**2. Settings page as autosave field-grid.**
Each control saves on change (debounced 800 ms for text): pending dot → "Saved" tick → error state with retry, value preserved and marked unsynced. Risky group (email/password) sits behind explicit save + reauthentication. Undo toast on destructive toggles. No global Save button ambiguity, no unsaved-changes modal — the policy is visible per control.

**3. The wizard that respects refresh.**
Insurance quote, 5 steps. Position in URL (`/quote/step-3`), values in server-side draft (created at step 1, PATCHed per step), per-step validation, back always free, review step with edit-links before submit. User's browser crashes at step 4; returning link restores to step 4 with data. Support tickets about "had to start over" go to zero — measured, because step-abandonment analytics existed from launch.

**4. Server-error contract wiring.**
API error shape standardized: `{errors: [{field: "shipping.postal_code", code: "invalid_for_country", message: "..."}]}`. Client: one mapper walks `errors[]`, `setError(field, message)` per entry, aggregates unmapped codes into a top banner with request-id, focuses the first mapped field. Every future form inherits correct server-error UX by using the mapper — the fix was a contract + one function, not per-form heroics.

## Evaluation Rubric

Score 1–10:

- **1–2**: Input loss possible on common paths; validation fires on keystroke-one or only after submit; server errors unmapped; placeholder labels; double-submit live.
- **3–4**: Library used but timing defaults unexamined; errors show but copy unhelpful; masks fight paste; wizard resets on refresh.
- **5–6**: Blur-then-change timing; field-mapped server errors on main forms; busy-state submits; labels and basic aria; drafts or guards on long forms.
- **7–8**: Full checklist; schema shared/aligned with server; async validation raced correctly; a11y verified with keyboard+reader; ugly-path tests exist.
- **9–10**: Additionally: field-level analytics driving field-count reduction; concurrent-edit policy; IME/unicode/autofill edges handled; the input-loss review is a written artifact; completion-rate improvements measured, not assumed.
