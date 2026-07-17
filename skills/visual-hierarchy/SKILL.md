---
name: visual-hierarchy
description: "Use when a screen feels cluttered or 'off,' users miss the primary action, laying out a new view, or setting spacing tokens — size, weight, color, spacing, alignment, density."
---

# Visual Hierarchy, Spacing & Density

## Purpose

Control where the eye goes and in what order — using size, weight, color, spacing, and position deliberately — so interfaces read instantly instead of demanding effort. Includes spacing systems, negative space, alignment, and density decisions.

## When to use

- A screen "feels off," cluttered, or amateur and nobody can say why.
- Designing any new view: dashboard, landing section, card, settings page, table.
- Users miss the primary action or can't find information that's on screen.
- Establishing spacing tokens for a design system.
- Reviewing UI where everything competes for attention.

## Goals

- One clear focal point per view; a deliberate second and third read.
- Grouping communicated by space first, borders last.
- A single spacing scale used everywhere, with space-between-groups > space-within-groups.
- Density matched to audience and task, not to habit.

## Inputs

- The content's actual priority order: what must the user see first, second, third? (From product intent, not from whoever shouts loudest.)
- User context: daily power tool vs occasional consumer surface; scanning vs reading vs comparing.
- Existing tokens: spacing scale, type scale, color roles.
- Real content: longest names, empty values, worst-case data — hierarchy built on lorem ipsum collapses on contact.

## Expert Mental Model

- **Hierarchy is rationed emphasis.** You have a budget: if everything is big, bold, or colored, nothing is. Experts spend emphasis on one primary element per view, then actively de-emphasize the rest — muting secondary text, ghosting tertiary actions. The de-emphasis is where amateurs stop short; making things quieter feels like making them worse, but the loud thing only works because of the quiet around it.
- **Five levers, use ≤2 per distinction**: size, weight, color/contrast, spacing/position, and decoration (borders, backgrounds). A heading that is bigger AND bolder AND colored AND boxed is shouting through a megaphone in a library. One or two levers per level keeps the system calm and legible.
- **Space is meaning.** Proximity is the strongest grouping signal humans have: things close together read as related — before any border or background is drawn. The cardinal spacing law: **space between groups must exceed space within groups.** Most "cluttered" interfaces violate exactly this — uniform 16 px everywhere means no grouping information at all.
- **Grouping tools, in order of preference: space → alignment → background → border.** Borders are the loudest and least elegant divider; every box adds visual noise. Experts delete borders and add whitespace, and the design "suddenly looks premium" — that's the whole trick behind half of minimal SaaS aesthetics.
- **Alignment is invisible until broken.** Every distinct alignment line on screen is one more thing the eye must reconcile. Fewer lines = calmer. A single hard left edge shared by heading, body, and controls does more for "designed-ness" than any styling. Optical alignment beats mathematical (icons and quotes may need nudging to *look* aligned).
- **Density is a strategy decision.** Bloomberg-dense and Linear-dense serve daily experts who value information per screen; consumer onboarding wants air and one idea at a time. The failure is unchosen density — inheriting whatever the component library defaulted to.

## Workflow

1. **Write the priority list before touching layout**: for this view, the user must (1) grasp X, (2) then Y, (3) be able to Z. Three levels, rarely more. This list is the spec hierarchy answers to.
2. **Assign emphasis with the budget**: level 1 gets the strongest treatment (size + weight, or size + position); level 2 gets one lever; level 3 gets *reduced* treatment (smaller, muted color `--text-secondary`). Actions: one primary button per view, secondary as outline/ghost, destructive kept visually quiet until context demands.
3. **Set the spacing scale**: base-8 (4, 8, 12, 16, 24, 32, 48, 64, 96) — or base-4 for dense products. Delete arbitrary values; every gap comes from the scale.
4. **Apply the grouping law**: within-group gaps small (4–8–12), between-group gaps larger (24–32–48), section gaps larger still (64–96). Ratio ≥2× between adjacent levels of grouping, or the grouping doesn't read.
5. **Reduce alignment lines**: choose a grid (12-col for pages, simple flex/stack rules for components), snap edges to shared lines, flush-left text in LTR (centered text only for short display moments), numbers right-aligned in tables.
6. **Strip decoration until it hurts, then add one back**: remove borders/boxes/shadows that duplicate what spacing already says. Keep dividers only where space can't do the job (dense tables, scannable lists).
7. **Choose density explicitly**: set row heights, padding, and font sizes per audience (see Decision Tree). If both audiences matter, density becomes a user setting (comfortable/compact) built on the same tokens.
8. **Squint test / blur test**: blur the screen (squint, or literally blur a screenshot). The intended focal point should still dominate; groups should read as distinct blobs. If it's uniform gray mush, the hierarchy failed.
9. **Test with worst-case content**: longest strings, zero states, 3-digit badges, missing images. Hierarchy that only works with ideal content is styling, not design.
10. **Do the de-emphasis pass**: find three things to make quieter (mute a timestamp, ghost a button, shrink a label). This pass improves nearly every screen and is the most commonly skipped step.

## Decision Tree

- If the view has >1 element claiming primary emphasis → demote all but one (the priority list decides; if the list can't decide, the product decision is missing — escalate that, don't style around it).
- If elements feel related but scattered → tighten within-group spacing first; only then consider a shared background; border last.
- If the design feels cluttered → remove decoration (borders, backgrounds, shadows) and increase between-group space; do NOT shrink content first.
- If the design feels empty/sparse but must stay light → strengthen alignment and add one level of type hierarchy rather than adding boxes.
- Density choice:
  - Daily-use expert tool (dashboards, admin, trading, dev tools) → compact: 13–14 px body, 32–36 px rows, 4/8 px within-group spacing; information density is a feature.
  - Consumer/marketing/onboarding → spacious: 16–18 px body, generous 24–48 px group gaps, one idea per viewport.
  - Mixed (SaaS app with occasional users) → default comfortable, offer compact toggle; never split the difference into mediocre-for-both.
- If a section must be separated → space first; if space is exhausted (dense UI) → hairline divider (`--border-subtle`); full boxes only for genuinely card-shaped content (self-contained, repeatable units).

## Heuristics

- The 2× rule: between-group space ≥ 2× within-group space, or grouping is invisible.
- Label-to-field gap must be visibly smaller than field-to-next-label gap — forms that violate this read as labels floating between fields.
- One primary CTA per view. Two "primary" buttons = zero primary buttons.
- Muted text (`--text-secondary`, ~60–70% strength) is doing hierarchy work; if <20% of your text is muted, you're probably shouting everything.
- Icon + text pairs: icon vertically centered to the cap-height/x-height optically, gap 6–8 px; icons inherit the text's muted-ness (secondary text gets secondary icons).
- Padding proportional to element importance: cards 16–24, page sections 48–96, buttons' horizontal padding ≈ 2–3× vertical.
- Corner radius is a voice, keep one: sharp (0–4) = technical/serious, medium (6–10) = friendly SaaS default, large (12–20) = consumer/playful. Mixed radii read as sloppy fast.
- Shadows: one elevation system, 2–3 levels max; shadows imply layering — a shadow on something that doesn't float is noise.
- Empty space at the end of a section is not waste; it's the signal that the section ended.
- If you must add a "View all" or meta-action to a group header, right-align it small and muted — headers carry one loud thing (the title).
- Real numbers beat adjectives in review: "gap 8 inside, 24 between" is checkable; "more breathing room" is a mood.

## Quality Checklist

- [ ] Priority list written; the squint test finds level 1 instantly.
- [ ] Every spacing value comes from the scale; no 13 px oddballs.
- [ ] Between-group ≥2× within-group everywhere; label proximity correct in forms.
- [ ] ≤2 levers per hierarchy distinction; one primary action per view.
- [ ] A visible share of text is deliberately muted; timestamps/meta ghosted.
- [ ] Alignment lines minimized; numbers right-aligned; no centered body text.
- [ ] Borders/boxes justified individually; space did the grouping where possible.
- [ ] Density chosen per audience with numbers (row height, body size) written down.
- [ ] Worst-case content tested; hierarchy survives.
- [ ] One radius system, one elevation system.

## Failure Modes

- **Uniform-spacing mush**: 16 px between everything → no groups, no rhythm; the layout is technically tidy and completely unreadable.
- **Emphasis inflation**: every stakeholder's element got bolded; the screen is all headline. Rationing was never enforced.
- **Box-itis**: every group in a bordered card, cards inside cards; borders doing work space should do. The UI reads as a wireframe someone shipped.
- **Missing de-emphasis**: primary is styled, but secondary text is full-black 16 px too — so nothing recedes and the primary can't win.
- **Center-alignment sprawl**: everything centered "to feel balanced" → ragged edges both sides, no shared lines, scanning destroyed.
- **Density cosplay**: consumer product built at Bloomberg density (intimidating), or pro tool built airy (info-starved power users pogo-scroll all day).
- **Decoration as hierarchy**: gradients, colored backgrounds, and icons trying to organize what size/space/weight should have.
- **Lorem-ipsum hierarchy**: perfect with 5-character names; production German compound words and 47-item lists shatter it.

## Edge Cases

- **Dark mode flattening**: shadows nearly vanish on dark backgrounds — elevation must shift to surface-lightness steps; borders gain relative importance.
- **User-generated content of wild length**: hierarchy needs truncation rules (line-clamp + title attr) and min/max widths, or one long title reorders the whole page's reading order.
- **Localization expansion**: German/Finnish +30–40% string length breaks tight labels; RTL mirrors the scanning pattern — alignment logic must be logical (start/end), not physical (left/right).
- **Data extremes in dashboards**: a 7-digit number where 2 digits were designed; negative values; the hierarchy of a stat card must survive magnitude changes (tabular nums, fixed heights).
- **Accessibility zoom (200%)**: spacing in fixed px compresses relative to enlarged text; verify reflow at zoom — hierarchy should degrade to a sane single column.
- **Print/export surfaces**: muted grays that carry hierarchy on screen can vanish on paper/PDF — check contrast in export paths.
- **Notification/badge collisions**: badges and dots are emphasis grenades; more than 2–3 visible at once and they cancel each other.
- **Marketing-page exception**: display sections legitimately break app rules (centered text, giant type) — the skill is keeping that voice out of the product UI.

## Tradeoffs

- **Density vs approachability**: more per screen serves experts, costs newcomers; resolve by audience, then by user setting — not by committee midpoint.
- **Whitespace vs scroll**: generous spacing pushes content below the fold; on decision-critical views (compare, checkout summary) keeping options co-visible can beat elegance. Space is a budget allocated to the decisions that matter.
- **Consistency vs local optimization**: the spacing scale occasionally loses to an optical fix (a 14 px gap that just looks right); take the optical exception rarely, and never invent a new *system* from one exception.
- **Borderless minimalism vs scannability**: pure-space grouping is beautiful until a 40-row data table needs row separators; dense data earns hairlines. Minimalism serves reading; dividers serve scanning.
- **Emphasis vs discoverability**: ghosting tertiary actions cleans the view but hides them from occasional users; overflow menus trade cleanliness for an extra click. Frequency of use decides: daily action stays visible, monthly action can hide.

## Optimization Strategies

- Institutionalize the scale as tokens (`--space-1..-12`); lint or review-block raw pixel values — consistency then happens by default.
- Build the de-emphasis pass into review: "name three things you muted." Screens improve monotonically.
- Screenshot-blur audits in PRs for key screens: attach the blurred image; the focal point should be namable by a reviewer who hasn't seen the spec.
- Steal ratios, not pixels: analyze products you admire for their between/within ratios, muted-text percentage, and border count per screen — the ratios transfer, the pixel values don't.
- Keep a worst-case content fixture set (long names, zeros, 999+ badges) and design against it from the first draft.
- When a screen resists fixing, rebuild it from the priority list with only type + space (no borders, no color) — then add back the minimum decoration. This "grayscale-first" rebuild finds the real structure fast.

## Self Review

- Blur it: does the intended #1 dominate? Do groups read as separate blobs?
- Can I state the within/between spacing numbers, and is the ratio ≥2×?
- What did I de-emphasize? (If the answer is "nothing," the pass was skipped.)
- How many alignment lines does this view have? How many borders — and which could whitespace replace?
- Is there exactly one primary action? Would a first-time user click it first?
- Did I choose this density, and for whom? Written where?
- Does it survive the worst-case fixture — longest name, empty state, 200% zoom?

## Examples

**1. Stat-card row rescue.**
Before: four KPI cards, each with border, icon, colored background, 16 px uniform padding, label and value same weight. Nothing stands out. After: borders removed (cards separated by 32 px gaps on the shared background), value promoted to 28 px semibold `--text-primary`, label demoted to 13 px `--text-secondary` 4 px above it, icons removed entirely (they carried no information), delta chip as the only color. Levers per distinction: two. The numbers now read left-to-right in under a second — verified by the blur test.

**2. Settings form regrouped by space alone.**
Before: 14 fields in one column, uniform 20 px gaps, three `<hr>`s. Users report it "feels endless." After: fields clustered into 4 groups (profile / notifications / security / danger); within-group 12 px, label-to-own-field 6 px, between-group 48 px with a 15 px semibold group heading; `<hr>`s deleted; danger zone additionally separated by 64 px + red-muted heading — position and space alone signal "different category of action." Same 14 fields, zero new components; completion time drops because the eye pre-chunks the work.

**3. Dashboard density done as a decision.**
Ops tool used 6 h/day by analysts. Explicit spec: body 13 px, table rows 32 px, within-group 4/8, panel gaps 16, page gutter 24; muted text for all metadata; hairline dividers allowed in tables only; compact/comfortable toggle deferred until a second persona actually appears. The doc records *why*: analysts compare across panels, so co-visibility beats whitespace. New-hire designers stop "airing it out" in redesigns because the density is documented as intent, not accident.

**4. Landing hero emphasis budget.**
Marketing hero with: logo carousel, headline, subhead, two CTAs, product screenshot, badge row — all loud. Rework from the priority list (1: value prop, 2: primary CTA, 3: proof): headline 56 px/tight/high-contrast (levers: size+weight); subhead 18 px `--text-secondary` max 60ch; single primary button + text-link secondary; screenshot pushed down and slightly muted (it was competing); logos to 40% opacity grayscale 96 px below. The blur test now shows exactly two hot spots — headline, then button — in reading order.

## Evaluation Rubric

Score 1–10:

- **1–2**: Uniform spacing, no focal point, box-itis, multiple primary CTAs; blur test = mush.
- **3–4**: Some type hierarchy but spacing arbitrary; grouping via borders; no de-emphasis; density unchosen.
- **5–6**: Spacing scale followed; grouping law mostly holds; one primary action; some muting; survives normal content.
- **7–8**: Full checklist: ≤2 levers per distinction, space-first grouping, alignment lines minimized, density chosen with numbers, worst-case content verified, blur test passes.
- **9–10**: Additionally: tokens enforced systemically; de-emphasis pass institutionalized; optical corrections applied knowingly; the view's hierarchy demonstrably matches the written priority list, and a stranger can recite the priorities from a blurred screenshot.
