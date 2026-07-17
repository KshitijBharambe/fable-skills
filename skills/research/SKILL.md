---
name: research
description: "Use when evaluating a framework/library/vendor before committing, answering 'does X support Y / how do others solve Z / is this possible,' checking prior art before building novel, or running a timeboxed spike."
---

# Technical Research

## Purpose

Investigate unfamiliar territory efficiently and come back with decision-grade answers: route every question to its cheapest reliable source, rank sources by how close they are to ground truth (primary beats secondary beats vibes), timebox the search, verify by running rather than reading — and deliver findings with confidence levels and receipts instead of a link pile.

## When to use

- Evaluating a framework, library, vendor, or approach before committing to it.
- A question can't be answered from the team's existing knowledge: "does X support Y?", "how do others solve Z?", "is this even possible?"
- Before building anything novel — the prior-art check that prevents reinventing (or re-failing) someone else's wheel.
- A spike: fog too thick to plan through, needing a timeboxed investigation with a kill criterion (see planning-and-estimation when-not-to-plan).
- When research has become the procrastination: three days of reading and no decision moved.

## Goals

- The question stated decision-first: what decision does this research feed, and what answer-shape would move it (see decomposing-ambiguity).
- Sources ranked and used by proximity to ground truth; every load-bearing claim traced to a primary source or a run experiment.
- Claims date-stamped and version-stamped — the answer that was true for v2 in 2023 is labeled as such.
- Timeboxes honored: research ends when the decision can be made, not when curiosity is satisfied.
- Findings delivered as a synthesis with confidence levels and receipts (see technical-writing) — reusable by the next person with the same question.

## Expert Mental Model

- **Research serves a decision; everything else is reading.** The expert starts from "what are we deciding, and what evidence would change the choice?" — which immediately prices the research (a two-way-door library pick earns an hour; a platform commitment earns a week — see judgment-under-uncertainty doors; brainstorming information-buying). Without the decision anchor, research becomes its own habitat: interesting, endless, and unaccountable. The test at any moment: "if I had to decide right now, what would I say, and what specifically am I still looking for?" — no answer to the second half means you're done and avoiding it.
- **The source hierarchy is the discipline.** Ground truth descending: (1) *running the thing yourself* — behavior observed beats behavior described, always; (2) *primary sources* — the source code, the official docs for your exact version, the spec/RFC, the changelog, the issue tracker (where the docs' claims go to be falsified); (3) *informed secondary* — maintainer talks, engineering-blog postmortems from teams running it in production at scale; (4) *uninformed secondary* — tutorials, SEO-farmed listicles, quora-shaped answers, and most "X vs Y in 2024" posts (written to rank, not to inform); (5) *training-data recall and vibes* — including an LLM's confident summary, which is a hypothesis-generator to verify against layers 1–2, never a source (see the AI edge case). Novices read layer 4 because it's easiest; experts skip to 1–2 because verification later costs more than rigor now.
- **The issue tracker and the changelog are where the truth lives.** Docs describe intent; the issue tracker describes reality — the open bug on exactly your use case, the "wontfix" on the feature the landing page implies, the maintainer's tone under pressure, the three-year-old PR that would have fixed your problem. The changelog and release cadence tell you the project's pulse (last release 14 months ago is a datum no benchmark captures). Ten minutes in issues-sorted-by-thumbs-up teaches more about a dependency's sharp edges than an hour of its documentation (see abstraction-and-simplicity: the dependency interview — this is its evidence-gathering arm).
- **Run it before you believe it.** The spike — a small, disposable, timeboxed experiment against *your* real constraints (your data shapes, your query patterns, your auth model) — outranks every document, because docs describe the general case and you are hiring for the specific one (see planning-and-estimation: spikes with kill criteria). The discipline that keeps spikes honest: written kill criterion before starting ("dead if it can't do X under Y"), production-shaped inputs (the 200-row toy dataset verifies nothing — see optimization-method: representative data), and *disposability* — spike code is evidence, not a foundation; promoting it to production without the real engineering pass is how research debt becomes architecture (see the failure modes).
- **Claims have versions and expiry dates.** The blog post is about v2; you'd adopt v5. The benchmark predates the rewrite. The limitation that shaped a whole comparison was fixed eight months ago — or the feature you're counting on was deprecated. Every claim collected gets stamped (version, date, source) and the stale ones get re-verified against layer 1–2 before they bear load (see first-principles: date-stamp every "impossible"; judgment-under-uncertainty: decisions inherit their assumptions' shelf lives). Fast-moving domains — and AI tooling is the current extreme — compress expiry to months.
- **Synthesis is the deliverable; a link pile is homework you're forwarding.** Research ends in a document (see technical-writing): the question, the answer with a confidence level, the evidence with receipts, what would change the conclusion, and what was deliberately not investigated. This is what makes research compound — the next engineer with the question gets an answer in one link instead of re-running the search (see brainstorming receipts; the decision-doc machinery, upstream). It's also what keeps the researcher honest: conclusions that must be written with confidence levels get noticeably more careful than conclusions delivered as hallway vibes.

## Workflow

1. **Anchor the decision**: what choice does this feed, who makes it, by when, and what answer-shape moves it ("we need: can it do X, at Y scale, under Z license — not: everything about it").
2. **Set the timebox and the depth** by door-type (see judgment-under-uncertainty): hours for reversible picks, days for platform commitments — written down, with a check-in at the halfway mark ("am I converging or wandering?").
3. **Write down what you already believe** (the priors, honestly — including the option you're secretly rooting for; see brainstorming: name the bias before it names your criteria) and what would falsify each belief.
4. **Do the survey pass at layer 2–3** (an hour, breadth-first): official docs' architecture page, the changelog/release cadence, issues-by-reaction, one or two production postmortems. Goal: the landscape, the vocabulary, and the shortlist of load-bearing claims to verify.
5. **Interrogate the load-bearing claims at layer 1–2**: for each claim the decision rests on, find the primary source (exact-version docs, the code itself, the maintainer's statement) or mark it "needs experiment."
6. **Spike what documents can't settle** (see the mental model): kill criterion first, production-shaped inputs, timeboxed, disposable. One spike per genuinely-uncertain claim, not one mega-spike for everything.
7. **Seek the disconfirming evidence deliberately**: search "<candidate> problems", "migrating away from <candidate>", the issue tracker's angriest threads — the failure stories are where the marketing isn't (see brainstorming: pre-mortems, outsourced to people who already lived them).
8. **Stamp everything**: version, date, source proximity — and prune the claims that turn out to be about a different version of reality.
9. **Synthesize**: the question, the answer, confidence level, receipts, the disconfirming evidence honestly weighed, what would reopen the conclusion, and what was out of scope — one document, findable (see technical-writing; the anti-relitigation payload).
10. **Stop at decision-grade**: when the decision-maker can decide, research is done — remaining curiosity goes in the ledger, not the calendar.

## Decision Tree

- If the question is "does X support Y?" → exact-version docs, then the issue tracker (the docs say yes; the issues say "yes, except" — you need the except), then a 30-minute spike if it's load-bearing.
- If the question is "how do others solve Z?" → production engineering blogs and postmortems (layer 3, but written by people with pagers), then the primary sources they cite; conference talks by practitioners beat tutorials by content farms.
- If the question is "X vs Y" → refuse the comparison-post shortcut: derive *your* criteria first (see brainstorming: criteria before options), then research each candidate against them at layer 1–2 — comparison posts hand you someone else's criteria wearing your decision's clothes.
- If the question is "is this possible at all?" → spike immediately; possibility questions are the worst fit for reading (docs describe the intended, not the boundary) and the best fit for a two-day experiment with a kill criterion.
- If sources conflict → check versions and dates first (most conflicts are two eras disagreeing), then proximity (the maintainer's issue comment beats the tutorial), then run it (the tiebreaker that never lies).
- If you can't find anyone who's done it → that's a finding, and it's ominous: either you've misdescribed the problem (rephrase and re-search — the right vocabulary unlocks the literature; see the survey pass), or the approach has a known-to-others flaw, or you're genuinely first (rare; price the pioneer tax honestly — see judgment-under-uncertainty: Knightian territory, smaller bets).
- If the research keeps expanding ("but first I should understand…") → check the decision anchor: does the decision *need* this layer? Usually the expanding frontier is curiosity wearing diligence's badge — ledger it and return to the question.
- If the timebox expires without convergence → that *is* the answer for now: report the state honestly ("can't confirm X within the box; options: extend with narrowed scope, spike it, or decide under stated uncertainty" — see judgment-under-uncertainty: consequence-framed doubt), and let the decision-owner price the extension.
- If you're researching to avoid deciding → (the tell: the decision hasn't moved in two sessions of "learning more") — write the decision memo with today's evidence and confidence levels; the gaps that actually matter will announce themselves in the writing (see technical-writing: writing as the test).

## Heuristics

- One hour of running beats one day of reading, for any claim you can run.
- Read the docs for what it does; read the issues for what it doesn't; read the changelog for where it's going; read the license and pricing page *first* if any of them could be fatal (the disqualifier check costs five minutes and voids whole afternoons).
- Search the failure phrases early: "migrating away from", "lessons learned", "post-mortem", "<thing> at scale problems" — pain writes more honestly than enthusiasm.
- The maintainer's reply-tone in contentious issues is due diligence: you're evaluating a future support relationship, not just code (see abstraction-and-simplicity: a dependency is a hiring decision).
- Note the date of everything you read before you read it — a 2021 take on a fast-moving tool is history, not guidance; in AI tooling, six months is a generation.
- Prefer sources with skin in the game: the team that runs it in production and says so beats the reviewer who benchmarked it for a weekend.
- Three sources agreeing means little if they share an upstream (the same original blog post, laundered through aggregators — see judgment-under-uncertainty: correlated evidence is one source with extra steps); trace the citation chain before counting heads.
- Vocabulary is half the search: five minutes finding the field's term of art ("what you call 'retry dedup' the literature calls 'idempotency'") multiplies every subsequent query (see domain-modeling).
- Keep a running log while researching — claims, sources, dead ends — the synthesis writes itself from the log, and the dead ends are findings too ("evaluated and rejected X because…" saves the next person the same detour).
- When an LLM answers your research question: treat it as a well-read colleague's recollection — fast, plausible, occasionally confabulated, never a citation; extract the claims and verify the load-bearing ones at layer 1–2 (it excels at *generating* the vocabulary and the checklist you then verify).
- Budget disqualification-first: check the fatal criteria (license, pricing model, platform support, data residency) before the interesting ones — most candidates die cheap if you let them.

## Quality Checklist

- [ ] Decision, decision-maker, and answer-shape named before searching.
- [ ] Timebox set by door-type; halfway check-in honored.
- [ ] Priors and the secretly-favored option written down first.
- [ ] Load-bearing claims verified at layer 1–2 (primary source or run experiment); source proximity noted per claim.
- [ ] Disqualifiers (license, pricing, platform) checked before deep investment.
- [ ] Disconfirming evidence deliberately sought, not just encountered.
- [ ] Spikes: kill criterion written first, production-shaped inputs, disposable code.
- [ ] Every claim version- and date-stamped; stale ones re-verified or pruned.
- [ ] Synthesis shipped: answer, confidence, receipts, what-would-reopen, out-of-scope — findable by the next asker.
- [ ] Research stopped at decision-grade; leftover curiosity ledgered.

## Failure Modes

- **The link pile**: forty tabs, no synthesis — research as collection, forwarded to the decision-maker as homework; the reading happened, the thinking didn't.
- **Tutorial-layer confidence**: the evaluation built entirely on layer-4 sources — the "X vs Y" post from a content farm, the tutorial that never left the happy path; the decision inherits the SEO author's ignorance at production scale.
- **The unfalsifiable spike**: no kill criterion, toy data, and a demo that "basically works" — the spike confirms whatever hope built it; the production attempt discovers what the 200-row dataset couldn't (see optimization-method: benchmark theater, research edition).
- **Version blindness**: the dealbreaker limitation from a 2022 post drives the rejection — fixed in the release you'd actually use; or its mirror: the counted-on feature, deprecated last quarter. Unstamped claims, silently expired.
- **Confirmation shopping**: the secretly-favored option researched for support, the rivals researched for flaws — search queries themselves biased ("why X is great" vs "Y problems"); the priors never written down, so the tilt was invisible even to the researcher (see brainstorming: post-hoc criteria).
- **Spike-to-production laundering**: the disposable experiment, demo'd once, becomes the foundation — no error handling, no tests, hardcoded everything, now load-bearing (see refactoring: it will be characterized someday, expensively).
- **Research as procrastination**: the decision is scary, so the investigation grows another week — depth as anxiety management; the tell is that new findings stopped changing the answer sessions ago (see brainstorming: analysis has a budget; judgment-under-uncertainty: soothing vs deciding).
- **The unrecorded expedition**: solid research, synthesized nowhere — six months later the same question re-run from scratch by the next engineer, including the same dead ends; the org pays for the same map twice (see technical-writing: the twice-asked question).

## Edge Cases

- **Researching under NDA/procurement constraints**: vendor claims can't be spike-verified without contracts — push for the proof-of-concept clause, reference calls with *current* customers running your use case (ask about the failure modes, not the satisfaction), and weight the escape terms as heavily as the features (see abstraction-and-simplicity: exit cost is the interview's sharpest question).
- **Fast-moving domains**: when the landscape shifts monthly (AI tooling now), lengthen nothing — shorten: smaller commitments, thinner adapters (see abstraction-and-simplicity), re-verification triggers on the claims ("re-check when v6 ships"), and a bias toward reversible picks *because* the research expires (see judgment-under-uncertainty: expiring decisions).
- **Researching people-questions**: "how do teams structure on-call?" has no primary source to run — proximity translates to: practitioners who've done it (interviews, engineering blogs with numbers) over consultants who advise it over surveys that aggregate it; and every answer is context-laden (their scale, their org) — port the *conditions*, not just the conclusion (see first-principles: best practices are average practices).
- **Academic-literature crossings**: when the trail leads to papers — read abstract → figures → conclusion → (only if load-bearing) methods; check citation counts and *who* cites it (follow-ups confirming or refuting?); a single unreplicated paper is a hypothesis, not a foundation (see the correlated-sources heuristic, formalized).
- **Security-sensitive research**: evaluating auth libraries, crypto, anything with CVE surface — the issue tracker's *security advisories* and the project's disclosure history become primary criteria; "no reported CVEs" in an unaudited project means unexamined, not safe (see security: boring adopted standards; security: the interview).
- **When the answer is "it depends" all the way down**: some questions genuinely resolve only at your scale/data/team ("will this index strategy work?" — see postgres) — the honest output is a decision tree plus the experiment that would settle it locally, not a false general answer.
- **Inherited research**: a predecessor's evaluation doc drives a standing decision — before extending it, re-verify its load-bearing stamps (versions moved, prices changed); inherited conclusions age exactly like your own, minus your memory of their assumptions (see refactoring: archaeology; judgment-under-uncertainty: assumption shelf lives).
- **The vocabulary desert**: genuinely novel intersections where no term of art exists — search the *components* of your problem separately, find the adjacent fields (your "sync conflict UX" is databases' "CRDT" plus design's "error recovery" — see brainstorming: analogy transfer), and expect the literature to be assembled, not found.

## Tradeoffs

- **Depth vs decision tempo**: every layer deeper costs calendar against a decision that may not need it — the door-type sets the budget, and the halfway check-in enforces it; under-research one-way doors and you ship regret, over-research two-way doors and you ship late (see judgment-under-uncertainty, the same dial).
- **Primary-source rigor vs practical speed**: reading the source code settles claims and costs hours; the tutorial answers in minutes and is sometimes right — route by load-bearingness: the claim the decision rests on gets layer 1–2; the peripheral ones can ride layer 3 with a stamp.
- **Breadth vs depth in the survey**: shortlist too early and the best candidate never got seen; survey too long and no candidate gets verified — the standard shape is one breadth hour to a shortlist of 2–3, then depth only on those (see brainstorming: the funnel).
- **Spiking vs reading**: experiments answer *your* question and cost setup; documents answer the *general* question and cost trust — spike the claims that are both load-bearing and context-dependent (performance on your data, fit with your auth); read everything else.
- **Freshness vs stability of sources**: the newest take knows the current version but hasn't been tested by time; the classic postmortem is battle-proven but describes an old world — hold both, stamped, and let the version-check arbitrate what still applies.
- **Reusable synthesis vs research velocity**: writing the findings doc costs an hour the decision doesn't strictly need — it pays the *next* asker and disciplines the current conclusion; skip it only for research too trivial to ever recur (and notice how rarely that's true — see technical-writing: the three documents that prevent forty meetings).

## Optimization Strategies

- Build the team's research commons: evaluations, spikes, and rejections in one findable place, each with stamps and reopen-triggers (see technical-writing: the decision log's sibling) — the second evaluation of anything should start from the first.
- Template the evaluation: your standing criteria (license, maintenance health, security posture, exit cost, fit-with-stack) pre-listed so each new candidate research starts at the interrogation instead of inventing the questions (see abstraction-and-simplicity: the dependency interview, institutionalized).
- Keep spike infrastructure warm: a scratch repo/environment with production-shaped sample data, ready for the 30-minute experiment — when spiking costs setup, teams read instead, and reading is where the errors hide (see planning-and-estimation: skeleton economics).
- Practice the source-proximity reflex on small questions: even for "how does this API paginate?", the habit of exact-version-docs-then-issues over blog-post-first compounds into calibrated instincts about where truth lives per domain.
- Calibrate your research like your estimates (see judgment-under-uncertainty: the scoreboard): when a researched decision later surprises you, trace which claim failed and at what source-layer it was verified — layer-4 failures teach the hierarchy viscerally.
- Pair research on the big ones: two researchers with written priors, splitting candidates adversarially ("you build the case against X, I'll build it against Y") — structured disconfirmation that no solo researcher's discipline fully replaces (see brainstorming: the bought dissent).

## Self Review

- What decision is this research feeding — and has my last hour of reading moved it?
- Which claims is the conclusion actually resting on — and at what source-layer did I verify each?
- What version and date is each load-bearing claim about — and is that the version we'd use?
- Did I search for the failure stories, or only the success stories? What did the angriest issue thread say?
- What was I secretly rooting for — and would a reader of my search queries be able to tell?
- What did I run, versus read about? Which readable claim deserves a 30-minute spike before it bears weight?
- If the timebox ended now, what would I say, at what confidence — and why am I not saying it?
- Where will the next person with this question find my answer?

## Examples

**1. The queue evaluation that read the issues first.**
Choosing a message queue for webhook delivery (see async-processing): the comparison posts crown the fashionable candidate. Decision-anchored criteria first (at-least-once delivery, per-tenant ordering, ops burden a two-person team can carry — see brainstorming), then layer 1–2 per candidate. The fashionable one's *docs* promise per-key ordering; its *issue tracker* has a 3-year thread — 200 thumbs — documenting ordering violations during rebalances, "wontfix by design," with the maintainer explaining why. That single thread (ten minutes) reverses the reading-layer conclusion. The boring alternative wins on the criteria; the synthesis records both, with the thread linked as the receipt. Six months later a new hire asks "why didn't we use X?" — one link (see technical-writing: relitigation, killed).

**2. The spike with a kill criterion, killing.**
"Can we do semantic search over our contracts corpus with the vendor's embedding API?" (see rag). Instead of two weeks of reading: a three-day spike, kill criterion written first — "dead if precision@10 < 0.7 on the 50-query golden set (see evals), or unit economics > $0.002/query at production volume." Production-shaped data: real contracts (with their OCR noise), real user queries from search logs — not the vendor's demo corpus. Day two: precision fine on clean documents, collapses on the OCR-noisy 30% — a finding no document could have surfaced, because no document knows your corpus is 30% scanned faxes from 2009. The spike dies on its criterion; the *research* succeeds — the synthesis reroutes the project to an OCR-cleanup phase first, and the disposable spike code is deleted with ceremony (see the laundering failure mode, avoided).

**3. Version blindness, caught by stamping.**
An architect rejects a database extension based on a well-written 2022 postmortem ("no transactional guarantees across X — bit us badly"). The stamping discipline flags it: post is about v1.4; the current release is v3.1. Changelog check (layer 2): the transactional gap closed in v2.0 — with the postmortem's *author* commenting approvingly in the release thread (proximity bonus: the burned party, satisfied). Re-verified with a one-hour spike against v3.1: holds. The near-miss becomes the team lesson: every claim wears a version tag, and rejections especially — because a stale rejection silently costs you the best option without ever being wrong out loud (see first-principles: date-stamped impossibles; judgment-under-uncertainty: expired assumptions).

**4. Research as procrastination, named and exited.**
Week three of "evaluating" workflow orchestrators; the doc of notes is now 11 pages and the decision hasn't moved since week one (the tell). The exit protocol: write the decision memo *today* with current evidence — and the writing surfaces the truth in an hour: two candidates both clear every load-bearing criterion; the remaining "research" was seeking a tiebreaker that doesn't exist because the options are genuinely equivalent for this use case (see brainstorming: when scores tie, the decision is cheap, not hard). The memo picks the one matching the team's existing operational skills (see system-design boring-tech), records the reopen-trigger, and ships. Two-way door, walked through; the eight remaining browser tabs, closed unread — correctly.

## Evaluation Rubric

Score 1–10:

- **1–2**: Tutorial-layer conclusions; no decision anchor; unstamped claims; the favored option researched for confirmation; findings live in browser tabs and vibes.
- **3–4**: Some primary-source use but unranked; timeboxes absent (research ends by exhaustion); spikes without kill criteria on toy data; synthesis skipped or a link pile.
- **5–6**: Decision-anchored questions; source hierarchy applied to load-bearing claims; disqualifiers checked early; claims stamped; a findable synthesis with receipts.
- **7–8**: Full checklist: priors written first, disconfirming evidence hunted, spikes disciplined and disposable, timeboxes with halfway check-ins, confidence levels and reopen-triggers in the synthesis.
- **9–10**: Additionally: a maintained research commons the team actually reuses; evaluation templates with standing criteria; spike infrastructure warm; researcher calibration tracked against outcomes — and the cultural tell: "let me check the issue tracker" is the team's reflex where "I read a post about it" used to live.
