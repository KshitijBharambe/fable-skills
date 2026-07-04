---
name: motion
description: "Use when adding animations or transitions (modals, panels, page nav, micro-interactions), fixing janky or sluggish motion, or defining motion tokens — durations, easings, springs, choreography."
---

# Motion Design

## Purpose

Use animation to explain causality, state, and spatial relationships — durations, easings, choreography, springs — so interfaces feel alive and responsive without becoming theme parks.

## When to use

- Adding transitions to state changes: modals, panels, list changes, page navigation.
- An interface feels abrupt/janky, or conversely slow/showy.
- Designing micro-interactions: buttons, toggles, hovers, drag feedback.
- Establishing motion tokens (durations, easings) for a design system.
- Reviewing animation-heavy PRs or Lottie/scroll-effect proposals.

## Goals

- Every animation answers "what does this explain?" (origin, destination, causality, progress) — decoration is the exception, chosen knowingly.
- Durations and easings come from a token set; nothing is hand-timed per component.
- Frequent actions are near-instant; rare/spatial changes get more time.
- All motion runs on the compositor (transform/opacity) and respects `prefers-reduced-motion`.

## Inputs

- The state changes in the flow: what appears, disappears, moves, reorders.
- Action frequency: how many times per day will a user see each animation?
- Spatial model: where do things "live" (panel slides from where it docks; modal grows from what spawned it)?
- Brand energy: calm/professional ↔ playful/expressive.
- Performance budget and device floor.

## Outputs

- Motion tokens: duration scale (e.g., 100/150/200/300/500 ms), easing set (standard/decelerate/accelerate + one spring), and rules for pairing them.
- Per-pattern specs: modal, drawer, toast, list add/remove, tab switch, hover/press — each with duration, easing, properties, and choreography order.
- Reduced-motion variants defined (not just "off").

## Expert Mental Model

- **Motion is explanation, not decoration.** Its jobs: (1) causality — "your click did this"; (2) origin/destination — "the modal came from that button; the item went to the archive"; (3) continuity — keeping context during change instead of teleporting; (4) status — "working on it." An animation that explains nothing is a tax on every future use. Experts ask "what would be *confusing* without motion?" and animate exactly that.
- **Frequency sets the volume.** The more often an animation plays, the subtler it must be. A first-run onboarding flourish can take 600 ms; a button used 200×/day gets ~100 ms of press feedback or nothing. Delight on first sight becomes friction by Friday — this single principle prevents most motion regret.
- **Duration bands are narrow**: micro-feedback (hover, press, toggles) 100–150 ms; small transitions (dropdowns, tooltips, toasts) 150–250 ms; medium (modals, drawers, accordions) 200–300 ms; large/spatial (page transitions, complex choreography) 300–500 ms. Above 500 ms only for deliberate storytelling. When in doubt, shorter — users never complain an interface is too responsive.
- **Easing is physics-truthiness.** Entering elements decelerate (`ease-out`: fast start, gentle landing — the UI feels eager); exiting elements accelerate (`ease-in` — leaving quickly, politely) or just go faster; on-screen moves use standard curves (ease-in-out-class). Linear is for marquees and progress, nothing else. Springs (mass/stiffness/damping) shine for gesture-driven and interruptible motion because they carry velocity naturally.
- **Enter/exit asymmetry**: exits run ~20–30% faster than entrances. Users care about what's arriving, not what's leaving; slow exits feel like the UI is milking it.
- **Only transform and opacity.** Animating layout properties (width/height/top/margin) triggers reflow every frame — jank by construction. Scale, translate, rotate, fade: compositor-cheap. Layout-feeling effects get built from transforms (FLIP technique) or accepted as snaps.
- **Interruptibility is table stakes.** Users will click "close" mid-open. Animations must be reversible from current state (springs and CSS transitions do this naturally; fixed keyframe timelines don't) — a UI that must finish its animation before obeying feels broken.

## Workflow

1. **List the moments**: every state change in the feature. For each: what appears/disappears/moves, and what confusion would exist with an instant cut?
2. **Assign purpose or delete**: moments with an explanatory job get motion; the rest get instant changes. (Instant is a valid, often correct, choice.)
3. **Map spatial logic**: decide where things come from and go to — drawers slide from their edge, modals scale from ~95% (or grow from trigger for strong causality), deleted items exit toward their destination (archive, trash). Inconsistent spatial logic is why some apps feel "dreamlike" in the bad way.
4. **Pick from the token bands**: duration by size-and-frequency, easing by direction (in/out/move). Never hand-tune per instance first — use the system, deviate with a reason.
5. **Choreograph multi-element changes**: one thing leads (the primary element), others follow with 20–50 ms stagger; list items cascade ≤30 ms apart, capped (~6 items then simultaneous) so long lists don't take seconds; related elements move as one group, unrelated changes shouldn't animate simultaneously at all.
6. **Implement on the compositor**: transform/opacity; `will-change` sparingly (it costs memory — apply just-in-time); FLIP for reorder/layout-feeling moves; check for accidental layout animation in DevTools.
7. **Make it interruptible**: transitions from current computed state; springs for gestures (carry finger velocity into the release animation); no `pointer-events: none` during animations that a user might redirect.
8. **Respect `prefers-reduced-motion`**: replace movement with fast crossfades (not nothing — abrupt cuts can be worse for orientation); kill parallax, auto-playing, and large translations entirely.
9. **Test at 6× CPU throttle and on real mid-tier hardware**: animations are the first thing to expose jank; a hitching animation is worse than none.
10. **Watch it 20 times in a row** (the frequency simulation): still fine? Now halve the duration and compare — pick the one that disappears into the interaction.

## Decision Tree

- If the action is instant-feedback (press, toggle, hover) → 100–150 ms, ease-out, tiny transform (scale 0.97 press, subtle bg shift); or instant + state change if the control is ultra-high-frequency.
- Else if content appears in place (tooltip, dropdown, toast) → 150–200 ms, ease-out, opacity + 4–8 px translate from its origin direction; exit 100–150 ms ease-in.
- Else if a surface enters over context (modal, drawer) → 200–300 ms; modal: fade + scale 0.96→1 with ease-out; drawer: translate from its docked edge; scrim fades in parallel slightly faster.
- Else if items reorder/insert/delete in a list → FLIP-move survivors (200 ms standard), fade+collapse the removed (exit first, then close the gap — or simultaneously at small sizes), stagger inserts ≤30 ms.
- Else if navigation between peers (tabs, steps) → directional slide 10–20% width + crossfade, 200–250 ms; direction encodes the mental model (forward = content moves left in LTR).
- Else if progress/waiting → see loading-states skill; motion here is honesty (indeterminate spinner <1 s wait, progress bar beyond), never entertainment that outlives the wait.
- If the animation is gesture-driven (swipe, drag) → track the finger 1:1 while touching; on release, spring with the gesture's velocity to the nearest valid state. Duration-based curves feel dead here.
- If brand wants "more delight" → concentrate expression in rare, meaningful moments (first-run, success/completion, empty states) — never on workhorse interactions.

## Heuristics

- Default set that covers 90% of product UI: `duration-fast: 150ms`, `duration-base: 200ms`, `duration-slow: 300ms`; `ease-out: cubic-bezier(0, 0, 0.2, 1)`, `ease-in: cubic-bezier(0.4, 0, 1, 1)`, `ease-in-out: cubic-bezier(0.4, 0, 0.2, 1)`.
- Distance scales duration, gently: a full-screen transition earns more time than an 8 px tooltip nudge — but sublinearly (2× distance ≠ 2× duration).
- Nothing should move more than ~20% of the screen for a routine action; big sweeps are for big moments.
- Two properties per animation is usually enough (opacity + one transform). Five-property extravaganzas read as wobble.
- Never animate blur at size (expensive) or box-shadow directly (animate a pre-rendered shadow layer's opacity instead).
- Stagger reads as intentional at 20–50 ms; at 100 ms+ it reads as slow-loading.
- Hover states: 100–150 ms in, ~50 ms out — or instant out; lingering hover-out effects smear across the UI when the cursor sweeps.
- If an element both moves and changes content, change content at the least-visible moment (start of exit, or mid-crossfade) — mid-move reflows look glitchy.
- Loading skeletons pulse slow (1.5–2 s cycle, subtle) — fast pulsing communicates anxiety.
- Auto-playing ambient motion (looping gradients, floating blobs) is a brand-surface tool; inside working UIs it competes with content forever.
- The "would this survive a demo to a tired user at 6 pm?" test beats any dribbble reaction.

## Quality Checklist

- [ ] Every animation has a namable explanatory purpose (or a documented delight exception).
- [ ] Durations/easings from tokens; bands respected (micro ≤150, standard ≤300, rare spatial ≤500).
- [ ] Enter decelerates, exit accelerates and runs faster than enter.
- [ ] Spatial logic consistent (things come from/return to where they live).
- [ ] Multi-element changes choreographed (lead + ≤50 ms stagger, capped cascades).
- [ ] Transform/opacity only; verified no layout thrash at 6× throttle.
- [ ] Interruptible: mid-animation input obeyed, gestures carry velocity.
- [ ] `prefers-reduced-motion` provides crossfade variants; parallax/autoplay killed.
- [ ] High-frequency actions near-instant; the 20-repetition test passed.
- [ ] Mid-tier device test: no dropped-frame hitches.

## Failure Modes

- **Everything slides**: uniform 400 ms slide-ins on every element of every page — the app feels like it's performing itself; users start waiting for the UI.
- **Duration vanity**: 500–800 ms modals because it "shows off the easing." Feels premium in the design review, molasses by day two.
- **Layout-property animation**: animating `height`/`top` → main-thread reflow per frame → jank exactly on low-end devices where trust is thinnest.
- **Uninterruptible sequences**: click close during open → queued animations play out → UI feels deaf.
- **Spatial contradictions**: drawer enters from right, exits downward; item deleted upward but "archived" — the space stops making sense subconsciously.
- **Stagger sprawl**: 40-item list × 80 ms stagger = 3.2 s of cascading rows. The cap was missing.
- **Hover noise**: cursor sweeping across a nav lights up a wake of lingering hover animations.
- **Reduced-motion ignored**: vestibular-triggering parallax with no opt-out — an accessibility failure, and increasingly a review-blocking one.
- **Delight on the workhorse**: confetti on every save. Cute Monday, insulting Thursday.

## Edge Cases

- **First paint/mount animations**: page-load entrance animations delay perceived readiness — animate on user-initiated changes, not on initial render (or keep initial fades ≤150 ms).
- **Rapid repeated triggers**: toast spam, double-clicks — animations must coalesce (restart or queue-with-cap), not stack into chaos.
- **Mid-animation data changes**: item deleted while its insert animation runs — state machine must own the element's lifecycle; orphaned exit animations crash or ghost.
- **Concurrent list ops**: insert + remove + reorder in one update — FLIP handles it if you snapshot before/after correctly; hand-rolled offsets don't.
- **Focus and screen readers**: moving focus must not wait on animation; announce state changes immediately even if the visual is transitioning.
- **Springs that never settle**: low damping = perpetual sub-pixel oscillation eating CPU; define rest thresholds.
- **Tab-hidden timers**: rAF pauses in background tabs; animations tied to real elapsed time (progress) must reconcile on visibility return.
- **Zoom/large-text modes**: pixel-tuned translations (8 px nudge) shrink relative to 200% text; use relative units where the motion should scale.

## Tradeoffs

- **Explanation vs speed**: continuity animations aid comprehension but cost wall-clock time on every occurrence. Bias: explain spatial/structural changes; cut time on frequent, already-understood ones.
- **Springs vs curves**: springs interrupt beautifully and carry gesture velocity, at the cost of nondeterministic duration (choreography gets harder) and library weight; CSS curves are cheap, cacheable, deterministic. Use springs where gestures live; curves elsewhere.
- **System uniformity vs moment expressiveness**: tokens keep the product coherent; hero moments (onboarding, success) legitimately break the bands. Budget the exceptions (a handful per product), don't ban them.
- **Skeleton/entrance polish vs honesty**: staged reveal animations can *mask* slowness or *add* to it; measure whether the choreography delays interactivity (INP) — polish that costs input readiness is net negative.
- **Native-feel vs brand-feel**: on mobile web/hybrid, mimicking platform transitions feels right but constrains brand; custom motion feels branded and slightly foreign. Consistency within your product beats fidelity to either.

## Optimization Strategies

- Centralize motion tokens and pattern specs (modal/drawer/toast/list) so 90% of animation code is applying a named recipe — review only the deviations.
- Build a motion debug mode (10× slow-mo toggle) for design review — the standard tool for catching choreography bugs.
- Profile the top 3 animations on a mid-tier device quarterly; regressions creep in via added DOM weight, not changed animation code.
- Replace JS-driven scroll effects with CSS scroll-driven animations/`content-visibility` where supported — off-main-thread by construction.
- Audit with the "motion inventory": list every animation in the product with purpose, duration, frequency; delete the purposeless ones — most products can cut 30% of their motion and improve.
- Steal timing, not effects, from products with great feel: measure their durations (screen-record + count frames) and note their restraint; the numbers transfer.

## Self Review

- For each animation: what does it explain? What did I delete because it explained nothing?
- Are all durations/easings tokens? What's my longest animation, and does its rarity justify it?
- Does exit run faster than enter? Do things return the way they came?
- What happens if the user acts mid-animation — everywhere?
- Did I run reduced-motion and actually look at it?
- Did I watch the hot-path animations 20 times and at 6× throttle?
- Would removing half the motion make the product feel worse — or calmer?

## Examples

**1. Modal, the reference recipe.**
Open: scrim opacity 0→1 (150 ms ease-out), dialog opacity 0→1 + scale 0.96→1 (200 ms ease-out), focus moves immediately, content already rendered (no post-open pop-in). Close: dialog 150 ms ease-in fade + scale to 0.98, scrim follows 100 ms; Escape mid-open reverses from current state. Reduced motion: crossfade only, 100 ms. Nothing here is clever — that's why it feels native everywhere.

**2. List deletion with spatial honesty.**
Email archive swipe: row tracks finger 1:1; release past threshold → row springs off-screen in swipe direction (velocity carried), then remaining rows FLIP up 200 ms standard-ease to close the gap; undo toast slides up 150 ms. The two-phase order (exit, then collapse) reads as "it left, space reclaimed" — collapsing while exiting reads as the list eating the row. 20-repetition test passed at these numbers; the original 350 ms exit felt fine once and slow by the tenth archive.

**3. Motion tokens installed, chaos retired.**
Audit finds 23 hand-tuned durations (180, 220, 250, 320, 400…) and 9 bezier strings. System: 3 durations + 3 curves + 1 spring config as design tokens; pattern recipes documented for the 6 recurring cases; PR rule — raw durations need a comment. Codemod maps existing values to nearest token. The product immediately feels more coherent, and nobody can quite say why — which is the correct outcome for motion.

**4. The delight budget, spent well.**
Team wants celebratory motion. Instead of confetti-on-save (rejected: 40×/day action), the budget goes to: first-project-created moment (one 600 ms choreographed sequence, seen ~once per user), streak-completion in the sidebar (300 ms spring pop, ~weekly), and an easter-egg logo spin on long-press (opt-in by curiosity). Workhorse saves stay at 120 ms feedback. Delight stays delightful because it stays rare.

## Evaluation Rubric

Score 1–10:

- **1–2**: Decorative motion everywhere or none at all; layout properties animated; uniform slow durations; no reduced-motion; uninterruptible.
- **3–4**: Some transitions with purpose but hand-timed chaos; enter/exit symmetric and slow; hover noise; stagger unbounded.
- **5–6**: Token bands adopted; transform/opacity discipline; exits faster; modal/drawer/list recipes correct; reduced-motion basic.
- **7–8**: Full checklist: choreography with capped staggers, interruptible + velocity-carrying gestures, frequency-tuned durations, throttle-tested, motion inventory pruned.
- **9–10**: Additionally: spatial model documented and consistent product-wide; delight budget explicitly allocated to rare moments; slow-mo review ritual; the product passes the paradox test — motion everywhere it helps, yet users describe the app as "fast" rather than "animated."
