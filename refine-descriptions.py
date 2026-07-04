#!/usr/bin/env python3
"""Overwrite each SKILL.md's frontmatter description with a curated, trigger-rich one."""
import re
from pathlib import Path

SKILLS = Path(__file__).parent / "skills"

DESC = {
"color": "Use when building a color palette or design system, adding dark mode, choosing chart/data-viz colors, fixing 'flat' or 'muddy' UI, or auditing contrast — neutrals, accents, semantic roles, scales.",
"design-language": "Use when deciding a product's visual identity or style direction, escaping a generic-template look, evaluating whether a trend (glassmorphism, brutalism, minimalism) fits, or setting design principles.",
"motion": "Use when adding animations or transitions (modals, panels, page nav, micro-interactions), fixing janky or sluggish motion, or defining motion tokens — durations, easings, springs, choreography.",
"typography": "Use when choosing or pairing fonts, setting a type scale, fixing UI that 'looks cheap/generic,' or tokenizing text styles — weights, line height, measure, letter spacing.",
"visual-hierarchy": "Use when a screen feels cluttered or 'off,' users miss the primary action, laying out a new view, or setting spacing tokens — size, weight, color, spacing, alignment, density.",
"agents": "Use when building an LLM agent (model + tools + loop), choosing between a fixed workflow and an agent, fixing unreliable agents (wrong tools, runaway loops, goal drift), or designing tools/memory/multi-agent topologies.",
"evals": "Use when building any LLM feature, deciding whether a prompt/model/pipeline change actually improved things, calibrating an untrustworthy LLM-judge, or gating LLM changes like CI — assertions, judges, human review.",
"prompt-engineering": "Use when writing or debugging prompts for LLM features (extraction, classification, generation, agents), fixing inconsistent or format-breaking output, taming an overgrown prompt, or migrating models.",
"rag": "Use when building or debugging retrieval-augmented Q&A/assistants over docs or code, choosing chunking/embeddings/vector stores/rerankers, fixing vague or 'confidently wrong' answers, or adding grounding/citations.",
"event-driven": "Use when designing event-based systems (event schemas, sagas, CQRS, eventual consistency), coordinating cross-service workflows without distributed transactions, or reviewing dual-write / 'just publish an event' designs.",
"observability": "Use when instrumenting a service (structured logs, RED/USE metrics, traces), defining SLOs, fixing alert fatigue or missing incident evidence, or controlling logging/metrics cost.",
"system-design": "Use when designing a new service or backend, scaling a system near its limits, evaluating architecture proposals (microservices, datastores, rewrites), or in system-design interviews — meet the actual QPS/latency/availability numbers.",
"api-design": "Use when designing a new HTTP/RPC API or adding endpoints, choosing REST vs GraphQL vs gRPC, reviewing an API/OpenAPI spec, or fixing an 'awkward' API — resource modeling, errors, pagination, versioning, compatibility.",
"async-processing": "Use when moving work out of the request path (queues, background workers), absorbing traffic spikes, keeping two systems consistent without distributed transactions, or reviewing dual-write designs — retries, DLQs, idempotency.",
"authentication": "Use when building login/signup, adding service-to-service auth, integrating OAuth/OIDC/SSO, choosing sessions vs JWTs, or reviewing code touching tokens/sessions/passwords/reset.",
"authorization": "Use when adding roles, permissions, sharing, or multi-tenant isolation, securing resource-by-ID endpoints (IDOR), or refactoring scattered inline access checks — RBAC, ABAC, ReBAC, fail-closed enforcement.",
"caching": "Use when adding a cache (Redis, in-process, CDN, HTTP) to a measured hot path, protecting a fragile dependency, reviewing a 'just cache it' PR, or debugging staleness bugs — invalidation, stampede protection.",
"postgres": "Use when designing Postgres schemas, diagnosing slow queries or timeouts, reading query plans, planning migrations on large/hot tables, or choosing keys/indexes/constraints.",
"convergent-evaluation": "Use when selecting among options after divergence (architectures, vendors, designs, bets), ending a re-litigated decision, or committing serious resources — criteria-first scoring, pre-mortems, kill criteria.",
"divergent-thinking": "Use when generating ideas (features, designs, names, architectures, stuck problems), interrupting the rush to the first plausible idea, or preparing real alternatives for a decision — inversion, SCAMPER, analogy.",
"first-principles": "Use when conventional approaches have failed, 'that's how it's done' appears in a justification, costs/timelines feel inherited, or a 10x improvement is needed — decompose to load-bearing facts and rebuild.",
"code-review": "Use when reviewing a PR (and calibrating how deeply), authoring a reviewable PR, responding to review feedback, or setting team review norms — severity, blast-radius attention, teaching comments.",
"technical-writing": "Use when writing a design doc, decision/ADR, PR description, incident report, runbook, or status update carrying bad news — lead with the conclusion, shape for the busiest reader, end relitigation.",
"abstraction-and-simplicity": "Use when designing an interface/module/function/schema, tempted to generalize or DRY up duplication, reviewing hard-to-name or hard-to-follow code, or judging over/underengineering — deep modules, rule of three.",
"concurrency-bugs": "Use when bugs are intermittent, load-dependent, or 'can't reproduce locally,' seeing duplicate records/lost updates/drifting counters/deadlocks, or reviewing check-then-act and shared mutable state — races, atomicity.",
"memory-leaks": "Use when memory grows to OOM, services need periodic restarts, latency degrades over hours, or hitting 'too many open files'/pool exhaustion/rising thread counts — snapshot diffs, growth curves, leak forensics.",
"production-debugging": "Use when an alert fires or users report an outage, a deploy 'feels off,' chasing intermittent production-only failures, or converting a mitigation into root cause — stabilize first, preserve evidence, run the incident.",
"root-cause-analysis": "Use when a bug's cause isn't obvious, a 'fixed' bug came back, chasing 'works on my machine,' or vetting a fix that can't explain the mechanism — reproduce, minimize, hypothesize, binary-search.",
"component-architecture": "Use when structuring a feature's component tree, a component grew past ~200 lines or 8 props, deciding where state lives, or reviewing frontend structure (React-idiom, transfers to Vue/Svelte/Solid).",
"forms": "Use when building any input surface (signup, checkout, settings, wizards, inline/bulk edits), fixing lost input or abandonment, mapping server errors to fields, or choosing a form library — validation timing, accessibility.",
"frontend-performance": "Use when the app is slow to load or laggy, Core Web Vitals fail (LCP/INP/CLS), before/after adding heavy features, or setting performance budgets — measure on real conditions, spend where the profile says.",
"state-management": "Use when choosing frontend state architecture, a global store became a dumping ground, data is stale/duplicated/flickering, or deciding on Redux/Zustand/Jotai/signals vs a server-cache library — server vs URL vs local vs global.",
"ci-cd": "Use when building or overhauling a build/test/deploy pipeline, deploys are scary/manual/rare, CI is slow or flaky, a migration broke rollback, or designing branch strategy and release gating — build-once, progressive delivery.",
"technical-leadership": "Use when you own outcomes you don't implement (tech lead, staff, team lead), a technical disagreement is looping, deciding what to delegate, or negotiating scope/debt/deadlines — decide legitimately, grow engineers, keep bus factor > 1.",
"learning-new-stacks": "Use when getting productive in an unfamiliar language/framework/codebase, deciding how deeply to learn it, when learning has stalled (tutorial-complete but can't build), or mentoring someone through a new stack.",
"decomposing-ambiguity": "Use when the request is a feeling not a spec ('app is slow,' 'make onboarding better,' 'add AI'), two people are solving different problems with the same words, or a task resists estimation — restate, surface assumptions, split.",
"judgment-under-uncertainty": "Use when deciding before the facts exist, someone is overconfident with expensive stakes, choosing prototype-fast vs production-careful, or judging in a post-mortem whether a call was bad or unlucky — calibrate, price being wrong.",
"planning-and-estimation": "Use when work spans multiple days or people, a date is being asked or promised, a project is stuck at '90% done,' or deciding whether to plan at all vs spike — sequence risk early, estimate with stated uncertainty.",
"optimization-method": "Use when something is measurably too slow or expensive (endpoint, query, build, render, bill), before optimizing anything, when a team optimizes by instinct without profiles, or capacity/load planning — measure, then optimize.",
"product-thinking": "Use when choosing what to build next, a feature request arrives, scoping an MVP, a shipped feature isn't moving metrics, or defining success metrics — separate wanted from technically-interesting.",
"legacy-migrations": "Use when changing a system with thin tests and departed authors, running any migration (database, framework, service extraction, vendor swap, v1-to-v2), when 'let's just rewrite it' comes up, or a migration stalled at 60%.",
"refactoring": "Use when code's shape resists a change ('make the change easy, then make the easy change'), the same bug family recurs, before extending code you don't understand, or a working PR deepens a structural problem — behavior-preserving.",
"research": "Use when evaluating a framework/library/vendor before committing, answering 'does X support Y / how do others solve Z / is this possible,' checking prior art before building novel, or running a timeboxed spike.",
"secrets-and-supply-chain": "Use when a credential is created or leaked, adding/upgrading/auditing dependencies (especially install scripts), designing CI/CD secret handling, onboarding a vendor SDK, or after a package-compromise incident.",
"web-security": "Use when designing any endpoint/form/upload/webhook touching untrusted input, reviewing code that crosses a trust boundary, threat-modeling features (money, PII, auth, files), or fixing a pentest finding by class.",
"ai-product-ux": "Use when adding LLM features (assistants, generation, summarization, agents), users don't trust or over-trust the AI, designing input/output/feedback affordances, or deciding agent autonomy and surfacing its actions.",
"dashboard-ux": "Use when building analytics/monitoring/executive/operational dashboards, engagement is low or users export to spreadsheets, stakeholders keep asking for 'another chart,' or choosing which metrics earn the screen.",
"data-tables": "Use when building a list of records (admin panels, CRMs, order/user lists, logs), users export to Excel to do real work, choosing pagination vs infinite scroll or inline edit, or fixing slow/lying sort and dangerous bulk ops.",
"interface-states": "Use when building any view that fetches or waits, designs only show the ideal populated state, error handling is inconsistent, or the app 'feels broken' during loads/failures — loading, empty, error, skeletons, toasts.",
"onboarding": "Use when designing signup-to-first-value flow, activation/retention is poor and users evaporate, someone proposes a product tour or checklist, or adding a heavy first-run prerequisite — empty states, time-to-value.",
}


def main():
    missing = []
    updated = 0
    for skill_dir in sorted(SKILLS.iterdir()):
        if not skill_dir.is_dir():
            continue
        slug = skill_dir.name
        f = skill_dir / "SKILL.md"
        if slug not in DESC:
            missing.append(slug)
            continue
        text = f.read_text(encoding="utf-8")
        new_desc = '"' + DESC[slug].replace('"', '\\"') + '"'
        new_text = re.sub(
            r"^description:.*$",
            f"description: {new_desc}",
            text,
            count=1,
            flags=re.M,
        )
        f.write_text(new_text, encoding="utf-8")
        updated += 1
    print(f"Updated {updated} descriptions")
    if missing:
        print("NO CURATED DESC FOR:", missing)


if __name__ == "__main__":
    main()
