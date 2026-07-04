---
name: decomposing-ambiguity
description: "Use when the request is a feeling not a spec ('app is slow,' 'make onboarding better,' 'add AI'), two people are solving different problems with the same words, or a task resists estimation — restate, surface assumptions, split."
---

# Decomposing Ambiguous Problems

## Purpose

Turn fog into a workable problem: restate what's actually being asked, surface the hidden assumptions, split the unknown into independently attackable pieces, and know which piece to attack first — before any solution vocabulary contaminates the framing.

## When to use

- The request is a feeling, not a spec ("the app is slow," "make onboarding better," "we need AI in the product").
- Two smart people in the room are confidently solving different problems with the same words.
- A task has resisted estimation twice — un-estimatable usually means un-decomposed.
- You're about to plan or build and can't state the acceptance criteria in one sentence.
- A stakeholder asks for a solution ("add a caching layer") and the problem behind it is unstated.

## Goals

- The problem restated in outcome terms, confirmed by the person who asked — "yes, that's what I mean" said out loud.
- Assumptions surfaced and tagged: verified / cheap-to-check / must-carry-as-risk.
- The fog cut into pieces where each piece has a knowable answer and an owner, and the dependencies between pieces are explicit.
- The riskiest-or-cheapest-to-resolve piece identified as the first move (not the easiest or most fun one).
- A visible record of what was deliberately left out of scope.

## Expert Mental Model

- **Requests arrive as solutions; problems must be excavated.** "Add a caching layer" means "something is slow and I once saw caching fix slowness." The expert's first move is always the restatement: "what would be different for you if this worked?" — answered in observable outcomes, not features (see product-thinking job-behind-the-request; first-principles question-behind-the-question). Most ambiguity dissolves at this step, before any decomposition machinery runs.
- **Ambiguity has two species and they need different treatment.** *Epistemic* ambiguity — facts nobody in the room knows but somebody could (what's the actual p99? which browsers matter? what does the contract say?) — is resolved by *going and looking* (see research primary sources). *Essential* ambiguity — genuinely undecided things (what should happen when two editors conflict?) — is resolved by *someone deciding*, and the skill is routing it to the person with authority to decide rather than guessing on their behalf. Novices treat both as discussion topics; discussions resolve neither.
- **A good decomposition cuts along seams of independence, not along the org chart or the noun list.** The test of a cut: can this piece be answered/built/validated without holding the other pieces in your head? Cuts that leave every piece entangled with every other piece ("frontend part, backend part" of a fundamentally unclear feature) are re-labelings, not decompositions (see system-design service boundaries — same seam-finding instinct at a different altitude).
- **Hidden assumptions live in the words everyone thinks are obvious.** "User," "done," "fast," "real-time," "secure," "migrated" — each is a bag of unexamined decisions. The expert move is to force quantification and instantiation: "fast" becomes a number with a percentile; "user" becomes three named personas or one; "done" becomes a checklist (see planning-and-estimation definition-of-done). The clarifying questions worth asking are the ones whose answers *change what you'd build* — question count is not the metric; decision-changing answers are.
- **Ask questions in batches, hypothesis-first.** Twenty questions delivered serially is an interrogation and makes stakeholders stop answering. The expert states a strawman ("here's what I think you mean — X for Y users, measured by Z; what's wrong with it?") because people correct a wrong concrete far better than they specify a blank (see elaborating specs generally; forms — same principle as good defaults). Wrong-on-purpose beats blank.
- **The first piece to attack is chosen by risk economics, not comfort.** Resolve first whichever unknown is (a) most likely to invalidate everything else, or (b) nearly free to check. Everything else waits. Teams that start with the comfortable piece build three weeks of scaffolding around an unexamined assumption that dies on contact (see convergent-evaluation information-buying; planning-and-estimation walking skeleton).

## Workflow

1. **Capture the request verbatim**, then restate it as an outcome with no solution words: who changes what behavior, observable how. Read it back; get explicit confirmation or a correction (both are wins).
2. **Ask "how will we know it worked?"** — extract a measurable or at least observable success signal now, while it's cheap (see evals for the AI-flavored version; product-thinking metrics).
3. **List the load-bearing words** in the restatement ("user," "fast," "sync," "migrate") and instantiate each: numbers, named cases, percentiles, concrete examples. Every word that survives uninstantiated is an assumption in hiding.
4. **Write the assumption ledger**: everything being taken as true, each tagged epistemic (go look — assign who/where) or essential (needs a decision — assign whom), plus verified/cheap-to-check/carry-as-risk.
5. **Cut the problem along independence seams**: pieces answerable/buildable separately, each with a one-sentence "resolved when…" Note dependencies between pieces explicitly (an arrow list, not a mural).
6. **Scope explicitly**: write the not-doing list with the same care as the doing list — deferred pieces with the reason, so scope creep has to argue with a document instead of a memory (see change-request thinking).
7. **Pick the first piece by risk economics**: highest invalidation-power or lowest check-cost. Say why out loud — "we're checking X first because if it's false, nothing else matters."
8. **Timebox the resolution of that piece** and set the tripwire: what answer, by when, or the question escalates (see research timeboxes — same discipline).
9. **Re-decompose after each resolved piece** — answers change the map; the decomposition is a living document for exactly as long as the problem is alive.

## Decision Tree

- If the request names a solution → excavate: "what problem does that solve for you?" Restate as outcome; only then evaluate the proposed solution as one candidate among others.
- If two stakeholders confirm different restatements → stop decomposing; you have two problems (or a values conflict). Surface it to whoever owns the tradeoff (see technical-leadership stakeholders) — building the average of two problems satisfies neither.
- If a piece is epistemic → nobody discusses it; someone *looks it up*, with a name and a deadline.
- If a piece is essential → route to the decision-owner with a recommendation attached (see technical-writing decision docs); if you can't find an owner, the ambiguity is organizational, and that's the finding.
- If the problem resists cutting (every piece touches every piece) →
  - Try a different axis: by user journey stage, by data lifecycle, by failure mode, by "what must be true" chains — the noun-based cut is usually the one that fails.
  - Still entangled → build the thinnest end-to-end slice instead (see planning-and-estimation walking skeleton); vertical slices decompose what horizontal analysis can't.
- If you cannot state how you'd know it worked → you don't have a problem yet, you have a mood; return to step 2 and don't build.
- If the asker can't answer the clarifying questions → find the person the asker is proxying for (requests are often second-hand); interview the source (see product-thinking user interviews).
- If every question is answered "use your judgment" → take it literally: write your judgments down as the assumption ledger, ship the ledger for objections with a deadline, then proceed. Silence after a visible ledger is consent; silence around an invisible one is a trap.
- If the ambiguity is genuinely irreducible before building (taste, market response) → stop analyzing; convert to an experiment with a kill criterion (see evals; product-thinking experimentation).

## Heuristics

- The question behind "can we just…?" is never about capability — answer the unstated cost/risk question instead.
- If you can't write the acceptance test, you can't write the code — the test-first instinct applies to problem statements before it applies to functions (see legacy-migrations characterization: same move against a different fog).
- Three concrete examples beat any abstract definition: "walk me through the last time this happened" extracts more spec than an hour of "what should it do."
- Count decision-changing answers, not questions asked: if an answer wouldn't change what you build, don't ask it (yet).
- The words "obviously," "just," "simply," and "everyone knows" mark burial sites of assumptions — dig there first.
- A piece that has been "almost resolved" for two weeks is essential ambiguity wearing an epistemic costume: someone doesn't want to decide. Name the decision and its owner.
- Strawman early, in writing, with numbers: "assume 10k users, p95 < 200ms, English-only for v1 — object by Thursday" resolves more per hour than any meeting.
- Deferred ≠ rejected: the not-doing list with reasons is what makes deferral stick (and what makes revisiting cheap).
- When estimation keeps failing, decompose further — pieces that can't be estimated to within 3× are still fog (see planning-and-estimation reference-class).
- Say the scary restatement out loud: "so if I understand, we'd be dropping X to get Y" — the flinch (or its absence) is data no document contains.

## Quality Checklist

- [ ] Restatement in outcome terms, solution-vocabulary-free, explicitly confirmed by the asker.
- [ ] Success signal defined and observable before any building started.
- [ ] Load-bearing words instantiated (numbers, percentiles, named cases) — no "fast/secure/done" left abstract.
- [ ] Assumption ledger written: each item tagged epistemic/essential, with owner and check-cost.
- [ ] Decomposition cuts along independence seams; each piece has a "resolved when…"; dependencies explicit.
- [ ] Not-doing list written with reasons.
- [ ] First piece chosen by invalidation-power or check-cost, and the choice justified in a sentence.
- [ ] Essential ambiguities routed to named decision-owners with recommendations, not left as discussion topics.
- [ ] Decomposition revisited after resolutions — the map matches the current territory.

## Failure Modes

- **Solving the stated solution**: six weeks building the requested caching layer; the slowness was an N+1 query (see postgres; root-cause-analysis) — nobody restated the problem, so nobody looked.
- **Clarification theater**: twenty questions asked, none decision-changing; stakeholder patience spent, fog intact — questions as procrastination-with-props.
- **Analysis as a residence**: the decomposition polished for weeks while the cheap-to-check assumption sat uncheckd; experts *resolve* pieces, they don't landscape them (see convergent-evaluation: analysis has a budget).
- **Guessing on essential ambiguity**: the conflict-resolution behavior nobody decided, decided silently by an engineer at 6pm, discovered by users — essential ambiguity needs an owner's decision, not a quiet default (or at minimum a *loud* default in the ledger).
- **Noun-list decomposition**: "the database part, the API part, the UI part" of a problem whose actual unknowns run through all three — re-labeling that leaves every risk uncut (see planning-and-estimation: horizontal slicing).
- **The average of two problems**: two stakeholders' incompatible restatements quietly merged into one blurred spec; the shipped thing is precisely nobody's need — conflicts must surface, not blend.
- **Scope by accretion**: no not-doing list, so every conversation adds a piece; the problem grows faster than pieces resolve.
- **Comfort-first sequencing**: starting with the well-understood piece because progress feels good; the invalidating unknown detonates in week four with maximal sunk cost.

## Edge Cases

- **The proxy requester**: the PM relaying "sales needs X" can't answer instantiation questions — interview the source; second-hand ambiguity compounds per hop.
- **Ambiguity as policy**: sometimes vagueness is deliberate (political cover, unresolved leadership conflict) — recognizing "this is vague because deciding is expensive for someone" changes your move from clarifying to escalating (see technical-leadership disagree-and-commit).
- **The problem that dissolves**: restatement occasionally reveals no problem ("we need this report" → nobody reads it) — deletion is a valid, high-value resolution (see first-principles: the problem that dissolves).
- **Emergencies**: during an incident, decomposition compresses to minutes — restate ("what's actually broken for users?"), one assumption check, act (see production-debugging: stabilize before diagnose). The skill survives compression; the ceremony doesn't.
- **Research-shaped problems**: when the unknown is "is this possible at all," decomposition yields spikes with kill criteria, not tasks with estimates (see research; planning-and-estimation when-not-to-plan).
- **Cross-team seams**: a piece whose resolution lives in another team's backlog is a dependency risk, not a task — track it as such, with the escalation path pre-agreed (see planning-and-estimation integration costs).
- **The confidently wrong instantiation**: stakeholders will confirm a restatement that's subtly wrong to end the meeting — confirm with an example, not a nod ("so concretely: Maria uploads a 40MB file on hotel wifi, and she should see…?").
- **Legacy fog**: "make it work like the old system" where nobody fully knows what the old system does — the decomposition routes through characterization (see legacy-migrations characterization) before through anyone's memory.

## Tradeoffs

- **Clarifying vs momentum**: every question costs stakeholder patience and calendar time; every unasked decision-changing question costs rework. Spend questions where answers change the build; spend strawmen everywhere else.
- **Restating vs presuming rapport**: forced restatement can read as pedantic when trust is high and the domain is shared — calibrate ceremony to stakes and to how often this pair of people has been burned before.
- **Decomposition granularity vs coordination overhead**: finer pieces are easier to attack and estimate but multiply hand-offs and status surface (see planning-and-estimation: the coordination tax) — cut until pieces are attackable, then stop.
- **Deciding-by-default vs blocking on owners**: a loud documented default keeps motion but occasionally ships a wrong guess; blocking on the owner is safe but converts their calendar into your critical path. Route by reversibility (see convergent-evaluation door-classification).
- **Scope discipline vs responsiveness**: the not-doing list protects focus but can ossify — pair it with an explicit revisit trigger, not a "never."
- **Speed vs correctness of the framing itself**: an 80% right framing now usually beats a 98% framing in two weeks — except on one-way doors, where framing errors are the most expensive errors there are (see judgment-under-uncertainty).

## Optimization Strategies

- Template the ledger: a standing four-column doc (assumption / tag / owner / status) per project — the artifact reusable across every ambiguous request, and the anti-relitigation record later (see technical-writing decision docs).
- Practice the restatement reflex until it's sub-verbal: every incoming request, restate before responding, even trivially — reps on cheap cases build the muscle for expensive ones.
- Maintain a domain phrasebook: the load-bearing words of *your* product ("account," "active," "sync") pre-instantiated once, so each new problem doesn't re-litigate the vocabulary (see model-domain thinking; define-language work).
- Run pre-mortems on the framing, not just the plan: "it's six months later and we solved the wrong problem — what was it?" (see convergent-evaluation pre-mortems) — framing failures are cheaper to catch as fiction.
- Score your own history: for the last three projects, which assumption killed or bent the schedule? The pattern (usually: an essential ambiguity everyone treated as epistemic) tells you where your ledger discipline leaks.
- Pair with planning explicitly: this skill ends where the pieces are known; planning-and-estimation sequences and prices them; the hand-off artifact is the decomposition with dependencies — keep them one document.

## Self Review

- Can I state the problem in one sentence with no solution words — and did the asker confirm *that sentence*, not a vibe?
- Which words in my framing are still abstract? What number, percentile, or named example is each hiding?
- What am I assuming that a 30-minute check would verify — and why haven't I checked it?
- Which ambiguity am I treating as "needs discussion" that is actually "needs an owner to decide"?
- If my first piece resolves against me, what survives? (If the answer is "everything," I chose a comfortable piece, not a risky one.)
- What did I put on the not-doing list — and if it's empty, is the scope actually total, or is the list dishonest?
- Whose problem is this second-hand? Have I talked to the source?
- Would two readers of my decomposition build compatible things?

## Examples

**1. "The app is slow" excavated.**
Request arrives as "we need a performance sprint." Restatement pass: slow *where, for whom, doing what?* — the asker (support lead) is proxying three customer complaints. Interviews with the sources: all three are the invoice-list screen, all three are agencies with 10k+ invoices. Load-bearing word "slow" instantiated: 12–18s render. Ledger: "it's the backend" tagged epistemic → one look at traces (see observability) shows 200ms API, 11s client render. Decomposition by journey stage kills the planned "performance sprint" (backend-shaped, three weeks) in favor of one piece: virtualize the table (see data-tables; frontend-performance). Two days. The sprint would have optimized the fast part.

**2. Essential ambiguity routed, not guessed.**
Spec for collaborative editing says "handle conflicts gracefully." Instantiation forces the question: last-write-wins, merge, or block? This is essential, not epistemic — no amount of research answers it; it's a product-values decision (data-loss risk vs complexity vs UX friction). Ledger routes it to the product owner with a recommendation ("LWW with visible edit-history for v1; merge is a quarter of work — see async-processing for why") and a deadline. Owner picks LWW knowingly. When a customer later complains, the decision doc answers in one link — the engineer who would have guessed silently is not holding the bag.

**3. The un-estimatable task decomposed by "what must be true."**
"Migrate search to the new engine" has failed estimation twice (answers ranged 3 weeks–2 quarters — the 3× tripwire). Noun-cut ("indexer, query layer, UI") leaves every risk entangled. Re-cut along "what must be true": (a) new engine handles our query patterns — *cheap to check, high invalidation power*: two-day spike replaying the top-100 production queries (see research spikes); (b) reindex fits the maintenance window — *arithmetic, one hour*; (c) relevance parity — *needs a golden set* (see evals). Spike (a) fails on one query family; the project reshapes around fixing that first. Three weeks of scaffolding never gets built on the dead assumption.

**4. Wrong-on-purpose strawman.**
"We need AI in the product" from leadership. Rather than a questions barrage: a one-page strawman — "concretely: auto-draft replies in the support inbox, for the 40% of tickets matching known intents, measured by draft-acceptance rate ≥50% (see ai-product-ux); explicitly NOT a chatbot, NOT search. Object by Friday." Leadership's corrections ("actually the pain is triage, not drafting") land in 48 hours and are decision-grade. The blank-page version of this conversation historically took six weeks of workshops.

## Evaluation Rubric

Score 1–10:

- **1–2**: Built the stated solution; no restatement, no ledger; "fast/done/user" never instantiated; first piece chosen by comfort.
- **3–4**: Some clarifying questions, mostly non-decision-changing; assumptions surfaced but untagged and unowned; decomposition is a noun re-labeling.
- **5–6**: Confirmed outcome restatement; key words instantiated; ledger exists with epistemic/essential tags; pieces mostly independent; first piece defensibly chosen.
- **7–8**: Full checklist: strawman-driven clarification, not-doing list, dependencies explicit, essential ambiguities routed to owners with recommendations, decomposition maintained as answers land.
- **9–10**: Additionally: framing pre-mortem run; second-hand requests traced to sources; at least one problem dissolved or converted to a cheap experiment instead of built; the ledger later *demonstrably* prevented rework or relitigation.
