# AI Agents

## Purpose

Build LLM agents — model + tools + loop — that accomplish real tasks reliably: tool design as the core craft, context curation, stop conditions, verification steps, and the safety rails that keep autonomy earned rather than assumed.

## When to use

- A task needs multiple steps, tool calls, or decisions the model must sequence itself.
- Deciding between a workflow (fixed pipeline of LLM calls) and an agent (model-directed loop).
- An existing agent is unreliable: wrong tools, runaway loops, goal drift, context rot.
- Designing tool interfaces, memory, or multi-agent topologies.
- Reviewing agent autonomy and permission boundaries.

## Goals

- The agent's job is scoped: definition of done, budget (steps/tokens/time), and what it must never do.
- Tools are designed like APIs for a sharp-but-literal consumer: clear contracts, actionable errors, minimal overlap.
- Context stays curated (the working memory doesn't rot); state that matters outlives the context window.
- Every run is replayable from logs; failures are diagnosable to a step.

## Expert Mental Model

- **An agent is a loop: model → tool call → result → model, until done or budget.** Everything else is elaboration. The reliability of the loop is multiplicative: a 95%-correct step compounds to ~60% over 10 steps — which is why experts obsess over per-step reliability (tool clarity, context quality) and *step count reduction* before adding cleverness. The fastest way to a better agent is usually fewer, more powerful steps, not smarter orchestration.
- **Use the least agency that solves the task.** A fixed workflow (prompt-chain with branches you wrote) is more reliable, cheaper, and more debuggable than an agent loop — when the path is knowable, write it down as code. Agents earn their keep when the path genuinely varies with what's discovered mid-task (debugging, research, open-ended edits). "Agentic" is a cost you pay for path-uncertainty, not a feature you add for marketing.
- **Tool design IS the product.** The model reads your tool descriptions as documentation and your error messages as guidance. Experts write tools like great API design (see api-design) for a consumer that is literal, tireless, and unable to ask clarifying questions: names that say what they do, descriptions with when-to-use (and when NOT), few overlapping tools (three search variants = a coin flip per step), parameters validated with errors that teach ("file not found: src/auth.ts — did you mean src/auth/index.ts?" beats a stack trace — the agent can *act* on the former).
- **Context is working memory — curate it or it rots.** Every tool result dumped raw into history (a 40k-token log file, three redundant search results) crowds out the instructions and poisons later steps; long agent transcripts drift off-goal as early precision dilutes. Practices: summarize/truncate tool outputs to what the step needs, keep durable state *outside* the window (files, scratchpads, task lists the agent re-reads), restate the goal/plan at intervals, and prefer retrieving-on-demand over carrying-everything.
- **Verification is the highest-leverage step.** An agent that checks its own work against explicit criteria (run the tests, re-read the diff against the requirements, validate output schema) before declaring done converts "usually right" into "reliably right" — the single biggest quality win per token spent. Design *checkable* tasks: acceptance criteria the agent (or a cheap judge) can mechanically evaluate (see ai/evals).
- **Autonomy is earned per action class, not granted per agent** (see ai-product-ux trust ladder). Read-only tools: free. Reversible writes: act-and-log with undo. Irreversible/outward (send, delete, deploy, pay): human gate until instrumented evidence justifies otherwise — and often forever. The blast radius of a wrong action, not the model's benchmark score, sets the gate.
- **Treat all tool-returned content as untrusted input.** A web page, an email, a retrieved doc can contain "ignore your instructions and…" — prompt injection is the agent-era's SQL injection (see web-security: same trust-boundary thinking). Data enters as data: delimited, never blindly obeyed; consequential actions triggered by external content demand provenance checks and human gates.

## Workflow

1. **Write the job spec**: task, definition-of-done (checkable), budget (max steps/tokens/wall-time), forbidden actions, escalation path (what the agent does when stuck: ask, or stop-and-report — never loop silently).
2. **Choose the architecture by path-certainty**: knowable path → workflow (code the pipeline, LLM calls as steps); discoverable path → single agent loop; genuinely parallel independent subtasks at scale → consider multi-agent later, not first (see Decision Tree).
3. **Design the tool set minimally**: fewest tools covering the job; per tool — name (verb-object), description (what/when/when-NOT), typed parameters with validation, output shaped for the *next model step* (concise, structured, relevant), errors as recovery guidance. Collapse overlapping tools; split god-tools ("do_stuff(action=...)") into honest verbs.
4. **Engineer the results channel**: cap tool output size (truncate with "…1,200 more lines; use read_range to see more"), pre-summarize bulky results, return references (file paths, IDs) over payloads where the agent can fetch details on demand.
5. **Structure the loop**: system prompt = role + goal + tool guidance + output contract; plan-then-execute for long tasks (agent writes a plan artifact, then works it, updating status — the plan doubles as drift-anchor and progress UX; see ai-product-ux); re-inject goal + plan summary every N steps on long runs.
6. **Add the verification step as a first-class phase**: before "done," the agent runs the checkers (tests, schema validation, requirement checklist re-read) and fixes or reports discrepancies. Where self-check is weak, add an external check (cheap judge model, deterministic validator).
7. **Wire the safety rails**: step/token/time budgets enforced by the harness (not the model's discretion); loop detection (same tool+args twice → intervene); permission tiers per tool with human gates on the irreversible tier; sandbox execution (containers, scoped credentials, dry-run modes) so even a confused agent has bounded blast radius.
8. **Log everything as replayable structure**: every step's (context-in, tool, args, result, tokens, latency) — the trace that makes "why did it do that?" answerable and feeds evals (see observability: same discipline, new signal type).
9. **Evaluate on outcomes**: end-state task success on a case suite (not step-imitation — many valid paths exist); track success rate, steps-to-success, cost-per-success, intervention rate; failures become cases (see ai/evals flywheel).
10. **Iterate on the evidence**: read failing traces weekly; classify (wrong tool chosen → description fix; bad plan → prompt/plan-structure fix; context rot → curation fix; capability wall → model upgrade or task re-scope); fix the dominant class first.

## Decision Tree

- If the path is knowable in advance (classify → extract → format → store) → workflow, not agent: code the pipeline, each LLM step with its own contract. Reach for an agent only where you genuinely can't write the flowchart.
- If the task is one tool-use away (answer + search) → single model call with tools, no loop machinery needed.
- If steps exceed ~15–20 routinely → decompose: either a workflow of agent-phases (plan → execute → verify as separate contexts) or checkpointed state (task list file) so each phase starts with curated context rather than a 100k-token transcript.
- Multi-agent?
  - Independent parallel subtasks with separable contexts (research N topics, review M files) → orchestrator spawning parallel workers, results merged — the win is context isolation and wall-clock, not intelligence.
  - Sequential handoffs ("planner agent → coder agent → reviewer agent") → often a workflow wearing a costume; simpler as phases of one loop unless contexts genuinely must differ.
  - Agents debating/conversing freely → rarely earns its complexity; demand eval evidence over the single-agent baseline before shipping.
- If the agent must act on external systems:
  - Read-only → allow.
  - Reversible + logged → allow with undo + activity feed (see ai-product-ux).
  - Irreversible/outward → plan-preview + human approval; batch → sampled review + staged apply (see ai-product-ux batch pattern).
- If the agent gets stuck (budget近 exhausted, loop detected, error repeated) → structured surrender: summarize state, what was tried, best hypothesis, and hand off — a good failure report is a deliverable; silent spinning is not.
- If tool results come from the outside world (web, email, docs) → injection posture: content delimited as data, instructions in content never executed, consequential follow-ups gated (see web-security trust boundaries).

## Heuristics

- Tool count: single digits per agent where possible; past ~15–20, selection accuracy degrades and overlapping tools become coin flips — consolidate or namespace by phase.
- Write tool descriptions like you're preventing a specific misuse you've already seen; after every failure-trace review, the descriptions get sharper ("use for X; for Y use tool_z instead").
- The error message is a prompt: every tool error should name what went wrong AND a next action ("rate limited; retry after 30s" / "query returned 4,000 rows; add a filter"). Errors that only humans can interpret produce retry-loops.
- Give the agent a scratchpad (file or state field) and instruct it to externalize: plans, findings, TODO status — externalized state survives context compaction and re-anchors the loop.
- Budgets are load-bearing: a runaway agent burns money *and* trust; the harness kills at budget with a structured report, always.
- Same-tool-same-args twice = intervention point (inject "this was already tried; result was X; try a different approach").
- Prefer one powerful tool call over five weak ones: `search_code(query)` returning ranked snippets beats `list_dir` + `read_file` × 4 — design tools at the altitude of the agent's *intent* (see api-design: consumer-inward design; same principle).
- Order tool results by relevance and put critical caveats at the top of the result, not the bottom of a dump.
- Temperature near 0 for tool-selection-heavy loops; save creativity for content-generation steps.
- Sandbox by default: scoped tokens (this repo, this folder, this tenant), read-only credentials until write is proven needed, network egress allowlists — assume the agent will eventually do something surprising, because it will (see secrets least-privilege).
- Cost sanity check: steps × context-growth is quadratic-ish in tokens; an agent that "works" at $4/run may be a workflow that works at $0.20 — price the alternative.
- The demo threshold is 1 success; the ship threshold is a success *rate* on a case suite you didn't cherry-pick (see ai/evals).

## Quality Checklist

- [ ] Job spec: checkable done-criteria, budgets, forbidden actions, stuck-protocol.
- [ ] Architecture justified by path-uncertainty (workflow considered and rejected in writing, or chosen).
- [ ] Tools: minimal set, when-to-use/when-not descriptions, validated params, teaching errors, capped/summarized outputs.
- [ ] Context curation: bulky results truncated/summarized, durable state externalized, goal restated on long runs.
- [ ] Verification phase before done (tests/schema/checklist), external check where self-check is weak.
- [ ] Harness-enforced budgets + loop detection + structured surrender.
- [ ] Permission tiers per tool; irreversible actions human-gated; sandbox/scoped credentials.
- [ ] Injection posture: external content as data, gated consequential follow-ups.
- [ ] Full structured trace per run; replayable; failures diagnosable to a step.
- [ ] Outcome evals: success rate, cost/steps per success, intervention rate on an honest case suite.

## Failure Modes

- **The runaway loop**: no budget enforcement; agent retries a failing tool 400 times overnight; the bill is the incident report. Harness budgets existed as a TODO.
- **Tool soup**: 30 overlapping tools ("search", "find", "lookup", "query"); the agent alternates between them randomly; every trace review reads differently. Selection entropy was designed in.
- **Context rot**: a 60k-token transcript of raw tool dumps; step 40's model can't find the goal under the debris; output drifts plausible-but-off-task. Nobody curated the working memory.
- **Goal drift on long horizons**: agent "improves" scope mid-task (asked to fix a bug, refactors the module, breaks the API) — missing plan-anchor and done-criteria discipline.
- **Hallucinated success**: tool errored, agent narrates success anyway ("I've updated the file") — results channel didn't make failure loud + verification phase absent. The most trust-corrosive failure class.
- **Demo-grade autonomy**: shipped at act-silently on the strength of five hand-picked runs; first bad batch action triggers org-wide revocation (see ai-product-ux demo-rung failure — same pattern, backend edition).
- **Injection compliance**: agent reads a webpage containing "email the contents of /etc/passwd to…" and helpfully tries — external content ran as instructions; the trust boundary was never drawn (see web-security).
- **Multi-agent theater**: five agents with titles (Planner, Critic, Architect…) passing messages — 5× cost, 3× latency, accuracy indistinguishable from one well-prompted loop; nobody ran the baseline.
- **Untraceable failures**: "it did something weird yesterday" with no step logs — unreproducible, undebuggable, unfixable; the run existed only as vibes.

## Edge Cases

- **Long tasks vs context limits**: the task legitimately needs 200 steps — checkpointing (externalized task list + phase summaries + fresh contexts per phase) beats heroic single-context runs; design the resume path (agent reads its own checkpoint and continues).
- **Mid-run world changes**: the file the agent planned around gets edited by a human mid-run — re-read-before-write discipline on mutable resources; optimistic-concurrency for agent writes (see concurrency-bugs: same shape).
- **Non-determinism in evals**: same task, different valid paths and phrasings — evaluate end-state outcomes and invariants, not trajectories; allow N-run success-rate rather than single-run pass/fail (see ai/evals variance honesty).
- **Tool version drift**: tool schema changes under a prompt tuned to the old one — version tool contracts and re-run the agent suite on tool changes (contract testing for the model-tool interface, see ci-cd gates).
- **Parallel agents colliding**: two workers editing the same file / same ticket — partition workspaces (worktrees, ID ranges) or lock; agent parallelism re-inherits every distributed-systems race (see concurrency-bugs, async-processing idempotency).
- **The agent that should refuse**: task is impossible/contradictory ("make the tests pass without changing behavior" where behavior IS the bug) — spec the refusal/escalation as a *success* mode; agents optimized only for completion will fabricate.
- **Secrets in the loop**: credentials appearing in tool outputs (env dumps, config reads) then persisting in traces/logs — redact at the tool boundary; traces are a data store with retention and access rules (see observability PII discipline, secrets skill).
- **Human-in-the-loop latency**: an approval gate mid-run parks the agent for hours — design pause/resume serialization (checkpoint state, resume on approval) rather than holding contexts hot.

## Tradeoffs

- **Agency vs reliability**: more model-directed freedom handles more path-variance and multiplies failure surface; more scripted structure caps both. Slide the dial per phase: scripted skeleton (workflow) with agentic sub-steps inside is the pragmatic middle for most products.
- **Tool power vs blast radius**: `execute_sql(query)` is maximally capable and maximally dangerous; `get_customer_orders(customer_id)` is safe and rigid. Tier by data sensitivity: broad tools in sandboxes/read-replicas, narrow tools against production (see authorization: same deny-by-default instinct).
- **Context richness vs cost/rot**: more history helps continuity and bloats cost while rotting relevance; summarize-and-externalize is the escape, at the price of summary-lossiness on rare backtracks. Keep raw traces in logs (replayable) even when the window holds summaries.
- **Verification depth vs cost/latency**: full test-suite runs per step are certainty at 10× cost; end-of-run verification catches most at 1×. Verify at phase boundaries and before irreversible actions; per-step only for the cheapest checks (schema validation).
- **Single vs multi-agent**: parallelism buys wall-clock and context isolation, costs orchestration + merge complexity + N× spend. Adopt for genuinely parallel work with separable contexts; refuse for sequential role-play without eval evidence.
- **Autonomy vs human throughput**: every gate protects and bottlenecks; the earned-autonomy ladder (see ai-product-ux) with instrumented promotion (intervention rate falling, success rate stable) resolves it over time — gates are re-priced by evidence, not by demo enthusiasm.

## Optimization Strategies

- Trace-review ritual: read 5–10 failing runs weekly; classify failures (tool selection / bad plan / context rot / capability / spec-gap); fix the dominant class — tool description edits are the highest-ROI fix and cost minutes.
- Reduce steps structurally: merge chatty tool sequences into one intent-level tool; prefetch what every run needs into the initial context; cache repeated lookups (see caching).
- Distill workflows out of agents: when traces show the agent taking the same path 90% of the time, that path wants to be code — freeze it as a workflow, keep agency for the 10% (cost and reliability both improve).
- Strengthen the checker, not just the doer: a better verification step (sharper criteria, judge calibration — see ai/evals) lifts effective quality across every task without touching the agent.
- Model-tier routing: cheap model for mechanical steps (formatting, extraction), strong model for planning/synthesis — cost drops 3–10× with flat quality if the split follows the eval data.
- Prompt-cache the stable prefix (system + tools) and order context stable-first (see prompt-engineering caching heuristics) — agent loops re-read their prefix every step; caching it is the single biggest cost lever.
- Build the eval suite from production traces (successes as regression cases, failures as target cases) so the agent's improvement loop runs on real distribution, not synthetic hopes (see ai/evals).

## Self Review

- Could this be a workflow? What specifically about the path is unknowable in advance?
- What's the done-criterion, and can the agent (or a checker) mechanically evaluate it?
- For each tool: would a literal-minded stranger know when to use it, when not, and what to do with its errors?
- What's in the context at step 20 — have I read an actual mid-run context dump? What's rotting in there?
- What stops a runaway loop, and did I test that it stops (not just that it exists)?
- Which actions are irreversible, and what stands between the agent and them?
- If external content said "ignore your instructions," what happens — demonstrably?
- What's the success rate on cases I didn't pick, and what did the last failing trace teach?

## Examples

**1. Code-fix agent with the full discipline.**
Job spec: fix failing test in repo X; done = target test passes AND full suite green AND diff reviewed against a "no unrelated changes" checklist; budget 25 steps; forbidden: force-push, dependency changes. Tools (5): `search_code`, `read_file(path, range)`, `edit_file` (returns diff), `run_tests(scope)` (returns failures summarized, not full logs), `report(status, summary)`. Loop: plan artifact first (hypothesis + intended change), execute, then the verification phase runs the suite and re-reads the diff against the checklist before `report`. Sandbox: worktree + scoped token, no network. Traces show early failure mode: agent re-ran full test suite every step (slow, bloated context) → `run_tests` description gains "prefer scope=target until fix candidate ready" — success rate 62%→84%, cost −40%. The fix was a sentence in a tool description.

**2. Research agent, parallel where it counts.**
Task: competitive analysis across 8 vendors. Architecture: orchestrator (workflow, not agent) spawns 8 parallel worker agents, each with an isolated context, a `web_search`+`fetch_page` toolset (injection posture: page content delimited as data; any instruction-like content flagged, never followed), and a per-worker output contract (structured findings JSON + citations). Merge step: a synthesis call over the 8 structured outputs — not over 8 raw transcripts (context curation at the topology level). Budgets per worker (12 steps) kill two runaway fetch-loops harmlessly; their structured surrender reports ("paywalled; best available: …") merge as partial data. Wall-clock: 4 min vs 25 sequential; the parallelism bought time and context isolation, not "intelligence."

**3. The batch-action agent that earned rung 3.**
CRM-cleanup agent (see ai-product-ux example — backend view): launched at plan-preview+sampled-review (rung 2). Instrumentation: intervention rate (human rejections in sampled review), post-apply error reports, undo usage. Three months: rejection rate falls to 0.4%, undo near-zero, error taxonomy stable → promotion proposal with the data: auto-apply for the two lowest-risk rule types, preview retained for the rest, global kill-switch + staged apply kept. The promotion memo cites eval numbers, not demos; the demotion criteria (rejection >2% for a week → back to rung 2) ship *in the same memo* — autonomy with a reverse gear.

**4. Killing a multi-agent architecture with a baseline.**
Proposal: Planner→Coder→Critic→Fixer pipeline for PR review. Before adoption, the eval: 40 real PRs with known issues, measured against (a) the 4-agent pipeline, (b) one agent with a verification phase, (c) one strong model call with a great rubric prompt. Results: (a) finds 71% of seeded issues at $1.90/PR with 4× latency; (b) 74% at $0.55; (c) 66% at $0.12. Decision: (b) ships; (c) becomes the cheap pre-filter tier; (a) is retired with thanks. The lesson institutionalized in the design doc template: *multi-agent proposals must beat the single-loop baseline on the suite* — role-play is not an architecture (see ai/evals: the suite settles arguments that architecture diagrams start).

## Evaluation Rubric

Score 1–10:

- **1–2**: Unbounded loop, tool soup, raw dumps in context, no logs, no verification; autonomy by demo; injection unconsidered.
- **3–4**: Basic loop with budgets; tools work but overlap and errors are opaque; some logging; success measured anecdotally; gates uniform or missing.
- **5–6**: Job-spec'd with checkable done-criteria; minimal tool set with teaching errors; context curation practiced; verification phase; permission tiers; outcome evals on an honest suite.
- **7–8**: Full checklist: structured surrender, loop detection, externalized state for long tasks, injection posture tested, replayable traces feeding a weekly failure-review ritual, workflow-vs-agent decision documented.
- **9–10**: Additionally: earned-autonomy promotions/demotions on instrumented evidence; workflows distilled from stable agent paths; model-tier routing and prompt-cache economics tuned; multi-agent used only where it beat the baseline; the agent's failure reports are good enough to be deliverables themselves.
