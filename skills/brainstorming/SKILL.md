---
name: brainstorming
description: "Use when generating ideas (features, designs, architectures, stuck problems) or selecting among options, interrupting the rush to the first plausible idea, or ending a re-litigated decision — inversion, SCAMPER, criteria-first scoring, pre-mortems, kill criteria."
---

# Brainstorming: Diverge, Then Converge

## Purpose

Run the full idea loop: generate genuinely many, genuinely different options — quantity discipline, deferred judgment, forcing functions (inversion, constraint games, analogy transfer, SCAMPER) — then kill them fairly and fast with criteria set before options are viewed, reversibility-weighted scrutiny, pre-mortems, and cheap information-buying tests. Divergence without convergence is a wall of stickies; convergence without divergence is rationalizing the first idea.

## When to use

- Starting anything creative: features, designs, names, architectures, solutions to a stuck problem.
- The team converged on the first plausible idea within minutes (the reflex this skill exists to interrupt).
- Choosing between architectures, vendors, designs, strategies, or roadmap bets.
- A decision keeps getting re-litigated (the convergence never actually happened).
- A team is converging by fatigue, seniority, or sunk cost instead of judgment.
- Facilitating a group ideation or decision session.

## Goals

- 20–30+ ideas before any evaluation, including deliberately bad and deliberately weird ones; ≥3 that surprised the generator.
- Generation and judgment strictly separated in time (the single load-bearing rule).
- Criteria written and weighted *before* options are compared; scrutiny scaled to reversibility.
- The chosen option survived a pre-mortem; the runner-up is documented with a revisit trigger.
- Where uncertainty is decision-relevant, information was bought cheaply (spike, prototype, test) instead of argued expensively.

## Inputs

- The problem or decision, framed as a question ("How might we [outcome for whom]?") — or the recognition that the framing itself is contested.
- Who's in the room, their stakes and status dynamics (anchoring risk), and who decides.
- The decision's reversibility: two-way door or one-way door, and the real deadline.
- Hard constraints and disqualifiers (budget ceilings, compliance, latency floors) — separated from habits wearing constraint costumes.

## Outputs

- A clustered, named idea inventory captured verbatim, with surprises counted.
- A decision record: winner + why (criteria results), runner-up + revisit trigger, recorded dissent, accepted risks, kill criteria wired to calendars/monitors.
- Cheap-test results with pre-set pass bars where assumptions carried the decision.

## Expert Mental Model

**Divergence:**

- **The killer of ideation is inline evaluation.** Judging while generating prunes the tree at its root: each criticism doesn't just kill one idea, it teaches the generator to pre-censor the next ten. Enforce the mode split physically — generation time (no criticism, no feasibility talk, not even praise, which is also judgment) and evaluation time (later, structured). One person can hold this discipline alone; groups need a facilitator.
- **The gold is past the obvious.** The first third of any idea list is shared defaults; the interesting material starts after the "I'm out of ideas" moment — precisely where most sessions stop. The quantity target (20–30, not 5) is a forcing function to *outlast the obvious*.
- **Ideas breed by mutation and combination.** Generating from scratch exhausts fast; operating on *existing* ideas doesn't: invert it, extreme-ify it, combine it with its neighbor, transplant it to a different user/scale/medium. A list of 10 becomes 40 by operations — which is why capture-verbatim matters; half-formed idea #7 is feedstock, not failure.
- **Constraints generate; blank pages don't.** "Any ideas?" produces silence; "how would we do this with zero budget?" produces ten answers. Carry a kit: remove the assumed constraint (free/instant/infinite?), add an artificial one (10× users, ship tomorrow, no UI), swap the medium (the paper version? the human-concierge version?).
- **Inversion unlocks stuck rooms.** "How would we guarantee this fails?" — people are fluent in failure; the anti-goal list inverts item-by-item into a fresh strategy list. (The pre-mortem below is this same move pointed at risk.)
- **Analogy is structured theft.** Map the problem's *structure* (matching supply to demand under uncertainty; queueing under bursty load) into a domain that solved it long ago, then transfer the solution shape back — verifying the mapping holds at the load-bearing point (see first-principles).
- **Groups anchor; structure defends.** The first idea spoken aloud gravitationally pulls everything after it; seniority amplifies the pull. Defenses: write-first-share-after (brainwriting), round-robins that reach the quiet people, "yes, and" as the only permitted response. An unfacilitated group brainstorm reliably underperforms its members working alone; a structured one beats both.

**Convergence:**

- **Criteria before options, or it's rationalization with paperwork.** Humans pick intuitively in seconds and then construct justifications; criteria invented *after* seeing the options bend toward the favorite. Writing criteria, weights, and disqualifiers first is the single structural defense. If the criteria are contested, that's the real meeting.
- **Reversibility sets the scrutiny budget.** Two-way doors (feature flags, most code) deserve fast decisions — walking back is cheap. One-way doors (partition keys, public APIs, rewrites, brand names) deserve the full apparatus: pre-mortems, dissent, information-buying, sleep. The classic failure is uniform process — committees on trivia, YOLO on architecture (see system-design one-way doors).
- **The pre-mortem weaponizes hindsight in advance.** "It's twelve months later and this choice failed — write the story of why." Prospective hindsight surfaces risks that "any concerns?" misses, because it converts dissent from disloyalty into an assignment. Risks surfaced become mitigations, kill criteria, or disqualifiers.
- **Buy information before buying commitment.** When two options are close and the disagreement rests on an untested assumption, the move is neither more debate nor a coin flip — it's the cheapest test that discriminates: a day's spike, a five-user prototype, a load test, with the pass bar set *in advance*. Arguments are estimates; tests are evidence.
- **Kill the losers respectfully and keep the receipts.** A decision is "A wins *because* [criteria result], B returns to the table *if* [trigger]." Documented runners-up stop the re-litigation loop (the answer to "but what about B?" is a link) and preserve optionality when conditions shift (see technical-writing decision docs).
- **Convergence has known biases; name them to tame them**: *sunk cost* (past investment is irrelevant to forward value), *HiPPO* (the highest-paid opinion converging the room by gravity), *novelty bias* (new beats boring on excitement, loses on receipts), *feasibility-only convergence* (picking the easiest-to-build quietly kills every ambitious option — counter: keep one bold option alive into the final round on purpose), and *consensus-as-goal* (unanimity usually means the option offends no one and thrills no one).

## Workflow

**Phase 1 — Diverge:**

1. **Frame the prompt as a question worth answering**: "How might we [outcome for whom]?" — concrete enough to grip, open enough to diverge. If the framing is contested, generate *framings* first — often the most valuable round (see decomposing-ambiguity).
2. **Set the container**: quantity target (25+), time box (10–25 min per round), the no-judgment rule stated out loud, capture surface ready (one idea per line, verbatim).
3. **Round 1 — flush the obvious**: solo silent writing, everything that comes, no filtering. The defaults block the channel while unexpressed.
4. **Hit the wall, keep going**: at "I'm out," apply a forcing function rather than stopping — this is the moment the session is decided. Pick 2–3 per session: inversion (list ways to guarantee failure → invert each), constraint removal/addition, SCAMPER sweep over the current best, perspective shifts (how would a bank do this? a game studio? our harshest competitor?), analogy transfer.
5. **Mutation round**: take the 5 most interesting ideas; generate 3 variants of each (extreme, minimal, combined-with-another). Run a bad-ideas-on-purpose round when energy dips — laughter reopens the channel, and inverted bad ideas are regularly good ones.
6. **Capture and cluster**: affinity-map verbatim ideas, name the clusters, count the surprises — the session's quality metric. Stop while warm; schedule evaluation *later* (hours or a day — distance improves judgment).

**Phase 2 — Converge:**

7. **Classify the door**: reversible → lightweight path (criteria sketch, quick pass, decide today); irreversible/costly → full apparatus. Write which and why.
8. **Set criteria blind**: before reviewing options, list criteria with weights and — separately — *disqualifiers* (hard constraints). Contribute criteria before anyone advocates. Freeze them.
9. **Triage, then develop the shortlist**: plot impact × feasibility; kill the low-low quadrant without ceremony; shortlist the top-right plus one deliberate bold outlier. Develop 3–5 finalists to comparable depth (a one-pager each) — unequal depth is a thumb on the scale.
10. **Score against frozen criteria**: disqualifiers first (a 9/10 option that fails a hard constraint is a 0); coarse scales (1–3, not 1–10); note where scorers *disagree* — disagreements mark ambiguous criteria or untested assumptions.
11. **Pre-mortem the leader(s)**: 10 minutes, silently written: "this failed — why?" Cluster the stories; each becomes mitigate, monitor (→ kill criterion), or accept (risk register).
12. **Buy information where the decision still hangs**: name the load-bearing untested assumption; design the cheapest discriminating test with a pre-set pass bar; run it; re-score.
13. **Decide, with dissent recorded**: named decision-maker calls it (consensus is input, not the mechanism — see technical-leadership). Write-up: winner + why, runner-up + revisit trigger, accepted risks, kill criteria + review date. Wire tripwires to actual calendars/monitors (see observability).
14. **Close the loop with the losers' authors**: why theirs lost, what would revive it — the divergence pipeline stays generous only if evaluation is seen to be fair.

## Decision Tree

- If the session produces only sensible, expected ideas → the judgment filter is still on: run the bad-ideas round or inversion; restate the no-criticism rule.
- If ideas are wild but useless → ground with constraint *addition* (real budget, ship-in-a-month) — tune divergence by tightening the box, not by starting to judge.
- If the room goes silent or one voice dominates → drop group-verbal mode: silent brainwriting, round-robin reveal, ideas read without attribution.
- If the framing itself feels wrong mid-session → pause and diverge on framings ("what problem are we actually solving?"), then resume with the winner.
- If solo → the discipline shifts to persistence and operators: quantity enforced by count, forcing functions on schedule, the inline critic silenced by writing bad ideas deliberately.
- If the decision is reversible and cheap → decide now with a criteria sketch; the full apparatus is procrastination wearing rigor.
- If options can't be compared because they solve different problems → converge the *framing* first (see decomposing-ambiguity).
- If two finalists are within noise → an untested assumption separates them: buy the information; genuinely equivalent: pick by second-order criteria (optionality, exit cost, team energy) and *stop deliberating*.
- If the room converged instantly and unanimously → be suspicious: anchor? HiPPO? Run one pre-mortem round before ratifying.
- If someone keeps reopening a decided question → new evidence: re-open formally against recorded criteria; no new evidence: point at the decision doc.
- If every surviving option is safe/incremental → feasibility bias ran the table: resurrect the strongest killed bold option and make the case *for* it before finalizing.
- If no option passes the disqualifiers → don't force a winner: relax a constraint explicitly with its owner, or return to divergence with the constraint map as the new prompt (see first-principles).

## Heuristics

- Quantity is the lever: the correlation between idea count and best-idea quality is the field's most replicated finding. Set the number, hit the number.
- Capture verbatim, judge never (during generation): paraphrasing while capturing is stealth evaluation.
- The second wall matters more than the first: the ideas after the *second* "I'm out" are where even experienced generators surprise themselves.
- Specific beats abstract in prompts: "how might we make the first 60 seconds rewarding for a solo user?" out-generates "improve onboarding."
- Separate people diverge better than meetings: collect written ideas *before* the session; use the meeting for mutation and clustering.
- An idea that makes the room laugh is flagged, not discarded — humor marks a violated assumption.
- Weight the criteria before you love an option; re-weighting after scoring is the tell that rationalization has begun.
- Disqualifiers first, always: hard constraints filter before soft scores rank.
- Coarse scores, rich notes: 1–3 with a sentence per cell beats 1–10 silent precision — the sentences are where disagreements become visible.
- The pre-mortem question is "why DID it fail," never "could it fail" — the past tense is the mechanism.
- Sunk cost check, verbatim: "if we were starting today with no history, would we choose A?" — ask it out loud on any decision defending an incumbent.
- Never average your way out of a bimodal room: half score A high, half low → the room disagrees about a *fact* or a *criterion* — find which, don't split the difference.
- Cheap tests have pass bars set in advance, or they become Rorschach tests — everyone sees their prior confirmed in the prototype.
- Time-box deliberation to the door: even one-way doors have a decision date, because "still deciding" is itself a decision (usually for the incumbent).

## Quality Checklist

- [ ] Prompt framed at the right altitude; framing itself questioned at least once.
- [ ] Judgment deferred — verifiably: no feasibility talk, criticism, or praise during generation.
- [ ] Quantity target (20–30+) hit; the wall crossed at least twice; ≥2 forcing functions; ≥1 mutation pass.
- [ ] Group defenses used where group: silent-write-first, round-robin, build-only responses; capture verbatim.
- [ ] Output clustered and named; surprises counted (≥3); bad/weird ideas present on the list.
- [ ] Door classified and the process scaled to it, in writing.
- [ ] Criteria + weights + disqualifiers frozen before options were reviewed.
- [ ] Options developed to comparable depth; a bold option survived to the final round deliberately.
- [ ] Pre-mortem run on finalists; outputs became mitigations / kill criteria / accepted risks.
- [ ] Load-bearing assumptions tested where cheap; pass bars pre-set.
- [ ] Named decision-maker; decision recorded with rationale, dissent, runner-up + revisit trigger; kill criteria calendared.
- [ ] Losers' authors closed-loop with reasons.

## Failure Modes

- **The 4-idea "brainstorm"**: three obvious options and someone's pet idea; evaluation begins in minute six. The meeting laundered a foregone conclusion.
- **Inline sniping**: one feasibility comment in minute two, and the room quietly stops offering anything risky. The session continues; the divergence is already over.
- **Anchor gravity**: the VP speaks first; forty minutes of variations on the VP's idea follow.
- **Wild-only theater**: all constraint-removal, no grounding — a wall of moonshots, and the team concludes brainstorming "doesn't work here" (it wasn't finished, not broken).
- **Evaluation same-hour**: generation ends, judging begins immediately with the same brains in the same mode — attachment and fatigue judge instead of criteria.
- **Post-hoc criteria**: the favorite is chosen in minute one; the "framework" is reverse-engineered around it; everyone senses it; the process loses authority for every future decision.
- **The uniform committee**: six weeks to pick a linting rule; the database migration decided in a hallway. Scrutiny uncorrelated with reversibility — both tails wrong.
- **Consensus laundering**: the option nobody objects to wins — the beige compromise that thrills no one.
- **Prototype theater**: a test run without a pre-set bar; both camps declare victory from the same data.
- **Sunk-cost gravity**: "we've already built half of A" carries the vote; the second half of A costs more than all of B would have.
- **Decision without receipts**: A wins, nothing written; re-litigation monthly, from memory, forever.
- **Kill criteria as decoration**: written, never calendared, never checked; the zombie ships and shambles (see product-thinking).

## Edge Cases

- **Emotionally loaded topics** (reorgs, deprecating someone's system): judgment-deferral needs explicit safety framing, anonymous written input, sometimes an outside facilitator (see technical-leadership).
- **Expert-blindness domains**: deep experts generate inside their paradigm's walls; mix in adjacent-domain outsiders — the "naive" question is the constraint-removal an expert can't self-administer.
- **Remote/async groups**: anchoring defenses come free (async written rounds) but energy and building suffer — generate async, reserve synchronous time for mutation and clustering. Score asynchronously too: written blind scores → the meeting starts at the disagreements.
- **Time-critical loops** (incidents, closing windows): compress, don't skip — five minutes of "three genuinely different options, disqualifiers, cheapest-reversible-first" is the apparatus at emergency scale (see production-debugging).
- **Evaluating your own idea against others'**: conflict-of-interest by construction — hand the scoring to someone else, blind authorship where feasible, or at minimum declare it and over-weight the dissent.
- **Incommensurable criteria** (safety vs speed vs morale): weights across different value-types are political, not analytical — the weighting IS the leadership decision; don't hide the politics in the arithmetic.
- **Irreversibles with unknowable payoffs** (research bets, market entries): scores are theater at this uncertainty level — shift to bounded-loss thinking ("what can we afford to lose to find out?") and stage the commitment in tranches with kill criteria between.
- **Generating or evaluating with an LLM as partner**: the machine never fatigues and never self-censors, but it anchors *you* — generate your own round first, then prompt it with forcing functions; use it to stress-test (pre-mortem stories, unconsidered criteria), never to launder authority ("the model ranked them" is HiPPO with a GPU).
- **The pre-converged room**: stakeholders arrive having decided; either surface that honestly (convert to a pre-mortem on the decided option) or fight for one true written round before the anchor drops.

## Tradeoffs

- **Quantity vs depth**: divergence wants shallow-and-many (development is convergence's job); the exception is technical design, where "design it twice" needs real alternative shapes — 2–3 *radically* different architectures sketched to comparable depth, not labels.
- **Structure vs flow**: heavy facilitation defends against group pathologies and can suffocate a room that's genuinely cooking. Structure by default, loosen when ideas outrun the protocol.
- **Group vs solo**: groups build and cross-pollinate but anchor and posture; solos are unanchored but hit walls without rescue. The hybrid (solo-generate → group-mutate) captures most of both.
- **Time diverging vs deciding**: budget proportional to reversibility — an hour of divergence for a one-way door is cheap; for a two-way door, ten minutes may be the right spend.
- **Rigor vs momentum**: every day of evaluation is a day not building — and one wrong one-way door costs quarters. The door classification IS the resolution.
- **Consensus vs speed vs commitment**: consensus is slow and sticky; command is fast and brittle. Consult-then-decide with recorded dissent is the working middle for most doors.
- **Optionality vs focus**: the least-foreclosing choice hedges uncertainty and dilutes force; at some point the option premium exceeds the hedge value — the review date is where you re-ask.
- **Bold-option protection vs honest scoring**: the finals seat for ambition guarantees a *hearing* (developed to depth, pre-mortemed), never a handicap on the scores.

## Optimization Strategies

- Build the team's forcing-function deck (literal cards or a doc): the six games with one-line instructions — sessions start faster and plateau later.
- Template the decision doc (context, door class, criteria+weights, options, scores+notes, pre-mortem outputs, decision, dissent, runner-up+trigger, kill criteria+date) — the format enforces the sequence; the archive becomes the org's case law.
- Run the decision retro loop: quarterly, revisit 2–3 past decisions against outcomes — were the criteria right? did the kill criteria fire? (See planning-and-estimation calibration.)
- Build the assumption-test playbook: the ten cheap discriminating tests your domain uses most (latency spike, fake door, concierge pilot, five-user prototype) with cost/pass-bar templates.
- Seed a "crazy ideas" parking lot and a runner-up registry, both queryable: today's unusable moonshot and yesterday's runner-up are the cheapest "new" ideas the org will ever get.
- Rotate facilitation and the devil's-advocate seat: both are learnable checklists, not personalities; rotation prevents the permanent-contrarian and the empty ritual.
- Pair every recurring decision meeting with a 10-minute divergence prelude ("three real options before we discuss") — the smallest institutional dose with the highest yield.

## Self Review

- Did I actually defer judgment — or did feasibility sneak in wearing "just being practical"?
- How many ideas? How many after the second wall? How many surprised me?
- Are there bad/weird ideas on the list, or is it suspiciously respectable?
- Did the loudest voice's first idea shape everything after it?
- Did I write the criteria before I saw (or loved) the options? Would the weights survive publication?
- What door is this — and did the process I ran match it?
- Which assumption is carrying the decision, and could a cheap test have replaced this argument?
- Is there a named decision-maker, recorded dissent, a runner-up with a trigger, a kill criterion on a calendar?
- If we had no history with the incumbent, would it still win?
- Who lost, and have they heard why from me rather than from the grapevine?

## Examples

**1. Feature ideation, rescued from the pet idea — then converged with receipts.**
Session goal: reduce week-2 churn. The PM arrives with "email drip campaign" (the anchor-in-waiting). Facilitator runs silent-write-first: 8 people × 5 minutes → 31 distinct ideas before anyone speaks. Inversion round ("how would we guarantee week-2 churn?") yields "make them set up integrations alone," "hide the value they created" → inverted into pre-built integration templates and a week-1 recap artifact. Mutation crosses the recap with the shareability cluster → "week-1 recap you can send your boss." Final: 44 ideas, 6 clusters, 5 surprises. Evaluation happens Thursday, not in the room: criteria frozen (activation lift weight 3, build cost 2, support risk 1), drip campaign scores mid-pack and ships as one bet among three — with a kill criterion, not as the meeting's foregone conclusion.

**2. Stuck technical problem, unstuck by analogy.**
Flaky cross-service integration tests block every deploy (see ci-cd). Obvious ideas exhausted (retry, quarantine, more mocks). Structure named: "verifying agreements between independently-changing parties." Analogous domains: legal contracts, aviation pre-flight checks, diplomacy protocols. Transfer: contracts → *consumer-driven contract tests* (each consumer publishes expectations; providers verify in isolation). A constraint-addition round ("no shared environment may exist at all") independently converges on the same shape. The transcript shows the winning idea appearing at #23 — six past the second wall.

**3. Datastore choice, run by the book.**
One-way door (migration cost makes it so). Criteria frozen first: ops-fit for a 9-person team (weight 3), access-pattern fit (3), cost at 10× (2); disqualifiers: no managed offering = out, no row-level security = out (see auth). The trendy candidate fails a disqualifier *before* its seductive benchmarks enter the room. One bimodal scoring cell (ops-fit for candidate C) resolves as a fact-question with a two-day spike. Pre-mortem on the leader (Postgres) clusters on "write ceiling at year 3" → becomes a monitored kill criterion with a pre-sketched partition plan (see postgres, system-design). Decision doc: Postgres; runner-up C "if write volume 5× ahead of projection"; dissent recorded — the dissenter now owns the tripwire. Re-litigation attempts since: two, both answered with a link.

**4. The prototype that ended an argument.**
Two checkout-flow redesigns; three weeks of aesthetic debate between anchored camps. Convergence rebooted: criteria frozen (completion rate 80% of weight), the load-bearing assumption named — "users will/won't understand the single-page variant." Information bought: five-user prototype per variant, pass bar pre-set (completion ≥8/10, ≤1 confusion event). Result: single-page completes 9/10 but generates 4 confusion events at the payment step — *both* camps partially right, and the data pointed at a hybrid neither had proposed. Cost: four days. Three weeks of debate had produced zero of these facts.

## Evaluation Rubric

Score 1–10:

- **1–2**: First plausible idea adopted; "brainstorm" = discussion of the anchor; favorite chosen first, framework fitted after; no criteria, no receipts; sunk cost and seniority decide.
- **3–4**: A list gets made (≤10, all obvious); judgment leaks constantly; some scoring exists but criteria post-date the options; uniform process regardless of door; losers vanish silently.
- **5–6**: Real quantity discipline (20+), judgment mostly deferred, forcing functions used, verbatim capture; criteria frozen first on major decisions; door classification practiced; pre-mortem on the leader; decision docs with rationale.
- **7–8**: Full checklist both halves: walls crossed with operators, group defenses, mutation rounds, surprises counted; comparable-depth options with a protected bold seat, information bought with pre-set bars, dissent and runners-up recorded with triggers, kill criteria calendared.
- **9–10**: Additionally: framing itself diverged when needed; decision retros calibrate the judgment loop; the archive functions as case law; shipped decisions traceably include past-the-wall ideas — proof the machinery finds what reflex misses — and re-litigation has measurably died.
