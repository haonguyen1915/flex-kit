---
name: flex-docs
description: Create, update, or refine the project's docs/ - agent-facing specs derived from the codebase, in the inject: + description format. Use to set up or maintain the docs the agents follow.
argument-hint: [audit|create|update|refine]
---

Create, update, or refine `docs/` for: **$ARGUMENTS** (default: `audit`).

## Purpose

`docs/` carries the **project-specific knowledge an agent needs to code correctly** -
the decisions and invariants the code assumes but states nowhere in one place. It is
*not* a tutorial, *not* general best practice, *not* a restatement of what the code
already shows. The goal is the smallest set of specs that keep the agents consistent with
how this project actually works.

## What earns a doc (criteria)

Include a fact only if it is **all** of these - otherwise leave it out or delete it:

- **Project-specific** - true of *this* codebase, not advice the model already knows
  (general conventions belong in a skill, or nowhere).
- **Non-obvious** - an agent reading the code could plausibly get it wrong unprompted.
- **Enforceable** - the `reviewer` agent could cite it to flag a deviation in a change.
- **Stable** - an invariant or convention, not a detail that rots every change.
- **Not duplicated** - not already in a skill or `CLAUDE.md`.

Fewer, sharper docs beat many. Human-only docs (onboarding, contributor runbooks) get
**no** `inject:` signal, so they never enter the agent index.

## Doc kinds (the concept = the question it answers)

The folder classifies the *concept*, not the audience. The same topic can appear as a
rule, a lens, and a how-to - different kinds, not duplication.

| Kind | Answers |
|---|---|
| `architecture.md` | the codebase map - layers, modules, boundaries |
| `adr/` | **WHY** - a decision + its rationale |
| `domain/` | **INVARIANT** - a fact the code must always hold |
| `conventions/` | **RULE** - the enforceable bar for *writing* code (naming, error/API shape) |
| `review/` | **LENS** - what to *inspect* + known pitfalls (not new rules) |
| `guides/` | **HOW** - deep, procedural, code-sampled reference |

Classifying test: a one-sentence "must / must not" -> a **rule** (`conventions/`); a "when
reviewing, watch for…" or a past mistake -> a **lens** (`review/`); anything needing a
walkthrough or code sample -> a **guide**.

## Who to inject (judge per doc, from the content)

`inject:` follows **who actually acts on the doc's content** - decided per doc by reading
it, never a fixed rule from its folder. Target by id or lane from this project's roster
(`[docs]` = the agent has a `<!-- DOCS -->` marker, so a doc can reach it - targeting one
without it warns in `doctor`):

<!-- AGENTS -->

Ask: whose work changes if they read this? Then pick from the roster above:

- a fact every agent must honor (an invariant, a decision) -> `all`
- a rule only the writers and the reviewer apply -> the build-lane agents + `reviewer`
- an inspection lens only the reviewer runs -> `reviewer`
- a deep how-to too long to inject -> no `inject:` (a skill pulls it on demand)

Folder tendencies are *typical*, not rules: a `conventions/` doc that genuinely matters
everywhere is `all`; a `domain/` fact only one writer touches is just that agent. Read the
content, then pick the target from the roster.

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
5. **Write.** Pick the folder from **Doc kinds** (the concept) and the `inject:` target
   from **Who to inject** (the content). Add a concise `description` - the index label
   injected into the agents, a short line just enough to route, no padding. Narrow targets
   are agent ids / lanes (`reviewer`, `reviewer, implementer`, `review`). Scaffold missing
   structure with `flex-kit init-docs`.
6. **Verify.** Re-check each claim against the code, then `flex-kit gen` + `flex-kit doctor`.

## Rules

- Evidence only - every claim traces to code; never write what you did not verify.
- Prefer deleting/merging over adding; confirm the plan before writing.
