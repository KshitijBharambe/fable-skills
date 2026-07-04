---
name: technical-writing
description: "Use when writing a design doc, decision/ADR, PR description, incident report, runbook, or status update carrying bad news — lead with the conclusion, shape for the busiest reader, end relitigation."
---

# Technical Writing

## Purpose

Write documents that do work: design docs that surface disagreement before code does, decision docs that end relitigation, PR descriptions that direct reviewer attention, incident reports that convert outages into institutional memory, and status updates that carry bad news early — each led by the conclusion and shaped for its busiest reader.

## When to use

- A decision, design, or incident needs to outlive the meeting (or the people) that produced it.
- Before building anything with cross-team surface area — the design doc *is* the cheap round of iteration.
- Writing PR descriptions, deprecation notices, runbooks, READMEs, or the status update containing news nobody wants.
- When the same question keeps getting re-asked or the same decision keeps getting re-argued — a document is missing.
- When your writing is producing confusion, silence, or meetings-about-the-email — the craft needs a pass.

## Goals

- The busiest reader gets the point from the first three sentences; every document leads with the conclusion (BLUF: bottom line up front).
- Documents match their reader's altitude — one doc, one audience; execs and implementers don't share a document, they share a summary.
- Decisions recorded with context, options, and rationale — findable, dated, and citable in one link (the anti-relitigation machinery).
- Incident reports that are blameless, specific, and produce class-fixes with owners — not apology theater.
- Bad news travels faster than good news, with options and a recommendation attached.

## Expert Mental Model

- **Writing is thinking made checkable; the document is a byproduct.** The design doc's first customer is the author: prose forces the hand-waving into the open ("it'll just sync" becomes three paragraphs revealing you don't know how). Teams that "save time" by skipping the doc pay for it in code — the most expensive medium for discovering disagreement (see decomposing-ambiguity: the strawman in writing; convergent-evaluation: criteria on paper). A doc that was easy to write and surfaced nothing was probably written after the thinking, as decoration.
- **Lead with the conclusion; earn the detail.** Engineers narrate chronologically ("first I investigated X, then I tried Y…") because that's how the knowledge arrived — but readers need it in *decision order*: what should I know/do, then why, then the supporting archaeology for whoever wants it. The inverted pyramid isn't journalism affectation; it's respect for the fact that every document has more skimmers than readers. Test: if your reader stops after paragraph one, do they leave with the right takeaway or a cliffhanger?
- **Write for the reader you have, not the one who shares your context.** The curse of knowledge is the craft's central enemy: you can't un-know what you know, so your draft assumes vocabulary, context, and stakes the reader lacks. The disciplines that fight it: name the audience *before* writing (one doc, one altitude — the VP needs impact-and-ask; the implementer needs schemas and edge cases); define terms at first use or link them; and get one cold read from someone matching the real audience before wide distribution — their first confusion is your map (see onboarding: the same empathy, different medium).
- **Documents are decision infrastructure, not records.** The decision doc (ADR-shaped: context, options considered, decision, consequences, date, owner) exists so that six months later "why don't we just use X?" is answered with a link instead of a meeting — and so the decision can be *honestly revisited* when its recorded assumptions expire (see judgment-under-uncertainty: decision-time records; first-principles: constraint maps with dates). The failure isn't missing documentation — it's missing *the three documents that would have prevented forty meetings*. Write those; skip the rest. A wiki full of stale pages is worse than sparse-but-true, because readers who get burned once stop trusting all of it.
- **Incident reports are engineering artifacts with a political payload.** The blameless discipline isn't kindness — it's data quality: reports that name-and-shame get sanitized inputs next time, and the org loses its only honest error signal (see judgment-under-uncertainty: outcome-judged teams hide). The excellent incident report: timeline in facts (times, actions, observations — no adverbs), contributing causes plural (the trigger, the conditions, the missing guardrail — see root-cause-analysis), user-impact quantified, and remediation as *class-fixes with owners and dates*, not "be more careful." Its test: could an engineer who joins next year read it and avoid the same hole?
- **Bad news is a perishable good.** The status update that says "we're red, here's why, here are two options with a recommendation" is valuable exactly once — early, while options exist; the same facts reported late are just an autopsy (see planning-and-estimation: the re-baseline shipped same-day). The options-with-recommendation format is the load-bearing move: it converts "problem" (which lands on the reader's desk) into "decision" (which the reader can make in two minutes), and it's the difference between reading as a competent owner versus a bearer of chaos. Numbers travel with their captions — a "6 weeks" that escapes its "if the vendor sandbox behaves" clause will be quoted against you, caption-free, in a meeting you're not in.

## Workflow

1. **Name the reader and the job**: who reads this, what do they know already, and what should they *do* after reading? One sentence, written first. Multiple audiences → multiple docs (or one doc with a genuinely self-sufficient summary).
2. **Write the last line first**: the conclusion/ask/decision in one or two sentences. This is your BLUF; everything else exists to support it.
3. **Draft in decision order**: BLUF → context the reader lacks → the reasoning/options → the details/appendix. Chronology and archaeology go at the bottom, for the readers who want them.
4. **Make it skimmable as a parallel document**: headers that assert ("Migration cost is the binding constraint," not "Costs"), bold on the load-bearing claims, lists for enumerable things, tables for comparisons — a skimmer reading only headers and bold should get the honest gist.
5. **Instantiate every abstraction**: each general claim gets a number, an example, or a name ("significantly slower" → "p95: 80ms → 210ms"; see decomposing-ambiguity: load-bearing words). Every number keeps its caption (conditions, date, source).
6. **Cut by half, then by taste**: first drafts run double; delete throat-clearing openings, hedges that carry no information ("it could be argued that"), and everything the reader already knows. What remains, write in full sentences — compression by *selection*, not by telegraphese.
7. **Run the cold read**: one person matching the real audience reads it and narrates where they stumbled or skimmed. Their confusion is a defect list; fix the doc, not the reader.
8. **Ship it where it will be found**: the doc's home matters as much as its content — linked from the code it explains, the channel where its question recurs, the index people actually search (see the findability heuristics).
9. **Date it and own it**: every doc carries its date, author, and status (draft/active/superseded) — staleness explicit beats staleness discovered (see legacy-migrations: docs pointing at the corpse).

## Decision Tree

- If the same question has been answered twice in Slack → it's a document now; write it where the third asker will look, and answer question three with the link.
- If a decision is contentious or expensive → decision doc *before* the decision meeting: context, options with honest tradeoffs, recommendation — the meeting reviews a document instead of generating a transcript (see convergent-evaluation: criteria before options).
- If you're about to write a design doc →
  - Cross-team surface or one-way door → full treatment: problem, constraints, options considered (including the rejected ones, *with reasons* — the rejected options are the anti-relitigation payload), chosen design, risks, rollout (see judgment-under-uncertainty doors).
  - Team-internal and reversible → one page; the ceremony should match the blast radius.
- If writing a PR description → lead with *what and why* in two sentences, then reviewer directions: what changed structurally vs behaviorally (see refactoring: which kind of diff), where the risk concentrates, what you're unsure about — the description is reviewer-attention routing, not a changelog (see code-review: the author's half of the contract).
- If reporting status → green/yellow/red honestly; yellow and red lead with the delta, the cause, options, recommendation, and what you need — never bury the red in paragraph four (see planning-and-estimation triggers).
- If writing the incident report → facts-first timeline, plural contributing causes, quantified impact, class-fix actions with owners/dates; adjectives and blame deleted in review (see root-cause-analysis; the report is its output format).
- If the document keeps growing → it's several documents: split by reader (exec summary vs implementation spec) or by job (tutorial vs reference vs decision record — they have different truth-maintenance costs).
- If nobody reads your docs → diagnose as UX, not as audience failure: wrong home (not where readers look), wrong altitude (written for the author), or missing BLUF (readers sampled the first paragraph, found throat-clearing, left) — see the failure modes.
- If English isn't the reader's first language, or the audience is global → shorter sentences, no idioms, no cultural shorthand — plain style is also the inclusive style.

## Heuristics

- The first sentence is the document: most readers get no further — spend accordingly.
- Assert in headers: a reader scanning only your headers should absorb your argument's skeleton, not your table of contents.
- One idea per paragraph; the paragraph's first sentence is its BLUF — recursive structure, all the way down.
- Concrete beats abstract at every altitude: "the retry storm added 40k requests/min" outworks "significant additional load" in every audience including executives.
- Write the objection into the doc: the strongest counterargument, stated fairly and answered, converts skeptics and shortens meetings — omitted, it becomes the meeting.
- Hedge once, precisely, then commit: "80% confident, the risk is X" beats a document soaked in "possibly/perhaps/it seems" (see judgment-under-uncertainty: calibrated language) — diffuse hedging reads as either evasion or anxiety.
- Active voice puts owners in sentences: "the deploy script deleted the queue" not "the queue was deleted" — passive voice in incident reports is where accountability goes to hide.
- Examples are load-bearing: every API doc, runbook, and format spec leads with a worked example — readers pattern-match from examples and only read the prose when the example fails them (see api-design docs; onboarding).
- Link, don't summarize, the stable stuff; summarize, don't link, the load-bearing stuff — the reader shouldn't need to leave the doc to follow its main argument.
- Read it aloud once: the sentence you stumble over is the sentence that's broken.
- A runbook is only real if it's been executed by someone other than its author — same law as backups and rollbacks (see ci-cd; legacy-migrations: rehearsed reverts).

## Quality Checklist

- [ ] Reader and job named; the document matches their altitude and vocabulary.
- [ ] BLUF: conclusion/ask in the first three sentences; a paragraph-one-only reader leaves correctly informed.
- [ ] Decision-order structure; chronology demoted to appendix.
- [ ] Skimmable skeleton: asserting headers, bolded claims, lists/tables where the content is enumerable.
- [ ] Every abstraction instantiated; every number captioned with conditions and date.
- [ ] The strongest objection stated and answered in-doc.
- [ ] Cut pass done; hedges consolidated into one calibrated statement.
- [ ] Cold read by an audience-matched reader; their stumbles fixed.
- [ ] Dated, owned, statused, and homed where its readers actually look.
- [ ] For decisions: options-considered with rejection reasons; for incidents: blameless facts, plural causes, owned class-fixes; for status: bad news early with options and a recommendation.

## Failure Modes

- **The chronological narrative**: "First we noticed… then we tried…" — the conclusion in the final paragraph, where only the author's manager's manager never arrives; readers skim, miss the ask, and the doc "didn't work."
- **Curse-of-knowledge prose**: undefined acronyms, assumed context, the internal codename used as if universal — the doc is correct and incomprehensible, and readers blame themselves and stop reading (see onboarding: the expert's blind spot).
- **The everything document**: exec summary, implementation spec, API reference, and FAQ cohabiting one page for four audiences — each reader wades through three-quarters written for someone else; nobody finishes.
- **Hedge soup**: every claim wrapped in "possibly/may/it could be argued" — the author's anxiety exported as the reader's confusion; decisions can't be made from a document that won't commit (the calibrated alternative: one confidence statement, owned).
- **The blame-shaped incident report**: "the engineer failed to check…" — next quarter's reports arrive pre-sanitized, and the org's error data degrades permanently (see judgment-under-uncertainty: outcome-judged teams hide; the report format *is* the incentive structure).
- **Decision docs written after the fight**: rationale reverse-engineered to justify the winner, rejected options strawmanned — the anti-relitigation machinery corrupted into propaganda; relitigation returns, now with distrust (see convergent-evaluation: post-hoc criteria).
- **The stale wiki**: 400 pages, 60% wrong, no dates or owners — one burned reader generalizes to "the wiki lies," and the three true documents die with the rest (staleness is contagious; date-and-status is the vaccine).
- **Numbers escaping their captions**: the "6 weeks (if X and Y)" quoted as "6 weeks" in the exec deck — the caption was in paragraph three; the commitment is now yours (put conditions *adjacent* to numbers, always, or give ranges that survive decapitation).

## Edge Cases

- **Writing for hostile or skeptical readers**: the doc will be read uncharitably (post-incident, cross-org disputes, deprecations someone hates) — every claim needs its receipt inline, tone flatter than feels natural, and the reader's likely objection pre-answered; humor and irony are transport risks (see technical-leadership stakeholders).
- **Legal/compliance gravity**: incident reports and security docs may be discoverable; "we've always known this was broken" written casually is a deposition exhibit — facts and timelines, no editorializing, and when in doubt on breach-adjacent docs, the review includes counsel (see web-security; the blameless discipline conveniently overlaps).
- **The deprecation notice**: three audiences in one artifact (the user who'll migrate this week, the one who'll ignore it, the one who'll find it via a broken build next year) — dates, alternatives, migration examples, and escalating in-band repetition; one email is not a deprecation (see legacy-migrations 3-2-1 comms; api-design).
- **Docs as API: runbooks under stress**: the 3am reader has 20% of their usual cognition — runbooks get numbered steps, exact commands (copy-pasteable, with placeholders visually loud), expected outputs after each step, and a "if this doesn't match, stop and page X" branch (see production-debugging; interface-states: error paths get the most design).
- **Cross-cultural directness calibration**: "this design has a flaw" reads as collegial in one culture and as an attack in another — on global teams, criticize designs with questions and data ("what happens when the queue backs up?") and keep praise/critique ratios in mind; the goal is the fix, not the point-scoring.
- **When the truth is politically expensive**: the honest status update that contradicts a VP's public commitment — accuracy is non-negotiable, but framing is a choice: lead with the shared goal, present the delta as options-with-costs, and deliver the draft to your chain *before* wide distribution (no ambushes; see technical-leadership: managing up).
- **AI-era authorship**: generated drafts are fluent and confidently generic — the human value-add concentrates in exactly what generation lacks: the real constraints, the actual numbers, the political context, the honest confidence levels; a fluent doc with no load-bearing specifics is decoration either way (see prompt-engineering for the production side).
- **The document that shouldn't exist**: some knowledge is better as a test, a type, a lint rule, or a code comment at the point of use — before writing the wiki page "remember to always X," ask if the system can enforce X instead (see web-security: construction over vigilance; the doc is the fallback, not the fix).

## Tradeoffs

- **Completeness vs reading probability**: every added section lowers the chance any section is read — the resolution is layering (BLUF → body → appendix), not amputation; put completeness where only its seekers pay for it.
- **Precision vs accessibility**: exact terminology serves experts and walls off everyone else — pick per audience, and when both matter, plain language in the body with precision in parentheses or appendix ("the queue backs up (consumer lag exceeds the retention window)").
- **Speed vs polish**: the same-day rough status beats next week's polished one, always (bad news is perishable); the design doc inverts — its whole value is the thinking, so "fast" defeats the purpose. Match polish to the document's job, not to your pride.
- **Documentation coverage vs maintenance debt**: every doc written is a doc that can go stale and lie — write the few that prevent meetings and incidents, put truth-maintenance where docs touch volatile facts (generate from source, link to dashboards, date everything), and prefer sparse-and-true to complete-and-rotting.
- **Candor vs relationships**: the incident report that names the deploy process (owned by a proud team) as a contributing cause, the status update that flags a peer team's slip — soften the *framing*, never the *facts*; a document that protects feelings by omitting causes buys comfort with recurrence (see technical-leadership: truth with a communication plan).
- **Standardization vs fit**: templates (ADRs, postmortem formats, PR checklists) lower the writing barrier and raise the floor — and produce checkbox prose when the template outruns the thinking; treat templates as prompts, not forms, and let short honest deviations beat long compliant emptiness.

## Optimization Strategies

- Maintain the three templates that pay rent — decision doc, incident report, status update — pre-structured with BLUF slots and options-with-recommendation sections; the format doing the remembering means the 2am version is still shaped right (see judgment-under-uncertainty: templates teach the org).
- Build the decision log as a first-class index: one page linking every ADR with date and one-line outcome — the relitigation-killer is findability, not existence (see convergent-evaluation receipts).
- Instrument your documents where stakes justify it: the runbook that logs its own execution, the design doc with a comment deadline, the deprecation notice with click-through tracking — documents have observable outcomes; treat silence as a signal to re-home or re-write (see observability thinking, applied to prose).
- Do the cold-read exchange as a standing practice: trade pre-publication reads with a peer weekly — you catch their curse-of-knowledge, they catch yours; both writers compound (see code-review: the same fresh-eyes economics).
- Collect your own before/after pairs: the doc that confused → its fixed version; the buried-lede status → its BLUF rewrite — a personal corpus of ten pairs teaches more than any style guide, and makes the patterns teachable to your team (see learning-new-stacks: worked examples).
- Write the summary first for anything longer than a page — if you can't write the three-sentence version, the thinking isn't done, and the long version will be long *because* it's unresolved (writing as thinking, used as the test).

## Self Review

- Who is the reader, and what do they do after reading — and does the first paragraph alone get them there?
- If someone reads only my headers and bold text, what story do they get — and is it the true one?
- What does the reader not know that I've assumed? (Name three things; you'll find one that's load-bearing.)
- Where's my strongest critic's objection — in the doc and answered, or waiting in the comments?
- Which numbers could be quoted without their captions — and do they survive decapitation?
- Is my bad news in sentence one or paragraph four — and if I'm sitting on it, what am I waiting for that won't be worse later?
- Did anyone matching the real audience read this cold — or am I shipping on the author's comprehension?
- Six months from now, does this document answer a question in one link, or start a meeting?

## Examples

**1. The buried lede, exhumed.**
Draft status update: three paragraphs of sprint accomplishments, then — paragraph four — "we've also discovered the vendor API doesn't support batch operations, which may impact the timeline." The rewrite leads: "**The launch date is at risk: the vendor API lacks batch support, adding 3–5 weeks. Two options below; recommendation: option B. Decision needed by Friday.**" Then options with costs (A: sequential calls + caching, 3 weeks, degrades p95; B: vendor's bulk-export path, 5 weeks, keeps latency — see planning-and-estimation re-baseline), then, last, the sprint notes. Same facts; the first version generates a "wait, what?" meeting next week (see the perishability law); the second generates a decision by Friday. The delta was structure, not information.

**2. The decision doc that ended a two-year argument.**
The "why Postgres and not a document store" debate resurfaces quarterly with each new hire (see postgres). One ADR ends it: context (2023 scale assumptions, team skills, the transactional core), options considered — including the document store, *fairly*: its real wins listed, and the two conditions under which it would have won ("if the schema were truly document-shaped; if we lacked relational query needs") — the decision, its consequences (accepted operational costs), date, and revisit-trigger ("re-open if we shard past N or the flexible-schema surface exceeds M tables"). The next "why don't we just use Mongo?" gets a link and a genuine offer: "if you think the trigger conditions are met, let's re-open it." Two relitigations since: one dissolved by the link in minutes; one *legitimately reopened* by the trigger — which is the doc working both ways (see first-principles: the constraint map; convergent-evaluation receipts).

**3. The incident report as engineering artifact.**
Outage: checkout down 47 minutes. The draft says "the on-call engineer failed to notice the alert." The blameless rewrite reconstructs *why not-noticing was the system's most likely outcome*: timeline in timestamps (14:02 deploy; 14:09 error-rate alert fired *into a channel muted during a prior alert storm* — see observability alert fatigue; 14:31 first customer report; 14:49 rollback). Contributing causes, plural: the migration lacked a lock-timeout (trigger), the alert channel was muted (detection gap), rollback required a manual step undocumented since the runbook predated the new deploy system (recovery gap — see legacy-migrations: docs pointing at the corpse). Actions, all class-shaped with owners and dates: lock-timeouts enforced by CI check (see ci-cd), alert routing rebuilt with paging escalation, rollback automated and *rehearsed*. The engineer's name appears once — in the "responded" credits. Next quarter's near-identical incident at a peer team: their engineer finds this report by searching, and their outage lasts six minutes.

**4. One design, two documents.**
A search-infrastructure migration (see legacy-migrations) needs both VP sign-off and implementation review. The single 14-page draft serves neither: the VP won't read past page one; the implementers can't find the schema among the budget justifications. Split: a one-pager for the decision-makers — BLUF ("recommend migrating; $Xk/quarter savings, 2 engineers × 1 quarter; the risk is relevance parity, mitigated by shadow-diffing — see the plan"), a costs/options table, the ask; and the full spec for the builders — schemas, cutover stages, diff thresholds, rollback gates. The one-pager links the spec; the spec's summary *is* the one-pager. Both audiences read their document to the end — which, for the 14-page draft, neither would have done. The extra cost: one hour. (See system-design for the architecture itself; this example is about the paper.)

## Evaluation Rubric

Score 1–10:

- **1–2**: Chronological narratives with buried conclusions; undefined jargon; hedge soup; blame-shaped postmortems; no decision records — the same arguments recur monthly.
- **3–4**: Docs exist but are author-shaped: single everything-documents, numbers without captions, rejected options unrecorded, status updates that lead with the good news.
- **5–6**: BLUF discipline on most documents; audiences named; decision docs with options and dates; blameless incident format; bad news shipped early with options.
- **7–8**: Full checklist: asserting headers, instantiated claims, in-doc objections, cold reads, findable homes, templates for the big three, captioned numbers that survive quoting.
- **9–10**: Additionally: a maintained decision log that demonstrably kills relitigation; incident reports that other teams learn from; documents with revisit-triggers that actually fire; a personal/team corpus of before/after pairs used for teaching — and the observable outcome: fewer meetings, because the documents attend them for you.
