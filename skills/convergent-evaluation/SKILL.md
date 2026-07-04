---
name: convergent-evaluation
description: "Use when selecting among options after divergence (architectures, vendors, designs, bets), ending a re-litigated decision, or committing serious resources — criteria-first scoring, pre-mortems, kill criteria."
---

# Convergent Evaluation & Idea Selection

## Purpose

Kill ideas fairly and fast: criteria set before options are viewed, reversibility-weighted scrutiny, pre-mortems, cheap information-buying tests, and pre-committed kill criteria — the judgment half that turns divergence into decisions.

## When to use

- After a divergence pass produced clusters of options (see divergent-thinking).
- Choosing between architectures, vendors, designs, strategies, or roadmap bets.
- A decision keeps getting re-litigated (the convergence never actually happened).
- A team is converging by fatigue, seniority, or sunk cost instead of judgment.
- Before committing serious resources to any single option.

## Goals

- Criteria written and weighted *before* options are compared (the anti-rationalization move).
- Scrutiny scaled to reversibility: one-way doors get depth, two-way doors get speed.
- The chosen option survived a pre-mortem; the runner-up is documented with a revisit trigger.
- Where uncertainty is decision-relevant, information was bought cheaply (prototype, test, spike) instead of argued expensively.

## Expert Mental Model

- **Criteria before options, or it's rationalization with paperwork.** Humans pick intuitively in seconds and then construct justifications; scoring criteria invented *after* seeing the options bend toward the favorite (the weights get tuned until the right answer wins). Writing criteria and weights first — what matters, what disqualifies, what's merely nice — is the single structural defense. If the criteria are contested, that's the real meeting; resolve it before comparing anything (see product-thinking: same discipline at portfolio scale).
- **Reversibility sets the scrutiny budget.** Two-way doors (feature flags, most code, pricing experiments) deserve fast decisions — deciding slowly costs more than occasionally deciding wrong, because you can walk back. One-way doors (partition keys, public APIs, rewrites, layoffs, brand names) deserve the full apparatus: pre-mortems, dissent, information-buying, sleep. The classic failure is uniform process — committees on trivia, YOLO on architecture (see system-design one-way doors; api-design promises).
- **The pre-mortem weaponizes hindsight in advance.** "It's twelve months later and this choice failed — write the story of why." Prospective hindsight reliably surfaces risks that direct questioning ("any concerns?") misses, because it converts dissent from disloyalty into an assignment. Every finalist gets one; the risks surfaced become mitigations, kill criteria, or disqualifiers (see product-thinking pre-committed kills; production-debugging postmortems — this is that, run before the incident).
- **Buy information before buying commitment.** When two options are genuinely close and the disagreement rests on an untested assumption ("approach B can't hit the latency budget"; "users won't understand the new flow"), the expert move is neither more debate nor a coin flip — it's the cheapest test that discriminates: a day's spike, a landing page, a prototype in five interviews, a load test (see product-thinking cheapest-sufficient-test; rag's not-RAG arithmetic). Arguments are estimates; tests are evidence; and a week of prototyping is cheaper than a quarter of building the wrong one.
- **Kill the losers respectfully and keep the receipts.** A decision isn't "option A wins"; it's "A wins *because* [criteria result], B was closest and returns to the table *if* [trigger]." Documented runners-up with revisit triggers do two jobs: they stop the re-litigation loop (the answer to "but what about B?" is a link), and they preserve optionality when conditions shift (see technical-writing decision docs; design-language ledger — same pattern).
- **Convergence has known biases; name them to tame them**: *sunk cost* (we've invested in A already — irrelevant to A's forward value), *HiPPO* (the highest-paid opinion converging the room by gravity — see divergent-thinking anchoring, evaluation edition), *novelty bias* (new beats boring on excitement, loses on receipts — see system-design boring-tech), *feasibility-only convergence* (picking the easiest-to-build, which quietly kills every ambitious option — the counter is keeping one bold option alive into the final round on purpose), and *consensus-as-goal* (unanimity usually means the option offends no one and thrills no one; the strongest choices often carry a documented objection).
- **Portfolio beats point-picking when you can afford it.** For bets (not for single architectural commitments): one safe + one bold beats five mediums — mediums share the downside of boldness (they can fail) without the upside (they can't transform). Convergence sometimes means choosing a *shape of spread*, not a single winner (see product-thinking focus-vs-portfolio).

## Workflow

1. **Classify the door**: reversible → lightweight path (criteria sketch, quick pass, decide today); irreversible/costly → full apparatus below. Write which and why — the classification itself is often the clarifying act.
2. **Set criteria blind**: before reviewing options, list decision criteria with weights and — separately — *disqualifiers* (hard constraints: budget ceilings, compliance, latency floors). Have the group contribute criteria before anyone advocates an option. Freeze them.
3. **First pass — two-axis triage**: plot all options impact × feasibility (or value × cost). Kill the low-low quadrant without ceremony; shortlist the top-right plus one deliberate bold outlier (the anti-feasibility-bias seat).
4. **Develop the shortlist to comparable depth**: 3–5 options, each sketched enough to score honestly (a one-pager: how it works, costs, risks, what it forecloses). Unequal depth is a thumb on the scale — the familiar option always scores better until the others are drawn.
5. **Score against the frozen criteria**: coarse scales (1–3, not 1–10 — false precision invites weight-gaming); score disqualifiers first (a 9/10 option that fails a hard constraint is a 0); note where scorers *disagree* — the disagreements mark either ambiguous criteria or untested assumptions.
6. **Pre-mortem the leader(s)**: 10 minutes, silently written: "this failed — why?" Cluster the failure stories; for each: mitigate (plan changes), monitor (becomes a kill criterion), or accept (risk register). A leader that collapses under its pre-mortem loses the crown — better here than in production.
7. **Buy information where the decision still hangs**: identify the load-bearing untested assumption behind the remaining disagreement; design the cheapest discriminating test with a pre-set pass bar; run it; re-score. (If no test can discriminate within the decision's timeframe, say so and decide on the recorded balance — deciding under acknowledged uncertainty beats fake certainty.)
8. **Decide, with dissent recorded**: named decision-maker calls it (consensus is input, not the mechanism — see technical-leadership disagree-and-commit); the write-up: winner + why (criteria results), runner-up + revisit trigger, accepted risks, kill criteria + review date.
9. **Set the tripwires**: the kill criteria and pre-mortem monitors become actual monitors/review dates on a calendar (see product-thinking kill criteria honored; observability: tripwires need instruments).
10. **Close the loop with the losers' authors**: why theirs lost, what would revive it — the divergence pipeline stays generous only if evaluation is seen to be fair (see divergent-thinking ownership politics).

## Decision Tree

- If the decision is reversible and cheap → decide now with a criteria sketch; the full apparatus is procrastination wearing rigor (speed is the correct form of quality here).
- If options can't be compared because they solve different problems → converge the *framing* first (see decomposing-ambiguity; divergent-thinking framing rounds) — scoring apples against staplers produces confident nonsense.
- If two finalists are within noise of each other →
  - An untested assumption separates them → buy the information (spike/test/prototype).
  - Genuinely equivalent → pick by second-order criteria (team energy, optionality preserved, exit cost) and *stop deliberating* — past this point, deliberation is pure cost.
- If the room converged instantly and unanimously → be suspicious: anchor? HiPPO? too-safe option? Run one pre-mortem round before ratifying — cheap insurance against comfortable consensus.
- If someone keeps reopening a decided question →
  - New evidence in hand → legitimate: re-open formally against the recorded criteria/trigger.
  - No new evidence → point at the decision doc; the re-litigation loop is what the receipts exist to end.
- If every surviving option is safe/incremental → feasibility bias has run the table: resurrect the strongest killed bold option and make the case *for* it before finalizing (the devil's-advocate seat, pointed at ambition).
- If the decision-maker is also the loudest advocate → separate the roles: advocates present, a different named person decides, or scoring happens written-and-blind before advocacy (see divergent-thinking write-first — same defense, evaluation edition).
- If no option passes the disqualifiers → don't force a winner; the honest outputs are: relax a constraint (explicitly, with its owner), or return to divergence with the constraint map as the new prompt (see first-principles constraint interrogation).

## Heuristics

- Weight the criteria before you love an option; re-weighting after scoring is the tell that rationalization has begun.
- Disqualifiers first, always: hard constraints filter before soft scores rank — it prevents the seductive option that can't actually ship from distorting the field.
- Coarse scores, rich notes: 1–3 with a sentence per cell beats 1–10 silent precision; the sentences are where the real information lives (and where disagreements become visible).
- The pre-mortem question is "why DID it fail," never "could it fail" — the past tense is the mechanism (it grants permission and demands specifics).
- Time-box deliberation to the door: two-way doors get minutes-to-hours; one-way doors get days-to-weeks — but even one-way doors have a decision date, because "still deciding" is itself a decision (usually for the incumbent).
- The runner-up file is half the value: "B if [trigger]" converts tomorrow's second-guessing into a lookup.
- Watch for criteria that are proxies for "familiar" ("team knows it" is legitimate; weight it honestly rather than laundering it through five other criteria).
- One documented objection is a feature: record the strongest dissent with the decision (it sharpens the kill criteria and honors the dissenter — see technical-leadership disagree-and-commit).
- Sunk cost check, verbatim: "if we were starting today with no history, would we choose A?" — ask it out loud on any decision defending an incumbent.
- Never average your way out of a bimodal room: if half score A high and half score it low, the room disagrees about a *fact* or a *criterion* — find which, don't split the difference (see evals contested labels: same move).
- Cheap tests have pass bars set in advance, or they become Rorschach tests — everyone sees their prior confirmed in the prototype (see product-thinking pre-set pass/fail; evals gating).
- The option that forecloses least is worth a bonus when uncertainty is high: optionality is a criterion, not a cowardice (see abstraction-and-simplicity: deferring decisions cheaply is a skill).

## Quality Checklist

- [ ] Door classified (reversible/one-way) and the process scaled to it, in writing.
- [ ] Criteria + weights + disqualifiers frozen before options were reviewed.
- [ ] Options developed to comparable depth before scoring; a bold option survived to the final round deliberately.
- [ ] Disqualifiers applied first; coarse scores with notes; scorer disagreements surfaced and resolved as facts-vs-criteria.
- [ ] Pre-mortem run on finalists; outputs became mitigations / kill criteria / accepted risks.
- [ ] Load-bearing assumptions tested where cheap and discriminating; pass bars pre-set.
- [ ] Named decision-maker; decision recorded with rationale, dissent, runner-up + revisit trigger.
- [ ] Kill criteria wired to calendars/monitors, not just prose.
- [ ] Losers' authors closed-loop with reasons.
- [ ] Sunk-cost and HiPPO checks actually asked out loud where they applied.

## Failure Modes

- **Post-hoc criteria**: the favorite is chosen in minute one; the "framework" is reverse-engineered around it; everyone senses it; the process loses its authority for every future decision.
- **The uniform committee**: six weeks and four meetings to pick a linting rule; the database migration decided in a hallway. Scrutiny uncorrelated with reversibility — both tails wrong.
- **Consensus laundering**: the option nobody objects to wins — the beige compromise that thrills no one; five mediums funded, transformation impossible (see portfolio logic).
- **Pre-mortem skipped for the favorite**: risks surface at month three as incidents instead of at day one as line items; the postmortem reads like the pre-mortem would have (see production-debugging — the rhyme is the indictment).
- **Prototype theater**: a test run without a pre-set bar; both camps declare victory from the same data; a week spent buying information nobody agreed how to read.
- **Sunk-cost gravity**: "we've already built half of A" carries the vote; forward value never separately assessed; the second half of A costs more than all of B would have.
- **Silent HiPPO**: scores collected after the director "just shares a perspective"; the spreadsheet ratifies the room's gravity and calls it analysis (see divergent-thinking anchoring).
- **Decision without receipts**: A wins, nothing written; re-litigation monthly; the runner-up's advocate relitigates from memory against defenders arguing from vibes — the meeting is quarterly and immortal.
- **Kill criteria as decoration**: written, never calendared, never checked; the zombie ships and shambles (see product-thinking zombie portfolio).

## Edge Cases

- **Decisions under time pressure** (incidents, closing windows): compress, don't skip — 5 minutes of "options, disqualifiers, cheapest-reversible-first" is the apparatus at emergency scale (see production-debugging mitigation levers: it's the same table).
- **Evaluating your own idea against others'**: conflict-of-interest by construction — hand the scoring to someone else, or blind the options' authorship where feasible; at minimum declare it and over-weight the dissent.
- **Incommensurable criteria** (safety vs speed vs morale): weights across genuinely different value-types are political, not analytical — surface that honestly (the weighting IS the leadership decision; see technical-leadership) rather than hiding the politics in the arithmetic.
- **Option sets that shift mid-evaluation** (vendor updates pricing, a new candidate appears): re-open the criteria freeze deliberately and once — chronic re-opening means the decision date was fiction.
- **Two-team decisions** (shared platform choices): criteria must be co-authored before either team advocates, and the decision-maker named across both — else the evaluation becomes a proxy war and the loser's team treats the outcome as imposed (see technical-leadership stakeholders).
- **Evaluating irreversibles with unknowable payoffs** (research bets, market entries): scores are theater at this uncertainty level — shift to bounded-loss thinking: "what can we afford to lose to find out?" and stage the commitment (option-style tranches with kill criteria between).
- **The decision that's actually values** ("should we build engagement-maximizing features?"): no criteria matrix resolves a values conflict — name it as one and route it to the people accountable for values (see product-thinking exec pet project honesty).
- **AI/tool-assisted evaluation**: models score options tirelessly and inherit the criteria's flaws at scale — use them to stress-test (generate pre-mortem stories, find unconsidered criteria, argue the bold option), never to launder authority ("the model ranked them" is HiPPO with a GPU).

## Tradeoffs

- **Rigor vs momentum**: every day of evaluation is a day not building — and one wrong one-way door costs quarters. The door classification IS the resolution; the failure is spending the budget uniformly (see workflow step 1).
- **Blind fairness vs informed judgment**: blinding authorship and pre-freezing criteria remove bias and also remove legitimate context ("the team that will run this hates it" matters). Blind the *scoring*, then un-blind for the *decision* conversation — sequence, don't choose.
- **Consensus vs speed vs commitment**: consensus is slow and sticky (everyone owns it); command is fast and brittle (compliance without conviction). Consult-then-decide with recorded dissent is the working middle for most doors (see technical-leadership decision mechanics).
- **Optionality vs focus**: preserving options (the least-foreclosing choice, the staged commitment) hedges uncertainty and dilutes force; at some point the option premium exceeds the hedge value — the review date is where you re-ask.
- **Documented rigor vs process theater**: the full written apparatus on every decision teaches the org that decisions mean meetings; the discipline is a ladder — hallway-with-criteria-sketch at the bottom, full ceremony at the top — and the skill is placing each decision on the right rung.
- **Bold option protection vs honest scoring**: reserving a finals seat for ambition fights feasibility bias — and can become affirmative action for bad moonshots. The seat guarantees a *hearing* (developed to comparable depth, pre-mortemed), never a handicap on the scores.

## Optimization Strategies

- Template the decision doc (context, door class, criteria+weights, options, scores+notes, pre-mortem outputs, decision, dissent, runner-up+trigger, kill criteria+date) — the format enforces the sequence, and the archive becomes the org's case law.
- Run the decision retro loop: quarterly, revisit 2–3 past decisions against outcomes — were the criteria right? did the kill criteria fire? was the runner-up trigger ever consulted? (See planning-and-estimation calibration ledger — judgment improves only with feedback.)
- Build the assumption-test playbook: the ten cheap discriminating tests your domain uses most (latency spike, fake door, concierge pilot, load test, five-user prototype) with cost/time/pass-bar templates — information-buying becomes a reflex when the menu is printed (see product-thinking decision tree).
- Rotate the devil's-advocate seat with teeth: the assignee's job is the strongest case *against* the leader and *for* the bold option — rotation prevents both the permanent-contrarian and the empty ritual.
- Score asynchronously before meeting synchronously: written blind scores → the meeting starts at the disagreements (the only interesting part) — an hour of alignment for fifteen minutes of meeting (see divergent-thinking async rounds: same physics).
- Keep the runner-up registry queryable: when conditions shift (a constraint lifts, a vendor changes), grep the triggers — revived runners-up are the cheapest "new" ideas the org will ever get (see divergent-thinking parking lot).

## Self Review

- Did I write the criteria before I saw (or before I loved) the options? Would the weights survive publication?
- What door is this — and did the process I ran match it?
- Did every finalist get a pre-mortem, including the one I'm rooting for?
- Which assumption is carrying the decision, and could a cheap test have replaced this argument?
- Where are the disqualifiers' receipts? Did anything seductive skip them?
- Is there a named decision-maker, a recorded dissent, a runner-up with a trigger, a kill criterion on a calendar?
- If we had no history with the incumbent, would it still win?
- Who lost, and have they heard why from me rather than from the grapevine?

## Examples

**1. Datastore choice, run by the book.**
One-way door (migration cost makes it so — see system-design partition keys). Criteria frozen first: ops-fit for a 9-person team (weight 3), access-pattern fit (3), cost at 10× (2), ecosystem maturity (2); disqualifiers: no managed offering = out; no row-level security = out (compliance — see authorization RLS). Four candidates developed to one-pager depth; the trendy one fails a disqualifier (no managed offering) *before* its seductive benchmarks enter the room. Scoring surfaces one bimodal cell — ops-fit for candidate C splits the room → resolved as a fact-question with a two-day spike (operate it locally, run the runbook drills). Pre-mortem on the leader (Postgres): failure stories cluster on "write ceiling at year 3" → becomes a monitored kill criterion (WAL throughput alert; see postgres) with a pre-sketched partition plan (see system-design example 3). Decision doc: Postgres; runner-up C "if write volume 5× ahead of projection"; dissent recorded (one engineer's scaling worry — now the tripwire's owner). Re-litigation attempts since: two, both answered with the link.

**2. The prototype that ended an argument.**
Two checkout-flow redesigns; three weeks of aesthetic debate (see divergent-thinking pre-converged room — both camps anchored). Convergence rebooted: criteria frozen (completion rate is 80% of the weight; the rest: support-ticket risk, build cost); the disagreement's load-bearing assumption named — "users will/won't understand the single-page variant." Information bought: five-user prototype test per variant, pass bar pre-set (task completion ≥8/10, ≤1 confusion event). Result: single-page completes 9/10 but generates 4 confusion events at the payment step — *both* camps were partially right, and the data pointed at a hybrid neither had proposed. Cost: four days. The three weeks of debate had produced zero of these facts (see product-thinking: tests beat arguments — the argument was estimates colliding).

**3. Portfolio convergence at quarter planning.**
Twelve initiative candidates; the room's reflex: fund the top six by average score — six mediums (see the beige failure mode). Intervention: re-frame as portfolio — criteria include *variance*, not just expected value. Outcome: four safe-core bets (high-confidence, compounding) + one bold (the killed-then-resurrected marketplace experiment, given the finals seat and a bounded-loss budget with staged tranches: $40k to the first kill-criterion checkpoint) + one deliberate non-bet documented ("we are not entering X this year because…" — the anti-goal receipt). The bold bet's pre-mortem produces its tranche gates. Two quarters later the bold bet dies at gate two — *on schedule, at budget* — and the write-up recycles its demand evidence into an adjacent bet (see product-thinking kill example: the learning is the return).

**4. Converging under fire (the compressed apparatus).**
Incident: primary region degrading; options: fail over now (30-min data-loss window), throttle and diagnose (users suffer, data safe), emergency scale-up (cost, uncertain fix). Sixty seconds of structure instead of zero: disqualifier check ("any option that risks payment-data loss is out" — kills naive failover; a scoped failover variant survives), reversibility sort (scale-up is fully reversible → try first while failover is *prepared*), pre-set tripwire ("if p99 not halved in 10 min, execute failover"). The compressed ceremony fits inside the incident's tempo and prevents both panic-failover and analysis-paralysis (see production-debugging decision tree — this is that skill's decision spine, named). Post-incident, the 60-second record becomes the postmortem's cleanest section.

## Evaluation Rubric

Score 1–10:

- **1–2**: Favorite chosen first, framework fitted after; no criteria, no receipts; sunk cost and seniority decide; decisions re-litigated forever.
- **3–4**: Some scoring exists but criteria post-date the options; uniform process regardless of door; pre-mortems and tests absent; losers vanish silently.
- **5–6**: Criteria frozen first on major decisions; door classification practiced; coarse scoring with disqualifiers; pre-mortem on the leader; decision docs with rationale.
- **7–8**: Full checklist: comparable-depth options with a protected bold seat, information bought with pre-set bars, dissent and runners-up recorded with triggers, kill criteria calendared.
- **9–10**: Additionally: decision retros calibrate the judgment loop; the assumption-test playbook makes evidence the reflex; the archive functions as case law; and re-litigation has measurably died — the receipts, not the meetings, hold the decisions.
