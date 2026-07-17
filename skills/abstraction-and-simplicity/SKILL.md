---
name: abstraction-and-simplicity
description: "Use when designing an interface/module/function/schema, tempted to generalize or DRY up duplication, reviewing hard-to-name or hard-to-follow code, or judging over/underengineering — deep modules, rule of three."
---

# Abstraction and Simplicity

## Purpose

Choose the right level of abstraction and defend simplicity as an engineering discipline: name things truthfully, build interfaces deeper than their surfaces, apply the rule of three before unifying, count dependencies as complexity, and know when *not* to abstract — because complexity is the one debt every codebase pays interest on.

## When to use

- Designing any interface, module, function, or schema — the abstraction decision is being made whether or not you notice.
- The urge to generalize appears ("we might need this to support X later"), or the third duplicate of something just landed.
- Reviewing code that's hard to follow, hard to name, or hard to change — all three are abstraction symptoms.
- Choosing between adding a dependency and writing the code.
- Something feels overengineered (or underengineered) and you need better vocabulary than "feels."

## Goals

- Every abstraction earns residency: it hides real complexity behind a smaller surface (deep, not shallow), and it emerged from real instances, not prophecy.
- Names that tell the truth at the right altitude — a reader can predict behavior from the name alone.
- Complexity budgeted consciously: essential complexity (the problem's own) accommodated; accidental complexity (ours) hunted.
- Dependencies treated as long-term liabilities with interview processes, not as free candy.
- "We don't need it yet" said out loud, and honored — with the trigger for "yet" written down.

## Expert Mental Model

- **Complexity is anything that makes a system harder to understand or modify — and it compounds.** Its two species: *essential* (the problem really has 40 tax jurisdictions) and *accidental* (we chose four config systems). Its two symptoms: *change amplification* (a small behavior change requires edits in many places) and *cognitive load* (how much a reader must hold in their head to touch anything safely). Its growth law: incremental — no single commit "adds complexity"; it accretes in reasonable-looking steps until the system is feared. The expert posture is therefore *zero-tolerance in the small* (every review asks "does this pull its weight?") because there is no later checkpoint where the accretion becomes visible enough to stop (see refactoring: churn as the map of where it hurts).
- **Deep modules: small surface, big implementation.** The best abstractions hide a lot behind a little — a file API of five calls concealing buffers, permissions, devices, and caching. The worst are *shallow*: interfaces as complicated as what they wrap (the wrapper with 14 pass-through parameters, the "manager" class that just forwards). Depth is the measure: **functionality hidden per unit of interface exposed**. A shallow abstraction is negative-value — it adds a layer to learn without removing anything to know (the classic pass-through method, the config option that just relocates a decision to the caller). When you can't make a layer deep, ask whether it should exist.
- **Abstractions are discovered from instances, not predicted from imagination.** The rule of three (see refactoring rule-of-three): with one instance you know nothing about what varies; with two you're guessing; with three, the axis of variation is *visible* and the abstraction can be extracted along it. Predicted abstractions ("we'll surely need multiple payment providers") encode guesses as structure, and structure is expensive to be wrong in — the wrong abstraction is costlier than duplication because every future reader pays its comprehension tax and every future caller inherits its wrong shape. YAGNI is not anti-planning; it's epistemic humility about *which* generality you'll need — with the escape hatch that cheap-now/expensive-later insurance (an ID column, a version field in a wire format — see api-design; event-driven envelopes) is bought even before need, because *that* asymmetry is priced, not guessed (see judgment-under-uncertainty).
- **Names are the compression layer, and lying names are the most expensive bug class that never pages you.** A name is a claim: `getUser` claims a lookup — if it also creates one on miss, every reader's mental model is now wrong, and the bugs that follow are charged to "carelessness" instead of to the lie. Expert naming discipline: names state what a thing *is/does at its abstraction level* (not how — `retryDelay`, not `sleepMs`); vague names (`data`, `info`, `manager`, `util`, `process`) are unpaid design work — the struggle to name a thing precisely is the design telling you the thing has no single identity (can't name it → can't scope it → split it). Renaming toward truth is the highest-ROI refactor per keystroke (see refactoring: rename first).
- **A dependency is a hiring decision.** Every package is code you now ship, an upgrade treadmill you now walk, a security surface you now own (see security: your dependencies run with your permissions), and an abstraction you now think in — its bugs are your bugs with worse debuggability (see production-debugging: the seam you don't control). The interview: does it replace *hard* code (crypto, parsers, timezone math — adopt gratefully) or *easy* code (left-pad-shaped — write it)? Is it maintained, bounded, exit-able? For the middle ground, the thin-adapter move: wrap the dependency behind your own small interface, so the exit is a re-implementation of your adapter, not a codebase-wide migration.
- **Simplicity is a fight against defaults, not a preference.** Every force in software points toward more: more features (product), more generality (engineers' aesthetics), more layers (architecture fashion), more dependencies (velocity), more config (avoiding decisions — see the shallow-module smell). Simple systems exist only where someone repeatedly said no and paid the short-term costs: the awkward meeting, the duplicated twenty lines, the "we don't support that." The payoff compounds invisibly — in every onboarding, every debug session, every change that took an afternoon instead of a sprint (see system-design boring-tech: the same discipline at architecture scale).

## Workflow

1. **Separate essential from accidental** before designing: what complexity does the *problem* mandate (write it down — the domain's real rules; see domain-modeling), and what is everything else? The everything-else is the budget under review.
2. **Design the interface before the implementation**, from the caller's chair: write the calling code you *wish* you could write for the three most important use cases — the interface that makes those read well is the target (see api-design: consumer-first; brainstorming: design it twice).
3. **Check depth**: list what the interface exposes vs what it hides. Pass-throughs, leaked internals (see the edge cases), and config options that relocate decisions to callers all shrink depth. Can two exposed things merge? Can a default replace an option?
4. **Name everything as a truth claim**, at the interface's altitude: verbs for actions with effects, nouns for values, no lies, no vagueness. Where naming stalls, treat it as a design signal — re-scope until the name comes easily.
5. **Apply the rule of three to every generalization urge**: fewer than three real instances → write the concrete version, leave a note. Three or more → extract along the *observed* axis of variation only (not the imaginable ones).
6. **Interview every dependency** (see the mental model): hard-code replaced? health? transitive weight? exit cost? Middle-ground adoptions get a thin adapter; trivial ones get twenty lines of your own.
7. **Do the complexity accounting on the PR**: what must a reader now know that they didn't before? What change tomorrow got harder? If the answer embarrasses the feature, redesign before merging (see code-review: this is a review dimension, not an aesthetic).
8. **Write the "not-yet" ledger**: generalities considered and declined, each with the trigger that would revisit ("second provider signs → extract the interface") — the YAGNI decisions made findable, so the future extraction starts from a note instead of an argument (see decomposing-ambiguity: the not-doing list).
9. **Prune on a cadence**: dead flags, unused options, single-caller indirections, the abstraction whose three instances collapsed back to one — simplicity is maintained by deletion, not achieved by design (see refactoring: delete before you organize).

## Decision Tree

- If you're about to build for a future need → is there a concrete trigger and a priced asymmetry (cheap now, brutal later — schema versioning, ID types)? Yes → buy the insurance, minimally. No → concrete version + not-yet ledger entry.
- If two code paths look similar → resemblance or shared *reason to change*? Same reason → candidate for unification (await the third instance unless the sync-bug cost is already real). Different reasons → leave apart forever; they'll diverge (see refactoring: duplication vs wrong abstraction).
- If an interface needs many options/parameters →
  - Most callers use the same values → defaults, and demote the options.
  - Different callers genuinely differ → is this one abstraction or two wearing a trenchcoat? Split beats configuring.
  - The option relocates a decision the module should own → own it (depth over deference).
- If you can't name it cleanly → the scope is wrong: split it, merge it, or re-altitude it until the name arrives; do not ship `ProcessManager2`.
- If a layer only forwards → delete it; if it exists "for future flexibility" → ledger + delete; if it wraps a dependency as an exit hatch → that's a *thin adapter*, keep it thin (pass-through count is its health metric).
- If adding a dependency → hard problem (adopt, pin, wrap if deep-integrated — see security pinning) vs easy problem (write it) vs framework-scale commitment (that's an architecture decision with a decision doc — see technical-writing; brainstorming).
- If the design discussion says "just make it generic so we never touch it again" → that sentence has preceded most of the wrong abstractions in history; ask for the three instances.
- If simplicity and performance conflict → measure first (see optimization-method); pay complexity only at proven hot spots, and quarantine it (the fast-ugly core behind a clean interface — depth as containment).
- If the team disagrees on "too clever" → the tiebreak is the reader: can the median maintainer (not the author) predict behavior and make the next change safely? Author pride is not a criterion (see code-review).

## Heuristics

- Depth test in one line: if explaining the interface takes as long as explaining the implementation, the module is shallow.
- Count what a change touches: one concept changed → ideally one place edited; the N-file rename for one behavior shift is change amplification announcing itself (see refactoring shotgun surgery).
- Different things should look different: near-identical names/shapes for different semantics (`userId: int` vs `accountId: int` both passed as bare ints) invite the transposition bug — make the type system carry the difference where it's cheap.
- Errors out of existence where possible: the API that can't be called wrong (unsubscribe that's idempotent, ranges that clamp) beats the one that documents its landmines (see api-design; interface-states for the UX twin).
- Comments explain *why*, code explains *what*: the comment that paraphrases the line is noise; the one that carries the constraint the code can't show ("vendor rate-limits at 10/s, hence the queue") is load-bearing (see the codebase's comment discipline).
- Prefer functions over frameworks, data over machinery: the config-driven rules engine with two rules is a `switch` statement with a mortgage.
- Twenty boring lines beat one clever one that needs a comment, a test, and a legend.
- "Util", "helper", "common", "misc" are junk drawers — code lands there when nobody did the naming work; each one grows monotonically until someone splits it by *reason to change*.
- The adapter you write around a dependency should be embarrassingly small — when it starts having opinions, you're building a framework around a framework.
- Generality has a smell in the signature: unused parameters, `options: object`, callbacks nobody passes — the imagined futures, visible as API scar tissue; prune them.
- When stuck between two designs, pick the one that's easier to *delete* — reversibility is simplicity's best friend (see judgment-under-uncertainty doors).

## Quality Checklist

- [ ] Essential vs accidental complexity named; the accidental has a justification or a removal plan.
- [ ] Interfaces designed from the caller's chair; the top use cases read cleanly.
- [ ] Modules are deep: surface small relative to what's hidden; no pass-through layers.
- [ ] Every name is a true claim at the right altitude; no vague or lying names shipped.
- [ ] No abstraction from fewer than three instances (or a written asymmetry argument for the insurance).
- [ ] Dependencies interviewed; middle-ground ones wrapped in thin adapters; trivial ones written instead.
- [ ] PR-level complexity accounting done: reader burden and change amplification checked.
- [ ] Not-yet ledger updated with declined generalities and their triggers.
- [ ] Something was deleted or simplified this cycle — the pruning cadence is alive.

## Failure Modes

- **The wrong abstraction, compounding**: unified from two instances on resemblance; flags accrete as reality diverges; every caller now pays every other caller's complexity — and un-abstracting is nobody's ticket (see refactoring: premature unification; the fix is inline-back-and-resplit).
- **Shallow layer sediment**: service → manager → handler → helper, each forwarding with slight renames — four files to trace one behavior; architecture as geology, each stratum a fashion that passed.
- **Speculative generality**: the plugin system with one plugin, the multi-tenant flag for one tenant, the abstract factory for a class with one implementation — imagined futures shipped as present-tense costs (YAGNI's whole case).
- **The lying name**: `validateOrder` that also *saves*; `cache.get` that fetches on miss with a 3s timeout; `isReady` with side effects — every reader's model wrong, every resulting bug misattributed (see production-debugging: the mental-model bug).
- **Config as decision-laundering**: every hard design choice deferred to a config option — the module ships with 40 knobs, callers must understand the internals to set them, and depth is zero (deference dressed as flexibility).
- **Dependency candy**: 20 lines saved, 400 transitive packages adopted; the graph nobody reviews becomes the attack surface and the upgrade treadmill (see security: the maintainer account that gets phished is now in your build).
- **Clever-author code**: the point-free triple-nested combinator that took a day to write and takes everyone a day to read — optimization for the writer's satisfaction over the reader's Tuesday (the median-maintainer test, failed).
- **Simplicity theater**: "simple" as an excuse for missing essential complexity — the domain really does have 40 jurisdictions, and the "clean" design that models 3 ships corruption, not elegance (essential complexity denied is a bug farm; see domain-modeling).

## Edge Cases

- **Leaky abstractions under load**: the clean interface whose performance cliff exposes the implementation (the ORM's N+1, the network call behind a property getter — see postgres; frontend-performance) — depth includes *cost honesty*; interfaces that hide an order of magnitude belong on the suspect list, and hot-path callers deserve interfaces that show the price.
- **Abstraction boundaries vs failure boundaries**: hiding *where* something runs (local vs network) hides *how it fails* — retries, timeouts, and partial failure can't be abstracted away without lying (see system-design: the fallacies of distributed computing; async-processing). At failure seams, less abstraction is more truth.
- **The DSL threshold**: internal DSLs and codegen buy expressiveness and cost every future debugger a second language (see debugging through generated frames) — the threshold is team-scale and problem-permanence, not author enthusiasm.
- **Cross-team interfaces ossify instantly**: the "we'll iterate on it" internal API becomes a contract the moment a second team calls it (see api-design: publishing is forever-ish) — spend the design care *before* first external caller, because the rule of three doesn't get to run retroactively on a public surface.
- **Test code counts**: DRY applied to tests (clever shared fixtures, parameterized meta-tests) optimizes the wrong variable — tests are read in isolation at 2am; a little duplication that keeps each test self-evident beats a fixture archaeology dig (see testing-strategy: tests are documentation).
- **Generated and vendored abstractions**: the codegen'd client with 200 methods you didn't design — wrap the 6 you use behind your own interface; your codebase should speak your domain's vocabulary, not the vendor's (see refactoring: the same adapter logic).
- **When duplication is the design**: deliberately duplicated logic across failure domains (two independent validators — see security belt-and-braces) or across teams that must not couple (see system-design service boundaries) — DRY's jurisdiction ends where independence is the requirement.
- **The senior-junior asymmetry**: abstractions legible to their author's experience level can be walls for the team's actual distribution — calibrate to who maintains it, and treat "only Dana can touch that module" as a failed depth test, however elegant the module (see technical-leadership bus factor).

## Tradeoffs

- **Duplication vs coupling**: DRY reduces sync-bugs and creates shared fate (every caller moves when the shared thing moves); duplication isolates and drifts — arbitrate by *reason to change* (shared reason → unify at three; different reasons → duplicate proudly) and by blast radius of the coupling.
- **Depth vs discoverability**: deep modules hide machinery, and sometimes a newcomer *needs* to see the machinery to trust or debug it — the resolution is layered disclosure (clean surface + excellent internal docs + observable internals; see observability), not a shallower interface.
- **Flexibility vs decisiveness**: every option you add serves one caller and taxes all readers; every decision you make on callers' behalf risks being wrong for someone — default to deciding (depth), escape-hatch rarely, and count options as debt.
- **Insurance vs YAGNI**: some generality is cheap now and brutal later (wire-format versioning, ID width) — buy it; most is expensive now and unneeded later — decline it; the discriminator is the priced asymmetry, not the vividness of the imagined future (see judgment-under-uncertainty: name the odds and the costs).
- **Clever vs boring**: the clever solution is sometimes genuinely 10× shorter/faster — pay for it only where the win is measured, quarantine it behind a boring interface, and document the trick where it lives (see optimization-method: complexity spent only at proven hot spots).
- **Consistency vs fit**: matching the codebase's existing pattern keeps the whole legible even when a locally-better pattern exists — diverge only with a migration intention (see refactoring: new patterns need a plan, or they're entropy; design-language for the visual twin).

## Optimization Strategies

- Institutionalize the caller-first design habit: every new interface PR opens with "here's the calling code for the top three use cases" — the cheapest design-review artifact and the fastest shallow-module detector (see brainstorming: design it twice).
- Track the junk-drawer metric: size and growth of `utils/`, `helpers/`, `common/` — quarterly splits by reason-to-change keep the unnamed-design backlog visible (see refactoring churn maps).
- Run un-abstraction reviews alongside abstraction ones: the quarterly hunt for flag-grown unifications, single-implementation interfaces, and pass-through layers — deletion candidates surface reliably once someone looks (see refactoring: practice un-abstracting).
- Keep the dependency budget explicit (see security): additions need an interview note; the graph's growth rate is reviewed like a cost line — because it is one.
- Make the not-yet ledger a living doc that planning actually reads (see planning-and-estimation): declined generalities with triggers become one-line lookups when the trigger fires, converting "I told you so" into "here's the note."
- Teach depth with the team's own code: the internal workshop that walks one shallow module → deep redesign end-to-end beats any style guide — vocabulary ("shallow," "change amplification," "lying name") shifts reviews more than rules do (see code-review shared standards).

## Self Review

- What here is essential to the problem, and what did I add — and can I defend each addition to a reader who pays its tax?
- Would the calling code I *wish existed* match the interface I built? Did I ever write that wish down?
- Is each module hiding more than it exposes — or am I shipping corridors between rooms?
- Do my names make claims a reader can bank on? Which name did I settle for because the honest one wouldn't come — and what design problem is that hiding?
- Which abstraction did I build from imagination rather than instances? What are its three instances, really?
- What did this PR make harder to change? What must a maintainer now know that they didn't?
- Which dependency did I adopt this month, and did it get an interview or a shrug?
- What did I delete recently? If nothing — what's accreting while I'm not looking?

## Examples

**1. The notification "platform" descoped to a function.**
Ticket: send a Slack message when a job fails. The design that almost shipped: a `NotificationService` with pluggable channels, template registry, retry policies, and a config schema — for one message to one channel (speculative generality, textbook). What shipped instead: a 30-line `notifySlack(message)` with the vendor call behind it, plus a not-yet ledger entry: "second channel or second message-shape → extract channel interface." Eight months later email lands (trigger fires); *now* there are two real instances, and the extraction takes an afternoon along the observed axis (transport varies; formatting mostly doesn't — the opposite of the original design's guess, which had made formatting pluggable and hardcoded transport). The wrong abstraction was avoided by waiting for the evidence.

**2. Depth by decision: the upload module that stopped asking.**
A file-upload module exposes 11 options (chunk size, retry count, backoff, mime-strictness, temp-dir…) — every caller copy-pastes the same incantation from the one team that read the source (config as decision-laundering; zero depth). Redesign from the caller's chair: the wished-for call is `upload(file)` — so the module *owns* the decisions: chunking adaptive to file size, retries with sane backoff (see async-processing), mime checked by content (see security file lies). Surface shrinks 11 options → 2 (an optional progress callback, an optional privacy flag — the two things callers *genuinely* differ on). The diff deletes 40 lines of every caller and one wiki page of incantation lore. Depth up, cognitive load down, and the module finally has behavior worth testing once instead of per-caller.

**3. The lying name, invoiced.**
An incident (see production-debugging): duplicate charges under retry load. Root cause chain ends at a name — `getOrCreateSession` was refactored months ago to *also* extend session expiry (a write), but callers kept treating it as a read: safe to call twice, safe to call in the retry path. The behavior change was reviewed; the *name* wasn't — so every caller's mental model quietly went stale (the lie, compounding). Fixes at three altitudes: the immediate bug (idempotency key on the charge path — see async-processing), the class (rename to `touchSession`, and a review-checklist line: *does the name still tell the truth after this diff?* — see code-review), and the instinct: names audited as claims, in the same pass as logic (see root-cause-analysis: fix the reason the review missed it).

**4. Write vs adopt, decided twice, correctly both times.**
Same sprint, two urges. (a) Date-range arithmetic for a report ("just add the date library" — 60 transitive packages): the actual need is "start/end of month, UTC" — 25 lines with tests, written; the interview verdict was *easy problem, heavy dependency* (see security dependency budget). (b) Timezone-aware recurring schedules ("how hard can it be?"): the interview goes the other way — DST transitions, leap seconds, locale rules; this is the *hard* pile where confident hand-rolls become CVE-adjacent folklore — the mature library is adopted, pinned, and wrapped in a thin adapter exposing the three calls the product needs in domain vocabulary (`nextRunAfter(schedule, t)`), so the exit, if ever needed, is one file. Two opposite conclusions, one method: interview the problem's hardness, not the package's popularity.

## Evaluation Rubric

Score 1–10:

- **1–2**: Abstractions from prophecy; shallow layer sediment; junk-drawer modules; lying and vague names; dependencies adopted by reflex; nothing ever deleted.
- **3–4**: Some naming care and occasional YAGNI, but pass-throughs unchallenged, options accrete, rule of three unknown, complexity accounting absent from review.
- **5–6**: Caller-first interfaces on new work; depth checked; rule of three applied; dependencies interviewed; names treated as claims; a not-yet ledger exists.
- **7–8**: Full checklist: essential/accidental separation explicit, PR-level complexity accounting routine, thin adapters on middle-ground dependencies, pruning cadence alive, insurance-vs-YAGNI decided by priced asymmetry.
- **9–10**: Additionally: un-abstraction practiced as routinely as abstraction; junk-drawer and dependency-growth metrics tracked and trending right; the team's review vocabulary carries the concepts (depth, amplification, lying names); and the codebase shows the receipts — modules a new hire can predict from their names, and at least one celebrated deletion per quarter.
