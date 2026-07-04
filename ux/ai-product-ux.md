# AI Product UX

## Purpose

Design interfaces for AI-powered features — chat, generation, agents, copilots — that set honest expectations, make wrongness survivable, stream latency away, and earn autonomy gradually instead of demanding trust upfront.

## When to use

- Adding LLM features to a product: assistants, generation, summarization, extraction, agents.
- Users don't trust, don't adopt, or over-trust an AI feature.
- Designing input affordances (blank box problem), output presentation (verification), or feedback loops.
- Deciding how much autonomy to give an agent and how to surface its actions.
- Reviewing AI UX where errors are silent or latency is a spinner.

## Goals

- Users know what the AI can and can't do before their first attempt (calibrated expectations).
- Every AI output is verifiable, editable, and cheap to retry — wrongness is a handled state, not a betrayal.
- Latency is honestly staged (streaming, progress phases), never a dead spinner.
- Consequential actions keep a human gate until the feature has earned autonomy with evidence.

## Inputs

- The capability envelope: what the model does well/badly here, measured (from evals — see ai/evals), not vibes.
- Error asymmetry: what does a wrong output cost the user (mild retype? sent email? deleted data? legal exposure?).
- Latency distribution p50/p95 per operation, and whether streaming is possible.
- User population: prompt-fluent early adopters or mainstream users who type two words?
- Feedback capture path: where would corrections/ratings flow, and who consumes them?

## Expert Mental Model

- **Design for wrongness first.** Every other software feature ships when it works; AI features ship *knowing* they'll be wrong some percentage of the time. The design question is not "how do we make it right" (that's the eval/model work) but "what happens to the user when it's wrong?" — can they *detect* it (verification affordances), *recover* (edit, retry, undo), and *calibrate* (learn when to trust)? Products fail on silent wrongness, not on wrongness.
- **The blank box is a capability mystery.** An empty text field with "Ask me anything" transfers the entire burden of discovering the capability envelope to the user, who will try two things, get one mediocre result, and leave. Experts seed the surface: example prompts specific to the user's context, templates for the top jobs, suggested next actions — these are the feature's real documentation, and they shape usage toward what evals say works.
- **Latency is narratable.** 8 seconds behind a spinner is broken; 8 seconds of visible progress — streaming tokens, phase labels ("Searching your docs… found 12 → drafting") — is a feature working hard. Streaming isn't just perceived speed: it lets users abort bad directions early (read the first sentence, cancel, rephrase), which cuts real cost too.
- **Trust is a ladder, not a toggle.** Sequence autonomy: (1) AI suggests, human does → (2) AI drafts, human approves → (3) AI acts, human reviews after → (4) AI acts silently. Each rung requires evidence from the rung below (acceptance rates, correction rates). Launching at rung 3 because the demo was cool is how AI features get feature-flagged off after the first incident. Where actions are irreversible or outward-facing (send, delete, pay, publish), the human gate stays until data justifies otherwise — and often forever.
- **Show the work in proportion to the stakes.** Citations with sources for claims, diffs instead of final states for changes ("here's what I'll modify" beats "done!"), plans before actions for agents, confidence framing only when it's real (calibrated) — decoration-confidence ("I'm 95% sure!" from an uncalibrated model) is worse than nothing.
- **Feedback UX is your eval pipeline wearing product clothes.** Thumbs up/down is nearly worthless alone; the correction *is* the signal — "user edited the draft's tone," "user re-asked with more specifics," "user abandoned after output." Design capture of implicit signals (edits, retries, accepts, copies) and route them to the eval set (see ai/evals). A feature without feedback capture can't improve; one with it compounds.

## Workflow

1. **Map the capability envelope from evals**: what's reliably good (ship prominently), spotty (ship with guardrails/verification emphasis), bad (block or don't ship — a visible refusal beats a confident failure).
2. **Classify every AI action by consequence**: read-only (summaries, answers) / reversible writes (drafts, edits with undo) / irreversible or outward-facing (send, execute, delete). Assign each a rung on the autonomy ladder and its gate design.
3. **Design the entry affordance against the blank box**: 3–5 example prompts drawn from the user's actual context (their data, their role), templates for the top 3 jobs-to-be-done, and progressive disclosure of advanced control (system prompt-ish settings hidden from mainstream). Rotate examples by usage data.
4. **Stage the latency**: stream text always when possible; label phases for multi-step operations; show partial results as they materialize; provide cancel that actually aborts (and doesn't bill); past ~10 s, convert to async with notification (see interface-states ladder — AI ops live on its upper rungs).
5. **Design the verification surface per output type**: claims → citations linking to sources (with the quoted span highlighted); extractions → side-by-side with the source document; code/config → diff view + run/test affordance; long generations → structural skim aids (headings, TL;DR). The user must be able to check without leaving.
6. **Make retry cheap and directed**: regenerate (same input), refine ("make it shorter" chips + freeform), and edit-in-place — three different recovery verbs; don't collapse them into one "try again." Preserve the previous version (users compare; sometimes v1 was better).
7. **Gate consequential actions with preview-as-default**: agents show the plan (steps, targets, blast radius) before executing; changes render as diffs with per-item accept/reject; sends show the final artifact with an explicit "Send" owned by the human. Batch operations get sampling review ("check 5 of the 200 before applying all").
8. **Instrument the trust signals**: acceptance rate, edit distance on accepted outputs, retry rate, abandonment after output, feature-return rate. These are the autonomy ladder's evidence and the eval set's feed.
9. **Write the refusal and degradation UX**: model down/overloaded → honest status + non-AI fallback path (the feature is an enhancement, not a hostage-taker); refusals → explain category and offer adjacent help; low-confidence internal signals → hedge the framing ("I couldn't find a definitive answer — closest matches:") rather than fake certainty.
10. **Close the loop visibly**: when user corrections actually improve things (better retrieval, updated instructions), tell them ("Got it — I'll format future reports this way") — visible learning builds the usage that generates more signal. Never fake it: claiming to learn while stateless is a trust debt that compounds.

## Decision Tree

- If the AI output is a claim about facts/data → citations mandatory; no citation available → say so in the output frame ("based on general knowledge, not your documents").
- Else if output is content the user will send/publish under their name → draft mode always: human owns the send; AI never auto-publishes identity-bearing artifacts.
- Else if output is an action on systems (agent) →
  - Reversible + scoped → act-then-report with prominent undo and an activity log.
  - Irreversible / outward / >small blast radius → plan-preview + explicit approval; for batches, sampled review + staged rollout (apply to 10, confirm, apply to rest).
- Else (informational, low stakes) → answer directly; over-gating trivial outputs teaches users the gates are noise (gate fatigue is real — see confirmation design).

Input affordance:
- If users are mainstream/two-word-typers → structured inputs where possible (dropdowns/fields feeding a prompt template beats freeform; the best AI UX often hides the prompt entirely behind a button: "Summarize this thread").
- Else if power users → freeform + visible controls + saved prompts.
- If the same job recurs → convert the successful freeform pattern into a named one-click action; chat is the discovery interface, buttons are the retention interface.

Latency posture:
- If <1 s p95 → inline, no theater.
- Else if streamable → stream + phase labels.
- Else if 3–15 s → phase progress + cancel; consider optimistic partials.
- Else → async job + notification; never a modal spinner hostage-taking the app.

Confidence display:
- If you have calibrated scores (retrieval scores, eval-validated thresholds) → use them to *change behavior* (hedge framing, offer alternatives, escalate to human) rather than printing percentages.
- Else → no numeric confidence; uncalibrated numbers are decor that mis-trains users.

## Heuristics

- The example prompts ARE the docs: users infer the envelope from them; choose examples that showcase verified strengths, not aspirations.
- Anthropomorphism budget: small. A name and a tone, fine; "I'm thinking…" fine; simulated feelings, apology theater, and first-person overreach ("I remember you!" when stateless) erode trust with every interaction.
- Never destroy the user's input: their prompt/draft survives every failure, regeneration, and navigation (see forms — the cardinal sin applies double when the input took thought).
- Regenerate must vary meaningfully (temperature/seed) or it's a broken button; refine-chips ("shorter", "more formal", "as a table") outperform freeform refinement for mainstream users.
- Diffs beat descriptions: "I changed the deadline to Friday" < highlighted before/after. For anything the AI modified, show the modification.
- Accepted-with-heavy-edits is a *failure* signal wearing a success costume — track edit distance, not just acceptance.
- Empty-state for AI features: show 2–3 completed examples (input → output) so users see the quality bar before spending effort.
- Rate limits and cost: burn user patience, not user trust — "3 generations left today" upfront beats a surprise paywall mid-task.
- Latency honesty beats latency hiding: fake fast (instant placeholder, then long silent finish) reads as broken twice.
- Chat is not always the answer: if the job is "fix my grammar," a button beats a conversation; reach for chat only when the task genuinely needs dialogue (ambiguity, iteration, exploration).
- Log every agent action visibly (activity feed with timestamps, targets, and undo links where possible) — the audit trail is both a trust feature and your incident-response tool.
- The "second session" test: does anything from session one make session two better (memory, saved patterns, learned preferences)? If yes, show it; if no, don't imply it.

## Quality Checklist

- [ ] Capability envelope documented from evals; entry affordances (examples/templates) showcase verified strengths.
- [ ] Every AI action classified by consequence with an assigned autonomy rung and gate design.
- [ ] Streaming/phased progress for >1 s ops; cancel aborts truly; >10 s goes async.
- [ ] Verification surface per output type: citations, diffs, side-by-source, or skim aids.
- [ ] Three recovery verbs distinct (regenerate / refine / edit); prior versions preserved; user input never lost.
- [ ] Irreversible/outward actions human-gated with preview; batches get sampled review + staged apply.
- [ ] Refusal, overload, and low-confidence states designed with non-AI fallbacks.
- [ ] Feedback captured beyond thumbs (edits, retries, abandons) and routed to the eval set.
- [ ] Trust metrics instrumented: acceptance, edit distance, retry, return rate.
- [ ] No uncalibrated confidence numbers; no fake learning claims; anthropomorphism within budget.

## Failure Modes

- **Silent wrongness**: fluent, confident, uncited output; the user finds out from their boss. The feature's real output was a trust incident.
- **Blank-box abandonment**: "Ask anything" → two mediocre attempts → never returns. The envelope was never communicated; the user priced the feature off a bad sample.
- **Demo-rung autonomy**: agent launched at act-silently because the sizzle reel needed it; first mis-fire triggers org-wide revocation and a quarter of rebuilding trust that gating would have never spent.
- **Spinner hostage**: 20 s modal spinner over the whole app for a summarization; users force-refresh, losing state, learning to avoid the button.
- **Thumbs-only feedback**: 2% click-through on ratings, zero edit capture — the team flies blind while sitting on the richest correction stream (user edits) unlogged.
- **Confidence cosplay**: "92% confident" printed from nothing calibrated; users trust the 92s and get burned, or learn all numbers are noise — both outcomes poison real signals later.
- **Gate fatigue**: confirmation modals on every trivial suggestion; users learn to click through; the one gate that mattered gets clicked through too.
- **Regenerate roulette**: identical retries (same seed/params) — users hammer the button, conclude "it's stuck," and the button teaches helplessness.
- **The hostage feature**: AI path breaks and takes the whole workflow with it — no manual fallback was kept; an enhancement became a dependency without earning it.

## Edge Cases

- **Prompt injection via user data**: the AI summarizes a document containing "ignore instructions and…" — retrieved/user content must be treated as data, not instructions (see ai/agents); UX implication: outputs influenced by injected content need provenance visibility.
- **Mid-stream failure**: connection drops at token 400 — preserve the partial output, mark it truncated, offer resume/retry; discarding streamed partials wastes the user's read.
- **Concurrent edits during generation**: user edits the doc while the AI drafts into it — lock the target region visibly or merge explicitly; silent clobbering of human words by machine words is the worst version of the conflict.
- **Long-context truncation**: the user pasted 200 pages; the model saw 50 — say what was actually considered ("analyzed the first ~50 pages") or the user trusts a conclusion drawn from data the model never read.
- **Multilingual input/output**: user writes in Portuguese, examples are English — mirror the user's language in outputs and examples, or state the limitation.
- **Repeated identical asks with different answers**: nondeterminism confuses ("it said X yesterday") — for factual/lookup-style features, pin down temperature and cache answers; variability is for creative surfaces.
- **Sensitive content in transcripts**: chat histories and agent logs contain PII/secrets users pasted — retention, redaction, and "delete this conversation" are product requirements, not compliance afterthoughts.
- **Model/version migrations**: outputs change tone/format overnight → users notice ("it got worse") — version-note UX and eval-gated rollouts (see ai/evals); silent model swaps on a beloved feature generate churn you can't attribute.
- **The over-truster**: power users wiring unreviewed AI output into downstream automation — rate the risk: where outputs feed machines, push for schema validation and sampling audits in the integration path.

## Tradeoffs

- **Friction vs safety**: every gate costs flow; every removed gate costs incident risk. Price by consequence class, not uniformly — and re-price with evidence (acceptance/correction rates) quarterly. The ladder exists to make this trade explicit.
- **Capability honesty vs marketing**: examples showcasing only strengths undersell; aspirational examples oversell and burn first-sessions. Showcase verified strengths, roadmap the rest visibly ("coming: X") — honesty compounds into the retention marketing wants.
- **Chat flexibility vs button reliability**: chat handles the long tail and hides discoverability in a box; buttons nail the head jobs and cap the ceiling. Mature AI products migrate: chat discovers demand → buttons harvest it.
- **Streaming immediacy vs composed quality**: streaming shows unpolished first-drafts thinking (occasionally retracted mid-stream); buffered output reads better but waits. Stream for conversational/generative; buffer short structured outputs (a wrong number briefly shown is remembered).
- **Memory/personalization vs privacy and predictability**: remembered context improves outputs and raises "what does it know about me" anxiety + drift surprises. Make memory inspectable and editable (show what's stored, let users delete), or don't build it.
- **Human review depth vs throughput**: sampled review scales where per-item review can't — accept the residual risk knowingly and instrument it (spot-audit error rates), rather than pretending full review happens.

## Optimization Strategies

- Mine the correction stream: cluster user edits of AI outputs monthly → the top clusters are your prompt/retrieval/model fixes, pre-prioritized by users (route into ai/evals cases).
- Promote successful freeform prompts into one-click actions with names — measure adoption; each promotion moves users up the reliability curve and down the effort curve.
- A/B the entry affordances (example sets, templates) against activation-to-second-use — the examples are cheap to iterate and move the top of the funnel hard.
- Track edit-distance-on-accept by segment: falling distance = candidate for a rung promotion on the autonomy ladder; rising = investigate before users churn quietly.
- Cache and dedupe identical/near-identical requests (semantic cache) — latency and cost win that also stabilizes answers for lookup-style asks.
- Review the activity/audit log UX with your most cautious enterprise buyer — their objections forecast the trust features the market will demand next.
- Once a quarter, watch five first-sessions raw: where the blank box wins, where the first wrongness lands, whether recovery verbs get found. First-session field notes out-inform dashboards.

## Self Review

- What does the user see the first time the AI is wrong — and can they detect, recover, and calibrate from it?
- Could a new user state, after 60 seconds, what this feature is good and bad at? What taught them?
- Which actions can the AI take without a human, and what evidence earned each rung?
- Where does a citation/diff/preview exist, and where am I asking for blind trust?
- What happens at p95 latency? Mid-stream failure? Model down?
- What signal do I capture when a user silently fixes the output — and who consumes it?
- Is there any confidence number, learning claim, or memory implication I can't back?
- If the model were swapped tomorrow, what UX would catch the regression before users do?

## Examples

**1. Email drafting copilot, ladder-disciplined.**
Rung at launch: draft-and-approve. Entry: "Draft reply" button (no blank box) + tone chips (concise/warm/formal) derived from the thread; output streams into a draft pane — *never* the send pipeline; diffs shown when it edits user text; Send stays a human verb with the draft fully editable. Recovery: regenerate (varied), refine chips, edit-in-place; v1 preserved behind "versions." Instrumented: acceptance 71%, median edit distance falling for "concise" (candidate to promote suggestions inline), rising for "formal" (eval case cluster filed). Six months of data later, low-stakes internal replies gain "send automatically after 30 s unless I cancel" — rung 3, earned, scoped, cancelable.

**2. RAG answers with verifiable bones.**
Support knowledge assistant: every claim carries a citation chip → click opens the source doc scrolled to the highlighted span; answers without sufficient retrieval score render as "No definitive answer in your docs — closest three articles:" (behavior change, not fake confidence). Phase-labeled progress ("Searching 4,200 docs… → reading 8 → answering") streams; agents can flag wrong answers inline, and the flag files the query + retrieved set into the eval queue automatically. Deflection went up; more telling, agent *verification* time per answer dropped — the citations did the trust work.

**3. Batch agent with sampled review.**
Data-cleanup agent proposes normalizing 4,120 CRM records. UX: plan first ("3 rule types, 4,120 records, est. 2 min — nothing deleted, all changes reversible 30 days"); sampled review of 10 representative diffs with accept/reject each (rejections refine the rules live); staged apply (100 → confirm drift-free → rest) with a progress feed; full activity log with per-record undo and a global revert. The user reviewed 10 records to safely apply 4,120 — review scaled by sampling, risk contained by staging and reversibility.

**4. The blank box, fixed.**
Analytics copilot launched as an empty chat; week-2 retention: 9%. Rework: entry shows three example questions *built from the user's own data* ("How did **Acme Corp's** usage change this quarter?"), a "surprise me" insight button, and two completed example Q&As demonstrating the quality bar; successful query patterns get "save as report" (chat → button migration); refusals for unsupported asks ("forecasting isn't available yet") link to what *is* supported. Same model, same backend. Week-2 retention: 34% — the capability didn't change; its legibility did.

## Evaluation Rubric

Score 1–10:

- **1–2**: Blank box + spinner + confident uncited output; auto-acting agent; thumbs as the only feedback; wrongness is the user's problem.
- **3–4**: Some examples/templates; streaming present; gates exist but uniform (fatigue) or missing where irreversible; feedback captured but unrouted.
- **5–6**: Consequence-classified actions on a ladder; verification surfaces on main outputs; recovery verbs distinct; honest degradation paths; basic trust metrics.
- **7–8**: Full checklist: eval-derived envelope shaping entry UX, preview/diff/sampled-review gates, correction-stream capture feeding evals, no uncalibrated confidence, input never lost.
- **9–10**: Additionally: autonomy promotions/demotions driven by instrumented evidence; chat→button migration running; memory inspectable; model-swap regressions caught by UX+eval gates before users; first-session field observation is a standing ritual.
