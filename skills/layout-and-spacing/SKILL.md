---
name: layout-and-spacing
description: "Use when laying out screens, a UI 'looks off' or cluttered, defining spacing tokens/grids/breakpoints, reviewing responsive behavior, or content breaks the layout (long names, translations, empty lists) — proximity, alignment, fluid-first responsive design."
---

# Layout & Spacing

## Purpose

Structure screens with deliberate geometry — spacing scales, grids, alignment, and responsive behavior that adapts by design rather than by accident — so interfaces read as composed rather than assembled, and layouts survive real content, real translations, and real screens.

## When to use

- Laying out any new screen, page, or component arrangement.
- A UI "looks off" and nobody can say why (it's usually spacing and alignment — see visual-hierarchy for the attention side).
- Defining spacing tokens, grid systems, or breakpoint strategy for a design system (see design-language).
- Reviewing responsive behavior: the tablet view nobody designed, the sidebar at 1280px, the modal on a phone.
- Content broke the layout: long names, translations, empty sections, 4K monitors.

## Goals

- All spacing drawn from one scale (tokens), applied by rule — related things closer, separate things farther.
- Alignment lines are few and intentional; every element snaps to something.
- Layouts are content-driven and range-tested: no width between 320px and 4K renders broken.
- Reading order, tab order, and visual order agree (see accessibility).
- The layout system is documented once and reused, not re-derived per screen.

## Inputs

- The content's real shape: actual copy lengths, image ratios, data ranges, worst cases (the 47-character German compound noun, the empty list, the 40-item list — see interface-states).
- The type scale and line-height rhythm the spacing must harmonize with (see typography).
- Device/viewport reality from analytics: what widths actually visit.
- The product's density needs: consumer-airy vs ops-dense (see dashboard-ux; data-tables).

## Outputs

- A tokenized spacing scale with semantic assignments (component padding, stack gaps, section gaps).
- A macro-layout with named regions, a grid keeping their edges shared, and a capped content measure.
- Per-region responsive behavior: fluid techniques by default, content-derived breakpoints where arrangement must change, container queries for reused components.
- Range-tested layouts: every container's overflow answer (wrap/truncate/scroll/reflow) chosen and verified against worst-case content.

## Expert Mental Model

- **Space is meaning: proximity is the strongest grouping signal you have.** Before color, borders, or headings, users parse a screen by distance — things near each other belong together (Gestalt's oldest law). This gives the working rule: *space within a group < space between groups*, applied recursively (field-to-its-label < field-to-next-field < section-to-section). Most "cluttered" UIs aren't over-full; they're *evenly spaced* — uniform gaps carry zero grouping information, so every element floats alone and the user pays the parsing tax (see visual-hierarchy: the attention-layer of the same failure). Borders and boxes are the fallback grouping tool; spacing is the primary one — remove the box, widen the gap, and the design usually improves.
- **A spacing scale turns judgment calls into system output.** Pixel-by-eye spacing produces 13px here, 15px there — micro-inconsistencies that read as "unpolished" without being nameable. A geometric-ish scale (4/8/12/16/24/32/48/64) shrinks the decision space: you choose a *step*, not a number, and adjacent steps are visibly different (24 vs 32 reads as intentional; 24 vs 26 reads as error). Tokenize it (see design-language) and the scale becomes enforceable in review — "that's not a token" is a faster conversation than "that feels tight."
- **Grids are alignment infrastructure, not aesthetic ideology.** The value of a column grid is shared *edges*: elements starting and ending on common lines produce the invisible order that reads as "designed." Count the alignment lines on a screen — strong layouts have few (a text edge, a field edge, maybe two more); weak ones have a dozen near-misses (the 2px-off label column that makes the whole form shimmer). The 12-column tradition survives because it factors well (2/3/4/6 splits), but the grid serves the content: define regions from what the content needs, then use the grid to keep their edges honest. Optical alignment overrides mathematical alignment at the edges — icons, quotes, and circles need nudging past the line to *look* on it.
- **Design for content ranges, not content specimens.** The layout that's "done" with designer-length names ships broken for `Dr. Maria-Theresia von Habsburg-Lothringen` and `李`. Every container holds a range: empty, short, typical, long, absurd — and the layout must have an *answer* per range (wrap, truncate-with-title, scroll, reflow), chosen deliberately (see interface-states: the empty and overflowing states are states; data-tables for the truncation rules). Translation multiplies this: German runs ~35% longer than English, Arabic flips the axis (see typography; the RTL note in accessibility). The professional habit: test layouts with worst-case content *as part of building them*, not as QA's discovery.
- **Responsive design is layout with width as an input, and content sets the breakpoints.** The layout is a function: width in, arrangement out — and the good ones change *arrangement*, not just scale (sidebar → drawer; 3-up cards → carousel-free single column; table → prioritized rows — see data-tables). Breakpoints belong where *your content* breaks (the point where the card row gets cramped), not at device-name folklore (768px is an iPad from 2010, not a law). Modern tools shift the unit of response: flexible units and `minmax`/wrapping handle most adaptation continuously; container queries let components respond to *their* width rather than the viewport's — which is what component reuse actually requires (see component-architecture).
- **Density is a product decision expressed in spacing.** The same components at 4px vs 12px gaps produce a trading terminal or a meditation app. Neither is "right": density trades scannable-at-a-glance volume against parseable-per-item calm — chosen per audience and task frequency (see ux-fundamentals: expert-daily tools earn density; see dashboard-ux). The failure isn't high or low density; it's *unchosen* density — accidental airiness in an ops tool, accidental cramming in a consumer signup. Whitespace is not wasted space; it's the budget the content breathes with — but in a dense tool, generous padding is a tax on every scan.

## Workflow

1. **Inventory the content first**: what must this screen hold, what are each element's real ranges (copy, counts, images), and what's their priority order (see visual-hierarchy; the content inventory precedes the boxes it goes in).
2. **Adopt the spacing scale** (or inherit the system's — see design-language): base unit (4 or 8), steps, and the semantic assignments (component-internal padding, stack gaps, section gaps) written as tokens.
3. **Block the macro-layout**: regions (nav, content, aside, actions) from content needs; choose the grid that keeps their edges shared; set the content column's max-width from line-length comfort (see typography: measure), not from "use all the pixels."
4. **Apply proximity math within regions**: recursive grouping — tightest spacing inside a unit, wider between units, widest between sections; delete boxes/rules that spacing now does the work of.
5. **Establish the alignment lines**: pick the few edges everything snaps to; left-align ragged text blocks to one line; align numbers right in columns (see data-tables); nudge for optical alignment where geometry lies.
6. **Define the responsive behavior per region**: how does each region adapt across the width range — reflow, collapse, hide-behind-disclosure, reorder? Set breakpoints where the content demands them; prefer fluid techniques (wrap, minmax, clamp) that make breakpoints rare; use container queries for components that live in multiple contexts.
7. **Stress-test with range content**: longest names, empty states, 3× items, translated strings, 320px through ultrawide, 200% zoom (see accessibility: reflow is a requirement, not a courtesy).
8. **Reconcile the orders**: visual order after responsive reshuffling must match DOM/tab order (see accessibility) — CSS reordering that diverges from source order is a screen-reader and keyboard trap.
9. **Tokenize and document the decisions**: the scale, the grid, the breakpoint rationale, the per-pattern density rules — into the system so screen two inherits screen one's thinking (see design-language; component-architecture).

## Decision Tree

- If elements feel related but read as separate (or vice versa) → adjust proximity first, borders last: gaps within groups shrink, gaps between groups grow — one step apart on the scale minimum.
- If a screen feels chaotic with nothing nameably wrong → count alignment lines; merge the near-misses onto shared edges; check for uniform-spacing flatness (no grouping rhythm).
- If a container must handle wildly variable content → choose the range answer deliberately: wrap (default for text), truncate + full-on-hover/title (identifiers in constrained rows — see data-tables), scroll (bounded regions with own context), or reflow (cards/grids via wrapping).
- If designing the responsive behavior → can flexible units + wrapping + minmax handle it continuously? Prefer that. Does the *arrangement* need to change? Breakpoint at the content's breaking width. Is it a reused component? Container query, not viewport query.
- If the layout needs to work in a sidebar and a full page → the component responds to its container; if you're branching on viewport width inside a reusable component, the abstraction is wrong (see component-architecture).
- If text lines run long on wide screens → cap the measure (~45–75ch — see typography); wide viewports get margins/multi-column, never 200-character lines.
- If the design wants asymmetry/overlap/broken-grid energy → break the grid *from* a grid: deviations read as intentional only against an established order (see design-language: the same law for style rules); one deliberate violation per view, not a dozen accidents.
- If density is contested → resolve by audience and task frequency (see ux-fundamentals): daily-expert scanning → compact tokens; occasional-consumer deciding → comfortable tokens; and ship density modes only if you'll maintain both (see data-tables).
- If mobile is an afterthought arriving late → invert: rebuild the layout mobile-first (single column, priority order — which forces the priority conversation the desktop layout dodged), then let width *add* arrangement.
- If the layout breaks at one odd width → don't patch with a point breakpoint; find the rigid element (fixed width, no-wrap, absolute positioning) and make it flexible — point patches accumulate into unmaintainable breakpoint soup.

## Heuristics

- Space within < space between, recursively — if you remember one rule, this is the one.
- When in doubt, double it: adjacent scale steps (16 → 24 → 32) read as decisions; ±2px reads as sloppiness.
- Padding before borders: a group defined by whitespace is calmer than one defined by a box; boxes-in-boxes-in-boxes means spacing failed twice.
- Consistent gutters, consistent card padding, consistent stack gaps — the *same* kind of gap gets the same token everywhere or the rhythm dies.
- Left edges do the aligning in LTR interfaces; ragged-right is fine, ragged-left is chaos (see typography: flush-left default).
- Numbers align right, text aligns left, headers align with their columns (see data-tables); centered layouts are for symmetric content (marketing heroes), not for forms (see forms: labels and fields want a hard left line).
- Touch targets ≥44px with breathing room between destructive and routine (see accessibility; ux-fundamentals: slip prevention is spacing too).
- min-width: 0 and overflow rules are part of the layout: flex/grid children default to refusing to shrink below content — the "why is this blowing out" classic.
- Test at 320px, a mid tablet width, your analytics' modal width, and full-wide — the bugs live between the widths you designed at.
- Fixed heights are almost always a bug incubating: content grows, translations grow, zoom grows — let height come from content plus padding.
- The 8px eye: audit any screen by overlaying its gaps — if you find 7 distinct gap sizes in one card, the scale isn't being used, it's being decorated with.
- Vertical rhythm matters most in long-form reading (see typography baseline discussion); in app UIs, consistent stack tokens beat strict baseline grids for effort-to-payoff.

## Quality Checklist

- [ ] All spacing from the token scale; no off-scale one-offs without written reason.
- [ ] Grouping legible from spacing alone (squint test): units, groups, sections distinguishable.
- [ ] Alignment lines few and shared; no near-miss edges; optical corrections applied.
- [ ] Content ranges tested: empty, typical, worst-case, translated; each container has a chosen overflow answer.
- [ ] Fluid-first responsive behavior; breakpoints content-derived and few; reused components container-queried.
- [ ] Measure capped for reading; density chosen per audience, consistently.
- [ ] 320px→ultrawide walkthrough clean; 200% zoom reflows without loss (see accessibility).
- [ ] Visual order = DOM order = tab order after all responsive rearrangement.
- [ ] Touch targets and slip-spacing honored.
- [ ] Decisions tokenized/documented in the system (see design-language).

## Failure Modes

- **Uniform-gap soup**: every element 16px from every other — no grouping signal anywhere; the screen is a list of orphans and the user does the grouping in their head.
- **The 13px special**: spacing by eye per screen — seven near-identical gaps, nothing aligned, and the UI reads "unpolished" in a way stakeholders feel but can't articulate.
- **Specimen-content design**: built with "John Smith" and three perfect cards; production delivers 47-character names, zero cards, and 40 cards — three layouts nobody designed (see interface-states).
- **Device-folklore breakpoints**: 768/1024 set on day one, unexamined; the layout is awkward at 900 where actual users live, and "tablet view" is a broken desktop nobody owns.
- **Breakpoint soup**: point-patches accumulated per bug — 14 breakpoints, interacting, unmaintainable; the rigid element that caused them all still unfixed.
- **The centered form**: labels centered, fields centered, ragged left edges everywhere — every row starts at a different x; the eye re-finds the start of every line (see forms).
- **Desktop-shrunk "mobile"**: the desktop layout scaled down — 9px text, three columns on a phone, horizontal scroll; width treated as zoom instead of as an input that changes arrangement.
- **Box-border archaeology**: grouping attempted with nested cards, rules, and background tints because spacing was never systematized — the UI wears its scaffolding.
- **CSS-order divergence**: grid/flex reordering for visual polish; tab and reader order now tell a different story than the pixels (see accessibility: reading order = DOM order).

## Edge Cases

- **User-generated content extremes**: the URL-as-title, the emoji-only name, the 4000-word comment — layout policy per field (truncation, max-heights with expansion, break-word) decided at design time, because "we'll see what users do" means users decide your layout (see data-tables).
- **Internationalization geometry**: German +35% width, Japanese denser per glyph, Arabic/Hebrew mirroring the entire axis — logical properties (start/end, not left/right), stretch-tested labels (see forms), and RTL as a layout test case, not a translation afterthought (see typography; accessibility).
- **Zoom and OS text scaling**: 200% browser zoom must reflow (WCAG — see accessibility); OS-level font scaling on mobile inflates text inside fixed containers — relative units and content-driven heights are the immunity.
- **Ultrawide and TV**: 3440px viewports turn full-width layouts into neck exercises — max-width the content, use the surplus for margins or genuinely useful secondary panes, never for longer lines (see typography measure).
- **Print and PDF export**: dashboards and invoices get printed (see dashboard-ux); paged media has no scroll — breakable layouts, print styles for the surfaces where it matters (invoices, reports, tickets).
- **Embedded contexts**: your component inside a partner's iframe, a webview, a sidebar — viewport queries lie there; container queries and self-contained spacing are the survival kit (see component-architecture).
- **Split-screen and foldables**: mobile multitasking gives your "phone" layout 320px beside another app; foldables hinge mid-viewport — the fluid-first approach absorbs these; the breakpoint-folklore approach shatters.
- **Keyboard-visible viewports**: mobile keyboards eat 40% of the height — fixed-bottom actions disappear behind them; test forms with the keyboard up (see forms).

## Tradeoffs

- **Density vs breathing room**: information-per-glance vs parse-cost-per-item — decided by audience and task (see the mental model), then *held consistent*; the worst layout is dense here and airy there without reason.
- **Fluid vs stepped adaptation**: fluid layouts (wrap, minmax, clamp) handle every width with less code and less control at any *specific* width; stepped breakpoints give per-width art direction at maintenance cost — fluid for app UI defaults, stepped where marketing needs the pixel-perfect moment.
- **Grid rigor vs content service**: strict 12-column adherence gives cross-screen consistency and occasionally fights what the content wants — the grid is a tool for shared edges, not a compliance regime; deviate deliberately, on system rails (see design-language).
- **Truncation vs wrapping**: truncation preserves geometry and hides information (dangerous for identifiers — see data-tables); wrapping shows everything and breaks row rhythm — choose per data criticality, and never truncate without a full-value affordance.
- **Consistency vs context**: the system's spacing tokens serve most screens; the data-dense exception (see dashboard-ux) may genuinely need its own density tier — add it to the *system* (compact tokens) rather than forking off-system.
- **Container queries vs simplicity**: per-container response is correct for reused components and adds a reasoning layer; for single-context layouts, viewport techniques remain simpler — adopt per component reuse reality, not per fashion.

## Optimization Strategies

- Encode the scale as tokens and lint for raw values (see design-language; ci-cd for the gate): `padding: 13px` should fail review mechanically, not depend on a designer's eye passing by.
- Build stack/cluster/grid layout primitives once (see component-architecture): components that *own* their internal spacing via tokens kill the per-screen re-derivation and most of the 13px specials.
- Keep a worst-case content fixture set (long names, empty, huge counts, German, Arabic) wired into component previews/tests — range-testing becomes free instead of heroic (see testing-strategy: fixtures; interface-states).
- Audit real breakpoint traffic quarterly: analytics' width histogram vs your breakpoints — design where users actually are.
- Do squint-test reviews on new screens: blur the mock; if grouping and priority survive blurring, the spacing is doing its work (see visual-hierarchy: same test, both layers).
- Adopt logical properties and fluid units as defaults in the codebase — i18n and zoom resilience arrive as a side effect instead of a retrofit.

## Self Review

- Can I name the token for every gap on this screen — and does the same relationship get the same token everywhere?
- Does spacing alone (no boxes, no color) reveal the grouping? What does the squint test say?
- How many alignment lines does this screen have, and is each one earning its place?
- What happens with the longest name, the empty list, the 40-item list, the German translation?
- Where are my breakpoints, and can I defend each from content behavior rather than device folklore?
- Does this component belong to its container or to the viewport — and did I code it that way?
- Do visual, DOM, and tab order still agree after every rearrangement?
- Is this screen's density a choice I can articulate, or an accident I've normalized?

## Examples

**1. The settings page that spacing fixed.**
A settings screen "feels cluttered" despite modest content: 24 controls, every element 16px apart, each field boxed in a bordered card, cards in section cards. Diagnosis: uniform gaps carry no grouping; borders are doing spacing's job, twice. Rework: spacing scale applied recursively — label-to-field 4px, field-to-field 12px, group-to-group 32px, section-to-section 48px; all nested boxes deleted (section titles + spacing carry the structure); one alignment line for labels, one for fields. Element count unchanged, borders reduced by ~90%, and the "cluttered" feedback disappears — the screen was never over-full, it was under-grouped (see visual-hierarchy for the attention half of the same rework).

**2. Card grid, fluid-first.**
A dashboard's card row: three fixed 380px cards, breaking at laptop widths (wrap to 2+1 with a hole), overflowing at 900px, comical at ultrawide. Replacement: `grid-template-columns: repeat(auto-fill, minmax(320px, 1fr))` + one gap token — cards flow 1/2/3/4-up continuously, no breakpoints at all; the card itself gets a container query flipping its internal layout (icon-top vs icon-left) below 360px of *its own* width, so the same card works in the narrow sidebar where it's also used. Fourteen lines of CSS replace ninety; the tablet bug class is extinct because there is no tablet special case to break (see component-architecture: the component owns its response).

**3. The i18n stress test that redesigned a toolbar.**
An action toolbar designed in English: six labeled buttons, fixed widths, pixel-fit. German QA: two labels overflow, one wraps to two lines, the toolbar breaks its row. The retrofit temptation — shrink fonts per-locale — is rejected as whack-a-mole. Redesign for ranges instead: buttons size from content with min/max bounds and a shared padding token; the toolbar wraps by rule with overflow actions collapsing into a "More" menu by *priority order* (which forces the useful conversation about which actions matter — see ux-fundamentals; data-tables' progressive disclosure). English, German, and Japanese now render from one layout; the RTL pass later costs one logical-properties sweep instead of a rebuild.

## Evaluation Rubric

Score 1–10:

- **1–2**: Pixel-by-eye spacing; no scale, no grid; specimen-content design; desktop-only with shrunk "mobile"; fixed sizes breaking on real content.
- **3–4**: A nominal 8px grid honored sporadically; device-folklore breakpoints; grouping via boxes because spacing is uniform; worst-case content breaks layouts in production.
- **5–6**: Token scale applied; proximity grouping legible; few shared alignment lines; content ranges tested for main screens; fluid techniques for standard cases; measure capped.
- **7–8**: Full checklist: recursive spacing rhythm, content-derived minimal breakpoints, container queries where reuse demands, i18n/zoom resilience, orders reconciled, density chosen and consistent, decisions tokenized.
- **9–10**: Additionally: layout primitives make off-system spacing hard to write; worst-case fixtures in every preview; lint gates on raw values; breakpoint decisions audited against real traffic — and screens read as composed across the whole product because they share one geometric system, not one designer's eye.
