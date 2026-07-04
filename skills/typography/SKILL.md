---
name: typography
description: "Use when choosing or pairing fonts, setting a type scale, fixing UI that 'looks cheap/generic,' or tokenizing text styles — weights, line height, measure, letter spacing."
---

# Typography

## Purpose

Set type that does 90% of an interface's design work: scale, weights, line height, measure, letter spacing, font selection and pairing — the decisions that separate "professionally designed" from "developer defaults" even when nobody can name why.

## When to use

- Starting a product, design system, or marketing site.
- UI "looks cheap/generic" and layout changes haven't fixed it.
- Choosing or pairing fonts; setting a type scale; tokenizing text styles.
- Text-heavy surfaces: docs, blogs, dashboards with data labels, long-form reading.
- Reviewing designs where text sizes/weights have multiplied ad hoc.

## Goals

- A closed type system: 4–6 sizes, 2–3 weights, defined line heights — used everywhere, extended never (without a system change).
- Body text comfortable at length: right size, measure, line height, contrast.
- Hierarchy achieved through weight and color before size.
- Numbers, labels, and data set with the right variants (tabular figures, tracked-out caps).

## Inputs

- Product voice: technical/serious ↔ friendly/consumer, dense-expert ↔ airy-marketing.
- Reading contexts: continuous reading? scanning? data comparison? glancing on mobile?
- Constraints: brand fonts mandated? performance budget (webfont bytes)? multilingual (script coverage)?
- Current inventory: audit of every size/weight/style actually in the product (there are usually 30+; there should be ~10).

## Outputs

- Type tokens: named styles (`display`, `title`, `body`, `body-sm`, `caption`, `code`...) each specifying family, size, weight, line-height, letter-spacing, and case.
- Font stack with fallbacks metrically tuned; loading strategy (subset, preload, `font-display`).
- Usage rules: which style for which role, and the demotion path (what to do before inventing a new size).

## Expert Mental Model

- **Typography is 90% of UI design because UI is 90% text.** Get type right and bare HTML looks designed; get it wrong and no amount of shadows and gradients recovers it. Experts fix type before touching any decoration.
- **A scale is a vocabulary, not a menu.** Pick 4–6 sizes generated from a ratio (UI: ~1.2; marketing/display: 1.25–1.333), then *close the set*. Every ad-hoc 15 px is a leak in the system; the discipline is what creates rhythm across screens. Practical UI scale: 12, 13/14, 16, 20, 24, 32, 48 — snap to sensible integers rather than worshiping the ratio's decimals.
- **Line height is inversely proportional to size.** Body wants 1.5–1.6; headings want 1.1–1.25; giant display wants 1.0–1.1. The default-1.5-everywhere mistake makes headlines float apart; the designer's 1.2-everywhere mistake suffocates paragraphs. Also: line height should scale with measure — wider columns need more leading.
- **Weight and color before size.** Novices make important things bigger; experts make them heavier or darker first. A 14 px semibold `--text-primary` label over 14 px regular `--text-secondary` value creates hierarchy with zero layout disruption. Size changes are the loudest lever — spend them on true level changes only. Corollary: create three text colors (primary ~90% strength, secondary ~60%, tertiary/disabled ~40%) and use them constantly.
- **Measure (line length) is the invisible comfort dial**: 45–75 characters per line for body (66 is the classic sweet spot); past 90ch the eye loses the return path; text containers need `max-width` in `ch` units, not just page-level luck.
- **Letter spacing bends with size**: large display type tightens (-1% to -3%, i.e., -0.01 to -0.03 em); body stays neutral; small ALL-CAPS labels open up (+5 to +10%). Fonts are drawn for body sizes; you're compensating at the extremes. This single detail — tight display, tracked caps — reads as "professional" almost subliminally.
- **Font choice is casting, pairing is chemistry.** The font's voice must match the product's claim (a grotesque says neutral-modern; a humanist sans says friendly; a serif says editorial/authoritative). One family with a weight range is usually enough for product UI; pairing (display + body, or sans + mono) demands contrast in role and harmony in proportion (similar x-height) — the classic failure is two similar sans-serifs that read as a mistake rather than a choice.

## Workflow

1. **Audit what exists**: extract every (family, size, weight, line-height) tuple in the product. The list's chaos is your case for the system.
2. **Define the voice in adjectives** (e.g., "precise, calm, technical") and shortlist 2–3 families that embody it. Test candidates with YOUR real content — navigation labels, data tables, error messages — never with pangrams.
3. **Check font mechanics before falling in love**: weight range (need 400/500/600 minimum), true italics if needed, tabular figures for data, x-height (larger = better small-size legibility), character coverage for your locales, variable-font availability (one file, all weights).
4. **Build the scale**: choose base (16 px web body; 13–14 px dense UI), ratio ~1.2, generate, snap to integers, cap at 6 sizes. Assign names by role, not size (`title` not `text-24`) so redesigns re-map cleanly.
5. **Set line heights per size** (1.5–1.6 body, 1.3 subheads, 1.1–1.2 display) and letter-spacing per extreme (tighten display, track small caps). Encode in tokens; never set raw.
6. **Define the color trio** (primary/secondary/tertiary text) and the rule for use: values vs labels, content vs metadata.
7. **Set measure limits**: body containers `max-width: 65ch`; form help text ~45ch; never full-bleed paragraphs on desktop.
8. **Engineer the loading**: woff2 only, subset to used scripts, preload the 1–2 critical files, `font-display: swap` with a metrically-tuned fallback (`size-adjust`, `ascent-override`) so swap doesn't reflow; self-host (cross-site cache-sharing is dead).
9. **Apply the details pass**: real quotes “ ” and apostrophes ’, en/em dashes, `tabular-nums` on all data columns and timers, `text-wrap: balance` on headings, hyphenation or `break-words` policy for user content, ellipsis truncation rules.
10. **Document the demotion path**: when someone "needs" a new size, the answer is usually the nearest existing size + weight/color change. New sizes require a system PR, not a local override.

## Decision Tree

- If product UI (apps, tools) → one family, 3 weights (400/500/600), system-adjacent metrics; consider high-quality system stack if brand allows (fast, native, free).
- Else if editorial/marketing → display family for headlines (can be characterful) + workhorse body family; test the pair at real sizes together.
- If dense data product → prioritize: large x-height, open apertures, tabular figures, distinct Il1 0O — legibility features beat personality.
- If code/technical content → add a mono family; match its apparent size to body (monos run large — often needs 0.9em).

When hierarchy is insufficient:
- First → increase weight one step or promote color (secondary → primary).
- Then → adjust case/tracking (label treatment) or add space above.
- Last → increase size one scale step. (Size is the loudest, least reversible lever.)

When two fonts fight:
- If similar classification (two grotesques) → cut one; use weights of the survivor.
- If pairing needed → contrast the classification (serif display + sans body, or sans + mono), match the x-height proportion, and let exactly one carry personality.

When body text "feels off," check in order:
1. Size ≥16 px for continuous reading (13–14 px only for dense scanning UI)?
2. Line height 1.5–1.6?
3. Measure ≤75ch?
4. Contrast: near-black on near-white (not pure #000/#fff for long reading — slight softening reduces glare; but never below AA 4.5:1)?
5. Then and only then, blame the font.

## Heuristics

- 4–6 sizes, 2–3 weights, 3 text colors: if you can't build the screen with that vocabulary, the screen's structure is the problem.
- Don't use 300/light weights below 18 px, or on any background image — they shimmer into illegibility on low-DPI and dark mode.
- Semibold (600) beats bold (700) for UI emphasis at small sizes; 700+ at 13 px clogs counters.
- ALL-CAPS only for short labels (≤2–3 words), always tracked out +5–10%, one size smaller than you'd think, usually secondary color.
- Line height in unitless values (`line-height: 1.5`), never px — px leading breaks the moment sizes change.
- Tabular figures (`font-variant-numeric: tabular-nums`) on: tables, prices, timers, dashboards, anything vertically stacked or live-updating. Proportional figures dance.
- One `rem`-based root; sizes in rem so user font-size preferences work; UI chrome may pin px deliberately (document it if so).
- Icon size ≈ cap height to x-height of adjacent text (roughly 1em box, optically adjusted), never "24 px because the icon set said so."
- Headings: `text-wrap: balance`; paragraphs: consider `pretty`; never center multi-line body text.
- Placeholder text is styling, not labeling — one shade lighter than tertiary, disappears on focus-with-value designs prohibited.
- If the brand font is weak at small sizes, split duties: brand for display, workhorse (Inter-class) for UI ≤16 px. Common, honorable, invisible to users.
- Fake bold/italic (browser-synthesized) is visibly mushy — load the real weights or don't use them.

## Quality Checklist

- [ ] Closed scale: every text node maps to a named token; audit shows no stray sizes.
- [ ] Body: ≥16 px reading / 13–14 px dense-UI rationale written; 1.5–1.6 leading; ≤75ch measure; ≥4.5:1 contrast.
- [ ] Display type tightened; caps labels tracked; both encoded in tokens, not sprinkled.
- [ ] Three text colors in active use; hierarchy attempts weight/color before size.
- [ ] Tabular figures on all numeric columns/timers.
- [ ] Real punctuation (curly quotes, em dashes); heading balance; truncation rules defined.
- [ ] Fonts: woff2, subset, preloaded critical faces, swap with tuned fallback metrics, self-hosted.
- [ ] Il1/0O distinguishable if IDs/codes are displayed; mono sized to match body.
- [ ] Localization tried: +35% string growth and target scripts render in the chosen fonts.
- [ ] The demotion path is documented and enforced in review.

## Failure Modes

- **Scale sprawl**: 23 sizes after a year of "just this once." Rhythm gone; every screen slightly different. The system needed a gatekeeper, not better intentions.
- **Size-only hierarchy**: every level distinction made by size → screens shout, layouts shift with content, and the 5 levels needed exceed the 4 sizes available.
- **1.5 line-height on 56 px headlines**: floating lines that read as separate elements; the flip side — 1.2 on body — dense unreadable slabs.
- **Full-width paragraphs**: 140-character lines on desktop docs pages; readers lose the line return and skim instead of read.
- **Light-gray-on-white body text** (contrast 3:1 "because elegant") — illegible on cheap panels, in sunlight, and for a third of users; elegance that fails AA is a defect.
- **Two-similar-sans pairing**: Helvetica-alike + Inter reads as inconsistency, not design. Nobody can name the problem; everybody feels it.
- **FOIT/reflow theater**: invisible text for 3 s, then a layout-shifting swap. Loading strategy was an afterthought.
- **Proportional figures in data**: totals column wiggling as numbers update; scanning down misaligned digits. One CSS property was missing.
- **Trusting the specimen**: font chosen from the foundry's gorgeous specimen page; falls apart on your 13 px table labels. Always audition with real UI.

## Edge Cases

- **User font-size preferences & zoom**: rem-based scales honor browser settings; test 200% zoom — fixed-height containers clip ascenders first.
- **CJK/mixed-script text**: no italics, different line-height needs (~1.7 body), fallback stack per script; tracked-caps rules don't apply.
- **RTL**: letter-spacing on Arabic breaks joining — tracking rules must be script-conditional.
- **Dynamic/variable content in headings**: user-generated titles hit the tightened display tracking with ALL-CAPS words and emoji — clamp, don't crash.
- **Subpixel/low-DPI rendering**: hairline weights and 13 px text that look crisp on retina fuzz on 1× monitors — check on a cheap external display once.
- **Emoji and symbol fallback**: system emoji inside brand-font text shifts baseline; accept it, but verify line-height absorbs it.
- **Numbers inside sentences vs data**: prose uses proportional oldstyle comfortably; UI values want tabular lining — same font, two variant settings.
- **Long words in narrow columns** (German, URLs, tokens): `overflow-wrap: anywhere` policy for user content or single words blow out cards.

## Tradeoffs

- **Brand personality vs legibility**: characterful fonts tax small sizes and data; split duties (display personality, workhorse body) rather than compromising either.
- **System stack vs webfonts**: system fonts are instant, free, native-feeling — and generic, inconsistent across OS, off-brand. Product UIs behind login lean system-stack harder than marketing surfaces can.
- **Variable font vs static weights**: variable = one file, animation-capable, all weights (~50–150 KB); static trio can be smaller if you truly need only 2 weights. Choose by measured bytes, not fashion.
- **More sizes vs simpler system**: a 7th size occasionally genuinely helps (mega-display); every addition taxes every future decision. Additions go through the system, priced accordingly.
- **Perfect ratios vs pragmatic snapping**: modular purity produces 19.2 px; shipping products round to 19 or 20. The ratio is scaffolding — the built system is integers.

## Optimization Strategies

- Tokenize as composite styles (size+leading+tracking+weight together, e.g. `text-title`), not independent axes — prevents illegal combinations by construction.
- Lint raw `font-size` in code review/CI; the system survives only if the escape hatch squeaks.
- Build a one-page live specimen (all tokens, real content, light+dark) — designers and engineers align on it, and font regressions become visible diffs.
- Revisit the audit quarterly: entropy accumulates; a 30-minute prune keeps the vocabulary closed.
- For performance: subset aggressively (Latin-only cuts most files 60–80%), preload only above-the-fold faces, lazy-load display/marketing faces.
- Steal proportions from products you admire: measure their body size, leading, scale ratio, and muted-text usage — proportions transfer across brands; exact fonts don't need to.

## Self Review

- Can I name the token for every piece of text on this screen? What escaped the system?
- Did I try weight/color before size for each hierarchy step?
- Read a full paragraph on the actual target device: comfortable? Measure ≤75ch? Would I read 5 of these?
- Are display sizes tightened and caps tracked — or is one global letter-spacing pretending?
- Do the numbers align in every column? Timers jiggle-free?
- What happens at 200% zoom, +35% German, and on a 1× monitor?
- Does the font's voice match what the product claims to be — would a stranger guess the product category from a text-only screenshot?

## Examples

**1. The "looks cheap" fix with zero new fonts.**
SaaS app, default stack, complaint: "feels like a prototype." Changes: body 14→16 px (reading surfaces) with 1.55 leading and 65ch max; headings from bold-and-huge to 20/600 tightened -1%; labels to 12 px caps +6% tracking in `--text-secondary`; all metadata demoted to secondary color; tabular-nums on the tables. Same family throughout. The app reads as "designed" — every change was proportions and discipline, which is the actual secret.

**2. Choosing a font like a casting director.**
Fintech dashboard; adjectives: "precise, trustworthy, quiet." Candidates auditioned on a real screen (dense table + form + empty state): candidate A (geometric, charming) fails Il1 test and clogs at 13 px; candidate B (grotesque, large x-height, tabular figures, variable) is boring alone and perfect in place. B ships for everything; personality delegated to one display serif used only on marketing headlines. Decision recorded with the audition screenshots.

**3. Type scale as tokens with a demotion path.**
System: `display 48/1.1/-2%`, `headline 32/1.2/-1%`, `title 24/1.25`, `subtitle 18/1.4/500`, `body 16/1.55`, `body-sm 14/1.5`, `caption 12/1.4/+2%/secondary`. A PR requests 15 px "because 16 feels big in the sidebar." Review applies the path: sidebar items → `body-sm` (14) + weight 500, primary color — accepted, no new size. Six months later the audit still shows 7 sizes. The path, not the scale, is what held.

**4. Loading strategy that ended the reflow.**
Marketing site: brand font FOIT 2.8 s on 3G, then a two-line→three-line headline shift (CLS 0.21). Fix: woff2 subset (Latin, 41 KB), `<link rel="preload">` for display + body faces, `font-display: swap`, fallback `Arial` overridden with `size-adjust: 96%; ascent-override: 93%` tuned against the brand font until the swap is motionless. Text visible at first paint, swap invisible, CLS 0.01.

## Evaluation Rubric

Score 1–10:

- **1–2**: Default stack unexamined; ad-hoc sizes everywhere; size-only hierarchy; unreadable measures; contrast failures.
- **3–4**: A scale exists but leaks; line height uniform; no tracking discipline; figures proportional in data; loading naive.
- **5–6**: Closed 4–6 size scale with tokens; leading per size; weight/color hierarchy in use; measure capped; fonts subset and swapped.
- **7–8**: Full checklist: extremes tracked, tabular figures, tuned fallback metrics, three-color text system, localization and zoom verified, demotion path enforced.
- **9–10**: Additionally: font casting documented with real-content auditions; composite tokens prevent illegal combos; specimen page maintained; the product passes the text-only screenshot test — voice recognizable, hierarchy legible, nothing to add or remove.
