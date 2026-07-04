# RAG (Retrieval-Augmented Generation)

## Purpose

Build retrieval-augmented systems where the retrieval actually retrieves and the generation actually grounds — eval-first development, chunking, hybrid search, reranking, and the diagnosis discipline that separates retrieval failures from synthesis failures.

## When to use

- Building Q&A/assistant features over documents, knowledge bases, tickets, or codebases.
- An existing RAG system gives wrong, vague, or "confidently missing" answers.
- Choosing chunking, embeddings, vector stores, or rerankers.
- Deciding between RAG, long-context stuffing, fine-tuning, or plain search.
- Grounding/citation requirements ("only answer from our docs").

## Goals

- A labeled eval set (real questions → expected sources/answers) exists before tuning anything.
- Retrieval measured (recall@k) separately from generation (faithfulness, answer quality).
- The system refuses gracefully when the corpus doesn't contain the answer.
- Freshness pipeline keeps the index honest; citations let users verify (see ai-product-ux).

## Expert Mental Model

- **The LLM cannot answer from what retrieval didn't fetch.** RAG quality is dominated by retrieval quality; teams instinctively tune prompts (visible, easy) when the failure was recall (invisible without measurement). The first diagnostic reflex for any bad answer: *look at the retrieved chunks* — was the answer present? Everything forks on that question: absent → retrieval problem (chunking, embedding, query mismatch); present → synthesis problem (prompt, model, context assembly). Skipping this fork means tuning the wrong half indefinitely.
- **Eval-first or vibes-forever.** 50–100 real questions with labeled expected sources (and ideally gold answers) is the minimum instrument; without it, every change (new chunk size! better embedding!) is judged by three cherry-picked queries and ships regressions invisibly. The eval set starts day one, grows from every observed failure (see ai/evals — the failure→case flywheel), and splits by question type (lookup, synthesis-across-docs, aggregation, out-of-corpus) because systems regress *per type*.
- **Chunking is where meaning gets cut.** Chunks are the retrieval atoms: too small → answers span chunks and recall fragments; too big → embeddings blur multiple topics and precision dies; boundary-blind splitting (every N tokens) cuts tables from headers and answers from their conditions. Structure-aware chunking (headings/sections, with parent-context breadcrumbs like "Refunds > Enterprise plans" prepended) beats fixed-size in most corpora; 200–800 tokens is the working range; overlap is a patch, structure is the fix.
- **Hybrid beats either alone.** Vector search catches paraphrase and semantics; lexical (BM25) catches exact terms, IDs, codes, and names — and real queries are full of exact terms ("error E4012", "clause 7.3", product names). Dense-only systems whiff on precisely the queries users consider easiest. Hybrid (both, fused — e.g., reciprocal rank fusion) + metadata pre-filtering (tenant! date! doctype! — filter *before* similarity, and tenant filtering is a security boundary, not a relevance nicety; see authorization) is the standard adult architecture.
- **Retrieve wide, rerank narrow.** First-stage retrieval optimizes recall (top 30–100 candidates, cheap); a cross-encoder reranker optimizes precision (top 3–8 into the context, expensive but tiny-N). This two-stage shape is the single most reliable quality upgrade in the pattern — it decouples "don't miss it" from "put the best first," which single-stage similarity forces into one compromise.
- **Grounding is a system property, not a prompt line.** "Only answer from the context" in the prompt helps; it does not bind. Real grounding = instruction + citations-with-verification-UX (see ai-product-ux) + refusal path when retrieval confidence is low + *faithfulness evals* that measure hallucination-despite-context (see ai/evals LLM-judge). The refusal path matters most: a RAG system's worst output is a fluent answer to a question its corpus can't answer.
- **Long context didn't kill RAG; it changed the tradeoff curve.** Stuffing 200 pages per query costs latency + money per-query forever, and attention degrades over haystacks; retrieval costs indexing complexity once. Small stable corpus + low query volume → stuffing is honestly simpler. Large/multi-tenant/fresh corpus → retrieval wins on cost, latency, freshness, and access control. Do the arithmetic per use case instead of joining a religion.

## Workflow

1. **Define the job and the refusal boundary**: what questions must this answer, from which corpus, and what should it say when the answer isn't there? Write example Q→A pairs including out-of-corpus questions.
2. **Build the eval set first**: 50–100 real questions (from support logs, user interviews, stakeholders), each labeled with expected source docs/chunks and gold answers where possible; typed (lookup/synthesis/aggregation/out-of-corpus); wired into a harness that reports recall@k and answer quality per type (see ai/evals).
3. **Ingest with structure**: parse documents preserving hierarchy (headings, tables, lists — table-blind parsing silently destroys tabular answers); chunk on semantic boundaries (sections/paragraphs) targeting 200–800 tokens; prepend breadcrumb context (doc title > section path); attach metadata (source, tenant, date, doctype, URL/anchor for citations).
4. **Index hybrid**: embeddings (choose by trying 2–3 on YOUR eval set — domain fit beats leaderboard rank) + BM25/lexical; metadata filters as first-class (pre-filter, not post-filter).
5. **Handle the query side**: conversational queries need rewriting (resolve "what about for enterprise?" against chat history into a standalone query); consider decomposition for multi-part questions; log every query + retrieved set (this log is your future eval set and your debugging corpus).
6. **Two-stage retrieve**: top 30–100 hybrid candidates → cross-encoder rerank → top 3–8 into context, ordered sensibly (either relevance-first or document-order for coherence — test both on evals), with per-chunk source markers for citation.
7. **Assemble generation**: system prompt with grounding instruction + refusal instruction ("if the context doesn't contain the answer, say so and point to what's closest") + citation format; context clearly delimited as data, not instructions (prompt-injection posture — see agents/prompt-engineering).
8. **Measure the two halves**: retrieval recall@k against labeled sources; generation faithfulness (does the answer contain claims absent from context?) and quality via rubric judge calibrated against human labels (see ai/evals). Fix the failing half — this is the fork from the mental model, industrialized.
9. **Ship with verification UX**: citations linked to source-with-highlight, confidence-behavior (low retrieval score → hedged framing/refusal), feedback capture routed to the eval set (see ai-product-ux).
10. **Build the freshness pipeline**: document updates → re-chunk → re-embed → swap atomically (versioned index or upsert-by-doc-id with tombstones); deletion propagates (a deleted policy doc still being cited is a legal incident, not a bug); staleness monitoring (index age vs source-of-truth updated_at).

## Decision Tree

- If answers are wrong/missing → inspect retrieved chunks for 10 failing eval cases:
  - Answer not in any retrieved chunk →
    - Not in corpus at all → ingestion gap (missing source, parse failure — check the parser on that doc) or genuinely out-of-scope (refusal should have fired).
    - In corpus, not retrieved → query-document vocabulary mismatch (add lexical/hybrid, query rewriting), chunking cut the answer from its context (restructure), or embedding blind spot (test alternatives on the eval set).
    - Retrieved at rank 20 but you send top-5 → widen first stage + add/fix reranker.
  - Answer in chunks, output wrong → synthesis: context assembly (too much noise → tighten k, rerank harder), prompt (grounding/refusal instructions weak), or model capability (upgrade model before exotic pipeline surgery).
- If users ask aggregations ("how many customers requested X?") → RAG-over-chunks is the wrong tool; route to structured search/SQL over metadata (query classification layer in front — RAG is one tool in the router, not the router).
- If the corpus is small (<~50–100k tokens), stable, single-tenant, low QPS → consider long-context stuffing (simpler, no index ops); re-run the arithmetic when any of those changes.
- If exact-match queries fail (IDs, error codes, names) → you're dense-only; add BM25 hybrid today.
- If multi-tenant → tenant filter enforced at the retrieval layer as a security invariant (test cross-tenant leakage explicitly — see authorization deny tests).
- If answers need reasoning over many docs (synthesis/aggregation type) → raise k with reranking, consider map-reduce summarization patterns, or agentic retrieval (iterative search — see ai/agents) — and expect this type to lag lookup quality; measure it separately.
- If fine-tuning is proposed "to teach the model our docs" → almost always wrong tool (facts churn; tuning is for *style/format/skill*, retrieval is for *knowledge*); revisit only with stable domain language and RAG demonstrably capped.

## Heuristics

- Read your chunks. Actually open 20 random chunks and read them: are they self-contained? Would a human find the answer given only this text? Garbage chunks explain more RAG failures than model choice ever does.
- The query log is gold: real user phrasings differ from your team's test phrasings (shorter, vaguer, typo'd, jargon-mixed) — sample eval cases from production weekly.
- Recall@k before anything else: if recall@50 is bad, no reranker or prompt can save you; if recall@50 is good but recall@5 is bad, it's precisely a reranking problem.
- Breadcrumbs are cheap recall: prepending "Doc: Enterprise Agreement > Section: Termination" to each chunk lifts both retrieval (terms in the path match queries) and synthesis (the model knows what it's reading).
- Tables, code blocks, and lists need type-aware handling: a table split mid-row is noise; embed a table's serialized form + its caption, or route tabular questions to structured extraction.
- k into the context is a precision dial, not a generosity dial: more chunks = more distractors; models anchor on irrelevant-but-present text. 3–8 well-reranked chunks beat 20 hopefuls.
- Embed the *question form* where possible: indexing synthetic "questions this chunk answers" (HyDE-adjacent, or QA-pair generation at ingest) narrows the query-document gap for FAQ-shaped corpora.
- Version everything that shapes retrieval (chunker, embedder, index build) — an un-reproducible index is an undebuggable one; keep the eval harness pinned against index versions (see ai/evals regression discipline).
- Citation precision beats citation existence: cite the chunk/anchor, not "the 80-page PDF" — verification UX dies at page 1 of 80 (see ai-product-ux).
- Cost sanity: embedding re-index of the whole corpus should be a button, not a project — you'll need it every time you change chunking or models, which is more often than planned.
- Refusal rate is a metric with two failure directions: too low → hallucinating past corpus edges; too high → useless. Track both on the typed eval set (out-of-corpus cases exist to measure this).

## Quality Checklist

- [ ] Typed eval set (≥50 real questions, labeled sources, out-of-corpus cases included) in a runnable harness.
- [ ] Retrieval and generation measured separately (recall@k; faithfulness + quality per type).
- [ ] Structure-aware chunking with breadcrumbs; tables/code handled type-aware; 20-chunk manual read done.
- [ ] Hybrid (dense+lexical) retrieval; metadata pre-filters; tenant isolation tested as a deny test.
- [ ] Two-stage: wide first-stage recall → reranker → 3–8 chunks.
- [ ] Query rewriting for conversational input; query+retrieval logging on.
- [ ] Grounding: citations with anchors, refusal path for low-confidence, context delimited as data.
- [ ] Freshness: update/delete propagation verified (deleted doc → uncitable), staleness monitored.
- [ ] Failure-to-eval-case flywheel running (production misses become labeled cases weekly).
- [ ] Index/chunker/embedder versioned; full re-index is push-button.

## Failure Modes

- **Prompt-tuning a retrieval problem**: weeks of prompt iterations while recall@5 sits at 40% — the answer was never in the context; nobody looked at the chunks.
- **Fixed-size chunking massacre**: 512-token windows cutting answers from their conditions ("refunds allowed…" [chunk break] "…except enterprise contracts") — the system confidently states half-truths that are worse than wrong.
- **Dense-only whiffing exact terms**: "error E4012" retrieves philosophically-similar chunks about errors in general; the user's easiest query is the system's blindest spot.
- **Demo-set overfitting**: tuned to the 10 questions the team always tries; production queries (vaguer, weirder) collapse. The eval set was a demo script, not a sample.
- **No refusal path**: out-of-corpus question → fluent fabrication with fake-confident tone; user checks nothing (why would they? it sounded certain); the incident report writes itself.
- **Stale index betrayal**: policy updated Monday, RAG cites the old one Friday — worse than no answer, because it's authoritative-looking and wrong; no freshness pipeline, no staleness alarm.
- **Context stuffing as generosity**: k=25 "to be safe" — distractor chunks dilute attention, answers cite the wrong doc, latency and cost triple. Precision was the missing virtue.
- **Cross-tenant leakage**: post-filtering (retrieve-then-filter) drops rank-1 results and occasionally *doesn't* drop them — a tenant reads another's contract clause. Retrieval filters are authz surface (see authorization IDOR — same bug, new costume).
- **Metric monotheism**: optimizing one aggregate answer-quality score while out-of-corpus refusal quietly degrades — typed evals exist because RAG regresses per question type (see ai/evals slicing).

## Edge Cases

- **Conversational context resolution**: "and for Germany?" — without query rewriting against history, retrieval sees three words; with naive concatenation, it sees noise. Rewrite-to-standalone is the standard fix; eval it with multi-turn cases.
- **Conflicting sources**: two docs disagree (old policy vs new, marketing vs legal) — retrieval surfaces both; generation must acknowledge conflict + prefer by metadata (recency, authority tier), not silently pick one. Needs an explicit authority policy at ingest.
- **Duplicate/near-duplicate corpus**: the same paragraph in 40 docs floods top-k with copies (k slots wasted on one fact) — dedupe at index time or diversity-penalize at retrieval (MMR-class).
- **Very long answers spanning many chunks** (procedures, legal clauses): retrieval gets step 3 of 9 — parent-document retrieval (match on chunk, return the section/parent) fixes the fragment problem for procedure-shaped content.
- **Multilingual corpora/queries**: query in Spanish, docs in English — multilingual embeddings or translate-at-query; lexical hybrid breaks across languages (BM25 doesn't translate); test explicitly if this is your reality.
- **Access-controlled corpora with per-user visibility**: retrieval must filter by *the asking user's* ACL at query time (not index-time roles that staled) — and the citation UX must not leak titles of unreadable docs (existence leak — see authorization 403/404 logic).
- **Documents that are mostly images/scans**: parse quality gates everything — OCR confidence should flow into metadata; a corpus that's 30% unparseable is a silent 30% recall ceiling nobody measured.
- **Numeric/temporal reasoning over retrieved facts** ("what's the total across these three plans?"): retrieval fetches correctly, synthesis does arithmetic wrong — route computation to tools/code (see ai/agents tool use) rather than trusting generation math.

## Tradeoffs

- **Chunk size**: small = precise matching, fragmented context; large = coherent context, blurred embeddings and wasted context budget. Resolve per corpus via evals, and with parent-document retrieval (match small, return big) when both matter.
- **k (context breadth) vs precision**: more chunks raise recall-into-context and lower signal density; reranking moves the frontier but doesn't repeal it. Tune per question type (synthesis types need more; lookup needs less).
- **Freshness vs indexing cost**: near-real-time upserts complicate the pipeline; nightly rebuilds are simple and stale by up to a day. Match to corpus change rate and the cost of citing stale (policy docs: minutes matter; engineering wiki: nightly is fine). State the budget like a caching decision (see caching staleness budgets).
- **Self-hosted vs managed vector store**: managed buys ops simplicity and bills per-query forever; pgvector-in-your-Postgres buys operational familiarity and one fewer system (see system-design boring-tech bias) until scale or features force the move. Choose by ops reality, not benchmark theater.
- **Latency vs quality stack**: rewriting + hybrid + rerank + big-model synthesis stacks to seconds; each stage earns its latency on the eval set or gets cut. Cheap-fast draft for lookup types, full stack for synthesis types (router by classified question type) is the mature shape.
- **RAG vs fine-tuning vs both**: retrieval for knowledge (fresh, auditable, deletable), tuning for behavior (format, tone, domain reasoning patterns); the combination is legitimate when both gaps are proven — sequence: RAG first (cheaper to iterate, easier to debug), tune only for what retrieval demonstrably can't fix.

## Optimization Strategies

- Rank failures by type from the typed evals and fix the dominant type first — chunking fixes lift lookup; reranking lifts precision types; routing lifts aggregation; effort-to-lift differs 10× across types.
- Mine the query logs monthly: cluster failed/refused/abandoned queries → each cluster is either an ingestion gap (add sources), a query-understanding gap (rewriting rules), or a product gap (out-of-scope demand worth roadmapping).
- Cheap wins ladder (try in order): breadcrumbs on chunks → hybrid fusion → cross-encoder rerank → query rewriting → parent-document retrieval → embedding swap → agentic retrieval. Each step is measurable on the harness before the next.
- Cache aggressively: embedding cache (identical chunks re-embed free), semantic query cache for lookup-type repeats (see caching + ai-product-ux stability benefits).
- Distill the reranker's judgment into first-stage improvements periodically (hard-negative mining from rerank disagreements retrains/re-prompts the first stage).
- Run a quarterly "citation audit": sample 50 production answers, verify each citation actually supports the claim — faithfulness drift is invisible from aggregate scores (see ai/evals human-gold sampling).

## Self Review

- For the last 10 bad answers: did I look at the retrieved chunks before touching anything? Which half failed?
- What's recall@5 / recall@50 by question type right now? Which type is worst and is my current work aimed at it?
- Have I read 20 random chunks this month? Would I find answers in them?
- What happens on an out-of-corpus question — demonstrably, on eval cases, not hopefully?
- If a document was deleted this morning, when does it stop being citable — and how do I know?
- Can a tenant retrieve another tenant's content under any query? Where's the deny test?
- What did the last chunking/embedding change do to the eval numbers? (If I can't answer: the harness isn't in the loop.)
- Which production queries failed this week, and are they eval cases yet?

## Examples

**1. The fork in action: support-bot rescue.**
Symptom: "answers feel generic." Ten failing cases pulled; retrieved chunks inspected: 7/10 don't contain the answer (retrieval), 3/10 do (synthesis). Retrieval seven: five are exact-term queries (SKUs, error codes) whiffed by dense-only → hybrid BM25+RRF added; two are chunking cuts (policy conditions split from rules) → structure-aware re-chunk with breadcrumbs. Synthesis three: k=20 noise → rerank to top-5. Eval harness (built first, 80 labeled support questions): recall@5 41%→78%; faithfulness judge: violations 12%→3%. Prompt changes made: zero. The fork prevented a month of prompt archaeology.

**2. Eval-first build for a contracts assistant.**
Before any pipeline: 60 questions from the legal team (typed: clause-lookup 30, cross-contract synthesis 15, aggregation 8, out-of-corpus 7) with labeled source clauses. Baseline (naive fixed chunks, dense-only, no rerank): lookup recall@5 55%, synthesis 30%, aggregations wrong, refusals never fire. Ladder applied with measurements per rung: structure chunking (+18 lookup), hybrid (+9), rerank (+11 precision), parent-clause retrieval (+15 synthesis), aggregation questions *routed* to metadata SQL (not RAG — classification layer), refusal threshold tuned on the 7 out-of-corpus cases (fires 6/7, one gap → new case). Ship gate: lookup ≥85% recall@5, faithfulness violations <2%, cross-tenant deny tests green. Every number is re-runnable; the next embedding model gets judged in an afternoon.

**3. The stale-citation incident and the freshness pipeline.**
Legal updates the data-retention policy; two weeks later the assistant cites the superseded version to a customer — escalation. Root cause chain: nightly rebuild had silently failed for 16 days (no staleness alarm); deletes weren't tombstoned (old chunks survived rebuilds). Fixes: ingest becomes event-driven (doc updated → re-chunk → upsert by doc_id, delete → tombstone → verified uncitable), staleness metric (index max(updated_at) vs source-of-truth) with a 4-hour alert, and a "cite date" chip in the answer UX so users see document vintage (see ai-product-ux provenance). The incident's eval legacy: a "superseded document" case type — ask about updated policies, assert the new version wins.

**4. Choosing NOT-RAG (the arithmetic).**
Internal tool: Q&A over a 60k-token employee handbook, ~200 queries/day, doc changes quarterly. RAG proposal priced: chunking+index+rerank pipeline, ops surface, freshness machinery. Alternative priced: cache the handbook in-context (prompt caching makes repeat-context cheap), full-document attention, zero index ops; latency and per-query cost within budget at this volume. Chosen: stuffing, with a written trigger to revisit ("corpus >300k tokens, or multi-tenant, or >2k queries/day"). Six months later the trigger fires (three more handbooks, per-country) — and the eval set built during the stuffing era (real questions accumulated) makes the RAG migration measurable from day one. The religion was skipped; the arithmetic was kept.

## Evaluation Rubric

Score 1–10:

- **1–2**: No eval set; fixed-size chunks unread; dense-only; prompt-tuning as the only tool; no refusal path; staleness unmanaged.
- **3–4**: Some test questions (untyped, unlabeled); hybrid or rerank present but unmeasured; chunks never inspected; citations decorative; tenant filtering assumed.
- **5–6**: Labeled typed eval set with recall@k and answer metrics; the retrieval-vs-synthesis fork practiced; structure-aware chunking; hybrid+rerank; refusal cases measured.
- **7–8**: Full checklist: two-stage retrieval tuned per type, query rewriting, freshness pipeline with deletion verification, tenant deny tests, failure→case flywheel, versioned reproducible indexes.
- **9–10**: Additionally: question-type routing (SQL/tools for aggregation, parent-doc for procedures); citation audits; hard-negative mining loop; cost/latency budgeted per type; the harness gates every pipeline change like CI gates deploys (see ci-cd — same discipline, different artifact).
