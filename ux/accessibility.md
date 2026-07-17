# Accessibility

## Purpose

Build interfaces that work for people using screen readers, keyboards, voice control, magnification, and every other way humans actually operate software — by reaching for semantics first, ARIA last, and testing with the actual assistive stack — so accessibility is a property of the architecture, not a remediation sprint before an audit.

## When to use

- Building any interactive UI: forms, modals, menus, tables, custom widgets (i.e., always).
- Replacing a native element (`<select>`, `<button>`, checkbox) with a custom component.
- An accessibility audit, lawsuit risk, or procurement requirement (VPAT, WCAG conformance) has arrived.
- Reviewing designs: color choices, focus states, touch targets, motion.
- Keyboard users, screen-reader users, or zoom users report the app is unusable — or nobody has ever checked.

## Goals

- Every interactive element reachable, operable, and understandable by keyboard alone — visible focus, logical order, no traps.
- The accessibility tree tells the same story as the pixels: names, roles, states programmatically determinable.
- Content readable at 200% zoom and WCAG AA contrast; nothing conveyed by color alone.
- Dynamic changes (validation errors, async results, route changes) announced, not just painted.
- WCAG 2.1/2.2 AA as the floor — met by construction, verified by both automated and manual passes.

## Inputs

- The interaction inventory: every widget, flow, and state the UI presents (see interface-states — error and loading states need accessible treatment too).
- Design tokens: color pairs and their contrast ratios (see color), type sizes (see typography), focus styles, motion (see motion).
- The compliance context: WCAG level, legal jurisdiction, procurement requirements.
- The component library's existing semantics — what the framework gives free vs what custom components must reimplement.

## Outputs

- Semantic markup with a coherent heading outline, landmarks, and native elements doing native jobs.
- Keyboard interaction specs per custom widget (what Tab, Arrow, Escape, Enter do), implemented and tested.
- Focus management wired for every dynamic transition: modals, deletions, route changes, async updates.
- An accessibility test layer: automated checks in CI + a manual keyboard/screen-reader pass per feature.

## Expert Mental Model

- **The accessibility tree is a parallel UI — and it's the one assistive tech actually uses.** Browsers derive a tree of names, roles, and states from your markup; screen readers navigate *that*, not your pixels. A `<div onClick>` renders identically to a `<button>` and is invisible to that tree: no role, no keyboard, no announcement. Experts think in both renderings at once — every widget has a visual state and an accessible state, and bugs live where they disagree (the toggle that looks pressed but doesn't expose `aria-pressed`; the error painted red that never reaches the tree).
- **Semantics first; ARIA is the fallback, not the toolkit.** Native elements (`<button>`, `<select>`, `<a>`, `<input>`, `<dialog>`) ship with keyboard handling, focus behavior, states, and announcements — decades of platform work for free. ARIA provides *only* the announcement layer: it makes promises to assistive tech ("this is a listbox") that *you* must keep with focus management and key handlers. The first rule of ARIA is don't use ARIA when HTML suffices; the second is that wrong ARIA is worse than none — a `role="button"` that ignores Space is a lie told directly to a screen reader.
- **Keyboard operability is the load-bearing test.** The keyboard path exercises focus order, focus visibility, and operability — the same machinery switch controls and voice access rely on. If you can Tab to everything interactive, operate it, see where you are, and never get trapped, most of the interaction layer is sound. If you can't, no amount of ARIA labels repairs it. Corollary: focus is state you must manage (see state-management) — every DOM mutation that removes or reveals content has to answer "where does focus go now?"
- **Accessibility is constraint-driven design, and the constraints improve the design.** Contrast requirements produce readable palettes (see color); "don't rely on color alone" produces redundant encoding that helps everyone in sunlight; visible focus helps every power user; reduced-motion support respects vestibular disorders and preference alike (see motion); clear labels and error recovery are just good forms (see forms). Teams that treat WCAG as a checklist bolt things on; teams that internalize the constraints ship better interfaces for everyone — curb cuts, systematically.
- **Automated tools find ~30–40% of issues; the rest requires hands and ears.** Axe-class scanners catch missing alt text, contrast failures, and ARIA misuse — mechanically checkable facts. They cannot tell whether the focus order makes sense, whether the announcement is comprehensible, whether the alt text is *useful*, or whether the custom combobox is operable. The manual pass — keyboard-only run, then a screen-reader run (VoiceOver/NVDA) — is not optional polish; it's the other 60%.
- **Accessibility debt compounds like all debt, but remediation is worst-case expensive.** A semantic foundation costs ~nothing extra at build time; retrofitting a div-soup app is an archaeology project (see refactoring: same economics, higher interest). The cheap moment is the component library: fix the shared Button/Modal/Select once and every consumer inherits it (see component-architecture; design-language tokens for the visual side).

## Workflow

1. **Start from document structure**: one `<h1>`, headings in outline order (never skipped for styling — see visual-hierarchy for the visual layer of the same concern), landmarks (`<main>`, `<nav>`, `<header>`) so users can jump regions.
2. **Use native elements for native jobs**: links navigate, buttons act, inputs collect. Every custom replacement of a native control is a project (keyboard spec + ARIA states + focus management) — budget it as one or don't replace the native.
3. **Label everything programmatically**: visible `<label>` for inputs (see forms), accessible names for icon-only buttons (`aria-label`), `alt` that serves the *purpose* ("Delete invoice" not "trash icon"; decorative images get `alt=""`).
4. **Implement the keyboard layer per widget**: Tab reaches it, Enter/Space activates, Arrows navigate within composites (menus, tabs, radio groups), Escape dismisses. Follow the ARIA Authoring Practices patterns — they're specs, not suggestions.
5. **Manage focus across every transition**: modal opens → focus enters it and is trapped until close → returns to the trigger. Item deleted → focus to the next item or list. Route change in a SPA → focus the new page's heading and announce it. Async content replacing a busy region → focus or announce, never silently swap.
6. **Announce dynamic changes**: validation errors linked via `aria-describedby` and announced; toast/status updates through `aria-live="polite"` regions (sparingly — a chatty live region is unusable); loading and completion states surfaced, not just spun (see interface-states).
7. **Verify the visual layer**: AA contrast (4.5:1 text, 3:1 large text and UI components — see color), 200% zoom without horizontal scroll or clipped content (see layout-and-spacing: relative units), touch targets ≥ 44px, `prefers-reduced-motion` honored (see motion).
8. **Wire automated checks into CI** (axe on component tests and E2E pages; lint rules like eslint-plugin-jsx-a11y at commit time — see ci-cd) so regressions are caught at the cheap gate.
9. **Run the manual pass per feature**: full keyboard-only journey, then a screen-reader journey; fix what's incomprehensible, not just what's broken.
10. **Encode wins into the component library**: every fixed pattern (accessible modal, combobox, table sort) becomes the shared component so the class is killed, not the instance (see component-architecture; the class-fix instinct from root-cause-analysis applies).

## Decision Tree

- If choosing an element for an interaction → does a native element do this? Use it and style it. Only when styling genuinely can't be achieved (rare post-`appearance`/`::backdrop`) → custom, with the full keyboard + ARIA spec implemented.
- If it navigates → `<a href>`; if it acts → `<button>`. The styled-link-as-button (and vice versa) breaks middle-click, keyboard expectations, and announcements.
- If an image carries information → alt text stating the information; if decorative → `alt=""` (missing alt makes readers announce the filename); if it's a chart → a text alternative carrying the *conclusion* plus access to the data (see dashboard-ux; data-tables).
- If building a composite widget (menu, tabs, combobox, tree) → implement the corresponding ARIA Authoring Practices pattern: roving tabindex or `aria-activedescendant`, the specified key map, the specified states — or use a headless library that has (adopt > build here; the edge cases are deep).
- If content appears/disappears dynamically → will a non-sighted user know? Errors → `aria-describedby` + announcement; new results → live region or focus move; removed content that held focus → move focus deliberately.
- If using color to signal something (error, status, selection) → add a second channel: icon, text, weight, underline (see color: redundant encoding; interface-states).
- If motion/animation is meaningful → provide the `prefers-reduced-motion` variant that preserves the information without the movement (see motion).
- If text overlays images or gradients → guarantee contrast structurally (scrim, solid panel), not by hoping the image cooperates (see color).
- If a third-party widget is inaccessible → wrap-and-fix if shallow, replace if deep, and file the issue — but your users experience *your* app; "vendor's fault" isn't an exemption (see research: evaluate a11y before adopting).
- If audit findings arrive → fix by class through the shared components, not instance-by-instance through 200 pages.

## Heuristics

- Unplug the mouse for ten minutes on every feature — the fastest audit that exists; if you get stuck or lost, so does everyone relying on the keyboard.
- The Tab count is a UX metric: 40 tab-stops before the main content means you need a skip link and fewer focusable decorations.
- Focus outline is never `outline: none` without a visible replacement — the invisible-focus app is unusable by keyboard, full stop.
- Reading order = DOM order: CSS that reorders visually (flex `order`, grid placement) leaves screen readers and Tab reading the DOM's story — keep them aligned (see layout-and-spacing).
- One `<h1>`; headings are structure, not styling — style with classes, outline with levels.
- `aria-label` on a `<div>` does nothing without a role; role without behavior is a broken promise; the triad is role + states + keyboard, always shipped together.
- Placeholder is not a label: it vanishes on input and fails contrast (see forms).
- Disabled buttons are invisible to Tab — for "can't submit yet," prefer enabled-with-validation-feedback over silently unreachable (see forms; interface-states).
- Zoom to 200% and use the app — text should reflow, not clip or overlap (see typography: relative units, line-height).
- Live regions announce *changes*, not existence: render the container early, mutate its content when the news happens.
- Test the accessible name of every icon button in the tree devtools — "button, unlabeled" is the most common finding in the wild.
- Auto-playing motion, carousels, and videos need pause controls; auto-anything that moves content under a user's focus is hostile.

## Quality Checklist

- [ ] Full keyboard operability: everything reachable, operable, visible focus, no traps, logical order.
- [ ] Heading outline coherent; landmarks present; skip link where nav is long.
- [ ] Every input labeled; every icon-only control named; every image alt-texted by purpose.
- [ ] Custom widgets follow ARIA Authoring Practices key maps and states — or are headless-library-backed.
- [ ] Focus managed across modals, deletions, route changes, async swaps.
- [ ] Errors and dynamic updates announced (`aria-describedby`, live regions), not just painted.
- [ ] AA contrast verified from tokens; nothing conveyed by color alone.
- [ ] 200% zoom usable; touch targets ≥ 44px; `prefers-reduced-motion` honored.
- [ ] Automated a11y checks in CI; lint rules at commit.
- [ ] Manual keyboard + screen-reader pass done on the feature before ship.

## Failure Modes

- **Div soup**: click handlers on divs everywhere — no roles, no keyboard, no announcements; the app is pixels only. The retrofit costs 50× the doing-it-right.
- **ARIA as paint**: roles sprinkled to satisfy a scanner — `role="menu"` on a nav list (imposing a key map that was never implemented), `aria-live` on everything (announcement spam), labels that contradict visible text (voice-control users can't target what they see).
- **The focus black hole**: modal opens, focus stays behind it; Tab cycles the obscured page; Escape does nothing; the close button is a hoverable div. One widget, four failures, complete lockout.
- **Scanner-green complacency**: axe passes, ship it — while the focus order is nonsense and the combobox is inoperable; the 60% was never tested.
- **Contrast vibes**: light-gray-on-white aesthetic shipped unmeasured; fails 4.5:1 by half; every low-vision user, and everyone outdoors, squints (see color; typography).
- **The silent update**: form submits, error appears in red at the top, screen reader hears nothing; the user waits, then re-submits (see forms: error announcement is part of the error).
- **Remediation-sprint theater**: audit findings patched page-by-page while the shared components keep manufacturing the same violations; next audit, same findings (fix the class — the component).
- **Keyboard-trap embeds**: the third-party date picker or chat widget that focus enters and cannot leave — the single WCAG failure that hard-blocks *everything* after it.

## Edge Cases

- **Infinite scroll and virtualized lists**: focus and screen-reader position break when DOM nodes recycle — provide "load more" alternatives or manage `aria-setsize`/`aria-posinset`, and never trap Tab inside a 10,000-row virtual list (see data-tables; frontend-performance).
- **Drag-and-drop**: pointer-only reordering excludes keyboard and switch users — ship the keyboard equivalent (select, move-up/down commands) and announce the result; WCAG 2.2 makes single-pointer alternatives explicit.
- **Charts and dashboards**: the visualization is one rendering; provide the conclusion in text and the data in an accessible table — "the chart is decoration for the sentence" is the accessible framing (see dashboard-ux).
- **CAPTCHA and liveness checks**: classic full blockers — prefer invisible/risk-based approaches; every human-test needs an accessible channel.
- **Canvas/WebGL surfaces**: invisible to the tree by construction — parallel DOM for controls and state, keyboard handlers at the canvas boundary; budget this or reconsider canvas (see the same tradeoff in frontend-performance).
- **Timed sessions and auto-logout**: screen-reader and switch users are slower by necessity — warn accessibly, allow extension (WCAG timing-adjustable), and never discard work on expiry (see forms: preserve input).
- **Internationalized and bidirectional text**: `lang` attributes drive pronunciation; RTL flips reading and focus order expectations — logical CSS properties and `lang` per content region (see typography).
- **Reduced motion ≠ no feedback**: `prefers-reduced-motion` users still need state-change feedback — swap the slide for a fade or instant change with announcement; removing the transition *and* the signal is a regression (see motion).

## Tradeoffs

- **Native-and-plain vs custom-and-branded**: native controls are robust and dated-looking; custom controls are on-brand and a permanent maintenance contract. Middle path: headless a11y libraries (behavior solved, styling free). Reserve full-custom for widgets that are the product.
- **Announcement richness vs verbosity**: every state announced is thorough and exhausting; screen-reader UX is an economy of attention — announce what changed and matters, let structure carry the rest. Test with actual users where stakes justify it.
- **Strict conformance vs usable-first**: chasing AAA line-items on a flow whose focus order is broken optimizes the audit, not the user. Sequence: operable keyboard paths and comprehensible announcements first, then conformance line-items — though in procurement/legal contexts the checklist has its own deadlines (see compliance-and-privacy).
- **Overlay/widget "solutions" vs real fixes**: accessibility overlays promise compliance via injected script — they don't fix the tree, often worsen screen-reader UX, and are litigation-tested failures. The money spends better on the component library.
- **Performance vs assistive richness**: deeply annotated live regions and large accessible DOMs have costs (see frontend-performance) — but the tree is not the bottleneck in real apps; don't trade a11y for microseconds unprofiled.

## Optimization Strategies

- Fix the component library first: accessible Button, Field, Modal, Select, Table once → every product surface inherits; new violations become structurally hard to write (see component-architecture).
- Put the linters at the cheapest gate: jsx-a11y-class rules catch missing alt/labels/roles at commit time for free (see ci-cd).
- Add axe assertions to existing component tests and E2E smokes — zero-new-infrastructure automation (see testing-strategy: cheapest sufficient layer).
- Make the keyboard pass a PR-checklist item for UI changes — ten minutes, catches the majority of interaction failures before review.
- Teach one screen reader to the team (VoiceOver is already on every Mac): the developer who has *heard* their app writes different markup afterward — same mechanism as attacker-eyes in security.
- Track a11y findings like defects with classes and regression tests, not like an annual audit event (see root-cause-analysis: class-fixes).
- Buy the deep widgets: combobox, date picker, data grid from accessibility-serious vendors/libraries; the edge-case matrix (screen reader × browser × input mode) is bigger than your team's testing budget (see research: adopt-vs-build).

## Self Review

- Can I complete every flow I just built with the keyboard alone — and does focus visibly travel a sensible path?
- Does the accessibility tree tell the same story as the screen: names, roles, states, for every control?
- When content changed dynamically, what did a screen-reader user hear? (Actually listen.)
- What happens at 200% zoom? On `prefers-reduced-motion`? Without color vision?
- Is every ARIA attribute I added backed by implemented behavior — or is any of it aspirational?
- Where does focus go when this modal closes, this row deletes, this route changes?
- Did I fix the shared component, or patch one instance of a class that will recur?
- If a screen-reader user filed a bug on this feature, would it be the first time anyone had tried their path?

## Examples

**1. The custom dropdown, paid in full.**
Design rejects the native `<select>`. The team prices the real cost: listbox pattern from ARIA Authoring Practices — trigger button with `aria-expanded`/`aria-haspopup`, popup `role="listbox"` with `aria-activedescendant`, full key map (arrows, Home/End, type-ahead, Enter selects, Escape restores), focus return to trigger, `aria-selected` states, axe + keyboard tests. Two days, done once in the component library — every product dropdown inherits it. The counterfactual shipped in an hour and was a div that mouse users alone could operate; the difference is 5% of users locked out of *every form in the app*.

**2. The silent error, made audible.**
Support ticket: "blind user re-submitted payment three times." The form paints a red banner on failure; the tree never hears it. Fix per forms + interface-states: errors summarized in a focused alert region on submit failure (focus moves to the summary, which links each error to its field), inline errors tied via `aria-describedby`, submit button state announced. The re-submission class disappears — and sighted-user support tickets about "did it work?" drop too, because the same fix added an explicit success state. Curb cuts.

**3. Retrofit triage after an audit.**
A 190-finding audit lands on a five-year-old SPA. Instead of page-by-page whack-a-mole: findings clustered by class → 80% trace to six shared components (unlabeled icon buttons, the modal, the custom checkbox, table sort, toasts, focus styles). Fix order: keyboard traps first (hard blockers), then the six components (kills ~150 findings at the source), then per-page leftovers by traffic. CI gains axe checks + lint rules so the classes can't silently return (see ci-cd). The next audit: 11 findings, all new features from one team that had bypassed the component library — which is a process finding, and gets a process fix.

## Evaluation Rubric

Score 1–10:

- **1–2**: Div soup; mouse-only operability; no labels or alt text; focus invisible or removed; color the only signal; never tested with keyboard or reader.
- **3–4**: Semantics where the framework defaults provided them; ARIA sprinkled unverified; contrast unmeasured; dynamic updates silent; a11y addressed only when a complaint or audit arrives.
- **5–6**: Native-first markup, labeled controls, coherent headings; keyboard works for main flows; focus managed in modals; AA contrast from tokens; automated checks in CI.
- **7–8**: Full checklist: Authoring-Practices-compliant custom widgets, focus management across all transitions, announcements for dynamic changes, zoom/motion/touch handled, manual keyboard + reader pass per feature, fixes landed in shared components.
- **9–10**: Additionally: a11y is architectural — the component library makes violations hard to express; findings tracked as classes with regression tests; team fluent in at least one screen reader; periodic testing with actual assistive-tech users — and the pattern of audit findings trending toward zero because the sources, not the symptoms, were fixed.
