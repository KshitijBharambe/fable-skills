# Planning and Estimation

## Purpose

Sequence work so risk dies early and value ships continuously, and produce estimates that are honest instruments (with stated uncertainty and update triggers) rather than negotiated fictions — including knowing when planning itself is the wrong move.

## When to use

- Work spans more than a few days or more than one person, and someone needs to coordinate around it.
- A date is being asked for, promised, or (worse) already promised on your behalf.
- A project keeps "90% done" for weeks — the plan's shape, not the team's effort, is usually the defect.
- Before committing to scope on anything with dependencies, integrations, or unknowns.
- When deciding *whether* to plan: novel/exploratory work may need a spike and a kill criterion instead of a Gantt bar.

## Goals

- Work sequenced by risk-retirement: the assumptions that could kill the project die in week one, not week nine.
- A walking skeleton — thinnest end-to-end slice through every layer — running before any layer is "finished."
- Estimates given as ranges with confidence and *what would change them*, anchored in reference-class history, not introspection.
- Integration, review, deploy, and coordination costs priced in explicitly — the invisible 40% made visible.
- A plan that is a living instrument: re-estimated on triggers, with slack that survives contact with management.

## Expert Mental Model

- **Plans are for risk-sequencing, not fortune-telling.** The novice plans to predict the future; the expert plans to *order the work so the future has fewer ways to surprise them*. The plan's first job: identify what could invalidate the project and schedule those things first (see decomposing-ambiguity: first piece by invalidation-power). A plan whose week one is "set up repo, write models" and whose week eight is "integrate with the payment provider" has scheduled its biggest unknown at the point of maximum sunk cost.
- **The walking skeleton is the highest-leverage planning move.** Build the thinnest possible end-to-end path — one request through UI, API, database, third-party, deploy pipeline, production — before deepening any layer. It converts integration risk (the kind that surfaces in week nine) into week-one knowledge, gives every subsequent estimate a real substrate, and makes the project demoable forever after (see ci-cd: deploy the skeleton on day one; system-design: the seams reveal themselves).
- **Reference-class estimation beats introspection, always.** "How long will this take?" answered by imagining the work produces the planning fallacy — humans imagine the happy path, and imagination doesn't include the sick day, the flaky test, the API that lies. The expert asks instead: "how long did things *of this kind* actually take, here, historically?" The outside view (last three integrations: 3×, 2.5×, 4× their estimates) beats the inside view even when the inside view knows more details — details feed optimism, base rates feed accuracy.
- **Vertical slices, not horizontal layers.** "All the models, then all the APIs, then all the UI" delivers nothing until everything, hides integration risk until the end, and makes progress unmeasurable ("the backend is 80% done" is a sentence with no truth conditions). Slices — each a user-visible capability touching all layers — deliver value continuously, integrate continuously, and make progress binary: the slice ships or it doesn't (see develop-tdd slice thinking; product-thinking MVP).
- **The invisible 40%: integration, coordination, and the last mile.** Estimates cover typing; projects consist of typing *plus* code review latency, environment fights, cross-team hand-offs, QA cycles, deploy windows, and the brutal last 10% (edge cases, polish, migration) that takes as long as the first 90%. "90% done" is a measurement error: the remaining "10%" is typically the second half (see legacy-migrations: the long tail is the migration). Experts price hand-offs per seam and treat every cross-team dependency as a schedule risk with an owner.
- **When not to plan**: exploratory, research-shaped, or taste-shaped work resists decomposition-by-task because the tasks aren't knowable yet. Planning theater on such work produces fictional Gantt charts and real frustration. The honest instruments there: timeboxed spikes with kill criteria ("two days; if the query engine can't handle pattern X, we stop" — see research; convergent-evaluation information-buying), and re-planning gates once the fog lifts. Plan the *learning*, not the unknowable building.

## Workflow

1. **Start from a decomposition** (see decomposing-ambiguity) — pieces, dependencies, assumption ledger. No decomposition, no plan; go do that first.
2. **Rank pieces by invalidation-power**: which, if it fails, kills or reshapes the project? Those are week one, regardless of how "foundational" other work feels.
3. **Design the walking skeleton**: the thinnest end-to-end slice touching every layer and every scary integration (auth, payments, the third-party API, the deploy pipeline). Schedule it first; deploy it to production-like infrastructure immediately (see ci-cd).
4. **Slice the remaining work vertically**: each slice user-visible, independently shippable, demoable. Name each slice by the capability it delivers, not the layer it touches.
5. **Estimate by reference class**: for each slice, find the three most similar past pieces of work and use their *actuals* (from your tracker, not from memory — memory launders overruns). No history → widen the range and say so.
6. **Estimate as ranges with confidence**: "2–4 weeks, 80%" not "3 weeks." State what would move the estimate ("if the vendor sandbox matches prod behavior, low end; if not, high end") — the estimate's assumptions are part of the estimate.
7. **Price the invisible 40%**: add explicit line items for integration per seam, review latency, deploy/migration, and a hand-off tax per cross-team dependency. If the sum embarrasses the draft date, the draft date was fiction — better to know now.
8. **Add slack as a visible line item** ("unplanned/discovered work: 20%") — hidden slack gets negotiated away; visible slack with historical justification survives (see the tradeoffs section).
9. **Set re-planning triggers**: any slice exceeding its range, any assumption in the ledger flipping, any dependency slipping a week → re-estimate the remainder *from actuals so far*, and communicate the new range immediately (see technical-writing: bad news ages badly).
10. **For fog-heavy portions**: schedule spikes with timeboxes and kill criteria instead of tasks with estimates; put a re-planning gate after each spike.

## Decision Tree

- If asked for a date before decomposition exists → give a range so wide it's honest ("2–10 weeks; I can narrow it to ±30% with two days of spike work") and buy the narrowing (see convergent-evaluation information-buying).
- If the work is novel/exploratory → don't task-plan it: spike + kill criterion + re-plan gate. If someone insists on a Gantt chart for research, the chart is the deliverable they'll get and the schedule is fiction — say so once, in writing (see technical-leadership disagree-and-commit).
- If a slice's estimate exceeds one person-week → decompose further; week-plus tasks hide unknowns at the exact granularity where they hurt.
- If the plan has a "big integration" phase near the end → restructure: pull one thread of that integration into the walking skeleton now.
- If a dependency lives in another team → treat as risk, not task: named owner both sides, committed interface date, and a fallback (mock, vendored copy, descoped slice) decided *now* (see decomposing-ambiguity cross-team seams).
- If "90% done" for two consecutive check-ins → the remaining work is not 10%; force a fresh bottom-up re-estimate of *the remainder only*, from actuals.
- If actuals are running 2× estimates by slice three → the multiplier is data about the whole plan, not bad luck about three slices; re-baseline everything and communicate (the multiplier rarely improves on its own).
- If the date is fixed (compliance, launch event) → scope becomes the only honest variable: rank slices by value, cut from the bottom, and publish what's out (see product-thinking prioritization; change-request thinking).
- If estimating someone else's work → their reference class, not yours; and their estimate, calibrated by their history — an expert's "3 days" and a new hire's "3 days" are different currencies.

## Heuristics

- Schedule the scariest integration inside the first 20% of the calendar — fear is an excellent risk-ranking signal.
- Multiply introspective estimates by your personal historical multiplier (most engineers: 1.5–3×; you find yours by checking, not guessing) — and prefer to skip introspection entirely for reference class.
- An estimate without a confidence level is a different number to every listener: say "80% confident in 2–4 weeks" and watch how differently the room plans.
- Anything estimated at "a few hours" that involves another team is a week. Anything involving a vendor is two (see async-processing vendor edges — the sandbox always lies a little).
- Count the seams: integration cost scales with pairwise-connected components, not lines of code (see system-design: coordination costs).
- Demo cadence is a plan-health metric: a project that can't demo weekly is horizontally sliced or skeleton-less, whichever — both are fixable early and fatal late.
- The first slice through any new layer costs 2–3× the later ones (setup, learning, plumbing) — front-load one slice per layer to pay this early and calibrate the rest.
- Keep estimates and targets in separate sentences: "the estimate is 6–8 weeks; the target is 5; here's the scope cut that reconciles them" — conflating them corrupts both.
- Track actuals visibly even when nobody asks — the reference-class library is built one honest retro at a time, and it's the only asset that improves your next estimate.
- Never re-promise the original date after a trigger fires by "working harder" — schedule pressure converts to defect rates and attrition at a well-documented exchange rate (see judgment-under-uncertainty speed-vs-correctness).

## Quality Checklist

- [ ] Riskiest assumptions scheduled first; the week-one work would actually invalidate-or-confirm them.
- [ ] Walking skeleton defined, scheduled first, deployed to production-like infra.
- [ ] Work sliced vertically; every slice user-visible and demoable; no layer-phases.
- [ ] Estimates are ranges with confidence levels and stated assumptions, anchored in reference-class actuals.
- [ ] Integration, review, deploy, migration, and cross-team hand-offs are explicit line items.
- [ ] Slack visible and historically justified, not smuggled.
- [ ] Every cross-team dependency has an owner, an interface date, and a fallback.
- [ ] Re-planning triggers defined; the plan has a designated re-visit cadence.
- [ ] Fog-heavy work planned as spikes with kill criteria, not tasks with estimates.
- [ ] Estimate vs target distinguished in every communication.

## Failure Modes

- **The fortune-teller plan**: task-by-task Gantt to the day, three months out, for work containing two research problems — precision cosplaying accuracy; falls apart at first contact and takes credibility with it.
- **Horizontal layering**: "data layer done" for six weeks with nothing demoable; all integration risk compounding silently at the end (the walking skeleton, skipped).
- **Introspective estimation**: happy-path imagination as schedule; the planning fallacy delivering its reliable 2–3×; retros that blame execution for what was an estimation defect.
- **The invisible 40% omitted**: typing-time estimates presented as delivery dates; review queues, environment issues, and migration eating the "slack" that was never there.
- **90% syndrome**: progress reported by task-completion feel rather than shipped slices; the last "10%" running as long as the first 90 because it *was* the second half (see first-principles component-cost fantasy — same arithmetic hole).
- **Slack laundering**: hidden padding discovered and stripped by management ("why is this 3 days?"), leaving less than honest-zero; visible, justified slack was the defensible version.
- **Trigger-blindness**: slice actuals at 2× by week three, original date still being reported upward — bad news deferred is bad news compounded (see technical-leadership: managing up).
- **Planning theater on fog**: research work forced into sprint tasks; the team "fails" sprints doing exactly the learning the project needed — the instrument was wrong, the verdict lands on the people.

## Edge Cases

- **The date that precedes the project**: sometimes the deadline arrives before the work is scoped (contract, event). The plan inverts: fixed date, ranked scope, cut-line published and re-negotiated weekly — this is a legitimate planning mode, not a failure, *if* the cut-line is honest.
- **Estimating under sales pressure**: a number said aloud in a meeting becomes a commitment somewhere else — give ranges verbally, confirm in writing, and never let the low end travel alone (see technical-writing: numbers detach from their captions).
- **The expert's curse**: your reference class isn't the team's — senior engineers estimating for juniors under-price the learning curve; use the *executor's* history (or 2× yours and say why).
- **Maintenance and interrupt load**: a team at 30% interrupt load has 70% of a calendar week — plans that ignore measured interrupt rates are wrong by exactly that rate; measure it (see sre thinking; observability) and budget it.
- **Long-tail migrations**: "migrate the users" is 95% of users in week one and the last 5% across a quarter (locked accounts, weird states, the enterprise customer with a contract clause) — plan the tail as its own phase with its own owner (see legacy-migrations: the long tail).
- **Re-estimating mid-crisis**: after a slip, the pressure is to promise recovery; the honest move is re-baselining from actuals — the multiplier that got you here is the best predictor of the road remaining.
- **Multi-quarter programs**: beyond ~a quarter, plan the current quarter in slices and the rest in named risk-retirement milestones only — detail past the fog line is fiction that costs real maintenance.
- **Estimates as anchors**: the first number spoken in a room anchors everything after; if you must estimate live, state the range *high end first*, or defer ("I'll send a range by tomorrow with assumptions attached").

## Tradeoffs

- **Planning depth vs fog density**: detail is an asset exactly as far as knowledge extends and a liability past it — plan in high resolution to the fog line, in milestones past it, and re-draw the line as it moves.
- **Risk-first vs morale-first sequencing**: attacking the scariest thing first can stall a team on a hard problem with no wins; the blend — skeleton first (a win *and* a risk-retirement), then alternate hard/satisfying — keeps both accounts funded.
- **Slice thinness vs overhead**: every slice pays fixed costs (review, deploy, QA); slices too thin drown in ceremony, too thick hide risk — one person-week is the working default, adjusted to your deploy pipeline's fixed costs (see ci-cd: cheap deploys enable thin slices).
- **Visible slack vs negotiation exposure**: visible slack invites the red pen; hidden slack corrupts your data and your integrity. Visible-with-receipts ("our last four projects ran 25% discovered work") is the defensible position — it converts negotiation into a data argument.
- **Commitment vs adaptability**: external parties need dates they can build on; the plan needs to change as knowledge lands. Reconcile with commitment tiers: hard commitments only on skeleton-verified work; everything past the fog line explicitly "planning-grade, not promise-grade."
- **Estimation effort vs estimation value**: a two-way-door task needs a t-shirt size, not a reference-class study (see convergent-evaluation door-classification) — calibrate the ceremony to the reversibility and blast radius of being wrong.

## Optimization Strategies

- Build the reference-class library deliberately: every project retro records estimate vs actual by slice *type* (integration, CRUD, migration, novel) — after three projects, your estimates come from data; after ten, they're the best in the room.
- Track your personal and team multipliers quarterly — calibration is trainable, and the feedback loop is the training (see evals: same loop, different subject).
- Standardize the skeleton: a template repo/pipeline that stands up the end-to-end slice in a day (see ci-cd; setup patterns) makes risk-first sequencing nearly free.
- Run pre-mortems on the plan (see convergent-evaluation pre-mortems): "it's three months later and we're 2× over — what happened?" The answers (that vendor, that migration, that team's review queue) become line items while they're still cheap.
- Instrument the plan like a system: burn-up by shipped slices (not task checkboxes), interrupt-rate, review-latency — the plan's observability (see observability: same philosophy, different substrate).
- Rehearse the re-baseline conversation before you need it: the team that has agreed *in advance* on triggers and the communication template ships bad news in hours, not weeks.

## Self Review

- What's the first thing this plan would learn, and is it the thing most able to kill the project?
- Where's the walking skeleton — and does it touch the integration I'm most afraid of?
- Is anything sliced by layer? What user-visible capability does week two actually ship?
- Where did each estimate come from — reference-class actuals, or imagination? What's my historical multiplier and did I apply it?
- What are the integration and hand-off line items? If they're absent, what am I claiming — that this project uniquely has none?
- Can I name each estimate's confidence and the assumption that would move it?
- What fires a re-plan, and would I actually notice it firing?
- If the target and estimate disagree, have I said both numbers out loud to the person who needs them reconciled?

## Examples

**1. The payment integration, resequenced.**
Original plan: 8 weeks — models and admin UI first, Stripe integration week 6. Risk-ranking flips it: the project's kill-condition is "our invoicing flow can't express usage-based billing in Stripe's model." Week one becomes a walking skeleton: one hardcoded customer, one real usage event, through the API to a real Stripe test invoice, deployed (see ci-cd). The skeleton surfaces it immediately: proration behavior breaks the pricing model's assumptions. Two pricing options go to product with the constraint named (see decomposing-ambiguity: essential ambiguity routed). The reshape costs three days in week one; discovered in week six it would have been a month of rework atop a sunk UI.

**2. Reference class vs the confident insider.**
Estimate requested for "SSO integration, enterprise customer." Inside view: "the library handles SAML, 1 week." Reference class from the tracker: the last three enterprise SSO integrations took 4, 6, and 5 weeks — the overrun living in *their* IdP's quirks, cert rotation, staging-tenant provisioning, and a security review each time (see authentication; the invisible 40% itemized). Estimate shipped: "4–6 weeks, 80%; 1 of those weeks is customer-side latency we don't control — it compresses only if their IT pre-provisions the staging tenant." Actual: 5 weeks. The 1-week version of this promise was made by a peer team the same quarter; that customer escalation is now *their* reference class.

**3. Fog planned as spikes, not fiction.**
"Add semantic search" (see rag) resists estimation — retrieval quality on this corpus is unknowable in advance. Instead of fictional tasks: two spikes with kill criteria. Spike 1 (3 days): embed 10k real documents, replay 50 real queries, human-judge relevance against a golden set (see evals) — kill if precision unacceptable at any chunking config. Spike 2 (2 days): latency and cost at production scale — kill if p95 or unit economics fail (see optimization-method: measure first). Both pass with data; *now* the work is plannable in slices with a reference class of one honest week. The alternative universe's Gantt chart had "build search — 3 weeks" and no kill switch.

**4. The re-baseline that preserved trust.**
Week 3 of 10: slices running 1.8× estimates (a dependency's API is lying about pagination; see api-design). Trigger fires. Re-baseline from actuals: remaining work re-priced at the observed multiplier → new range 13–15 weeks, or 10 weeks with the export slice cut. Both options shipped upward *that day* with the cause named and the scope-cut recommendation attached (see technical-writing: options-with-recommendation format). Stakeholders pick the cut; the date holds; the postmortem is boring. The counterfactual — reporting green until week 8 — is the version where trust, not just the schedule, takes the write-down.

## Evaluation Rubric

Score 1–10:

- **1–2**: Single-point dates from introspection; layer-phased plan; integration at the end; no slack; "90% done" as a status.
- **3–4**: Some slicing and padding, but risk unranked, skeleton absent, estimates rangeless, invisible 40% unpriced.
- **5–6**: Risk-first sequencing with a walking skeleton; vertical slices; ranged estimates with reference-class input on major items; dependencies owned.
- **7–8**: Full checklist: confidence levels and assumptions on estimates, visible justified slack, re-planning triggers that actually fire, fog handled with spikes and kill criteria, estimate/target kept distinct.
- **9–10**: Additionally: maintained reference-class library with measured multipliers; plan instrumented (shipped-slice burn-up, interrupt rate); pre-mortem findings visible as line items; at least one honest re-baseline shipped early enough that the *stakeholders* called the project predictable.
