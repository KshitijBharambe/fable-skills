# Divergent Thinking

## Purpose

Generate genuinely many, genuinely different ideas — quantity discipline, deferred judgment, and forcing functions (inversion, constraint games, analogy transfer, SCAMPER, perspective shifts) that push past the obvious first third into the territory where original options live.

## When to use

- Starting anything creative: features, designs, names, architectures, campaigns, solutions to a stuck problem.
- The team converged on the first plausible idea within minutes (the reflex this skill exists to interrupt).
- A problem has resisted the obvious approaches.
- Preparing options for a decision that deserves real alternatives (see convergent-evaluation — this skill feeds that one).
- Facilitating a group ideation session.

## Goals

- 20–30+ ideas before any evaluation, including deliberately bad and deliberately weird ones.
- Generation and judgment strictly separated in time (the single load-bearing rule).
- At least 3 ideas that surprised the generator — evidence the session escaped the obvious.
- Output captured verbatim and clustered, ready for convergent evaluation.

## Expert Mental Model

- **The killer of ideation is inline evaluation.** Judging while generating ("that won't work because…") prunes the tree at its root: each criticism doesn't just kill one idea, it teaches the generator to pre-censor the next ten. Experts enforce the mode split physically — generation time (no criticism, no feasibility talk, not even praise, which is also judgment) and evaluation time (later, structured — see convergent-evaluation). One person can hold this discipline alone; groups need a facilitator to hold it for them.
- **The gold is past the obvious.** The first third of any idea list is what anyone would think of (the shared defaults); the second third is variations; the interesting material starts where it gets uncomfortable — after the "I'm out of ideas" moment, which is precisely where most sessions stop. The quantity target (20–30, not 5) isn't bureaucracy; it's a forcing function to *outlast the obvious*. Persistence past the cringe is the skill.
- **Ideas breed by mutation and combination, not just spawning.** Generating from scratch exhausts fast; operating on *existing* ideas doesn't: take any idea and invert it, extreme-ify it, combine it with its neighbor, transplant it to a different user/scale/medium. A list of 10 becomes 40 by operations. This is why capture-verbatim matters — half-formed idea #7 is feedstock, not failure.
- **Constraints generate; blank pages don't.** "Any ideas?" produces silence; "how would we do this with zero budget?" produces ten answers. The mind searches better in a bounded space. Experts carry a kit of constraint-games: remove the assumed constraint (what if it were free/instant/legal/infinite?), add an artificial one (10× the users, 1/10 the budget, ship tomorrow, no UI at all), and swap the medium (what's the paper version? the human-concierge version? the API-only version?).
- **Inversion unlocks stuck rooms.** "How would we guarantee this fails?" / "how could we make users hate this?" — people are fluent in failure and criticism; the anti-goal list inverts item-by-item into a fresh strategy list, and it's *fun*, which reopens a room that's gone flat. (The pre-mortem in convergent-evaluation is this same move pointed at risk.)
- **Analogy is structured theft.** "How does nature/logistics/gaming/restaurants solve this shape of problem?" — the move is mapping the problem's *structure* (matching supply to demand under uncertainty; teaching a skill through failure; queueing under bursty load) into a domain that solved it long ago, then transferring the solution shape back (verify the mapping holds at the load-bearing point — see first-principles). Random stimulus (open a dictionary, force-connect the word to the problem) is analogy's chaotic cousin: low hit rate, real hits.
- **Groups anchor; structure defends.** The first idea spoken aloud gravitationally pulls every subsequent idea toward it; seniority amplifies the pull. The defense is write-first-share-after (everyone generates silently, then reveals — "brainwriting"), round-robins that reach the quiet people, and building-on ("yes, and") as the only permitted response during generation. An unfacilitated group brainstorm reliably underperforms its members working alone; a structured one beats both.

## Workflow

1. **Frame the prompt as a question worth answering**: "How might we [outcome for whom]?" — concrete enough to grip, open enough to diverge. Wrong altitude kills sessions: "how might we improve the product" (too vast — no traction), "which button color" (too closed — no room). If the framing is contested, generate *framings* first (a divergence round on the question itself — often the most valuable round; see decomposing-ambiguity).
2. **Set the container**: quantity target (25+), time box (10–25 min per round), the no-judgment rule stated out loud, capture surface ready (one idea per sticky/line, verbatim).
3. **Round 1 — flush the obvious**: solo silent writing, everything that comes, no filtering. Getting the defaults *out* is necessary; they block the channel while unexpressed.
4. **Hit the wall, keep going**: at "I'm out," apply the first forcing function rather than stopping — this is the moment the session is decided.
5. **Rounds 2–4 — forcing functions** (pick 2–3 per session, not all):
   - *Inversion*: list ways to guarantee failure → invert each.
   - *Constraint removal*: no budget/time/physics/legacy limits — what would we do? (Then: which part of that is achievable anyway?)
   - *Constraint addition*: must ship in a day; must work with no UI; must serve 100× users; must cost nothing to run.
   - *SCAMPER sweep* over the current best ideas: Substitute / Combine / Adapt / Magnify-Minify / Put to other use / Eliminate / Reverse.
   - *Perspective shift*: how would a bank do this? a game studio? a street market? our harshest competitor? a mischievous intern?
   - *Analogy transfer*: name the problem's structure, list 3 domains with the same structure, mine each.
6. **Mutation round**: take the 5 most interesting ideas so far; generate 3 variants of each (extreme version, minimal version, combined-with-another version).
7. **Bad-ideas-on-purpose round** (when energy dips or the room is too safe): worst possible solutions, actively harmful ones — laughter reopens the channel, and inverted bad ideas are regularly good ones.
8. **Capture and cluster**: group verbatim ideas by theme (affinity mapping), name the clusters, note the surprises (ideas nobody expected to write) — the surprise count is the session's quality metric.
9. **Stop while warm, hand off cold**: end generation with energy remaining (exhausted sessions poison the next one); schedule evaluation *later* (hours or a day — distance improves judgment) and hand the clustered output to the convergent process (see convergent-evaluation).

## Decision Tree

- If the session produces only sensible, expected ideas → the judgment filter is still on: run the bad-ideas round or inversion; restate the no-criticism rule (someone is frowning eloquently).
- If ideas are wild but useless → ground with constraint *addition* (real budget, real users, ship-in-a-month) — divergence tuned by tightening the box, not by starting to judge.
- If the group circles one theme → force perspective shifts or ban the theme for a round ("next 10 ideas may not involve the app").
- If the room goes silent → drop group-verbal mode: silent brainwriting 5 minutes, then round-robin reveal; silence in groups is usually anchoring + status fear, and writing dissolves both.
- If one voice dominates → structure harder: written rounds, facilitator round-robins, ideas read aloud without attribution.
- If the problem framing itself feels wrong mid-session → pause and diverge on framings ("what problem are we actually solving?" — see decomposing-ambiguity: the question behind the question), then resume with the winner.
- If solo (no group to defend against) → the discipline shifts to *persistence and operators*: quantity target enforced by count, forcing functions applied on schedule, and the inline-critic silenced by writing bad ideas deliberately on the list.
- If ideas are needed on a technical design → same machinery, plus: "design it twice" minimum (see design-interface thinking) — force 2–3 *radically* different shapes (monolith vs pipeline vs event-driven; buy vs build vs don't) before detailing any.

## Heuristics

- Quantity is the lever: the correlation between count and best-idea quality is the most replicated finding in the field. Set the number, hit the number.
- Capture verbatim, judge never (during generation): paraphrasing while capturing is stealth evaluation — the facilitator writes what was said.
- "Yes, and" over "yes, but": during generation, every response to an idea either builds or stays silent.
- The second wall matters more than the first: most people push past "I'm out" once; the ideas after the *second* wall are where even experienced generators surprise themselves.
- Specific beats abstract in prompts: "how might we make the first 60 seconds feel rewarding for a solo user?" out-generates "how might we improve onboarding" every time.
- Weird early beats weird late: sanctioning strangeness in round 1 (facilitator contributes a deliberately odd idea first) raises the whole session's ceiling — permission is set by example.
- Separate people diverge better than meetings: for high-stakes questions, collect written ideas *before* the session; use the meeting for building and mutation, not first-generation.
- Energy is a resource: 3 × 15-minute rounds with breaks beat one 60-minute grind; stop rounds at the peak, not the dregs.
- Steal the adjacent-possible: review what the last three sessions produced but didn't use — old clusters re-read against a new problem are pre-warmed feedstock.
- An idea that makes the room laugh is flagged, not discarded — humor marks a violated assumption, and violated assumptions are where original solutions hide.
- Count your surprises: <3 ideas that genuinely surprised you = the session stayed home; run one more forcing round.

## Quality Checklist

- [ ] Prompt framed at the right altitude ("how might we…" with a who and an outcome).
- [ ] Judgment deferred — verifiably: no feasibility talk, no criticism, no praise during generation.
- [ ] Quantity target (20–30+) set and hit; the wall crossed at least twice.
- [ ] ≥2 forcing functions applied; ≥1 mutation/combination pass over existing ideas.
- [ ] Group defenses used where group: silent-write-first, round-robin, build-only responses.
- [ ] Everything captured verbatim; nothing "cleaned up" in flight.
- [ ] Output clustered and named; surprises counted (≥3).
- [ ] Bad/weird ideas present on the list (their absence = the filter was on).
- [ ] Evaluation scheduled separately, with distance; handoff to convergent-evaluation clean.
- [ ] Framing itself was questioned at least once.

## Failure Modes

- **The 4-idea "brainstorm"**: three obvious options and the pet idea someone brought in; evaluation begins in minute six. Nothing diverged; the meeting laundered a foregone conclusion.
- **Inline sniping**: "interesting, but users would never…" — one feasibility comment in minute two, and the room quietly stops offering anything risky. The session continues; the divergence is already over.
- **Anchor gravity**: the VP speaks first; forty minutes of variations on the VP's idea follow. No written round, no defense.
- **Wild-only theater**: all constraint-removal, no grounding — a wall of moonshots nobody can use, and the team concludes brainstorming "doesn't work here" (it wasn't finished, not broken).
- **Facilitator paraphrase-filtering**: ideas captured as sanitized summaries; the weird edges — the valuable parts — sanded off at the whiteboard.
- **Evaluation same-hour**: generation ends, judging begins immediately with the same brains in the same mode — attachment and fatigue judge instead of criteria (see convergent-evaluation: distance is an input).
- **The exhausted grind**: 90 minutes without breaks "to be thorough"; the last 40 produce nothing and the team dreads the next session — the ritual's reputation is a resource too.
- **Solo skip**: individuals assume the discipline is for groups and take their own first idea; the inline critic runs uncontested precisely where no one can see it.

## Edge Cases

- **Emotionally loaded topics** (reorgs, deprecating someone's system): judgment-deferral needs explicit safety framing, anonymous written input, and sometimes an outside facilitator — the ideas at stake are attached to people in the room (see technical-leadership).
- **Expert-blindness domains**: deep experts generate inside their paradigm's walls; mix in adjacent-domain outsiders deliberately — the "naive" question ("why does it need a database at all?") is the constraint-removal an expert can't self-administer (see learning-new-stacks beginner's-mind value).
- **Remote/async groups**: anchoring defenses come free (async written rounds) but energy and building suffer — run generation async, reserve synchronous time for mutation and clustering.
- **Time-critical divergence** (incident workarounds, deadline crunches): compress, don't skip — even 5 minutes of "three genuinely different options" before committing beats zero (see production-debugging mitigation levers: options-first is the same move under fire).
- **Idea ownership politics**: attribution during capture breeds attachment and status games; strip names at capture, restore credit at retro — the idea must survive on merit before it acquires an owner (see convergent-evaluation sunk-cost).
- **Generating with an LLM as partner**: the machine never fatigues and never self-censors, but it anchors *you* — generate your own round first, then prompt it with forcing functions ("20 more, each violating one assumption of the first 20"), and treat its output as feedstock for mutation, not verdicts.
- **The pre-converged room**: stakeholders arrive having decided; the "brainstorm" is theater — either surface that honestly (convert to a pre-mortem on the decided option; see convergent-evaluation) or fight for one true written round before the anchor drops.
- **Cultural dynamics**: in high power-distance or criticism-averse cultures, verbal "yes, and" sessions can still suppress — lean harder on anonymous written rounds; the discipline's *mechanics* must adapt even when its principles don't.

## Tradeoffs

- **Quantity vs depth**: 30 shallow sketches vs 5 developed concepts — divergence wants shallow-and-many (development is convergence's job); the exception is technical design, where an idea needs a minimum sketch depth to be distinguishable (design-it-twice needs real alternative shapes, not labels).
- **Structure vs flow**: heavy facilitation (rounds, timers, protocols) defends against groups' pathologies and can suffocate a room that's genuinely cooking. Read the energy: structure by default, loosen when the ideas are outrunning the protocol.
- **Wild vs grounded**: too-safe sessions produce nothing new; too-wild ones produce nothing usable. The mature session oscillates deliberately — remove constraints to escape the local optimum, add them back to make the escape actionable.
- **Group vs solo**: groups build and cross-pollinate but anchor and posture; solos are unanchored but hit their own walls without rescue. The hybrid (solo-generate → group-mutate) captures most of both, at the cost of scheduling ceremony.
- **Time spent diverging vs deciding**: divergence has diminishing returns and deciding has deadlines; the honest budget is proportional to the decision's reversibility (see convergent-evaluation one-way doors) — an hour of divergence for a one-way door is cheap; for a two-way door, ten minutes may be the right spend.
- **Freshness vs preparation**: pre-reading and problem immersion improve idea quality and pre-anchor the space; the split — immerse in the *problem* (data, user sessions, constraints), abstain from the *solutions* (competitor feature lists anchor hardest) — threads it.

## Optimization Strategies

- Build the team's forcing-function deck (literal cards or a doc): the six games with one-line instructions — sessions start faster and plateau later when the rescue moves are ready-to-hand.
- Track session metrics lightly: idea count, surprise count, and (later) how many shipped decisions trace back to which round — the retro data teaches which functions work for *this* team's domains.
- Seed a "crazy ideas" parking lot that persists across sessions: today's unusable moonshot is next quarter's option when constraints shift (see product-thinking validated-problems backlog: same pattern, ideas edition).
- Train facilitation as a rotating skill, not a personality: the checklist (rules stated, rounds timed, quiet voices reached, verbatim capture) is learnable; teams with three capable facilitators diverge on demand.
- Prime with problem immersion, not solution research: before big sessions, circulate user recordings, support tickets, constraint lists — fuel that doesn't anchor (see product-thinking evidence).
- Pair every recurring decision meeting with a 10-minute divergence prelude ("three real options before we discuss") — the smallest institutional dose with the highest yield; it retrains the converge-first reflex org-wide.

## Self Review

- Did I actually defer judgment — or did feasibility sneak in wearing "just being practical"?
- How many ideas? How many after the second wall? How many surprised me?
- Which forcing functions did I use — and did I stop at the first wall where one was needed?
- Are there bad/weird ideas on the list, or is it suspiciously respectable?
- Did the loudest voice's first idea shape everything after it? What did the written round say before the talking started?
- Is anything captured in my words instead of theirs?
- Did I question the framing at least once?
- Is evaluation scheduled with distance — or am I about to judge with generation-warm attachment?

## Examples

**1. Feature ideation, rescued from the pet idea.**
Session goal: reduce churn in week 2. The PM arrives with "email drip campaign" (the anchor-in-waiting). Facilitator runs silent-write-first: 8 people × 5 minutes → 31 distinct ideas before anyone speaks. Round 2, inversion ("how would we guarantee week-2 churn?"): "make them set up integrations alone," "hide the value they created in week 1," "go silent after day 3" → inverted into: pre-built integration templates, a week-1 recap artifact ("here's what you built"), and a day-4 human check-in for high-value signups. Mutation round crosses the recap artifact with the shareability cluster → "week-1 recap you can send your boss." Final: 44 ideas, 6 clusters, 5 surprises. The drip campaign ships too — as one cluster among six, not the meeting's foregone conclusion. Evaluation happens Thursday (see convergent-evaluation), not in the room.

**2. Stuck technical problem, unstuck by analogy + constraint games.**
Problem: flaky cross-service integration tests block every deploy (see ci-cd flakes). Obvious ideas exhausted (retry, quarantine, more mocks). Structure named: "verifying agreements between independently-changing parties." Analogous domains listed: legal contracts (signed agreements + audits, not re-negotiation per interaction), aviation (pre-flight checklists against known interfaces), diplomacy (protocols + embassies). Transfer: contracts → *consumer-driven contract tests* (each consumer publishes its expectations; providers verify against them in isolation — the integration test's job, decomposed). Constraint-addition round ("no shared environment may exist at all") independently converges on the same shape, plus recorded-replay verification. The eventual architecture came from the legal-contracts mapping; the session's transcript shows it appearing at idea #23 — six past the second wall.

**3. Solo divergence with the discipline intact.**
One engineer naming a new internal tool (low stakes, good practice): target 30, timer 15 minutes. First wall at 9 (all descriptive compounds). SCAMPER: Reverse → names from the *user's* outcome, not the tool's function (+6); Adapt → names from adjacent domains: cartography, kitchens, rail (+8). Bad-ideas round on purpose: three awful puns → one, inverted from its badness, becomes the shortlist's dark horse. Final count 34, surprises 4. Total cost: 20 minutes. The point isn't the name — it's that the solo discipline (count, wall, operators, deliberate bad ideas) ran exactly like a facilitated session, because the inline critic doesn't take small stakes off.

**4. Diverging on the framing itself.**
Prompt as delivered: "how might we speed up the export feature?" (engineering had a caching design ready — the session was nearly theater; see the pre-converged room edge case). One true round on framings first: "how might we… make exports unnecessary? / make waiting painless? / deliver the data where it's needed before it's asked for?" The third framing wins the room: half the exports feed the same Thursday meeting (recognized from support archaeology — see product-thinking's export example). The session pivots to scheduled-delivery ideas; the caching design ships too, but as a minor rung. The most valuable divergence of the hour happened before a single solution idea was generated — on the question.

## Evaluation Rubric

Score 1–10:

- **1–2**: First plausible idea adopted; "brainstorm" = discussion of the anchor; criticism throughout; nothing captured.
- **3–4**: A list gets made (≤10, all obvious); judgment leaks constantly; loudest voice shapes the space; no forcing functions.
- **5–6**: Real quantity discipline (20+), judgment mostly deferred, one or two forcing functions, verbatim capture, clustering done.
- **7–8**: Full checklist: walls crossed with operators, group defenses (write-first, round-robin), mutation rounds, surprises counted, evaluation separated in time.
- **9–10**: Additionally: framing itself diverged when needed; bad-ideas and analogy rounds land usable material; session metrics tracked and facilitation rotates; the team's shipped decisions traceably include ideas from past-the-wall territory — proof the machinery finds what reflex misses.
