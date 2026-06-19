---
name: flex-docs
description: Create, update, or refine the project's docs/ - agent-facing specs derived from the codebase, in the inject:true + description format. Use to set up or maintain the docs that planner/implementer/reviewer follow.
argument-hint: [audit|create|update|refine]
---

Create, update, or refine `docs/` for: **$ARGUMENTS** (default: `audit`).

## Purpose

`docs/` carries the **project-specific knowledge an agent needs to code correctly** -
the decisions and invariants the code assumes but states nowhere in one place. It is
*not* a tutorial, *not* general best practice, *not* a restatement of what the code
already shows. The goal is the smallest set of specs that keep planner/implementer/
reviewer consistent with how this project actually works.

## What earns a doc (criteria)

Include a fact only if it is **all** of these - otherwise leave it out or delete it:

- **Project-specific** - true of *this* codebase, not advice the model already knows
  (general conventions belong in a skill, or nowhere).
- **Non-obvious** - an agent reading the code could plausibly get it wrong unprompted.
- **Enforceable** - the `reviewer` agent could cite it to flag a deviation in a change.
- **Stable** - an invariant or convention, not a detail that rots every change.
- **Not duplicated** - not already in a skill or `CLAUDE.md`.

Fewer, sharper docs beat many. Human-only docs (guides, onboarding) get **no** `inject:`
signal, so they never enter the agent index.

## Good vs bad

GOOD - a project invariant the code assumes but states nowhere:
- "Money is stored as integer cents, never floats." - one wrong float corrupts data.
- "Repository methods return `Result<T>`; they never raise." - reviewer can enforce it.
- "Webhooks must be idempotent - dedupe by `event_id` in `webhook_events`." - easy to miss.

BAD - drop these:
- "Use meaningful variable names." - general advice the model already knows.
- "The login route is `POST /auth/login`." - restates code that rots; read the router.
- "We should add more tests." - aspiration, not a spec to follow.
- "We use Python 3.10." - obvious from config; nothing to enforce per change.

## Flow

1. **Audit.** Read the existing `docs/` + the code. List gaps: stale / wrong /
   contradicts the code / missing / noise. Trace each claim to `file:line`.
2. **Extract the design.** From the code, map what an agent must follow: architecture
   (layers, modules, boundaries), conventions (naming, error handling, API shape, test
   patterns), domain rules, non-obvious decisions. Never write a claim you did not verify.
3. **Filter.** Apply the criteria above; drop everything that fails any of them.
4. **Plan + confirm.** Present the plan - files to add / update / remove, one line of
   reason each. **Wait for approval before writing.**
5. **Write.** Use frontmatter `inject: true` + a `description` - the index label
   injected into the agents, so keep it concise: a short line, just enough to route, no
   padding. Place docs under `architecture.md` / `conventions/` / `domain/` / `adr/`;
   scaffold missing structure with `flex-kit init-docs`.
6. **Verify.** Re-check each claim against the code, then `flex-kit gen` + `flex-kit doctor`.

## Rules

- Evidence only - every claim traces to code; never write what you did not verify.
- Prefer deleting/merging over adding; confirm the plan before writing.
