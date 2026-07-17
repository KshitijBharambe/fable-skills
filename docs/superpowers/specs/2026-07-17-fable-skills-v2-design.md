# fable-skills v2: Consolidation + Expansion

Date: 2026-07-17
Status: Approved (user confirmed direction + additions in session)

## Goal

Restructure the 50-skill pack: merge overlapping skills so the pack doesn't overpopulate the
skill listing, add missing high-value topics (testing, accessibility, resilience, data/domain
modeling, general UI/UX, deployment, compliance). Net: 55 skills, version 2.0.0.

## Merges (8 skills → 4)

| New skill | Absorbs | Rationale |
|---|---|---|
| `brainstorming` | divergent-thinking, convergent-evaluation | Two halves of one loop, always used together. Diverge-then-converge is the spine. |
| `auth` | authentication, authorization | Same domain, same reader, same task context. AuthN/AuthZ preserved as internal halves. |
| `refactoring` | refactoring, legacy-migrations | Same discipline at two scales; migrations become the "systems you didn't build" half. |
| `security` | web-security, secrets-and-supply-chain | One defensive-posture skill: trust boundaries + attack classes + secrets + supply chain. |

Merged docs are rewritten into one coherent 17-section doc (~4–4.5k words), not concatenated.
Source files for absorbed skills are deleted from their category dirs.

Explicitly NOT merged: concurrency-bugs/memory-leaks (different domains), the five aesthetics
skills (each genuinely deep), root-cause-analysis/production-debugging (method vs. live-fire).

## New skills (9)

| Skill | Category dir | Scope |
|---|---|---|
| `testing-strategy` | testing/ | Test pyramid/trophy, what to test at which layer, flakiness, coverage as signal |
| `accessibility` | ux/ | Semantics, keyboard, focus management, ARIA as last resort, testing |
| `resilience-engineering` | architecture/ | Retries, timeouts, circuit breakers, backpressure, graceful degradation |
| `data-modeling` | backend/ | Schema design, normalization judgment, evolution, modeling for access patterns |
| `ux-fundamentals` | ux/ | Usability heuristics, IA, user flows, cognitive load, mental models |
| `layout-and-spacing` | aesthetics/ | Grids, spacing systems, responsive breakpoints, adaptive patterns |
| `domain-modeling` | backend/ | Business rules, invariants, state machines, layering, where logic lives |
| `deployment` | infrastructure/ | Environments, release strategies, rollback, zero-downtime, config |
| `compliance-and-privacy` | infrastructure/ | GDPR/PII, retention, audit trails, licensing, platform policies |

All follow the 17-section template (Purpose, When to use, Goals, Inputs, Outputs, Expert Mental
Model, Workflow, Decision Tree, Heuristics, Quality Checklist, Failure Modes, Edge Cases,
Tradeoffs, Optimization Strategies, Self Review, Examples, Evaluation Rubric) in the pack's
existing voice.

## Housekeeping

- Fix stale cross-refs: `loading-states` → `interface-states` (aesthetics/motion.md); "secrets
  skill" refs (ai/agents.md, infrastructure/ci-cd.md) → `security`.
- Sweep every "see X skill" reference to the 8 retired names → merged names.
- refine-descriptions.py: remove 8 curated entries, add 13 (4 merged + 9 new).
- build-plugin.py: PLUGIN_VERSION 2.0.0, PLUGIN_DESC "55 expert…".
- README: category list, count, install text unchanged otherwise.

## Verification

- `python3 build-plugin.py && python3 refine-descriptions.py` runs clean, no "NO CURATED DESC" warning.
- `skills/` contains exactly 55 dirs; retired dirs absent.
- Every "see X skill" prose ref resolves against an actual skill name.
- Each new/merged doc has all 17 sections.

## Out of scope

- Renaming the plugin, changing install flow, touching memory/ or git history.
- Content edits to the 38 untouched skills beyond cross-ref fixes.
