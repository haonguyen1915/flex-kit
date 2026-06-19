---
name: flex-agent-creator
description: Create, audit, or update a .flexkit agent so it follows the kit's format - correct frontmatter, the SKILLS/DOCS markers, and the Verification Gate + Context Handoff Contract sections. Use to add an agent or fix format drift.
argument-hint: [audit|create|update] [id]
---

Create, audit, or update a `.flexkit/agents/` agent for: **$ARGUMENTS** (default: `audit`).

## Purpose

An agent file *is* a subagent's whole system prompt, and the kit's mechanics depend on
every agent sharing one format: the `<!-- SKILLS -->` / `<!-- DOCS -->` markers get the
catalog injected at `gen`, the frontmatter drives generation and routing, and the named
protocol sections (`Verification Gate`, `Context Handoff Contract`) let agents hand off
through files instead of chat. This command keeps every agent on that format so none drifts.

It owns the **prose contract**. Mechanical checks (name == filename, description present,
generated-in-sync) stay in `flex-kit doctor` - audit defers to it, never restates it.

## The agent contract

Frontmatter (all four required):

| Field | Rule |
|---|---|
| `name` | kebab-case, **== filename** (`<id>.md`) |
| `description` | one concise line - injected into every other agent's skill catalog, so keep it tight and behavioral (what it does + when to pick it) |
| `model` | `opus` \| `sonnet` \| `haiku` |
| `lane` | `build` (plan / implement) \| `review` (verify / critique) |

Body - include a section only when its trigger applies (not every agent gets every one):

| Section | Include when |
|---|---|
| role line (1 sentence) | always - who the agent is |
| `## Available Skills` + `<!-- SKILLS -->` | always |
| `## Project Docs` + `<!-- DOCS -->` | the agent writes or judges against specs |
| *role sections* (`## Process`, `## Review`, ...) | always - the actual work |
| `## Output` | the agent emits files / handoffs |
| `## Verification Gate` | the agent emits a verdict / report - a checklist it self-confirms, closing with "if a gate fails, emit `DONE_WITH_CONCERNS` and explain" |
| `## Context Handoff Contract` | the agent reads a handoff - the field-list it expects + "if absent, rebuild from plan / spec / diff, never chat" |

Tail order when present: `## Output` -> `## Verification Gate` -> `## Context Handoff Contract`.

The base `reviewer` / `tester` / `implementer` agents are the reference shape - match them.

## Good vs bad (description)

The description is injected into other agents, so it must read as a routing label.

GOOD:
- "Review a code change for correctness, risk, and convention, then write an approve or revise verdict."
- "Run the project's tests for a change and report failures."

BAD:
- "This agent is very helpful and reviews things." - vague, no routing value.
- "Reviewer." - too terse; says nothing about when to pick it.
- A three-sentence paragraph - it bloats every other agent's catalog.

## Flow

1. **Audit.** Read the target agent(s) against the contract. List drift: missing/extra
   marker, a missing gate or handoff section where the trigger applies (or one present
   where it does not), frontmatter gaps (`model` / `lane`), a description that is vague or
   does not match the body. Report it - do not fix in audit.
2. **Plan + confirm.** For create / update, present the frontmatter + the section set you
   will write, one line of reason each. **Wait for approval before writing.**
3. **Write.** Create or edit `.flexkit/agents/<id>.md` to the contract. For update, make
   the smallest diff that closes the drift - do not rewrite sections that already conform.
4. **Verify.** `flex-kit gen` + `flex-kit doctor` - the mechanical floor + that the host
   surfaces are in sync.

## Rules

- The command owns format / prose; `doctor` owns the mechanical floor - delegate, don't duplicate.
- Conditional sections: never add a gate / handoff section to an agent whose trigger does
  not apply - an empty gate is noise.
- Keep bodies tight - trust the agent, cut padding. Confirm the plan before writing.
