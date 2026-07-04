---
name: first-principles
description: "Use when conventional approaches have failed, 'that's how it's done' appears in a justification, costs/timelines feel inherited, or a 10x improvement is needed — decompose to load-bearing facts and rebuild."
---

# First-Principles Thinking

## Purpose

Decompose problems to their load-bearing facts — separating physics from convention, constraint from habit — and rebuild solutions from the ground up: constraint interrogation, Chesterton's fence discipline, analogy verification, and the question-behind-the-question.

## When to use

- A problem resists all conventional approaches (the defaults have been tried).
- "Because that's how it's done" appears in a design justification.
- Costs, timelines, or "impossibilities" feel inherited rather than derived.
- Entering a domain where best practices may be cargo cult (or may be load-bearing — the point is to find out which).
- A 10× improvement is needed where 10% thinking is installed.

## Goals

- Every constraint on the problem is tagged: fundamental / economic / regulatory / conventional / assumed.
- At least one "impossible" or "required" element traced to its actual source — and found movable or confirmed fixed.
- Solutions rebuilt from fundamentals compared honestly against the conventional baseline (which sometimes wins).
- Fences understood before removal (Chesterton honored, not just quoted).

## Expert Mental Model

- **Reasoning by analogy is the default; reasoning from fundamentals is the override.** Analogy ("this is like X, so do what X does") is fast, usually right, and occasionally catastrophically limiting — it imports X's constraints along with X's solutions. First-principles thinking is expensive and slow; experts deploy it *selectively*: where the stakes are high, where convention's costs feel suspiciously inherited, where 10× matters. Running it on everything is paralysis; running it on nothing is cargo cult. The skill begins with choosing where.
- **Constraints have a taxonomy, and the taxonomy is the tool.** For each constraint ask "what enforces this?": *fundamental* (physics, math, information theory — light speed, CAP-flavored limits, entropy), *economic* (true cost structures — which change with scale and technology, so date-stamp them), *regulatory/contractual* (real but negotiable on different timescales, with owners you can talk to), *conventional* (industry habit — "everyone uses X" enforces nothing), *assumed* (nobody ever checked — the richest category). Most "requirements" dissolve under this interrogation into the bottom two categories; the discipline is doing the tagging with evidence, not vibes.
- **The cost-from-components move**: when a price or effort estimate feels inherited ("that costs $50k," "that takes a quarter"), decompose to raw inputs — materials, compute, labor-hours, API calls — and price the components. The famous version is batteries priced by commodity metals vs market price; the everyday version is "why does this report take three weeks?" decomposed into two hours of compute and 14 days of hand-offs. When component cost ≪ current cost, the delta is process, margin, or convention — all attackable.
- **Chesterton's fence is first-principles' seatbelt.** "Remove the fence once you know why it was built" — the naive first-principler deletes the weird check, the redundant step, the ugly special case, and rediscovers (in production) the 2019 incident it guarded (see root-cause-analysis; legacy-migrations characterization). Understanding the fence isn't deference to it: many fences guarded conditions that no longer exist — but *that* is a finding, with evidence, not an assumption. The move is archaeology, then demolition.
- **Question the question before answering it.** "How do we make the elevator faster?" assumes the problem is speed; the lobby mirror solved "waiting feels long." The problem-behind-the-problem move (see decomposing-ambiguity; product-thinking's job-behind-the-request) is first-principles applied to the *framing*: what outcome is actually wanted, and is this question the only path to it? Half of "impossible" problems are hard questions standing in front of easy ones.
- **Analogies are hypotheses, not proofs.** After rebuilding from fundamentals, analogies re-enter as transfer devices ("this is structurally like queueing at a restaurant") — the expert discipline is verifying the mapping *at the load-bearing point*: the place where your solution depends on the analogy holding. Restaurant queues and request queues both smooth bursts; only one can tell customers to come back Tuesday. Analogy verification is where borrowed solutions earn residency (see divergent-thinking analogy transfer — that skill generates them; this one stress-tests them).
- **"Best practices" are average practices for average contexts.** They encode the constraint-set of the contexts that produced them; when your context differs on a load-bearing dimension (scale, team, risk profile, era), the practice may not transfer (see system-design resume-driven architecture — the inverse failure). The first-principles question isn't "is this practice good?" but "do the conditions that made it good hold here?" — which respects the practice's wisdom while refusing its authority.

## Workflow

1. **Pick the target deliberately**: high stakes, suspected inherited constraints, or a needed 10×. Write why this problem earns the expensive treatment (if it doesn't — use the defaults and move on; see the mental model's selectivity).
2. **State the goal in outcome terms**, stripped of solution vocabulary ("move people between floors with minimal perceived wait," not "faster elevator") — the question-behind-the-question pass (see decomposing-ambiguity restatement).
3. **List every constraint and requirement** as currently believed — the inherited spec. Include the invisible ones ("must be a web app," "must use our platform," "must be real-time") by asking "what am I not even considering, and why not?"
4. **Tag each constraint** [fundamental / economic / regulatory / conventional / assumed] *with the evidence for the tag*: who/what enforces it, when it was last verified, what would change it. The tags with no evidence are homework, not conclusions.
5. **Run the fence check on everything tagged conventional/assumed**: why does this exist? Archaeology — commit history, old incidents, the person who was there, the regulation it once satisfied (see root-cause-analysis timeline discipline). Outcomes: still-load-bearing (retag it), obsolete (removable, with the evidence), or unknowable (treat as risk, test carefully — see legacy-migrations characterization tests as the safe fence-prober).
6. **Decompose costs/efforts to components** where numbers feel inherited: raw compute, storage, labor-hours, per-unit fees. Compare component-sum to current cost; name where the delta lives.
7. **Rebuild from the keepers**: with only fundamental + verified constraints, design fresh — "if we started today with no legacy, what would we build?" Generate 2–3 rebuild candidates (divergence discipline applies here — see divergent-thinking; first-principles without quantity just swaps one anchor for another).
8. **Re-import reality**: the rebuilds now face the constraints you *chose* to honor (migration costs, team skills, regulatory timelines) — this is where "green-field beautiful" meets "brown-field true." Often the answer is a staged path from here to there (see legacy-migrations strangler thinking) rather than the rebuild itself.
9. **Compare against the conventional baseline honestly** (see convergent-evaluation: criteria, pre-mortems, information-buying) — first-principles analysis that always concludes "rebuild everything" is a bias wearing a method. Sometimes the fence-check *validates* the convention; that's a success, not a failure: you now know why, and the "because that's how it's done" is retired either way.
10. **Record the constraint map** — tags, evidence, fences checked, dated — as a living artifact: next year's team inherits verified constraints instead of folklore (see technical-writing decision docs; the map is the deliverable that outlives the decision).

## Decision Tree

- If the conventional approach is cheap, reversible, and adequate → use it; spend the first-principles budget elsewhere (see convergent-evaluation door-classification — same economics).
- If a constraint blocks everything ("we can't because X") →
  - Tag X. Fundamental → design around it honestly (and check: fundamental at *your* scale? Light-speed matters for global sync, not for a single-region app).
  - Economic → decompose to components; re-price at current technology (yesterday's "too expensive" ages fast — date-stamp it).
  - Regulatory/contractual → find the owner and the actual text; the real rule is often narrower than its folklore ("compliance requires X" frequently means "someone once said compliance requires X" — see the assumed tag).
  - Conventional/assumed → fence-check, then test the removal cheaply (see convergent-evaluation information-buying).
- If "why" hits bedrock in ≤2 hops → you're at fundamentals; rebuild from there.
- If "why" recurses forever ("because B, because C, because…") → you're in convention all the way down; pick the deepest layer you can act on and treat deeper layers as context (see root-cause-analysis: fix at the deepest *economical* layer).
- If the rebuild looks 10× better on paper → suspect the paper: which real constraint did the rebuild quietly drop? (Migration cost, team capability, and support burden are the usually-dropped three — see product-thinking feature tax.) Re-import and re-compare.
- If someone quotes a best practice as a trump card → ask for the conditions that made it best ("at what scale/team/era does this hold?") — adopt, adapt, or decline *with the conditions named* (see system-design boring-tech: sometimes the practice wins the interrogation).
- If the analogy is carrying the design → find the load-bearing point (where does the solution *depend* on the mapping?) and verify exactly there; the rest of the analogy is decoration.
- If first-principles keeps concluding "everything must be rebuilt" → the method has become the bias; hand the analysis to convergent-evaluation with the incumbent given a fair criteria run.

## Heuristics

- Five-whys with a taxonomy beats five-whys alone: each "why" answer gets a tag, and the recursion stops at the first fundamental (see root-cause-analysis: trigger vs root vs conditions — same laddering).
- Date-stamp every economic "impossible": compute, storage, model capability, and API pricing all move an order of magnitude per era — "we evaluated that in 2021" is an expired tag.
- The phrase "for historical reasons" is a fence-check work order, not an explanation.
- Prefer removing a constraint to optimizing within it: 10% comes from optimization; 10× usually comes from a dissolved constraint ("what if we didn't need real-time?" beats "how do we make real-time faster" — see caching staleness budgets as institutionalized constraint-dissolution).
- Ask "what would make this problem trivial?" — then price whatever that is; sometimes the trivializer (pre-computation, a data purchase, a policy change) costs less than the clever solution to the hard version.
- The intern question is a tool: "why do we do it this way?" asked sincerely by someone with no status to lose surfaces assumed-constraints the veterans can't see — borrow the move even when you're the veteran (see learning-new-stacks beginner's mind; divergent-thinking outsider mixing).
- Count the hops to physics: a design justified in ≤2 hops from fundamentals ("we batch because network round-trips dominate, because latency") is sturdy; one justified in 5 hops of convention is a Jenga tower — know which you're standing on.
- Every "must" in a spec is a claim wearing a uniform: re-write specs with "must (because [tag])" and watch half the musts become "prefers."
- When decomposing costs, include the coordination tax honestly: components + hand-offs is the true sum; pretending hand-offs are zero is how naive rebuilds under-bid reality (see planning-and-estimation integration costs).
- Keep one conventional option alive through the rebuild comparison — as control group, not as tribute (see convergent-evaluation bold-seat inverted: here the *boring* seat is protected).
- The fence you can't explain after real archaeology is a risk, not a green light: probe it with a reversible test (flag it off for 1% — see ci-cd) before demolition.

## Quality Checklist

- [ ] Target justified: stakes/inheritance/10× need named before the expensive analysis began.
- [ ] Goal restated in outcome terms; the question-behind-the-question asked.
- [ ] Constraint list complete (including invisible defaults) with tags AND evidence per tag.
- [ ] Every conventional/assumed tag fence-checked with actual archaeology (not vibes-archaeology).
- [ ] Inherited numbers decomposed to components where load-bearing; deltas located.
- [ ] ≥2 rebuild candidates generated from verified constraints only.
- [ ] Reality re-imported: migration/team/support costs priced into the rebuilds.
- [ ] Honest comparison vs conventional baseline run through real evaluation (criteria first — see convergent-evaluation).
- [ ] Outcome recorded either way — including "convention validated, here's why."
- [ ] Constraint map saved, dated, owned — folklore retired.

## Failure Modes

- **Naive fence demolition**: the "pointless" retry-delay deleted; the thundering herd of 2019 returns on schedule (see production-debugging metastable failures). Chesterton quoted, never practiced.
- **First-principles as aesthetic**: the analysis performed to justify a predetermined rewrite — constraints tagged by convenience, fences checked selectively, the incumbent scored by its worst day and the rebuild by its brochure (see convergent-evaluation post-hoc criteria; legacy-migrations rewrite death spiral).
- **Physics-blindness**: rebuilding into an actual fundamental ("we'll just sync globally in real-time," "we'll compress it further" past entropy) — the taxonomy's top tier mis-tagged as convention; expensive education follows.
- **Everything-is-negotiable syndrome**: regulatory and contractual constraints treated as vibes; the rebuild meets the auditor; the auditor wins (see authorization/compliance edges).
- **Analysis paralysis by recursion**: every constraint interrogated to bedrock on a two-way-door decision — the method's cost ignored; the quarter spent tagging while competitors shipped defaults (the selectivity rule from the mental model, violated).
- **Analogy smuggling**: the rebuild "from fundamentals" quietly imports an analogy's whole constraint set unverified — first-principles theater over reasoning-by-resemblance (the load-bearing point never checked).
- **Component-cost fantasy**: raw inputs summed, coordination/integration/support taxed at zero; the "10× cheaper" rebuild lands at 1.2× after reality re-imports (see planning-and-estimation 90% syndrome — same arithmetic hole).
- **Lone-genius framing**: the analysis run solo against a team's accumulated context; half the "assumed" tags were load-bearing knowledge the analyst never asked about — first-principles without archaeology interviews is just confidence (see technical-leadership: the fence-builders often still work here).

## Edge Cases

- **Constraints that are fundamental *at scale* but not below it** (and vice versa): consistency guarantees, coordination costs, attention limits — tag them with their scale domain ("fundamental above N, conventional below"), or the rebuild optimizes for the wrong regime (see system-design five numbers).
- **Fences guarding rare events**: the check that fires once a year looks dead in any month's archaeology — search incident history and low-frequency paths before declaring obsolescence (see memory-leaks soak-length logic: the observation window must match the phenomenon).
- **Political fences**: some conventions exist to keep a peace treaty between teams — removing them is possible and correct only with the treaty renegotiated (see technical-leadership stakeholders; the constraint is real, just not technical).
- **Moving fundamentals**: model capabilities, hardware economics, and legal landscapes shift under long projects — a constraint map with dates needs re-verification triggers, or the plan built on 2024's fundamentals ships into 2027's (see system-design quarterly assumption re-checks).
- **The problem that dissolves**: sometimes the question-behind-the-question reveals no problem at all (the report nobody reads, the sync nobody needs) — the highest-value outcome of the method is occasionally *deletion*, and it takes nerve to bank it (see product-thinking deletions ship too).
- **Safety/security domains**: "why do we do this?" has answers like "defense in depth" where redundancy IS the function — a layer that looks pointless given the other layers is the design working (see web-security belt-and-braces; don't first-principle away the second lock).
- **Regulated impossibilities that are actually lobbying targets**: on long horizons, regulatory constraints have change-processes too — tag with timescale ("fixed for 2 years, negotiable in 5") rather than binary fixed/free.
- **First-principles in someone else's domain**: the confident outsider's rebuild of medicine/law/payments rediscovers why the conventions exist, expensively — pair the method with domain archaeology interviews; the taxonomy needs domain knowledge to tag honestly (see research skill: primary sources).

## Tradeoffs

- **Depth of interrogation vs decision tempo**: every tag verified is time; the door-classification from convergent-evaluation prices it — one-way doors earn full archaeology; two-way doors get the 15-minute tag pass.
- **Rebuild purity vs migration reality**: the from-scratch design is cleaner; the path from here usually routes through hybrid states that dilute it (see legacy-migrations strangler) — the purist who won't stage ships nothing; the pragmatist who won't envision the end-state staggers without direction. Hold both: end-state from fundamentals, path from the brown field.
- **Constraint-questioning vs team trust**: interrogating every convention reads, to the people who built them, as indictment — the archaeology-interview framing ("help me understand what this protects") extracts the knowledge *and* honors the builders; the audit framing burns sources you'll need (see technical-leadership).
- **Original thinking vs proven paths**: fundamentals-derived solutions carry discovery risk (you're the first to hit their failure modes); conventions carry known costs and known fixes (see system-design boring-tech). The portfolio answer: originality where it's the advantage, convention where it's plumbing.
- **The method's cost vs its hit rate**: most first-principles runs conclude "the convention holds" — that looks like waste and isn't (retired folklore, verified map), but budget it honestly: the method pays in occasional 10×s and steady folklore-retirement, not in per-run wins.
- **Component-cost truth vs organizational feelings**: pricing the delta between component cost and current cost names where margin/process lives — sometimes that's a vendor, sometimes a team. Truth with a communication plan (see technical-writing incident-report tact) beats truth as a grenade.

## Optimization Strategies

- Institutionalize the constraint map as a living doc per system: tags, evidence, dates, owners — new engineers read verified constraints instead of absorbing folklore; re-verification triggers fire on schedule (see system-design assumption re-checks).
- Run a quarterly "assumption sweep" on one system: one hour, list the musts, tag them fresh — the cheapest recurring dose of the method, and the folklore graveyard grows steadily.
- Pair the method with divergence and convergence explicitly: first-principles *derives the real constraint set*; divergent-thinking *generates within it*; convergent-evaluation *chooses honestly* — the three skills are one pipeline, and skipping the middle produces single-anchor rebuilds.
- Keep a "retired fences" log with the evidence that retired them: when the removed check's ghost gets re-proposed ("shouldn't we validate X?"), the log answers in one link (see convergent-evaluation receipts — same anti-relitigation machinery).
- Practice on costs first: component-decomposition of one inherited number per month (that vendor bill, that "three-week" process) — the muscle builds on low-stakes reps, and the hit rate on costs is the method's highest.
- Interview before you interrogate: 30 minutes with the fence-builder (or their commit history) before any removal proposal — the cheapest archaeology, and the one most skipped.

## Self Review

- Why did this problem earn the expensive method — and would I defend that in front of the backlog?
- What question is behind my question? Did I try to dissolve the problem before solving it?
- For each constraint: what's the tag, and what's the *evidence* for the tag? Which tags are actually homework I skipped?
- Which fences did I check with real archaeology — and which did I demolish on vibes?
- Where do my rebuild's numbers come from — components plus coordination, or components plus hope?
- Did the conventional baseline get a fair trial with frozen criteria — or was the conclusion loaded from the start?
- What did I date-stamp, and when does it expire?
- If the fence-builder read my analysis, what would they correct?

## Examples

**1. The "three-week report" decomposed.**
Finance's monthly close report: three weeks, accepted as physics ("it's always been three weeks"). Component decomposition: actual computation ≈ 2 hours; the rest = data hand-offs between five teams (each batching to their own weekly cadence), two approval queues, and one manual reconciliation guarding a 2018 incident. Tags: compute (fundamental, 2h), hand-offs (conventional — cadences nobody chose), approvals (regulatory: one real, one assumed — the second traced to a manager's preference, retired), reconciliation (fence-checked: the 2018 bug it guarded was fixed in 2019; replaced with an automated check — see root-cause-analysis class-fixes). Rebuild: event-fed pipeline with one human approval. Close time: 3 weeks → 2 days. Nothing was invented; four inherited constraints were tagged and three dissolved.

**2. Chesterton honored: the fence that stayed.**
A first-principles sweep flags a "pointless" 150 ms artificial delay in the login path — obvious removal candidate ("latency is bad, this is self-inflicted"). Archaeology before demolition: commit message references a ticket; the ticket documents a credential-stuffing wave — the delay is a deliberate tarpit that made bulk attacks uneconomical, tuned with security (see authentication rate-limiting heuristics). Outcome: retagged [security control, load-bearing], documented in the constraint map with its evidence, *and* improved — the flat delay became adaptive (clean logins fast, suspicious patterns slow), which the archaeology enabled: understanding the fence's job made it upgradable, not just survivable. The naive removal would have shipped a 150 ms win and a bot-storm regression.

**3. Best practice interrogated: microservices declined with receipts.**
New CTO inherits a plan: "decompose the monolith — industry best practice." The conditions-check (see the mental model's average-practices rule): the practice's payoff conditions are many-teams deploy-contention and independent-scaling needs (see system-design org-pressure test); this org: 11 engineers, one product, deploy contention zero (trunk-based, 6 deploys/day — see ci-cd). Tags: "monoliths don't scale" (assumed — falsified by the load numbers: 300 QPS against a ceiling of thousands); "hiring needs modern architecture" (conventional, weakly evidenced). Verdict recorded in the constraint map: modular monolith, extraction triggers defined (team >25 or a component with 10× divergent scaling). The best practice wasn't wrong — its conditions weren't present, and now the *conditions* are monitored instead of the fashion.

**4. Dissolving the constraint instead of optimizing it.**
Goal as delivered: "make search indexing faster — users complain new products take 40 minutes to appear" (see rag freshness). Optimization framing would tune the indexing pipeline (10–20% available). Question-behind-the-question: what do users actually need? Interviews (see product-thinking behavioral evidence): sellers need *their own just-added product* visible immediately; nobody notices the global lag. Constraint re-tagged: "the index must be globally fresh in minutes" [assumed] → dissolved into "the *author* must see their item instantly" — solved with read-your-writes routing for the author's session (see postgres replica-lag edge; state-management) at ~1% of the pipeline-rebuild cost. Global freshness stayed at 40 minutes; complaints ended. The 10× wasn't in the pipeline; it was in the requirement.

## Evaluation Rubric

Score 1–10:

- **1–2**: Convention followed or defied by temperament, not analysis; "that's how it's done" and "burn it down" both unexamined; fences demolished on vibes.
- **3–4**: Some why-asking, untagged; costs taken at face value; analogies imported unverified; the analysis reliably concludes whatever it started believing.
- **5–6**: Constraint taxonomy applied with evidence on major items; fence archaeology practiced; component decomposition on load-bearing numbers; conventional baseline compared.
- **7–8**: Full checklist: question-behind-the-question, ≥2 rebuilds with reality re-imported, honest convergent comparison, constraint map recorded with dates and owners.
- **9–10**: Additionally: selectivity visibly practiced (the method aimed only where it pays); fences upgraded not just kept/removed; assumption sweeps institutionalized; the constraint map demonstrably retired folklore — and at least once, the analysis validated the convention and the team banked that as the win it is.
