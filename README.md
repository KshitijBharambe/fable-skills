# Kshitij's Expert Skills

50 expert software-engineering skills for [Claude Code](https://claude.com/claude-code), spanning AI, backend, frontend, architecture, security, UX, debugging, and engineering judgment.

## Install

In an interactive Claude Code session:

```
/plugin marketplace add KshitijBharambe/fable-skills
/plugin install kshtj-expert-skills
```

Or test locally before pushing:

```
/plugin marketplace add /Users/kshtj/skills
/plugin install kshtj-expert-skills
```

Once installed, the skills auto-load by their descriptions whenever a relevant task comes up — no manual invocation needed.

## What's inside

Skills live in [`skills/`](skills/), one folder per skill with a `SKILL.md`. Categories:

- **AI** — agents, evals, prompt-engineering, rag
- **Backend** — api-design, async-processing, authentication, authorization, caching, postgres
- **Frontend** — component-architecture, forms, frontend-performance, state-management
- **Architecture** — system-design, event-driven, observability
- **Aesthetics** — color, typography, motion, visual-hierarchy, design-language
- **UX** — ai-product-ux, dashboard-ux, data-tables, interface-states, onboarding
- **Security** — web-security, secrets-and-supply-chain
- **Debugging** — root-cause-analysis, concurrency-bugs, memory-leaks, production-debugging
- **Meta / judgment** — decomposing-ambiguity, judgment-under-uncertainty, planning-and-estimation, first-principles, divergent-thinking, convergent-evaluation
- Plus code-review, refactoring, legacy-migrations, technical-writing, technical-leadership, product-thinking, research, learning-new-stacks, optimization-method, abstraction-and-simplicity, ci-cd.

## Editing / regenerating

The `skills/` folders are generated from the source docs (`ai/`, `backend/`, etc.):

- `build-plugin.py` — scaffolds `skills/<name>/SKILL.md` and the manifests from the source `category/*.md` files.
- `refine-descriptions.py` — overwrites each skill's frontmatter `description` with a curated, trigger-rich one.

Workflow after editing a source doc: run `python3 build-plugin.py` **then** `python3 refine-descriptions.py` (in that order — build regenerates SKILL.md; refine restores the curated descriptions).
