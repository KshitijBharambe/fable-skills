---
name: color
description: "Use when building a color palette or design system, adding dark mode, choosing chart/data-viz colors, fixing 'flat' or 'muddy' UI, or auditing contrast — neutrals, accents, semantic roles, scales."
---

# Color Systems

## Purpose

Build color systems — neutrals, accents, semantic roles, scales, dark mode — that look intentional, meet contrast law, and survive growth, instead of accumulating 47 hexes nobody can name.

## When to use

- Starting a product palette or design system.
- UI looks "flat," "muddy," or "like a rainbow exploded" — the two opposite color failures.
- Adding dark mode.
- Charts/data-viz need palettes (categorical, sequential, diverging).
- Auditing accessibility (contrast) or consolidating color chaos.

## Goals

- A token architecture where components reference roles (`--bg-surface`, `--text-primary`, `--border-subtle`), never raw hexes.
- 90%+ of every screen is neutrals; accent color is scarce and therefore meaningful.
- Every text/background pair passes WCAG AA in both themes, verified not vibed.
- Dark mode is a designed theme, not an inversion.

## Inputs

- Brand color(s) if mandated, and how negotiable they are (many brand colors fail AA as backgrounds/text — surface this early).
- Product temperature: clinical/technical ↔ warm/human; density and audience.
- Surfaces inventory: how many elevation/background levels the UI actually needs.
- Semantic needs: success/warning/danger/info, chart series count, status taxonomies.

## Outputs

- Token architecture in two layers: primitive scales (`blue-50…950`, `gray-50…950`) → semantic roles (`--bg-page`, `--bg-surface`, `--bg-raised`, `--text-primary/secondary/tertiary`, `--border-subtle/strong`, `--accent`, `--accent-hover`, `--danger`…), with light+dark values per role.
- Contrast matrix: every sanctioned text-on-background combination with its measured ratio.
- Usage rules: what accent may touch; what each semantic color means; chart palette assignments.

## Expert Mental Model

- **A color system is 90% neutrals.** The grays do the layout's work: page background, surfaces, borders, text hierarchy. Experts obsess over the neutral ramp first — beginners pick the brand blue first and wonder why screens look incoherent. Get 10–12 neutral steps right and the product already looks designed.
- **Pure gray is dead gray.** Neutrals carry a slight temperature: warm (toward yellow/red — friendly, editorial) or cool (toward blue — technical, clinical). Pick one temperature, thread it through every neutral, and the UI gains a subliminal coherence. Mixed-temperature grays are why screens feel "muddy" without visible cause.
- **Scarcity makes accents premium.** One accent, used only for interactive/brand moments (primary buttons, links, focus, selection), reads as confident. The accent's power is inversely proportional to its coverage — Linear/Stripe-class products are mostly gray with drops of color. When everything is colored, color stops meaning anything.
- **Build scales in a perceptual space (OKLCH/LCH), not by hex-lightening.** Naive lighten/darken of a hex shifts hue and saturation unevenly (blues go purple, yellows go mud). Perceptually stepped ramps keep each step equidistant to the eye and let you swap hue while preserving the lightness architecture — which is exactly what dark mode and theming need. Rough recipe: fixed lightness ladder (e.g., L: 97, 93, 87, 78, 66, 55, 47, 39, 30, 22), chroma peaking mid-scale, hue held near-constant (small drifts OK for optics).
- **Contrast is physics plus law, checked in context.** AA: 4.5:1 body text, 3:1 large text (≥24 px or 19 px bold) and UI components/focus indicators. But numbers don't see: saturated accent on white can "pass" and vibrate, gray-on-color can fail while looking fine. Measure, then look.
- **Dark mode is a second design, sharing the token layer.** Rules that change: elevation flips from shadows to *lighter surfaces* (shadows die on dark); saturated colors glow — desaturate/darken accents one-two steps; pure black (#000) with pure white text causes halation — start near `#0B0E14`-class deep neutrals; "same hue, adjusted L/C" per role, not `invert()`.
- **Semantic separation is non-negotiable**: success/warning/danger are a separate vocabulary from brand. If brand is green, success-green must still be distinguishable (or success gets a different treatment). And color is never the *only* channel — icons/labels ride along for the colorblind ~5% of male users.

## Workflow

1. **Choose neutral temperature** from the product's voice; generate a 10–12 step neutral ramp in OKLCH (hold hue ~constant, tiny chroma 0.005–0.02, lightness ladder). Verify: page/surface/raised backgrounds distinct but subtle; three text steps hit AA on all sanctioned surfaces.
2. **Set the accent**: brand hue tuned for function — a 500-weight for fills (white text must pass on it: aim L≈0.55, check 4.5:1), a 600–700 for text/links on light backgrounds, pale 50–100 steps for selected/hover washes. If the mandated brand color can't pass as a fill, keep it for marketing moments and derive a functional accent — say this out loud early.
3. **Build semantic ramps** (success/warning/danger/info) with the same lightness architecture — each needs at minimum: strong text step, fill step, subtle background step, border step. Warning is the perennial problem child (yellow text never passes on white — use amber-800-class for text, amber-100 for backgrounds).
4. **Define the role layer**: components consume `--bg-surface`, `--text-secondary`, `--accent` — never `blue-500` directly. This indirection *is* dark mode, theming, and every future rebrand.
5. **Assign dark values per role**: backgrounds from deep neutrals (not black), elevation = +L steps (surface lighter than page, raised lighter than surface), text at slightly reduced contrast vs light mode (pure white on dark glares — use ~L 0.93), accents desaturated one step, semantic colors re-tuned (dark-mode red must not vibrate).
6. **Run the contrast matrix**: script or tool every sanctioned (text, bg) pair in both themes; fix failures by moving lightness steps, not by ad-hoc new colors.
7. **Set the usage constitution**: accent = interactive only (if it's colored, you can click it — or accept and document the exceptions); semantic colors = status only (never decoration); one accent per view rule; charts get their own palette (next step).
8. **Charts**: categorical = 6–8 hues distinct in lightness as well as hue (colorblind-check with a simulator; blue/orange/teal/rose-class sets beat rainbow); sequential = single-hue lightness ramp; diverging = two hues through a neutral midpoint; gray is a data color too (context series muted, focus series accented).
9. **Test in hostile conditions**: cheap monitor, night shift/f.lux, grayscale filter (does hierarchy survive?), colorblind simulation, bright sunlight on mobile if relevant.
10. **Document with do/don'ts screenshots** — color rules without pictures don't transmit.

## Decision Tree

- If a screen looks chaotic → count distinct non-neutral colors visible; if >3, demote (convert colored elements to neutrals; keep accent for the primary action, semantic for true status).
- If it looks flat/lifeless → don't add hues; increase *contrast rhythm* (deeper text color, more distinct surface steps, one stronger accent moment) and check neutral temperature isn't pure-gray.
- If brand color fails AA as a button fill → darken until passing (if it survives brand review) or use it as large-type/graphic accents only, with a derived functional accent for UI.
- If choosing text color on a colored fill → compute both white and near-black; take the passer; if both pass, take the one matching surrounding temperature.
- If dark mode looks "washed out" → surfaces too light/too many steps; compress the ladder, re-anchor page near L 0.13–0.16.
- If dark mode colors "glow/vibrate" → chroma too high; drop C one step, raise L slightly on accents.
- If two semantic states are colliding (brand-green vs success-green) → shift one's hue 15–20° or differentiate by construction (success always icon+tint-bg, brand never on status surfaces).
- If chart series exceed 8 → stop adding hues; group into "top N + other," use interaction (hover/filter) instead of color to distinguish the tail.

## Heuristics

- Count rule: a typical product view holds ~90% neutrals, one accent presence, and semantic color only where status exists. Screenshot-audit against this.
- Never style disabled states with semantic colors; disabled = reduced-contrast neutrals (~40% text), full stop.
- Borders: two steps are enough (`subtle` for structure, `strong` for inputs/emphasis); if you have five border grays, three are noise.
- Hover/active states come from the same ramp (±1 step), not from opacity hacks on arbitrary colors (opacity stacks unpredictably on varied surfaces).
- Selected/highlight backgrounds: accent at 8–14% strength (the 50–100 step), with full-strength accent reserved for the indicator (left bar, check, border).
- Text-on-accent buttons: if you're at 4.4:1, you're at "no" — move the fill, don't round up.
- Focus rings: 2 px, high-contrast (3:1 against adjacent colors), offset from the element; they're law (and keyboard users' cursor), not decoration.
- Overlays/scrims: neutral black at 40–60% alpha, one token, everywhere — five different scrim values is a common invisible inconsistency.
- Images/avatars carry uncontrolled color; surround them with neutrals so they don't fight the accent.
- Gradients: same-hue lightness gradients (blue-500→blue-700) are safe; cross-hue gradients are brand-grade decisions, keep them out of components.
- When two colors must be told apart by meaning, also differ them by lightness ≥20 L points — hue-only differences die in grayscale, colorblindness, and sunlight.

## Quality Checklist

- [ ] Neutral ramp: one temperature, 10–12 steps, distinct surface levels, three AA-passing text steps.
- [ ] Two-layer tokens: primitives → roles; zero raw hexes in components (grep-verified).
- [ ] Contrast matrix green for every sanctioned pair, both themes, including text-on-accent and focus indicators.
- [ ] Accent scarce and interactive-meaning consistent; ≤3 non-neutral colors visible on typical views.
- [ ] Semantic set complete (text/fill/bg/border per state), warning legible, color-plus-icon everywhere status appears.
- [ ] Dark theme: designed per-role (lightness elevation, desaturated accents, no pure black/white), not inverted.
- [ ] Charts: colorblind-simulated, lightness-differentiated, sequential/diverging used for the right data shapes.
- [ ] Hover/active/selected/disabled derived from ramps by rule.
- [ ] Grayscale test: hierarchy and status still readable (via icons/weight).
- [ ] Usage doc with visual do/don'ts exists.

## Failure Modes

- **Hex soup**: 47 slightly-different grays and 6 blues accreted over two years; every new screen invents more because nobody can find the right one. Missing token layer, not missing taste.
- **Rainbow UI**: every feature team claimed a color; the dashboard looks like a candy shop and the one thing that matters can't stand out.
- **Brand-color tyranny**: illegible brand-yellow buttons shipped because "brand said so" — the conversation about functional derivatives never happened.
- **Inverted dark mode**: `filter: invert()`-grade theming; shadows glow, images look radioactive, saturated accents sear. No lightness architecture existed to remap.
- **Contrast by vibes**: gray-400 placeholder text and gray-500 help text shipped at 2.8:1; fails audits, users, and sunlight — retro-fixing touches every screen.
- **Hue-only semantics**: red/green status dots indistinguishable to deuteranopes and in grayscale exports; the lawsuit-and-support-ticket special.
- **Opacity-state hacks**: `hover: opacity 0.8` on colored fills → different perceived colors on every surface; states should be ramp steps.
- **Chart rainbow default**: library default 10-hue palette with no lightness plan; adjacent series merge for colorblind users; the "one important line" isn't.

## Edge Cases

- **User content color collisions**: labels/tags users color themselves will collide with semantic red/green — constrain the user palette away from semantic hues, or ensure status never relies on hue alone nearby.
- **P3/wide-gamut displays**: hexes clip differently; OKLCH lets you offer P3 accents with sRGB fallbacks — a polish item, but why perceptual-space workflows age well.
- **Forced-colors / high-contrast mode (Windows)**: custom colors get overridden; ensure borders/focus states use real borders (not box-shadow only) so the UI survives forced-colors.
- **Email/PDF/print exports**: dark-mode-designed assets embedded in emails, muted grays vanishing on print — export paths need their own token resolution.
- **Transparency over images**: text-on-photo needs a guaranteed scrim (gradient overlay tuned to worst-case bright image), not "the photos are usually dark."
- **Sequential data with zero/null**: "no data" must be visually distinct from "low value" — pattern or explicit neutral, never the ramp's bottom step.
- **Legacy brand migrations**: run old and new as two theme token sets during transition rather than mid-flight mixed palettes.
- **Elevation stacking in dark mode**: modal-on-raised-on-surface can run out of lightness headroom — cap nesting or add borders at the top of the ladder.

## Tradeoffs

- **Brand expression vs functional legibility**: strong brand hues everywhere vs quiet neutrals with brand moments. Products live in the quiet end; marketing can shout. Negotiate the split explicitly — "brand owns marketing + one hero moment per view; function owns the rest."
- **More ramp steps vs decision speed**: 12-step ramps cover everything but slow every choice; roles fix this — most contributors touch only ~15 role tokens.
- **Warm vs cool neutrals**: warm flatters content/photography and feels human; cool flatters data and feels precise. Pick by product, but pick — the tradeoff you can't take is both.
- **AA vs AAA**: AAA (7:1) benefits low-vision users and constrains design severely; commit to AA everywhere + AAA for body-reading surfaces as a pragmatic line.
- **Semantic strictness vs expressiveness**: forbidding decorative use of red/green/amber keeps status trustworthy but frustrates marketing-ish features; carve an explicit "illustrative palette" apart from the semantic one rather than diluting semantics.

## Optimization Strategies

- Generate ramps programmatically (OKLCH ladder script) so new hues inherit the lightness architecture — a new brand color becomes a 10-minute task, not a redesign.
- Contrast-check in CI: tokens file → matrix script → fail on regression; color law enforcement should not depend on designer vigilance.
- Quarterly screenshot audit against the count rule (≤3 non-neutrals per view) — entropy is measurable.
- Keep a "color decisions" log (why warning text is amber-800, why accent desaturates in dark) — the system survives team turnover through recorded rationale.
- Steal architectures, not palettes: analyze admired products for neutral temperature, accent coverage %, and surface-step count. Those transfer; their hex codes don't matter.
- Build the grayscale-preview habit: one keystroke filter during design review catches hue-dependence before users do.

## Self Review

- What fraction of this screen is neutral? What, precisely, did the accent buy with its scarcity?
- Can I trace every rendered color to a role token? What would a rebrand touch?
- Does the contrast matrix cover the pairs I actually shipped — including placeholder text, disabled states, and focus rings?
- In grayscale: is hierarchy intact? Is status readable?
- In dark mode: is elevation carried by lightness? Do any colors glow?
- Are red and green ever the sole carriers of meaning anywhere?
- If a colorblind user, a sunlit phone, and a cheap monitor all used this today — which one files the bug?

## Examples

**1. From hex soup to a two-layer system.**
Audit finds 47 grays, 6 blues, 3 reds. Rebuild: OKLCH cool-neutral ramp (12 steps), one blue ramp, semantic ramps; role layer of 24 tokens; codemod maps old hexes → nearest role (manual review on ~40 ambiguous sites); grep-CI forbids raw hexes thereafter. Visual diff of the app: barely perceptible. That's the point — the system now *matches* the best existing screens and makes every future screen default to them.

**2. Dark mode as a designed theme.**
Light theme: page `gray-50`, surface white, raised white+shadow, text `gray-900/600/400`, accent blue-600. Dark mapping per role: page L0.14, surface L0.17, raised L0.21 (elevation by lightness; shadows retired), text L0.93/0.70/0.50, accent desaturated one chroma step and lightened (blue-400-class) so white-on-accent still passes, warning re-derived (amber-300 text on amber-950/40% bg). Screenshots of both themes ship in the PR with the matrix output. No component changed — only role values.

**3. The dashboard rainbow intervention.**
Ops dashboard: 11 colors visible — status chips, category tags, chart defaults, three teams' pet accents. Rework: chips keep semantics (with icons); tags demoted to neutral with colored *dot* only; charts to a 6-hue colorblind-safe categorical set with the KPI series in accent and comparison series in gray-500; team accents deleted. Result: the single red anomaly on screen is now visible from across the room — which was the dashboard's entire job.

**4. Brand color that couldn't be a button.**
Brand: vivid yellow (#FFD400). White text on it: 1.6:1; black text: passes but reads as a warning sign. Resolution negotiated: yellow owns marketing hero moments, large display type, and an 8% tint for "highlighted" surfaces; functional accent derived as a deep warm charcoal-gold (L 0.45) for primary buttons where brand-adjacent warmth survives and 4.5:1 holds; semantic warning shifted hue away from brand to amber. Brand team signed off because the tradeoff was shown as side-by-side legibility, not opinion.

## Evaluation Rubric

Score 1–10:

- **1–2**: Raw hexes in components; no ramps; contrast unchecked; rainbow or mud; dark mode inverted or absent.
- **3–4**: Some palette discipline; token names exist but leak; contrast spot-checked; semantics collide with brand; charts on library defaults.
- **5–6**: Two-layer tokens; perceptual ramps; AA verified on main pairs; accent scarcity mostly held; dark mode designed per-role with rough edges.
- **7–8**: Full checklist: matrix in CI or ritual, grayscale/colorblind passes, states from ramps, chart palettes fit data shapes, usage doc with visuals.
- **9–10**: Additionally: generated ramps make new hues cheap; decision log maintained; screenshot audits keep the count rule honest; the system demonstrably survived a rebrand or theming request with role-layer-only changes.
