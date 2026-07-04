---
name: code-review
description: "Use when reviewing a PR (and calibrating how deeply), authoring a reviewable PR, responding to review feedback, or setting team review norms — severity, blast-radius attention, teaching comments."
---

# Code Review

## Purpose

Review code the way senior engineers do: attention allocated by blast radius (not by line count), comments that teach and carry severity labels, standards enforced by tools so humans review judgment — and the author's half of the contract honored, because reviewability is a property of the PR before it's a property of the reviewer.

## When to use

- Reviewing any change — and calibrating *how deeply* this one deserves.
- Authoring a PR: shaping it so review is fast, focused, and likely to catch what matters.
- Responding to review feedback, especially feedback that stings or misses.
- Setting team review norms: what blocks, what's advisory, what's automated away.
- When review has become the bottleneck (queues, rubber stamps, or 400-comment wars) and the process itself needs review.

## Goals

- High-blast-radius problems (data loss, security, contract breaks, silent corruption) caught before merge; style noise eliminated from human review entirely.
- Every comment labeled by severity (blocking / should / consider / nit) and carrying its reason — the reviewer teaches, not just gates.
- PRs sized and described for reviewability: one intention per PR, structure separated from behavior, risk flagged by the author.
- Review latency short enough that it isn't the team's critical path (see planning-and-estimation: the invisible 40%).
- Knowledge actually spreads: reviews leave both parties knowing more, and the codebase's standards live in shared vocabulary, not one gatekeeper's taste.

## Expert Mental Model

- **Review depth is allocated by blast radius, not by diff size.** The 400-line test refactor needs a skim; the 3-line change to payment retry logic needs a meditation (see judgment-under-uncertainty doors — the same classification, applied to reading). Experts triage first: what does this change touch (money, auth, data integrity, public contracts, concurrency — see the hot-spot list in the workflow), how reversible is a mistake, who depends on it? The novice reviews linearly, spending equal attention per line, which guarantees the attention runs out before the dangerous part — usually located in the migration file at the bottom of the diff.
- **The reviewer's real job is what the tests and tools can't see.** Linters own formatting; CI owns "does it pass"; type-checkers own signatures (automate all of it — every style comment a human writes is a process failure; see the norms below). What remains is the human layer: *should* this exist (does it solve the actual problem — see decomposing-ambiguity)? Is the approach right at this altitude (see abstraction-and-simplicity: depth, naming-as-claims, wrong abstractions)? What happens when it fails (the error path, the race, the retry — see the edge-case eye below)? Will the next reader understand it? A review that's all syntax is a review that outsourced its judgment to nobody.
- **The absence eye: the hardest skill is reviewing what isn't in the diff.** The diff shows what changed; the bugs live in what didn't — the caller that also needed updating, the missing migration for the renamed column, the error path that new code never handles, the test that should exist and doesn't, the invariant maintained everywhere except here (see refactoring: shotgun surgery — the diff that should have been bigger). Experts read diffs *outward*: from each change, briefly into its callers, its siblings, its failure modes. This is also why local diff-beauty is a weak signal: a perfect-looking function that breaks its one invisible caller reviews "clean" and ships an incident.
- **Comments are teaching with a severity contract.** Every comment carries (a) what, (b) why — the reason is the teaching payload and the difference between a standard and a taste ("this races under concurrent refunds because X" vs "I wouldn't do it this way"), and (c) severity: **blocking** (correctness, security, data, contracts — must fix), **should** (real improvement, author may argue), **consider/nit** (author's call, no re-review needed). Unlabeled comments force the author to guess which hills are yours to die on — and guessing wrong in either direction costs a round trip or a resentment. Questions beat verdicts where genuine ("what happens if the queue is down here?") — they teach, they surface the author's reasoning, and half the time the answer is "good catch," delivered by the author to themselves.
- **The author owns reviewability.** A PR is a document with a reader (see technical-writing: the busiest reader) — the author's contract: one intention per PR (the feature *or* the refactor *or* the fix — see refactoring: structure vs behavior commits); a description that routes attention (what changed, why, where the risk concentrates, what you're unsure about — flagging your own doubt is seniority, not weakness; see judgment-under-uncertainty); self-review before requesting (the debug print, the commented block, and the accidental lockfile churn are the author's to catch); and size discipline — defect-detection per line collapses past a few hundred lines, so the 1,200-line PR gets either a rubber stamp or a week of latency, both failures (see the tradeoffs).
- **Review is a trust-and-knowledge protocol, not a gate with a human face.** Calibrate to the author (the new hire gets depth *and* warmth — their first reviews set their model of the team's bar; the veteran in their home module gets speed), let review rotate so knowledge spreads (see technical-leadership bus factor: review as the cheapest pairing), and remember both directions carry information — the reviewer who only ever transmits learns nothing, and half of review's compound value is the reviewer discovering how this module actually works (see legacy-migrations archaeology: reviews are how you keep the map current). Tone compounds too: the codebase outlives every PR, but so does the relationship — critique the code, never the coder, and write like it'll be read at 2am by someone having a bad week, because it will.

## Workflow

1. **Read the description and triage first**: what is this trying to do, what's its blast radius, how deep does it deserve? No description → send it back for one; reviewing an unlabeled diff is archaeology at premium rates (see technical-writing: PR descriptions).
2. **Check the shape before the lines**: does this change belong here (right module, right layer — see abstraction-and-simplicity)? Is it one intention? Approach-level problems get raised *now*, at the top — approach comments after 40 line comments waste everyone's evening.
3. **Sweep the hot spots**: money paths, auth/authz (see authorization: is the object-level check here?), migrations and anything touching data irreversibly, concurrency (shared state, check-then-act — see concurrency-bugs), external contracts (API/event schemas — see api-design; event-driven), injection surfaces (see web-security: string-built anything), error/retry paths (see async-processing: is it idempotent?).
4. **Run the absence eye**: from each change, glance outward — callers of the changed function, the invariant's other enforcement sites, the test file that should have changed and didn't, the docs/runbook now stale (see the mental model; this pass catches what the diff can't show).
5. **Read the tests as claims**: do they pin the behavior that matters (see enforce-first), or do they mock the world and assert the mocks? Would they fail if the bug existed? A diff whose tests couldn't catch its own regression is half-reviewed by definition.
6. **Write comments with the contract**: severity label + reason + (where useful) a question or a sketch. Batch them in one pass — comment-dribble across a day multiplies the author's context-switches.
7. **Decide explicitly**: approve (nits notwithstanding — say so), approve-with-blocking-items-fixed (only for mechanical fixes), or request changes with the blocking list unambiguous. The worst outcome is ambiguity about whether the author may merge.
8. **As author, run the mirror protocol**: self-review the diff cold (you'll catch a third of what the reviewer would), write the attention-routing description, flag your own uncertainty, keep it one-intention and reviewably sized, and respond to feedback by fixing, arguing with reasons, or explicitly deferring with a ticket — never by silence (see respond-review).
9. **Escalate disagreements out of the thread**: three rounds of comment-volley → synchronous conversation (or the team's decision protocol — see technical-leadership); comment threads are where nuance goes to die and positions go to harden. Record the resolution back in the thread for the archaeology.

## Decision Tree

- If the PR is huge → don't heroically review it: ask for a split (structure/behavior, or slice by capability — see refactoring; planning-and-estimation slicing); if it genuinely can't split (the generated migration, the vendored update), review the hand-written core deeply and say explicitly what got skimmed.
- If the approach is wrong → one top-level comment, stop line-reviewing, offer a conversation — the kindest possible version of "this needs rethinking" delivered *before* the author polishes the wrong thing further.
- If you don't understand the code → that *is* the finding, not your failure: ask — either you're missing context the description should have carried, or the code is too clever for its next maintainer too (see abstraction-and-simplicity: the median-maintainer test); both are the author's to fix.
- If it touches an area you don't know → say so, review what you can (clarity, tests, error paths travel across domains), and pull in the domain owner for the rest — a confident stamp on unfamiliar deep water is how "reviewed" incidents happen (see technical-leadership: review routing).
- If you find a real bug adjacent to but not caused by the diff → don't hold the PR hostage: note it, spin it into its own ticket, let this PR land (scope discipline applies to reviewers too).
- If the author pushes back with reasons → engage the reasons; if they're right, say so cheerfully (the reviewer who can't lose an argument teaches everyone to stop arguing — see technical-leadership: safety pricing); if it's taste-vs-taste → author wins by default (their name is on the maintenance).
- If it's blocking-severity and the author wants to ship anyway ("deadline") → severity doesn't negotiate with calendars on correctness/security/data items; the escalation path is the lead and the risk decision made *explicitly* (see judgment-under-uncertainty: one-way doors under pressure), not a worn-down approve.
- If you're rubber-stamping from fatigue or social pressure → decline the review honestly ("can't give this the attention it needs today") — a stamp without a review is worse than a delay, because it *looks* like a control (see the failure modes).
- If the same comment recurs across PRs/authors → it's not a comment anymore, it's a missing lint rule, a missing doc, or a missing team decision — automate it, write it, or decide it once (see technical-writing: the twice-asked question; the norms below).

## Heuristics

- Review the tests first when short on time: they state what the author believes the code does; the gap between that belief and the diff is where the bugs are.
- The migration file at the bottom of the diff is the most dangerous text in most PRs — read it first, not last (irreversibility lives there; see legacy-migrations expand-contract; postgres locks).
- Ask "what happens when this fails?" once per external call, queue write, and transaction in the diff — the error path is where review attention pays 10× (see production-debugging: incidents live on the unhappy path).
- Names are review surface: does each new name tell the truth (see abstraction-and-simplicity: lying names) — and does the *diff* make any existing name a lie (`getUser` growing a write)?
- Praise specifically and in public comments: "this refactor makes the retry logic actually followable" — reviews teach what good looks like at least as much as what bad looks like.
- Watch for the diff that should exist and doesn't: renamed concept, un-renamed docs; new config, no default in the deploy env; new error, no alert (the absence eye's checklist form).
- Two mediums beat forty nits: if you're writing your 15th comment, the PR (or the standard) has a problem your comments won't fix — zoom out.
- Timebox and declare: 30 focused minutes catches most of what 3 unfocused hours does; say what depth you gave ("deep on the state machine, skimmed the fixtures") so the stamp is honest.
- Your approval means *you* would maintain this — if that thought produces a flinch, the flinch is a comment you haven't written yet.
- Review latency is a team SLO: same-day is the healthy default; a PR aging three days costs a context-switch tax on both sides and pressures the next review toward a rubber stamp (see planning-and-estimation: review latency as a line item).
- The author's "I'm not sure about the locking here" is the most valuable sentence in any description — reward it with attention, never with "then why did you write it?"

## Quality Checklist

- [ ] Triage done: blast radius named, depth matched to it, hot spots swept.
- [ ] Approach validated (or challenged) before line-level investment.
- [ ] Absence eye run: callers, invariants, missing tests, stale docs checked around the diff.
- [ ] Error paths, concurrency, and idempotency questioned wherever the diff touches them.
- [ ] Tests read as claims; they'd fail if the bug existed.
- [ ] Every comment: severity-labeled, reason-carrying, code-directed (never coder-directed).
- [ ] Decision unambiguous: the author knows exactly what blocks merge.
- [ ] As author: one intention, self-reviewed, description routes attention, uncertainty flagged, size reviewable.
- [ ] Style and mechanical checks fully automated — zero human comments on formatting.
- [ ] Recurring comments converted to lint rules, docs, or team decisions.

## Failure Modes

- **The line-by-line equalizer**: every line gets equal attention, so the budget dies in the test fixtures before reaching the migration — depth uncalibrated to danger; the incident ships with 40 nits fixed.
- **The style gate**: humans litigating brace placement and import order while the check-then-act race sails through — the automatable occupying the irreplaceable (and teaching authors that review = formatting theater).
- **Rubber-stamp culture**: same-hour approvals on everything, "LGTM" as a reflex — review as ritual; the control everyone believes exists, exists nowhere, and the first bad incident audits it publicly (see judgment-under-uncertainty: correlated safeguards).
- **The hostage review**: 60 comments spanning blocking-to-whim, unlabeled, dribbled over three days, plus scope demands ("while you're here, fix the module") — the author can't find the merge path; velocity and goodwill both bleed out.
- **Ego review**: verdicts without reasons, taste enforced as law, sarcasm as style ("did you even test this?") — authors learn to route around the reviewer (timing PRs to their vacations), and the team's real review coverage quietly halves (see technical-leadership: the corrosive expert).
- **The unreviewable PR, unchallenged**: 1,800 lines, three intentions, no description — and the reviewer heroically "reviews" it anyway, finding nits and missing the design flaw; the correct review was "please split this," sent in minute two.
- **Approve-under-protest erosion**: blocking concerns worn down by deadline pressure into a sighing stamp — the severity contract collapses; next time the author knows blocking just means "argue longer" (see the decision tree: severity doesn't negotiate with calendars).
- **Knowledge monoculture**: all reviews route through one gatekeeper — quality is fine, the bus factor is 1, latency is their calendar, and nobody else ever learns the module (see technical-leadership: rotation; the gate that should have been a school).

## Edge Cases

- **Emergency/incident reviews**: the 3am hotfix gets a different contract — one reviewer, correctness-of-the-fix only ("does this stop the bleeding, can we revert it?"), with the *real* review as a scheduled follow-up on the calm version (see production-debugging: stabilize first; the follow-up actually happening is the discipline).
- **Generated and vendored diffs**: lockfiles, codegen, formatter migrations — review the *generator inputs* and spot-check outputs; line-reviewing 10k generated lines is theater (but the lockfile diff gets the supply-chain eye — see secrets-and-supply-chain: read the lockfile diff).
- **Cross-team and drive-by PRs**: an outside contributor doesn't know your conventions — the review carries onboarding weight; link the convention doc instead of enforcing it as if it were obvious (see onboarding; technical-writing: the doc that answers in one link), and weight kindness double: this review is your team's front door.
- **Reviewing your senior / your lead**: the severity contract is rank-blind by design — the junior who blocks the staff engineer's race condition should be celebrated *loudly* (see technical-leadership: safety pricing); if that feels unthinkable on your team, that's the finding.
- **AI-generated code in the diff**: fluent, confident, and unowned — the review question shifts to "does the *author* understand this?" (ask them to walk the tricky part); volume pressure rises (generation is cheap, review isn't), which makes size discipline and the absence eye *more* load-bearing, not less (see judgment-under-uncertainty: fluency is not calibration).
- **The perpetual re-request**: a PR on its sixth round — something upstream failed (the design conversation that never happened — see decomposing-ambiguity; or requirements moving under it); stop reviewing and have the conversation the rounds are substituting for.
- **Config, infra, and one-line diffs**: the smallest diffs carry the largest blast radii (the retry count, the timeout, the IAM wildcard — see secrets-and-supply-chain least-privilege; system-design: config as code) — one-line changes to production behavior get *more* scrutiny per line than anything else in the queue.
- **Review across timezones**: the volley that costs a day per round — front-load completeness (one thorough batch, explicit severity, suggested diffs where trivial) and pre-authorize ("fix the two blockers and merge, no re-review needed") so the contract spans the ocean without a third round trip (see technical-writing: write for the reader's timezone too).

## Tradeoffs

- **Thoroughness vs latency**: the deep review catches more and costs queue time (and stale-diff rebases); the fast review keeps flow and misses subtleties — resolve by triage (depth where blast radius lives) and by SLO (same-day default, depth *declared*), not by uniform policy.
- **Author autonomy vs reviewer standards**: taste-tie goes to the author (their maintenance, their name); standards-tie goes to the codebase (consistency compounds — see abstraction-and-simplicity: consistency vs fit); the discipline is knowing which kind of tie you're in, and labeling accordingly.
- **Blocking rigor vs shipping pressure**: holding the line on correctness under deadline costs a hard conversation now; folding costs an incident-shaped invoice later (see judgment-under-uncertainty: the exchange rate) — the pressure valve is scope (ship less, correct) rather than bar-lowering (ship all of it, hopeful).
- **Review as gate vs review as school**: pure gatekeeping maximizes short-term defect-catching (the expert reviews everything) and starves growth and bus factor; pure rotation maximizes learning and lets subtle things through — blend by blast radius: crown jewels get the expert *plus* the learner, everything else rotates (see technical-leadership: delegation calculus, same curve).
- **Comment completeness vs signal density**: writing every observation buries the two that matter under the twenty that don't — severity labels partially rescue this, but the stronger move is selection: drop the "consider"s that wouldn't change what the reader does (see technical-writing: selection over compression).
- **Small PRs vs integration visibility**: slicing for reviewability can hide the emergent whole (five clean PRs, one incoherent feature) — pair small diffs with a design doc or a draft-PR overview that shows the destination (see technical-writing design docs; planning-and-estimation: the skeleton first makes later slices legible).

## Optimization Strategies

- Automate ruthlessly and continuously: every human style comment becomes a lint rule the same week; formatting, imports, and obvious footguns (see web-security: the grep-able banlist) run pre-review — the human budget is reserved for judgment by *construction*.
- Write the team's review contract down (severity vocabulary, latency SLO, size norms, what blocks) and onboard people into it (see onboarding; technical-writing) — unwritten review culture is learned by collision.
- Use checklists per danger zone, not per PR: the migration checklist (locks? backfill? rollback? — see postgres; legacy-migrations), the endpoint checklist (authz? rate limit? injection? — see web-security), pulled out only when the diff touches that zone — targeted ceremony beats uniform ceremony.
- Track the two health metrics: review latency (queue-to-first-response) and escaped-defect origin (did incidents pass through review? what kind of eye would have caught them? — see root-cause-analysis: fix the class, including review-process classes).
- Rotate deliberately and pair the review: high-risk diffs get expert+learner; the learner writes the first pass, the expert adds the delta — review as the cheapest structured mentoring the team owns (see technical-leadership: growing on purpose).
- Retro your own review misses: when an incident traces through a PR you approved, diff your review against the bug — was it depth allocation, absence-eye, or contract erosion? The reviewer's calibration loop is the same as every other judgment loop (see judgment-under-uncertainty: the scoreboard).

## Self Review

- Where does the blast radius live in this diff — and did my attention actually go there, or did I read linearly until tired?
- What *isn't* in this diff that should be — which caller, test, migration, doc, or error path did I check for?
- Would these tests fail if the bug existed — or do they assert the mocks?
- Is every comment labeled, reasoned, and aimed at the code? Which one is actually just my taste wearing a standards costume?
- Does the author know, unambiguously, what blocks merge?
- (As author) Did I self-review cold, route the reviewer's attention, and flag my own doubts — or am I outsourcing my uncertainty as their surprise?
- Am I about to stamp something I wouldn't maintain — and if so, what's the flinch trying to tell me?
- What comment have I now written three times — and why is it still a comment instead of a lint rule?

## Examples

**1. Triage beats thoroughness.**
Two PRs arrive together: a 700-line rename-and-move refactor (structure-only, tests untouched and green — see refactoring: mechanical commits) and a 9-line change to webhook processing. The equalizer instinct says the big one needs the time; triage says otherwise. The refactor gets 15 minutes: spot-check the mechanical transform, verify no behavior diff smuggled in (tests unchanged is the tell), approve. The 9-liner gets 40 minutes: it moves a `charge()` call inside a retry loop — the absence eye asks "is this idempotent?" and finds no idempotency key on the charge path (see async-processing): a duplicate-payment bug that would have shipped inside the week's most innocent-looking diff. One blocking comment with the failure scenario spelled out; the author fixes it with a key and a test that pins it. Attention allocated by danger caught what attention allocated by volume would have missed.

**2. The severity contract in action.**
A mid-level engineer's PR gets 14 comments from their reviewer — labeled: 2 blocking ("this SQL is string-built — injection surface, see the query-layer helper", "migration takes an exclusive lock on a 40M-row table during peak — see the expand-contract pattern"), 4 should ("this name claims a read but writes — rename or split"), 8 consider/nit ("could be a guard clause", style-adjacent musings). The author fixes the blockers, argues one should ("the write is intentional — here's why") and wins it cheerfully conceded, batch-accepts three nits and declines five — *no re-review requested per the contract*, merge on green. Total wall-clock: four hours, one round. The identical unlabeled review at a previous team had taken this same author three days and two resentments — the delta is entirely the contract.

**3. The absence eye catches the invisible caller.**
A clean PR renames `Account.balance` to `Account.available_balance` and updates every reference — the diff is complete, consistent, green. The outward glance: who *else* speaks this name? A grep beyond the repo finds the analytics pipeline (separate repo) consuming the field from the event payload — the diff renames it in the event schema too, which is a *contract break* wearing a refactor costume (see event-driven: schema evolution; api-design: publishing is forever-ish). The blocking comment redirects: additive evolution (new field alongside old, consumers migrated, old field deprecated on a schedule — see legacy-migrations 3-2-1). The PR's local perfection was the trap: nothing *in* the diff was wrong; the bug was the diff's edge, where it met a consumer the author couldn't see (see decomposing-ambiguity: invisible consumers).

**4. Reviewing the process, not the person.**
An incident postmortem (see technical-writing: blameless) traces a data-corruption bug through an approved PR. The review retro avoids the easy story ("reviewer missed it") and diffs the review against the bug: the corruption lived in a check-then-act race (see concurrency-bugs) inside a 1,400-line mixed PR (feature + refactor + drive-by fixes) reviewed in one sitting at 6pm. Class-fixes, not vigilance-pledges: size norms adopted (soft 400-line limit, structure/behavior separation required — see refactoring), the concurrency checklist added for diffs touching shared state, and review latency SLO set so PRs stop aging into end-of-day marathons. Two quarters later the escaped-defect log shows the class extinct — the review process got the same engineering treatment as the code it guards (see root-cause-analysis: the fix at the deepest economical layer).

## Evaluation Rubric

Score 1–10:

- **1–2**: Line-by-line equalizing or reflex-stamping; style wars by hand; unlabeled comment piles; huge PRs reviewed heroically; tone that authors route around; review latency measured in days.
- **3–4**: Some real findings but depth uncalibrated to risk; severity implicit and guessed at; absence eye absent; recurring comments never automated; author-side contract unhonored (no descriptions, mixed intentions).
- **5–6**: Triage by blast radius; hot spots swept; comments labeled with reasons; mechanical checks automated; PRs sized and described; decisions unambiguous.
- **7–8**: Full checklist: absence eye routine, tests read as claims, error-path interrogation standard, danger-zone checklists in use, taste-vs-standard distinguished, latency SLO held, escalation paths that work.
- **9–10**: Additionally: review demonstrably spreads knowledge (rotation with expert+learner pairing, bus factors above one); escaped defects traced to review-process class-fixes; the team's review vocabulary shared and rank-blind; authors flag their own risks as a norm — and the culture tell: juniors block seniors' unsafe diffs, and get thanked in public.
