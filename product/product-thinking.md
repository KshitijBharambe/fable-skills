# Product Thinking

## Purpose

Decide what to build and what to skip: problem framing before solutions, riskiest-assumption testing, prioritization that survives stakeholders, MVP scoping that actually tests something, and metrics that measure outcomes instead of activity.

## When to use

- Choosing what to build next (roadmap, sprint, side project).
- A feature request arrives (from a customer, exec, or your own excitement).
- Scoping an MVP or first version.
- A shipped feature isn't moving anything and nobody can say why.
- Defining success metrics for an initiative.
- Engineering-led products drifting toward "technically interesting" over "wanted."

## Goals

- Every initiative can state its problem without mentioning its solution.
- The riskiest assumption is identified and tested by the cheapest sufficient experiment.
- Prioritization is legible: inputs visible, vetoes explicit, losers told why.
- Success metrics are outcome-shaped, instrumented before launch, with kill criteria pre-committed.

## Expert Mental Model

- **Work backward from the problem, not forward from the solution.** The discipline test: state who has the problem, what pain, how often, how badly, and what they do about it today — *without naming your feature*. If the problem statement collapses without the solution in it ("users need a dashboard" is a solution wearing a problem costume), you don't have a problem yet, you have an idea shopping for justification. Ideas are cheap; validated problems are the scarce input.
- **A feature request is a problem report in disguise.** "Add an export button" encodes "I need this data in a meeting on Thursdays." Dig for the underlying job (the five-whys of product — see root-cause-analysis: same move, different domain): sometimes the real fix is smaller (a shareable link), sometimes bigger (the meeting shouldn't need the data), rarely exactly what was asked. Users are experts on their pain and amateurs on your solution space — take the diagnosis, question the prescription.
- **Past behavior is evidence; hypotheticals are noise.** "Would you use X?" invites politeness ("sure!"); "tell me about the last time you had this problem — what did you do?" retrieves facts. Expert user interviews are archaeology, not sales: concrete recent incidents, actual workarounds (a spreadsheet workaround is the strongest buy-signal that exists — someone's already paying with labor), what they've tried and abandoned, what they *paid* for. People's stated preferences and revealed behavior diverge constantly; build against the revealed.
- **The MVP tests the riskiest assumption, not the smallest feature list.** Every initiative rests on a chain of assumptions (people have this problem → they want it solved → they'll adopt our solution → they'll pay/stay). The riskiest link is usually *demand*, not feasibility — engineers de-risk the buildable part (comfortable) while the "will anyone care" part ships untested. The MVP question: "what's the cheapest thing that gives evidence on the riskiest link?" — often a landing page, a concierge/wizard-of-oz version, a prototype in five interviews, a fake-door test — before the real build (see research: timeboxed spikes; buy information before buying construction).
- **Prioritization frameworks are inputs, not verdicts.** RICE-class scoring (reach × impact × confidence ÷ effort) makes assumptions explicit and comparable — that's its entire value; the numbers are estimates wearing decimal points. Strategy retains veto power (a low-scoring bet that's the wedge into a new market; a high-scoring feature that deepens a dead-end). The failure modes are symmetrical: worshipping the spreadsheet, and HiPPO-overriding it silently. The fix for both is legibility: scores public, vetoes explicit and reasoned, losers told why (see technical-writing: decisions with rationale).
- **Metrics are proxies; treat them with proxy discipline.** One activation/north-star metric per initiative, leading over lagging (you can steer by leading indicators; lagging ones arrive post-mortem), instrumented *before* launch (retro-instrumented metrics are archaeology at best — see onboarding activation metrics). Every metric eventually gets gamed by well-meaning optimization (Goodhart) — pair each with a counter-metric (activation ↗ paired with 30-day retention ↘ catches hollow activation) and revisit when the number moves without the reality moving.
- **Pre-commit the kill criteria.** Before launch: "what result, by when, means this failed?" Written down, with a named decision date. Post-launch, sunk cost + attachment + ambiguity conspire to keep everything alive forever ("give it another quarter"); the pre-commitment is the only reliable antidote (see brainstorming: same bias, same cure). A product surface where nothing ever dies becomes a museum with a login page.

## Workflow

1. **Write the problem statement** (who / pain / frequency / severity / current workaround), solution-free. If you can't, the next step is discovery, not design.
2. **Gather evidence of the problem**: 5–8 behavioral interviews (past incidents, workarounds, spend), support-ticket archaeology, usage data on adjacent features. Weight: paid-for > built-workaround > complained > agreed-when-asked.
3. **Map the assumption chain** (problem exists → want it solved → will adopt ours → will pay/retain → we can build/serve it) and mark the riskiest link with the least evidence.
4. **Design the cheapest sufficient test** for that link (see Decision Tree): interview with prototype, landing-page signup, concierge service, fake door, scoped pilot. Define pass/fail *before* running it.
5. **Scope the first real version by the test's result**: one job done end-to-end for one persona (a vertical slice that delivers the value — see planning-and-estimation walking skeleton), with explicit non-goals written down (the feature's edges are a decision, not an accident).
6. **Define the metric set**: one success metric (outcome-shaped: "weekly teams creating ≥1 report," not "reports created"), its counter-metric, the leading indicator you'll steer by, kill criteria + decision date. Instrument before launch (see onboarding funnel discipline).
7. **Prioritize into the portfolio**: score the candidates (RICE-ish, coarse buckets over false precision), apply strategy vetoes *in writing*, sequence by dependency and risk-retirement (see planning-and-estimation), tell the losers why.
8. **Ship, then actually decide**: at the decision date, compare against the pre-committed criteria — double down (evidence strong), iterate (specific fixable gap named), or kill (criteria missed; write the learning, delete the code or sunset with a plan). "Extend the deadline" requires *new evidence*, not new hope.
9. **Close the loop on the requesters**: customers/stakeholders who fed the problem hear the outcome (built/changed/declined-with-reason) — the pipeline of good input dries up exactly as fast as requests vanish into silence.
10. **Run the portfolio review quarterly**: what did we kill, what did we learn per initiative, where did estimates vs reality diverge (see planning-and-estimation reference-class updating) — the meta-loop that improves the judgment itself.

## Decision Tree

- Testing the riskiest assumption, by which link is riskiest:
  - "Does the problem exist at scale?" → behavioral interviews + support/search data; count workarounds in the wild.
  - "Will they adopt a solution?" → landing page/fake door (measure clicks→signups against a pre-set bar), or prototype-in-interview watching them *try*, not opine.
  - "Will they pay?" → pre-orders, LOIs, pilot-with-price — anything but "would you pay?" (everyone says yes; nobody means it).
  - "Can we deliver the value?" → concierge/wizard-of-oz (humans behind the curtain) before automation; if humans-doing-it-manually can't delight users, software won't either.
  - "Can we build it?" → technical spike, timeboxed (see research/spike disciplines) — and note that this being the *least* risky link is the common case engineers invert.
- A feature request arrives:
  - Multiple independent sources + evidence of workarounds → into discovery (problem statement + evidence pass).
  - One loud voice (even a big customer) → dig for the job behind it; check who else has it; consider services/config over product surface (one-customer features are contracts wearing feature costumes).
  - Contradicts strategy → decline with the reason, log it; a pattern of declined-for-strategy requests accumulating around one theme is strategy feedback.
- Post-launch, at the decision date:
  - Metric hit + counter-metric healthy → double down (deepen, expand persona).
  - Missed, with a *named, specific* barrier discovered (onboarding cliff, missing integration) → one iteration cycle scoped to that barrier, new date.
  - Missed, no specific fixable cause → kill; write the two-paragraph learning (assumption that failed, evidence, what it implies for adjacent bets — see production-debugging postmortem shape).
- If stakeholders demand a feature you believe is wrong → cheapest-test it rather than argue: a fake door or pilot converts the argument into evidence either way (and sometimes you're wrong — the test protects against both egos).
- If everything is "P0" → the prioritization has no inputs; run the scoring pass publicly — forced trade-offs surface the real ranking that "all critical" was hiding.

## Heuristics

- The spreadsheet test: if target users maintain a spreadsheet/notion-doc/email-chain doing X manually, X has demand evidence no survey can match.
- Count the "second call": users who *follow up* about a problem unprompted are the demand signal; users who agreed in a meeting are ambience.
- Impact math sanity: reach × frequency beats intensity-for-few in most portfolios — a daily papercut for 80% of users usually outranks a weekly delight for 5% (but strategy veto applies: the 5% might be the market you're entering).
- Scope cuts before quality cuts before date slips: when the triangle squeezes, cut *whole capabilities* (clean edges, honest non-goals), never ship all of it at half-quality (see planning-and-estimation; a half-broken everything teaches users to distrust everything).
- "Fast follow" is a myth to say out loud: v1.1 arrives when v1's fires allow, which is later than anyone plans — if the cut feature is truly essential, the scope was wrong; if it can wait indefinitely, it wasn't essential.
- Beware averages of users (see dashboard-ux averages): "users want" usually means two personas wanting opposite things; segment before designing, or the feature averages into fitting no one.
- Adoption ≠ love: usage spikes from launch announcements decay; cohort retention (do week-4 users keep doing the job?) is the truth serum (see onboarding activation vs retention).
- Every feature has a permanent tax: support surface, docs, testing, migration weight, cognitive load in every future design ("what about how it interacts with X?") — price maintenance into RICE's effort, not just construction (see abstraction-and-simplicity complexity budget: same economics).
- Deletions are shipping too: removing a confusing, unused feature moves metrics more often than teams expect — the portfolio review should propose kills, not just adds.
- If the metric moved but users don't seem happier → suspect the proxy (Goodhart arriving on schedule); go watch five sessions before celebrating (see onboarding session recordings — the qualitative override).
- Write the press release / one-pager first (working-backward): if the announcement paragraph is boring or unwritable, the feature is too (cheapest possible test — it costs one page).

## Quality Checklist

- [ ] Problem statement exists, solution-free, with who/pain/frequency/severity/workaround.
- [ ] Evidence weighted by behavior (paid > built > complained > agreed); ≥5 behavioral interviews or equivalent data for significant bets.
- [ ] Assumption chain mapped; riskiest link named; test designed with pre-set pass/fail.
- [ ] MVP is a vertical slice testing that link; non-goals written.
- [ ] One outcome metric + counter-metric + leading indicator, instrumented pre-launch.
- [ ] Kill criteria and decision date pre-committed in writing.
- [ ] Prioritization inputs public; strategy vetoes explicit; declined requests answered with reasons.
- [ ] Decision executed at the date (double-down/iterate/kill) — extensions require new evidence.
- [ ] Learnings written per kill/iterate; portfolio review cadence live.
- [ ] Feature tax (support, docs, maintenance) priced into effort estimates.

## Failure Modes

- **Solution in search of a problem**: the elegant feature built because it was buildable; launch, silence, quiet removal two years later. The problem statement was never writable.
- **The feature factory**: roadmap = requests sorted by requester loudness; velocity high, outcomes flat; nobody can say what any feature was *for*, so nothing can fail, so nothing is learned.
- **Validation theater**: surveys ("87% said they'd use it!") and demo-nods standing in for behavior; the launch meets the gap between saying and doing.
- **MVP as small-mediocre-product**: the "minimum" version cut quality everywhere instead of scope somewhere — it tests nothing (users reject the jank, not the idea) and the team learns the wrong lesson.
- **Riskiest-assumption inversion**: six months de-risking the architecture for a product whose demand assumption dies in the first sales call. The comfortable risk got the budget.
- **Metric theater**: success declared on "reports created" (activity) while retention sags (outcome); or the pre-launch metric never instrumented, so success is narrated instead of measured.
- **The zombie portfolio**: nothing has kill criteria, so nothing dies; every surface is maintained forever; new work slows under the accumulated tax; the museum grows.
- **HiPPO whiplash**: the scored ranking silently overridden per-meeting by seniority; the team learns scoring is theater and stops providing honest inputs — legibility was the whole point, and it's gone.
- **One-customer capture**: the big account's requests consume three quarters; the product becomes their internal tool with a login page; the market moves on (the strategy veto existed for this).

## Edge Cases

- **B2B: buyer ≠ user**: procurement buys on the checklist, users live in the workflow — two problem statements, two metric sets (sale-ability AND adoption); features that serve only the demo eventually churn the account (see onboarding bought-not-chosen users).
- **Platform/internal products**: users are developers/teams; "revenue" is adoption and support-ticket reduction — the discipline holds (problem statements, kill criteria) even without a market (internal tools are where zombie portfolios thrive worst).
- **Zero-to-one vs optimization regimes**: pre-product-market-fit, cohort retention is the only metric that matters and most optimization is premature (see onboarding); post-fit, the machinery here (portfolio, counter-metrics) earns its keep — applying growth-stage process to a searching-stage product kills the search.
- **Regulated/contractual features**: compliance work has no adoption metric — it's priced as risk-removal (what's the exposure without it?) and exempted from the RICE queue honestly rather than laundered through fake impact numbers.
- **Deprecations as products**: sunsetting a feature needs the full treatment — affected-user evidence, migration path, comms plan, success metric (support tickets, churn among affected) — removal done carelessly torches more trust than the feature earned (see api-design deprecation mechanics).
- **Network-effect features** (marketplaces, collaboration): value arrives only at density — MVP tests must simulate density (concierge matchmaking, seeded supply) or they measure the cold-start, not the proposition.
- **Big-bet leaps** that can't be A/B'd (repositioning, platform migrations): substitute staged conviction — explicit assumption docs, pre-mortems (see brainstorming), reversibility engineering where possible, and pre-committed checkpoint reviews in place of the impossible experiment.
- **The founder/exec pet project**: sometimes it's vision, sometimes it's a zombie with sponsorship — the honest move is the same cheapest-test framing ("let's fake-door it this sprint"), which respects both possibilities (see decision tree: tests beat arguments).

## Tradeoffs

- **Speed of shipping vs depth of validation**: every validation step delays learning-by-shipping; every skipped step risks building the wrong thing thoroughly. Price by reversibility and cost: cheap-reversible features can ship as their own test; expensive-sticky ones (pricing, platform, data models) earn the full discovery pass (see planning-and-estimation when-not-to-plan — same dial).
- **Focus vs portfolio breadth**: one big bet learns fast on one question and risks everything on it; many small bets diversify and starve each under-critical-mass. The brainstorming portfolio logic applies: one bold + safe core, not five mediums.
- **User-led vs vision-led**: pure request-following produces a coherent-to-no-one product (the averaged persona); pure vision produces elegant irrelevance. The working blend: vision picks the problems worth solving; users' revealed behavior tests every solution.
- **Quantitative vs qualitative weight**: metrics scale and miss the why; sessions and interviews explain and don't scale. The override rule from both sides: a metric moving against five confused user sessions loses; a beloved-in-interviews feature with flat cohort retention also loses. Behavior at scale > behavior observed > opinion.
- **Building vs buying vs integrating**: every "should we build X" carries the unpriced alternative (partner, integrate, recommend) — the feature tax makes build the *most* expensive option more often than roadmaps admit (see system-design buy-before-build: same instinct).
- **Killing fast vs learning fully**: quick kills conserve resources and can amputate slow-burn successes (some products need cohorts to mature); the kill criteria should encode the *mechanism's* timeline (network features get density-adjusted dates), not a uniform quarter.

## Optimization Strategies

- Institutionalize the problem-statement gate: no initiative enters the roadmap without the who/pain/frequency/severity/workaround paragraph — the cheapest quality filter a portfolio can have.
- Keep a validated-problems backlog separate from the solutions backlog: problems age well (they persist until solved); solutions age badly (they assume last year's context) — prioritize from the problems side.
- Time-track discovery honestly: teams "too busy shipping to interview users" are optimizing output over outcomes by policy; 10% of capacity on discovery is the standing hedge against building the wrong thing at full velocity.
- Post-launch reviews on cadence (30/90-day against the pre-committed criteria), portfolio-wide — the ritual that makes kill criteria real rather than decorative (see ci-cd delivery retro: same loop, different layer).
- Maintain the estimate-vs-actual ledger for impact (not just effort — see planning-and-estimation): whose impact predictions calibrate well? The org's confidence weights should follow the track record.
- Watch five user sessions monthly, leadership included — the highest-information-density hour available; dashboards summarize what recordings explain (see onboarding, dashboard-ux: the qualitative loop).

## Self Review

- Can I state the problem without the solution? Who specifically has it, and what did they do about it last Tuesday?
- What's the riskiest assumption, and what's the cheapest test that could kill it — have I run it, or am I building around it?
- Is my evidence behavior or agreement? What have these users *paid* (money or labor) for this problem?
- What's the one metric, its counter-metric, and the kill criteria — written where, decided when?
- What did I decline lately, and did the requester hear why?
- What died last quarter? (If nothing: are the kill criteria real?)
- Which feature am I attached to beyond its evidence — and what would I advise someone else holding it?
- Does the effort estimate include the forever-tax, or just the construction?

## Examples

**1. The export button, dug to its job.**
Enterprise customer demands CSV export "urgently." Five-whys with the actual users: the data feeds a Thursday ops meeting; the CSV gets pasted into a slide table; the underlying job is "show the team this week's exceptions." Cheapest tests: a shareable, auto-refreshing view link (prototype in one interview — the user immediately asks "can I just present this?"). Shipped: scheduled email digest + presentable link view; CSV export deferred (two other requesters, both with the same meeting-shaped job). Outcome metric: weekly digest opens by non-login users (the meeting audience) — 4× the projected CSV usage. The request was real; the prescription wasn't.

**2. Riskiest-assumption discipline on a new product line.**
Team wants to build automated compliance reports for SMBs (6-month build). Assumption chain: SMBs feel the pain monthly (evidence: strong — support tickets, interviews with spreadsheet workarounds); they'd adopt ours (unknown); they'd pay $99/mo (unknown, riskiest — SMB willingness-to-pay is the graveyard). Tests before build: landing page with pricing + "start free assessment" (fake door): 11% visitor→email, but 0.8% past the pricing page (bar was 3%). Concierge pilot: 10 customers, reports assembled manually — at $49 they stay, at $99 seven of ten decline renewal citing budget cycles. Decision: the $99 business doesn't exist; the $49 one can't fund the build. Killed in 6 weeks for ~$8k of tests; the six-month build would have discovered the same fact for fifty times the price. The learning doc redirects the compliance expertise into an add-on for the existing product — where it ships and retains.

**3. Kill criteria, honored under pressure.**
A collaboration feature launches with pre-committed criteria: "≥15% of weekly active teams use it by day 90, or we kill it." Day 90: 6%. The pressure arrives on schedule ("the sales team mentions it in demos!", "just one more quarter"). The pre-commitment holds the line, with the honest escape hatch applied: is there a *named, specific* barrier? Session recordings show discovery is fine — teams try it once and don't return (the job wasn't weekly-shaped). No fixable barrier named → sunset with a migration note; the two-paragraph learning ("we validated wanting-to-try, never wanting-weekly; separate those tests next time") updates the team's test design permanently. Six months later, nobody misses it — including the sales team.

**4. Prioritization made legible.**
Quarterly planning arrives with 40 candidates and three VPs, everything "critical." The pass: RICE-coarse scoring (T-shirt buckets, no decimals) done openly; the top 10 by score posted; two strategy vetoes applied *in writing* ("#14 jumps the queue — it's the wedge for the mid-market motion; #3 drops despite its score — it deepens the legacy surface we're sunsetting"); the 28 losers get one-line reasons in the planning doc. Effect measured in the next cycle: stakeholder escalations drop by half (the reasons pre-empted them), and two "critical" requests quietly withdraw when their sponsors have to fill in the reach/impact columns themselves. The framework didn't decide anything; the legibility did.

## Evaluation Rubric

Score 1–10:

- **1–2**: Roadmap = loudest requests + pet projects; no problem statements; success = shipped; nothing measured, nothing killed.
- **3–4**: Some user input (surveys, hypotheticals); MVPs are small-mediocre products; metrics are activity counts; prioritization exists but is silently overridden.
- **5–6**: Problem statements and behavioral evidence on major bets; riskiest assumptions named with some cheap tests; outcome metrics instrumented; occasional honest kills.
- **7–8**: Full checklist: assumption-chain discipline, pre-committed kill criteria executed at dates, counter-metrics, legible prioritization with written vetoes, requesters closed-loop.
- **9–10**: Additionally: validated-problems backlog, discovery capacity protected, impact-estimate calibration tracked, deprecations run as products, and the portfolio demonstrably learns — kills produce written lessons that visibly redirect the next quarter's bets.
