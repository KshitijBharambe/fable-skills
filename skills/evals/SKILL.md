---
name: evals
description: "Use when building any LLM feature, deciding whether a prompt/model/pipeline change actually improved things, calibrating an untrustworthy LLM-judge, or gating LLM changes like CI — assertions, judges, human review."
---

# Evals (LLM Evaluation)

## Purpose

Replace vibes with measurement in LLM systems: build eval suites from real cases, layer cheap assertions under calibrated LLM-judges under sampled human review, and gate every prompt/model/pipeline change the way CI gates deploys.

## When to use

- Building any LLM feature (evals start with the feature, not after it).
- Deciding whether a prompt change, model swap, or pipeline redesign actually improved things.
- Users report quality issues that dashboards can't see.
- An LLM-judge's scores feel untrustworthy (they probably are, uncalibrated).
- Comparing architectures (RAG configs, agent designs — see rag, agents) with money on the line.

## Goals

- A living eval suite of real cases gates changes; regressions are caught pre-ship, not post-complaint.
- Metrics are layered by cost: deterministic checks → LLM-judge → human gold, each trusted to its calibrated limit.
- Scores slice by case type; no single aggregate hides a regression.
- The failure→case flywheel runs: every production miss becomes a labeled case within days.

## Expert Mental Model

- **No evals = vibes engineering.** Without a fixed case set, every change is judged on three cherry-picked examples and recency bias; improvements to case A silently trade against case B; arguments are settled by seniority instead of data. The eval suite is to LLM systems what the test suite is to code (see ci-cd) — the difference is that LLM changes are *always* behavioral changes, so shipping without evals is shipping every PR without running tests.
- **Start tiny and real; grow by failure.** 20–50 real cases on day one beats 500 synthetic ones in month three. Synthetic cases test what you imagined; real cases (from support logs, user sessions, stakeholder interviews) test the distribution that exists. The flywheel is the engine: production failure observed → labeled and added → fix verified against it → regression-guarded forever. A mature suite is an archaeology of every bug you've ever had — exactly like a good regression test suite (see root-cause-analysis: same ratchet).
- **Layer the judges by cost and trust**: (1) *deterministic checks* — schema validity, required fields, length bounds, citation-present, forbidden-content regex: free, instant, unarguable; run on everything, always. (2) *LLM-as-judge* — rubric-scored quality dimensions (faithfulness, relevance, tone): cheap enough for every change, but only as trustworthy as its calibration. (3) *Human review* — gold labels, sampled: expensive, slow, ground truth. The failure is using layer 2 where layer 1 suffices (paying for judgment on checkable facts) or trusting layer 2 without layer 3 ever auditing it.
- **An uncalibrated judge is a random number generator with confidence.** LLM judges carry biases: position (prefers first/last option), verbosity (longer = "better"), self-preference (favors its own model family's style), sycophancy toward confident tone. Calibration = measure agreement with human labels on a sample (aim for agreement comparable to human-human agreement on the same task); fix disagreement with sharper rubrics (binary/few-level scales beat 1–10; per-dimension beats holistic); re-calibrate when the judge model or rubric changes. A judge you've never calibrated is a vibe wearing a lab coat.
- **Slice or be fooled.** Aggregate score 82→84 can hide: lookup questions +6, refusal handling −9. LLM systems regress *per case type* (see rag typed evals); the dashboard must show slices (by task type, difficulty, language, tenant tier) or improvements will be quietly cannibalistic. Corollary: pin every eval run to versions (prompt, model, pipeline, index) — an eval number without its version tuple is gossip.
- **Statistical honesty at small n.** With 30 cases and nondeterministic outputs, a 2-point delta is noise: run multiple trials where variance exists, compare *paired* per-case results (which cases flipped, and why) rather than aggregate deltas, and read the flipped cases — at eval scale, the qualitative read of 10 diffs beats the quantitative read of one average. Growth cures this; pretending it away ships coin-flips as wins.
- **Offline evals bound quality; online signals reveal it.** The suite says "not worse on what we know"; production says what users actually experience — thumbs, edits, retries, abandonment, escalations (see ai-product-ux feedback capture). The two loops close into one system: online signals source new offline cases; offline gates protect what online discovered.

## Workflow

1. **Define what "good" means, in writing**: the task's quality dimensions (correctness, faithfulness-to-source, completeness, tone, format), each with a one-line description and 2–3 anchor examples of pass/fail. Undefined "quality" produces judges that measure nothing (see technical-writing: same discipline — criteria before critique).
2. **Collect 20–50 real cases**: from production logs, support tickets, user interviews; deliberately include edges (empty, ambiguous, adversarial, out-of-scope — see rag out-of-corpus cases). Label each: input, expected output or expected *properties*, case type.
3. **Wire the harness**: run all cases against the system, output per-case results + per-slice scores, diffable between runs, pinned to the version tuple (prompt@x, model@y, pipeline@z). Make it one command — friction determines whether it's actually used (see ci-cd: the 10-minute rule's cousin).
4. **Implement layer 1 (deterministic)**: schema/parse validity, required elements, bounds, forbidden patterns, citation presence, latency/cost per case. These run on every change forever and catch the embarrassing class free.
5. **Build layer 2 (LLM-judge) per dimension**: binary or 3-level rubric per dimension (not holistic 1–10); the rubric includes anchor examples; judge sees the *criteria*, the input, the output (and source docs for faithfulness); mitigate biases (randomize positions in comparisons, cap length effects by instruction, judge model ≠ generator model where self-preference risks).
6. **Calibrate layer 2 against layer 3**: humans label 30–50 outputs on the same rubric; measure judge-human agreement; iterate the rubric until agreement ≈ human-human; record the calibration number next to every judge score it produces. Re-calibrate on judge/rubric changes and quarterly drift checks.
7. **Gate changes**: prompt/model/pipeline PRs run the suite; the diff report shows per-slice deltas + flipped cases; regressions block or get explicitly accepted in writing (see ci-cd gates — identical ceremony).
8. **Run the flywheel**: weekly triage of production signals (flags, corrections, escalations — see ai-product-ux) → new labeled cases → the suite grows where reality disagrees with it. Retire cases that no longer represent the product (with the same ceremony as adding).
9. **Add online measurement for launches**: A/B on the real metric where feasible (task completion, edit distance, retention — not thumbs alone); staged rollouts watch the correction-signal monitors (see ci-cd canary; ai-product-ux trust metrics).
10. **Audit the auditors quarterly**: sample judge-scored outputs for fresh human review (drift check); re-read the dimension definitions against what the product now is; prune, re-anchor, re-calibrate.

## Decision Tree

- Choosing the measurement for a property:
  - Mechanically checkable (format, presence, bounds, exact match for closed answers) → deterministic check. Never pay a judge for what a regex knows.
  - Judgment-requiring but rubric-describable (faithful? relevant? on-tone?) → calibrated LLM-judge, per-dimension, binary/3-level.
  - Taste-level or high-stakes (medical accuracy, legal soundness, brand voice at launch) → human review; judges only pre-filter.
- If two variants must be compared (prompt A vs B, model X vs Y) → paired comparison per case (same inputs), position-randomized if judge-ranked; read the flips, not just the delta.
- If the eval score and user complaints disagree → trust the complaints, audit the suite: coverage gap (complained-about cases missing → add them), rubric gap (dimension unmeasured), or judge miscalibration (re-run calibration). The suite is a model of quality; reality outranks the model (see product-thinking: metrics are proxies).
- If a metric like BLEU/ROUGE/embedding-similarity is proposed for open-ended generation → almost always wrong (they measure token overlap, not quality); use them only where reference-closeness genuinely IS the task (translation-ish); otherwise rubric-judge.
- If n is small and the delta is small → run k trials, paired stats, and read flipped cases; if still ambiguous, the honest answer is "no detectable difference — decide on cost/latency instead."
- If the suite passes but you're still nervous → your nervousness knows about cases the suite doesn't; write them down as cases (nervousness is unlabeled domain knowledge).
- If evals are proposed *after* launch to justify a decision already made → that's not an eval, that's a press release; the gate only works前 pre-decision (see brainstorming/convergent-evaluation: criteria before options — same bias, same cure).

## Heuristics

- Real > synthetic; recent > old; failed > passed: when sampling cases to add, production failures are worth 10× synthetic successes.
- Binary rubrics ("does the answer contain claims absent from the source? Y/N") calibrate far better than scales ("rate faithfulness 1–10") — judges and humans agree on lines, not gradients.
- Per-dimension judging beats holistic: one "overall quality 7/10" hides which dimension failed; four binary dimensions localize the fix.
- The judge prompt is a prompt (see prompt-engineering): spec'd, structured, versioned, eval'd — yes, the judge has evals (its calibration set).
- Cost-shape the suite: deterministic on all cases every run; judge on all cases every change; humans on samples every quarter + every calibration. If judging costs make you skip runs, the suite is mis-shaped, not too big.
- Keep a "golden dozen": the 12 cases that best represent the product's soul, reviewed by a human on every significant change even when everything's green — the smoke test's cousin (see ci-cd).
- Track eval-suite metrics about itself: case count by type, last-added date, flywheel latency (production failure → case added), judge calibration score — a suite nobody feeds is a suite that's quietly dying.
- Never let the generator grade its own homework unaudited: same-model judging inflates; different-family judges or human anchors keep it honest.
- Latency and cost are eval dimensions: a 4-point quality win at 3× latency is a product decision, not an automatic ship (see ai-product-ux latency honesty) — the report shows all three.
- Version-pin everything in the run record; "the eval improved" without the tuple is unfalsifiable (see prompt-engineering versioning).
- When a case is contested (team disagrees on the expected output) — that's not an eval problem, that's an unmade product decision surfacing; escalate it as one (see decomposing-ambiguity).

## Quality Checklist

- [ ] Quality dimensions defined in writing with pass/fail anchors.
- [ ] ≥20–50 real cases, typed, including edges/adversarial/out-of-scope; labels versioned.
- [ ] One-command harness; per-slice scores; paired diffs between runs; version-tuple pinning.
- [ ] Layer 1 deterministic checks on everything (schema, bounds, forbidden, citations, latency, cost).
- [ ] Layer 2 judges: per-dimension, binary/few-level, bias-mitigated, calibration number recorded.
- [ ] Layer 3 human gold: calibration sets + quarterly drift audits + golden-dozen reviews.
- [ ] Changes gated: eval diff attached to prompt/model/pipeline PRs; regressions blocked or signed.
- [ ] Flywheel running: production signals triaged to cases weekly; flywheel latency tracked.
- [ ] Online metrics wired for launches (task-level, not thumbs-only); staged rollouts monitored.
- [ ] Statistical honesty: multi-trial where nondeterministic, flipped-case reads, "no detectable difference" allowed as a verdict.

## Failure Modes

- **Vibes with extra steps**: a suite exists but isn't run on changes ("we ran it last month") — the regression ships anyway; the suite was decor. Gate or it didn't happen (see ci-cd: same law).
- **Synthetic-only suites**: 300 GPT-generated test questions, all grammatical, none like real users — production distribution (typos, fragments, mixed languages, weird intents) never measured; the suite certifies a product nobody uses.
- **The uncalibrated judge**: "faithfulness 92%" from a judge never checked against humans; a rubric tweak later it's 97% and nothing changed — numbers moving without meaning, decisions built on sand.
- **Aggregate blindness**: overall +2 celebrated; refusal-handling slice −12 unnoticed; three weeks later the "hallucination incident" that the slice predicted (see rag metric monotheism).
- **Reference-metric misuse**: ROUGE optimized on summaries → the system learns to parrot source sentences; the metric was never measuring quality, and now the system optimizes the confusion.
- **Judge self-preference**: model X judging model X vs Y "prefers" X; the architecture bake-off was rigged by family loyalty; nobody randomized or cross-checked.
- **Overfitting to the suite**: months of tuning against the same 40 cases — the suite is memorized (implicitly via prompt tweaks targeting specific cases); held-out cases or fresh production sampling is the tell (score gap suite-vs-fresh).
- **Contested labels papered over**: half the team thinks case #23's expected output is wrong; it stays; every run's score carries a ±1 argument — the unmade product decision taxes every measurement (see decomposing-ambiguity).
- **Flywheel rust**: launch-week suite never grows; a year later it measures the product's fossil record; new failure modes have no cases, old cases test removed features.

## Edge Cases

- **Nondeterministic outputs**: temperature >0 or model-side variance → k-trial runs with per-case pass rates; a case passing 3/5 is information (fragility), not noise to round.
- **Multi-turn/conversational evals**: single-shot cases miss context-carrying failures — script conversation cases (fixed turns) for regressions + simulated-user evals (an LLM plays the user) for exploration, holding the simulator's version pinned like everything else.
- **Agent/trajectory evals**: many valid paths to done → evaluate end-state outcomes and invariants (task success, budget respected, no forbidden actions) not step imitation (see agents outcome-evals); log-derived checks ("did it verify before declaring done?") supplement.
- **Long-output evals** (reports, documents): holistic judging degrades over length — decompose: per-section rubric dimensions, claim-extraction + faithfulness per claim, structure checks deterministic (see rag citation audits).
- **Subjective dimensions** (humor, creativity, brand voice): human panels with forced-choice pairwise beat any judge; keep the judge for pre-filtering only, and accept wider error bars.
- **Privacy in eval sets**: real cases carry PII — scrub/pseudonymize at case-creation (the suite is a data store with retention rules; see observability PII discipline); synthetic stand-ins only where scrubbing destroys the case's point.
- **Eval-set leakage into prompts**: few-shot examples drawn from the eval set = testing on the training set, prompt edition — partition (example pool ∩ eval pool = ∅) and check on every prompt change (see prompt-engineering examples).
- **Regulated domains**: "the judge said it's fine" is not a compliance answer — human sign-off paths and audit trails are eval-system requirements, designed in (see ci-cd compliance environments: same pattern).

## Tradeoffs

- **Suite size vs signal freshness**: big suites detect small deltas and cost per run; small suites iterate fast and miss subtle regressions. Resolve by tiers: fast core (golden dozen + deterministic on all) per change, full suite per merge/nightly (see ci-cd stage ordering — the same fail-fast shape).
- **Judge quality vs cost**: strongest judge model on every case × every change is real money; calibrate a cheaper judge against the strong one + humans, reserve the strong judge for disagreements and audits (model-tier routing for judges — see agents).
- **Rubric strictness vs judgment room**: hyper-specific rubrics calibrate well and miss unanticipated quality dimensions; loose rubrics see more and agree less. Per-dimension binary rubrics + a free-text judge "notes" field (mined for new dimensions quarterly) covers both.
- **Offline coverage vs online truth**: more offline investment delays launches; more online reliance means users find your regressions. High-blast features front-load offline; low-stakes surfaces can lean on staged rollouts + monitors (blast-radius pricing — see ci-cd canary tiers, ai-product-ux consequence classes).
- **Automation vs human touch**: full automation scales and drifts; humans anchor and don't scale. The calibration-and-audit loop *is* the tradeoff resolution: automation does volume, humans do truth, on a schedule.

## Optimization Strategies

- Mine online signals as pre-labeled cases: user edits (the correction is the label), escalations, thumbs-with-comments — cheapest high-quality case source (see ai-product-ux correction stream).
- Build the diff-reading habit: every eval run's report leads with flipped cases (regressed + fixed), not the aggregate — ten minutes of reading flips finds the mechanism the average hides (see root-cause-analysis: read the evidence).
- Hard-case mining: cases where k-trial pass rate is 40–80% are the frontier — tuning against them moves real capability; cases at 0% or 100% teach nothing per run.
- Rotate a held-out set: refresh 20% of cases quarterly from fresh production sampling; the suite-vs-fresh score gap is your overfitting meter.
- Make eval reports legible to non-engineers (slices, trends, example flips with before/after) — evals become the shared language for "is it better," which is what ends the vibes meetings (see technical-writing: audience first).
- Invest in eval tooling proportional to iteration rate: teams tuning prompts daily need one-command, <5-minute suites (see prompt-engineering iterate step); the harness IS the velocity.

## Self Review

- If I shipped this change right now, what number tells me tomorrow whether it regressed — and would anyone look?
- What fraction of my cases came from real usage? When did the suite last grow from a production failure?
- What's my judge's agreement with humans, measured when, on how many labels?
- Which slice is worst right now, and does my current work target it?
- Are any wins I've claimed within noise (single trial, small n, unpaired)?
- Do my few-shot examples leak into my eval set?
- Which contested labels am I tolerating instead of escalating as product decisions?
- If a stakeholder asked "is it better than last month," could I answer with a version-pinned diff — or a feeling?

## Examples

**1. Day-one suite for a support summarizer.**
Before writing the prompt (see prompt-engineering workflow): dimensions defined — coverage (key issues present: judge, binary per issue), faithfulness (no claims absent from thread: judge, binary), format (schema+length: deterministic), tone (3-level judge). 35 real threads sampled across types (billing, bug, angry-customer, multi-issue, one-liner). Harness: one command, per-type slices, version-pinned. First calibration: judge-human agreement 71% on faithfulness — rubric sharpened ("claim = any factual assertion about the customer's situation"; anchors added) → 92%, near the 94% human-human ceiling. Now prompt iteration is measurable: v3 wins coverage +11 with faithfulness flat, and the one regressed case (a sarcastic thread misread) becomes case #36 and a tone-rubric anchor.

**2. The model-swap decision, settled by paired diffs.**
New model release; marketing says upgrade. The suite (120 cases by now) runs both: aggregate +1.8 (looks like noise). Paired per-case: 9 fixed, 7 regressed — the regressions cluster in the "refusal-appropriate" slice (new model answers out-of-scope questions it should decline — see rag refusal metric). Verdict: hold the swap; add a refusal-hardening instruction; re-run — regressed slice recovers, fixes retained; migrate with staged rollout + parse-failure monitors (see prompt-engineering migration playbook). The aggregate would have shipped a hallucination regression with a celebration emoji.

**3. Judge audit catching drift.**
Quarterly audit: humans re-label 40 judge-scored outputs; agreement has slid 92%→78%. Diagnosis: the product added a "concise mode," and the judge's verbosity bias now penalizes correct-but-terse answers as "incomplete." Fix: coverage rubric re-anchored with concise-mode examples; length explicitly excluded from the coverage judgment ("evaluate presence of issues, not elaboration"); re-calibrated to 90%. Every faithfulness/coverage number for the quarter gets a footnote in the dashboard. The audit cadence existed precisely because judges drift when products move under them — the auditors get audited (see observability: same instinct, watching the watchers).

**4. The flywheel in production.**
Week's triage: 14 flagged answers from the support-bot's escalation queue (see ai-product-ux feedback wiring). Clusters: 6 = a new product line missing from the corpus (ingestion gap → docs added — see rag query-log mining); 5 = date-math errors ("is my warranty still valid?") → new case type `temporal-reasoning` (8 cases), fix routes date math to a tool (see agents/rag numeric edge), slice added to the dashboard; 3 = correct answers users disliked (tone) → 2 tone cases + 1 contested label escalated to product ("should the bot apologize for policy?" — an unmade decision, now made). Flywheel latency this week: 4 days from production miss to gating case. The suite grew 11 cases, every one of them real.

## Evaluation Rubric

Score 1–10:

- **1–2**: No suite; changes judged on cherry-picked examples; judges (if any) uncalibrated; quality arguments settled by seniority.
- **3–4**: A test-question list exists, mostly synthetic, run occasionally; single aggregate score; reference-metrics misused; no gating, no flywheel.
- **5–6**: Real typed cases in a harness; deterministic layer + per-dimension judges; calibration done once; changes usually gated; slices visible.
- **7–8**: Full checklist: bias-mitigated calibrated judges with recorded agreement, paired-diff discipline, flywheel with tracked latency, version-pinned runs, statistical honesty at small n.
- **9–10**: Additionally: held-out rotation measuring overfitting; judge audits on cadence; online metrics closing the loop; eval reports as the org's shared quality language; the suite demonstrably caught regressions pre-ship — receipts, not testimony.
