---
name: flex-skill-creator
description: Create, audit, or update a .flexkit skill so it follows the kit's format - name == dir, a "use when" description, a tight token-conscious body, references/ for long sections. Use to add a skill or fix skill drift.
argument-hint: [audit|create|update] [id]
---

Create, audit, or update a `.flexkit/skills/` skill for: **$ARGUMENTS** (default: `audit`).

## Purpose

A skill teaches the agent how to do one kind of task well. In flex-kit a skill is
`.flexkit/skills/<id>/SKILL.md` (+ optional `references/`); `gen` produces the host copies
(`.claude/skills/`, `.agents/skills/`). This command keeps every skill on one format so
none drifts, and audits the existing ones against it.

It owns the **prose contract**. Mechanical checks (kebab name, description length,
generated-in-sync) stay in `flex-kit doctor` - audit defers to it, never restates it.

## The skill contract

```
.flexkit/skills/<id>/
  SKILL.md       required: frontmatter (name, description) + a markdown body
  references/    optional: long material, copied verbatim to every host
```

Frontmatter:

| Field | Rule |
|---|---|
| `name` | kebab-case, **== the directory `<id>`**, and **group-prefixed** (`<group>-<topic>`) - see below |
| `description` | one line - what it does + **when to use** (`"… Use when <situation>"`); it drives triggering, so keep it trigger-focused, not a feature list |

**Naming & grouping.** Skills `gen`-flatten into one host namespace (`.claude/skills/<id>/`),
so an id must be globally unique. Convention: a **pack is a discipline group**, and a **skill
id is `<group>-<topic>`** - e.g. `engineering-design-patterns`, `backend-api-design`. The
prefix prevents collisions and makes the flat list self-grouping. Groups:

| prefix | scope |
|---|---|
| `engineering-` | universal craft (language-agnostic): patterns, architecture, errors, concurrency, testing |
| `backend-` | server-side: api, data, caching, auth (+ `backend-<lang>` for implementation) |
| `frontend-` | client-side: components, state, a11y, performance (+ `frontend-<framework>`) |
| `ai-` | AI/LLM: prompting, RAG, evals, agents, context engineering |
| `data-` | persistence: schema, migrations, indexing, query tuning |
| `security-` | hardening, authz, token/key handling, threat modeling |
| `infra-` | build / ship / run: CI/CD, deploy, observability, IaC |
| `product-` | discovery, spec, requirements |

The kit's own **base process skills** (`navigator`, `verify-fix-loop`, …) are exempt - they
are operating-system skills, not a discipline, so they keep bare names. Add new prefixes as
new disciplines appear; one prefix per pack.

Body - principles, not a rigid template:

- **One skill = one job.**
- **Token-conscious** - every section must change the agent's behavior; if removing it
  wouldn't, cut it. Process over reference dumps, specific over general.
- **Progressive disclosure** - `SKILL.md` is loaded whenever the skill triggers, so keep it
  tight (aim under ~250 lines); `references/` is the on-demand overflow - move any section
  past ~100 lines into `references/<topic>.md`, linked from the body.
- **High-stakes skills** (a quality gate, a destructive op) earn a short `## Red Flags`
  (observable signs it is being violated) and/or `## Rationalizations` (the costly excuses
  + their rebuttals).

## Flow

1. **Audit.** Read the target skill(s) against the contract. List drift: `name` != dir, a
   missing or wrong **group prefix**, a description with no "use when" or that reads as a
   feature list, a bloated body, a >100-line section that should be a `references/` file, a
   high-stakes skill with no Red Flags. Report it - do not fix in audit.
2. **Plan + confirm.** For create / update, present the frontmatter + body outline, one
   line of reason each. **Wait for approval before writing.**
3. **Write.** Create or edit `.flexkit/skills/<id>/SKILL.md` to the contract. For update,
   make the smallest diff that closes the drift.
4. **Verify.** `flex-kit gen` + `flex-kit doctor` - the mechanical floor + that the host
   surfaces are in sync. Never hand-edit `.claude/skills/` or `.agents/skills/`.

## Rules

- The command owns format / prose; `doctor` owns the mechanical floor - delegate, don't duplicate.
- Conditional sections: don't add a Red Flags / Rationalizations block to a low-stakes
  skill - it is noise.
- Keep bodies tight - trust the agent, cut padding. Confirm the plan before writing.
