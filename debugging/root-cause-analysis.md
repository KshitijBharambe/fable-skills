# Root Cause Analysis

## Purpose

Find why something is actually broken — reproduction, minimization, hypothesis discipline, binary search over code/time/data — so fixes kill bug classes instead of symptoms, and "cannot reproduce" stops being a resolution.

## When to use

- Any bug whose cause isn't obvious within the first few minutes.
- A fix was applied and the bug came back (the last "fix" treated a symptom).
- Intermittent or "works on my machine" reports.
- Post-incident: turning a mitigation into an understanding.
- Reviewing someone's proposed fix that can't explain the mechanism.

## Goals

- A reproduction exists before any fix is attempted (or the decision to proceed without one is explicit and justified).
- The final explanation predicts the evidence: it explains why it broke, why now, why in this shape, and why not elsewhere.
- The fix addresses the mechanism; a regression test pins it; sibling instances are audited.
- Time-boxed process: systematic beats heroic, and escalation criteria are known upfront.

## Inputs

- The failure report: exact symptom, when it started, frequency, affected scope (one user? one region? one build?).
- Change timeline: deploys, config changes, dependency bumps, data migrations, cert rotations, traffic shifts around onset.
- Access to evidence: logs, traces, the failing artifact/input, environment details.
- The system's expected behavior — what "correct" is, precisely (surprisingly often nobody wrote it down).

## Expert Mental Model

- **No repro, no fix — only mitigations.** Until you can make the bug happen on demand, you cannot verify any fix; you can only ship a guess and wait. Experts spend what feels like "too long" on reproduction because it converts an infinite search into a finite experiment loop. When a repro is truly impossible (one-shot production corruption), they explicitly switch modes: instrument-and-wait, or reason-from-artifacts, acknowledging the confidence downgrade.
- **Debugging is binary search, applied to whichever axis is cheapest**: bisect the *code timeline* (git bisect between last-good and first-bad), the *data* (which half of the input triggers it?), the *pipeline* (is the value already wrong at the API boundary? at the DB read? at render?), or the *configuration* (diff prod vs staging, disable half the plugins). One well-chosen split eliminates half the search space; five splits beat fifty log statements.
- **A hypothesis must be falsifiable and cheap to kill.** The discipline: state it ("the cache returns stale entries after the TTL config change"), derive a discriminating prediction ("then bypassing the cache should make it correct"), run the *cheapest* test that could kill it. Experts run experiments to *eliminate*, not to confirm — confirmation bias is the debugger's occupational disease.
- **"It can't be X" marks X as a prime suspect.** The bug lives, by definition, in the space between reality and your model of the system; the components you trust most are the least examined. Framework, compiler, and library bugs are rare — but *your assumption about how you use them* is the single richest bug habitat. When stuck, walk the assumption stack explicitly: is the code I think is deployed actually deployed? Is this the DB I think it is? Is the clock right? Is the cache off when I think it's off?
- **Distinguish trigger, root cause, and contributing conditions.** The deploy triggered it; the root cause was the unvalidated assumption in code from two years ago; contributing conditions (missing timeout, absent alert) shaped the blast radius. Fixing only the trigger (rollback) leaves the landmine; good RCA names all three and fixes at the deepest economical layer.
- **Read the error like a forensic document, not a vibe.** Bottom frame of the stack answers "where"; the frames above answer "how did we get here"; the *first* error in the log answers "what started it" (later errors are usually cascade noise). Exact wording matters: "connection refused" (nothing listening) vs "connection timeout" (network/overload) vs "connection reset" (peer died mid-conversation) point at three different worlds.

## Workflow

1. **Capture the symptom precisely**: expected vs actual, exact error text, timestamps, affected scope, frequency. "Login is broken" becomes "POST /sessions returns 500 for ~3% of users since 14:02 UTC, all on tenant shard B."
2. **Establish the timeline**: what changed around onset — deploys, configs, dependencies, data jobs, certificates, traffic patterns. ~80% of new breakage follows a change; the change list is your prior.
3. **Reproduce**: shrink toward on-demand failure — same input, same account, same environment. For intermittents, amplify (loop the operation, add load, inject latency/delays) until frequency is workable. Record the exact recipe.
4. **Minimize the repro**: binary-search away irrelevant parts (half the input, half the config, half the steps) until every remaining element is necessary. The minimal repro usually *is* the diagnosis — and it becomes the regression test.
5. **Localize with bisection**: pick the cheapest axis — git bisect across commits; trace the value across pipeline stages to find the first wrong hop; A/B environment differences. Write down what each probe eliminated.
6. **Generate hypotheses from the evidence** (not from folklore): rank by (prior probability × cheapness to test). Test the discriminating prediction of the top one. One variable at a time — parallel tweaks destroy the information each probe carries.
7. **When a hypothesis survives testing, make it predict something new**: "if stale cache is the cause, then the error rate should be exactly the cache-hit rate for shard B" — confirmed novel predictions are what separate the real cause from a coincidence that fit.
8. **Explain the full shape before fixing**: why now (trigger), why this mechanism (root cause), why this scope and not wider (conditions). Residual mysteries ("but why only shard B?") are unexploded ordnance — chase them or explicitly accept the risk.
9. **Fix the class, not the instance**: the mechanism fix + a regression test from the minimal repro + a grep/audit for sibling instances of the same pattern + (where warranted) a guardrail that makes the class impossible (type, lint, constraint, alert).
10. **Write the two-paragraph postmortem** even for non-incidents: symptom → mechanism → why the tests missed it → what now catches it. This is how team debugging skill compounds.

## Decision Tree

- If it broke recently and a change list exists → bisect the changes first (highest prior); confirm the suspect by reverting/flagging it off in isolation.
- Else if it fails deterministically for some input → minimize the input; diff a passing vs failing input; the delta names the mechanism.
- Else if intermittent →
  - Correlates with load/time-of-day → suspect resource exhaustion, timeouts, contention (see concurrency-bugs, memory-leaks).
  - No correlation visible → amplify: loop it 10,000×, inject delays at suspicious seams, run under stress; measure frequency so you can tell later whether a "fix" changed anything (a bug at 1/1,000 needs thousands of clean runs to claim victory).
- Else if it fails only in one environment → diff the environments mechanically (versions, configs, data volume, permissions, network path) — never by memory; the difference you "know" about is rarely the one that matters.
- If the value is wrong at the end of a pipeline → probe the middle: is it wrong at the DB? after the service transform? at the API response? at the client? Each probe halves the pipeline. First wrong hop = home of the bug.
- If you cannot reproduce at all →
  - Artifacts exist (logs, dumps, the corrupted row) → reason backward from the artifact: what code paths *can* produce this exact state? Enumerate and eliminate by evidence.
  - No artifacts → add targeted instrumentation at the suspected boundaries, deploy, wait for recurrence — and say honestly that status = instrumented, not fixed.
- If two hours of systematic work yields nothing → re-question the frame: is the report accurate (watch the user/repro yourself)? Is "expected behavior" actually specified? Are you debugging the right layer (the "API bug" that's a client-side cache)? Then take the walk / write the ducknote (explaining state to an imagined colleague — the act reliably surfaces the skipped assumption).

## Heuristics

- Before deep-diving, run the 5-minute cheap sweep: is it plugged in? — deployed version matches HEAD? service actually restarted? cache cleared? right environment/DB? clock sane? disk full? cert expired? An embarrassing fraction of "deep" bugs die here.
- The bug is almost never in the compiler/framework/OS. It's in your code, your config, or your understanding of the framework — in that order of prior. (When it *is* the framework, the minimal repro proves it, and that repro is your bug report.)
- One first error: in a wall of red, find the earliest timestamp — everything after is likely cascade. Fix causes, not echoes.
- Exact-match the error string into the codebase before the search engine: your own error wrapping often hides the real origin one layer down.
- When behavior contradicts the code you're reading, you're reading the wrong code (wrong version, wrong branch, wrong service, dead path, overridden config). Verify what's actually executing — add a deliberate marker (log line/version string) and confirm it appears.
- Intermittent under debugger, solid without: timing perturbation — you have a race (go to concurrency-bugs).
- Fixed by restart: state accumulation — leak, cache corruption, connection pool exhaustion (go to memory-leaks / production-debugging). "Restart fixed it" is a symptom report, not a resolution.
- The reporter's theory is data about the symptom, not about the cause — receive it warmly, verify it coldly. Same for your own first theory.
- Log the *values*, not just the arrival: "got here" tells you path; `user_id=42 plan=null expected=pro` tells you mechanism.
- Every probe you run, note what it eliminated. Unwritten debugging repeats itself after lunch.
- Time-box heroics: 30–45 min without new information → change axis (different bisection dimension), change tool (debugger ↔ logs ↔ trace), or change brain (explain it to someone).

## Quality Checklist

- [ ] Symptom precisely stated with scope, onset, frequency; "expected" behavior explicit.
- [ ] Change timeline assembled before deep code-diving.
- [ ] Reproduction on demand (or amplified to workable frequency, or explicitly declared irreproducible with instrumentation deployed).
- [ ] Repro minimized: every element necessary; recipe recorded.
- [ ] Probes changed one variable each; eliminations logged.
- [ ] Final explanation covers trigger + mechanism + scope-shape, and made at least one confirmed novel prediction.
- [ ] No unexplained residual anomalies (or each is named and risk-accepted).
- [ ] Fix targets the mechanism; regression test derived from the minimal repro is green-then-red-then-green (fails without fix, passes with).
- [ ] Sibling instances of the pattern audited; class-level guardrail considered.
- [ ] Two-paragraph writeup: why missed, what now catches it.

## Failure Modes

- **Shotgun debugging**: change three things, it works, ship it — cause unknown, so the bug returns wearing a different coat, and now the code carries three superstitious edits.
- **Symptom whack-a-mole**: null-check added where it crashed; the null's *origin* (the real bug) keeps feeding nulls to nine other consumers.
- **Confirmation-first testing**: only running experiments that would agree with the pet theory; the contradicting probe never scheduled.
- **Cascade chasing**: three hours on the OOM that was the 47th consequence of the connection leak logged at 09:01.
- **Fix-by-coincidence**: bug went quiet after a change (traffic dipped; cache warmed) — victory declared on an unfalsified guess; recurrence scheduled for the worst possible moment.
- **The un-minimized repro**: debugging inside the full 40-step scenario, drowning in variables that a 10-minute minimization would have deleted.
- **"Cannot reproduce → closed"**: the user's environment held the clue nobody requested (extension, locale, data shape); the ticket reopens at 10× volume.
- **Multi-variable probes**: toggled the flag AND bumped the version AND cleared the cache — it works now, and the information about which one mattered is gone forever.
- **Heroic memory**: six hours of undocumented probing; the same engineer re-eliminates the same suspects tomorrow.

## Edge Cases

- **Heisenbugs**: observation changes timing (debugger, verbose logging) — prefer low-perturbation evidence: counters, ring buffers, sampled traces, post-hoc dumps.
- **The bug in the test**: "code fails the test" has two suspects — validate the test against a known-good oracle before overhauling the code.
- **Two bugs interacting**: symptoms that only occur when A and B are both present resist single-axis bisection — if bisection gives inconsistent verdicts, hypothesize interaction and bisect with one suspect pinned.
- **Data-shape bugs**: only user #48,201's data triggers it (unicode, boundary length, legacy schema remnant) — diff their data against a control's; the repro is a data fixture, not a code path.
- **Time bugs**: DST transitions, month boundaries, leap days, TTL expiries — correlate onset timestamps with calendar/clock events before blaming the deploy that coincided.
- **Environment-drift bugs**: staging diverged from prod months ago (versions, extensions, kernel) — the "prod-only" bug is an environment diff wearing a mystery costume; diff mechanically.
- **Fixed-in-the-wrong-layer**: the retry you added in the client masks the server's real defect — permissible as mitigation, dishonest as resolution; track the debt.
- **Nondeterministic external dependencies**: third-party API misbehaving for a subset — your RCA ends at a well-evidenced vendor case (timestamps, request IDs, frequency), which is a legitimate root-cause terminus.

## Tradeoffs

- **Mitigate vs diagnose**: production bleeding demands mitigation first (rollback, flag off — see production-debugging), which often destroys the evidence and the failing state. Capture evidence *fast* (snapshot logs/metrics/a failing pod) before mitigating when you can do so in minutes, not hours.
- **Time-to-repro vs reason-from-code**: rare bugs may cost days to reproduce; sometimes artifact-reasoning (enumerate code paths that can produce the corrupted state) is cheaper. Choose by expected cost, but label the confidence difference: verified-by-repro beats consistent-with-evidence.
- **Depth of "root"**: five-whys can descend into "because capitalism"; fix at the deepest layer whose fix is economical and owned by you. Naming deeper causes without fixing them is still valuable (they inform risk).
- **Class-fix scope**: making the whole bug class impossible (new abstraction, type-level guarantee) is a bigger change with its own regression risk vs the surgical instance fix. Instance-fix now + class-fix as scheduled follow-up is often the honest sequencing — if the follow-up actually gets scheduled.
- **Instrument-everything vs signal clarity**: blanket debug logging drowns the next investigation and costs money; targeted, structured, removable instrumentation at boundaries preserves signal (see observability).

## Optimization Strategies

- Build the repro-amplifier toolkit once: loop harnesses, latency/fault injectors, load drivers, time-travel (fake clocks) — intermittents become 100× cheaper across every future bug.
- Make `git bisect` frictionless (fast build, seedable test env, `bisect run` scripts); a 12-commit bisect should cost minutes.
- Keep a team "bug bestiary": each nasty bug's symptom → mechanism in two lines, searchable. Half of "new" mysteries rhyme with an old entry.
- Practice the pipeline-probe pattern in calm times: know your standard taps (API boundary, queue payload, DB row, cache entry, render input) and how to read each in one command.
- Convert every RCA's minimal repro into a permanent regression test *in the same PR* as the fix — the ratchet that stops re-litigating old bugs.
- Track your own misses: when the cause turns out to be in the last place you looked, note which early assumption deferred looking there. Personal bias patterns are fixable.

## Self Review

- Can I make it fail on demand? If not, what did I decide about that, explicitly?
- What did each experiment eliminate? Could I hand my notes to a colleague and have them continue without repeating me?
- Does my explanation account for the onset time, the scope, AND the shape of the symptom? What residual anomaly am I ignoring?
- What novel prediction did the theory make, and did I test it?
- Did I change exactly one variable per probe?
- Does the regression test fail without the fix? Where else does this pattern live in the codebase?
- If this recurs in six months, what will make it a five-minute find instead of a five-hour one?

## Examples

**1. Timeline-first: the 3% login failure.**
Report: 500s on login, ~3%, started 14:02. Sweep: no deploy at 14:02 — but a config-service change at 13:58 (connection pool size lowered). Hypothesis: pool exhaustion under midday load → prediction: errors should be `TimeoutError: acquire` and correlate with concurrent-session peaks. Logs confirm both. Repro: staging + load generator at prod concurrency + new pool size → fails on demand; old size → clean. Root cause: pool sized for last year's traffic, config change merely exposed it (trigger vs cause distinguished). Fix: right-size pool + acquire-timeout alert + load test gate on pool configs. Regression test: the load scenario in CI, nightly.

**2. Pipeline bisection: the corrupted invoice totals.**
Symptom: some PDFs show totals off by cents. Probe the pipeline: DB row correct → API response correct → PDF-renderer input *wrong*. Bug is in the transform between API and renderer. Minimize: one line item with quantity 3 × $10.01 reproduces — `3 * 10.01 = 30.029999...`; a float crept in where cents-as-integers were the convention. Mechanism found by two probes and one minimal case. Class fix: money type enforced at the transform boundary (lint bans float arithmetic on `*_cents`), audit finds two sibling transforms with the same leak; regression tests pin all three.

**3. Amplifying an intermittent: the once-a-day duplicate email.**
~1/5,000 signups gets two welcome emails. Can't repro singly. Amplify: script hammers signup at 50 concurrent on staging → 12 duplicates per 10k — workable frequency. Bisect the suspects with one variable at a time: disable the retry middleware → duplicates vanish. Mechanism: client timeout at 2 s, p99 signup at 2.3 s under load → retry fires, both requests succeed; email send isn't idempotent. Root cause: missing idempotency, trigger: latency regression, contributing: aggressive timeout (see async-processing). Fix at the class level: idempotency key on signup + email dedupe constraint; the amplifier script joins CI as a soak test. Frequency math honored: 30k clean amplified runs before declaring victory.

**4. The "impossible" prod-only bug.**
Feature works everywhere except production. "It can't be the code — it's identical." Assumption walk: is the deployed artifact identical? Version endpoint says yes. Config diff: 200 lines, one suspicious — prod sets `HTTP_PROXY` for an egress gateway. Hypothesis: the new SDK ignores `NO_PROXY` for the internal service → prediction: the failing call in prod logs should show the proxy's IP. Confirmed. Minimal repro: any container with that proxy env + SDK ≥ 4.2. Vendor bug filed *with* the two-line repro; mitigation: explicit `NO_PROXY` entry; tracking issue pins the SDK until fixed upstream. The mystery was an environment diff, found mechanically, not by staring at application code — where three prior hours had been spent.

## Evaluation Rubric

Score 1–10:

- **1–2**: Fix attempted before repro; multi-variable shotgun probes; symptom patched at crash site; nothing written down; "restart fixed it" closed the ticket.
- **3–4**: Some reproduction effort; hypotheses tested but confirmation-biased; cascade errors chased; fix plausible but mechanism unverified; no regression test.
- **5–6**: On-demand repro (or honest instrumented-wait); one-variable probes with notes; bisection on at least one axis; mechanism explains most evidence; regression test added.
- **7–8**: Full checklist: minimized repro, novel-prediction confirmation, trigger/cause/conditions distinguished, sibling audit, class guardrail weighed, writeup teaches the team.
- **9–10**: Additionally: repro-amplification tooling used or built; residual anomalies zero or risk-signed; the fix demonstrably killed the class (audit found and fixed siblings); the investigation notes read as a replayable experiment log; total time bounded by discipline, not luck.
