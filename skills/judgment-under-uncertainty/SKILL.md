---
name: judgment-under-uncertainty
description: "Use when deciding before the facts exist, someone is overconfident with expensive stakes, choosing prototype-fast vs production-careful, or judging in a post-mortem whether a call was bad or unlucky — calibrate, price being wrong."
---

# Judgment Under Uncertainty

## Purpose

Act well when the facts are incomplete: calibrate confidence to evidence, price the cost of being wrong in each direction, choose the speed-vs-correctness point deliberately, and build the habit of noticing — and saying — "I might be wrong about X, and here's what it would cost."

## When to use

- A decision must be made before the information you'd like exists (most decisions).
- Someone (possibly you) is very confident, and the stakes make miscalibration expensive.
- Choosing how much rigor a task deserves: prototype-fast vs production-careful.
- Weighing "ship now, 80% sure" against "verify for two days, 95% sure."
- Post-incident or post-mortem, when judging whether a call was bad or just unlucky.

## Goals

- Confidence expressed as a number or odds, matched to actual hit rate over time (calibration, not vibes).
- Asymmetry of errors priced before choosing: what does wrong-in-each-direction cost, and is it reversible?
- The speed/correctness dial set per-decision by blast radius and reversibility — not by team habit or personal temperament.
- Assumptions carried consciously, with tripwires that fire when one breaks.
- Decisions judged (and recorded) by process quality, not outcome luck.

## Expert Mental Model

- **Decisions and outcomes are different objects.** A good decision can lose; a bad one can win. Judging by outcomes alone trains superstition — the team that shipped recklessly and got lucky learns to ship recklessly. The expert asks "given what was knowable *then*, was the process sound?" and keeps a record so hindsight can't repaint it (see convergent-evaluation receipts; technical-writing decision docs). This is also self-protection: process-judged teams take smart risks; outcome-judged teams hide.
- **Calibration is a trainable skill with a scoreboard.** "Pretty sure" means 55% from one person and 95% from another. Experts state probabilities ("80% this migration is backward-compatible") and check themselves against results over time. Persistent overconfidence at the 90% level (being right 70% of the time you say 90%) is the most common and most expensive miscalibration in engineering — it converts directly into missed dates (see planning-and-estimation multipliers) and skipped verification (see verification generally).
- **Error costs are asymmetric; find the cheap side.** Almost every uncertain choice has a direction where being wrong is survivable and one where it isn't. Deleting data vs keeping stale data; paging too often vs missing the incident (see observability alert tuning); blocking a release vs shipping a bad one. The expert doesn't ask "what's most likely?" first — they ask "which mistake can I afford?" and bias toward it. Expected value with a survival constraint: never take a positive-EV bet that risks ruin (the wiped prod database has no hedge — see guard-git instincts; backups).
- **Reversibility sets the speed dial.** Two-way doors (most code, most configs, most product copy): decide at 60–70% confidence, ship, learn from reality — analysis past that point costs more than the occasional walk-back (see convergent-evaluation door-classification). One-way doors (public API contracts — see api-design versioning; data deletions; schema of published events — see event-driven; security posture — see web-security; the company's word to a customer): slow down, buy information, get the second brain. The classic failure is a temperament applied uniformly: the mover-fast who ships one-way doors at 60%, the verifier who takes two weeks on two-way doors.
- **Hidden assumptions are the variance you're not pricing.** Every plan carries "…assuming the vendor's docs are accurate, the traffic pattern holds, the person who knows the deploy is not on vacation." Unnamed, these are silent bets at unknown odds. Named — in a ledger with tripwires (see decomposing-ambiguity assumption ledger) — they become monitored positions. The expert reflex when confident: "what am I assuming that I haven't checked, and what's it doing to my error bars?"
- **Uncertainty is information to communicate, not weakness to hide.** "It's fine" and "I'm 85% it's fine; the 15% is the retry path, which I haven't tested under load" lead to different (better) decisions downstream. Teams where stated uncertainty is punished get confident-sounding guesses instead — and the uncertainty doesn't disappear, it just travels unlabeled into someone else's plan (see technical-leadership: making doubt speakable; observability: the system's version of the same honesty).

## Workflow

1. **Name the decision and the deadline it actually has** — many "urgent" decisions have a real clock of days, and manufactured urgency is a calibration destroyer.
2. **Classify the door**: reversible (cheap walk-back, contained blast radius) or one-way (contracts, deletions, published schemas, trust). Set the confidence bar accordingly: ~60–70% for two-way, ~90%+ plus a second reviewer for one-way.
3. **Price the asymmetry**: write one sentence per error direction — "wrong toward A costs X; wrong toward B costs Y." If one side risks ruin, the EV math is over; bias hard to the survivable side.
4. **State your confidence as a number** before gathering more info (the prior), and note what evidence would move it up or down — this is what makes step 5 a real decision.
5. **Buy information only if it's worth it**: cost of the check vs (probability of being wrong × cost of being wrong). A 2-day verification against a 15% chance of a 3-month mistake is cheap; against a 15% chance of a 1-hour revert, it's waste (see convergent-evaluation information-buying).
6. **Name the load-bearing assumptions** and set tripwires: "this holds unless traffic doubles / the vendor changes auth / the p95 crosses 400ms" — wire the tripwires to something that actually fires (see observability; planning-and-estimation re-planning triggers).
7. **Decide, and record the state of knowledge at decision time**: three lines — what we knew, what we assumed, why this option (see technical-writing decision docs). This is the artifact that lets you judge process later instead of outcome.
8. **Pre-commit the review point**: when results arrive, compare against the stated confidence — was 80% right about 80% of the time? Feed the scoreboard.
9. **When wrong**: distinguish unlucky (process sound, dice bad) from miscalibrated (evidence was available and unweighed) — only the second changes how you decide next time.

## Decision Tree

- If the choice is reversible and the walk-back is cheap → decide now at moderate confidence; reality is the cheapest oracle (see ci-cd: small deploys as experiments).
- If one error direction risks ruin (data loss, security exposure, broken public contract, legal) → the survivable-side bias overrides likelihood; take the "probably unnecessary" precaution (see web-security belt-and-braces; backups before migrations).
- If you're above 90% confident on something that matters →
  - Ask: what am I assuming? When did I last check it? Would a colleague put money on my number?
  - If the 90% rests on memory of docs, or "it worked last time" → downgrade until verified; those are 70% sources wearing 95% costumes.
- If two experts disagree confidently → the disagreement *is* the finding: they're using different assumptions; extract them (see decomposing-ambiguity: two restatements) before averaging or voting.
- If you can't put a number on your confidence → you haven't articulated the claim precisely enough; sharpen the claim ("the migration is safe" → "the migration is backward-compatible with v3 readers under concurrent writes") until a number becomes possible.
- If someone demands certainty ("will this work, yes or no?") → give the calibrated version anyway ("85%, and the 15% is X, which we'd detect within an hour and revert") — translating uncertainty into consequences-and-detection is what makes it usable by non-engineers.
- If the deadline forces action below your confidence bar → shrink the blast radius instead of inflating the confidence: flag it, canary it, stage it (see ci-cd progressive rollout) — turn the one-way door into a series of two-way doors.
- If you were wrong → run the unlucky-vs-miscalibrated split *before* the retro assigns blame; the decision doc from step 7 is the evidence.

## Heuristics

- Say the number out loud. "Probably" hides; "80%" can be wrong in a way you can learn from.
- The confidence you feel after reading docs is ~70% wearing 95% clothes; the confidence after *running it* is real (see verification instinct; learning-new-stacks: run, don't read).
- Never take a bet you can't survive losing, whatever the odds — ruin has no expected value.
- When everyone in the room agrees quickly on something important, buy one dissent: assign a devil's advocate or run a pre-mortem (see convergent-evaluation pre-mortems); fast consensus is a calibration smell, not a comfort.
- Time pressure narrows perception before it improves speed — under pressure, deliberately widen once: "what would I check if I had one more hour?" Sometimes you do have the hour.
- Trust the odometer, not the horoscope: your past hit rate at "90%" is the best predictor of your current 90%.
- "It's always worked before" is N observations of the happy path, not a proof — ask what's different this time (traffic, data shape, dependency versions) before reusing the confidence (see production-debugging: what changed).
- Precision signals should match actual precision: "about 2–4 weeks" and "17.5 days" claim different knowledge; don't let formatting inflate your certainty.
- The cheap tripwire beats the expensive analysis: often you can't know, but you *can* detect fast — invest in detection and reversal speed instead of prediction (see observability; ci-cd rollback).
- Beware sunk-confidence: having argued for a position raises your felt certainty without adding evidence — re-price after debates as if hearing the case fresh.

## Quality Checklist

- [ ] Decision classified by reversibility; confidence bar set to match.
- [ ] Both error directions priced; ruin-risk checked; bias direction chosen consciously.
- [ ] Confidence stated numerically, with the evidence that would move it.
- [ ] Information purchases justified by the check-cost vs error-cost arithmetic.
- [ ] Load-bearing assumptions named, with tripwires wired to real signals.
- [ ] Decision-time knowledge recorded (three lines minimum).
- [ ] Review point pre-committed; calibration scoreboard fed.
- [ ] Blast radius shrunk (canary/flag/stage) wherever confidence ran below the bar.
- [ ] Post-hoc judgment separates unlucky from miscalibrated.

## Failure Modes

- **Uniform temperament**: one speed for all doors — the cowboy who ships schema changes like CSS tweaks, the auditor who spends two days verifying a revertible config; both are the same error (unpriced reversibility) in opposite costumes.
- **Outcome-judged retros**: the reckless win promoted, the sound loss punished — six months later the team has learned to gamble and to hide, and every stated confidence is inflated by self-defense.
- **Confidence theater**: "definitely fine" because hedging reads as weakness in this room — the uncertainty travels unlabeled into the dependent team's plan and detonates there (see technical-leadership: what your certainty costs others).
- **EV worship without a survival constraint**: the 95%-safe migration run without a backup because "the odds are great" — the 5% branch contained ruin, and ruin doesn't amortize.
- **Analysis as anxiety management**: information bought past the point where it changes the decision — the third benchmark, the fifth stakeholder review — because deciding feels dangerous and studying feels safe (see convergent-evaluation: analysis has a budget).
- **The unnamed assumption**: "we assumed the CSV export was under a gigabyte" — nobody said it, so nobody watched it, so the OOM arrived unannounced (see memory-leaks; the assumption ledger, skipped).
- **Calibration without a scoreboard**: probabilities stated, never checked — numbers as vibes-with-decimals; the discipline is the *comparison*, not the stating.
- **Hindsight repainting**: after the outcome, "we always knew" — without the decision-time record, process-judgment is impossible and the loudest reviser writes history.

## Edge Cases

- **Compounding small risks**: ten independent "95% fine" steps are ~60% fine jointly — serial confidence multiplies down, and pipelines (see ci-cd; async-processing) are exactly such chains; price the chain, not the links.
- **Correlated failures**: two "independent" safeguards sharing a dependency (same region, same library, same person) are one safeguard with extra paperwork (see system-design failure domains) — independence claims deserve their own audit.
- **Expertise inversion**: deep experts are *better* calibrated in-domain and often *worse* just outside it, with no felt difference — the confidence feels identical; check whether this problem is actually inside the domain (see learning-new-stacks: the adjacent-domain trap).
- **Uncertainty about the uncertainty**: sometimes you can't even bound the odds (novel domain, no reference class) — that's Knightian territory; the move is not a braver number but a smaller bet: timebox, spike, stage (see research; planning-and-estimation when-not-to-plan).
- **Decisions that expire**: a sound call at 2024 prices/traffic/team may be unsound now — decisions inherit their assumptions' shelf lives; date-stamp them (see first-principles date-stamping) and re-open on tripwire, not on anniversary.
- **The confident stakeholder**: a non-engineer's "this definitely can't happen" about their own domain (finance rules, legal constraints) is data but not proof — the same calibration discipline applies across the org chart, applied with tact (see decomposing-ambiguity: instantiate with examples).
- **When stated doubt gets weaponized**: in low-trust rooms, "85%" becomes "so you're not sure" — the fix is consequence-framing ("here's what we'd see and do in the 15% case"), which reads as preparedness, not doubt.
- **Luck streaks**: three risky wins in a row *feel* like skill and adjust your priors upward without evidence — audit wins with the same rigor as losses; the market eventually grades honestly.

## Tradeoffs

- **Speed vs correctness is a dial, not a virtue contest**: fast-and-wrong wins on reversible low-blast decisions (reality teaches cheapest); slow-and-right wins on one-way doors — the failure is a fixed dial (see the mental model; planning-and-estimation: schedule pressure's exchange rate into defects).
- **Calibration honesty vs persuasion**: the accurate "70%" may lose the room to a rival's confident "definitely" — short-term. Long-term, the scoreboard is public and trust compounds to the calibrated; choose which game you're playing (and see technical-leadership for surviving the short term).
- **Tripwire density vs alarm fatigue**: every monitored assumption costs attention; instrument the load-bearing ones and consciously accept silence on the rest (see observability alert economics — identical curve).
- **Bias-to-survivable vs opportunity cost**: always taking the safe side has a price too (the launch not shipped, the migration not run) — survivable-side bias applies to *ruin-class* risks; ordinary risks get ordinary EV treatment.
- **Recording vs velocity**: decision docs cost minutes and pay in retro-honesty and anti-relitigation — three lines is the minimum viable record; the failure modes are zero lines and three pages.
- **Individual calibration vs team throughput**: making everyone number their confidence adds friction; deploy it where miscalibration is expensive (estimates, launch calls, incident hypotheses — see production-debugging: confidence-ranked hypotheses) rather than everywhere.

## Optimization Strategies

- Keep a personal prediction log: date, claim, probability, resolution — twenty entries in, your miscalibration pattern (usually: overconfident at 90, underconfident at 60) is visible and trainable.
- Make "what would change my mind?" a standing question in design reviews — it converts positions into testable claims and surfaces assumptions while they're cheap (see convergent-evaluation criteria-first).
- Institutionalize the pre-mortem on one-way doors (see convergent-evaluation) — it's the cheapest structured pessimism available and it de-stigmatizes doubt by making it an exercise.
- Build the revert muscle: fast rollback, feature flags, staged rollouts (see ci-cd) — every unit of reversal speed you buy converts one-way-ish doors into two-way doors and lets the whole team run at a faster confidence bar.
- Run calibration retros quarterly: pull five recorded decisions, judge process-vs-luck explicitly, adjust bars — the team version of the prediction log.
- Normalize consequence-framed uncertainty in status language ("green, with one watched risk: X") — templates teach the org that stated doubt is competence (see technical-writing status updates).

## Self Review

- What number is my confidence — and what's my track record when I say that number?
- Which direction of wrong is cheaper here, and did I bias toward it, or toward my temperament?
- Is this door one-way or two-way — and am I applying the matching speed, or my default speed?
- What am I assuming that I haven't checked? Which assumption, if false, hurts most — and is there a tripwire on it?
- Is more analysis still changing the decision, or just soothing me?
- If this goes wrong, will the record show a sound process — or will I be reconstructing my reasoning from memory in a blame-shaped room?
- Am I about to punish (or quietly celebrate) an outcome instead of a process?
- What would change my mind — and have I looked for it, or only for confirmation?

## Examples

**1. The migration with a survivable-side bias.**
Schema migration, 95% confident it's backward-compatible; the 5% branch corrupts writes (ruin-class, one-way). EV says go; the survival constraint says: not without converting the door. Plan restructured — expand-migrate-contract pattern (see postgres migrations; legacy-migrations), dual-write behind a flag, one-hour soak on 5% of traffic with a diff-checker, backup verified restorable *before* start. The 5% branch fires (an old reader nobody knew about — an unnamed assumption found by the tripwire, not the outage). Cost of the caution: two days. Value: the incident that became a log line.

**2. Calibration with a scoreboard.**
An engineer starts logging predictions: "90% the flaky test is the race in the queue consumer," "80% the vendor ships the fix by Friday." Three months in, the log shows 90%-claims landing 68% — systematic overconfidence, concentrated in claims about *other people's* timelines. Adjustment: vendor and cross-team predictions get an automatic downgrade and a fallback plan (see planning-and-estimation: dependencies as risks). Estimates stop slipping. Nothing about the engineer's knowledge changed — only the exchange rate between feeling and number.

**3. Two experts, one extraction.**
Staff engineer: "the cache will absorb the launch traffic, 95%." SRE: "it'll fall over, 80%." Instead of debate or hierarchy: assumption extraction (see decomposing-ambiguity). The engineer is assuming the traffic mix matches the beta (cache-friendly, 90% reads); the SRE is assuming launch-day behavior (cold caches, stampeding herds — see caching stampede protection). Both are right *given their assumptions*; the real question — which traffic mix? — is checkable: the last two launches' patterns split the difference. Decision: ship with stampede locks and a pre-warmed cache. The disagreement, mined instead of averaged, produced the design.

**4. Fast where fast is right.**
A two-way-door pile: button copy, an internal dashboard layout, a retry backoff constant, a log format. The team's habitual process — design doc, review meeting, sign-off — prices every door as one-way. Re-classified (see convergent-evaluation door-classification): all four ship same-day behind cheap reverts at ~65% confidence; two get walked back within the week for a total cost of an hour. Meanwhile the *actual* one-way door in the same sprint — the public webhook payload schema (see api-design versioning; event-driven schema evolution) — gets the full treatment: pre-mortem, second reviewer, consumer-versioned rollout. Same team, same week, two speeds: that's the skill.

## Evaluation Rubric

Score 1–10:

- **1–2**: Vibes-confidence ("should be fine"); one speed for every door; error asymmetry unpriced; wrong calls judged by outcome and repainted by hindsight.
- **3–4**: Occasional hedging without numbers; some caution on big decisions but by temperament, not classification; assumptions carried unnamed.
- **5–6**: Doors classified with matching confidence bars; numeric confidence on major calls; ruin-class risks biased survivable; key assumptions named.
- **7–8**: Full checklist: information purchases priced, tripwires wired, decision-time records kept, review points pre-committed, unlucky-vs-miscalibrated separated in retros.
- **9–10**: Additionally: running calibration scoreboard with measured (and improving) hit rates; reversal speed invested in as infrastructure; consequence-framed uncertainty is the team's native status language; at least one sound-process loss on record that was *not* punished — proof the culture prices decisions, not dice.
