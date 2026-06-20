---
name: flex-guide-creator
description: Create or refresh the repo's root agent guide - CLAUDE.md + AGENTS.md, kept identical - as a thin WHAT/WHY/HOW manual that points to docs/ and skills rather than restating them. Use to set up or tighten the guide every session loads.
argument-hint: [audit|create|refresh]
---

Create or refresh the root agent guide (`CLAUDE.md` + `AGENTS.md`) for: **$ARGUMENTS**
(default: `audit`).

## Purpose

`CLAUDE.md` (Claude) and `AGENTS.md` (Codex) are the ONLY files auto-loaded into every
session - the agent is otherwise stateless. So the guide must carry the startup
essentials and nothing else: a thin **WHAT / WHY / HOW** manual that *points* to the
detail (docs/, skills, agents), never restates it. Padding here costs every session - a
frontier model follows ~150-200 instructions and the host already spends ~50, so each
line must earn universal, every-session relevance.

Write the SAME content to both files (Claude reads `CLAUDE.md`, Codex reads `AGENTS.md`) -
keep them identical, no drift.

## What earns a line

Include a line only if it is **all** of these - otherwise leave it out:

- **Startup-essential** - the agent needs it before reading any other file.
- **Universal** - true every session, not task- or phase-specific.
- **WHAT / WHY / HOW** - the project's shape, its purpose, or how to build / test / verify.
- **Non-obvious** - not something the model already knows or the code states plainly.
- **Not in `docs/`** - the `inject:true` docs carry the detailed specs; the guide points to
  them.

Explicitly leave out: **code style** (a linter / formatter owns it - never send an agent
to do a linter's job), an **exhaustive command list** (name the few that matter, point to
the Makefile / scripts), a **skills / agents inventory** (the host already surfaces those
to the session), the **README's content** (the guide complements README with
agent-specific context - it doesn't copy it), and anything a `docs/` spec already covers.

## Outline (the guide it writes)

```
# <Project> - agent operating guide

<one line: what this is + why it exists>           # WHY

## Stack & shape                                    # WHAT
- language / framework / runtime + tooling pref (e.g. bun, not node)
- module map: the 4-6 dirs that matter, one line of role each (paths, not prose)

## How to work                                      # HOW
- the few essential commands (build / test / verify) - point to the Makefile / scripts
- the verify-before-done expectation

## Where to look  (progressive disclosure)
- authoritative specs -> docs/ (the agent reads only what's relevant)
- "read X before doing Y" pointers, with file:line

## Project rules / gotchas
- the handful of non-obvious invariants an agent gets wrong unprompted
```

Aim for ~60 lines, hard cap ~300. Fewer, sharper lines beat coverage.

## Flow

1. **Audit.** Read the existing `CLAUDE.md` / `AGENTS.md` + scan the repo (stack, dir
   layout, build / test commands, existing `docs/` + skills). List what's stale, missing,
   redundant with `docs/`, or code-style noise to cut. Trace each kept claim to evidence.
2. **Draft.** Fill the outline from what you verified - point to docs / skills, use
   `file:line`, drop anything that fails a criterion.
3. **Confirm.** Present the draft + a one-line reason per section. **Wait for approval
   before writing** - think about every line; never blind-generate (`/init`-style).
4. **Write.** Write the SAME content to `CLAUDE.md` and `AGENTS.md`.

## Rules

- Curate every line - the guide loads into every session; noise degrades all of them.
- Point, don't copy: `file:line` + links to docs / skills over inlined snippets that rot.
- No code style, no exhaustive command dumps, nothing `docs/` already owns.
- `CLAUDE.md` and `AGENTS.md` stay identical.
- **Monorepo** - scope a guide per package (nested `AGENTS.md` / `CLAUDE.md`); agents read
  the nearest, so each subproject ships tailored instructions and the root stays thin.
- **Imports** - Claude expands `@path` references at launch, but that is Claude-only; with
  identical `CLAUDE.md` / `AGENTS.md`, prefer plain pointers so both hosts behave the same.
