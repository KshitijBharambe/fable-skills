# UX Fundamentals

## Purpose

Apply the general laws of usable interfaces — mental models, information architecture, cognitive load, feedback, error prevention, the usability heuristics that predate every framework — so products feel obvious to the people using them instead of obvious only to the people who built them.

## When to use

- Designing any flow, screen, or interaction — before the specialized skills (forms, dashboards, tables) take over.
- Users "don't get it": support tickets ask how to do things the UI "clearly" supports; features ship and go unused.
- Structuring navigation and information architecture for a product or a new area.
- Reviewing designs or PRs for usability, not just visuals (see visual-hierarchy for the visual layer).
- Adjudicating a UX debate that's currently being settled by whoever feels strongest.

## Goals

- Users can predict what an action will do before doing it, and verify it did that after (the gulf of execution and evaluation, both bridged).
- Navigation matches the users' mental model of the domain — findable by guessing, not by training.
- Cognitive load spent on the user's task, not on decoding the interface.
- Errors prevented by design where possible, recoverable where not (see interface-states for the error surfaces).
- UX decisions argued from principles and evidence, not taste and volume.

## Inputs

- Who the users are and what they're *trying to accomplish* — the task, not the feature request (see product-thinking; decomposing-ambiguity).
- Their existing mental models: what they use today, what vocabulary they bring, what conventions they've internalized.
- The task landscape: frequency × criticality per task — what's daily-critical vs annual-rare.
- Evidence available: support tickets, session recordings, analytics funnels, past usability findings (see research).

## Outputs

- An information architecture (navigation structure, grouping, naming) matched to user vocabulary.
- Flow designs with the interaction cost accounted: steps, decisions, inputs per task.
- A heuristic-review record: what was checked, what failed, what changed.
- Named conventions for feedback, confirmation, undo, and error handling reused across the product (see design-language for the visual twin).

## Expert Mental Model

- **Users act on their mental model, not on your implementation.** Every user carries a story of how the system works, assembled from other products, your labels, and guesswork. When the model and the system agree, the product feels "intuitive"; when they diverge, users make errors that are perfectly logical *inside their story* ("I archived it, so it's in Archive" — but your "archive" is a soft delete). The designer's job is either to match the existing model (the invoice looks like an invoice) or to *teach* the new one deliberately (see onboarding) — never to assume the implementation's model transfers by osmosis. The corollary is the curse of knowledge: you cannot evaluate your own interface's obviousness, because you already know the answer (see the testing bias below).
- **Two gulfs, one loop.** Every interaction crosses the *gulf of execution* (how do I do what I intend? — affordances, labels, discoverability) and the *gulf of evaluation* (did it work? what state is it in now? — feedback, status visibility). Most UX failures are one gulf or the other: the button that doesn't look clickable (execution), the save that gives no confirmation (evaluation — see interface-states: the feedback ladder). Walk any flow asking alternately "how would they know to do this?" and "how would they know it worked?"
- **Cognitive load is a budget; the interface spends it or the task does.** Working memory holds a handful of items; every label decoded, option compared, state remembered across screens, and convention violated spends from the same budget the user needs for their actual work. The levers: recognition over recall (show options, don't demand remembered syntax; show the previous value, don't ask them to re-know it), chunking (7 settings in 3 groups reads as 3 things), progressive disclosure (the 20% daily-use surface visible, the rest one honest step away), and consistency (a convention followed is a decision the user doesn't make — see design-language). Simplicity isn't fewer pixels; it's fewer *demands*.
- **Consistency is compound interest; conventions are free training.** Internal consistency (your product's own patterns behaving identically everywhere) and external consistency (matching platform and industry conventions — cart on the right, settings under the gear) both let users transfer learning instead of relearning. Every deviation from convention is a withdrawal: sometimes justified (your innovation is the product), usually vanity (a novel date picker is a tax on every date). Jakob's law states the economics plainly: users spend most of their time in *other* products; your interface is a dialect of a language they already speak.
- **Errors are design data, not user failure.** Slips (right intention, wrong action — fat-fingered the wrong row) want forgiving design: bigger targets (see layout-and-spacing), undo over confirmation, spacing between destructive and routine actions. Mistakes (wrong intention from a wrong model — see above) want better system-image: clearer labels, previews of consequences, status visibility. The hierarchy: *prevent* (constraints, good defaults, disable-with-explanation), then *protect* (undo, drafts, grace windows), then *recover* (error messages that say what happened, whether data is safe, what to do — see interface-states; forms). A confirmation dialog is the weakest tool in the box — habituation defeats it by the tenth appearance — yet it's most teams' only tool.
- **Frequency times criticality decides where the design effort goes.** The daily task deserves keystroke-level optimization (defaults, shortcuts, muscle-memory stability); the rare-but-critical task (billing change, data export, account deletion) deserves guidance and guardrails, not speed; the rare-and-trivial can be ugly in a menu. Uniform polish is misallocated budget (see dashboard-ux and data-tables for the specialized ends of this). And the interaction cost is measurable before any user sees it: count the steps, decisions, and inputs between intent and done — then ask which ones the *system* could absorb (see forms: every field must justify itself; the same law generalizes).

## Workflow

1. **Name the users and their top tasks**: for each — who, trying to accomplish what, how often, how bad is failure. This table is the design's constitution; every later debate appeals to it (see product-thinking).
2. **Map the users' existing mental models**: what do they use now, what words do they use, what will they *assume* your product does? Card-sorting (even informal, five users) reveals the categories they'd guess (see research: cheap evidence first).
3. **Design the information architecture from their vocabulary**: group by user task, not by org chart or database schema; name things in their words (glossary discipline — see domain-modeling: the same ubiquitous-language law, surfaced in nav labels).
4. **Sketch flows at interaction-cost granularity**: per task, list the steps, decisions, and inputs; interrogate each ("could the system default this? remember this? infer this?"); order steps so the common path is the short path.
5. **Bridge both gulfs at every step**: execution — is the next action visible, labeled in task language, and does it look like what it does? Evaluation — after acting, does the interface confirm the result and show the new state (see interface-states; motion for feedback timing)?
6. **Apply the error hierarchy**: constrain what can go wrong, default what can be defaulted, undo what can be undone (destructive actions get undo windows or soft-delete grace — see data-modeling), confirm only what can't be undone, and design the error surfaces for the rest (see forms; interface-states).
7. **Run the heuristic pass** (the ten classics compressed): status visible? system-world match? user control (undo/exit)? consistency? error prevention? recognition over recall? efficient for experts (shortcuts) without penalizing novices? minimal noise? helpful errors? help-where-needed? Twenty minutes per flow, findings written down.
8. **Test with humans who aren't you**: five users, real tasks, think-aloud, you silent — the standard finding is that 5 users surface ~80% of the problems. Watch where they hesitate; hesitation is the interface asking them to think (see research: watching beats asking).
9. **Instrument the shipped flow**: funnel completion, time-on-task, error rates, rage-clicks, support-ticket themes (see observability: product telemetry deserves the same rigor) — the evidence for iteration two.
10. **Canonize what worked**: patterns that tested well become named conventions (see design-language; component-architecture) so the next flow inherits instead of reinvents.

## Decision Tree

- If users can't find a feature → IA problem, not a feature problem: their category guess didn't match your grouping — re-sort by *their* model (card-sort data beats opinions), or add the cross-links their guesses reveal.
- If users find it but don't understand it → labeling/model problem: rename in task vocabulary; show consequences before commitment (preview, summary); check which gulf is failing.
- If users understand but err constantly → slip vs mistake: same wrong action repeatedly across users = design invites the slip (proximity, similarity, defaults); varied confusions = model mismatch, teach or rename.
- If the flow is correct but feels laborious → count the interaction cost; kill steps via defaults, inference, and remembered context; move rare options behind progressive disclosure.
- If experts want speed and novices want guidance → layer, don't average: visible guided path + accelerators (shortcuts, bulk actions, command palette) that never *replace* the visible path (see data-tables: same law for density).
- If a destructive action needs protection → undo > confirmation; if truly irreversible (see compliance-and-privacy: real deletion), make the confirmation *informative* (what exactly will be lost) and friction proportional to loss — typed confirmation for the account, not for a filter reset.
- If the team debates two designs by taste → convert to evidence: which spends less user budget (count it), which matches convention (name it), or test both with five users (see brainstorming: cheap information-buying beats argument).
- If a redesign will break existing users' muscle memory → the improvement must exceed the retraining tax across the whole user base; incremental migration with opt-in periods for big shifts (see refactoring: the same two-system economics, UX edition).
- If the "user need" arrived as a feature demand ("add an export button") → interrogate the task behind it (what do they do with the export?) before building the literal ask (see product-thinking; decomposing-ambiguity: the question behind the question).
- If accessibility, layout, or copy specifics are the open question → hand off: see accessibility, layout-and-spacing, typography — this skill decides *what the interaction is*; those govern how it's rendered.

## Heuristics

- The five-second test: show the screen cold; can a stranger say what it's for and what to do first? (See visual-hierarchy for why they can't.)
- Speak task language everywhere: "Invite teammate," not "Create user object"; menus are answers to "where would I…" questions.
- Recognition over recall, always: dropdowns over remembered codes, recent items over blank searches, previews over syntax.
- Defaults are decisions you make so users don't have to — and most users never change them; make defaults the recommendation (see forms).
- One primary action per screen; everything competing with it pays rent in user attention (see visual-hierarchy).
- Status always visible: what mode am I in, what's selected, what's unsaved, what's the system doing (see interface-states: the loading ladder).
- Undo is the feature that makes everything else feel safe — it converts exploration from risky to free, which is how users learn interfaces at all.
- Every interruption (modal, confirmation, nag) is a loan against user attention — count your modals per session and be embarrassed.
- The empty state is the first impression: teach, don't shrug (see onboarding; interface-states).
- If the interface needs a tooltip to explain a label, the label failed; if it needs a tour to explain the structure, the IA failed (tours treat symptoms — see onboarding).
- Hesitation in a session recording is a bug report: the user is paying the think-tax somewhere you didn't price.
- Latency is UX: perceived speed (instant feedback, optimistic UI, skeletons) is part of the interaction design, not an engineering afterthought (see frontend-performance; motion).

## Quality Checklist

- [ ] Top tasks named with frequency × criticality; effort allocated accordingly.
- [ ] IA matches user vocabulary and card-sort reality; findable by guessing.
- [ ] Every flow step bridges both gulfs: predictable action, visible result.
- [ ] Interaction cost counted; system absorbs what it can (defaults, memory, inference).
- [ ] Error hierarchy applied: prevention → undo → recovery; confirmations rare and informative.
- [ ] Conventions (internal and platform) followed; deviations individually justified.
- [ ] Expert accelerators layered over a novice-safe visible path.
- [ ] Heuristic pass run and recorded; failures fixed or consciously accepted.
- [ ] Tested with ≥5 real users on real tasks before major ship.
- [ ] Post-ship instrumentation confirms the flow works (completion, errors, tickets).

## Failure Modes

- **The org-chart IA**: navigation mirroring internal team structure — "Platform," "Services," "Tools" — legible to employees, gibberish to users; the support macro "click Settings, then no, the *other* settings" is the tell.
- **The engineer's mental model shipped raw**: the UI exposing the database ("Create relation," "Sync entities") — accurate, and meaningless to the human with a task (see domain-modeling: ubiquitous language exists for users too).
- **Confirmation-dialog security blanket**: every action confirmed, so no confirmation means anything; the one that mattered gets clicked through by trained reflex — while undo was never built.
- **The demo-optimized flow**: gorgeous for the salesperson's scripted path, brutal for the daily user's real one — frequency-blindness in design allocation.
- **Feature-request literalism**: the export button built as asked, the underlying task (a Monday report) never discovered — a workflow that could have been one click ships as eleven (see product-thinking).
- **Novelty tax**: custom scrolling, reinvented pickers, mystery-meat icons — every convention broken for brand "distinctiveness" is a training course the user didn't enroll in (see design-language: distinctiveness has better homes).
- **The unsupervised power user**: the design tuned to the loudest expert's requests — density and shortcuts compounding until new users bounce off entirely; the churn is invisible because the experts are the ones in the feedback channel.
- **Testing your own interface**: the team walks the flow, finds it obvious, ships; the curse of knowledge guaranteed the verdict before the walk started — five outsiders would have found the four things support will now field forever.

## Edge Cases

- **Expert-only tools** (internal ops consoles, trading, dispatch): convention-matching matters less than consistency and speed; the users are trained and daily — optimize keystrokes, density, and stability of muscle memory; but the error hierarchy matters *more* (tired experts make expensive slips — see production-debugging: 3am UX is part of incident response).
- **First-run vs thousandth-run tension**: the guidance that helps day one is noise by day thirty — design decay into the interface: dismissible teaching, progressive density, "don't show again" honored (see onboarding).
- **Cross-cultural products**: conventions diverge (reading direction, color semantics, formality of tone, date formats) — the "universal" convention is often a local one exported; validate IA vocabulary per market (see typography and color for the rendering side).
- **Interruptions and resumption**: real tasks span sessions and devices — design for abandonment and return: drafts persist (see forms), state survives, "where was I" is answered on re-entry (see interface-states).
- **The unhappy-path user**: locked out, disputing a charge, deleting a dead relative's account — flows designed under emotional load need shorter paths, plainer language, and human escape hatches; the cheerful upsell tone is a category error here (see compliance-and-privacy for the obligations that often apply).
- **AI-mediated interactions**: probabilistic outputs break the predictability contract — the evaluation gulf widens (did it do what I meant?); mitigate with previews, confidence signals, easy correction, and undo-everything (see ai-product-ux: this is its whole subject).
- **Migration of an entrenched UX**: ten thousand users' muscle memory is an asset you're proposing to burn — parallel availability, opt-in windows, and changelogs that teach (see the refactoring two-system economics; onboarding for re-onboarding).
- **Accessibility as a fundamental, not an edge**: every principle here (feedback, predictability, error recovery) has an assistive-tech dimension — the keyboard path and announcements are the same design, rendered differently (see accessibility).

## Tradeoffs

- **Simplicity vs capability**: hiding options lowers load and buries power; progressive disclosure is the standard resolution, but each layer of disclosure is a discoverability tax — put the 80% path on the surface and *test* that the 20% is findable.
- **Consistency vs improvement**: the better pattern introduced in one corner makes the product locally better and globally less predictable (see design-language: same law) — batch improvements into coherent migrations rather than dripping inconsistency.
- **Novice guidance vs expert speed**: training wheels that can't come off insult the expert; naked efficiency abandons the novice — layering (visible path + accelerators) costs double design effort and is usually worth it; when forced to choose, choose by who your users *actually are* by month three.
- **Convention vs differentiation**: matching platform patterns is free usability; your product's soul may genuinely need a signature interaction — spend deviation budget on the interactions that *are* the product, follow convention everywhere else (see design-language).
- **Friction as protection vs friction as tax**: deliberate friction (typed confirmations, cooling-off steps) protects high-stakes actions and infuriates when misapplied — price friction by irreversibility × frequency: high-stakes-rare earns it, anything frequent never does.
- **Research rigor vs shipping cadence**: five-user tests are cheap and catch most issues; full studies are slow and catch the subtle ones — match the investment to the decision's reversibility (see brainstorming: door classification applies to UX bets too).

## Optimization Strategies

- Maintain the task-frequency table as a living artifact — every nav debate, density argument, and polish allocation re-reads it; it's the UX equivalent of the churn map (see refactoring).
- Build the five-user test into the release rhythm for anything flow-shaped: recruiting from support tickets is free and finds the motivated confused (see research).
- Mine support tickets monthly by theme: each recurring "how do I…" is an IA or labeling bug with a frequency count attached — fix the interface, then watch the theme's volume (see root-cause-analysis: class thinking for UX).
- Keep a decision log of UX conventions with rationale (see technical-writing; design-language ledger) — "why undo instead of confirm here" answered once, cited forever.
- Watch real sessions quarterly, whole team: nothing recalibrates the curse of knowledge like users hesitating where it's "obvious" — the empathy is renewable and it expires.
- Prototype at the cheapest fidelity that answers the question: paper for IA, clickable for flows, code for feel (see brainstorming: cheapest discriminating test).

## Self Review

- Which user and which task is this screen for — and did I design for its actual frequency and stakes?
- Could a new user predict what each primary action does before clicking? Would they know it worked after?
- What am I asking users to remember, decode, or decide that the system could absorb?
- Where does my labeling use our words instead of theirs?
- What's the worst slip this design invites, and does it get undo or just a dialog?
- Which conventions did I break, and can I defend each deviation out loud?
- Have five outsiders used this, or have five insiders admired it?
- What will the support tickets say?

## Examples

**1. The settings sprawl, re-sorted by the users.**
A B2B product's settings: 60 options across 9 tabs organized by which microservice owns them ("Identity," "Workspace," "Platform"). Support's top macro is literally navigation directions. Fix: card-sort with 12 customers — their piles are task-shaped ("who can do what," "how we get billed," "what we get notified about"), producing 5 groups with *their* labels; a settings search added for the long tail; the three settings that account for 70% of visits (from analytics) surfaced on the first screen. Settings-navigation tickets drop 60% in a quarter; the deeper win is the team's new reflex — the next feature's placement gets decided by "where would users look" with card-sort data, not by which team built it.

**2. Undo replaces the confirmation forest.**
An ops tool confirms everything — archive, reassign, close, delete — and users click through all of it by reflex; the month's incident: a bulk-close of 400 tickets, confirmed without reading, unrecoverable. Redesign per the error hierarchy: destructive actions get a 15-second undo toast (soft-delete grace under the hood — see data-modeling: deletion semantics); bulk operations get a preview ("400 tickets match — closing affects 12 assignees") *instead* of a warning; confirmations survive only for the two truly irreversible acts, upgraded to informative ones (what exactly is lost). Modal count per session drops from 9 to 1; the next bulk mistake is undone by its author in 4 seconds, unreported — which is the design working: errors made cheap instead of scolded.

**3. The expert tool that was drowning its novices.**
A logistics dispatch console, built request-by-request for its power users: 40 columns, 200 keyboard shortcuts, dense beyond parsing — and new dispatcher onboarding takes 6 weeks with heavy churn. The frequency table reveals two populations, one interface: veterans doing 8 core tasks at speed; trainees failing to find the same 8 tasks under 32 rarely-used ones. Layering, not averaging: default view rebuilt around the 8 (visible, labeled, guided), full density one toggle away ("expert mode," sticky per user), shortcuts kept and made *discoverable* (palette with searchable commands showing their keys — recognition teaching recall). Veterans lose nothing (their toggle persists); trainee time-to-solo drops to 2 weeks. The lesson recorded: the loudest users describe *their* interface, not the interface (see product-thinking: wanted vs asked).

## Evaluation Rubric

Score 1–10:

- **1–2**: Implementation model shipped raw; IA by org chart; no feedback on actions; errors scolded, not designed; never watched a user.
- **3–4**: Conventions followed where the framework enforced them; labels in system vocabulary; confirmations as the only safety; design debates settled by seniority; testing = the team clicking through.
- **5–6**: Tasks named and flows designed against them; IA user-sorted; both gulfs checked; undo on the destructive paths; heuristic passes run; occasional five-user tests.
- **7–8**: Full checklist: interaction costs counted and shaved, error hierarchy applied product-wide, layered novice/expert paths, conventions canonized, testing and instrumentation routine.
- **9–10**: Additionally: support themes trending down because interfaces fix them at the class level; the task table and convention log are living documents the whole team cites; session-watching a standing ritual — and the product's usability demonstrably compounds: each new flow cheaper to learn because it inherits a system users already trust.
