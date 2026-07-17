# Fable's Expert Skills Pack

55 expert software-engineering skills for [Claude Code](https://claude.com/claude-code), spanning AI, backend, frontend, architecture, security, testing, UX, deployment, debugging, and engineering judgment.

## Install

In an interactive Claude Code session:

```
/plugin marketplace add KshitijBharambe/fable-skills
/plugin install fable-skills
```

Or test locally before pushing:

```
/plugin marketplace add /Users/kshtj/skills
/plugin install fable-skills
```

Once installed, the skills auto-load by their descriptions whenever a relevant task comes up — no manual invocation needed.

## What's inside

Skills live in [`skills/`](skills/), one folder per skill with a `SKILL.md`. Categories:

- **AI** — agents, evals, prompt-engineering, rag
- **Backend** — api-design, async-processing, auth, caching, data-modeling, domain-modeling, postgres
- **Frontend** — component-architecture, forms, frontend-performance, state-management
- **Architecture** — system-design, event-driven, observability, resilience-engineering
- **Aesthetics** — color, typography, motion, visual-hierarchy, design-language, layout-and-spacing
- **UX** — ux-fundamentals, accessibility, ai-product-ux, dashboard-ux, data-tables, interface-states, onboarding
- **Security** — security (web, secrets & supply chain)
- **Testing** — testing-strategy
- **Infrastructure** — ci-cd, deployment, compliance-and-privacy
- **Debugging** — root-cause-analysis, concurrency-bugs, memory-leaks, production-debugging
- **Meta / judgment** — decomposing-ambiguity, judgment-under-uncertainty, planning-and-estimation, first-principles, brainstorming
- Plus code-review, refactoring (incl. legacy migrations), technical-writing, technical-leadership, product-thinking, research, learning-new-stacks, optimization-method, abstraction-and-simplicity.

### Changed in v2.0.0

Merged (8 → 4): divergent-thinking + convergent-evaluation → **brainstorming**; authentication + authorization → **auth**; refactoring + legacy-migrations → **refactoring**; web-security + secrets-and-supply-chain → **security**. Added 9 new skills: testing-strategy, accessibility, resilience-engineering, data-modeling, domain-modeling, ux-fundamentals, layout-and-spacing, deployment, compliance-and-privacy.

## Editing / regenerating

The `skills/` folders are generated from the source docs (`ai/`, `backend/`, etc.):

- `build-plugin.py` — scaffolds `skills/<name>/SKILL.md` and the manifests from the source `category/*.md` files.
- `refine-descriptions.py` — overwrites each skill's frontmatter `description` with a curated, trigger-rich one.

Workflow after editing a source doc: run `python3 build-plugin.py` **then** `python3 refine-descriptions.py` (in that order — build regenerates SKILL.md; refine restores the curated descriptions).
